import json
from pathlib import Path

from aapp.deterministic_firewall import (
    ALLOW,
    DENY,
    REQUIRE_APPROVAL,
    handle_tool_call,
    run_file,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str):
    return json.loads((FIXTURES / name).read_text())


def test_allow_forwards_and_records(tmp_path):
    policy = _load("firewall_policy.json")
    message = _load("firewall_allowed_tools_call.json")
    calls = []

    def fake_executor(call):
        calls.append(call)
        return {"ok": True, "tool_name": call["tool_name"]}

    result = handle_tool_call(message, policy, executor=fake_executor, trace_path=tmp_path / "trace.jsonl")

    assert result["decision"] == ALLOW
    assert result["executed"] is True
    assert calls and calls[0]["tool_name"] == "read_status"
    assert (tmp_path / "trace.jsonl").exists()
    assert result["trace"]["latency_ms"] >= 0


def test_deny_does_not_execute_but_records(tmp_path):
    policy = _load("firewall_policy.json")
    message = _load("firewall_blocked_tools_call.json")
    calls = []

    result = handle_tool_call(message, policy, executor=lambda call: calls.append(call), trace_path=tmp_path / "trace.jsonl")

    assert result["decision"] == DENY
    assert result["executed"] is False
    assert calls == []
    trace = (tmp_path / "trace.jsonl").read_text()
    assert "destructive_database_operation" in trace
    assert '"executed": false' in trace


def test_require_approval_does_not_execute(tmp_path):
    policy = _load("firewall_policy.json")
    message = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "refund_payment", "arguments": {"payment_id": "pay_123"}}
    }
    calls = []

    result = handle_tool_call(message, policy, executor=lambda call: calls.append(call), trace_path=tmp_path / "trace.jsonl")

    assert result["decision"] == REQUIRE_APPROVAL
    assert result["executed"] is False
    assert calls == []
    assert "payment_refund_requires_approval" in (tmp_path / "trace.jsonl").read_text()


def test_invalid_params_default_deny(tmp_path):
    policy = _load("firewall_policy.json")
    message = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "read_status", "arguments": "not-an-object"}
    }

    result = handle_tool_call(message, policy, executor=lambda call: (_ for _ in ()).throw(RuntimeError("should not run")), trace_path=tmp_path / "trace.jsonl")

    assert result["decision"] == DENY
    assert result["executed"] is False
    assert "invalid_params" in result["trace"]["reason_code"]


def test_unknown_tool_default_deny(tmp_path):
    policy = _load("firewall_policy.json")
    message = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {"name": "unknown_tool", "arguments": {}}
    }
    calls = []

    result = handle_tool_call(message, policy, executor=lambda call: calls.append(call), trace_path=tmp_path / "trace.jsonl")

    assert result["decision"] == DENY
    assert result["executed"] is False
    assert calls == []
    assert result["trace"]["reason_code"] == "default_decision"


def test_cli_run_file_outputs_trace_verdict_and_report(tmp_path):
    result = run_file(
        FIXTURES / "firewall_policy.json",
        FIXTURES / "firewall_allowed_tools_call.json",
        tmp_path / "firewall",
    )

    assert result["decision"] == ALLOW
    assert (tmp_path / "firewall" / "firewall.trace.jsonl").exists()
    assert (tmp_path / "firewall" / "firewall.verdict.json").exists()
    assert (tmp_path / "firewall" / "firewall.report.md").exists()
