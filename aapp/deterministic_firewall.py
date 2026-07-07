from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = "aapp.deterministic_firewall.v1"

ALLOW = "ALLOW"
DENY = "DENY"
REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISIONS = {ALLOW, DENY, REQUIRE_APPROVAL}


def _now_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def _read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: str | Path, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def normalize_tool_call(message: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(message, dict):
        raise ValueError("message_not_object")
    if message.get("method") != "tools/call":
        raise ValueError("not_tools_call")

    params = message.get("params")
    if not isinstance(params, dict):
        raise ValueError("params_not_object")

    name = params.get("name")
    arguments = params.get("arguments", {})
    if not isinstance(name, str) or not name.strip():
        raise ValueError("tool_name_invalid")
    if not isinstance(arguments, dict):
        raise ValueError("arguments_not_object")

    return {
        "request_id": message.get("id"),
        "tool_name": name.strip(),
        "arguments": arguments,
        "jsonrpc": message.get("jsonrpc", "2.0"),
    }


def _match_rule(rule: dict[str, Any], call: dict[str, Any]) -> bool:
    match = rule.get("match", {})
    if not isinstance(match, dict):
        return False

    tool_name = call["tool_name"]
    arguments = call["arguments"]

    if "tool_name" in match and tool_name != match["tool_name"]:
        return False
    if "tool_name_prefix" in match and not tool_name.startswith(str(match["tool_name_prefix"])):
        return False
    if "tool_name_contains" in match and str(match["tool_name_contains"]) not in tool_name:
        return False

    required_args = match.get("required_args", [])
    if required_args:
        if not isinstance(required_args, list):
            return False
        for key in required_args:
            if key not in arguments:
                return False

    arg_equals = match.get("arg_equals", {})
    if arg_equals:
        if not isinstance(arg_equals, dict):
            return False
        for key, expected in arg_equals.items():
            if arguments.get(key) != expected:
                return False

    return True


def evaluate_policy(call: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, dict):
        return {"decision": DENY, "reason_code": "policy_not_object", "rule_id": None}
    if policy.get("schema_version") != "aapp.firewall_policy.v1":
        return {"decision": DENY, "reason_code": "unsupported_policy_schema", "rule_id": None}

    rules = policy.get("rules", [])
    if not isinstance(rules, list):
        return {"decision": DENY, "reason_code": "rules_not_list", "rule_id": None}

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        if not _match_rule(rule, call):
            continue

        decision = rule.get("decision", DENY)
        if decision not in DECISIONS:
            decision = DENY
        return {
            "decision": decision,
            "reason_code": str(rule.get("reason", "matched_rule")),
            "rule_id": rule.get("id"),
        }

    default_decision = policy.get("default_decision", DENY)
    if default_decision not in DECISIONS:
        default_decision = DENY
    return {
        "decision": default_decision,
        "reason_code": "default_decision",
        "rule_id": None,
    }


def mcp_error(request_id: Any, message: str, code: int = -32602) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def mcp_result(request_id: Any, content_text: str, is_error: bool = False) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": content_text}],
            "isError": is_error,
        },
    }


def handle_tool_call(
    message: dict[str, Any],
    policy: dict[str, Any],
    executor: Callable[[dict[str, Any]], Any] | None = None,
    trace_path: str | Path | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    request_id = message.get("id") if isinstance(message, dict) else None
    normalized: dict[str, Any] | None = None
    execution_result: Any = None
    executed = False

    try:
        normalized = normalize_tool_call(message)
        verdict = evaluate_policy(normalized, policy)
    except Exception as exc:
        verdict = {"decision": DENY, "reason_code": f"invalid_params:{type(exc).__name__}", "rule_id": None}

    decision = verdict["decision"]

    if decision == ALLOW:
        if executor is None:
            execution_result = {"ok": True, "note": "no_executor_supplied"}
        else:
            execution_result = executor(normalized or {})
        executed = True
        response = mcp_result(request_id, json.dumps({"decision": ALLOW, "result": execution_result}, sort_keys=True))
    elif decision == REQUIRE_APPROVAL:
        response = mcp_result(
            request_id,
            json.dumps({"decision": REQUIRE_APPROVAL, "reason_code": verdict["reason_code"]}, sort_keys=True),
            is_error=True,
        )
    else:
        response = mcp_error(request_id, f"DENY: {verdict['reason_code']}")

    trace = {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "tool_name": normalized.get("tool_name") if normalized else None,
        "decision": decision,
        "reason_code": verdict["reason_code"],
        "rule_id": verdict.get("rule_id"),
        "executed": executed,
        "latency_ms": _now_ms(start),
    }

    if trace_path is not None:
        _append_jsonl(trace_path, trace)

    return {
        "schema_version": SCHEMA_VERSION,
        "decision": decision,
        "executed": executed,
        "trace": trace,
        "response": response,
        "execution_result": execution_result,
    }


def run_file(policy_path: str | Path, request_path: str | Path, out: str | Path) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    policy = _read_json(policy_path)
    message = _read_json(request_path)
    trace_path = out / "firewall.trace.jsonl"

    def fake_executor(call: dict[str, Any]) -> dict[str, Any]:
        return {"fake_executor_called": True, "tool_name": call.get("tool_name")}

    result = handle_tool_call(message, policy, executor=fake_executor, trace_path=trace_path)
    _write_json(out / "firewall.verdict.json", result)

    report = [
        "# Deterministic MCP Firewall",
        "",
        f"- Decision: `{result['decision']}`",
        f"- Executed: `{result['executed']}`",
        f"- Reason: `{result['trace']['reason_code']}`",
        f"- Latency ms: `{result['trace']['latency_ms']}`",
        "",
    ]
    (out / "firewall.report.md").write_text("\n".join(report), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic MCP firewall for tools/call messages.")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--out", default=".aapp/firewall")
    args = parser.parse_args(argv)

    result = run_file(args.policy, args.request, args.out)
    print(
        "AAPP firewall complete: "
        f"decision={result['decision']} "
        f"executed={result['executed']} "
        f"out={Path(args.out).resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
