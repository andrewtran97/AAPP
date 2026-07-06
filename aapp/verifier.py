from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .scope import ScopeError, load_scope, require_authorized_scope, scope_id


SUPPORTED_RECORD_SCHEMA_VERSION = "0.1.0"

REQUIRED_RECORD_FIELDS = frozenset(
    {
        "schema_version",
        "record_id",
        "session_id",
        "timestamp",
        "actor",
        "tool",
        "scope",
        "policy",
        "redaction",
        "parent_hash",
        "record_hash",
        "signature",
    }
)


class VerifierError(Exception):
    """Raised when an AAPP trace is malformed or semantically unsafe."""


def _as_object(value: Any, *, field: str, line_no: int) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise VerifierError(f"line {line_no}: {field} must be an object")
    return value


def _as_string(value: Any, *, field: str, line_no: int) -> str:
    if not isinstance(value, str) or not value:
        raise VerifierError(f"line {line_no}: {field} must be a non-empty string")
    return value


def load_trace_records(trace_path: str | Path) -> List[Tuple[int, Dict[str, Any]]]:
    path = Path(trace_path)
    if not path.exists():
        raise VerifierError(f"trace file does not exist: {path}")

    records: List[Tuple[int, Dict[str, Any]]] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise VerifierError(f"trace is not valid UTF-8: {path}") from exc

    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise VerifierError(f"line {line_no}: malformed JSONL: {exc.msg}") from exc

        if not isinstance(record, dict):
            raise VerifierError(f"line {line_no}: JSONL record must be an object")

        records.append((line_no, record))

    if not records:
        raise VerifierError("trace contains no records")

    return records


def validate_record_semantics(
    record: Dict[str, Any],
    *,
    line_no: int,
    expected_scope: Optional[Dict[str, Any]] = None,
) -> None:
    missing = sorted(REQUIRED_RECORD_FIELDS - set(record.keys()))
    if missing:
        raise VerifierError(
            f"line {line_no}: missing required fields: {', '.join(missing)}"
        )

    schema_version = record.get("schema_version")
    if schema_version != SUPPORTED_RECORD_SCHEMA_VERSION:
        raise VerifierError(
            f"line {line_no}: unsupported schema_version: {schema_version}"
        )

    _as_string(record.get("record_id"), field="record_id", line_no=line_no)
    _as_string(record.get("session_id"), field="session_id", line_no=line_no)
    _as_string(record.get("timestamp"), field="timestamp", line_no=line_no)
    _as_string(record.get("record_hash"), field="record_hash", line_no=line_no)

    actor = _as_object(record.get("actor"), field="actor", line_no=line_no)
    tool = _as_object(record.get("tool"), field="tool", line_no=line_no)
    record_scope = _as_object(record.get("scope"), field="scope", line_no=line_no)
    policy = _as_object(record.get("policy"), field="policy", line_no=line_no)
    redaction = _as_object(record.get("redaction"), field="redaction", line_no=line_no)
    signature = _as_object(record.get("signature"), field="signature", line_no=line_no)

    actor_type = _as_string(actor.get("actor_type"), field="actor.actor_type", line_no=line_no)
    tool_type = _as_string(tool.get("tool_type"), field="tool.tool_type", line_no=line_no)

    _as_string(policy.get("decision"), field="policy.decision", line_no=line_no)
    _as_string(signature.get("signature_type"), field="signature.signature_type", line_no=line_no)
    _as_string(signature.get("signature_value"), field="signature.signature_value", line_no=line_no)

    if redaction.get("raw_secret_stored") is True:
        raise VerifierError(f"line {line_no}: raw_secret_stored=true is forbidden")

    if record_scope.get("authorization_status") != "authorized":
        raise VerifierError(f"line {line_no}: record scope is not authorized")

    record_scope_id = _as_string(
        record_scope.get("scope_id"),
        field="scope.scope_id",
        line_no=line_no,
    )

    if expected_scope is not None:
        expected_scope_id = scope_id(expected_scope)
        if record_scope_id != expected_scope_id:
            raise VerifierError(
                f"line {line_no}: scope_id mismatch: "
                f"record={record_scope_id} expected={expected_scope_id}"
            )

        try:
            require_authorized_scope(
                scope=expected_scope,
                actor_type=actor_type,
                tool_type=tool_type,
            )
        except ScopeError as exc:
            raise VerifierError(
                f"line {line_no}: record outside authorized scope: {exc}"
            ) from exc


def validate_trace_semantics(
    trace_path: str | Path,
    scope_path: str | Path | None = None,
) -> None:
    if trace_path is None:
        raise VerifierError("trace path is required")

    expected_scope: Optional[Dict[str, Any]] = None
    if scope_path is not None:
        expected_scope = load_scope(scope_path)

    records = load_trace_records(trace_path)

    for line_no, record in records:
        validate_record_semantics(
            record,
            line_no=line_no,
            expected_scope=expected_scope,
        )
