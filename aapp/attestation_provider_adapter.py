from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

REQUEST_SCHEMA = "aapp.attestation_provider_request.v1"
EVIDENCE_SCHEMA = "aapp.attestation_provider_evidence.v1"
VERDICT_SCHEMA = "aapp.attestation_provider_verdict.v1"

VERIFIED = "VERIFIED"
UNTRUSTED = "UNTRUSTED"
STALE = "STALE"
NONCE_MISMATCH = "NONCE_MISMATCH"
IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
MALFORMED = "MALFORMED"
UNSUPPORTED = "UNSUPPORTED"

SUPPORTED_PROVIDERS = {"local_static", "tee_attestation_shape"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def evidence_digest(evidence: dict[str, Any]) -> str:
    clean = dict(evidence)
    clean.pop("evidence_digest", None)
    return "sha256:" + hashlib.sha256(canonical_json(clean)).hexdigest()


def parse_utc_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.][0-9]{1,6})?Z", value) is None:
        raise ValueError("timestamp_must_be_utc_rfc3339")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.tzinfo is None:
        raise ValueError("timestamp_timezone_missing")
    return parsed.astimezone(timezone.utc)


REQUEST_REQUIRED_FIELDS = (
    "schema_version",
    "request_id",
    "provider_type",
    "workload_identity_ref",
    "expected_artifact_digest",
    "expected_runtime_digest",
    "expected_policy_version",
    "expected_nonce",
    "expected_evidence_digest",
    "evaluated_at",
    "max_age_seconds",
    "max_future_skew_seconds",
)

EVIDENCE_REQUIRED_FIELDS = (
    "schema_version",
    "provider_type",
    "workload_identity_ref",
    "artifact_digest",
    "runtime_digest",
    "policy_version",
    "nonce",
    "attestation_timestamp",
    "trusted",
    "evidence_digest",
)

CHECK_NAMES = (
    "schema_valid",
    "provider_supported",
    "evidence_digest_valid",
    "provider_matches",
    "trusted",
    "timestamp_valid",
    "nonce_matches",
    "identity_matches",
    "artifact_matches",
    "runtime_matches",
    "policy_matches",
)


def _new_checks() -> dict[str, bool]:
    return {name: False for name in CHECK_NAMES}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_non_negative_int(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def _missing_field(
    value: dict[str, Any],
    required_fields: tuple[str, ...],
) -> str | None:
    for field in required_fields:
        if field not in value:
            return field
    return None


def _is_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and DIGEST_RE.fullmatch(value) is not None
    )


def _result(
    request: Any,
    evidence: Any,
    *,
    verdict: str,
    reason_code: str,
    checks: dict[str, bool],
) -> dict[str, Any]:
    request_obj = request if isinstance(request, dict) else {}
    evidence_obj = evidence if isinstance(evidence, dict) else {}

    return {
        "schema_version": VERDICT_SCHEMA,
        "request_id": request_obj.get("request_id"),
        "provider_type": request_obj.get("provider_type"),
        "workload_identity_ref": evidence_obj.get(
            "workload_identity_ref"
        ),
        "artifact_digest": evidence_obj.get("artifact_digest"),
        "runtime_digest": evidence_obj.get("runtime_digest"),
        "policy_version": evidence_obj.get("policy_version"),
        "nonce": evidence_obj.get("nonce"),
        "attestation_timestamp": evidence_obj.get(
            "attestation_timestamp"
        ),
        "source_evidence_digest": evidence_obj.get(
            "evidence_digest"
        ),
        "verdict": verdict,
        "reason_codes": [reason_code],
        "checks": dict(checks),
    }


REQUEST_STRING_FIELDS = (
    "schema_version",
    "request_id",
    "provider_type",
    "workload_identity_ref",
    "expected_policy_version",
    "expected_nonce",
    "evaluated_at",
)

REQUEST_DIGEST_FIELDS = (
    "expected_artifact_digest",
    "expected_runtime_digest",
    "expected_evidence_digest",
)

REQUEST_INTEGER_FIELDS = (
    "max_age_seconds",
    "max_future_skew_seconds",
)

EVIDENCE_STRING_FIELDS = (
    "schema_version",
    "provider_type",
    "workload_identity_ref",
    "policy_version",
    "nonce",
    "attestation_timestamp",
)

EVIDENCE_DIGEST_FIELDS = (
    "artifact_digest",
    "runtime_digest",
    "evidence_digest",
)


def _validate_request_shape(
    request: Any,
) -> tuple[str, str] | None:
    if not isinstance(request, dict):
        return MALFORMED, "REQUEST_NOT_OBJECT"

    missing = _missing_field(request, REQUEST_REQUIRED_FIELDS)
    if missing is not None:
        return (
            MALFORMED,
            f"MISSING_REQUIRED_FIELD:request.{missing}",
        )

    for field in REQUEST_STRING_FIELDS:
        if not _is_non_empty_string(request[field]):
            return (
                MALFORMED,
                f"INVALID_FIELD_TYPE:request.{field}",
            )

    for field in REQUEST_DIGEST_FIELDS:
        if not _is_digest(request[field]):
            return (
                MALFORMED,
                f"INVALID_DIGEST_FORMAT:request.{field}",
            )

    for field in REQUEST_INTEGER_FIELDS:
        if not _is_non_negative_int(request[field]):
            return (
                MALFORMED,
                f"INVALID_FIELD_TYPE:request.{field}",
            )

    if request["schema_version"] != REQUEST_SCHEMA:
        return UNSUPPORTED, "UNSUPPORTED_SCHEMA_VERSION:request"

    if request["provider_type"] not in SUPPORTED_PROVIDERS:
        return UNSUPPORTED, "UNSUPPORTED_PROVIDER:request"

    return None


def _validate_evidence_shape(
    evidence: Any,
) -> tuple[str, str] | None:
    if not isinstance(evidence, dict):
        return MALFORMED, "EVIDENCE_NOT_OBJECT"

    missing = _missing_field(evidence, EVIDENCE_REQUIRED_FIELDS)
    if missing is not None:
        return (
            MALFORMED,
            f"MISSING_REQUIRED_FIELD:evidence.{missing}",
        )

    for field in EVIDENCE_STRING_FIELDS:
        if not _is_non_empty_string(evidence[field]):
            return (
                MALFORMED,
                f"INVALID_FIELD_TYPE:evidence.{field}",
            )

    for field in EVIDENCE_DIGEST_FIELDS:
        if not _is_digest(evidence[field]):
            return (
                MALFORMED,
                f"INVALID_DIGEST_FORMAT:evidence.{field}",
            )

    if not isinstance(evidence["trusted"], bool):
        return (
            MALFORMED,
            "INVALID_FIELD_TYPE:evidence.trusted",
        )

    if evidence["schema_version"] != EVIDENCE_SCHEMA:
        return UNSUPPORTED, "UNSUPPORTED_SCHEMA_VERSION:evidence"

    if evidence["provider_type"] not in SUPPORTED_PROVIDERS:
        return UNSUPPORTED, "UNSUPPORTED_PROVIDER:evidence"

    return None


def _evaluate_timestamp_window(
    request: dict[str, Any],
    evidence: dict[str, Any],
) -> tuple[str, str] | None:
    try:
        evaluated_at = parse_utc_timestamp(request["evaluated_at"])
    except (TypeError, ValueError):
        return (
            MALFORMED,
            "INVALID_TIMESTAMP:request.evaluated_at",
        )

    try:
        attestation_timestamp = parse_utc_timestamp(
            evidence["attestation_timestamp"]
        )
    except (TypeError, ValueError):
        return (
            MALFORMED,
            "INVALID_TIMESTAMP:evidence.attestation_timestamp",
        )

    age_seconds = (
        evaluated_at - attestation_timestamp
    ).total_seconds()

    if age_seconds < -request["max_future_skew_seconds"]:
        return STALE, "EVIDENCE_FROM_FUTURE"

    if age_seconds > request["max_age_seconds"]:
        return STALE, "EVIDENCE_STALE"

    return None


def evaluate_attestation_provider(
    request: Any,
    evidence: Any,
) -> dict[str, Any]:
    checks = _new_checks()

    request_error = _validate_request_shape(request)
    if request_error is not None:
        verdict, reason_code = request_error
        return _result(
            request,
            evidence,
            verdict=verdict,
            reason_code=reason_code,
            checks=checks,
        )

    evidence_error = _validate_evidence_shape(evidence)
    if evidence_error is not None:
        verdict, reason_code = evidence_error
        return _result(
            request,
            evidence,
            verdict=verdict,
            reason_code=reason_code,
            checks=checks,
        )

    checks["schema_valid"] = True
    checks["provider_supported"] = True

    try:
        calculated_digest = evidence_digest(evidence)
    except (TypeError, ValueError, RecursionError):
        return _result(
            request,
            evidence,
            verdict=MALFORMED,
            reason_code="EVIDENCE_CANONICALIZATION_FAILED",
            checks=checks,
        )

    if (
        calculated_digest != evidence["evidence_digest"]
        or calculated_digest != request["expected_evidence_digest"]
    ):
        return _result(
            request,
            evidence,
            verdict=DIGEST_MISMATCH,
            reason_code="EVIDENCE_DIGEST_MISMATCH",
            checks=checks,
        )

    checks["evidence_digest_valid"] = True

    if request["provider_type"] != evidence["provider_type"]:
        return _result(
            request,
            evidence,
            verdict=DIGEST_MISMATCH,
            reason_code="PROVIDER_TYPE_MISMATCH",
            checks=checks,
        )

    checks["provider_matches"] = True

    if not evidence["trusted"]:
        return _result(
            request,
            evidence,
            verdict=UNTRUSTED,
            reason_code="EVIDENCE_UNTRUSTED",
            checks=checks,
        )

    checks["trusted"] = True

    timestamp_error = _evaluate_timestamp_window(
        request,
        evidence,
    )
    if timestamp_error is not None:
        verdict, reason_code = timestamp_error
        return _result(
            request,
            evidence,
            verdict=verdict,
            reason_code=reason_code,
            checks=checks,
        )

    checks["timestamp_valid"] = True

    if request["expected_nonce"] != evidence["nonce"]:
        return _result(
            request,
            evidence,
            verdict=NONCE_MISMATCH,
            reason_code="NONCE_MISMATCH",
            checks=checks,
        )

    checks["nonce_matches"] = True

    if (
        request["workload_identity_ref"]
        != evidence["workload_identity_ref"]
    ):
        return _result(
            request,
            evidence,
            verdict=IDENTITY_MISMATCH,
            reason_code="WORKLOAD_IDENTITY_MISMATCH",
            checks=checks,
        )

    checks["identity_matches"] = True

    if (
        request["expected_artifact_digest"]
        != evidence["artifact_digest"]
    ):
        return _result(
            request,
            evidence,
            verdict=DIGEST_MISMATCH,
            reason_code="ARTIFACT_DIGEST_MISMATCH",
            checks=checks,
        )

    checks["artifact_matches"] = True

    if (
        request["expected_runtime_digest"]
        != evidence["runtime_digest"]
    ):
        return _result(
            request,
            evidence,
            verdict=DIGEST_MISMATCH,
            reason_code="RUNTIME_DIGEST_MISMATCH",
            checks=checks,
        )

    checks["runtime_matches"] = True

    if (
        request["expected_policy_version"]
        != evidence["policy_version"]
    ):
        return _result(
            request,
            evidence,
            verdict=DIGEST_MISMATCH,
            reason_code="POLICY_VERSION_MISMATCH",
            checks=checks,
        )

    checks["policy_matches"] = True

    return _result(
        request,
        evidence,
        verdict=VERIFIED,
        reason_code="ALL_CHECKS_PASSED",
        checks=checks,
    )
