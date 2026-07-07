import json
import shutil
from pathlib import Path

from aapp.workload_identity import (
    EXPIRED_IDENTITY,
    IDENTITY_NOT_ACTIVE,
    INVALID,
    MALFORMED,
    POLICY_NOT_ALLOWED,
    SCOPE_MISMATCH,
    UNSAFE,
    UNSUPPORTED,
    VALID,
    build_from_files,
    verify_from_files,
)


FIXTURE = Path(__file__).parent / "fixtures" / "workload_identity"


def build_valid(tmp_path):
    out = tmp_path / "identity-bind"
    result = build_from_files(
        FIXTURE / "identity.claims.valid.json",
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        out,
    )
    return out, result


def test_valid_identity_binding_verifies(tmp_path):
    out, result = build_valid(tmp_path)

    assert result["verdict"]["verdict"] == VALID
    assert (out / "identity.binding.json").exists()
    assert (out / "identity.verdict.json").exists()
    assert (out / "identity.report.md").exists()

    verdict = verify_from_files(
        FIXTURE / "identity.claims.valid.json",
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        out / "identity.binding.json",
        tmp_path / "verify",
    )
    assert verdict["verdict"] == VALID


def test_expired_identity_fails(tmp_path):
    result = build_from_files(
        FIXTURE / "identity.claims.expired.json",
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == EXPIRED_IDENTITY


def test_unregistered_workload_fails_identity_not_active(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.valid.json").read_text())
    claims["workload_id"] = "github-actions:unknown"

    clean = dict(claims)
    clean.pop("identity_digest", None)
    import hashlib
    digest = "sha256:" + hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    claims["identity_digest"] = digest

    path = tmp_path / "identity.json"
    path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        path,
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == IDENTITY_NOT_ACTIVE
    assert result["verdict"]["reason"] == "workload_not_registered"


def test_controller_mismatch_fails_scope_mismatch(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.scope_mismatch.json").read_text())
    registry = json.loads((FIXTURE / "identity.registry.json").read_text())

    # Isolate controller scope mismatch. The identity must still be ACTIVE
    # in registry; otherwise the verifier correctly returns IDENTITY_NOT_ACTIVE
    # before reaching the controller_id check.
    registry["active_identities"]["github-actions:ci-basic"]["identity_digest"] = claims["identity_digest"]

    registry_path = tmp_path / "identity.registry.scope_mismatch.json"
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        FIXTURE / "identity.claims.scope_mismatch.json",
        registry_path,
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == SCOPE_MISMATCH
    assert result["verdict"]["reason"] == "controller_id_mismatch"


def test_artifact_mismatch_fails_scope_mismatch(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.valid.json").read_text())
    claims["artifact_id"] = "wrong-artifact"
    clean = dict(claims)
    clean.pop("identity_digest", None)
    import hashlib
    digest = "sha256:" + hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    claims["identity_digest"] = digest

    registry = json.loads((FIXTURE / "identity.registry.json").read_text())
    registry["active_identities"]["github-actions:ci-basic"]["identity_digest"] = digest

    claims_path = tmp_path / "claims.json"
    registry_path = tmp_path / "registry.json"
    claims_path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n")
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        claims_path,
        registry_path,
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == SCOPE_MISMATCH
    assert result["verdict"]["reason"] == "artifact_id_mismatch"


def test_policy_not_allowed_fails(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.valid.json").read_text())
    claims["allowed_policy_ids"] = ["other-policy"]
    clean = dict(claims)
    clean.pop("identity_digest", None)
    import hashlib
    digest = "sha256:" + hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    claims["identity_digest"] = digest

    registry = json.loads((FIXTURE / "identity.registry.json").read_text())
    registry["active_identities"]["github-actions:ci-basic"]["identity_digest"] = digest

    claims_path = tmp_path / "claims.json"
    registry_path = tmp_path / "registry.json"
    claims_path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n")
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        claims_path,
        registry_path,
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == POLICY_NOT_ALLOWED


def test_tampered_identity_digest_fails_invalid(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.valid.json").read_text())
    claims["identity_digest"] = "sha256:" + ("9" * 64)
    claims_path = tmp_path / "claims.json"
    claims_path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        claims_path,
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == INVALID
    assert result["verdict"]["reason"] == "identity_digest_mismatch"


def test_missing_required_field_malformed(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.valid.json").read_text())
    claims.pop("identity_id")
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        path,
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == MALFORMED


def test_unsupported_schema_fails(tmp_path):
    claims = json.loads((FIXTURE / "identity.claims.valid.json").read_text())
    claims["schema_version"] = "aapp.workload_identity_claims.v999"
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n")

    result = build_from_files(
        path,
        FIXTURE / "identity.registry.json",
        FIXTURE / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == UNSUPPORTED


def test_private_key_or_secret_is_unsafe(tmp_path):
    unsafe_dir = tmp_path / "unsafe"
    shutil.copytree(FIXTURE, unsafe_dir)

    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    (unsafe_dir / "unsafe.pem").write_text(marker + "\nnot-real\n", encoding="utf-8")

    result = build_from_files(
        unsafe_dir / "identity.claims.valid.json",
        unsafe_dir / "identity.registry.json",
        unsafe_dir / "attestation.binding.json",
        tmp_path / "out",
    )
    assert result["verdict"]["verdict"] == UNSAFE
    assert result["verdict"]["unsafe_findings"]


def test_machine_readable_verdict(tmp_path):
    out, result = build_valid(tmp_path)
    verdict = json.loads((out / "identity.verdict.json").read_text())

    assert verdict["schema_version"] == "aapp.workload_identity_verdict.v1"
    assert verdict["verdict"] == VALID
    assert result["binding"]["binding_hash"].startswith("sha256:")
    assert result["binding"]["dev_signature"].startswith("sha256:")
