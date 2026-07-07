from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "aapp.state_ledger.v1"

CAPABILITIES = {
    "filesystem",
    "repo",
    "cloud",
    "database",
    "deployment",
    "network",
    "payment",
    "unknown",
}


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    data = _canonical_json(obj).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def classify_action(action: dict[str, Any]) -> str:
    capability = str(action.get("capability", "unknown")).lower()
    if capability in CAPABILITIES:
        return capability

    op = str(action.get("operation", "")).lower()
    if any(x in op for x in ["file", "write", "delete_file"]):
        return "filesystem"
    if any(x in op for x in ["repo", "branch", "pr", "release", "commit"]):
        return "repo"
    if any(x in op for x in ["aws", "gcloud", "az", "cloud"]):
        return "cloud"
    if any(x in op for x in ["db", "database", "sql", "row"]):
        return "database"
    if any(x in op for x in ["deploy", "kubectl", "terraform"]):
        return "deployment"
    if any(x in op for x in ["http", "network", "webhook", "notify"]):
        return "network"
    if any(x in op for x in ["payment", "refund", "charge", "stripe"]):
        return "payment"
    return "unknown"


def reversal_for(action: dict[str, Any]) -> dict[str, Any]:
    capability = classify_action(action)
    operation = str(action.get("operation", "unknown")).lower()
    has_backup = bool(action.get("backup_ref") or action.get("pre_state_ref"))
    has_prior_version = bool(action.get("previous_version_ref") or action.get("snapshot_ref"))

    base = {
        "reversal_action": None,
        "reversal_available": False,
        "reversal_risk": "irreversible",
        "requires_human_approval": True,
        "auto_reversal_allowed": False,
        "reversal_reason": "unknown_or_irreversible",
    }

    if capability == "filesystem":
        if operation in {"create_file", "write_file"}:
            return {
                **base,
                "reversal_action": "delete_created_file_after_human_review",
                "reversal_available": True,
                "reversal_risk": "medium",
                "reversal_reason": "created_file_can_be_removed_but_requires_review",
            }
        if operation in {"delete_file", "modify_file", "update_file"} and has_backup:
            return {
                **base,
                "reversal_action": "restore_from_backup",
                "reversal_available": True,
                "reversal_risk": "medium",
                "reversal_reason": "backup_ref_present",
            }

    if capability == "repo":
        if operation in {"create_branch", "create_pr", "add_label", "create_release"}:
            return {
                **base,
                "reversal_action": "repo_compensating_change",
                "reversal_available": True,
                "reversal_risk": "medium",
                "reversal_reason": "repo_action_can_be_compensated_with_followup_change",
            }

    if capability in {"cloud", "deployment"}:
        if has_prior_version:
            return {
                **base,
                "reversal_action": "rollback_to_previous_version",
                "reversal_available": True,
                "reversal_risk": "high",
                "reversal_reason": "previous_version_ref_present",
            }
        return {
            **base,
            "reversal_action": None,
            "reversal_available": False,
            "reversal_risk": "high",
            "reversal_reason": "deployment_or_cloud_action_missing_previous_version",
        }

    if capability == "database":
        if has_backup or has_prior_version:
            return {
                **base,
                "reversal_action": "restore_database_state_from_snapshot_or_version",
                "reversal_available": True,
                "reversal_risk": "high",
                "reversal_reason": "database_restore_requires_human_review",
            }
        return {
            **base,
            "reversal_action": None,
            "reversal_available": False,
            "reversal_risk": "high",
            "reversal_reason": "database_action_missing_snapshot",
        }

    if capability in {"network", "payment"}:
        return {
            **base,
            "reversal_action": None,
            "reversal_available": False,
            "reversal_risk": "irreversible",
            "reversal_reason": "external_side_effect_not_auto_reversible",
        }

    return base


def finding_for(entry: dict[str, Any]) -> dict[str, Any] | None:
    if entry["reversal_available"] is False:
        return {
            "rule_id": "AAPP-STATE-REVERSAL-MISSING",
            "severity": "HIGH",
            "step_id": entry["step_id"],
            "capability": entry["capability"],
            "operation": entry["operation"],
            "target_ref": entry["target_ref"],
            "rationale": "stateful action has no safe reversal candidate",
            "next_action": "Add snapshot/backup/previous_version reference or mark manual_review explicitly.",
        }

    if entry["reversal_risk"] in {"high", "irreversible"}:
        return {
            "rule_id": "AAPP-STATE-REVERSAL-HIGH-RISK",
            "severity": "HIGH",
            "step_id": entry["step_id"],
            "capability": entry["capability"],
            "operation": entry["operation"],
            "target_ref": entry["target_ref"],
            "rationale": "reversal exists but requires human approval due to high impact",
            "next_action": "Keep no_auto_reversal and route to manual review.",
        }

    return None


def build_ledger(actions: list[dict[str, Any]], session_id: str = "state-ledger-session") -> dict[str, Any]:
    ledger = []
    plan = []
    findings = []

    prev_entry_hash = None

    for index, action in enumerate(actions, start=1):
        capability = classify_action(action)
        reversal = reversal_for(action)

        pre_state = action.get("pre_state", {})
        post_state = action.get("post_state", {})
        step_id = str(action.get("step_id", f"step-{index:04d}"))

        entry = {
            "schema_version": SCHEMA_VERSION,
            "session_id": session_id,
            "step_id": step_id,
            "seq": index,
            "action_id": str(action.get("action_id", step_id)),
            "capability": capability,
            "operation": str(action.get("operation", "unknown")),
            "target_ref": str(action.get("target_ref", "unknown")),
            "pre_state_digest": digest(pre_state),
            "post_state_digest": digest(post_state),
            "prev_entry_hash": prev_entry_hash,
            "reversal_action": reversal["reversal_action"],
            "reversal_available": reversal["reversal_available"],
            "reversal_risk": reversal["reversal_risk"],
            "requires_human_approval": reversal["requires_human_approval"],
            "auto_reversal_allowed": False,
            "reversal_reason": reversal["reversal_reason"],
            "external_side_effect_executed": False,
        }
        entry["entry_hash"] = digest(entry)

        ledger.append(entry)
        prev_entry_hash = entry["entry_hash"]

        plan_item = {
            "step_id": entry["step_id"],
            "capability": entry["capability"],
            "operation": entry["operation"],
            "target_ref": entry["target_ref"],
            "reversal_action": entry["reversal_action"],
            "reversal_available": entry["reversal_available"],
            "reversal_risk": entry["reversal_risk"],
            "requires_human_approval": entry["requires_human_approval"],
            "auto_reversal_allowed": False,
            "reason": entry["reversal_reason"],
        }
        plan.append(plan_item)

        finding = finding_for(entry)
        if finding:
            findings.append(finding)

    return {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "ledger": ledger,
        "reversal_plan": {
            "schema_version": "aapp.reversal_plan.v1",
            "session_id": session_id,
            "auto_rollback_enabled": False,
            "plan": plan,
            "findings": findings,
        },
    }


def run_file(actions_path: str | Path, out: str | Path, session_id: str = "state-ledger-session") -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    actions = _read_json(actions_path)
    if not isinstance(actions, list):
        raise ValueError("actions_file_must_be_list")

    result = build_ledger(actions, session_id=session_id)

    _write_jsonl(out / "state.ledger.jsonl", result["ledger"])
    _write_json(out / "reversal.plan.json", result["reversal_plan"])

    lines = [
        "# State Ledger + Reversal Plan",
        "",
        f"- Session: `{session_id}`",
        f"- Ledger entries: {len(result['ledger'])}",
        f"- Reversal findings: {len(result['reversal_plan']['findings'])}",
        f"- Auto rollback enabled: `{result['reversal_plan']['auto_rollback_enabled']}`",
        "",
        "## Entries",
        "",
    ]

    for entry in result["ledger"]:
        lines += [
            f"### {entry['step_id']} — {entry['capability']} / {entry['operation']}",
            "",
            f"- Target: `{entry['target_ref']}`",
            f"- Pre-state digest: `{entry['pre_state_digest']}`",
            f"- Post-state digest: `{entry['post_state_digest']}`",
            f"- Reversal available: `{entry['reversal_available']}`",
            f"- Reversal risk: `{entry['reversal_risk']}`",
            f"- Requires human approval: `{entry['requires_human_approval']}`",
            f"- Auto reversal allowed: `{entry['auto_reversal_allowed']}`",
            f"- Reversal action: `{entry['reversal_action']}`",
            "",
        ]

    (out / "reversal.report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create state ledger and reversal plan for stateful actions.")
    parser.add_argument("--actions", required=True)
    parser.add_argument("--out", default=".aapp/state-ledger")
    parser.add_argument("--session-id", default="state-ledger-session")
    args = parser.parse_args(argv)

    result = run_file(args.actions, args.out, session_id=args.session_id)
    print(
        "AAPP state ledger complete: "
        f"entries={len(result['ledger'])} "
        f"findings={len(result['reversal_plan']['findings'])} "
        f"out={Path(args.out).resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
