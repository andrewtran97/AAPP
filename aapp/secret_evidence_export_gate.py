"""B41 Secret Evidence Export Gate.

Deterministic reference gate for exporting evidence metadata without exporting
raw secret payloads or enabling training/fine-tuning use.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA_VERSION = "b41.secret_evidence_export_gate.v1"
REDACTION = "[REDACTED_BY_B41_SECRET_EVIDENCE_EXPORT_GATE]"

ALLOWED_EXPORT_PURPOSES = {
    "audit",
    "siem",
    "compliance",
    "incident_response",
    "security_review",
}

BLOCKED_PURPOSES = {
    "train",
    "training",
    "model_training",
    "fine_tune",
    "fine-tune",
    "finetune",
}

_SECRET_VALUE_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{8,}\b", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
)

_SECRET_FIELD_HINTS = (
    "api_key",
    "authorization",
    "bearer",
    "credential",
    "password",
    "private_key",
    "secret",
    "token",
)

_NON_SECRET_CONTROL_KEYS = {
    "action",
    "boundary_verdict",
    "created_at",
    "decision",
    "digest",
    "evidence_digest",
    "export_record",
    "export_verdict",
    "original_digest",
    "policy_ref",
    "purpose",
    "raw_secret_stored",
    "reason_codes",
    "receipt_ref",
    "record_id",
    "resource",
    "sanitized_digest",
    "schema_version",
    "source_ref",
    "subject",
    "tenant",
    "verdict",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_digest(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _is_sha256_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _walk_leaf_values(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_leaf_values(child, path + (str(key),))
        return

    if _is_sequence(value):
        for index, child in enumerate(value):
            yield from _walk_leaf_values(child, path + (str(index),))
        return

    yield path, value


def _secret_like_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if value in {"", REDACTION}:
        return False
    return any(pattern.search(value) for pattern in _SECRET_VALUE_PATTERNS)


def _secret_like_field_not_redacted(path: tuple[str, ...], value: Any) -> bool:
    if not path:
        return False

    key = path[-1].lower()
    if key in _NON_SECRET_CONTROL_KEYS:
        return False

    if not any(hint in key for hint in _SECRET_FIELD_HINTS):
        return False

    return value not in (None, "", False, REDACTION)


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def evaluate_secret_evidence_export(record: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate whether sanitized evidence metadata is safe to export."""
    if not isinstance(record, Mapping):
        return {
            "schema_version": SCHEMA_VERSION,
            "verdict": "BLOCKED",
            "reason_codes": ["malformed_record"],
            "original_digest": None,
            "sanitized_digest": None,
        }

    reason_codes: list[str] = []

    purpose = str(record.get("purpose", "")).lower()
    if purpose in BLOCKED_PURPOSES:
        reason_codes.append("training_purpose_blocked")
    if purpose not in ALLOWED_EXPORT_PURPOSES:
        reason_codes.append("purpose_not_export_safe")

    original_digest = record.get("original_digest")
    if not _is_sha256_digest(original_digest):
        reason_codes.append("missing_or_invalid_original_digest")

    boundary_verdict = record.get("boundary_verdict")
    if boundary_verdict not in {"ALLOWED", "REDACTED"}:
        reason_codes.append("missing_or_invalid_boundary_verdict")

    if record.get("raw_secret_stored") is True:
        reason_codes.append("raw_secret_stored_true")

    export_record = record.get("export_record")
    sanitized_digest = None

    if not isinstance(export_record, Mapping):
        reason_codes.append("missing_or_malformed_export_record")
    else:
        sanitized_digest = compute_digest(export_record)

        supplied_sanitized_digest = record.get("sanitized_digest")
        if supplied_sanitized_digest is not None and supplied_sanitized_digest != sanitized_digest:
            reason_codes.append("sanitized_digest_mismatch")

        for path, value in _walk_leaf_values(export_record):
            if _secret_like_value(value):
                reason_codes.append("inline_secret_like_value_detected")
            if _secret_like_field_not_redacted(path, value):
                reason_codes.append("secret_like_field_not_redacted")

    reason_codes = _dedupe(reason_codes)
    verdict = "BLOCKED" if reason_codes else "ALLOWED"

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "reason_codes": reason_codes or ["secret_safe_export_allowed"],
        "original_digest": original_digest if _is_sha256_digest(original_digest) else None,
        "sanitized_digest": sanitized_digest,
    }

    if verdict == "ALLOWED":
        result["export_record"] = export_record

    return result
