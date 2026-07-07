from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "aapp.verify_pack.v1"

VERIFIED = "VERIFIED"
FAILED = "FAILED"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"

SUPPORTED_HASH_ALGS = {"sha256"}

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _iter_files(package: Path):
    for path in package.rglob("*"):
        if path.is_file():
            yield path


def _unsafe_findings(package: Path) -> list[dict[str, Any]]:
    findings = []
    for path in _iter_files(package):
        rel = path.relative_to(package).as_posix()
        text = _safe_text(path)

        if PRIVATE_KEY_RE.search(text):
            findings.append({
                "type": "private_key",
                "file_path": rel,
                "reason": "private key marker detected",
            })

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({
                    "type": "secret_pattern",
                    "file_path": rel,
                    "reason": "secret-like token detected",
                })
                break

    return findings


def _load_manifest(package: Path) -> tuple[dict[str, Any] | None, str | None]:
    manifest_path = package / "manifest.json"
    if not manifest_path.exists():
        return None, "missing_manifest"
    try:
        manifest = _read_json(manifest_path)
    except Exception:
        return None, "manifest_not_json"
    if not isinstance(manifest, dict):
        return None, "manifest_not_object"
    return manifest, None


def verify_package(package_path: str | Path) -> dict[str, Any]:
    package = Path(package_path).resolve()

    base = {
        "schema_version": SCHEMA_VERSION,
        "package_path": str(package),
        "verdict": None,
        "reason": None,
        "checks": [],
        "unsafe_findings": [],
    }

    if not package.exists() or not package.is_dir():
        return {**base, "verdict": MALFORMED, "reason": "package_not_directory"}

    manifest, manifest_error = _load_manifest(package)
    if manifest_error:
        return {**base, "verdict": MALFORMED, "reason": manifest_error}

    if manifest.get("schema_version") != SCHEMA_VERSION:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_manifest_schema"}

    hash_alg = manifest.get("hash_alg", "sha256")
    if hash_alg not in SUPPORTED_HASH_ALGS:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_hash_alg"}

    required_files = manifest.get("required_files", [])
    if not isinstance(required_files, list):
        return {**base, "verdict": MALFORMED, "reason": "required_files_not_list"}

    files = manifest.get("files", {})
    if not isinstance(files, dict):
        return {**base, "verdict": MALFORMED, "reason": "files_not_object"}

    if "signature.profile.json" not in required_files:
        return {**base, "verdict": MALFORMED, "reason": "signature_profile_not_required"}

    if not any(str(p).endswith(".trace.jsonl") for p in required_files):
        return {**base, "verdict": MALFORMED, "reason": "no_required_trace_file"}

    for rel in required_files:
        p = package / rel
        if not p.exists() or not p.is_file():
            return {**base, "verdict": MALFORMED, "reason": f"missing_required_file:{rel}"}

    unsafe = _unsafe_findings(package)
    if unsafe:
        return {
            **base,
            "verdict": UNSAFE,
            "reason": "unsafe_content_detected",
            "unsafe_findings": unsafe,
        }

    checks = []
    for rel, expected_digest in files.items():
        p = package / rel
        if not p.exists() or not p.is_file():
            return {**base, "verdict": MALFORMED, "reason": f"manifest_file_missing:{rel}"}
        actual = _sha256(p)
        ok = actual == expected_digest
        checks.append({
            "file_path": rel,
            "expected": expected_digest,
            "actual": actual,
            "ok": ok,
        })
        if not ok:
            return {
                **base,
                "verdict": FAILED,
                "reason": f"digest_mismatch:{rel}",
                "checks": checks,
            }

    return {
        **base,
        "verdict": VERIFIED,
        "reason": "all_checks_passed",
        "checks": checks,
    }


def run_file(package_path: str | Path, out: str | Path) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    verdict = verify_package(package_path)
    _write_json(out / "verify.verdict.json", verdict)

    lines = [
        "# Verify Pack",
        "",
        f"- Package: `{verdict['package_path']}`",
        f"- Verdict: `{verdict['verdict']}`",
        f"- Reason: `{verdict['reason']}`",
        f"- Checks: `{len(verdict.get('checks', []))}`",
        f"- Unsafe findings: `{len(verdict.get('unsafe_findings', []))}`",
        "",
    ]

    for check in verdict.get("checks", []):
        lines += [
            f"## {check['file_path']}",
            "",
            f"- Expected: `{check['expected']}`",
            f"- Actual: `{check['actual']}`",
            f"- OK: `{check['ok']}`",
            "",
        ]

    for finding in verdict.get("unsafe_findings", []):
        lines += [
            f"## UNSAFE: {finding['type']}",
            "",
            f"- File: `{finding['file_path']}`",
            f"- Reason: {finding['reason']}",
            "",
        ]

    (out / "verify.report.md").write_text("\n".join(lines), encoding="utf-8")
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Agent Black Box evidence package.")
    parser.add_argument("--package", required=True, help="Evidence package directory.")
    parser.add_argument("--out", default=".aapp/verify-pack", help="Output directory.")
    args = parser.parse_args(argv)

    verdict = run_file(args.package, args.out)
    print(
        "AAPP verify pack complete: "
        f"verdict={verdict['verdict']} "
        f"reason={verdict['reason']} "
        f"out={Path(args.out).resolve()}"
    )
    return 0 if verdict["verdict"] == VERIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
