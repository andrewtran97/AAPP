from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


SUPPORTED_POLICY_SCHEMA_VERSION = "0.7.0"


class MCPBoundaryError(Exception):
    """Raised when a local MCP-style tool boundary blocks or rejects a call."""


@dataclass(frozen=True)
class ToolCallResult:
    tool_id: str
    decision: str
    reason: str
    output: Dict[str, Any]


def load_policy(path: str | Path) -> Dict[str, Any]:
    policy_path = Path(path)
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MCPBoundaryError(f"malformed policy JSON: {exc.msg}") from exc

    if not isinstance(policy, dict):
        raise MCPBoundaryError("policy must be an object")

    if policy.get("schema_version") != SUPPORTED_POLICY_SCHEMA_VERSION:
        raise MCPBoundaryError("unsupported policy schema_version")

    allowed_tools = policy.get("allowed_tools")
    if not isinstance(allowed_tools, list):
        raise MCPBoundaryError("allowed_tools must be a list")

    for item in allowed_tools:
        if not isinstance(item, str) or not item:
            raise MCPBoundaryError("allowed_tools entries must be non-empty strings")

    denied_tools = policy.get("denied_tools", [])
    if not isinstance(denied_tools, list):
        raise MCPBoundaryError("denied_tools must be a list")

    approval_required_tools = policy.get("approval_required_tools", [])
    if not isinstance(approval_required_tools, list):
        raise MCPBoundaryError("approval_required_tools must be a list")

    return policy


def tool_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "read_file": {
            "tool_type": "file_read",
            "network": False,
            "side_effect": False,
            "description": "Read a local fixture file from an allowed examples directory.",
        },
        "write_file": {
            "tool_type": "file_write",
            "network": False,
            "side_effect": True,
            "description": "Simulated local write. Does not write outside the simulator output directory.",
        },
        "shell_echo": {
            "tool_type": "shell",
            "network": False,
            "side_effect": False,
            "description": "Return a string as simulated shell output without invoking a shell.",
        },
        "blocked_api_call": {
            "tool_type": "network",
            "network": True,
            "side_effect": True,
            "description": "Blocked network-like call used for negative testing.",
        },
    }


def decide_tool_call(
    *,
    policy: Dict[str, Any],
    tool_id: str,
    approval_ref: str | None = None,
) -> ToolCallResult:
    registry = tool_registry()

    if tool_id not in registry:
        raise MCPBoundaryError(f"unknown tool: {tool_id}")

    if tool_id in policy.get("denied_tools", []):
        return ToolCallResult(
            tool_id=tool_id,
            decision="deny",
            reason=f"tool explicitly denied: {tool_id}",
            output={"executed": False},
        )

    if tool_id not in policy.get("allowed_tools", []):
        return ToolCallResult(
            tool_id=tool_id,
            decision="deny",
            reason=f"tool not allowed by policy: {tool_id}",
            output={"executed": False},
        )

    if tool_id in policy.get("approval_required_tools", []) and not approval_ref:
        return ToolCallResult(
            tool_id=tool_id,
            decision="require_human_approval",
            reason=f"tool requires approval: {tool_id}",
            output={"executed": False},
        )

    meta = registry[tool_id]
    if meta["network"] is True:
        return ToolCallResult(
            tool_id=tool_id,
            decision="deny",
            reason="network tools are blocked in local simulator",
            output={"executed": False},
        )

    return ToolCallResult(
        tool_id=tool_id,
        decision="allow",
        reason=f"tool allowed by local policy: {tool_id}",
        output={"executed": True, "tool_type": meta["tool_type"]},
    )


def simulate_tool_call(
    *,
    policy: Dict[str, Any],
    tool_id: str,
    input_payload: str,
    approval_ref: str | None = None,
    output_dir: str | Path | None = None,
) -> ToolCallResult:
    decision = decide_tool_call(
        policy=policy,
        tool_id=tool_id,
        approval_ref=approval_ref,
    )

    if decision.decision != "allow":
        return decision

    if tool_id == "read_file":
        return ToolCallResult(
            tool_id=tool_id,
            decision="allow",
            reason=decision.reason,
            output={"executed": True, "content": f"local fixture read: {input_payload}"},
        )

    if tool_id == "write_file":
        out_dir = Path(output_dir or ".")
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / "simulated-write.txt"
        target.write_text(input_payload, encoding="utf-8")
        return ToolCallResult(
            tool_id=tool_id,
            decision="allow",
            reason=decision.reason,
            output={"executed": True, "path": str(target)},
        )

    if tool_id == "shell_echo":
        return ToolCallResult(
            tool_id=tool_id,
            decision="allow",
            reason=decision.reason,
            output={"executed": True, "stdout": input_payload},
        )

    return decision


def run_policy_demo(
    *,
    policy_path: str | Path,
    output_dir: str | Path,
) -> List[Dict[str, Any]]:
    policy = load_policy(policy_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    calls = [
        ("read_file", "README.md", None),
        ("shell_echo", "hello from local simulator", None),
        ("write_file", "simulated write payload", None),
        ("write_file", "approved simulated write payload", "approval-001"),
        ("blocked_api_call", "https://example.invalid", None),
    ]

    results: List[Dict[str, Any]] = []
    for tool_id, payload, approval_ref in calls:
        result = simulate_tool_call(
            policy=policy,
            tool_id=tool_id,
            input_payload=payload,
            approval_ref=approval_ref,
            output_dir=out_dir,
        )
        results.append(
            {
                "tool_id": result.tool_id,
                "decision": result.decision,
                "reason": result.reason,
                "output": result.output,
                "approval_ref": approval_ref,
            }
        )

    return results
