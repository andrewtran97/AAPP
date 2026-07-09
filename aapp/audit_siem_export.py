"""Local deterministic Audit / SIEM Export reference for AAPP."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping


SUPPORTED_FORMATS = {"ecs_json", "cef_text"}

REQUIRED_FIELDS = {
    "schema_version",
    "record_id",
    "event_kind",
    "occurred_at",
    "actor",
    "action",
    "resource",
    "policy_verdict",
    "governance_verdict",
    "evidence_digest",
}

SECRET_LIKE_MARKERS = (
    "BEGIN PRIVATE KEY",
    "PRIVATE KEY",
    "AKIA",
    "ghp_",
    "xoxb-",
    "password=",
    "secret=",
    "api_key=",
)


def export_audit_record(record: Mapping[str, Any], output_format: str) -> Dict[str, Any]:
    """Export a single evidence-shaped record to a local audit format.

    This function is deterministic and performs no network or subprocess calls.
    """

    if output_format not in SUPPORTED_FORMATS:
        return {
            "verdict": "UNSUPPORTED",
            "format": output_format,
            "reason_codes": ["UNSUPPORTED_FORMAT"],
            "export": None,
        }

    if not isinstance(record, Mapping):
        return {
            "verdict": "MALFORMED",
            "format": output_format,
            "reason_codes": ["INPUT_NOT_OBJECT"],
            "export": None,
        }

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    if missing_fields:
        return {
            "verdict": "MALFORMED",
            "format": output_format,
            "reason_codes": ["MISSING_REQUIRED_FIELD"],
            "missing_fields": missing_fields,
            "export": None,
        }

    normalized = _normalize_record(record)
    redacted = normalized["summary"] == "[REDACTED]"
    verdict = "REDACTED" if redacted else "EXPORTED"

    if output_format == "ecs_json":
        export = _to_ecs_json(normalized)
    else:
        export = _to_cef_text(normalized)

    return {
        "verdict": verdict,
        "format": output_format,
        "reason_codes": normalized["reason_codes"],
        "evidence_digest": normalized["evidence_digest"],
        "export": export,
    }


def export_audit_event(record: Mapping[str, Any], output_format: str) -> Dict[str, Any]:
    """Backward-compatible alias for audit export callers."""

    return export_audit_record(record, output_format)


def _normalize_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = deepcopy(dict(record))

    reason_codes = list(normalized.get("reason_codes") or [])
    summary = str(normalized.get("summary", ""))

    if _contains_secret_like_value(summary):
        summary = "[REDACTED]"
        if "SECRET_LIKE_VALUE_REDACTED" not in reason_codes:
            reason_codes.append("SECRET_LIKE_VALUE_REDACTED")

    normalized["summary"] = summary
    normalized["reason_codes"] = sorted(str(code) for code in reason_codes)
    return normalized


def _to_ecs_json(record: Mapping[str, Any]) -> Dict[str, Any]:
    outcome = "success"
    if str(record["policy_verdict"]).upper() in {"DENY", "BLOCKED"}:
        outcome = "failure"
    if str(record["governance_verdict"]).upper() in {"BLOCKED", "EXPORT_NOT_ALLOWED"}:
        outcome = "failure"

    return {
        "@timestamp": record["occurred_at"],
        "message": record["summary"],
        "event": {
            "kind": "event",
            "category": ["configuration"],
            "type": ["info"],
            "action": record["action"],
            "outcome": outcome,
        },
        "aapp": {
            "schema_version": record["schema_version"],
            "record_id": record["record_id"],
            "event_kind": record["event_kind"],
            "actor": record["actor"],
            "resource": record["resource"],
            "policy_verdict": record["policy_verdict"],
            "governance_verdict": record["governance_verdict"],
            "evidence_digest": record["evidence_digest"],
            "reason_codes": record["reason_codes"],
        },
    }


def _to_cef_text(record: Mapping[str, Any]) -> str:
    severity = _cef_severity(record)

    extension = {
        "rt": record["occurred_at"],
        "suser": record["actor"],
        "act": record["action"],
        "dhost": record["resource"],
        "cs1Label": "evidence_digest",
        "cs1": record["evidence_digest"],
        "cs2Label": "policy_verdict",
        "cs2": record["policy_verdict"],
        "cs3Label": "governance_verdict",
        "cs3": record["governance_verdict"],
        "cs4Label": "reason_codes",
        "cs4": ",".join(record["reason_codes"]),
        "msg": record["summary"],
    }

    extension_text = " ".join(
        f"{key}={_escape_cef_value(str(value))}" for key, value in extension.items()
    )

    header = [
        "CEF:0",
        "AAPP",
        "Agent Black Box",
        "local-reference",
        _escape_cef_header(str(record["action"])),
        _escape_cef_header(str(record["event_kind"])),
        str(severity),
    ]

    return "|".join(header) + "|" + extension_text


def _contains_secret_like_value(value: str) -> bool:
    lowered = value.lower()
    return any(marker.lower() in lowered for marker in SECRET_LIKE_MARKERS)


def _cef_severity(record: Mapping[str, Any]) -> int:
    policy = str(record["policy_verdict"]).upper()
    governance = str(record["governance_verdict"]).upper()

    if policy in {"DENY", "BLOCKED"} or governance in {"BLOCKED", "EXPORT_NOT_ALLOWED"}:
        return 8
    if policy == "REQUIRE_APPROVAL" or governance in {"REDACTED", "TRAINING_NOT_ALLOWED"}:
        return 6
    return 3


def _escape_cef_header(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _escape_cef_value(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("=", "\\=")
        .replace("\n", " ")
        .replace("\r", " ")
    )
