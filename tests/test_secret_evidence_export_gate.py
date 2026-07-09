import json
import unittest
from pathlib import Path

from aapp.secret_evidence_export_gate import (
    compute_digest,
    evaluate_secret_evidence_export,
)

VALID_DIGEST = "sha256:" + ("a" * 64)


class SecretEvidenceExportGateTests(unittest.TestCase):
    def _valid_record(self):
        return {
            "purpose": "siem",
            "original_digest": VALID_DIGEST,
            "boundary_verdict": "REDACTED",
            "raw_secret_stored": False,
            "export_record": {
                "record_id": "evt_001",
                "source_ref": "b40.secret_evidence_boundary",
                "subject": "agent.local",
                "action": "tool_call",
                "resource": "repo.main",
                "decision": "REDACTED",
                "redaction_marker": "[REDACTED_BY_B40_SECRET_EVIDENCE_BOUNDARY]",
            },
        }

    def test_fixture_record_is_allowed(self):
        path = Path("tests/fixtures/secret_evidence_export_gate/sample_export_record.json")
        record = json.loads(path.read_text(encoding="utf-8"))

        result = evaluate_secret_evidence_export(record)

        self.assertEqual(result["verdict"], "ALLOWED")
        self.assertEqual(result["reason_codes"], ["secret_safe_export_allowed"])

    def test_allowed_record_returns_deterministic_sanitized_digest(self):
        record = self._valid_record()

        first = evaluate_secret_evidence_export(record)
        second = evaluate_secret_evidence_export(record)

        self.assertEqual(first["verdict"], "ALLOWED")
        self.assertEqual(first["sanitized_digest"], second["sanitized_digest"])
        self.assertEqual(first["sanitized_digest"], compute_digest(record["export_record"]))

    def test_inline_secret_like_value_is_blocked(self):
        record = self._valid_record()
        record["export_record"]["leaked_value"] = "Bearer abcdefghijklmnop"

        result = evaluate_secret_evidence_export(record)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("inline_secret_like_value_detected", result["reason_codes"])

    def test_secret_like_field_must_be_redacted(self):
        record = self._valid_record()
        record["export_record"]["api_key"] = "not-redacted"

        result = evaluate_secret_evidence_export(record)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("secret_like_field_not_redacted", result["reason_codes"])

    def test_training_purpose_is_blocked(self):
        record = self._valid_record()
        record["purpose"] = "model_training"

        result = evaluate_secret_evidence_export(record)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("training_purpose_blocked", result["reason_codes"])

    def test_raw_secret_stored_true_is_blocked(self):
        record = self._valid_record()
        record["raw_secret_stored"] = True

        result = evaluate_secret_evidence_export(record)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("raw_secret_stored_true", result["reason_codes"])

    def test_missing_original_digest_is_blocked(self):
        record = self._valid_record()
        del record["original_digest"]

        result = evaluate_secret_evidence_export(record)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("missing_or_invalid_original_digest", result["reason_codes"])


if __name__ == "__main__":
    unittest.main()
