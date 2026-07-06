import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args, cwd=ROOT):
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class PublicDemoExternalReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-public-demo-"))
        self.demo = self.tmp / "public-demo"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build_demo(self):
        return run_cmd([
            "bash",
            "scripts/build_public_demo.sh",
            str(self.demo),
        ])

    def test_public_demo_script_creates_expected_tree(self):
        result = self.build_demo()
        self.assertEqual(
            result.returncode,
            0,
            msg=f"public demo failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

        required = [
            "README.md",
            "recorded/trace.jsonl",
            "recorded/dev.key",
            "recorded/mcp-results.json",
            "recorded/verification_result.md",
            "replay_report.md",
            "AAPP-EVIDENCE-BUNDLE/scope.json",
            "AAPP-EVIDENCE-BUNDLE/trace.jsonl",
            "AAPP-EVIDENCE-BUNDLE/evidence.bundle.json",
            "AAPP-EVIDENCE-BUNDLE/evidence.report.md",
            "AAPP-EVIDENCE-BUNDLE/hashes.txt",
            "AAPP-EVIDENCE-BUNDLE/verification_result.md",
        ]

        for rel in required:
            self.assertTrue((self.demo / rel).is_file(), rel)

    def test_public_demo_readme_is_local_only(self):
        result = self.build_demo()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        text = (self.demo / "README.md").read_text(encoding="utf-8")
        required = [
            "This demo is local only.",
            "a live MCP server",
            "a network target",
            "an external service",
            "a credential store",
            "no production security certification",
            "no post-quantum security",
            "no Qubes certification",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_replay_report_contains_decision_evidence(self):
        result = self.build_demo()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        text = (self.demo / "replay_report.md").read_text(encoding="utf-8")
        required = [
            "blocked_api_call",
            "require_human_approval",
            "deny",
            "allow",
            "Record hash",
            "Parent hash",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_bundle_manifest_is_public_demo_safe(self):
        result = self.build_demo()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        manifest = json.loads(
            (self.demo / "AAPP-EVIDENCE-BUNDLE" / "evidence.bundle.json").read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["schema_version"], "0.4.0")
        self.assertEqual(manifest["bundle_type"], "AAPP-EVIDENCE-BUNDLE")
        self.assertEqual(manifest["verification_result"], "PASS")

        names = {item["path"] for item in manifest["files"]}
        for required in ["scope.json", "trace.jsonl", "evidence.report.md", "hashes.txt", "verification_result.md"]:
            self.assertIn(required, names)

    def test_external_review_artifacts_exist_and_restrict_claims(self):
        required_files = [
            ROOT / "docs" / "PUBLIC_DEMO_EXTERNAL_REVIEW.md",
            ROOT / "templates" / "EXTERNAL_REVIEW_REQUEST.md",
            ROOT / "checklists" / "PUBLIC_DEMO_RELEASE_CHECKLIST.md",
        ]
        for path in required_files:
            self.assertTrue(path.is_file(), str(path))

        text = (ROOT / "docs" / "PUBLIC_DEMO_EXTERNAL_REVIEW.md").read_text(encoding="utf-8")
        required = [
            "Send the review pack to 3 named reviewers.",
            "at least 1 written review requested",
            "live MCP integration",
            "production security certification",
            "post-quantum security",
            "Qubes-certified",
            "compliance guaranteed",
        ]
        for item in required:
            self.assertIn(item, text)


if __name__ == "__main__":
    unittest.main()
