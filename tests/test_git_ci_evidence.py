import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GitCIEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-git-ci-"))
        self.trace = self.tmp / "gitci.trace.jsonl"
        self.key = self.tmp / "dev.key"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cmd(self, args, env=None):
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        return subprocess.run(
            args,
            cwd=ROOT,
            env=full_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )

    def test_capture_and_verify(self):
        result = self.run_cmd([
            "python3", "-m", "aapp.git_ci_evidence", "capture",
            "--repo", ".",
            "--out", str(self.tmp),
            "--session-id", "test-session",
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.trace.is_file())
        self.assertTrue(self.key.is_file())

        verify = self.run_cmd([
            "python3", "-m", "aapp.git_ci_evidence", "verify",
            str(self.trace), "--key-file", str(self.key),
        ])
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        self.assertIn("PASS", verify.stdout)

    def test_trace_contains_git_evidence_not_raw_diff(self):
        self.test_capture_and_verify()
        record = json.loads(self.trace.read_text(encoding="utf-8").splitlines()[0])
        snapshot = record["snapshot"]

        self.assertEqual(record["adapter"], "git-ci")
        self.assertIn("head_sha", snapshot)
        self.assertIn("staged_diff_digest", snapshot)
        self.assertIn("unstaged_diff_digest", snapshot)
        self.assertNotIn("diff --git", self.trace.read_text(encoding="utf-8"))

    def test_github_actions_env_is_captured_without_token(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_RUN_ID": "123456",
            "GITHUB_RUN_NUMBER": "7",
            "GITHUB_SHA": "abc123",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_REPOSITORY": "andrewtran97/AAPP",
            "GITHUB_TOKEN": "ghp_secretsecretsecret",
        }

        result = self.run_cmd([
            "python3", "-m", "aapp.git_ci_evidence", "capture",
            "--repo", ".",
            "--out", str(self.tmp),
            "--session-id", "test-session",
        ], env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        text = self.trace.read_text(encoding="utf-8")
        self.assertIn("GITHUB_RUN_ID", text)
        self.assertNotIn("ghp_secretsecretsecret", text)
        self.assertNotIn("GITHUB_TOKEN", text)

    def test_report_contains_git_ci_summary(self):
        self.test_capture_and_verify()
        report = self.tmp / "report.md"

        result = self.run_cmd([
            "python3", "-m", "aapp.git_ci_evidence", "report",
            str(self.trace), "--out", str(report),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        text = report.read_text(encoding="utf-8")
        self.assertIn("Agent Black Box Git/CI Evidence Report", text)
        self.assertIn("Branch", text)
        self.assertIn("Commit", text)

    def test_tamper_fails_verification(self):
        self.test_capture_and_verify()

        tampered = self.tmp / "tampered.trace.jsonl"
        tampered.write_text(
            self.trace.read_text(encoding="utf-8").replace('"adapter":"git-ci"', '"adapter":"git-ci-tampered"', 1),
            encoding="utf-8",
        )

        verify = self.run_cmd([
            "python3", "-m", "aapp.git_ci_evidence", "verify",
            str(tampered), "--key-file", str(self.key),
        ])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)


if __name__ == "__main__":
    unittest.main()
