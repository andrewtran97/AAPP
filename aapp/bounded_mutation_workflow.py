"""Local deterministic bounded file mutation workflow for B44B."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Tuple

from .bounded_mutation_verifier import VERIFIED, verify_mutation_state


REQUEST_SCHEMA_VERSION = "aapp.bounded_mutation.request.v1"
RECEIPT_SCHEMA_VERSION = "aapp.bounded_mutation.receipt.v1"
SUPPORTED_OPERATION = "replace_exact_text"
SUPPORTED_POLICY_DECISION = "ALLOW"
SUPPORTED_RECOVERY_CLASS = "REVERSE"

REQUIRED_FIELDS = {
    "schema_version",
    "request_id",
    "workspace_root",
    "scope_ref",
    "identity_ref",
    "capability_ref",
    "policy_decision_ref",
    "policy_decision",
    "target_relative_path",
    "operation",
    "expected_pre_state_digest",
    "old_text",
    "new_text",
    "idempotency_key",
    "recovery_class",
}


class WorkflowDenied(ValueError):
    """Raised when a request cannot enter bounded execution."""

    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return "sha384:" + hashlib.sha384(data).hexdigest()


def _digest_object(value: Any) -> str:
    return digest_bytes(_canonical_json(value))


def _event(
    seq: int,
    event_type: str,
    status: str,
    reason_codes: List[str],
    **details: Any,
) -> Dict[str, Any]:
    event = {
        "seq": seq,
        "event_type": event_type,
        "status": status,
        "reason_codes": list(reason_codes),
    }
    event.update(details)
    return event


def _canonical_relative_parts(value: str) -> Tuple[str, ...]:
    if not isinstance(value, str) or not value:
        raise WorkflowDenied("TARGET_RELATIVE_PATH_REQUIRED")
    if "\\" in value:
        raise WorkflowDenied("BACKSLASH_PATH_SEPARATOR_UNSUPPORTED")

    path = PurePosixPath(value)
    if path.is_absolute():
        raise WorkflowDenied("ABSOLUTE_TARGET_PATH_FORBIDDEN")
    if path.as_posix() != value:
        raise WorkflowDenied("TARGET_PATH_NOT_CANONICAL")

    parts = path.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise WorkflowDenied("PATH_TRAVERSAL_FORBIDDEN")
    return parts


def _validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise WorkflowDenied("REQUEST_NOT_OBJECT")

    missing = sorted(REQUIRED_FIELDS - set(request))
    if missing:
        raise WorkflowDenied("MISSING_REQUIRED_FIELD")

    unknown = sorted(set(request) - REQUIRED_FIELDS)
    if unknown:
        raise WorkflowDenied("UNKNOWN_FIELD")

    if request["schema_version"] != REQUEST_SCHEMA_VERSION:
        raise WorkflowDenied("UNSUPPORTED_SCHEMA_VERSION")

    required_non_empty_strings = (
        "request_id",
        "workspace_root",
        "scope_ref",
        "identity_ref",
        "capability_ref",
        "policy_decision_ref",
        "target_relative_path",
        "operation",
        "expected_pre_state_digest",
        "old_text",
        "idempotency_key",
        "recovery_class",
    )
    for field in required_non_empty_strings:
        value = request.get(field)
        if not isinstance(value, str) or not value:
            raise WorkflowDenied(f"{field.upper()}_REQUIRED")

    if not isinstance(request.get("new_text"), str):
        raise WorkflowDenied("NEW_TEXT_MUST_BE_STRING")
    if request["old_text"] == request["new_text"]:
        raise WorkflowDenied("NO_CHANGE_REQUESTED")
    if request["operation"] != SUPPORTED_OPERATION:
        raise WorkflowDenied("UNSUPPORTED_OPERATION")
    if request["policy_decision"] != SUPPORTED_POLICY_DECISION:
        raise WorkflowDenied("POLICY_DECISION_NOT_ALLOWED")
    if request["recovery_class"] != SUPPORTED_RECOVERY_CLASS:
        raise WorkflowDenied("UNSUPPORTED_RECOVERY_CLASS")
    if not request["expected_pre_state_digest"].startswith("sha384:"):
        raise WorkflowDenied("UNSUPPORTED_DIGEST_FORMAT")

    _canonical_relative_parts(request["target_relative_path"])

    workspace_root = Path(request["workspace_root"])
    if not workspace_root.is_absolute():
        raise WorkflowDenied("WORKSPACE_ROOT_MUST_BE_ABSOLUTE")
    if workspace_root.is_symlink():
        raise WorkflowDenied("WORKSPACE_ROOT_SYMLINK_FORBIDDEN")
    if not workspace_root.is_dir():
        raise WorkflowDenied("WORKSPACE_ROOT_NOT_DIRECTORY")

    return request


def _open_target(
    workspace_root: str,
    target_relative_path: str,
    flags: int,
) -> int:
    root = Path(workspace_root)
    resolved_root = root.resolve(strict=True)
    parts = _canonical_relative_parts(target_relative_path)

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)
    directory = getattr(os, "O_DIRECTORY", 0)

    root_fd = os.open(
        str(resolved_root),
        os.O_RDONLY | directory | nofollow | cloexec,
    )
    current_fd = root_fd
    try:
        for part in parts[:-1]:
            parent_metadata = os.stat(part, dir_fd=current_fd, follow_symlinks=False)
            if stat.S_ISLNK(parent_metadata.st_mode):
                raise WorkflowDenied("PARENT_SYMLINK_FORBIDDEN")
            next_fd = os.open(
                part,
                os.O_RDONLY | directory | nofollow | cloexec,
                dir_fd=current_fd,
            )
            if current_fd != root_fd:
                os.close(current_fd)
            current_fd = next_fd

        target_metadata = os.stat(
            parts[-1],
            dir_fd=current_fd,
            follow_symlinks=False,
        )
        if stat.S_ISLNK(target_metadata.st_mode):
            raise WorkflowDenied("TARGET_SYMLINK_FORBIDDEN")
        return os.open(
            parts[-1],
            flags | nofollow | cloexec,
            dir_fd=current_fd,
        )
    except OSError as exc:
        raise WorkflowDenied("TARGET_CANNOT_BE_OPENED_SAFELY") from exc
    finally:
        if current_fd != root_fd:
            os.close(current_fd)
        os.close(root_fd)


def _read_all(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: List[bytes] = []
    while True:
        chunk = os.read(fd, 65536)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _write_all(fd: int, data: bytes) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    offset = 0
    while offset < len(data):
        written = os.write(fd, data[offset:])
        if written <= 0:
            raise OSError("write returned no progress")
        offset += written
    os.fsync(fd)


def _restore_original(
    *,
    workspace_root: str,
    target_relative_path: str,
    original_bytes: bytes,
    expected_device: int,
    expected_inode: int,
) -> Dict[str, Any]:
    try:
        fd = _open_target(
            workspace_root,
            target_relative_path,
            os.O_RDWR,
        )
    except (OSError, WorkflowDenied):
        return {
            "status": "FAILED",
            "reason_codes": ["RECOVERY_TARGET_UNAVAILABLE"],
            "restored_digest": None,
        }

    try:
        metadata = os.fstat(fd)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
            or metadata.st_dev != expected_device
            or metadata.st_ino != expected_inode
        ):
            return {
                "status": "FAILED",
                "reason_codes": ["RECOVERY_TARGET_IDENTITY_MISMATCH"],
                "restored_digest": None,
            }

        _write_all(fd, original_bytes)
        restored_digest = digest_bytes(_read_all(fd))
        expected_digest = digest_bytes(original_bytes)
        if restored_digest != expected_digest:
            return {
                "status": "FAILED",
                "reason_codes": ["RECOVERY_DIGEST_MISMATCH"],
                "restored_digest": restored_digest,
            }

        return {
            "status": "RESTORED",
            "reason_codes": ["PRE_STATE_RESTORED"],
            "restored_digest": restored_digest,
        }
    except OSError:
        return {
            "status": "FAILED",
            "reason_codes": ["RECOVERY_WRITE_FAILED"],
            "restored_digest": None,
        }
    finally:
        os.close(fd)


def _denied_result(
    *,
    request: Any,
    request_digest: str | None,
    reason_code: str,
    events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    events.append(
        _event(
            len(events),
            "REQUEST_DENIED",
            "DENIED",
            [reason_code],
        )
    )
    return {
        "status": "DENIED",
        "reason_codes": [reason_code],
        "request_id": request.get("request_id") if isinstance(request, dict) else None,
        "request_digest": request_digest,
        "execution_performed": False,
        "pre_state_digest": None,
        "post_state_digest": None,
        "verifier": None,
        "recovery": {"status": "NOT_REQUIRED", "reason_codes": []},
        "receipt": None,
        "incident": None,
        "evidence_events": events,
    }


def _build_receipt(
    *,
    request: Dict[str, Any],
    request_digest: str,
    pre_state_digest: str,
    post_state_digest: str,
    verifier: Dict[str, Any],
    events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_digest = _digest_object(events)
    core = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "request_id": request["request_id"],
        "request_digest": request_digest,
        "idempotency_key": request["idempotency_key"],
        "scope_ref": request["scope_ref"],
        "identity_ref": request["identity_ref"],
        "capability_ref": request["capability_ref"],
        "policy_decision_ref": request["policy_decision_ref"],
        "target_relative_path": request["target_relative_path"],
        "operation": request["operation"],
        "pre_state_digest": pre_state_digest,
        "post_state_digest": post_state_digest,
        "verifier_verdict": verifier["verdict"],
        "recovery_status": "NOT_REQUIRED",
        "evidence_digest": evidence_digest,
    }
    receipt = dict(core)
    receipt["receipt_id"] = "receipt:" + hashlib.sha384(_canonical_json(core)).hexdigest()
    return receipt


def run_bounded_mutation(request: Any) -> Dict[str, Any]:
    """Execute one exact-text mutation in a caller-provided temporary workspace."""

    request_digest = _digest_object(request) if isinstance(request, dict) else None
    events: List[Dict[str, Any]] = [
        _event(
            0,
            "REQUEST_RECEIVED",
            "RECORDED",
            [],
            request_digest=request_digest,
        )
    ]

    try:
        validated = _validate_request(request)
    except WorkflowDenied as exc:
        return _denied_result(
            request=request,
            request_digest=request_digest,
            reason_code=exc.reason_code,
            events=events,
        )

    events.append(
        _event(
            len(events),
            "AUTHORITY_VALIDATED",
            "ALLOWED",
            ["SCOPE_IDENTITY_CAPABILITY_POLICY_BOUND"],
            scope_ref=validated["scope_ref"],
            identity_ref=validated["identity_ref"],
            capability_ref=validated["capability_ref"],
            policy_decision_ref=validated["policy_decision_ref"],
        )
    )

    try:
        fd = _open_target(
            validated["workspace_root"],
            validated["target_relative_path"],
            os.O_RDWR,
        )
    except WorkflowDenied as exc:
        return _denied_result(
            request=request,
            request_digest=request_digest,
            reason_code=exc.reason_code,
            events=events,
        )

    mutation_started = False
    original_bytes = b""
    pre_state_digest = None
    post_state_digest = None
    device = -1
    inode = -1

    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise WorkflowDenied("TARGET_NOT_REGULAR_FILE")
        if metadata.st_nlink != 1:
            raise WorkflowDenied("TARGET_HARD_LINKED")

        device = metadata.st_dev
        inode = metadata.st_ino
        original_bytes = _read_all(fd)
        pre_state_digest = digest_bytes(original_bytes)

        if pre_state_digest != validated["expected_pre_state_digest"]:
            raise WorkflowDenied("PRE_STATE_DIGEST_MISMATCH")

        try:
            original_text = original_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WorkflowDenied("TARGET_NOT_UTF8_TEXT") from exc

        occurrence_count = original_text.count(validated["old_text"])
        if occurrence_count == 0:
            raise WorkflowDenied("EXACT_TEXT_NOT_FOUND")
        if occurrence_count != 1:
            raise WorkflowDenied("EXACT_TEXT_NOT_UNIQUE")

        expected_post_text = original_text.replace(
            validated["old_text"],
            validated["new_text"],
            1,
        )
        expected_post_bytes = expected_post_text.encode("utf-8")
        post_state_digest = digest_bytes(expected_post_bytes)

        events.append(
            _event(
                len(events),
                "PRE_STATE_CAPTURED",
                "VERIFIED",
                ["PRE_STATE_DIGEST_MATCH"],
                pre_state_digest=pre_state_digest,
                target_relative_path=validated["target_relative_path"],
            )
        )

        mutation_started = True
        _write_all(fd, expected_post_bytes)

        events.append(
            _event(
                len(events),
                "MUTATION_EXECUTED",
                "EXECUTED",
                ["ONE_EXACT_TEXT_MUTATION"],
                post_state_digest=post_state_digest,
            )
        )
    except WorkflowDenied as exc:
        return _denied_result(
            request=request,
            request_digest=request_digest,
            reason_code=exc.reason_code,
            events=events,
        )
    except OSError:
        events.append(
            _event(
                len(events),
                "MUTATION_FAILED",
                "FAILED",
                ["MUTATION_WRITE_FAILED"],
            )
        )
    finally:
        os.close(fd)

    if not mutation_started:
        return _denied_result(
            request=request,
            request_digest=request_digest,
            reason_code="MUTATION_NOT_STARTED",
            events=events,
        )

    verifier = verify_mutation_state(
        workspace_root=validated["workspace_root"],
        target_relative_path=validated["target_relative_path"],
        expected_post_state_digest=str(post_state_digest),
        expected_device=device,
        expected_inode=inode,
    )
    events.append(
        _event(
            len(events),
            "POST_STATE_VERIFIED",
            verifier["verdict"],
            list(verifier.get("reason_codes", [])),
            actual_post_state_digest=verifier.get("actual_post_state_digest"),
        )
    )

    if verifier["verdict"] == VERIFIED:
        receipt = _build_receipt(
            request=validated,
            request_digest=str(request_digest),
            pre_state_digest=str(pre_state_digest),
            post_state_digest=str(post_state_digest),
            verifier=verifier,
            events=events,
        )
        return {
            "status": "VERIFIED",
            "reason_codes": ["MUTATION_VERIFIED"],
            "request_id": validated["request_id"],
            "request_digest": request_digest,
            "execution_performed": True,
            "pre_state_digest": pre_state_digest,
            "post_state_digest": post_state_digest,
            "verifier": verifier,
            "recovery": {"status": "NOT_REQUIRED", "reason_codes": []},
            "receipt": receipt,
            "incident": None,
            "evidence_events": events,
        }

    recovery = _restore_original(
        workspace_root=validated["workspace_root"],
        target_relative_path=validated["target_relative_path"],
        original_bytes=original_bytes,
        expected_device=device,
        expected_inode=inode,
    )
    events.append(
        _event(
            len(events),
            "RECOVERY_COMPLETED",
            recovery["status"],
            list(recovery.get("reason_codes", [])),
            restored_digest=recovery.get("restored_digest"),
        )
    )

    if recovery["status"] == "RESTORED":
        return {
            "status": "RECOVERED_FAILURE",
            "reason_codes": ["VERIFICATION_FAILED_PRE_STATE_RESTORED"],
            "request_id": validated["request_id"],
            "request_digest": request_digest,
            "execution_performed": True,
            "pre_state_digest": pre_state_digest,
            "post_state_digest": post_state_digest,
            "verifier": verifier,
            "recovery": recovery,
            "receipt": None,
            "incident": None,
            "evidence_events": events,
        }

    incident = {
        "incident_type": "BOUNDED_MUTATION_RECOVERY_FAILURE",
        "request_id": validated["request_id"],
        "target_relative_path": validated["target_relative_path"],
        "pre_state_digest": pre_state_digest,
        "expected_post_state_digest": post_state_digest,
        "verifier_reason_codes": verifier.get("reason_codes", []),
        "recovery_reason_codes": recovery.get("reason_codes", []),
    }
    incident["incident_digest"] = _digest_object(incident)

    return {
        "status": "INCIDENT",
        "reason_codes": ["RECOVERY_FAILED"],
        "request_id": validated["request_id"],
        "request_digest": request_digest,
        "execution_performed": True,
        "pre_state_digest": pre_state_digest,
        "post_state_digest": post_state_digest,
        "verifier": verifier,
        "recovery": recovery,
        "receipt": None,
        "incident": incident,
        "evidence_events": events,
    }
