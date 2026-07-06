from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .crypto import verify_chain
from .verifier import VerifierError, validate_trace_semantics


DEFAULT_DEV_KEY = b"aapp-local-dev-key-do-not-use-in-production"


class ReplayError(Exception):
    """Raised when an AAPP trace cannot be replayed safely."""


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ReplayError("trace record must be an object")
                records.append(item)
    except json.JSONDecodeError as exc:
        raise ReplayError(f"malformed JSONL: {exc.msg}") from exc

    if not records:
        raise ReplayError("trace contains no records")
    return records


def _read_key(path: Path | None) -> bytes:
    if path is None:
        return DEFAULT_DEV_KEY
    return path.read_bytes().strip()


def replay_trace(
    *,
    trace_path: str | Path,
    key_file: str | Path | None = None,
    scope_path: str | Path | None = None,
) -> Dict[str, Any]:
    trace = Path(trace_path)
    key = _read_key(Path(key_file) if key_file else None)

    try:
        validate_trace_semantics(trace, scope_path)
    except VerifierError as exc:
        raise ReplayError(str(exc)) from exc

    records = _read_jsonl(trace)
    ok, messages = verify_chain(records, key)
    if not ok:
        raise ReplayError("trace signature/hash verification failed")

    timeline = []
    decision_counts: Dict[str, int] = {}

    for index, record in enumerate(records, start=1):
        decision = record["policy"]["decision"]
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

        timeline.append(
            {
                "index": index,
                "timestamp": record["timestamp"],
                "record_id": record["record_id"],
                "tool_id": record["tool"]["tool_id"],
                "tool_type": record["tool"]["tool_type"],
                "decision": decision,
                "reason": record["policy"]["reason"],
                "actor_id": record["actor"]["actor_id"],
                "scope_id": record["scope"]["scope_id"],
                "parent_hash": record["parent_hash"],
                "record_hash": record["record_hash"],
            }
        )

    return {
        "result": "PASS",
        "record_count": len(records),
        "decision_counts": decision_counts,
        "timeline": timeline,
        "verifier_messages": messages,
    }


def render_replay_report(replay: Dict[str, Any]) -> str:
    lines = [
        "# AAPP Replay Report",
        "",
        f"Result: {replay['result']}",
        f"Records: {replay['record_count']}",
        "",
        "## Decision counts",
        "",
    ]

    for decision, count in sorted(replay["decision_counts"].items()):
        lines.append(f"- {decision}: {count}")

    lines.extend(["", "## Timeline", ""])

    for item in replay["timeline"]:
        lines.extend(
            [
                f"### Record {item['index']}",
                "",
                f"- Timestamp: `{item['timestamp']}`",
                f"- Actor: `{item['actor_id']}`",
                f"- Tool: `{item['tool_id']}`",
                f"- Tool type: `{item['tool_type']}`",
                f"- Decision: `{item['decision']}`",
                f"- Reason: {item['reason']}",
                f"- Scope: `{item['scope_id']}`",
                f"- Parent hash: `{item['parent_hash']}`",
                f"- Record hash: `{item['record_hash']}`",
                "",
            ]
        )

    lines.extend(["## Verifier messages", ""])
    for message in replay["verifier_messages"]:
        lines.append(f"- {message}")

    lines.append("")
    return "\n".join(lines)


def write_replay_report(
    *,
    trace_path: str | Path,
    key_file: str | Path | None,
    scope_path: str | Path | None,
    out_path: str | Path,
) -> Path:
    replay = replay_trace(
        trace_path=trace_path,
        key_file=key_file,
        scope_path=scope_path,
    )
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_replay_report(replay), encoding="utf-8")
    return out
