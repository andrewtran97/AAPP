"""AAPP command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from .crypto import attach_signature, verify_chain
from .record import create_record
from .scope import ScopeError, load_scope, require_authorized_scope, scope_id

DEFAULT_DEV_KEY = b"aapp-local-dev-key-do-not-use-in-production"

def _write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")

def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def _read_key(path: Path | None) -> bytes:
    if path is None:
        return DEFAULT_DEV_KEY
    return path.read_bytes().strip()

def _write_dev_key(path: Path) -> None:
    path.write_bytes(DEFAULT_DEV_KEY + b"\n")

def _generate_demo_records(scope_path: str) -> List[Dict[str, Any]]:
    scope = load_scope(scope_path)
    session_id = "demo-session-001"
    parent_hash = None
    records: List[Dict[str, Any]] = []

    actions = [
        ("read_file", "file_read", "allow", "read-only repository inspection", "README.md", "file digest generated", None, None),
        ("edit_file", "file_write", "require_human_approval", "repository write requires approval", "proposed patch for docs", "patch staged for review", None, "approval-001"),
        ("run_tests", "shell", "allow", "test command in authorized scope", "python3 -m unittest", "PASS", None, None),
        ("secret_redaction_check", "artifact", "warn", "secret-like value redacted before report", "api_key=sk-1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", "secret-like value redacted", None, None),
        ("create_report", "artifact", "allow", "generate sanitized evidence report", "trace.jsonl", "evidence.report.md", "report digest only", None),
    ]

    for tool_id, tool_type, decision, reason, input_payload, output_payload, artifact_payload, approval_ref in actions:
        require_authorized_scope(scope=scope, actor_type="agent", tool_type=tool_type)

        record = create_record(
            session_id=session_id,
            parent_hash=parent_hash,
            actor_id="aapp-demo-agent",
            actor_type="agent",
            model_id="local-demo",
            scope_id=scope_id(scope),
            authorization_status="authorized",
            policy_id="policy-demo-human-controlled",
            tool_id=tool_id,
            tool_type=tool_type,
            decision=decision,
            reason=reason,
            input_payload=input_payload,
            output_payload=output_payload,
            artifact_payload=artifact_payload,
            approval_ref=approval_ref,
        )
        signed = attach_signature(record, DEFAULT_DEV_KEY)
        records.append(signed)
        parent_hash = signed["record_hash"]

    return records

def _render_report(records: List[Dict[str, Any]]) -> str:
    lines = [
        "# AAPP Evidence Report",
        "",
        "## Summary",
        "",
        f"Records: {len(records)}",
        "",
        "Raw secrets stored: No",
        "",
        "## Records",
        "",
    ]

    for index, record in enumerate(records):
        lines.extend([
            f"### Record {index + 1}",
            "",
            f"- Record ID: `{record['record_id']}`",
            f"- Actor: `{record['actor']['actor_id']}`",
            f"- Tool: `{record['tool']['tool_id']}`",
            f"- Tool type: `{record['tool']['tool_type']}`",
            f"- Scope ID: `{record['scope']['scope_id']}`",
            f"- Policy decision: `{record['policy']['decision']}`",
            f"- Reason: {record['policy']['reason']}",
            f"- Parent hash: `{record['parent_hash']}`",
            f"- Record hash: `{record['record_hash']}`",
            f"- Input digest: `{record['input_digest']}`",
            f"- Output digest: `{record['output_digest']}`",
            f"- Artifact digest: `{record['artifact_digest']}`",
            f"- Raw secret stored: `{record.get('redaction', {}).get('raw_secret_stored')}`",
            "",
        ])

    return "\n".join(lines)

def cmd_demo(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    trace_path = out_dir / "trace.jsonl"
    key_path = out_dir / "dev.key"
    report_path = out_dir / "evidence.report.md"

    try:
        records = _generate_demo_records(args.scope)
    except ScopeError as exc:
        print(f"BLOCKED: {exc}")
        return 2

    _write_jsonl(trace_path, records)
    _write_dev_key(key_path)
    report_path.write_text(_render_report(records), encoding="utf-8")

    print(f"PASS: wrote {trace_path}")
    print(f"PASS: wrote {key_path}")
    print(f"PASS: wrote {report_path}")
    print("WARN: dev.key is for local demo only; do not use in production")
    return 0

def cmd_verify(args: argparse.Namespace) -> int:
    trace_path = Path(args.trace)

    from .verifier import VerifierError, validate_trace_semantics

    try:
        validate_trace_semantics(trace_path, args.scope)
    except VerifierError as exc:
        import sys
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    key = _read_key(Path(args.key_file) if args.key_file else None)
    records = _read_jsonl(trace_path)

    ok, messages = verify_chain(records, key)
    for message in messages:
        print(message)

    if ok:
        print("PASS: action chain verified")
        return 0

    print("FAIL: action chain verification failed")
    return 1

def cmd_report(args: argparse.Namespace) -> int:
    records = _read_jsonl(Path(args.trace))
    report = _render_report(records)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"PASS: wrote {args.out}")
    else:
        print(report)

    return 0

def cmd_scope_check(args: argparse.Namespace) -> int:
    try:
        scope = load_scope(args.scope)
        require_authorized_scope(scope=scope, actor_type=args.actor_type, tool_type=args.tool_type)
    except ScopeError as exc:
        print(f"BLOCKED: {exc}")
        return 2

    print("PASS: scope authorizes requested operation")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aapp", description="AAPP local reference recorder")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="create a local demo evidence bundle")
    demo.add_argument("--scope", required=True, help="authorized scope JSON file")
    demo.add_argument("--out", default="evidence/demo", help="output directory")
    demo.set_defaults(func=cmd_demo)

    verify = sub.add_parser("verify", help="verify a JSONL action chain")
    verify.add_argument("trace", help="trace.jsonl path")
    verify.add_argument("--key-file", help="dev key file path")
    verify.add_argument("--scope", required=False, help="optional AAPP scope JSON for semantic scope checks")
    verify.set_defaults(func=cmd_verify)

    report = sub.add_parser("report", help="generate Markdown report from JSONL action chain")
    report.add_argument("trace", help="trace.jsonl path")
    report.add_argument("--out", help="output Markdown path")
    report.set_defaults(func=cmd_report)

    scope_check = sub.add_parser("scope-check", help="check whether scope authorizes an operation")
    scope_check.add_argument("--scope", required=True, help="authorized scope JSON file")
    scope_check.add_argument("--actor-type", required=True, help="actor type")
    scope_check.add_argument("--tool-type", required=True, help="tool type")
    scope_check.set_defaults(func=cmd_scope_check)

    return parser

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
