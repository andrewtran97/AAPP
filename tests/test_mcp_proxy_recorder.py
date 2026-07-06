import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MCPProxyRecorderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-mcp-proxy-"))
        self.trace = self.tmp / "mcp.trace.jsonl"
        self.key = self.tmp / "dev.key"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cmd(self, args, input_text=None, timeout=20):
        return subprocess.run(
            args,
            cwd=ROOT,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )

    def test_record_tools_call_and_verify(self):
        result = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "record",
            "--request", "tests/fixtures/mcp_tools_call_request.json",
            "--response", "tests/fixtures/mcp_tools_call_response.json",
            "--out", str(self.tmp),
            "--session-id", "test-session",
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        verify = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "verify",
            str(self.trace), "--key-file", str(self.key),
        ])
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        self.assertIn("PASS", verify.stdout)

    def test_tamper_fails_verification(self):
        self.test_record_tools_call_and_verify()

        tampered = self.tmp / "tampered.trace.jsonl"
        tampered.write_text(
            self.trace.read_text(encoding="utf-8").replace('"policy_decision": "allow"', '"policy_decision": "deny"', 1),
            encoding="utf-8",
        )

        verify = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "verify",
            str(tampered), "--key-file", str(self.key),
        ])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)

    def test_secret_like_values_are_not_written_to_trace(self):
        self.test_record_tools_call_and_verify()

        text = self.trace.read_text(encoding="utf-8")
        self.assertNotIn("sk-test-secret-123456789", text)
        self.assertNotIn("api_key", text)

    def test_blocked_tools_call_records_denial_without_execution(self):
        result = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "record",
            "--request", "tests/fixtures/mcp_blocked_tools_call_request.json",
            "--out", str(self.tmp),
            "--session-id", "test-session",
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        record = json.loads(self.trace.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(record["policy_decision"], "deny")
        self.assertFalse(record["executed"])

        verify = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "verify",
            str(self.trace), "--key-file", str(self.key),
        ])
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_report_contains_mcp_boundary_summary(self):
        self.test_record_tools_call_and_verify()
        report = self.tmp / "report.md"

        result = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "report",
            str(self.trace), "--out", str(report),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        text = report.read_text(encoding="utf-8")
        self.assertIn("Agent Black Box MCP Proxy Report", text)
        self.assertIn("tools/call", text)
        self.assertIn("read_file", text)

    def test_stdio_proxy_records_pass_through_tools_call(self):
        request_obj = json.loads((ROOT / "tests" / "fixtures" / "mcp_tools_call_request.json").read_text(encoding="utf-8"))
        request = json.dumps(request_obj, sort_keys=True, separators=(",", ":"))

        result = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "stdio",
            "--server-command", "python3 tests/fixtures/mcp_echo_server.py",
            "--out", str(self.tmp),
            "--session-id", "stdio-session",
        ], input_text=request + "\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        response = json.loads(result.stdout.strip().splitlines()[0])
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("result", response)

        verify = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "verify",
            str(self.trace), "--key-file", str(self.key),
        ])
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_stdio_proxy_tolerates_pretty_json_local_fixture(self):
        request = (ROOT / "tests" / "fixtures" / "mcp_tools_call_request.json").read_text(encoding="utf-8")

        result = self.run_cmd([
            "python3", "-m", "aapp.mcp_proxy_recorder", "stdio",
            "--server-command", "python3 tests/fixtures/mcp_echo_server.py",
            "--out", str(self.tmp),
            "--session-id", "stdio-pretty-session",
        ], input_text=request + "\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        response = json.loads(result.stdout.strip().splitlines()[0])
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("result", response)


if __name__ == "__main__":
    unittest.main()
