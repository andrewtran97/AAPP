import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class E2EProductRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-e2e-product-"))
        self.bundle = self.tmp / "session-bundle" / "AGENT-BLACK-BOX-BUNDLE"
        self.key = self.tmp / "session-bundle" / "dev.key"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cmd(self, args, timeout=90):
        return subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )

    def test_e2e_script_has_no_hardcoded_default_tamper_path(self):
        script = (ROOT / "scripts" / "run_agent_black_box_e2e.sh").read_text(encoding="utf-8")
        self.assertIn('OUT="${1:-.aapp/evidence/agent-black-box-e2e}"', script)
        self.assertIn('AAPP_E2E_OUT="$OUT"', script)
        self.assertNotIn('Path(".aapp/evidence/agent-black-box-e2e/session-bundle', script)

    def test_e2e_product_run_builds_verified_bundle(self):
        result = self.run_cmd(["bash", "scripts/run_agent_black_box_e2e.sh", str(self.tmp)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Agent Black Box E2E product run: PASS", result.stdout)

        required = [
            self.tmp / "sources" / "hook" / "session.trace.jsonl",
            self.tmp / "sources" / "mcp" / "mcp.trace.jsonl",
            self.tmp / "sources" / "git-ci" / "gitci.trace.jsonl",
            self.bundle / "manifest.json",
            self.bundle / "hook.trace.jsonl",
            self.bundle / "mcp.trace.jsonl",
            self.bundle / "gitci.trace.jsonl",
            self.bundle / "hashes.txt",
            self.bundle / "session.report.md",
            self.tmp / "PRODUCT_RUN_SUMMARY.txt",
        ]
        for path in required:
            self.assertTrue(path.is_file(), str(path))

        verify = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "verify",
            str(self.bundle),
            "--key-file", str(self.key),
        ])
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_e2e_product_run_contains_denied_records(self):
        result = self.run_cmd(["bash", "scripts/run_agent_black_box_e2e.sh", str(self.tmp)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        hook_records = read_jsonl(self.tmp / "sources" / "hook" / "session.trace.jsonl")
        mcp_records = read_jsonl(self.tmp / "sources" / "mcp" / "mcp.trace.jsonl")

        self.assertTrue(any(record.get("policy_decision") == "deny" for record in hook_records))
        self.assertTrue(any(record.get("policy_decision") == "deny" for record in mcp_records))
        self.assertTrue(any(record.get("executed") is False for record in mcp_records if record.get("policy_decision") == "deny"))

    def test_e2e_product_run_tamper_fails_after_run(self):
        result = self.run_cmd(["bash", "scripts/run_agent_black_box_e2e.sh", str(self.tmp)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        manifest = self.bundle / "manifest.json"
        obj = json.loads(manifest.read_text(encoding="utf-8"))
        obj["session_id"] = "tampered-again"
        manifest.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        verify = self.run_cmd([
            "python3", "-m", "aapp.session_bundle", "verify",
            str(self.bundle),
            "--key-file", str(self.key),
        ])
        self.assertNotEqual(verify.returncode, 0)
        self.assertIn("FAIL", verify.stdout)


if __name__ == "__main__":
    unittest.main()
