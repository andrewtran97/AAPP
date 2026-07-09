import copy
import json
import pathlib
import unittest

from aapp.crypto_migration_dry_run import dry_run_crypto_migration

FIXTURE = pathlib.Path(
    "tests/fixtures/crypto_migration_dry_run/sample_migration_plan.json"
)


class CryptoMigrationDryRunTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text())

    def test_fixture_generates_deterministic_readiness_verdict(self):
        plan = self.load_fixture()

        first = dry_run_crypto_migration(plan)
        second = dry_run_crypto_migration(copy.deepcopy(plan))

        self.assertEqual(first, second)
        self.assertEqual(first["dry_run_verdict"], "REQUIRES_APPROVAL")
        self.assertEqual(first["reason_codes"], ["dry_run_only", "manual_approval_required"])
        self.assertEqual(
            [step["readiness"] for step in first["step_results"]],
            ["REQUIRES_APPROVAL", "REQUIRES_APPROVAL"],
        )
        self.assertIn(
            "keep_execution_mode_dry_run",
            first["required_follow_up_actions"],
        )

    def test_evidence_digest_is_preserved(self):
        plan = self.load_fixture()

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["evidence_digest"], plan["evidence_digest"])

    def test_missing_required_field_is_malformed(self):
        plan = self.load_fixture()
        del plan["evidence_digest"]

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["dry_run_verdict"], "MALFORMED")
        self.assertEqual(verdict["reason_codes"], ["missing_evidence_digest"])
        self.assertEqual(verdict["step_results"], [])

    def test_unsupported_schema_version_is_unsupported(self):
        plan = self.load_fixture()
        plan["schema_version"] = "unsupported.schema.v0"

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["dry_run_verdict"], "UNSUPPORTED")
        self.assertEqual(verdict["reason_codes"], ["unsupported_schema_version"])

    def test_unsupported_migration_step_is_blocked(self):
        plan = self.load_fixture()
        plan["migration_steps"][0]["action"] = "CUSTOM_UNSAFE_STEP"

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["dry_run_verdict"], "BLOCKED")
        self.assertEqual(verdict["reason_codes"], ["step_0_unsupported_action"])
        self.assertEqual(verdict["required_follow_up_actions"], ["remove_unsupported_step"])

    def test_production_environment_is_blocked(self):
        plan = self.load_fixture()
        plan["target_environment"] = "production"

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["dry_run_verdict"], "BLOCKED")
        self.assertEqual(verdict["reason_codes"], ["production_environment_not_allowed"])

    def test_live_key_rotation_execution_is_blocked(self):
        plan = self.load_fixture()
        plan["migration_steps"][1]["execution_mode"] = "live"
        plan["migration_steps"][1]["live_key_rotation"] = True

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["dry_run_verdict"], "BLOCKED")
        self.assertEqual(
            verdict["reason_codes"],
            [
                "step_1_unsafe_execution_mode_requested",
                "step_1_live_key_rotation_requested",
            ],
        )

    def test_no_action_plan_is_ready(self):
        plan = self.load_fixture()
        plan["planner_verdict"] = "NO_ACTION"
        plan["reason_codes"] = ["no_crypto_migration_required"]
        plan["migration_steps"] = []

        verdict = dry_run_crypto_migration(plan)

        self.assertEqual(verdict["dry_run_verdict"], "READY")
        self.assertEqual(verdict["reason_codes"], ["dry_run_ready_no_migration_steps"])
        self.assertEqual(verdict["required_follow_up_actions"], [])


if __name__ == "__main__":
    unittest.main()
