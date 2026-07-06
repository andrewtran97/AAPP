from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


DOMAIN = b"AAPP_AGENT_BLACKBOX_RECORD_V1\x00"
DEFAULT_OUT = ".aapp/evidence/agent-blackbox"
TRACE_NAME = "session.trace.jsonl"
KEY_NAME = "dev.key"

SENSITIVE_KEY_RE = re.compile(
    r"(token|secret|password|passwd|api[_-]?key|authorization|cookie|private[_-]?key|credential)",
    re.IGNORECASE,
)

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{8,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{8,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
]

DESTRUCTIVE_COMMAND_PATTERNS = [
    re.compile(r"\brm\s+-rf\s+/", re.IGNORECASE),
    re.compile(r"\bsudo\s+rm\s+-rf\b", re.IGNORECASE),
    re.compile(r"\bchmod\s+-R\s+777\b", re.IGNORECASE),
    re.compile(r"\b(curl|wget)\b.*\|\s*(sh|bash)\b", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+(--force|-f)\b", re.IGNORECASE),
    re.compile(r"\bmkfs(\.|\\s)", re.IGNORECASE),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha384_bytes(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def _digest_obj(obj: Any) -> str:
    return _sha384_bytes(_canonical(obj))


def _redact_string(value: str) -> str:
    out = value
    for pattern in SENSITIVE_VALUE_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        clean: Dict[str, Any] = {}
        for key, value in obj.items():
            if SENSITIVE_KEY_RE.search(str(key)):
                clean[key] = "[REDACTED]"
            else:
                clean[key] = redact(value)
        return clean
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str):
        return _redact_string(obj)
    return obj


def _out_dir() -> Path:
    return Path(os.environ.get("AAPP_BLACKBOX_OUT", DEFAULT_OUT))


def _key_path(out_dir: Path) -> Path:
    return out_dir / KEY_NAME


def _trace_path(out_dir: Path) -> Path:
    return out_dir / TRACE_NAME


def _load_or_create_key(out_dir: Path) -> bytes:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = _key_path(out_dir)
    if not path.exists():
        path.write_text(secrets.token_hex(48) + "\n", encoding="utf-8")
        try:
            path.chmod(0o600)
        except OSError:
            pass
    raw = path.read_text(encoding="utf-8").strip()
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


def _read_trace(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL at line {line_no}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"record at line {line_no} is not an object")
        records.append(record)
    return records


def _last_hash(records: List[Dict[str, Any]]) -> str | None:
    if not records:
        return None
    value = records[-1].get("record_hash")
    return value if isinstance(value, str) else None


def _record_hash(unsigned_record: Dict[str, Any]) -> str:
    return _sha384_bytes(DOMAIN + _canonical(unsigned_record))


def _sign(key: bytes, record_hash: str) -> str:
    return hmac.new(key, record_hash.encode("utf-8"), hashlib.sha384).hexdigest()


def _tool_command(event: Dict[str, Any]) -> str:
    tool_input = event.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    return ""


def _is_destructive_command(command: str) -> bool:
    return any(pattern.search(command) for pattern in DESTRUCTIVE_COMMAND_PATTERNS)


def _event_name(event: Dict[str, Any]) -> str:
    for key in ("hook_event_name", "hookEventName", "event_name", "event"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _tool_name(event: Dict[str, Any]) -> str:
    value = event.get("tool_name")
    if isinstance(value, str) and value:
        return value
    value = event.get("toolName")
    if isinstance(value, str) and value:
        return value
    return "unknown"


def _session_id(event: Dict[str, Any]) -> str:
    value = event.get("session_id")
    if isinstance(value, str) and value:
        return value
    value = event.get("sessionId")
    if isinstance(value, str) and value:
        return value
    return "local-session"


def _policy_decision(event_name: str, tool_name: str, event: Dict[str, Any]) -> Tuple[str, str | None]:
    if event_name == "PreToolUse" and tool_name == "Bash":
        command = _tool_command(event)
        if _is_destructive_command(command):
            return "deny", "destructive command blocked by Agent Black Box"
        return "allow", None
    if event_name == "PreToolUse":
        return "allow", None
    if event_name == "PostToolUse":
        return "observed_after_execution", None
    return "observed", None


def _executed(event_name: str, decision: str) -> bool:
    if decision == "deny":
        return False
    return event_name == "PostToolUse"


def append_record(event: Dict[str, Any], out_dir: Path | None = None) -> Dict[str, Any]:
    out = out_dir or _out_dir()
    out.mkdir(parents=True, exist_ok=True)
    key = _load_or_create_key(out)
    trace = _trace_path(out)
    records = _read_trace(trace)

    event_name = _event_name(event)
    tool_name = _tool_name(event)
    decision, reason = _policy_decision(event_name, tool_name, event)
    executed = _executed(event_name, decision)

    redacted_input = redact(event.get("tool_input", {}))
    redacted_response = redact(event.get("tool_response", event.get("tool_output", {})))

    unsigned: Dict[str, Any] = {
        "schema_version": "aapp.agent_blackbox.record.v1",
        "session_id": _session_id(event),
        "seq": len(records),
        "cwd": str(event.get("cwd", "")),
        "hook_event_name": event_name,
        "tool_name": tool_name,
        "input_digest": _digest_obj(redacted_input),
        "output_digest": _digest_obj(redacted_response) if redacted_response else None,
        "policy_decision": decision,
        "policy_reason": reason,
        "executed": executed,
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
        expected_parent = record.get("parent_hash")
        if expected_parent != parent:
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

        calculated_sig = _sign(key, calculated_hash)
        if claimed_signature != calculated_sig:
            return False, f"signature mismatch at record {idx}"

        if record.get("policy_decision") == "deny" and record.get("executed") is not False:
            return False, f"deny record executed at record {idx}"

        parent = calculated_hash

    return True, f"verified {len(records)} records"


def _deny_output(reason: str) -> Dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def run_hook(stdin_text: str) -> int:
    if not stdin_text.strip():
        return 0

    try:
        event = json.loads(stdin_text)
    except json.JSONDecodeError as exc:
        print(f"Agent Black Box hook received malformed JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(event, dict):
        print("Agent Black Box hook input must be a JSON object", file=sys.stderr)
        return 1

    record = append_record(event)

    if record.get("hook_event_name") == "PreToolUse" and record.get("policy_decision") == "deny":
        print(json.dumps(_deny_output(str(record.get("policy_reason") or "blocked by Agent Black Box")), sort_keys=True))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    args = list(argv) if argv is not None else sys.argv[1:]

    if args and args[0] == "verify":
        parser = argparse.ArgumentParser(description="Verify Agent Black Box hook trace")
        parser.add_argument("trace")
        parser.add_argument("--key-file", required=True)
        ns = parser.parse_args(args[1:])
        ok, message = verify_trace(Path(ns.trace), Path(ns.key_file))
        print(("PASS: " if ok else "FAIL: ") + message)
        return 0 if ok else 1

    return run_hook(sys.stdin.read())


if __name__ == "__main__":
    raise SystemExit(main())
