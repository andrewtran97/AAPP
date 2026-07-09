"""Local deterministic crypto migration planner reference.

B36 boundary:
- no migration execution
- no production mutation
- no network calls
- no subprocess calls
"""

from __future__ import annotations

from typing import Any

SUPPORTED_SCHEMA_VERSION = "b36.crypto_migration_planner.input.v1"
OUTPUT_SCHEMA_VERSION = "b36.crypto_migration_planner.output.v1"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "record_id",
    "evidence_digest",
    "policy_verdict",
    "findings",
}

REQUIRED_FINDING_FIELDS = {
    "finding_id",
    "algorithm",
    "use",
    "risk_level",
    "decision",
    "recommendation",
}

DISALLOW_DECISIONS = {"DISALLOW", "REPLACE", "ROTATE", "MIGRATION_REQUIRED"}
APPROVAL_DECISIONS = {"REQUIRE_APPROVAL", "REVIEW"}
ALLOW_DECISIONS = {"ALLOW", "ACCEPT", "NO_ACTION"}


def plan_crypto_migration(record: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic migration plan for a crypto policy decision record."""
    malformed = _validate_record_shape(record)
    if malformed:
        return _base_output(record, "MALFORMED", malformed, [])

    if record["schema_version"] != SUPPORTED_SCHEMA_VERSION:
        return _base_output(
            record,
            "UNSUPPORTED",
            ["unsupported_schema_version"],
            [],
        )

    findings = record["findings"]
    steps = [_step_for_finding(finding) for finding in findings]
    actionable_steps = [step for step in steps if step["action"] != "NO_ACTION"]

    if actionable_steps:
        return _base_output(
            record,
            "PLAN_REQUIRED",
            ["migration_required"],
            sorted(actionable_steps, key=lambda item: item["finding_id"]),
        )

    return _base_output(
        record,
        "NO_ACTION",
        ["no_crypto_migration_required"],
        [],
    )


def _validate_record_shape(record: dict[str, Any]) -> list[str]:
    if not isinstance(record, dict):
        return ["record_not_object"]

    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(record))
    if missing:
        return [f"missing_{field}" for field in missing]

    if not isinstance(record.get("findings"), list):
        return ["findings_not_list"]

    for index, finding in enumerate(record["findings"]):
        if not isinstance(finding, dict):
            return [f"finding_{index}_not_object"]
        missing_finding = sorted(REQUIRED_FINDING_FIELDS - set(finding))
        if missing_finding:
            return [f"finding_{index}_missing_{field}" for field in missing_finding]

    return []


def _step_for_finding(finding: dict[str, Any]) -> dict[str, Any]:
    decision = str(finding["decision"]).upper()
    recommendation = str(finding["recommendation"])

    if decision in DISALLOW_DECISIONS:
        action = _action_from_recommendation(recommendation)
    elif decision in APPROVAL_DECISIONS:
        action = "REVIEW_USAGE"
    elif decision in ALLOW_DECISIONS:
        action = "NO_ACTION"
    else:
        action = "DOCUMENT_EXCEPTION"

    return {
        "finding_id": str(finding["finding_id"]),
        "algorithm": str(finding["algorithm"]),
        "use": str(finding["use"]),
        "risk_level": str(finding["risk_level"]).upper(),
        "decision": decision,
        "action": action,
        "recommendation": recommendation,
    }


def _action_from_recommendation(recommendation: str) -> str:
    normalized = recommendation.lower()

    if "rotate" in normalized:
        return "ROTATE_KEY"
    if "replace" in normalized:
        return "REPLACE_ALGORITHM"
    if "review" in normalized:
        return "REVIEW_USAGE"

    return "DOCUMENT_EXCEPTION"


def _base_output(
    record: dict[str, Any],
    verdict: str,
    reason_codes: list[str],
    migration_steps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "record_id": record.get("record_id") if isinstance(record, dict) else None,
        "evidence_digest": record.get("evidence_digest") if isinstance(record, dict) else None,
        "planner_verdict": verdict,
        "reason_codes": reason_codes,
        "migration_steps": migration_steps,
    }
