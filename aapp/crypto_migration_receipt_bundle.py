"""Deterministic crypto migration receipt bundle reference component.

B38 boundary:
- local deterministic reference only
- no migration execution
- no key rotation
- no network
- no subprocess
- no external dependencies
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Mapping


BUNDLE_SCHEMA_VERSION = "aapp.crypto_migration_receipt_bundle.v1"

REQUIRED_SOURCE_KEYS = (
    "inventory",
    "policy_decision",
    "migration_plan",
    "dry_run",
)

READY_DRY_RUN_VERDICTS = frozenset({"READY"})

BLOCKING_DRY_RUN_VERDICTS = frozenset(
    {
        "BLOCKED",
        "DENY",
        "DENIED",
        "NOT_READY",
        "REJECTED",
        "REQUIRES_APPROVAL",
        "ERROR",
    }
)


class ReceiptBundleError(ValueError):
    """Raised when a receipt bundle cannot be generated safely."""


def canonical_json(value: Mapping[str, Any]) -> str:
    """Return deterministic canonical JSON for digesting."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(value: Mapping[str, Any]) -> str:
    """Return sha256 digest for a mapping using canonical JSON."""
    encoded = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReceiptBundleError(f"{field}_must_be_object")
    return value


def _require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReceiptBundleError(f"{field}_required")
    return value


def _require_digest(value: Any, field: str) -> str:
    digest = _require_non_empty_string(value, field)
    if not digest.startswith("sha256:") or len(digest) <= len("sha256:"):
        raise ReceiptBundleError(f"{field}_must_be_sha256_digest")
    return digest


def _collect_source_refs(dry_run_result: Mapping[str, Any]) -> Dict[str, Dict[str, str]]:
    source_refs = _require_mapping(dry_run_result.get("source_refs"), "source_refs")
    collected: Dict[str, Dict[str, str]] = {}

    for source_key in REQUIRED_SOURCE_KEYS:
        source = _require_mapping(source_refs.get(source_key), f"source_refs.{source_key}")
        collected[source_key] = {
            "ref": _require_non_empty_string(source.get("ref"), f"source_refs.{source_key}.ref"),
            "subject_ref": _require_non_empty_string(
                source.get("subject_ref"), f"source_refs.{source_key}.subject_ref"
            ),
            "resource_ref": _require_non_empty_string(
                source.get("resource_ref"), f"source_refs.{source_key}.resource_ref"
            ),
            "plan_ref": _require_non_empty_string(
                source.get("plan_ref"), f"source_refs.{source_key}.plan_ref"
            ),
            "evidence_digest": _require_digest(
                source.get("evidence_digest"), f"source_refs.{source_key}.evidence_digest"
            ),
        }

    return collected


def _validate_consistent_refs(
    dry_run_result: Mapping[str, Any],
    collected_sources: Mapping[str, Mapping[str, str]],
) -> Dict[str, str]:
    expected = {
        "subject_ref": _require_non_empty_string(dry_run_result.get("subject_ref"), "subject_ref"),
        "resource_ref": _require_non_empty_string(dry_run_result.get("resource_ref"), "resource_ref"),
        "plan_ref": _require_non_empty_string(dry_run_result.get("plan_ref"), "plan_ref"),
    }

    for source_key, source in collected_sources.items():
        for field, expected_value in expected.items():
            actual = source[field]
            if actual != expected_value:
                raise ReceiptBundleError(f"{source_key}_{field}_mismatch")

    return expected


def create_crypto_migration_receipt_bundle(dry_run_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Create deterministic tamper-evident receipt bundle from a B37 dry-run result."""
    dry_run = _require_mapping(dry_run_result, "dry_run_result")
    source_refs = _collect_source_refs(dry_run)
    core_refs = _validate_consistent_refs(dry_run, source_refs)

    dry_run_verdict = _require_non_empty_string(dry_run.get("dry_run_verdict"), "dry_run_verdict")
    normalized_verdict = dry_run_verdict.upper()

    if normalized_verdict in BLOCKING_DRY_RUN_VERDICTS:
        raise ReceiptBundleError("dry_run_verdict_not_ready")
    if normalized_verdict not in READY_DRY_RUN_VERDICTS:
        raise ReceiptBundleError("dry_run_verdict_unsupported")

    dry_run_reason_codes = dry_run.get("reason_codes", [])
    if not isinstance(dry_run_reason_codes, list) or not all(
        isinstance(item, str) for item in dry_run_reason_codes
    ):
        raise ReceiptBundleError("reason_codes_must_be_string_list")

    required_follow_up_actions = dry_run.get("required_follow_up_actions", [])
    if not isinstance(required_follow_up_actions, list) or not all(
        isinstance(item, str) for item in required_follow_up_actions
    ):
        raise ReceiptBundleError("required_follow_up_actions_must_be_string_list")

    bundle_core: Dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "receipt_status": "ISSUED",
        "subject_ref": core_refs["subject_ref"],
        "resource_ref": core_refs["resource_ref"],
        "plan_ref": core_refs["plan_ref"],
        "dry_run_verdict": normalized_verdict,
        "source_refs": copy.deepcopy(source_refs),
        "upstream_evidence_digests": {
            source_key: source_refs[source_key]["evidence_digest"]
            for source_key in REQUIRED_SOURCE_KEYS
        },
        "reason_codes": ["receipt_bundle_created"] + sorted(dry_run_reason_codes),
        "required_follow_up_actions": sorted(required_follow_up_actions),
        "execution_allowed": False,
        "production_safety_claimed": False,
        "compliance_certification_claimed": False,
    }

    bundle_digest = sha256_digest(bundle_core)
    bundle = dict(bundle_core)
    bundle["bundle_digest"] = bundle_digest
    return bundle


def verify_crypto_migration_receipt_bundle(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Verify that a B38 receipt bundle digest matches canonical bundle content."""
    candidate = _require_mapping(bundle, "bundle")
    provided_digest = _require_digest(candidate.get("bundle_digest"), "bundle_digest")

    unsigned = dict(candidate)
    unsigned.pop("bundle_digest", None)

    expected_digest = sha256_digest(unsigned)
    valid = provided_digest == expected_digest

    return {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "verification_status": "VALID" if valid else "INVALID",
        "expected_bundle_digest": expected_digest,
        "provided_bundle_digest": provided_digest,
        "reason_codes": ["bundle_digest_verified"] if valid else ["bundle_digest_mismatch"],
    }
