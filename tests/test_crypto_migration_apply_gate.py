import json
import unittest
from pathlib import Path

from aapp.crypto_migration_apply_gate import evaluate_crypto_migration_apply_gate


FIXTURE = Path("tests/fixtures/crypto_migration_apply_gate/sample_receipt_bundle.json")


class CryptoMigrationApplyGateTests(unittest.TestCase):
    def _sample(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_valid_receipt_is_apply_ready_without_execution(self):
        result = evaluate_crypto_migration_apply_gate(self._sample())

        self.assertEqual(result["verdict"], "APPLY_READY")
        self.assertTrue(result["allowed_to_apply"])
        self.assertFalse(result["execution_performed"])
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(result["required_next_step"], "human_apply_confirmation")

    def test_missing_receipt_bundle_blocks(self):
        payload = self._sample()
        del payload["receipt_bundle"]

        result = evaluate_crypto_migration_apply_gate(payload)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertFalse(result["allowed_to_apply"])
        self.assertIn("missing_receipt_bundle", result["reason_codes"])

    def test_failed_dry_run_blocks(self):
        payload = self._sample()
        payload["receipt_bundle"]["dry_run_verdict"] = "FAILED"

        result = evaluate_crypto_migration_apply_gate(payload)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("dry_run_not_passed", result["reason_codes"])

    def test_non_production_environment_blocks(self):
        payload = self._sample()
        payload["environment"] = "staging"

        result = evaluate_crypto_migration_apply_gate(payload)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("unsupported_environment", result["reason_codes"])

    def test_invalid_receipt_digest_blocks(self):
        payload = self._sample()
        payload["receipt_bundle"]["receipt_digest"] = "not-a-digest"

        result = evaluate_crypto_migration_apply_gate(payload)

        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertIn("missing_or_invalid_receipt_digest", result["reason_codes"])

    def test_output_is_deterministic(self):
        payload = self._sample()

        first = evaluate_crypto_migration_apply_gate(payload)
        second = evaluate_crypto_migration_apply_gate(payload)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
