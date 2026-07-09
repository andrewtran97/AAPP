"""Local deterministic Tenant Boundary / Enterprise Data Isolation gate."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


REQUIRED_FIELDS = {
    "request_id",
    "source_tenant",
    "destination_tenant",
    "action",
    "has_governance_verdict",
    "evidence_digest",
}

ALLOWED = "ALLOWED"
MALFORMED = "MALFORMED"
TENANT_BOUNDARY_VIOLATION = "TENANT_BOUNDARY_VIOLATION"
CROSS_TENANT_EXPORT_NOT_ALLOWED = "CROSS_TENANT_EXPORT_NOT_ALLOWED"
CROSS_TENANT_TRAINING_NOT_ALLOWED = "CROSS_TENANT_TRAINING_NOT_ALLOWED"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
GOVERNANCE_VERDICT_REQUIRED = "GOVERNANCE_VERDICT_REQUIRED"

EXPORT_ACTIONS = {"export", "report", "evidence_release"}
TRAINING_ACTIONS = {"train", "training", "model_training", "fine_tuning", "dataset_build"}


def _stable_digest(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def evaluate_tenant_boundary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate tenant-boundary safety for a local deterministic request.

    This reference gate does not call networks, subprocesses, databases, or external services.
    """

    if not isinstance(payload, dict):
        return {
            "verdict": MALFORMED,
            "reason_codes": ["PAYLOAD_NOT_OBJECT"],
            "evidence_digest": None,
        }

    missing = sorted(field for field in REQUIRED_FIELDS if field not in payload)
    if missing:
        return {
            "verdict": MALFORMED,
            "reason_codes": ["MISSING_REQUIRED_FIELD"],
            "missing_fields": missing,
            "evidence_digest": payload.get("evidence_digest"),
        }

    source_tenant = payload.get("source_tenant")
    destination_tenant = payload.get("destination_tenant")
    action = str(payload.get("action", "")).lower()
    has_approval = bool(payload.get("approval_ref"))
    has_governance_verdict = bool(payload.get("has_governance_verdict"))

    if not source_tenant or not destination_tenant or not action:
        return {
            "verdict": MALFORMED,
            "reason_codes": ["EMPTY_REQUIRED_FIELD"],
            "evidence_digest": payload.get("evidence_digest"),
        }

    cross_tenant = source_tenant != destination_tenant

    if cross_tenant and action in TRAINING_ACTIONS:
        return {
            "verdict": CROSS_TENANT_TRAINING_NOT_ALLOWED,
            "reason_codes": ["CROSS_TENANT_TRAINING_BLOCKED"],
            "evidence_digest": payload["evidence_digest"],
        }

    if cross_tenant and action in EXPORT_ACTIONS and not has_governance_verdict:
        return {
            "verdict": GOVERNANCE_VERDICT_REQUIRED,
            "reason_codes": ["GOVERNANCE_VERDICT_REQUIRED_FOR_CROSS_TENANT_RELEASE"],
            "evidence_digest": payload["evidence_digest"],
        }

    if cross_tenant and action in EXPORT_ACTIONS and not has_approval:
        return {
            "verdict": CROSS_TENANT_EXPORT_NOT_ALLOWED,
            "reason_codes": ["CROSS_TENANT_EXPORT_REQUIRES_APPROVAL"],
            "evidence_digest": payload["evidence_digest"],
        }

    if cross_tenant and not has_approval:
        return {
            "verdict": TENANT_BOUNDARY_VIOLATION,
            "reason_codes": ["TENANT_MISMATCH"],
            "evidence_digest": payload["evidence_digest"],
        }

    return {
        "verdict": ALLOWED,
        "reason_codes": ["TENANT_BOUNDARY_OK"],
        "cross_tenant": cross_tenant,
        "request_digest": _stable_digest(payload),
        "evidence_digest": payload["evidence_digest"],
    }
