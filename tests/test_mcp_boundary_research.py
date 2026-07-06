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


class MCPBoundaryResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-a1-mcp-boundary-"))
        self.out = self.tmp / "a1"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a1_script_builds_required_output(self):
        result = run_cmd([
            "bash",
            "scripts/build_a1_mcp_boundary_research.sh",
            str(self.out),
        ])
        self.assertEqual(
            result.returncode,
            0,
            msg=f"A1 build failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

        required = [
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
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_a1_replay_contains_decision_evidence(self):
        result = run_cmd([
            "bash",
            "scripts/build_a1_mcp_boundary_research.sh",
            str(self.out),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        text = (self.out / "replay_report.md").read_text(encoding="utf-8")
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

    def test_a1_denied_tool_did_not_execute(self):
        result = run_cmd([
            "bash",
            "scripts/build_a1_mcp_boundary_research.sh",
            str(self.out),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        results = json.loads((self.out / "recorded" / "mcp-results.json").read_text(encoding="utf-8"))
        blocked = [item for item in results if item["tool_id"] == "blocked_api_call"]
        self.assertEqual(len(blocked), 1)
        self.assertFalse(blocked[0]["output"]["executed"])

    def test_a1_docs_define_local_only_boundary(self):
        doc = (ROOT / "docs" / "MCP_BOUNDARY_RESEARCH.md").read_text(encoding="utf-8")
        required = [
            "This is local-only research.",
            "no live MCP server integration",
            "no credential handling",
            "denied tool executes",
            "trace cannot verify",
        ]
        for item in required:
            self.assertIn(item, doc)


if __name__ == "__main__":
    unittest.main()
