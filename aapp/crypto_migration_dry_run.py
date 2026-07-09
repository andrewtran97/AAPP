"""Local deterministic crypto migration dry-run reference.

B37 boundary:
- no crypto migration execution
- no key rotation
- no production mutation
- no network calls
- no subprocess calls
- no external dependencies
"""

from __future__ import annotations

from typing import Any

SUPPORTED_INPUT_SCHEMA_VERSION = "b36.crypto_migration_planner.output.v1"
OUTPUT_SCHEMA_VERSION = "b37.crypto_migration_dry_run.output.v1"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "record_id",
    "evidence_digest",
    "planner_verdict",
    "reason_codes",
    "migration_steps",
}

REQUIRED_STEP_FIELDS = {
    "finding_id",
    "algorithm",
    "use",
    "risk_level",
    "decision",
    "action",
    "recommendation",
}

SUPPORTED_PLANNER_VERDICTS = {"PLAN_REQUIRED", "NO_ACTION"}

SUPPORTED_STEP_ACTIONS = {
    "NO_ACTION",
    "REPLACE_ALGORITHM",
    "ROTATE_KEY",
    "REVIEW_USAGE",
    "DOCUMENT_EXCEPTION",
}

APPROVAL_REQUIRED_ACTIONS = {
    "REPLACE_ALGORITHM",
    "ROTATE_KEY",
    "REVIEW_USAGE",
    "DOCUMENT_EXCEPTION",
}

DESTRUCTIVE_EXECUTION_ACTIONS = {
    "APPLY_MIGRATION",
    "EXECUTE_MIGRATION",
    "DELETE_KEY",
    "DISABLE_KEY",
    "DESTROY_KEY",
    "LIVE_ROTATE_KEY",
    "PRODUCTION_ROTATE_KEY",
}

PRODUCTION_ENVIRONMENTS = {"PROD", "PRODUCTION", "LIVE"}
UNSAFE_EXECUTION_MODES = {"APPLY", "EXECUTE", "MUTATE", "LIVE", "PRODUCTION"}


def dry_run_crypto_migration(plan: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic dry-run/readiness verdict for a B36 migration plan."""
    malformed = _validate_plan_shape(plan)
    if malformed:
        return _base_output(plan, "MALFORMED", malformed, [], [])

    if plan["schema_version"] != SUPPORTED_INPUT_SCHEMA_VERSION:
        return _base_output(
            plan,
            "UNSUPPORTED",
            ["unsupported_schema_version"],
            [],
            [],
        )

    planner_verdict = str(plan["planner_verdict"]).upper()
    if planner_verdict not in SUPPORTED_PLANNER_VERDICTS:
        return _base_output(
            plan,
            "BLOCKED",
            ["unsupported_planner_verdict"],
            [],
            ["regenerate_b36_plan"],
        )

    unsafe = _detect_unsafe_execution_request(plan)
    if unsafe:
        return _base_output(
            plan,
            "BLOCKED",
            unsafe,
            [],
            ["force_dry_run_mode", "use_non_production_environment"],
        )

    unsupported = _detect_unsupported_steps(plan["migration_steps"])
    if unsupported:
        return _base_output(
            plan,
            "BLOCKED",
            unsupported,
            [],
            ["remove_unsupported_step"],
        )

    step_results = [_step_result(step) for step in _sorted_steps(plan["migration_steps"])]

    if not step_results:
        return _base_output(
            plan,
            "READY",
            ["dry_run_ready_no_migration_steps"],
            [],
            [],
        )

    if any(step["readiness"] == "REQUIRES_APPROVAL" for step in step_results):
        return _base_output(
            plan,
            "REQUIRES_APPROVAL",
            ["dry_run_only", "manual_approval_required"],
            step_results,
            _required_follow_up_actions(step_results),
        )

    return _base_output(
        plan,
        "READY",
        ["dry_run_ready"],
        step_results,
        [],
    )


def evaluate_crypto_migration_dry_run(plan: dict[str, Any]) -> dict[str, Any]:
    """Alias for callers that prefer evaluate_* naming."""
    return dry_run_crypto_migration(plan)


def _validate_plan_shape(plan: dict[str, Any]) -> list[str]:
    if not isinstance(plan, dict):
        return ["plan_not_object"]

    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(plan))
    if missing:
        return [f"missing_{field}" for field in missing]

    if not isinstance(plan.get("reason_codes"), list):
        return ["reason_codes_not_list"]

    if not isinstance(plan.get("migration_steps"), list):
        return ["migration_steps_not_list"]

    for index, step in enumerate(plan["migration_steps"]):
        if not isinstance(step, dict):
            return [f"step_{index}_not_object"]
        missing_step_fields = sorted(REQUIRED_STEP_FIELDS - set(step))
        if missing_step_fields:
            return [f"step_{index}_missing_{field}" for field in missing_step_fields]

    return []


def _detect_unsafe_execution_request(plan: dict[str, Any]) -> list[str]:
    reason_codes: list[str] = []

    for key in ("environment", "target_environment", "deployment_environment"):
        if str(plan.get(key, "")).upper() in PRODUCTION_ENVIRONMENTS:
            reason_codes.append("production_environment_not_allowed")

    for key in ("execution_mode", "mode"):
        if str(plan.get(key, "")).upper() in UNSAFE_EXECUTION_MODES:
            reason_codes.append("unsafe_execution_mode_requested")

    if plan.get("execute") is True:
        reason_codes.append("execution_requested")

    if plan.get("live_key_rotation") is True:
        reason_codes.append("live_key_rotation_requested")

    for index, step in enumerate(plan["migration_steps"]):
        action = str(step.get("action", "")).upper()
        if action in DESTRUCTIVE_EXECUTION_ACTIONS:
            reason_codes.append(f"step_{index}_destructive_action_requested")

        for key in ("environment", "target_environment", "deployment_environment"):
            if str(step.get(key, "")).upper() in PRODUCTION_ENVIRONMENTS:
                reason_codes.append(f"step_{index}_production_environment_not_allowed")

        for key in ("execution_mode", "mode"):
            if str(step.get(key, "")).upper() in UNSAFE_EXECUTION_MODES:
                reason_codes.append(f"step_{index}_unsafe_execution_mode_requested")

        if step.get("execute") is True:
            reason_codes.append(f"step_{index}_execution_requested")

        if step.get("live_key_rotation") is True:
            reason_codes.append(f"step_{index}_live_key_rotation_requested")

    return _dedupe_in_order(reason_codes)


def _detect_unsupported_steps(steps: list[dict[str, Any]]) -> list[str]:
    reason_codes: list[str] = []

    for index, step in enumerate(steps):
        action = str(step["action"]).upper()
        if action not in SUPPORTED_STEP_ACTIONS:
            reason_codes.append(f"step_{index}_unsupported_action")

    return reason_codes


def _sorted_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(steps, key=lambda step: str(step["finding_id"]))


def _step_result(step: dict[str, Any]) -> dict[str, Any]:
    action = str(step["action"]).upper()

    if action == "NO_ACTION":
        readiness = "READY"
        reason_codes = ["no_action_required"]
        follow_up_actions: list[str] = []
    elif action == "REPLACE_ALGORITHM":
        readiness = "REQUIRES_APPROVAL"
        reason_codes = ["algorithm_replacement_requires_review"]
        follow_up_actions = [
            "prepare_test_vectors",
            "review_compatibility_impact",
            "obtain_human_approval",
        ]
    elif action == "ROTATE_KEY":
        readiness = "REQUIRES_APPROVAL"
        reason_codes = ["key_rotation_requires_non_production_rehearsal"]
        follow_up_actions = [
            "run_non_production_rotation_rehearsal",
            "obtain_human_approval",
        ]
    elif action == "REVIEW_USAGE":
        readiness = "REQUIRES_APPROVAL"
        reason_codes = ["manual_crypto_usage_review_required"]
        follow_up_actions = ["complete_manual_crypto_review"]
    else:
        readiness = "REQUIRES_APPROVAL"
        reason_codes = ["document_exception_before_migration"]
        follow_up_actions = ["document_exception_and_owner"]

    return {
        "finding_id": str(step["finding_id"]),
        "algorithm": str(step["algorithm"]),
        "use": str(step["use"]),
        "risk_level": str(step["risk_level"]).upper(),
        "decision": str(step["decision"]).upper(),
        "action": action,
        "readiness": readiness,
        "reason_codes": reason_codes,
        "required_follow_up_actions": follow_up_actions,
    }


def _required_follow_up_actions(step_results: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = ["keep_execution_mode_dry_run"]

    for step in step_results:
        actions.extend(step["required_follow_up_actions"])

    return _dedupe_in_order(actions)


def _dedupe_in_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)

    return output


def _base_output(
    plan: dict[str, Any],
    verdict: str,
    reason_codes: list[str],
    step_results: list[dict[str, Any]],
    required_follow_up_actions: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "record_id": plan.get("record_id") if isinstance(plan, dict) else None,
        "evidence_digest": plan.get("evidence_digest") if isinstance(plan, dict) else None,
        "dry_run_verdict": verdict,
        "reason_codes": reason_codes,
        "required_follow_up_actions": required_follow_up_actions,
        "step_results": step_results,
    }
