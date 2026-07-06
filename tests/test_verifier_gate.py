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


class VerifierGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aapp-verifier-gate-"))
        self.out = self.tmp / "demo"
        demo = run_cmd([
            sys.executable,
            "-m",
            "aapp.cli",
            "demo",
            "--scope",
            str(SCOPE_FILE),
            "--out",
            str(self.out),
        ])
        self.assertEqual(
            demo.returncode,
            0,
            msg=f"demo failed\nSTDOUT:\n{demo.stdout}\nSTDERR:\n{demo.stderr}",
        )
        self.trace = self.out / "trace.jsonl"
        self.key_file = self.out / "dev.key"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def verify(self, trace=None, scope=None):
        cmd = [
            sys.executable,
            "-m",
            "aapp.cli",
            "verify",
            str(trace or self.trace),
            "--key-file",
            str(self.key_file),
        ]
        if scope is not None:
            cmd.extend(["--scope", str(scope)])
        return run_cmd(cmd)

    def read_records(self):
        return [
            json.loads(line)
            for line in self.trace.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def write_records(self, records, path=None):
        target = path or self.trace
        target.write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
            encoding="utf-8",
        )
        return target

    def test_malformed_jsonl_rejected(self):
        bad = self.tmp / "malformed.jsonl"
        bad.write_text(
            self.trace.read_text(encoding="utf-8") + "\n{not-json\n",
            encoding="utf-8",
        )
        result = self.verify(trace=bad)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_required_record_id_rejected(self):
        records = self.read_records()
        records[0].pop("record_id", None)
        bad = self.write_records(records, self.tmp / "missing-record-id.jsonl")
        result = self.verify(trace=bad)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsupported_schema_version_rejected(self):
        records = self.read_records()
        records[0]["schema_version"] = "999.0.0"
        bad = self.write_records(records, self.tmp / "unsupported-schema.jsonl")
        result = self.verify(trace=bad)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_raw_secret_stored_true_rejected(self):
        records = self.read_records()
        records[0].setdefault("redaction", {})["raw_secret_stored"] = True
        bad = self.write_records(records, self.tmp / "raw-secret-stored.jsonl")
        result = self.verify(trace=bad)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_scope_option_is_accepted_for_valid_trace(self):
        result = self.verify(scope=SCOPE_FILE)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"valid scoped verify failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_scope_id_mismatch_rejected_when_scope_provided(self):
        wrong_scope = self.tmp / "wrong-scope.json"
        scope_obj = json.loads(SCOPE_FILE.read_text(encoding="utf-8"))
        scope_obj["scope_id"] = "wrong-scope-id"
        wrong_scope.write_text(json.dumps(scope_obj, sort_keys=True), encoding="utf-8")

        result = self.verify(scope=wrong_scope)
        combined = result.stdout + result.stderr
        self.assertNotIn("unrecognized arguments", combined)
        self.assertNotEqual(result.returncode, 0, combined)


if __name__ == "__main__":
    unittest.main()
