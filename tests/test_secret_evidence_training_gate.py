import json
import unittest
from pathlib import Path

from aapp.secret_evidence_training_gate import (
    REDACTION,
    evaluate_training_gate,
)


class SecretEvidenceTrainingGateTests(unittest.TestCase):
    def test_training_on_raw_secret_record_is_blocked(self):
        result = evaluate_training_gate({
            "record_id": "rec_001",
            "purpose": "training",
            "raw_secret_stored": True,
            "payload": {"note": "metadata only"},
        })

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("training_on_raw_secret_record_blocked", result["reason_codes"])

    def test_training_on_secret_like_payload_is_blocked_and_redacted(self):
        result = evaluate_training_gate({
            "record_id": "rec_002",
            "purpose": "fine_tune",
            "raw_secret_stored": False,
            "payload": {"token": "Bearer abcdefghijklmnop"},
        })

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("training_on_secret_like_payload_blocked", result["reason_codes"])
        self.assertEqual(result["sanitized_record"]["payload"], REDACTION)
        self.assertNotIn("abcdefghijklmnop", json.dumps(result, sort_keys=True))

    def test_sanitized_metadata_only_training_is_allowed(self):
        result = evaluate_training_gate({
            "record_id": "rec_003",
            "purpose": "training",
            "raw_secret_stored": False,
            "secret_classification": "sanitized_metadata_only",
            "original_digest": "sha256:" + "a" * 64,
            "allow_sanitized_metadata": True,
        })

        self.assertEqual(result["verdict"], "ALLOWED")
        self.assertIn("no_training_secret_boundary_violation", result["reason_codes"])
        self.assertEqual(result["secret_like_paths"], [])

    def test_non_training_audit_use_is_allowed(self):
        result = evaluate_training_gate({
            "record_id": "rec_004",
            "purpose": "audit",
            "raw_secret_stored": False,
            "secret_classification": "metadata_only",
        })

        self.assertEqual(result["verdict"], "ALLOWED")
        self.assertFalse(result["training_purpose"])

    def test_missing_record_id_is_malformed(self):
        result = evaluate_training_gate({
            "purpose": "training",
            "raw_secret_stored": False,
        })

        self.assertEqual(result["verdict"], "MALFORMED")
        self.assertIn("missing_record_id", result["reason_codes"])

    def test_fixture_case_matches_expected_verdict(self):
        fixture = Path("tests/fixtures/secret_evidence_training_gate/sample_training_record.json")
        record = json.loads(fixture.read_text(encoding="utf-8"))

        result = evaluate_training_gate(record)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("training_on_secret_like_payload_blocked", result["reason_codes"])
        self.assertNotIn("AKIA1234567890ABCD", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
