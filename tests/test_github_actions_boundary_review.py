import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GitHubActionsBoundaryReviewTests(unittest.TestCase):
    def test_audit_tool_exists_and_runs(self):
        tool = ROOT / "tools" / "audit_github_actions_boundary.py"
        self.assertTrue(tool.is_file(), "audit tool missing")

        result = subprocess.run(
            [sys.executable, str(tool)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"audit tool failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

        required = [
            "GitHub Actions Boundary Audit",
            "permissions",
            "pull_request_target",
            "workflow_run",
            "artifact",
            "github.event",
        ]
        for item in required:
            self.assertIn(item, result.stdout)

    def test_boundary_review_doc_exists(self):
        path = ROOT / "docs" / "GITHUB_ACTIONS_BOUNDARY_REVIEW.md"
        self.assertTrue(path.is_file(), "boundary review doc missing")
        text = path.read_text(encoding="utf-8")

        required = [
            "workflow permissions",
            "trigger boundary",
            "third-party action pinning",
            "artifact boundary",
            "untrusted input boundary",
            "Kill condition",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_ci_workflow_has_permissions_block(self):
        path = ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.is_file(), "ci.yml missing")
        text = path.read_text(encoding="utf-8")
        self.assertIn("permissions:", text)
        self.assertIn("contents: read", text)


if __name__ == "__main__":
    unittest.main()
