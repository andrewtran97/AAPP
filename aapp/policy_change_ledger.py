from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

POLICY_SCHEMA = "aapp.policy.v1"
PROPOSAL_SCHEMA = "aapp.policy_change_proposal.v1"
APPROVALS_SCHEMA = "aapp.policy_change_approvals.v1"
APPROVAL_SCHEMA = "aapp.policy_change_approval.v1"
REGISTRY_SCHEMA = "aapp.policy_active_registry.v1"

APPROVED = "APPROVED"
REJECTED = "REJECTED"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"
STALE_CHANGE = "STALE_CHANGE"
INSUFFICIENT_APPROVAL = "INSUFFICIENT_APPROVAL"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
POLICY_DOWNGRADE = "POLICY_DOWNGRADE"

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
]

SECURITY_LEVEL_ORDER = {
    "permissive": 1,
    "balanced": 2,
    "strict": 3,
}

HIGH_TRUST_ROLES = {"security_lead", "platform_owner", "policy_admin"}


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj)).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp_invalid")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp_missing_timezone")
    return parsed.astimezone(timezone.utc)


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def component_scan_roots(paths: list[Path]) -> list[Path]:
    roots: list[Path] = []
    seen: set[str] = set()
    parent_counts: dict[str, int] = {}

    normalized = [Path(p) for p in paths]
    for path in normalized:
        if path.is_file():
            key = str(path.parent.resolve())
            parent_counts[key] = parent_counts.get(key, 0) + 1

    def add(candidate: Path) -> None:
        try:
            key = str(candidate.resolve() if candidate.exists() else candidate.absolute())
        except OSError:
            key = str(candidate.absolute())
        if key not in seen:
            seen.add(key)
            roots.append(candidate)

    for path in normalized:
        add(path)

    for path in normalized:
        if not path.is_file():
            continue
        parent = path.parent
        if parent_counts.get(str(parent.resolve()), 0) >= 2:
            add(parent)

    return roots


def unsafe_findings(paths: list[Path]) -> list[dict[str, Any]]:
    findings = []
    files = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend([p for p in path.rglob("*") if p.is_file()])

    for path in files:
        text = safe_text(path)

        if PRIVATE_KEY_RE.search(text):
            findings.append({
                "type": "private_key",
                "file_path": str(path),
                "reason": "private key marker detected",
            })

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({
                    "type": "secret_pattern",
                    "file_path": str(path),
                    "reason": "secret-like token detected",
                })
                break

    return findings


def policy_digest(policy: dict[str, Any]) -> str:
    return sha256_digest(policy)


def approval_digest(approval: dict[str, Any]) -> str:
    clean = dict(approval)
    clean.pop("approval_digest", None)
    return sha256_digest(clean)


def required_fields(obj: dict[str, Any], fields: list[str], prefix: str) -> str | None:
    for field in fields:
        if field not in obj:
            return f"missing_{prefix}_field:{field}"
    return None


def is_policy_downgrade(old_policy: dict[str, Any], new_policy: dict[str, Any]) -> bool:
    old_level = str(old_policy.get("security_level", "balanced")).lower()
    new_level = str(new_policy.get("security_level", "balanced")).lower()

    old_score = SECURITY_LEVEL_ORDER.get(old_level, 2)
    new_score = SECURITY_LEVEL_ORDER.get(new_level, 2)
    if new_score < old_score:
        return True

    old_mode = str(old_policy.get("enforcement_mode", "enforce")).lower()
    new_mode = str(new_policy.get("enforcement_mode", "enforce")).lower()
    if old_mode == "enforce" and new_mode in {"monitor", "allow_all"}:
        return True

    return False


def evaluate_policy_change(
    old_policy: dict[str, Any],
    new_policy: dict[str, Any],
    proposal: dict[str, Any],
    approvals_doc: dict[str, Any],
    registry: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or utc_now()
    base = {
        "schema_version": "aapp.policy_change_verdict.v1",
        "verdict": None,
        "reason": None,
        "checks": [],
        "unsafe_findings": [],
        "ledger_entry": None,
    }

    if not isinstance(old_policy, dict) or not isinstance(new_policy, dict):
        return {**base, "verdict": MALFORMED, "reason": "policy_not_object"}
    if not isinstance(proposal, dict):
        return {**base, "verdict": MALFORMED, "reason": "proposal_not_object"}
    if not isinstance(approvals_doc, dict):
        return {**base, "verdict": MALFORMED, "reason": "approvals_not_object"}
    if not isinstance(registry, dict):
        return {**base, "verdict": MALFORMED, "reason": "registry_not_object"}

    if old_policy.get("schema_version") != POLICY_SCHEMA or new_policy.get("schema_version") != POLICY_SCHEMA:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_policy_schema"}
    if proposal.get("schema_version") != PROPOSAL_SCHEMA:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_proposal_schema"}
    if approvals_doc.get("schema_version") != APPROVALS_SCHEMA:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_approvals_schema"}
    if registry.get("schema_version") != REGISTRY_SCHEMA:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_registry_schema"}

    proposal_required = [
        "change_id",
        "policy_id",
        "old_policy_version",
        "new_policy_version",
        "old_policy_digest",
        "new_policy_digest",
        "change_reason",
        "risk_class",
        "requested_by",
        "created_at",
        "valid_until",
        "rollback_policy_version",
        "rollback_policy_digest",
        "required_approval_count",
    ]
    missing = required_fields(proposal, proposal_required, "proposal")
    if missing:
        return {**base, "verdict": MALFORMED, "reason": missing}

    old_digest = policy_digest(old_policy)
    new_digest = policy_digest(new_policy)
    checks = [
        {"check": "old_policy_digest", "expected": proposal["old_policy_digest"], "actual": old_digest, "ok": proposal["old_policy_digest"] == old_digest},
        {"check": "new_policy_digest", "expected": proposal["new_policy_digest"], "actual": new_digest, "ok": proposal["new_policy_digest"] == new_digest},
    ]

    if proposal["old_policy_digest"] != old_digest:
        return {**base, "verdict": DIGEST_MISMATCH, "reason": "old_policy_digest_mismatch", "checks": checks}
    if proposal["new_policy_digest"] != new_digest:
        return {**base, "verdict": DIGEST_MISMATCH, "reason": "new_policy_digest_mismatch", "checks": checks}

    try:
        valid_until = parse_time(proposal["valid_until"])
    except Exception:
        return {**base, "verdict": MALFORMED, "reason": "proposal_valid_until_invalid", "checks": checks}

    if now >= valid_until:
        return {**base, "verdict": STALE_CHANGE, "reason": "proposal_expired", "checks": checks}

    approvals = approvals_doc.get("approvals")
    if not isinstance(approvals, list):
        return {**base, "verdict": MALFORMED, "reason": "approvals_not_list", "checks": checks}

    required_count = int(proposal.get("required_approval_count", 2))
    if required_count < 2:
        required_count = 2

    approver_ids = []
    approved = []
    high_trust_approved = False

    for approval in approvals:
        if not isinstance(approval, dict):
            return {**base, "verdict": MALFORMED, "reason": "approval_not_object", "checks": checks}
        if approval.get("schema_version") != APPROVAL_SCHEMA:
            return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_approval_schema", "checks": checks}

        approval_required = [
            "change_id",
            "approver_id",
            "approver_role",
            "decision",
            "approved_at",
            "approval_digest",
        ]
        missing = required_fields(approval, approval_required, "approval")
        if missing:
            return {**base, "verdict": MALFORMED, "reason": missing, "checks": checks}

        if approval["change_id"] != proposal["change_id"]:
            return {**base, "verdict": MALFORMED, "reason": "approval_change_id_mismatch", "checks": checks}

        expected_digest = approval_digest(approval)
        checks.append({
            "check": f"approval_digest:{approval['approver_id']}",
            "expected": approval.get("approval_digest"),
            "actual": expected_digest,
            "ok": approval.get("approval_digest") == expected_digest,
        })
        if approval.get("approval_digest") != expected_digest:
            return {**base, "verdict": DIGEST_MISMATCH, "reason": "approval_digest_mismatch", "checks": checks}

        if approval.get("decision") == "REJECTED":
            return {**base, "verdict": REJECTED, "reason": "rejected_approval_present", "checks": checks}

        if approval.get("decision") == "APPROVED":
            approved.append(approval)
            approver_ids.append(str(approval["approver_id"]))
            if str(approval.get("approver_role")) in HIGH_TRUST_ROLES:
                high_trust_approved = True

    unique_approver_ids = set(approver_ids)
    if len(approved) < required_count:
        return {**base, "verdict": INSUFFICIENT_APPROVAL, "reason": "not_enough_approvals", "checks": checks}
    if len(unique_approver_ids) < required_count:
        return {**base, "verdict": INSUFFICIENT_APPROVAL, "reason": "duplicate_approver", "checks": checks}

    if is_policy_downgrade(old_policy, new_policy) and not high_trust_approved:
        return {**base, "verdict": POLICY_DOWNGRADE, "reason": "policy_downgrade_without_high_trust_approval", "checks": checks}

    ledger_entry = {
        "schema_version": "aapp.policy_change_ledger_entry.v1",
        "change_id": proposal["change_id"],
        "policy_id": proposal["policy_id"],
        "old_policy_version": proposal["old_policy_version"],
        "new_policy_version": proposal["new_policy_version"],
        "old_policy_digest": old_digest,
        "new_policy_digest": new_digest,
        "risk_class": proposal["risk_class"],
        "requested_by": proposal["requested_by"],
        "approver_ids": sorted(unique_approver_ids),
        "approval_count": len(unique_approver_ids),
        "ledger_digest": sha256_digest({
            "change_id": proposal["change_id"],
            "policy_id": proposal["policy_id"],
            "old_policy_digest": old_digest,
            "new_policy_digest": new_digest,
            "approver_ids": sorted(unique_approver_ids),
        }),
    }

    return {
        **base,
        "verdict": APPROVED,
        "reason": "dual_control_policy_change_approved",
        "checks": checks,
        "ledger_entry": ledger_entry,
    }


def evaluate_from_files(
    old_policy_path: str | Path,
    new_policy_path: str | Path,
    proposal_path: str | Path,
    approvals_path: str | Path,
    registry_path: str | Path,
    out: str | Path,
) -> dict[str, Any]:
    paths = [Path(p) for p in [old_policy_path, new_policy_path, proposal_path, approvals_path, registry_path]]
    unsafe = unsafe_findings(component_scan_roots(paths))

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    if unsafe:
        verdict = {
            "schema_version": "aapp.policy_change_verdict.v1",
            "verdict": UNSAFE,
            "reason": "unsafe_content_detected",
            "checks": [],
            "unsafe_findings": unsafe,
            "ledger_entry": None,
        }
    else:
        old_policy = read_json(old_policy_path)
        new_policy = read_json(new_policy_path)
        proposal = read_json(proposal_path)
        approvals = read_json(approvals_path)
        registry = read_json(registry_path)
        verdict = evaluate_policy_change(old_policy, new_policy, proposal, approvals, registry)

    ledger_entry = verdict.get("ledger_entry")
    if ledger_entry:
        with (out / "policy.change.ledger.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(ledger_entry, sort_keys=True) + "\n")

    clean = dict(verdict)
    write_json(out / "policy.change.verdict.json", clean)

    report = [
        "# Policy Change Ledger Dual Control",
        "",
        f"- Verdict: `{clean['verdict']}`",
        f"- Reason: `{clean['reason']}`",
        f"- Ledger entry: `{'present' if ledger_entry else 'not_written'}`",
        "",
    ]
    (out / "policy.change.report.md").write_text("\n".join(report), encoding="utf-8")
    return clean


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify policy change dual-control ledger evidence.")
    parser.add_argument("--old-policy", required=True)
    parser.add_argument("--new-policy", required=True)
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--approvals", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    verdict = evaluate_from_files(
        args.old_policy,
        args.new_policy,
        args.proposal,
        args.approvals,
        args.registry,
        args.out,
    )
    print(f"AAPP policy change ledger complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
    return 0 if verdict["verdict"] == APPROVED else 1


if __name__ == "__main__":
    raise SystemExit(main())
