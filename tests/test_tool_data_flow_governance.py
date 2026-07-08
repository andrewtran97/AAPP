import json
import unittest
from pathlib import Path

from aapp.tool_data_flow_governance import govern_tool_data_flow


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "tool_data_flow_governance"
    / "sample_tool_flow.json"
)


class ToolDataFlowGovernanceTests(unittest.TestCase):
    def load_cases(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        return fixture["cases"]

    def test_fixture_cases_match_expected_governance(self):
        for case in self.load_cases():
            with self.subTest(case=case["name"]):
                actual = govern_tool_data_flow(case["input"])
                expected = case["expected"]

                for key, value in expected.items():
                    self.assertEqual(actual.get(key), value)

    def test_evidence_digest_is_preserved(self):
        for case in self.load_cases():
            with self.subTest(case=case["name"]):
                actual = govern_tool_data_flow(case["input"])
                self.assertEqual(
                    actual.get("evidence_digest"),
                    case["input"].get("evidence_digest"),
                )

    def test_missing_required_field_is_malformed(self):
        record = dict(self.load_cases()[0]["input"])
        del record["record_id"]

        actual = govern_tool_data_flow(record)

        self.assertEqual(actual["governance_verdict"], "MALFORMED")
        self.assertEqual(actual["reason_codes"], ["MALFORMED_RECORD"])
        self.assertFalse(actual["export_allowed"])
        self.assertFalse(actual["training_allowed"])

    def test_blocked_record_cannot_export_or_train(self):
        case = next(
            item for item in self.load_cases() if item["name"] == "raw_secret_blocked"
        )

        actual = govern_tool_data_flow(case["input"])

        self.assertEqual(actual["governance_verdict"], "BLOCKED")
        self.assertFalse(actual["export_allowed"])
        self.assertFalse(actual["training_allowed"])


if __name__ == "__main__":
    unittest.main()
