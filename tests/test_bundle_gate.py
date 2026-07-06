import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE_FILE = ROOT / "examples" / "simple-tool-call" / "scope.demo.json"


def run_cmd(args, cwd=ROOT):
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class EvidenceBundleGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-bundle-gate-"))
        self.demo = self.tmp / "demo"
        self.bundle = self.tmp / "AAPP-EVIDENCE-BUNDLE"

        demo = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "demo",
            "--scope",
            str(SCOPE_FILE),
            "--out",
            str(self.demo),
        ])
        self.assertEqual(
            demo.returncode,
            0,
            msg=f"demo failed\nSTDOUT:\n{demo.stdout}\nSTDERR:\n{demo.stderr}",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def bundle_cmd(self, *extra):
        return run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "bundle",
            "--scope",
            str(SCOPE_FILE),
            "--trace",
            str(self.demo / "trace.jsonl"),
            "--key-file",
            str(self.demo / "dev.key"),
            "--report",
            str(self.demo / "evidence.report.md"),
            "--out",
            str(self.bundle),
            *extra,
        ])

    def test_bundle_command_creates_required_files(self):
        result = self.bundle_cmd()
        self.assertEqual(
            result.returncode,
            0,
            msg=f"bundle failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

        expected = {
            "scope.json",
            "trace.jsonl",
            "evidence.bundle.json",
            "evidence.report.md",
            "hashes.txt",
            "verification_result.md",
        }
        actual = {p.name for p in self.bundle.iterdir() if p.is_file()}
        self.assertTrue(expected.issubset(actual), actual)

    def test_bundle_manifest_references_hashes(self):
        result = self.bundle_cmd()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        manifest = json.loads((self.bundle / "evidence.bundle.json").read_text())
        self.assertEqual(manifest["schema_version"], "0.4.0")
        self.assertEqual(manifest["bundle_type"], "AAPP-EVIDENCE-BUNDLE")
        self.assertIn("files", manifest)

        names = {item["path"] for item in manifest["files"]}
        self.assertIn("scope.json", names)
        self.assertIn("trace.jsonl", names)
        self.assertIn("evidence.report.md", names)
        self.assertIn("verification_result.md", names)

        for item in manifest["files"]:
            self.assertTrue(item["sha384"].startswith("sha384:"))

    def test_bundle_rejects_invalid_trace(self):
        bad_trace = self.tmp / "bad-trace.jsonl"
        bad_trace.write_text("{not-json\n", encoding="utf-8")

        result = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "bundle",
            "--scope",
            str(SCOPE_FILE),
            "--trace",
            str(bad_trace),
            "--key-file",
            str(self.demo / "dev.key"),
            "--report",
            str(self.demo / "evidence.report.md"),
            "--out",
            str(self.bundle),
        ])
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bundle_report_must_not_contain_secret_like_value(self):
        result = self.bundle_cmd()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = (self.bundle / "evidence.report.md").read_text(encoding="utf-8")
        self.assertNotIn("sk-1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", report)
        self.assertNotIn("api_key=", report)


if __name__ == "__main__":
    unittest.main()
