from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from aapp.agent_blackbox_hook import redact


DOMAIN = b"AAPP_MCP_PROXY_RECORD_V1\x00"
DEFAULT_OUT = ".aapp/evidence/mcp-proxy"
TRACE_NAME = "mcp.trace.jsonl"
KEY_NAME = "dev.key"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha384(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def _digest_obj(obj: Any) -> str:
    return _sha384(_canonical(obj))


def _json_line(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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


def _read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _read_trace(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL at line {line_no}: {exc}") from exc
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


def _request_id(request: Dict[str, Any]) -> Any:
    return request.get("id")


def _method(request: Dict[str, Any]) -> str:
    value = request.get("method")
    return value if isinstance(value, str) else "unknown"


def _tool_name(request: Dict[str, Any]) -> str | None:
    params = request.get("params")
    if isinstance(params, dict):
        name = params.get("name")
        if isinstance(name, str):
            return name
    return None


def _arguments(request: Dict[str, Any]) -> Any:
    params = request.get("params")
    if isinstance(params, dict):
        return params.get("arguments", {})
    return {}


def _policy_decision(request: Dict[str, Any]) -> Tuple[str, str | None]:
    method = _method(request)

    if method == "tools/call":
        name = _tool_name(request)
        if not name:
            return "deny", "tools/call missing tool name"
        if name.startswith("blocked_"):
            return "deny", "blocked tool name"
        return "allow", None

    return "observe", None


def append_record(
    request: Dict[str, Any],
    response: Dict[str, Any] | None,
    out_dir: Path,
    session_id: str,
) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    key = _load_or_create_key(out_dir)
    trace = _trace_path(out_dir)
    records = _read_trace(trace)

    redacted_request = redact(request)
    redacted_response = redact(response or {})
    decision, reason = _policy_decision(request)

    unsigned: Dict[str, Any] = {
        "schema_version": "aapp.mcp_proxy.record.v1",
        "session_id": session_id,
        "seq": len(records),
        "jsonrpc": request.get("jsonrpc"),
        "request_id": _request_id(request),
        "method": _method(request),
        "tool_name": _tool_name(request),
        "arguments_digest": _digest_obj(redact(_arguments(request))),
        "request_digest": _digest_obj(redacted_request),
        "response_digest": _digest_obj(redacted_response) if response is not None else None,
        "policy_decision": decision,
        "policy_reason": reason,
        "executed": response is not None and decision != "deny",
        "response_is_error": bool(response and ("error" in response or response.get("result", {}).get("isError") is True)),
        "parent_hash": _last_hash(records),
        "timestamp": _utc_now(),
    }

    record_hash = _record_hash(unsigned)
    signed = dict(unsigned)
    signed["record_hash"] = record_hash
    signed["signature_type"] = "dev-hmac-sha384"
    signed["signature"] = _sign(key, record_hash)

    with trace.open("a", encoding="utf-8") as f:
        f.write(json.dumps(signed, sort_keys=True, ensure_ascii=False) + "\n")

    return signed


def verify_trace(trace_path: Path, key_path: Path) -> Tuple[bool, str]:
    key = _load_key(key_path)
    records = _read_trace(trace_path)
    parent: str | None = None

    for idx, record in enumerate(records):
        if record.get("parent_hash") != parent:
            return False, f"parent hash mismatch at record {idx}"

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

        if record.get("policy_decision") == "deny" and record.get("executed") is not False:
            return False, f"deny record executed at record {idx}"

        parent = calculated_hash

    return True, f"verified {len(records)} records"


def write_report(trace_path: Path, out_path: Path) -> None:
    records = _read_trace(trace_path)
    lines = [
        "# Agent Black Box MCP Proxy Report",
        "",
        f"Trace: `{trace_path}`",
        f"Records: {len(records)}",
        "",
        "| Seq | Method | Tool | Decision | Executed | Error | Record hash |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        lines.append(
            "| {seq} | {method} | {tool} | {decision} | {executed} | {error} | `{hash}` |".format(
                seq=record.get("seq"),
                method=record.get("method"),
                tool=record.get("tool_name") or "",
                decision=record.get("policy_decision"),
                executed=record.get("executed"),
                error=record.get("response_is_error"),
                hash=str(record.get("record_hash", ""))[:32],
            )
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _iter_stdin_json_messages() -> Iterable[Dict[str, Any]]:
    buffer = ""

    for raw in sys.stdin:
        if not raw.strip():
            continue

        buffer += raw

        try:
            value = json.loads(buffer)
        except json.JSONDecodeError:
            continue

        if not isinstance(value, dict):
            raise ValueError("stdin request must be a JSON object")

        yield value
        buffer = ""

    if buffer.strip():
        raise ValueError("incomplete or malformed JSON-RPC message on stdin")


def run_stdio_proxy(server_command: str, out_dir: Path, session_id: str) -> int:
    argv = shlex.split(server_command)
    if not argv:
        raise ValueError("server command is empty")

    proc = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    assert proc.stdin is not None
    assert proc.stdout is not None

    try:
        for request in _iter_stdin_json_messages():
            decision, reason = _policy_decision(request)

            if decision == "deny":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32001,
                        "message": reason or "blocked by Agent Black Box",
                    },
                }
                append_record(request, None, out_dir, session_id)
                print(_json_line(response), flush=True)
                continue

            proc.stdin.write(_json_line(request) + "\n")
            proc.stdin.flush()

            response_line = proc.stdout.readline()
            if not response_line:
                raise RuntimeError("downstream MCP server closed stdout")

            response = json.loads(response_line)
            if not isinstance(response, dict):
                raise ValueError("downstream response must be a JSON object")

            append_record(request, response, out_dir, session_id)
            print(_json_line(response), flush=True)
    finally:
        if proc.stdin:
            proc.stdin.close()
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Black Box MCP proxy recorder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    record = sub.add_parser("record", help="Record one MCP JSON-RPC request/response pair")
    record.add_argument("--request", required=True)
    record.add_argument("--response")
    record.add_argument("--out", default=DEFAULT_OUT)
    record.add_argument("--session-id", default="mcp-local-session")

    stdio = sub.add_parser("stdio", help="Run a minimal stdio MCP pass-through recorder")
    stdio.add_argument("--server-command", required=True)
    stdio.add_argument("--out", default=DEFAULT_OUT)
    stdio.add_argument("--session-id", default="mcp-stdio-session")

    verify = sub.add_parser("verify", help="Verify MCP proxy trace")
    verify.add_argument("trace")
    verify.add_argument("--key-file", required=True)

    report = sub.add_parser("report", help="Write a Markdown report from an MCP proxy trace")
    report.add_argument("trace")
    report.add_argument("--out", required=True)

    ns = parser.parse_args(list(argv) if argv is not None else None)

    if ns.cmd == "record":
        request = _read_json(Path(ns.request))
        response = _read_json(Path(ns.response)) if ns.response else None
        signed = append_record(request, response, Path(ns.out), ns.session_id)
        print(json.dumps({"record_hash": signed["record_hash"], "trace": str(_trace_path(Path(ns.out)))}, sort_keys=True))
        return 0

    if ns.cmd == "stdio":
        return run_stdio_proxy(ns.server_command, Path(ns.out), ns.session_id)

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
