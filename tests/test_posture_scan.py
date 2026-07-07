from pathlib import Path

from aapp.posture_scan import scan_repo


def test_posture_scan_detects_permission_secret_stateful_and_rollback_gap(tmp_path):
    repo = Path(__file__).parent / "fixtures" / "posture_scan_repo"
    out = tmp_path / "posture"
    result = scan_repo(repo, out)

    summary = result["posture_map"]["summary"]
    findings = result["posture_findings"]["findings"]
    rollback_gaps = result["rollback_gaps"]["rollback_gaps"]
    stateful_actions = result["stateful_actions"]["stateful_actions"]

    assert summary["workflows_scanned"] >= 2
    assert summary["scripts_scanned"] >= 2
    assert summary["posture_items"] > 0
    assert summary["high_findings"] > 0

    assert any(f["posture_type"] == "permission_risk" for f in findings)
    assert any(f["posture_type"] == "secret_usage" for f in findings)
    assert any(f["posture_type"] == "stateful_action" for f in findings)
    assert any(f["posture_type"] == "ci_runner_agent_path" for f in findings)

    assert any(f["severity"] == "HIGH" for f in findings)
    assert all(f["next_action"] for f in findings)
    assert stateful_actions
    assert rollback_gaps

    required = [
        "posture.map.json",
        "posture.findings.json",
        "stateful_actions.json",
        "rollback_gaps.json",
        "posture.report.md",
    ]
    for name in required:
        assert (out / name).exists(), name


def test_posture_scan_does_not_execute_fixture(tmp_path):
    repo = Path(__file__).parent / "fixtures" / "posture_scan_repo"
    marker = repo / "SHOULD_NOT_EXIST"
    if marker.exists():
        marker.unlink()

    scan_repo(repo, tmp_path / "posture")

    assert not marker.exists()
