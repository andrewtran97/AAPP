"""Local deterministic Policy Backend Adapter reference for AAPP."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping


SUPPORTED_BACKENDS = {"local_static", "opa_json_shape"}

REQUIRED_FIELDS = {
    "schema_version",
    "request_id",
    "subject",
    "action",
    "resource",
    "policy_input_digest",
}

SUPPORTED_DECISION_VERDICTS = {"ALLOW", "DENY", "REQUIRE_APPROVAL"}


def adapt_policy_backend_request(
    request: Mapping[str, Any],
    backend: str,
) -> Dict[str, Any]:
    """Adapt an AAPP policy-shaped request to a local backend-shaped response.

    This function is deterministic and performs no network or subprocess calls.
    """

    if backend not in SUPPORTED_BACKENDS:
        return {
            "adapter_verdict": "UNSUPPORTED",
            "backend": backend,
            "reason_codes": ["UNSUPPORTED_BACKEND"],
            "decision": None,
        }

    if not isinstance(request, Mapping):
        return {
            "adapter_verdict": "MALFORMED",
            "backend": backend,
            "reason_codes": ["INPUT_NOT_OBJECT"],
            "decision": None,
        }

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in request)
    if missing_fields:
        return {
            "adapter_verdict": "MALFORMED",
            "backend": backend,
            "reason_codes": ["MISSING_REQUIRED_FIELD"],
            "missing_fields": missing_fields,
            "decision": None,
        }

    normalized = _normalize_request(request)

    if backend == "local_static":
        decision = _to_local_static_decision(normalized)
    else:
        decision = _to_opa_json_shape(normalized)

    return {
        "adapter_verdict": "ADAPTED",
        "backend": backend,
        "policy_input_digest": normalized["policy_input_digest"],
        "reason_codes": normalized["reason_codes"],
        "decision": decision,
    }


def adapt_policy_backend(
    request: Mapping[str, Any],
    backend: str,
) -> Dict[str, Any]:
    """Backward-compatible alias for policy backend adapter callers."""

    return adapt_policy_backend_request(request, backend)


def _normalize_request(request: Mapping[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = deepcopy(dict(request))

    verdict = str(normalized.get("requested_verdict", "DENY")).upper()
    reason_codes = list(normalized.get("reason_codes") or [])
    obligations = list(normalized.get("obligations") or [])

    if verdict not in SUPPORTED_DECISION_VERDICTS:
        verdict = "DENY"
        if "UNSUPPORTED_REQUESTED_VERDICT_DEFAULT_DENY" not in reason_codes:
            reason_codes.append("UNSUPPORTED_REQUESTED_VERDICT_DEFAULT_DENY")

    normalized["requested_verdict"] = verdict
    normalized["reason_codes"] = sorted(str(code) for code in reason_codes)
    normalized["obligations"] = sorted(str(obligation) for obligation in obligations)
    normalized["context"] = dict(normalized.get("context") or {})
    return normalized


def _to_local_static_decision(request: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": "aapp.policy_backend_decision.v1",
        "backend": "local_static",
        "request_id": request["request_id"],
        "subject": request["subject"],
        "action": request["action"],
        "resource": request["resource"],
        "verdict": request["requested_verdict"],
        "reason_codes": request["reason_codes"],
        "obligations": request["obligations"],
        "policy_input_digest": request["policy_input_digest"],
        "claim_boundary": "local_deterministic_reference",
    }


def _to_opa_json_shape(request: Mapping[str, Any]) -> Dict[str, Any]:
    verdict = request["requested_verdict"]
    return {
        "result": {
            "allow": verdict == "ALLOW",
            "require_approval": verdict == "REQUIRE_APPROVAL",
            "deny": verdict == "DENY",
            "verdict": verdict,
            "request_id": request["request_id"],
            "reason_codes": request["reason_codes"],
            "obligations": request["obligations"],
            "policy_input_digest": request["policy_input_digest"],
            "metadata": {
                "backend": "opa_json_shape",
                "claim_boundary": "local_deterministic_reference",
            },
        }
    }
