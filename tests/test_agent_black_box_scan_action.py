import json
from pathlib import Path

from aapp.surface_scan import scan_repo as surface_scan
from aapp.posture_scan import scan_repo as posture_scan


ACTION = Path(".github/actions/agent-black-box-scan/action.yml")
FIXTURE = Path(__file__).parent / "fixtures" / "github_action_scan_repo"


def test_composite_action_metadata_contract():
    text = ACTION.read_text()

    assert 'name: Agent Black Box Scan' in text
    assert 'using: "composite"' in text
    assert 'repo-path:' in text
    assert 'out-dir:' in text
    assert 'fail-on-high:' in text
    assert 'verify-package-path:' in text

    assert 'python3 -m aapp.surface_scan' in text
    assert 'python3 -m aapp.posture_scan' in text
    assert 'python3 -m aapp.verify_pack' in text

    assert 'surface-high-findings' in text
    assert 'posture-high-findings' in text


def test_fixture_workflow_uses_action_and_uploads_artifact():
    workflow = FIXTURE / ".github" / "workflows" / "aapp-scan.yml"
    text = workflow.read_text()

    assert 'uses: ./.github/actions/agent-black-box-scan' in text
    assert 'uses: actions/upload-artifact@v4' in text
    assert 'path: .aapp/agent-black-box-scan' in text


def test_action_output_contract_with_existing_scanners(tmp_path):
    out = tmp_path / "agent-black-box-scan"
    surface_out = out / "surface"
    posture_out = out / "posture"

    surface_scan(FIXTURE, surface_out)
    posture_scan(FIXTURE, posture_out)

    required = [
        surface_out / "surface.map.json",
        surface_out / "risk_findings.json",
        surface_out / "evidence_gap.json",
        surface_out / "surface.metrics.json",
        surface_out / "surface.report.md",
        surface_out / "surface.sarif.json",
        posture_out / "posture.map.json",
        posture_out / "posture.findings.json",
        posture_out / "stateful_actions.json",
        posture_out / "rollback_gaps.json",
        posture_out / "posture.report.md",
    ]

    for path in required:
        assert path.exists(), path

    surface_metrics = json.loads((surface_out / "surface.metrics.json").read_text())
    posture_map = json.loads((posture_out / "posture.map.json").read_text())

    assert "high_findings" in surface_metrics
    assert "summary" in posture_map
    assert "high_findings" in posture_map["summary"]
