from pathlib import Path

from aapp.state_ledger import build_ledger, run_file


FIXTURE = Path(__file__).parent / "fixtures" / "state_ledger_actions.json"


def test_stateful_actions_create_ledger_entries(tmp_path):
    result = run_file(FIXTURE, tmp_path / "state-ledger", session_id="test-session")

    ledger = result["ledger"]
    plan = result["reversal_plan"]

    assert len(ledger) == 5
    assert plan["auto_rollback_enabled"] is False
    assert (tmp_path / "state-ledger" / "state.ledger.jsonl").exists()
    assert (tmp_path / "state-ledger" / "reversal.plan.json").exists()
    assert (tmp_path / "state-ledger" / "reversal.report.md").exists()

    for entry in ledger:
        assert entry["pre_state_digest"].startswith("sha256:")
        assert entry["post_state_digest"].startswith("sha256:")
        assert entry["entry_hash"].startswith("sha256:")
        assert entry["auto_reversal_allowed"] is False
        assert entry["external_side_effect_executed"] is False


def test_hash_chain_links_entries(tmp_path):
    result = run_file(FIXTURE, tmp_path / "state-ledger", session_id="test-session")
    ledger = result["ledger"]

    assert ledger[0]["prev_entry_hash"] is None
    for prev, current in zip(ledger, ledger[1:]):
        assert current["prev_entry_hash"] == prev["entry_hash"]


def test_irreversible_and_unknown_require_manual_review(tmp_path):
    result = run_file(FIXTURE, tmp_path / "state-ledger", session_id="test-session")
    ledger = result["ledger"]

    payment = next(e for e in ledger if e["capability"] == "payment")
    unknown = next(e for e in ledger if e["capability"] == "unknown")

    assert payment["reversal_available"] is False
    assert payment["reversal_risk"] == "irreversible"
    assert payment["requires_human_approval"] is True
    assert payment["auto_reversal_allowed"] is False

    assert unknown["reversal_available"] is False
    assert unknown["requires_human_approval"] is True
    assert unknown["auto_reversal_allowed"] is False


def test_known_reversible_actions_have_candidates(tmp_path):
    result = run_file(FIXTURE, tmp_path / "state-ledger", session_id="test-session")
    ledger = result["ledger"]

    deployment = next(e for e in ledger if e["capability"] == "deployment")
    database = next(e for e in ledger if e["capability"] == "database")

    assert deployment["reversal_available"] is True
    assert deployment["reversal_action"] == "rollback_to_previous_version"
    assert deployment["requires_human_approval"] is True

    assert database["reversal_available"] is True
    assert database["reversal_action"] == "restore_database_state_from_snapshot_or_version"
    assert database["requires_human_approval"] is True


def test_missing_reversal_creates_high_finding(tmp_path):
    result = run_file(FIXTURE, tmp_path / "state-ledger", session_id="test-session")
    findings = result["reversal_plan"]["findings"]

    assert findings
    assert any(f["severity"] == "HIGH" for f in findings)
    assert any(f["rule_id"] == "AAPP-STATE-REVERSAL-MISSING" for f in findings)


def test_build_ledger_does_not_execute_external_actions():
    actions = [
        {
            "step_id": "step-external",
            "capability": "cloud",
            "operation": "aws delete-bucket",
            "target_ref": "s3://should-not-run",
            "pre_state": {"exists": True},
            "post_state": {"exists": False}
        }
    ]

    result = build_ledger(actions, session_id="no-exec-test")
    entry = result["ledger"][0]

    assert entry["external_side_effect_executed"] is False
    assert entry["auto_reversal_allowed"] is False
