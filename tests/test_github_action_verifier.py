import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from aapp.agent_blackbox_hook import append_record as append_hook_record
from aapp.git_ci_evidence import append_record as append_git_ci_record
from aapp.git_ci_evidence import collect_git_ci_snapshot
from aapp.mcp_proxy_recorder import append_record as append_mcp_record
from aapp.session_bundle import create_bundle


ROOT = Path(__file__).resolve().parents[1]


class GitHubActionVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-action-verifier-"))
        self.hook_dir = self.tmp / "hook"
        self.mcp_dir = self.tmp / "mcp"
        self.git_dir = self.tmp / "git"
        self.bundle_out = self.tmp / "bundle-out"
        self.bundle_dir = self.bundle_out / "AGENT-BLACK-BOX-BUNDLE"
        self.key_file = self.bundle_out / "dev.key"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cmd(self, args):
        return subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )

    def make_bundle(self):
        append_hook_record(
            {
                "session_id": "action-test",
                "cwd": str(ROOT),
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "echo hello"},
            },
            self.hook_dir,
        )

        append_mcp_record(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "read_file", "arguments": {"path": "README.md"}},
            },
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"content": [{"type": "text", "text": "ok"}], "isError": False},
            },
            self.mcp_dir,
            "action-test",
        )

        append_git_ci_record(collect_git_ci_snapshot(ROOT), self.git_dir, "action-test")

        create_bundle(
            self.hook_dir / "session.trace.jsonl",
            self.mcp_dir / "mcp.trace.jsonl",
            self.git_dir / "gitci.trace.jsonl",
            self.bundle_out,
            "action-test",
        )

    def test_action_metadata_is_composite(self):
        action = ROOT / ".github" / "actions" / "agent-black-box-verify" / "action.yml"
        text = action.read_text(encoding="utf-8")

        self.assertIn("using: composite", text)
        self.assertIn("bundle_dir:", text)
        self.assertIn("key_file:", text)
        self.assertIn("report_out:", text)
        self.assertIn("python3 -m aapp.session_bundle verify", text)
        self.assertIn("python3 -m aapp.session_bundle report", text)

    def test_verify_command_passes_on_valid_bundle(self):
        self.make_bundle()

        result = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "verify",
            str(self.bundle_dir),
            "--key-file", str(self.key_file),
        ])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_report_command_writes_report(self):
        self.make_bundle()
        report = self.tmp / "action-report.md"

        result = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "report",
            str(self.bundle_dir),
            "--out", str(report),
        ])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Agent Black Box Unified Session Report", report.read_text(encoding="utf-8"))

    def test_tampered_bundle_fails(self):
        self.make_bundle()

        manifest = self.bundle_dir / "manifest.json"
        obj = json.loads(manifest.read_text(encoding="utf-8"))
        obj["session_id"] = "tampered"
        manifest.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        result = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "verify",
            str(self.bundle_dir),
            "--key-file", str(self.key_file),
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stdout)


    def test_public_action_has_no_builder_attribution(self):
        action = ROOT / ".github" / "actions" / "agent-black-box-verify" / "action.yml"
        text = action.read_text(encoding="utf-8").lower()

        forbidden = [
            "generated" + " with",
            "co-" + "authored-by:",
            "an" + "thropic",
            "cla" + "ude",
        ]

        for token in forbidden:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
