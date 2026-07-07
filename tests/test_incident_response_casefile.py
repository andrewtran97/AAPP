import json
from pathlib import Path

from aapp.incident_response_casefile import (
    CASE_CLOSED,
    CASE_NOT_REQUIRED,
    CASE_OPENED,
    CLOSURE_REJECTED,
    MALFORMED,
    UNSAFE,
    UNSUPPORTED,
    close_from_files,
    evaluate_from_files,
)


FIXTURE = Path(__file__).parent / "fixtures" / "incident_response_casefile"


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_firewall_deny_opens_case(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(FIXTURE / "firewall.deny.json", FIXTURE / "incident.policy.json", out)

    assert verdict["verdict"] == CASE_OPENED
    assert (out / "incident.casefile.json").exists()
    assert (out / "incident.timeline.jsonl").exists()
    assert (out / "incident.verdict.json").exists()
    assert (out / "incident.report.md").exists()

    casefile = read_json(out / "incident.casefile.json")
    assert casefile["source_type"] == "firewall"
    assert casefile["source_verdict"] == "DENY"
    assert casefile["severity"] == "CRITICAL"
    assert casefile["casefile_digest"].startswith("sha256:")


def test_verify_failed_opens_case(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(FIXTURE / "verify.failed.json", FIXTURE / "incident.policy.json", out)

    assert verdict["verdict"] == CASE_OPENED
    casefile = read_json(out / "incident.casefile.json")
    assert casefile["source_type"] == "verify"
    assert casefile["source_verdict"] == "FAILED"
    assert casefile["containment_action"] == "quarantine_evidence_package"


def test_governance_unsafe_opens_case(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(FIXTURE / "governance.unsafe.json", FIXTURE / "incident.policy.json", out)

    assert verdict["verdict"] == CASE_OPENED
    casefile = read_json(out / "incident.casefile.json")
    assert casefile["source_verdict"] == "UNSAFE"
    assert casefile["severity"] == "CRITICAL"


def test_policy_violation_opens_case(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(FIXTURE / "policy.violation.json", FIXTURE / "incident.policy.json", out)

    assert verdict["verdict"] == CASE_OPENED
    casefile = read_json(out / "incident.casefile.json")
    assert casefile["source_type"] == "policy_change"
    assert casefile["containment_action"] == "block_policy_activation_until_review"


def test_low_risk_allowed_returns_case_not_required(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(FIXTURE / "firewall.allow.low.json", FIXTURE / "incident.policy.json", out)

    assert verdict["verdict"] == CASE_NOT_REQUIRED
    assert not (out / "incident.casefile.json").exists()
    assert (out / "incident.verdict.json").exists()


def test_missing_source_type_returns_malformed(tmp_path):
    source = read_json(FIXTURE / "firewall.deny.json")
    source.pop("source_type")
    source_path = tmp_path / "missing.json"
    write_json(source_path, source)

    verdict = evaluate_from_files(source_path, FIXTURE / "incident.policy.json", tmp_path / "out")
    assert verdict["verdict"] == MALFORMED


def test_unsupported_source_schema_returns_unsupported(tmp_path):
    source = read_json(FIXTURE / "firewall.deny.json")
    source["schema_version"] = "aapp.unknown.v1"
    source_path = tmp_path / "unsupported.json"
    write_json(source_path, source)

    verdict = evaluate_from_files(source_path, FIXTURE / "incident.policy.json", tmp_path / "out")
    assert verdict["verdict"] == UNSUPPORTED


def test_private_key_raw_secret_returns_unsafe(tmp_path):
    source = read_json(FIXTURE / "firewall.deny.json")
    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    source["payload"] = {"pem": marker + "\nnot-real\n"}
    source_path = tmp_path / "unsafe.json"
    write_json(source_path, source)

    verdict = evaluate_from_files(source_path, FIXTURE / "incident.policy.json", tmp_path / "out")
    assert verdict["verdict"] == UNSAFE
    assert verdict["unsafe_findings"]


def test_closure_without_approval_rejected(tmp_path):
    open_out = tmp_path / "open"
    evaluate_from_files(FIXTURE / "firewall.deny.json", FIXTURE / "incident.policy.json", open_out)

    close_out = tmp_path / "close"
    verdict = close_from_files(open_out / "incident.casefile.json", FIXTURE / "closure.no_approval.json", close_out)

    assert verdict["verdict"] == CLOSURE_REJECTED
    assert not (close_out / "incident.closure.receipt.json").exists()


def test_closure_with_approval_writes_receipt(tmp_path):
    open_out = tmp_path / "open"
    evaluate_from_files(FIXTURE / "firewall.deny.json", FIXTURE / "incident.policy.json", open_out)

    close_out = tmp_path / "close"
    verdict = close_from_files(open_out / "incident.casefile.json", FIXTURE / "closure.approved.json", close_out)

    assert verdict["verdict"] == CASE_CLOSED
    assert (close_out / "incident.closure.receipt.json").exists()
    assert (close_out / "incident.timeline.jsonl").exists()

    receipt = read_json(close_out / "incident.closure.receipt.json")
    assert receipt["status"] == "CLOSED"
    assert receipt["closure_digest"].startswith("sha256:")
