import json
import unittest

from aapp.secret_evidence_boundary import (
    REDACTION,
    digest_value,
    evaluate_secret_evidence_boundary,
)


class SecretEvidenceBoundaryTests(unittest.TestCase):
    def test_secret_like_field_is_redacted_without_inlining_value(self):
        record = {
            "record_id": "ev-001",
            "action": "tool_call",
            "raw_secret_stored": False,
            "metadata": {
                "api_token": "test-only-placeholder",
                "public_note": "safe",
            },
        }

        result = evaluate_secret_evidence_boundary(record, purpose="export")
        serialized = json.dumps(result, sort_keys=True)

        self.assertEqual(result["verdict"], "REDACTED")
        self.assertIn("$.metadata.api_token", result["secret_paths"])
        self.assertEqual(result["sanitized_record"]["metadata"]["api_token"], REDACTION)
        self.assertNotIn("test-only-placeholder", serialized)

    def test_original_digest_is_preserved_after_sanitization(self):
        record = {
            "record_id": "ev-002",
            "metadata": {
                "client_secret": "test-only-placeholder",
            },
        }

        result = evaluate_secret_evidence_boundary(record, purpose="export")

        self.assertEqual(result["original_digest"], digest_value(record))
        self.assertNotEqual(result["original_digest"], result["sanitized_digest"])

    def test_training_on_secret_like_record_is_blocked(self):
        record = {
            "record_id": "ev-003",
            "metadata": {
                "session_token": "test-only-placeholder",
            },
        }

        result = evaluate_secret_evidence_boundary(record, purpose="training")

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("training_on_secret_like_value_blocked", result["reason_codes"])
        self.assertFalse(result["boundary"]["train_on_raw_secret"])

    def test_raw_secret_stored_flag_blocks_record(self):
        record = {
            "record_id": "ev-004",
            "raw_secret_stored": True,
            "metadata": {
                "public_note": "safe",
            },
        }

        result = evaluate_secret_evidence_boundary(record, purpose="export")

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("raw_secret_storage_declared", result["reason_codes"])

    def test_no_secret_like_value_is_allowed(self):
        record = {
            "record_id": "ev-005",
            "raw_secret_stored": False,
            "metadata": {
                "public_note": "safe",
            },
        }

        result = evaluate_secret_evidence_boundary(record, purpose="export")

        self.assertEqual(result["verdict"], "ALLOWED")
        self.assertEqual(result["redaction_count"], 0)
        self.assertEqual(result["secret_paths"], [])
        self.assertEqual(result["sanitized_record"], record)

    def test_malformed_input_is_rejected(self):
        result = evaluate_secret_evidence_boundary(["not", "an", "object"], purpose="export")

        self.assertEqual(result["verdict"], "MALFORMED")
        self.assertIn("record_must_be_object", result["reason_codes"])
        self.assertIsNone(result["sanitized_record"])


if __name__ == "__main__":
    unittest.main()
