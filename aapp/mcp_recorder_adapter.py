from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .crypto import attach_signature, verify_chain
from .mcp_boundary import MCPBoundaryError, load_policy, run_policy_demo, tool_registry
from .record import create_record
from .scope import ScopeError, load_scope, require_authorized_scope, scope_id
from .verifier import VerifierError, validate_trace_semantics


DEFAULT_DEV_KEY = b"aapp-local-dev-key-do-not-use-in-production"


class MCPRecorderAdapterError(Exception):
    """Raised when MCP-style tool calls cannot be recorded safely."""


def _write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def _write_dev_key(path: Path) -> None:
    path.write_bytes(DEFAULT_DEV_KEY + b"\n")


def _serialize_payload(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def record_mcp_style_tool_calls(
    *,
    policy_path: str | Path,
    scope_path: str | Path,
    out_dir: str | Path,
) -> Dict[str, Path]:
    policy_file = Path(policy_path)
    scope_file = Path(scope_path)
    out = Path(out_dir)

    try:
        policy = load_policy(policy_file)
        scope = load_scope(scope_file)
    except (MCPBoundaryError, ScopeError) as exc:
        raise MCPRecorderAdapterError(str(exc)) from exc

    out.mkdir(parents=True, exist_ok=True)

    try:
        results = run_policy_demo(policy_path=policy_file, output_dir=out)
    except MCPBoundaryError as exc:
        raise MCPRecorderAdapterError(str(exc)) from exc

    registry = tool_registry()
    records: List[Dict[str, Any]] = []
    parent_hash = None
    session_id = "mcp-recorder-demo-session-001"

    for index, item in enumerate(results, start=1):
        tool_id = item["tool_id"]
        tool_type = registry[tool_id]["tool_type"]

        try:
            require_authorized_scope(
                scope=scope,
                actor_type="agent",
                tool_type=tool_type,
            )
        except ScopeError as exc:
            raise MCPRecorderAdapterError(
                f"record outside authorized scope for tool {tool_id}: {exc}"
            ) from exc

        decision = item["decision"]
        reason = item["reason"]
        approval_ref = item.get("approval_ref")

        record = create_record(
            session_id=session_id,
            parent_hash=parent_hash,
            actor_id="aapp-mcp-recorder-agent",
            actor_type="agent",
            model_id="local-mcp-style-simulator",
            scope_id=scope_id(scope),
            authorization_status="authorized",
            policy_id=str(policy.get("policy_id", "policy-mcp-recorder-demo")),
            tool_id=tool_id,
            tool_type=tool_type,
            decision=decision,
            reason=reason,
            input_payload=_serialize_payload(
                {
                    "sequence": index,
                    "tool_id": tool_id,
                    "approval_ref": approval_ref,
                }
            ),
            output_payload=_serialize_payload(item["output"]),
            artifact_payload=None,
            approval_ref=approval_ref,
        )
        signed = attach_signature(record, DEFAULT_DEV_KEY)
        records.append(signed)
        parent_hash = signed["record_hash"]

    trace_path = out / "trace.jsonl"
    key_path = out / "dev.key"
    results_path = out / "mcp-results.json"
    verification_path = out / "verification_result.md"

    _write_jsonl(trace_path, records)
    _write_dev_key(key_path)
    results_path.write_text(
        json.dumps(results, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    try:
        validate_trace_semantics(trace_path, scope_file)
    except VerifierError as exc:
        raise MCPRecorderAdapterError(str(exc)) from exc

    ok, messages = verify_chain(records, DEFAULT_DEV_KEY)
    if not ok:
        raise MCPRecorderAdapterError("recorded MCP-style trace failed signature/hash verification")

    verification_lines = [
        "# AAPP MCP Recorder Verification Result",
        "",
        "Result: PASS",
        "",
    ]
    verification_lines.extend(f"- {message}" for message in messages)
    verification_lines.append("")
    verification_path.write_text("\n".join(verification_lines), encoding="utf-8")

    return {
        "trace": trace_path,
        "key": key_path,
        "results": results_path,
        "verification": verification_path,
    }
