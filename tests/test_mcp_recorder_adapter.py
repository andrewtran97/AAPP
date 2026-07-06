import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "examples" / "mcp-recorder-adapter" / "policy.demo.json"
SCOPE_FILE = ROOT / "examples" / "mcp-recorder-adapter" / "scope.demo.json"


def run_cmd(args, cwd=ROOT):
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class MCPRecorderAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-mcp-recorder-"))
        self.out = self.tmp / "mcp-recorded"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def record(self):
        return run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "mcp-record",
            "--policy",
            str(POLICY_FILE),
            "--scope",
            str(SCOPE_FILE),
            "--out",
            str(self.out),
        ])

    def test_mcp_record_command_creates_trace_outputs(self):
        result = self.record()
        self.assertEqual(
            result.returncode,
            0,
            msg=f"mcp-record failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

        for name in ["trace.jsonl", "dev.key", "mcp-results.json", "verification_result.md"]:
            self.assertTrue((self.out / name).is_file(), name)

    def test_recorded_trace_verifies_with_scope(self):
        result = self.record()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        verify = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "verify",
            str(self.out / "trace.jsonl"),
            "--key-file",
            str(self.out / "dev.key"),
            "--scope",
            str(SCOPE_FILE),
        ])
        self.assertEqual(
            verify.returncode,
            0,
            msg=f"verify failed\nSTDOUT:\n{verify.stdout}\nSTDERR:\n{verify.stderr}",
        )

    def test_denied_tool_is_recorded_as_denied_not_executed(self):
        result = self.record()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        records = [
            json.loads(line)
            for line in (self.out / "trace.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        denied = [r for r in records if r["tool"]["tool_id"] == "blocked_api_call"]
        self.assertEqual(len(denied), 1)
        self.assertEqual(denied[0]["policy"]["decision"], "deny")
        self.assertIn("network", denied[0]["tool"]["tool_type"])

        results = json.loads((self.out / "mcp-results.json").read_text(encoding="utf-8"))
        blocked = [r for r in results if r["tool_id"] == "blocked_api_call"]
        self.assertEqual(len(blocked), 1)
        self.assertFalse(blocked[0]["output"]["executed"])

    def test_write_file_requires_approval_then_records_approved_call(self):
        result = self.record()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        records = [
            json.loads(line)
            for line in (self.out / "trace.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        write_records = [r for r in records if r["tool"]["tool_id"] == "write_file"]
        decisions = {r["policy"]["decision"] for r in write_records}
        self.assertIn("require_human_approval", decisions)
        self.assertIn("allow", decisions)


if __name__ == "__main__":
    unittest.main()
