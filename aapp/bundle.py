from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .crypto import verify_chain
from .verifier import VerifierError, validate_trace_semantics


DEFAULT_DEV_KEY = b"aapp-local-dev-key-do-not-use-in-production"
BUNDLE_SCHEMA_VERSION = "0.4.0"
BUNDLE_TYPE = "AAPP-EVIDENCE-BUNDLE"

SECRET_LIKE_MARKERS = (
    "api_key=",
    "password=",
    "BEGIN PRIVATE KEY",
    "ghp_",
    "github_pat_",
    "sk-1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ",
)


class BundleError(Exception):
    """Raised when an AAPP evidence bundle cannot be created safely."""


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        raise BundleError(f"trace record must be an object: {path}")
                    records.append(obj)
    except json.JSONDecodeError as exc:
        raise BundleError(f"malformed JSONL: {exc.msg}") from exc

    if not records:
        raise BundleError("trace contains no records")

    return records


def _read_key(path: Path | None) -> bytes:
    if path is None:
        return DEFAULT_DEV_KEY
    return path.read_bytes().strip()


def _sha384(path: Path) -> str:
    digest = hashlib.sha384()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha384:" + digest.hexdigest()


def _copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise BundleError(f"missing input file: {src}")
    if not src.is_file():
        raise BundleError(f"input is not a file: {src}")
    shutil.copyfile(src, dst)


def _scan_report_for_secret_like_values(report_path: Path) -> None:
    text = report_path.read_text(encoding="utf-8")
    for marker in SECRET_LIKE_MARKERS:
        if marker in text:
            raise BundleError(f"secret-like value found in report: {marker}")


def create_evidence_bundle(
    *,
    scope_path: str | Path,
    trace_path: str | Path,
    key_file: str | Path | None,
    report_path: str | Path,
    out_dir: str | Path,
) -> Dict[str, Any]:
    scope_src = Path(scope_path)
    trace_src = Path(trace_path)
    key_src = Path(key_file) if key_file else None
    report_src = Path(report_path)
    out = Path(out_dir)

    try:
        validate_trace_semantics(trace_src, scope_src)
    except VerifierError as exc:
        raise BundleError(str(exc)) from exc

    records = _read_jsonl(trace_src)
    key = _read_key(key_src)
    ok, messages = verify_chain(records, key)
    if not ok:
        raise BundleError("trace signature/hash verification failed")

    _scan_report_for_secret_like_values(report_src)

    if out.exists():
        if not out.is_dir():
            raise BundleError(f"output path exists and is not a directory: {out}")
    else:
        out.mkdir(parents=True)

    scope_dst = out / "scope.json"
    trace_dst = out / "trace.jsonl"
    report_dst = out / "evidence.report.md"
    verification_dst = out / "verification_result.md"
    hashes_dst = out / "hashes.txt"
    manifest_dst = out / "evidence.bundle.json"

    _copy_file(scope_src, scope_dst)
    _copy_file(trace_src, trace_dst)
    _copy_file(report_src, report_dst)

    verification_lines = [
        "# AAPP Verification Result",
        "",
        "Result: PASS",
        "",
        "Verifier:",
        "",
    ]
    verification_lines.extend(f"- {message}" for message in messages)
    verification_lines.append("")
    verification_dst.write_text("\n".join(verification_lines), encoding="utf-8")

    core_files = [
        "scope.json",
        "trace.jsonl",
        "evidence.report.md",
        "verification_result.md",
    ]

    hashes_lines = []
    for name in core_files:
        hashes_lines.append(f"{_sha384(out / name)}  {name}")
    hashes_dst.write_text("\n".join(hashes_lines) + "\n", encoding="utf-8")

    manifest_files = core_files + ["hashes.txt"]
    manifest = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_type": BUNDLE_TYPE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verification_result": "PASS",
        "files": [
            {
                "path": name,
                "sha384": _sha384(out / name),
            }
            for name in manifest_files
        ],
    }

    manifest_dst.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    return manifest
