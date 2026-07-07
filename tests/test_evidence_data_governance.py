import json
from pathlib import Path

from aapp.evidence_data_governance import (
    ALLOWED,
    EXPORT_NOT_ALLOWED,
    MALFORMED,
    REDACTED,
    RETENTION_VIOLATION,
    UNSAFE,
    UNSUPPORTED,
    evaluate_from_files,
)


FIXTURE = Path(__file__).parent / "fixtures" / "evidence_data_governance"


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_public_clean_evidence_allowed(tmp_path):
    verdict = evaluate_from_files(
        FIXTURE / "evidence.public.json",
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == ALLOWED
    assert verdict["governance"]["data_classification"] == "public"
    assert (tmp_path / "out" / "governance.verdict.json").exists()
    assert (tmp_path / "out" / "governance.report.md").exists()


def test_internal_clean_evidence_allowed(tmp_path):
    verdict = evaluate_from_files(
        FIXTURE / "evidence.internal.json",
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == ALLOWED
    assert verdict["governance"]["pii_present"] is True
    assert verdict["governance"]["secret_present"] is False


def test_raw_secret_evidence_redacted(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(
        FIXTURE / "evidence.restricted_secret.json",
        FIXTURE / "governance.policy.json",
        out,
    )

    assert verdict["verdict"] == REDACTED
    assert verdict["redacted_output_written"] is True
    assert verdict["evidence_digest_before"] != verdict["evidence_digest_after"]

    redacted = json.loads((out / "governance.redacted.json").read_text())
    assert redacted["payload"]["api_token"] == "[REDACTED]"
    assert "synthetic-token-value" not in (out / "governance.redacted.json").read_text()


def test_private_key_evidence_unsafe(tmp_path):
    evidence = json.loads((FIXTURE / "evidence.public.json").read_text())
    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    evidence["payload"]["pem"] = marker + "\nnot-real\n"
    evidence_path = tmp_path / "evidence.private.json"
    write_json(evidence_path, evidence)

    verdict = evaluate_from_files(
        evidence_path,
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == UNSAFE
    assert verdict["governance"]["private_key_present"] is True


def test_restricted_export_not_allowed(tmp_path):
    evidence = json.loads((FIXTURE / "evidence.restricted_secret.json").read_text())
    evidence["payload"].pop("api_token")
    evidence["export_requested"] = True
    evidence["sharing_scope"] = "external"
    evidence_path = tmp_path / "evidence.restricted.export.json"
    write_json(evidence_path, evidence)

    verdict = evaluate_from_files(
        evidence_path,
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == EXPORT_NOT_ALLOWED


def test_retention_over_policy_violation(tmp_path):
    evidence = json.loads((FIXTURE / "evidence.internal.json").read_text())
    evidence["retention_days"] = 999
    evidence_path = tmp_path / "evidence.retention.json"
    write_json(evidence_path, evidence)

    verdict = evaluate_from_files(
        evidence_path,
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == RETENTION_VIOLATION


def test_missing_required_field_malformed(tmp_path):
    evidence = json.loads((FIXTURE / "evidence.public.json").read_text())
    evidence.pop("data_classification")
    evidence_path = tmp_path / "evidence.malformed.json"
    write_json(evidence_path, evidence)

    verdict = evaluate_from_files(
        evidence_path,
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == MALFORMED


def test_unsupported_schema(tmp_path):
    evidence = json.loads((FIXTURE / "evidence.public.json").read_text())
    evidence["schema_version"] = "aapp.evidence_data.v999"
    evidence_path = tmp_path / "evidence.unsupported.json"
    write_json(evidence_path, evidence)

    verdict = evaluate_from_files(
        evidence_path,
        FIXTURE / "governance.policy.json",
        tmp_path / "out",
    )

    assert verdict["verdict"] == UNSUPPORTED


def test_machine_readable_verdict(tmp_path):
    out = tmp_path / "out"
    verdict = evaluate_from_files(
        FIXTURE / "evidence.public.json",
        FIXTURE / "governance.policy.json",
        out,
    )

    machine = json.loads((out / "governance.verdict.json").read_text())
    assert machine["schema_version"] == "aapp.evidence_governance_verdict.v1"
    assert machine["verdict"] == ALLOWED
    assert machine["evidence_digest_before"].startswith("sha256:")
    assert machine["evidence_digest_after"].startswith("sha256:")
