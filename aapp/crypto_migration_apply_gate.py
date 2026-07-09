"""B39 Crypto Migration Apply Gate.

Reference-only deterministic gate for a future production apply path.
It does not execute migrations, call subprocesses, touch network, or mutate files.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


B39_SCHEMA_VERSION = "b39.crypto_migration_apply_gate.v1"
B38_RECEIPT_SCHEMA_VERSION = "b38.crypto_migration_receipt_bundle.v1"

ALLOWED_REQUEST_ACTION = "apply_migration"
ALLOWED_ENVIRONMENT = "production"
ALLOWED_DRY_RUN_VERDICTS = {"PASSED", "DRY_RUN_PASSED", "ALLOW", "ALLOWED"}
ALLOWED_POLICY_VERDICTS = {"ALLOW", "ALLOWED", "APPROVED"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_sha256_digest(value: Any) -> bool:
    return _is_non_empty_string(value) and value.startswith("sha256:") and len(value) > len("sha256:")


def evaluate_crypto_migration_apply_gate(payload: dict[str, Any]) -> dict[str, Any]:
    """Evaluate whether a crypto migration is ready for a future apply step.

    Returns a deterministic verdict only. This function never performs the apply.
    """

    if not isinstance(payload, dict):
        return {
            "schema_version": B39_SCHEMA_VERSION,
            "verdict": "MALFORMED",
            "allowed_to_apply": False,
            "execution_performed": False,
            "reason_codes": ["payload_not_object"],
            "evidence_digest": _digest({"malformed": True}),
        }

    reason_codes: list[str] = []

    request_id = payload.get("request_id")
    requested_action = payload.get("requested_action")
    environment = payload.get("environment")
    receipt_bundle = payload.get("receipt_bundle")

    if not _is_non_empty_string(request_id):
        reason_codes.append("missing_request_id")

    if requested_action != ALLOWED_REQUEST_ACTION:
        reason_codes.append("unsupported_requested_action")

    if environment != ALLOWED_ENVIRONMENT:
        reason_codes.append("unsupported_environment")

    if not isinstance(receipt_bundle, dict):
        reason_codes.append("missing_receipt_bundle")
        receipt_bundle = {}

    receipt_schema = receipt_bundle.get("schema_version")
    receipt_digest = receipt_bundle.get("receipt_digest")
    migration_plan_ref = receipt_bundle.get("migration_plan_ref")
    dry_run_verdict = receipt_bundle.get("dry_run_verdict")
    policy_verdict = receipt_bundle.get("policy_verdict")
    tamper_evident = receipt_bundle.get("tamper_evident")

    if receipt_schema != B38_RECEIPT_SCHEMA_VERSION:
        reason_codes.append("unsupported_receipt_schema")

    if not _has_sha256_digest(receipt_digest):
        reason_codes.append("missing_or_invalid_receipt_digest")

    if not _is_non_empty_string(migration_plan_ref):
        reason_codes.append("missing_migration_plan_ref")

    if dry_run_verdict not in ALLOWED_DRY_RUN_VERDICTS:
        reason_codes.append("dry_run_not_passed")

    if policy_verdict not in ALLOWED_POLICY_VERDICTS:
        reason_codes.append("policy_not_allowed")

    if tamper_evident is not True:
        reason_codes.append("receipt_not_tamper_evident")

    verdict = "APPLY_READY" if not reason_codes else "BLOCKED"

    gate_record = {
        "schema_version": B39_SCHEMA_VERSION,
        "request_id": request_id,
        "requested_action": requested_action,
        "environment": environment,
        "receipt_digest": receipt_digest,
        "migration_plan_ref": migration_plan_ref,
        "dry_run_verdict": dry_run_verdict,
        "policy_verdict": policy_verdict,
        "tamper_evident": tamper_evident,
        "verdict": verdict,
        "reason_codes": reason_codes,
        "execution_performed": False,
    }

    return {
        "schema_version": B39_SCHEMA_VERSION,
        "verdict": verdict,
        "allowed_to_apply": verdict == "APPLY_READY",
        "execution_performed": False,
        "reason_codes": reason_codes,
        "required_next_step": "human_apply_confirmation" if verdict == "APPLY_READY" else "fix_blocking_reasons",
        "receipt_digest": receipt_digest,
        "migration_plan_ref": migration_plan_ref,
        "evidence_digest": _digest(gate_record),
    }
