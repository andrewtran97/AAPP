import json
import unittest
from pathlib import Path

from aapp.audit_siem_export import export_audit_record


FIXTURE = Path("tests/fixtures/audit_siem_export/sample_evidence_event.json")


class AuditSiemExportTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_ecs_export_preserves_evidence_digest(self):
        record = self.load_fixture()

        result = export_audit_record(record, "ecs_json")

        self.assertEqual(result["verdict"], "EXPORTED")
        self.assertEqual(result["format"], "ecs_json")
        self.assertEqual(result["evidence_digest"], record["evidence_digest"])
        self.assertEqual(result["export"]["@timestamp"], record["occurred_at"])
        self.assertEqual(result["export"]["event"]["action"], record["action"])
        self.assertEqual(
            result["export"]["aapp"]["evidence_digest"],
            record["evidence_digest"],
        )

    def test_cef_export_preserves_evidence_digest(self):
        record = self.load_fixture()

        result = export_audit_record(record, "cef_text")

        self.assertEqual(result["verdict"], "EXPORTED")
        self.assertEqual(result["format"], "cef_text")
        self.assertIn("CEF:0|AAPP|Agent Black Box|local-reference|", result["export"])
        self.assertIn(f"cs1={record['evidence_digest']}", result["export"])

    def test_secret_like_summary_is_redacted(self):
        record = self.load_fixture()
        record["summary"] = "BEGIN PRIVATE KEY should not be exported"

        ecs_result = export_audit_record(record, "ecs_json")
        cef_result = export_audit_record(record, "cef_text")

        self.assertEqual(ecs_result["verdict"], "REDACTED")
        self.assertEqual(ecs_result["export"]["message"], "[REDACTED]")
        self.assertIn("SECRET_LIKE_VALUE_REDACTED", ecs_result["reason_codes"])
        self.assertNotIn("BEGIN PRIVATE KEY", cef_result["export"])

    def test_unsupported_format_is_deterministic(self):
        record = self.load_fixture()

        result = export_audit_record(record, "live_siem")

        self.assertEqual(result["verdict"], "UNSUPPORTED")
        self.assertEqual(result["format"], "live_siem")
        self.assertEqual(result["reason_codes"], ["UNSUPPORTED_FORMAT"])
        self.assertIsNone(result["export"])

    def test_missing_required_field_is_malformed(self):
        record = self.load_fixture()
        del record["evidence_digest"]

        result = export_audit_record(record, "ecs_json")

        self.assertEqual(result["verdict"], "MALFORMED")
        self.assertIn("MISSING_REQUIRED_FIELD", result["reason_codes"])
        self.assertEqual(result["missing_fields"], ["evidence_digest"])
        self.assertIsNone(result["export"])


if __name__ == "__main__":
    unittest.main()
