import json
import shutil
from pathlib import Path

from aapp.verify_pack import (
    FAILED,
    MALFORMED,
    UNSAFE,
    UNSUPPORTED,
    VERIFIED,
    run_file,
    verify_package,
)


FIXTURES = Path(__file__).parent / "fixtures" / "verify_pack"


def test_valid_package_verified(tmp_path):
    verdict = run_file(FIXTURES / "valid", tmp_path / "verify")
    assert verdict["verdict"] == VERIFIED
    assert verdict["reason"] == "all_checks_passed"
    assert (tmp_path / "verify" / "verify.verdict.json").exists()
    assert (tmp_path / "verify" / "verify.report.md").exists()


def test_tampered_package_failed():
    verdict = verify_package(FIXTURES / "tampered")
    assert verdict["verdict"] == FAILED
    assert verdict["reason"].startswith("digest_mismatch:")


def test_missing_manifest_malformed():
    verdict = verify_package(FIXTURES / "missing_manifest")
    assert verdict["verdict"] == MALFORMED
    assert verdict["reason"] == "missing_manifest"


def test_unsupported_schema_unsupported():
    verdict = verify_package(FIXTURES / "unsupported")
    assert verdict["verdict"] == UNSUPPORTED


def test_private_key_package_unsafe(tmp_path):
    pkg = tmp_path / "unsafe_private"
    shutil.copytree(FIXTURES / "valid", pkg)

    marker = "-----BEGIN " + "RSA " + "PRIVATE " + "KEY-----"
    (pkg / "reports" / "unsafe.pem").write_text(marker + "\nnot-a-real-key\n", encoding="utf-8")

    manifest = json.loads((pkg / "manifest.json").read_text())
    manifest["required_files"].append("reports/unsafe.pem")
    import hashlib
    digest = "sha256:" + hashlib.sha256((pkg / "reports" / "unsafe.pem").read_bytes()).hexdigest()
    manifest["files"]["reports/unsafe.pem"] = digest
    (pkg / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    verdict = verify_package(pkg)
    assert verdict["verdict"] == UNSAFE
    assert verdict["unsafe_findings"]


def test_secret_like_package_unsafe(tmp_path):
    pkg = tmp_path / "unsafe_secret"
    shutil.copytree(FIXTURES / "valid", pkg)

    token = "gh" + "p_" + ("A" * 36)
    (pkg / "reports" / "unsafe_token.txt").write_text(token + "\n", encoding="utf-8")

    manifest = json.loads((pkg / "manifest.json").read_text())
    manifest["required_files"].append("reports/unsafe_token.txt")
    import hashlib
    digest = "sha256:" + hashlib.sha256((pkg / "reports" / "unsafe_token.txt").read_bytes()).hexdigest()
    manifest["files"]["reports/unsafe_token.txt"] = digest
    (pkg / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    verdict = verify_package(pkg)
    assert verdict["verdict"] == UNSAFE
    assert verdict["unsafe_findings"]


def test_verdict_json_is_machine_readable(tmp_path):
    run_file(FIXTURES / "valid", tmp_path / "verify")
    verdict = json.loads((tmp_path / "verify" / "verify.verdict.json").read_text())
    assert verdict["schema_version"] == "aapp.verify_pack.v1"
    assert verdict["verdict"] == VERIFIED
