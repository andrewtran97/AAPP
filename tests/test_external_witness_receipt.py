import json
import unittest
from pathlib import Path

from aapp.external_witness_receipt import generate_witness_receipt


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "external_witness_receipt"
    / "sample_receipt_input.json"
)


class ExternalWitnessReceiptTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_generates_expected_fixture_receipt(self):
        fixture = self.load_fixture()

        first = generate_witness_receipt(fixture["input"])
        second = generate_witness_receipt(fixture["input"])

        self.assertEqual(first, fixture["expected"])
        self.assertEqual(second, fixture["expected"])
        self.assertEqual(first, second)

    def test_preserves_evidence_digest(self):
        fixture = self.load_fixture()

        receipt = generate_witness_receipt(fixture["input"])

        self.assertEqual(
            receipt["evidence_digest"],
            fixture["input"]["evidence_digest"],
        )

    def test_unsupported_witness_method_is_not_silently_allowed(self):
        fixture = self.load_fixture()
        record = dict(fixture["input"])
        record["witness_method"] = "REMOTE_TIMESTAMP_AUTHORITY"

        receipt = generate_witness_receipt(record)

        self.assertEqual(receipt["witness_status"], "UNSUPPORTED")
        self.assertIn("UNSUPPORTED_WITNESS_METHOD", receipt["reason_codes"])
        self.assertIn("NO_EXTERNAL_WITNESS", receipt["reason_codes"])
        self.assertEqual(receipt["evidence_digest"], record["evidence_digest"])

    def test_missing_required_field_is_rejected(self):
        fixture = self.load_fixture()
        record = dict(fixture["input"])
        del record["evidence_digest"]

        receipt = generate_witness_receipt(record)

        self.assertEqual(receipt["witness_status"], "LOCAL_REJECTED")
        self.assertIn("MISSING_REQUIRED_FIELD", receipt["reason_codes"])

    def test_receipt_shape_is_stable(self):
        fixture = self.load_fixture()

        receipt = generate_witness_receipt(fixture["input"])

        self.assertEqual(
            list(receipt.keys()),
            [
                "receipt_id",
                "evidence_digest",
                "witness_subject",
                "witness_method",
                "witness_status",
                "issued_at",
                "verifier_version",
                "reason_codes",
            ],
        )

    def test_module_has_no_network_or_subprocess_dependency(self):
        module_path = Path("aapp/external_witness_receipt.py")
        text = module_path.read_text(encoding="utf-8")

        forbidden_tokens = [
            "requests",
            "urllib",
            "http.client",
            "socket",
            "subprocess",
        ]

        for token in forbidden_tokens:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
