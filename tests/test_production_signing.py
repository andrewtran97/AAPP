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


class ProductionSigningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-prod-sign-"))
        self.hook_dir = self.tmp / "hook"
        self.mcp_dir = self.tmp / "mcp"
        self.git_dir = self.tmp / "git"
        self.bundle_out = self.tmp / "bundle-out"
        self.bundle_dir = self.bundle_out / "AGENT-BLACK-BOX-BUNDLE"
        self.key_dir = self.tmp / "keys"
        self.private_key = self.key_dir / "ed25519_private.pem"
        self.public_key = self.key_dir / "ed25519_public.pem"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cmd(self, args):
        return subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=40,
        )

    def make_bundle(self):
        append_hook_record(
            {
                "session_id": "prod-sign-test",
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
            "prod-sign-test",
        )

        append_git_ci_record(collect_git_ci_snapshot(ROOT), self.git_dir, "prod-sign-test")

        create_bundle(
            self.hook_dir / "session.trace.jsonl",
            self.mcp_dir / "mcp.trace.jsonl",
            self.git_dir / "gitci.trace.jsonl",
            self.bundle_out,
            "prod-sign-test",
        )

    def generate_keys(self):
        result = self.run_cmd([
            "python3", "-m", "aapp.production_signing", "gen-ed25519",
            "--out", str(self.key_dir),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.private_key.is_file())
        self.assertTrue(self.public_key.is_file())

    def sign_bundle(self):
        result = self.run_cmd([
            "python3", "-m", "aapp.production_signing", "sign-bundle",
            "--bundle-dir", str(self.bundle_dir),
            "--private-key", str(self.private_key),
            "--public-key", str(self.public_key),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.bundle_dir / "manifest.ed25519.sig").is_file())
        self.assertTrue((self.bundle_dir / "signature.profile.json").is_file())
        self.assertTrue((self.bundle_dir / "ed25519_public.pem").is_file())
        self.assertFalse((self.bundle_dir / "ed25519_private.pem").exists())

    def test_generate_sign_verify_bundle(self):
        self.make_bundle()
        self.generate_keys()
        self.sign_bundle()

        result = self.run_cmd([
            "python3", "-m", "aapp.production_signing", "verify-bundle",
            "--bundle-dir", str(self.bundle_dir),
        ])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_tampered_manifest_fails_detached_signature_verify(self):
        self.make_bundle()
        self.generate_keys()
        self.sign_bundle()

        manifest = self.bundle_dir / "manifest.json"
        obj = json.loads(manifest.read_text(encoding="utf-8"))
        obj["session_id"] = "tampered"
        manifest.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        result = self.run_cmd([
            "python3", "-m", "aapp.production_signing", "verify-bundle",
            "--bundle-dir", str(self.bundle_dir),
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stdout)

    def test_wrong_public_key_fails_verify(self):
        self.make_bundle()
        self.generate_keys()
        self.sign_bundle()

        other = self.tmp / "other-keys"
        result = self.run_cmd([
            "python3", "-m", "aapp.production_signing", "gen-ed25519",
            "--out", str(other),
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        result = self.run_cmd([
            "python3", "-m", "aapp.production_signing", "verify-bundle",
            "--bundle-dir", str(self.bundle_dir),
            "--public-key", str(other / "ed25519_public.pem"),
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stdout)

    def test_profile_has_conservative_claims_only(self):
        self.make_bundle()
        self.generate_keys()
        self.sign_bundle()

        profile = json.loads((self.bundle_dir / "signature.profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["signature_profile"], "openssl-ed25519-detached")
        self.assertEqual(profile["signed_file"], "manifest.json")
        self.assertEqual(profile["signature_file"], "manifest.ed25519.sig")
        self.assertEqual(profile["public_key_file"], "ed25519_public.pem")
        self.assertNotIn("private", json.dumps(profile).lower())

    def test_public_source_has_no_builder_attribution(self):
        text = (ROOT / "aapp" / "production_signing.py").read_text(encoding="utf-8").lower()
        for token in ["generated" + " with", "co-" + "authored-by:", "an" + "thropic", "cla" + "ude"]:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
