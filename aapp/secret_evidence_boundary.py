"""B40 Secret Evidence Boundary.

This module creates deterministic boundary decisions for evidence records that
may contain secret-like fields. It never returns the original record when a
secret-like value is detected; only a sanitized record plus digests/reason codes.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

SCHEMA_VERSION = "b40.secret_evidence_boundary.v1"
REDACTION = "[REDACTED_BY_B40_SECRET_EVIDENCE_BOUNDARY]"

_SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "access_key",
    "auth",
    "authorization",
    "bearer",
    "client_secret",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
    "token",
)

_SECRET_VALUE_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{8,}\b", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}\b"),
)

# These are AAPP boundary/control metadata keys, not user secret payload keys.
# Without this allowlist, raw_secret_stored=False is falsely redacted because
# the key contains the substring "secret".
_NON_SECRET_CONTROL_KEYS = {
    "action",
    "boundary",
    "raw_secret_stored",
    "record_id",
    "schema_version",
    "verdict",
}

_TRAINING_PURPOSES = {"train", "training", "model_training", "fine_tune", "fine-tune"}


def canonical_json(value: Any) -> str:
    """Return deterministic JSON for digesting evidence safely."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_value(value: Any) -> str:
    """Return a sha256 digest over canonical JSON."""
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _normalize_key(key: str) -> str:
    return key.lower().replace("-", "_").replace(" ", "_")


def _is_secret_key(key: str) -> bool:
    normalized = _normalize_key(key)
    if normalized in _NON_SECRET_CONTROL_KEYS:
        return False
    return any(marker in normalized for marker in _SECRET_KEY_MARKERS)


def _is_secret_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return any(pattern.search(value) for pattern in _SECRET_VALUE_PATTERNS)


def _redact(value: Any, path: str, secret_paths: list[str]) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for raw_key, raw_child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"

            if _is_secret_key(key):
                secret_paths.append(child_path)
                sanitized[key] = REDACTION
                continue

            sanitized[key] = _redact(raw_child, child_path, secret_paths)
        return sanitized

    if isinstance(value, list):
        return [_redact(child, f"{path}[{index}]", secret_paths) for index, child in enumerate(value)]

    if _is_secret_value(value):
        secret_paths.append(path)
        return REDACTION

    return value


def evaluate_secret_evidence_boundary(record: Any, purpose: str = "export") -> dict[str, Any]:
    """Evaluate and sanitize an evidence record at the secret boundary.

    Verdict contract:
    - MALFORMED: input is not an object.
    - BLOCKED: raw secret storage is declared, or secret-like data is used for training.
    - REDACTED: secret-like data exists but can be represented safely after redaction.
    - ALLOWED: no secret-like data was detected.
    """
    normalized_purpose = purpose.lower().replace("-", "_").strip()

    if not isinstance(record, Mapping):
        return {
            "schema_version": SCHEMA_VERSION,
            "purpose": normalized_purpose,
            "verdict": "MALFORMED",
            "reason_codes": ["record_must_be_object"],
            "original_digest": digest_value(record),
            "sanitized_digest": digest_value(None),
            "redaction_count": 0,
            "secret_paths": [],
            "sanitized_record": None,
            "boundary": {
                "export_raw_secret": False,
                "log_raw_secret": False,
                "train_on_raw_secret": False,
            },
        }

    secret_paths: list[str] = []
    sanitized_record = _redact(record, "$", secret_paths)
    secret_paths = sorted(set(secret_paths))
    redaction_count = len(secret_paths)

    raw_secret_stored = bool(record.get("raw_secret_stored") is True)
    reason_codes: list[str] = []

    if raw_secret_stored:
        reason_codes.append("raw_secret_storage_declared")
    if redaction_count:
        reason_codes.append("secret_like_field_redacted")

    if raw_secret_stored:
        verdict = "BLOCKED"
    elif redaction_count and normalized_purpose in _TRAINING_PURPOSES:
        verdict = "BLOCKED"
        reason_codes.append("training_on_secret_like_value_blocked")
    elif redaction_count:
        verdict = "REDACTED"
    else:
        verdict = "ALLOWED"
        reason_codes.append("no_secret_like_value_detected")

    return {
        "schema_version": SCHEMA_VERSION,
        "purpose": normalized_purpose,
        "verdict": verdict,
        "reason_codes": sorted(set(reason_codes)),
        "original_digest": digest_value(record),
        "sanitized_digest": digest_value(sanitized_record),
        "redaction_count": redaction_count,
        "secret_paths": secret_paths,
        "sanitized_record": sanitized_record,
        "boundary": {
            "export_raw_secret": False,
            "log_raw_secret": False,
            "train_on_raw_secret": False,
        },
    }
