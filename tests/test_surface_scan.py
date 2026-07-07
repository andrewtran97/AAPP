from pathlib import Path

from aapp.surface_scan import scan_repo


def test_surface_scan_fixture_outputs(tmp_path):
    repo = Path(__file__).parent / "fixtures" / "surface_scan_repo"
    out = tmp_path / "surface"
    result = scan_repo(repo, out)

    metrics = result["metrics"]
    findings = result["risk_findings"]["findings"]

    assert metrics["repos_scanned"] == 1
    assert metrics["workflows_scanned"] >= 1
    assert metrics["scripts_scanned"] >= 2
    assert metrics["surfaces_detected"] > 0
    assert metrics["high_findings"] > 0

    required = [
        "surface.map.json",
        "risk_findings.json",
        "evidence_gap.json",
        "surface.metrics.json",
        "surface.report.md",
        "surface.sarif.json",
    ]
    for name in required:
        assert (out / name).exists(), name

    assert any(f["severity"] == "HIGH" for f in findings)
    assert all(f["next_action"] for f in findings)
    assert all(f["rule_id"].startswith("AAPP-SURFACE-") for f in findings)


def test_surface_scan_does_not_execute_fixture(tmp_path):
    repo = Path(__file__).parent / "fixtures" / "surface_scan_repo"
    marker = repo / "SHOULD_NOT_EXIST"
    if marker.exists():
        marker.unlink()

    scan_repo(repo, tmp_path / "surface")

    assert not marker.exists()
