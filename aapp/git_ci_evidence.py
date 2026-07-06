from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from aapp.agent_blackbox_hook import redact


DOMAIN = b"AAPP_GIT_CI_RECORD_V1\x00"
DEFAULT_OUT = ".aapp/evidence/git-ci"
TRACE_NAME = "gitci.trace.jsonl"
KEY_NAME = "dev.key"

GITHUB_ACTIONS_ENV_KEYS = [
    "GITHUB_ACTIONS",
    "GITHUB_ACTOR",
    "GITHUB_EVENT_NAME",
    "GITHUB_JOB",
    "GITHUB_REF",
    "GITHUB_REF_NAME",
    "GITHUB_REPOSITORY",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_NUMBER",
    "GITHUB_SERVER_URL",
    "GITHUB_SHA",
    "GITHUB_WORKFLOW",
    "GITHUB_WORKSPACE",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha384(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def _digest_text(text: str) -> str:
    return _sha384(text.encode("utf-8"))


def _digest_obj(obj: Any) -> str:
    return _sha384(_canonical(obj))


def _json_line(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _run(repo: Path, args: List[str], timeout: int = 20) -> Tuple[int, str, str]:
    result = subprocess.run(
        args,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def _git(repo: Path, args: List[str], timeout: int = 20) -> str:
    code, out, err = _run(repo, ["git", *args], timeout=timeout)
    if code != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {err.strip()}")
    return out.strip()


def _safe_git(repo: Path, args: List[str], default: str = "", timeout: int = 20) -> str:
    code, out, _err = _run(repo, ["git", *args], timeout=timeout)
    if code != 0:
        return default
    return out.strip()


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


def _trace_path(out_dir: Path) -> Path:
    return out_dir / TRACE_NAME


def _read_trace(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"record at line {line_no} must be a JSON object")
        records.append(value)
    return records


def _last_hash(records: List[Dict[str, Any]]) -> str | None:
    if not records:
        return None
    value = records[-1].get("record_hash")
    return value if isinstance(value, str) else None


def _record_hash(unsigned_record: Dict[str, Any]) -> str:
    return _sha384(DOMAIN + _canonical(unsigned_record))


def _sign(key: bytes, record_hash: str) -> str:
    return hmac.new(key, record_hash.encode("utf-8"), hashlib.sha384).hexdigest()


def _github_actions_env() -> Dict[str, str]:
    clean: Dict[str, str] = {}
    for key in GITHUB_ACTIONS_ENV_KEYS:
        value = os.environ.get(key)
        if value is not None:
            clean[key] = value
    return clean


def _gh_run_view(repo: Path, run_id: str | None) -> Dict[str, Any] | None:
    if not run_id:
        return None

    cmd = [
        "gh",
        "run",
        "view",
        run_id,
        "--json",
        "attempt,conclusion,createdAt,databaseId,event,headBranch,headSha,name,number,status,updatedAt,url,workflowName",
    ]
    code, out, _err = _run(repo, cmd, timeout=25)
    if code != 0 or not out.strip():
        return None

    value = json.loads(out)
    return value if isinstance(value, dict) else None


def collect_git_ci_snapshot(repo: Path, run_id: str | None = None) -> Dict[str, Any]:
    repo = repo.resolve()

    head_sha = _git(repo, ["rev-parse", "HEAD"])
    branch = _safe_git(repo, ["branch", "--show-current"], default="")
    remote_url = _safe_git(repo, ["remote", "get-url", "origin"], default="")

    status_short = _safe_git(repo, ["status", "--short", "--untracked-files=no"], default="")
    staged_diff = _safe_git(repo, ["diff", "--cached", "--binary"], default="", timeout=30)
    unstaged_diff = _safe_git(repo, ["diff", "--binary"], default="", timeout=30)
    last_commit = _safe_git(
        repo,
        ["show", "-s", "--format=%H%n%P%n%an%n%ae%n%ad%n%s", "--date=iso-strict", "HEAD"],
        default="",
    )

    env = _github_actions_env()
    effective_run_id = run_id or env.get("GITHUB_RUN_ID")
    gh_run = _gh_run_view(repo, effective_run_id)

    return {
        "repo_path_digest": _digest_text(str(repo)),
        "remote_url_digest": _digest_text(remote_url) if remote_url else None,
        "branch": branch,
        "head_sha": head_sha,
        "head_short": head_sha[:12],
        "tracked_status_line_count": len([x for x in status_short.splitlines() if x.strip()]),
        "status_short_digest": _digest_text(status_short),
        "staged_diff_digest": _digest_text(staged_diff),
        "unstaged_diff_digest": _digest_text(unstaged_diff),
        "last_commit_digest": _digest_text(last_commit),
        "github_actions": redact(env),
        "gh_run": redact(gh_run) if gh_run else None,
    }


def append_record(snapshot: Dict[str, Any], out_dir: Path, session_id: str) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    key = _load_or_create_key(out_dir)
    trace = _trace_path(out_dir)
    records = _read_trace(trace)

    unsigned: Dict[str, Any] = {
        "schema_version": "aapp.git_ci.record.v1",
        "session_id": session_id,
        "seq": len(records),
        "adapter": "git-ci",
        "snapshot": snapshot,
        "snapshot_digest": _digest_obj(snapshot),
        "parent_hash": _last_hash(records),
        "timestamp": _utc_now(),
    }

    record_hash = _record_hash(unsigned)
    signed = dict(unsigned)
    signed["record_hash"] = record_hash
    signed["signature_type"] = "dev-hmac-sha384"
    signed["signature"] = _sign(key, record_hash)

    with trace.open("a", encoding="utf-8") as f:
        f.write(_json_line(signed) + "\n")

    return signed


def verify_trace(trace_path: Path, key_path: Path) -> Tuple[bool, str]:
    key = _load_key(key_path)
    records = _read_trace(trace_path)
    parent: str | None = None

    for idx, record in enumerate(records):
        if record.get("parent_hash") != parent:
            return False, f"parent hash mismatch at record {idx}"

        snapshot = record.get("snapshot")
        if not isinstance(snapshot, dict):
            return False, f"missing snapshot at record {idx}"

        if record.get("snapshot_digest") != _digest_obj(snapshot):
            return False, f"snapshot digest mismatch at record {idx}"

        claimed_hash = record.get("record_hash")
        claimed_signature = record.get("signature")

        unsigned = dict(record)
        unsigned.pop("record_hash", None)
        unsigned.pop("signature", None)
        unsigned.pop("signature_type", None)

        calculated_hash = _record_hash(unsigned)
        if claimed_hash != calculated_hash:
            return False, f"record hash mismatch at record {idx}"

        calculated_signature = _sign(key, calculated_hash)
        if claimed_signature != calculated_signature:
            return False, f"signature mismatch at record {idx}"

        parent = calculated_hash

    return True, f"verified {len(records)} records"


def write_report(trace_path: Path, out_path: Path) -> None:
    records = _read_trace(trace_path)
    lines = [
        "# Agent Black Box Git/CI Evidence Report",
        "",
        f"Trace: `{trace_path}`",
        f"Records: {len(records)}",
        "",
        "| Seq | Branch | Commit | Status lines | GitHub run | CI status | CI conclusion | Record hash |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        snapshot = record.get("snapshot", {})
        gh_run = snapshot.get("gh_run") if isinstance(snapshot, dict) else None
        if not isinstance(gh_run, dict):
            gh_run = {}

        lines.append(
            "| {seq} | {branch} | `{commit}` | {status_lines} | {run_id} | {status} | {conclusion} | `{record_hash}` |".format(
                seq=record.get("seq"),
                branch=snapshot.get("branch", "") if isinstance(snapshot, dict) else "",
                commit=snapshot.get("head_short", "") if isinstance(snapshot, dict) else "",
                status_lines=snapshot.get("tracked_status_line_count", "") if isinstance(snapshot, dict) else "",
                run_id=gh_run.get("databaseId", ""),
                status=gh_run.get("status", ""),
                conclusion=gh_run.get("conclusion", ""),
                record_hash=str(record.get("record_hash", ""))[:32],
            )
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Black Box Git/CI evidence adapter")
    sub = parser.add_subparsers(dest="cmd", required=True)

    capture = sub.add_parser("capture", help="Capture Git and optional CI evidence")
    capture.add_argument("--repo", default=".")
    capture.add_argument("--out", default=DEFAULT_OUT)
    capture.add_argument("--session-id", default="git-ci-session")
    capture.add_argument("--run-id")

    verify = sub.add_parser("verify", help="Verify Git/CI evidence trace")
    verify.add_argument("trace")
    verify.add_argument("--key-file", required=True)

    report = sub.add_parser("report", help="Write a Markdown report from a Git/CI trace")
    report.add_argument("trace")
    report.add_argument("--out", required=True)

    ns = parser.parse_args(list(argv) if argv is not None else None)

    if ns.cmd == "capture":
        snapshot = collect_git_ci_snapshot(Path(ns.repo), ns.run_id)
        signed = append_record(snapshot, Path(ns.out), ns.session_id)
        print(json.dumps({"record_hash": signed["record_hash"], "trace": str(_trace_path(Path(ns.out)))}, sort_keys=True))
        return 0

    if ns.cmd == "verify":
        ok, message = verify_trace(Path(ns.trace), Path(ns.key_file))
        print(("PASS: " if ok else "FAIL: ") + message)
        return 0 if ok else 1

    if ns.cmd == "report":
        write_report(Path(ns.trace), Path(ns.out))
        print(f"PASS: wrote {ns.out}")
        return 0

    raise AssertionError(ns.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
