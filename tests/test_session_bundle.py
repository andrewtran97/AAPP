import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from aapp.agent_blackbox_hook import append_record as append_hook_record
from aapp.git_ci_evidence import append_record as append_git_ci_record
from aapp.git_ci_evidence import collect_git_ci_snapshot
from aapp.mcp_proxy_recorder import append_record as append_mcp_record


ROOT = Path(__file__).resolve().parents[1]


def tamper_jsonl_field(path, field, value):
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise AssertionError(f"no JSONL records in {path}")
    record = json.loads(lines[0])
    if field not in record:
        raise AssertionError(f"missing field {field} in {path}")
    record[field] = value
    lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class SessionBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-session-bundle-"))
        self.hook_dir = self.tmp / "hook"
        self.mcp_dir = self.tmp / "mcp"
        self.git_dir = self.tmp / "git"
        self.out = self.tmp / "bundle-out"
        self.bundle = self.out / "AGENT-BLACK-BOX-BUNDLE"
        self.key = self.out / "dev.key"
        self._make_source_traces()

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

    def _make_source_traces(self):
        append_hook_record(
            {
                "session_id": "bundle-test",
                "cwd": str(ROOT),
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "echo hello", "api_key": "sk-test-secret-123456789"},
            },
            self.hook_dir,
        )

        append_mcp_record(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "read_file",
                    "arguments": {"path": "README.md", "token": "ghp_secretsecretsecret"},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"content": [{"type": "text", "text": "ok"}], "isError": False},
            },
            self.mcp_dir,
            "bundle-test",
        )

        snapshot = collect_git_ci_snapshot(ROOT)
        append_git_ci_record(snapshot, self.git_dir, "bundle-test")

    def create_bundle(self):
        result = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "create",
            "--hook-trace", str(self.hook_dir / "session.trace.jsonl"),
            "--mcp-trace", str(self.mcp_dir / "mcp.trace.jsonl"),
            "--git-ci-trace", str(self.git_dir / "gitci.trace.jsonl"),
            "--out", str(self.out),
            "--session-id", "bundle-test",
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_create_bundle_and_verify(self):
        self.create_bundle()

        required = [
            "manifest.json",
            "hook.trace.jsonl",
            "mcp.trace.jsonl",
            "gitci.trace.jsonl",
            "hashes.txt",
            "verification_result.md",
            "session.report.md",
        ]
        for rel in required:
            self.assertTrue((self.bundle / rel).is_file(), rel)

        verify = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "verify",
            str(self.bundle),
            "--key-file", str(self.key),
        ])
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        self.assertIn("PASS", verify.stdout)

    def test_report_contains_unified_session_summary(self):
        self.create_bundle()

        report = self.bundle / "session.report.md"
        text = report.read_text(encoding="utf-8")

        self.assertIn("Agent Black Box Unified Session Report", text)
        self.assertIn("Hook trace", text)
        self.assertIn("MCP trace", text)
        self.assertIn("Git/CI trace", text)

    def test_report_does_not_inline_secret_like_values(self):
        self.create_bundle()
        text = (self.bundle / "session.report.md").read_text(encoding="utf-8")

        self.assertNotIn("sk-test-secret", text)
        self.assertNotIn("ghp_secretsecretsecret", text)

    def test_tampering_hook_trace_fails(self):
        self.create_bundle()
        p = self.bundle / "hook.trace.jsonl"
        tamper_jsonl_field(p, "tool_name", "B0sh")

        verify = self.run_cmd(["python3", "-m", "aapp.session_bundle", "verify", str(self.bundle), "--key-file", str(self.key)])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)

    def test_tampering_mcp_trace_fails(self):
        self.create_bundle()
        p = self.bundle / "mcp.trace.jsonl"
        tamper_jsonl_field(p, "tool_name", "read_file_tampered")

        verify = self.run_cmd(["python3", "-m", "aapp.session_bundle", "verify", str(self.bundle), "--key-file", str(self.key)])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)

    def test_tampering_gitci_trace_fails(self):
        self.create_bundle()
        p = self.bundle / "gitci.trace.jsonl"
        tamper_jsonl_field(p, "adapter", "git-ci-tampered")

        verify = self.run_cmd(["python3", "-m", "aapp.session_bundle", "verify", str(self.bundle), "--key-file", str(self.key)])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)

    def test_tampering_manifest_fails(self):
        self.create_bundle()
        p = self.bundle / "manifest.json"
        manifest = json.loads(p.read_text(encoding="utf-8"))
        manifest["session_id"] = "tampered"
        p.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        verify = self.run_cmd(["python3", "-m", "aapp.session_bundle", "verify", str(self.bundle), "--key-file", str(self.key)])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)

    def test_missing_source_trace_fails(self):
        missing = self.tmp / "missing.trace.jsonl"
        result = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "create",
            "--hook-trace", str(missing),
            "--mcp-trace", str(self.mcp_dir / "mcp.trace.jsonl"),
            "--git-ci-trace", str(self.git_dir / "gitci.trace.jsonl"),
            "--out", str(self.out),
            "--session-id", "bundle-test",
        ])
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
