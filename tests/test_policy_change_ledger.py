import json
import shutil
from pathlib import Path

from aapp.policy_change_ledger import (
    APPROVED,
    DIGEST_MISMATCH,
    INSUFFICIENT_APPROVAL,
    MALFORMED,
    POLICY_DOWNGRADE,
    REJECTED,
    STALE_CHANGE,
    UNSAFE,
    UNSUPPORTED,
    evaluate_from_files,
    sha256_digest,
)


FIXTURE = Path(__file__).parent / "fixtures" / "policy_change_ledger"


def run_valid(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        FIXTURE / "policy_change.proposal.json",
        FIXTURE / "policy_change.approvals.json",
        FIXTURE / "policy.active_registry.json",
        out,
    )
    return out, verdict


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_valid_dual_approval_policy_change_approved(tmp_path):
    out, verdict = run_valid(tmp_path)

    assert verdict["verdict"] == APPROVED
    assert (out / "policy.change.ledger.jsonl").exists()
    assert (out / "policy.change.verdict.json").exists()
    assert (out / "policy.change.report.md").exists()

    ledger = json.loads((out / "policy.change.ledger.jsonl").read_text().splitlines()[0])
    assert ledger["change_id"] == "policy-change-001"
    assert ledger["approval_count"] == 2


def test_one_approval_insufficient(tmp_path):
    approvals = json.loads((FIXTURE / "policy_change.approvals.json").read_text())
    approvals["approvals"] = approvals["approvals"][:1]
    approvals_path = tmp_path / "approvals.json"
    write_json(approvals_path, approvals)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        FIXTURE / "policy_change.proposal.json",
        approvals_path,
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == INSUFFICIENT_APPROVAL


def test_duplicate_approver_insufficient(tmp_path):
    approvals = json.loads((FIXTURE / "policy_change.approvals.json").read_text())
    approvals["approvals"][1]["approver_id"] = approvals["approvals"][0]["approver_id"]

    from aapp.policy_change_ledger import approval_digest
    approvals["approvals"][1]["approval_digest"] = approval_digest(approvals["approvals"][1])

    approvals_path = tmp_path / "approvals.json"
    write_json(approvals_path, approvals)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        FIXTURE / "policy_change.proposal.json",
        approvals_path,
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == INSUFFICIENT_APPROVAL
    assert verdict["reason"] == "duplicate_approver"


def test_rejected_approval_rejected(tmp_path):
    approvals = json.loads((FIXTURE / "policy_change.approvals.json").read_text())
    approvals["approvals"][1]["decision"] = "REJECTED"

    from aapp.policy_change_ledger import approval_digest
    approvals["approvals"][1]["approval_digest"] = approval_digest(approvals["approvals"][1])

    approvals_path = tmp_path / "approvals.json"
    write_json(approvals_path, approvals)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        FIXTURE / "policy_change.proposal.json",
        approvals_path,
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == REJECTED


def test_old_digest_mismatch(tmp_path):
    proposal = json.loads((FIXTURE / "policy_change.proposal.json").read_text())
    proposal["old_policy_digest"] = "sha256:" + ("0" * 64)
    proposal_path = tmp_path / "proposal.json"
    write_json(proposal_path, proposal)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        proposal_path,
        FIXTURE / "policy_change.approvals.json",
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == DIGEST_MISMATCH
    assert verdict["reason"] == "old_policy_digest_mismatch"


def test_new_digest_mismatch(tmp_path):
    proposal = json.loads((FIXTURE / "policy_change.proposal.json").read_text())
    proposal["new_policy_digest"] = "sha256:" + ("1" * 64)
    proposal_path = tmp_path / "proposal.json"
    write_json(proposal_path, proposal)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        proposal_path,
        FIXTURE / "policy_change.approvals.json",
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == DIGEST_MISMATCH
    assert verdict["reason"] == "new_policy_digest_mismatch"


def test_expired_proposal_stale_change(tmp_path):
    proposal = json.loads((FIXTURE / "policy_change.proposal.json").read_text())
    proposal["valid_until"] = "2020-01-01T00:00:00Z"
    proposal_path = tmp_path / "proposal.json"
    write_json(proposal_path, proposal)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        proposal_path,
        FIXTURE / "policy_change.approvals.json",
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == STALE_CHANGE


def test_unsupported_schema(tmp_path):
    proposal = json.loads((FIXTURE / "policy_change.proposal.json").read_text())
    proposal["schema_version"] = "aapp.policy_change_proposal.v999"
    proposal_path = tmp_path / "proposal.json"
    write_json(proposal_path, proposal)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        proposal_path,
        FIXTURE / "policy_change.approvals.json",
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == UNSUPPORTED


def test_missing_required_field_malformed(tmp_path):
    proposal = json.loads((FIXTURE / "policy_change.proposal.json").read_text())
    proposal.pop("change_id")
    proposal_path = tmp_path / "proposal.json"
    write_json(proposal_path, proposal)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        FIXTURE / "policy.new.json",
        proposal_path,
        FIXTURE / "policy_change.approvals.json",
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == MALFORMED


def test_policy_downgrade_without_high_trust_approval(tmp_path):
    old_policy = json.loads((FIXTURE / "policy.old.json").read_text())
    new_policy = json.loads((FIXTURE / "policy.new.json").read_text())
    new_policy["security_level"] = "permissive"
    new_policy["enforcement_mode"] = "monitor"

    proposal = json.loads((FIXTURE / "policy_change.proposal.json").read_text())
    proposal["new_policy_digest"] = sha256_digest(new_policy)

    approvals = json.loads((FIXTURE / "policy_change.approvals.json").read_text())
    for approval in approvals["approvals"]:
        approval["approver_role"] = "developer"
        from aapp.policy_change_ledger import approval_digest
        approval["approval_digest"] = approval_digest(approval)

    new_policy_path = tmp_path / "policy.new.downgrade.json"
    proposal_path = tmp_path / "proposal.json"
    approvals_path = tmp_path / "approvals.json"

    write_json(new_policy_path, new_policy)
    write_json(proposal_path, proposal)
    write_json(approvals_path, approvals)

    verdict = evaluate_from_files(
        FIXTURE / "policy.old.json",
        new_policy_path,
        proposal_path,
        approvals_path,
        FIXTURE / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == POLICY_DOWNGRADE


def test_private_key_or_secret_is_unsafe(tmp_path):
    unsafe_dir = tmp_path / "unsafe"
    shutil.copytree(FIXTURE, unsafe_dir)

    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    (unsafe_dir / "unsafe.pem").write_text(marker + "\nnot-real\n", encoding="utf-8")

    verdict = evaluate_from_files(
        unsafe_dir / "policy.old.json",
        unsafe_dir / "policy.new.json",
        unsafe_dir / "policy_change.proposal.json",
        unsafe_dir / "policy_change.approvals.json",
        unsafe_dir / "policy.active_registry.json",
        tmp_path / "out",
    )
    assert verdict["verdict"] == UNSAFE
    assert verdict["unsafe_findings"]


def test_machine_readable_verdict(tmp_path):
    out, verdict = run_valid(tmp_path)
    machine = json.loads((out / "policy.change.verdict.json").read_text())

    assert machine["schema_version"] == "aapp.policy_change_verdict.v1"
    assert machine["verdict"] == APPROVED
    assert machine["ledger_entry"]["ledger_digest"].startswith("sha256:")
