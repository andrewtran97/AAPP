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


class ReplayReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-replay-"))
        self.recorded = self.tmp / "recorded"
        self.report = self.tmp / "replay_report.md"

        result = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "mcp-record",
            "--policy",
            str(POLICY_FILE),
            "--scope",
            str(SCOPE_FILE),
            "--out",
            str(self.recorded),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_replay_command_writes_report(self):
        result = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "replay",
            "--trace",
            str(self.recorded / "trace.jsonl"),
            "--key-file",
            str(self.recorded / "dev.key"),
            "--scope",
            str(SCOPE_FILE),
            "--out",
            str(self.report),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.report.is_file())

        text = self.report.read_text(encoding="utf-8")
        self.assertIn("# AAPP Replay Report", text)
        self.assertIn("blocked_api_call", text)
        self.assertIn("require_human_approval", text)
        self.assertIn("deny", text)
        self.assertIn("allow", text)

    def test_replay_rejects_malformed_trace(self):
        bad = self.tmp / "bad.jsonl"
        bad.write_text("{not-json\n", encoding="utf-8")

        result = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "replay",
            "--trace",
            str(bad),
            "--key-file",
            str(self.recorded / "dev.key"),
            "--scope",
            str(SCOPE_FILE),
            "--out",
            str(self.report),
        ])
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
