from pathlib import Path
import tempfile
import unittest

from aapp.mcp_boundary import (
    MCPBoundaryError,
    decide_tool_call,
    load_policy,
    run_policy_demo,
    simulate_tool_call,
    tool_registry,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "examples" / "mcp-style-simulator" / "policy.demo.json"


class MCPStyleToolPermissionBoundaryTests(unittest.TestCase):
    def test_policy_loads_and_registry_contains_expected_tools(self):
        policy = load_policy(POLICY_FILE)
        self.assertEqual(policy["schema_version"], "0.7.0")

        registry = tool_registry()
        for tool_id in ["read_file", "write_file", "shell_echo", "blocked_api_call"]:
            self.assertIn(tool_id, registry)

    def test_allowed_tool_executes(self):
        policy = load_policy(POLICY_FILE)
        result = simulate_tool_call(
            policy=policy,
            tool_id="shell_echo",
            input_payload="hello",
        )
        self.assertEqual(result.decision, "allow")
        self.assertTrue(result.output["executed"])
        self.assertEqual(result.output["stdout"], "hello")

    def test_denied_tool_does_not_execute(self):
        policy = load_policy(POLICY_FILE)
        result = simulate_tool_call(
            policy=policy,
            tool_id="blocked_api_call",
            input_payload="https://example.invalid",
        )
        self.assertEqual(result.decision, "deny")
        self.assertFalse(result.output["executed"])

    def test_approval_required_tool_blocks_without_approval(self):
        policy = load_policy(POLICY_FILE)
        result = simulate_tool_call(
            policy=policy,
            tool_id="write_file",
            input_payload="payload",
        )
        self.assertEqual(result.decision, "require_human_approval")
        self.assertFalse(result.output["executed"])

    def test_approval_required_tool_executes_with_approval(self):
        policy = load_policy(POLICY_FILE)
        with tempfile.TemporaryDirectory() as tmp:
            result = simulate_tool_call(
                policy=policy,
                tool_id="write_file",
                input_payload="payload",
                approval_ref="approval-001",
                output_dir=tmp,
            )
            self.assertEqual(result.decision, "allow")
            self.assertTrue(result.output["executed"])
            self.assertTrue((Path(tmp) / "simulated-write.txt").is_file())

    def test_unknown_tool_rejected(self):
        policy = load_policy(POLICY_FILE)
        with self.assertRaises(MCPBoundaryError):
            decide_tool_call(policy=policy, tool_id="unknown_tool")

    def test_policy_demo_has_required_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = run_policy_demo(policy_path=POLICY_FILE, output_dir=tmp)

        decisions = {(item["tool_id"], item["decision"]) for item in results}
        self.assertIn(("read_file", "allow"), decisions)
        self.assertIn(("shell_echo", "allow"), decisions)
        self.assertIn(("write_file", "require_human_approval"), decisions)
        self.assertIn(("write_file", "allow"), decisions)
        self.assertIn(("blocked_api_call", "deny"), decisions)


if __name__ == "__main__":
    unittest.main()
