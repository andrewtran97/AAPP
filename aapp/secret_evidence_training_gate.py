"""B42 Secret Evidence Training Gate.

Deterministic reference gate for deciding whether evidence records may be used
for training, model training, fine-tuning, or dataset construction.

The gate must not export, log, train on, or inline raw secret payloads.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

SCHEMA_VERSION = "b42.secret_evidence_training_gate.v1"
REDACTION = "[REDACTED_BY_B42_SECRET_EVIDENCE_TRAINING_GATE]"

TRAINING_PURPOSES = {
    "train",
    "training",
    "model_training",
    "fine_tune",
    "fine-tune",
    "finetune",
    "dataset_build",
    "dataset",
}

_SECRET_VALUE_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{8,}\b", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|gho|ghu|github_pat)_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{12,}\b"),
)

_NON_SECRET_CONTROL_KEYS = {
    "record_id",
    "schema_version",
    "purpose",
    "action",
    "boundary",
    "classification",
    "secret_classification",
    "raw_secret_stored",
    "training_allowed",
    "allow_sanitized_metadata",
    "digest",
    "original_digest",
    "evidence_digest",
    "receipt_digest",
    "reason_codes",
    "source",
    "source_trace",
    "policy_ref",
    "decision_ref",
}


def _canonical(data: Mapping[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(data: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _is_training_purpose(purpose: Any) -> bool:
    return isinstance(purpose, str) and purpose.strip().lower() in TRAINING_PURPOSES


def _contains_secret_like_value(value: Any) -> bool:
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in _SECRET_VALUE_PATTERNS)

    if isinstance(value, Mapping):
        return any(_contains_secret_like_value(v) for v in value.values())

    if isinstance(value, list):
        return any(_contains_secret_like_value(v) for v in value)

    return False


def _secret_like_payload_paths(data: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text

            if key_text not in _NON_SECRET_CONTROL_KEYS and _contains_secret_like_value(value):
                findings.append(path)

            findings.extend(_secret_like_payload_paths(value, path))

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            findings.extend(_secret_like_payload_paths(item, f"{prefix}[{idx}]"))

    return sorted(set(findings))


def _sanitize(data: Any) -> Any:
    if isinstance(data, Mapping):
        sanitized: dict[str, Any] = {}
        for key, value in data.items():
            if _contains_secret_like_value(value):
                sanitized[str(key)] = REDACTION
            else:
                sanitized[str(key)] = _sanitize(value)
        return sanitized

    if isinstance(data, list):
        return [_sanitize(item) for item in data]

    if isinstance(data, str) and _contains_secret_like_value(data):
        return REDACTION

    return data


def evaluate_training_gate(record: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate whether an evidence record may be used for training."""
    if not isinstance(record, Mapping):
        return {
            "schema_version": SCHEMA_VERSION,
            "verdict": "MALFORMED",
            "reason_codes": ["record_must_be_object"],
        }

    record_id = record.get("record_id")
    purpose = record.get("purpose")

    if not isinstance(record_id, str) or not record_id.strip():
        return {
            "schema_version": SCHEMA_VERSION,
            "verdict": "MALFORMED",
            "reason_codes": ["missing_record_id"],
        }

    if not isinstance(purpose, str) or not purpose.strip():
        return {
            "schema_version": SCHEMA_VERSION,
            "record_id": record_id,
            "verdict": "MALFORMED",
            "reason_codes": ["missing_purpose"],
        }

    raw_secret_stored = bool(record.get("raw_secret_stored", False))
    training_purpose = _is_training_purpose(purpose)
    payload_paths = _secret_like_payload_paths(record)
    sanitized = _sanitize(record)

    reason_codes: list[str] = []

    if training_purpose and raw_secret_stored:
        reason_codes.append("training_on_raw_secret_record_blocked")

    if training_purpose and payload_paths:
        reason_codes.append("training_on_secret_like_payload_blocked")

    if training_purpose and record.get("training_allowed") is False:
        reason_codes.append("training_explicitly_disallowed")

    if reason_codes:
        verdict = "BLOCKED"
    else:
        verdict = "ALLOWED"
        reason_codes.append("no_training_secret_boundary_violation")

    return {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "purpose": purpose,
        "training_purpose": training_purpose,
        "verdict": verdict,
        "reason_codes": sorted(set(reason_codes)),
        "original_digest": _digest(record),
        "sanitized_record": sanitized,
        "secret_like_paths": payload_paths,
    }
