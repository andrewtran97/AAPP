import json
import shutil
from pathlib import Path

from aapp.attestation_binding import (
    INVALID,
    MALFORMED,
    POLICY_MISMATCH,
    STALE_POLICY,
    UNSAFE,
    UNSUPPORTED,
    VALID,
    build_from_files,
    verify_from_files,
)


FIXTURE = Path(__file__).parent / "fixtures" / "attestation_binding"


def build_valid(tmp_path):
    out = tmp_path / "binding"
    result = build_from_files(
        FIXTURE / "evidence.json",
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        FIXTURE / "policy.json",
        FIXTURE / "active_policy_registry.json",
        FIXTURE / "decision.json",
        out,
    )
    return out, result


def test_valid_binding_verifies(tmp_path):
    out, result = build_valid(tmp_path)
    assert result["verdict"]["verdict"] == VALID
    assert (out / "attestation.binding.json").exists()
    assert (out / "attestation.verdict.json").exists()
    assert (out / "attestation.report.md").exists()

    verdict = verify_from_files(
        out / "attestation.binding.json",
        FIXTURE / "evidence.json",
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        FIXTURE / "policy.json",
        FIXTURE / "active_policy_registry.json",
        tmp_path / "verify",
    )

    assert verdict["verdict"] == VALID


def test_tampered_evidence_fails_invalid(tmp_path):
    out, _ = build_valid(tmp_path)
    tampered = tmp_path / "evidence.json"
    data = json.loads((FIXTURE / "evidence.json").read_text())
    data["records_digest"] = "sha256:" + ("0" * 64)
    tampered.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    verdict = verify_from_files(
        out / "attestation.binding.json",
        tampered,
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        FIXTURE / "policy.json",
        FIXTURE / "active_policy_registry.json",
        tmp_path / "verify",
    )

    assert verdict["verdict"] == INVALID
    assert verdict["reason"] == "evidence_digest_mismatch"


def test_tampered_artifact_controller_runtime_fail_invalid(tmp_path):
    out, _ = build_valid(tmp_path)

    for name, reason in [
        ("artifact", "artifact_digest_mismatch"),
        ("controller", "controller_digest_mismatch"),
        ("runtime", "runtime_digest_mismatch"),
    ]:
        tampered = tmp_path / f"{name}.json"
        data = json.loads((FIXTURE / f"{name}.json").read_text())
        data["tampered"] = True
        tampered.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

        paths = {
            "artifact": FIXTURE / "artifact.json",
            "controller": FIXTURE / "controller.json",
            "runtime": FIXTURE / "runtime.json",
        }
        paths[name] = tampered

        verdict = verify_from_files(
            out / "attestation.binding.json",
            FIXTURE / "evidence.json",
            paths["artifact"],
            paths["controller"],
            paths["runtime"],
            FIXTURE / "policy.json",
            FIXTURE / "active_policy_registry.json",
            tmp_path / f"verify-{name}",
        )

        assert verdict["verdict"] == INVALID
        assert verdict["reason"] == reason


def test_tampered_policy_fails_policy_mismatch(tmp_path):
    out, _ = build_valid(tmp_path)
    tampered = tmp_path / "policy.json"
    data = json.loads((FIXTURE / "policy.json").read_text())
    data["rules_digest"] = "sha256:" + ("1" * 64)
    tampered.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    verdict = verify_from_files(
        out / "attestation.binding.json",
        FIXTURE / "evidence.json",
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        tampered,
        FIXTURE / "active_policy_registry.json",
        tmp_path / "verify",
    )

    assert verdict["verdict"] == POLICY_MISMATCH
    assert verdict["reason"] == "policy_digest_mismatch"


def test_stale_policy_version_fails(tmp_path):
    out, _ = build_valid(tmp_path)
    stale_registry = tmp_path / "registry.json"
    registry = json.loads((FIXTURE / "active_policy_registry.json").read_text())
    registry["active_policies"]["default-agent-policy"]["policy_version"] = "v2"
    stale_registry.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")

    verdict = verify_from_files(
        out / "attestation.binding.json",
        FIXTURE / "evidence.json",
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        FIXTURE / "policy.json",
        stale_registry,
        tmp_path / "verify",
    )

    assert verdict["verdict"] == STALE_POLICY
    assert verdict["reason"] == "policy_version_not_active"


def test_missing_required_field_malformed(tmp_path):
    out, _ = build_valid(tmp_path)
    binding_path = out / "attestation.binding.json"
    binding = json.loads(binding_path.read_text())
    binding.pop("policy")
    binding_path.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n")

    verdict = verify_from_files(
        binding_path,
        FIXTURE / "evidence.json",
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        FIXTURE / "policy.json",
        FIXTURE / "active_policy_registry.json",
        tmp_path / "verify",
    )

    assert verdict["verdict"] == MALFORMED


def test_unsupported_schema_fails(tmp_path):
    out, _ = build_valid(tmp_path)
    binding_path = out / "attestation.binding.json"
    binding = json.loads(binding_path.read_text())
    binding["schema_version"] = "aapp.attestation_binding.v999"
    binding_path.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n")

    verdict = verify_from_files(
        binding_path,
        FIXTURE / "evidence.json",
        FIXTURE / "artifact.json",
        FIXTURE / "controller.json",
        FIXTURE / "runtime.json",
        FIXTURE / "policy.json",
        FIXTURE / "active_policy_registry.json",
        tmp_path / "verify",
    )

    assert verdict["verdict"] == UNSUPPORTED


def test_private_key_or_secret_is_unsafe(tmp_path):
    out, _ = build_valid(tmp_path)

    unsafe_dir = tmp_path / "unsafe"
    shutil.copytree(FIXTURE, unsafe_dir)

    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    (unsafe_dir / "unsafe.pem").write_text(marker + "\nnot-real\n", encoding="utf-8")

    verdict = verify_from_files(
        out / "attestation.binding.json",
        unsafe_dir / "evidence.json",
        unsafe_dir / "artifact.json",
        unsafe_dir / "controller.json",
        unsafe_dir / "runtime.json",
        unsafe_dir / "policy.json",
        unsafe_dir / "active_policy_registry.json",
        tmp_path / "verify-unsafe",
    )

    assert verdict["verdict"] == UNSAFE
    assert verdict["unsafe_findings"]


def test_machine_readable_verdict(tmp_path):
    out, result = build_valid(tmp_path)
    verdict = json.loads((out / "attestation.verdict.json").read_text())

    assert verdict["schema_version"] == "aapp.attestation_verdict.v1"
    assert verdict["verdict"] == VALID
    assert result["binding"]["binding_hash"].startswith("sha256:")
    assert result["binding"]["dev_signature"].startswith("sha256:")
