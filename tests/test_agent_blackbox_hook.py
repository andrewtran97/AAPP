import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_hook(fixture: str, out_dir: Path):
    env = os.environ.copy()
    env["AAPP_BLACKBOX_OUT"] = str(out_dir)
    payload = (ROOT / "tests" / "fixtures" / fixture).read_text(encoding="utf-8")
    return subprocess.run(
        ["python3", "-m", "aapp.agent_blackbox_hook"],
        cwd=ROOT,
        env=env,
        input=payload,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class AgentBlackBoxHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-hook-test-"))
        self.trace = self.tmp / "session.trace.jsonl"
        self.key = self.tmp / "dev.key"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read_records(self):
        return [
            json.loads(line)
            for line in self.trace.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_pretool_allowed_bash_records_event_silently(self):
        result = run_hook("agent_hook_pretool_bash.json", self.tmp)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")
        self.assertTrue(self.trace.is_file())

        records = self.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["hook_event_name"], "PreToolUse")
        self.assertEqual(records[0]["tool_name"], "Bash")
        self.assertEqual(records[0]["policy_decision"], "allow")
        self.assertFalse(records[0]["executed"])

    def test_pretool_blocked_bash_returns_deny_json_and_records_denial(self):
        result = run_hook("agent_hook_pretool_blocked_bash.json", self.tmp)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

        records = self.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["policy_decision"], "deny")
        self.assertFalse(records[0]["executed"])

    def test_posttool_records_executed_true(self):
        result = run_hook("agent_hook_posttool_write.json", self.tmp)

        self.assertEqual(result.returncode, 0, result.stderr)

        records = self.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["hook_event_name"], "PostToolUse")
        self.assertEqual(records[0]["tool_name"], "Write")
        self.assertTrue(records[0]["executed"])

    def test_trace_does_not_store_raw_secret_like_values(self):
        run_hook("agent_hook_pretool_bash.json", self.tmp)
        run_hook("agent_hook_pretool_blocked_bash.json", self.tmp)
        run_hook("agent_hook_posttool_write.json", self.tmp)

        text = self.trace.read_text(encoding="utf-8")
        forbidden = [
            "sk-test-secret",
            "ghp_secretsecretsecret",
            "github_pat_secretsecretsecret",
        ]
        for item in forbidden:
            self.assertNotIn(item, text)

    def test_verify_passes_then_fails_after_tamper(self):
        run_hook("agent_hook_pretool_bash.json", self.tmp)
        run_hook("agent_hook_pretool_blocked_bash.json", self.tmp)
        run_hook("agent_hook_posttool_write.json", self.tmp)

        ok = subprocess.run(
            ["python3", "-m", "aapp.agent_blackbox_hook", "verify", str(self.trace), "--key-file", str(self.key)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

        tampered = self.tmp / "tampered.trace.jsonl"
        tampered.write_text(
            self.trace.read_text(encoding="utf-8").replace('"tool_name": "Bash"', '"tool_name": "B0sh"', 1),
            encoding="utf-8",
        )

        bad = subprocess.run(
            ["python3", "-m", "aapp.agent_blackbox_hook", "verify", str(tampered), "--key-file", str(self.key)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("FAIL", bad.stdout)


if __name__ == "__main__":
    unittest.main()
