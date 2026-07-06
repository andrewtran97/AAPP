from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


DOMAIN = b"AAPP_SESSION_BUNDLE_V1\x00"
BUNDLE_DIR_NAME = "AGENT-BLACK-BOX-BUNDLE"
KEY_NAME = "dev.key"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha384(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def _digest_file(path: Path) -> str:
    return _sha384(path.read_bytes())


def _load_or_create_key(out_dir: Path) -> bytes:
    out_dir.mkdir(parents=True, exist_ok=True)
    key_path = out_dir / KEY_NAME
    if not key_path.exists():
        key_path.write_text(secrets.token_hex(48) + "\n", encoding="utf-8")
        try:
            key_path.chmod(0o600)
        except OSError:
            pass
    raw = key_path.read_text(encoding="utf-8").strip()
    try:
        return bytes.fromhex(raw)
    except ValueError:
        return raw.encode("utf-8")


def _load_key(path: Path) -> bytes:
    raw = path.read_text(encoding="utf-8").strip()
    try:
        return bytes.fromhex(raw)
    except ValueError:
        return raw.encode("utf-8")


def _sign(key: bytes, digest: str) -> str:
    return hmac.new(key, digest.encode("utf-8"), hashlib.sha384).hexdigest()


def _bundle_digest(unsigned_manifest: Dict[str, Any]) -> str:
    return _sha384(DOMAIN + _canonical(unsigned_manifest))


def _copy_required(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(f"missing source trace: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _write_hashes(bundle_dir: Path, trace_digests: Dict[str, str]) -> None:
    lines = [f"{digest}  {name}" for name, digest in sorted(trace_digests.items())]
    (bundle_dir / "hashes.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_bundle(
    hook_trace: Path,
    mcp_trace: Path,
    git_ci_trace: Path,
    out_dir: Path,
    session_id: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    key = _load_or_create_key(out_dir)

    bundle_dir = out_dir / BUNDLE_DIR_NAME
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    sources = {
        "hook.trace.jsonl": hook_trace,
        "mcp.trace.jsonl": mcp_trace,
        "gitci.trace.jsonl": git_ci_trace,
    }

    for name, src in sources.items():
        _copy_required(src, bundle_dir / name)

    trace_digests = {name: _digest_file(bundle_dir / name) for name in sources}
    _write_hashes(bundle_dir, trace_digests)

    file_digests = dict(trace_digests)
    file_digests["hashes.txt"] = _digest_file(bundle_dir / "hashes.txt")

    unsigned_manifest: Dict[str, Any] = {
        "schema_version": "aapp.session_bundle.v1",
        "session_id": session_id,
        "created_at": _utc_now(),
        "sources": {
            "hook_trace": "hook.trace.jsonl",
            "mcp_trace": "mcp.trace.jsonl",
            "git_ci_trace": "gitci.trace.jsonl",
        },
        "file_digests": file_digests,
    }

    digest = _bundle_digest(unsigned_manifest)
    manifest = dict(unsigned_manifest)
    manifest["bundle_digest"] = digest
    manifest["signature_type"] = "dev-hmac-sha384"
    manifest["signature"] = _sign(key, digest)

    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    ok, message = verify_bundle(bundle_dir, out_dir / KEY_NAME)
    (bundle_dir / "verification_result.md").write_text(
        f"# Verification Result\n\n{'PASS' if ok else 'FAIL'}: {message}\n",
        encoding="utf-8",
    )

    write_report(bundle_dir, bundle_dir / "session.report.md")
    return bundle_dir


def _read_manifest(bundle_dir: Path) -> Dict[str, Any]:
    path = bundle_dir / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing manifest: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("manifest must be a JSON object")
    return value


def _verify_hashes_txt(bundle_dir: Path, file_digests: Dict[str, str]) -> Tuple[bool, str]:
    hashes_path = bundle_dir / "hashes.txt"
    if not hashes_path.is_file():
        return False, "missing hashes.txt"

    expected_lines = []
    for name in ["gitci.trace.jsonl", "hook.trace.jsonl", "mcp.trace.jsonl"]:
        digest = file_digests.get(name)
        if not digest:
            return False, f"missing digest for {name}"
        expected_lines.append(f"{digest}  {name}")

    actual = hashes_path.read_text(encoding="utf-8").strip().splitlines()
    if sorted(actual) != sorted(expected_lines):
        return False, "hashes.txt content mismatch"

    return True, "hashes.txt matches source digests"


def verify_bundle(bundle_dir: Path, key_file: Path) -> Tuple[bool, str]:
    key = _load_key(key_file)
    manifest = _read_manifest(bundle_dir)

    file_digests = manifest.get("file_digests")
    if not isinstance(file_digests, dict):
        return False, "manifest missing file_digests"

    for rel, expected_digest in file_digests.items():
        path = bundle_dir / str(rel)
        if not path.is_file():
            return False, f"missing bundle file: {rel}"
        actual_digest = _digest_file(path)
        if actual_digest != expected_digest:
            return False, f"file digest mismatch: {rel}"

    ok, message = _verify_hashes_txt(bundle_dir, file_digests)
    if not ok:
        return False, message

    claimed_digest = manifest.get("bundle_digest")
    claimed_signature = manifest.get("signature")

    unsigned = dict(manifest)
    unsigned.pop("bundle_digest", None)
    unsigned.pop("signature_type", None)
    unsigned.pop("signature", None)

    calculated_digest = _bundle_digest(unsigned)
    if claimed_digest != calculated_digest:
        return False, "manifest digest mismatch"

    calculated_signature = _sign(key, calculated_digest)
    if claimed_signature != calculated_signature:
        return False, "manifest signature mismatch"

    return True, "bundle verified"


def write_report(bundle_dir: Path, out_path: Path) -> None:
    manifest = _read_manifest(bundle_dir)
    file_digests = manifest.get("file_digests", {})
    lines = [
        "# Agent Black Box Unified Session Report",
        "",
        f"Session: `{manifest.get('session_id', '')}`",
        f"Schema: `{manifest.get('schema_version', '')}`",
        "",
        "## Sources",
        "",
        "- Hook trace: `hook.trace.jsonl`",
        "- MCP trace: `mcp.trace.jsonl`",
        "- Git/CI trace: `gitci.trace.jsonl`",
        "",
        "## File digests",
        "",
        "| File | SHA-384 |",
        "| --- | --- |",
    ]

    if isinstance(file_digests, dict):
        for rel, digest in sorted(file_digests.items()):
            lines.append(f"| `{rel}` | `{digest}` |")

    lines.extend([
        "",
        "## Boundary",
        "",
        "This report summarizes bundle metadata only. It does not inline raw trace contents.",
    ])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Black Box unified session bundle")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create", help="Create unified session bundle")
    create.add_argument("--hook-trace", required=True)
    create.add_argument("--mcp-trace", required=True)
    create.add_argument("--git-ci-trace", required=True)
    create.add_argument("--out", required=True)
    create.add_argument("--session-id", required=True)

    verify = sub.add_parser("verify", help="Verify unified session bundle")
    verify.add_argument("bundle_dir")
    verify.add_argument("--key-file", required=True)

    report = sub.add_parser("report", help="Write unified session report")
    report.add_argument("bundle_dir")
    report.add_argument("--out", required=True)

    ns = parser.parse_args(list(argv) if argv is not None else None)

    if ns.cmd == "create":
        bundle = create_bundle(
            Path(ns.hook_trace),
            Path(ns.mcp_trace),
            Path(ns.git_ci_trace),
            Path(ns.out),
            ns.session_id,
        )
        print(json.dumps({"bundle": str(bundle), "key_file": str(Path(ns.out) / KEY_NAME)}, sort_keys=True))
        return 0

    if ns.cmd == "verify":
        ok, message = verify_bundle(Path(ns.bundle_dir), Path(ns.key_file))
        print(("PASS: " if ok else "FAIL: ") + message)
        return 0 if ok else 1

    if ns.cmd == "report":
        write_report(Path(ns.bundle_dir), Path(ns.out))
        print(f"PASS: wrote {ns.out}")
        return 0

    raise AssertionError(ns.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
