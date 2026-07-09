import copy
import json
import pathlib
import unittest

from aapp.crypto_migration_planner import plan_crypto_migration


FIXTURE = pathlib.Path(
    "tests/fixtures/crypto_migration_planner/sample_policy_decision.json"
)


class CryptoMigrationPlannerTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text())

    def test_fixture_generates_deterministic_migration_plan(self):
        record = self.load_fixture()

        first = plan_crypto_migration(record)
        second = plan_crypto_migration(copy.deepcopy(record))

        self.assertEqual(first, second)
        self.assertEqual(first["planner_verdict"], "PLAN_REQUIRED")
        self.assertEqual(first["reason_codes"], ["migration_required"])
        self.assertEqual(len(first["migration_steps"]), 2)
        self.assertEqual(
            [step["action"] for step in first["migration_steps"]],
            ["REPLACE_ALGORITHM", "ROTATE_KEY"],
        )

    def test_evidence_digest_is_preserved(self):
        record = self.load_fixture()

        plan = plan_crypto_migration(record)

        self.assertEqual(plan["evidence_digest"], record["evidence_digest"])

    def test_missing_required_field_is_malformed(self):
        record = self.load_fixture()
        del record["evidence_digest"]

        plan = plan_crypto_migration(record)

        self.assertEqual(plan["planner_verdict"], "MALFORMED")
        self.assertEqual(plan["reason_codes"], ["missing_evidence_digest"])
        self.assertEqual(plan["migration_steps"], [])

    def test_unsupported_schema_version_is_unsupported(self):
        record = self.load_fixture()
        record["schema_version"] = "unsupported.schema.v0"

        plan = plan_crypto_migration(record)

        self.assertEqual(plan["planner_verdict"], "UNSUPPORTED")
        self.assertEqual(plan["reason_codes"], ["unsupported_schema_version"])
        self.assertEqual(plan["migration_steps"], [])

    def test_allowed_findings_return_no_action(self):
        record = self.load_fixture()
        record["policy_verdict"] = "ALLOW"
        for finding in record["findings"]:
            finding["decision"] = "ALLOW"
            finding["risk_level"] = "LOW"
            finding["recommendation"] = "no_action"

        plan = plan_crypto_migration(record)

        self.assertEqual(plan["planner_verdict"], "NO_ACTION")
        self.assertEqual(plan["reason_codes"], ["no_crypto_migration_required"])
        self.assertEqual(plan["migration_steps"], [])

    def test_unknown_decision_documents_exception(self):
        record = self.load_fixture()
        record["findings"] = [
            {
                "finding_id": "finding-unknown",
                "algorithm": "custom-legacy-cipher",
                "use": "encryption",
                "risk_level": "MEDIUM",
                "decision": "UNKNOWN",
                "recommendation": "manual_review",
            }
        ]

        plan = plan_crypto_migration(record)

        self.assertEqual(plan["planner_verdict"], "PLAN_REQUIRED")
        self.assertEqual(plan["migration_steps"][0]["action"], "DOCUMENT_EXCEPTION")


if __name__ == "__main__":
    unittest.main()
