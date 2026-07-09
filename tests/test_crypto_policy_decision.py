import json
import unittest
from pathlib import Path

from aapp.crypto_policy_decision import decide_crypto_policy


FIXTURE = Path("tests/fixtures/crypto_policy_decision/sample_inventory.json")


class CryptoPolicyDecisionTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_maps_to_strictest_policy_verdict(self):
        result = decide_crypto_policy(self.load_fixture(), source_ref="sample_inventory.json")

        self.assertEqual(result["policy_verdict"], "DISALLOWED")
        self.assertEqual(result["decision_count"], 6)

    def test_approved_findings_are_approved(self):
        inventory = {
            "findings": [
                {"algorithm": "SHA-256", "category": "hash_algorithm"},
                {"algorithm": "AES", "category": "symmetric_encryption_algorithm"},
            ]
        }

        result = decide_crypto_policy(inventory)

        self.assertEqual(result["policy_verdict"], "APPROVED")
        self.assertEqual(result["reason_codes"], ["CRYPTO_APPROVED"])

    def test_review_required_algorithms_are_reason_coded(self):
        inventory = {
            "findings": [
                {"algorithm": "RSA", "category": "signature_or_public_key_algorithm"},
                {"algorithm": "ECDH", "category": "key_exchange_algorithm"},
            ]
        }

        result = decide_crypto_policy(inventory)

        self.assertEqual(result["policy_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(result["reason_codes"], ["CRYPTO_REVIEW_REQUIRED"])

    def test_deprecated_algorithms_are_reason_coded(self):
        inventory = {
            "findings": [
                {"algorithm": "MD5", "category": "hash_algorithm"},
                {"algorithm": "SHA-1", "category": "hash_algorithm"},
            ]
        }

        result = decide_crypto_policy(inventory)

        self.assertEqual(result["policy_verdict"], "DEPRECATED")
        self.assertEqual(result["reason_codes"], ["CRYPTO_DEPRECATED"])

    def test_migration_required_algorithms_are_stricter_than_deprecated(self):
        inventory = {
            "findings": [
                {"algorithm": "MD5", "category": "hash_algorithm"},
                {"algorithm": "DES", "category": "symmetric_encryption_algorithm"},
            ]
        }

        result = decide_crypto_policy(inventory)

        self.assertEqual(result["policy_verdict"], "MIGRATION_REQUIRED")
        self.assertIn("CRYPTO_MIGRATION_REQUIRED", result["reason_codes"])

    def test_private_key_marker_is_disallowed(self):
        inventory = {
            "findings": [
                {"algorithm": "PRIVATE_KEY_MARKER", "category": "certificate_or_key_marker"}
            ]
        }

        result = decide_crypto_policy(inventory)

        self.assertEqual(result["policy_verdict"], "DISALLOWED")
        self.assertEqual(result["reason_codes"], ["CRYPTO_MARKER_DISALLOWED"])

    def test_unknown_algorithm_requires_review(self):
        inventory = {
            "findings": [
                {"algorithm": "FutureAlgo", "category": "unknown"}
            ]
        }

        result = decide_crypto_policy(inventory)

        self.assertEqual(result["policy_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(result["reason_codes"], ["CRYPTO_UNKNOWN_REVIEW_REQUIRED"])

    def test_unsupported_input_is_deterministic(self):
        result = decide_crypto_policy(["not", "an", "object"])

        self.assertEqual(result["policy_verdict"], "UNSUPPORTED")
        self.assertEqual(result["reason_codes"], ["INPUT_NOT_OBJECT"])
        self.assertEqual(result["decisions"], [])
        self.assertEqual(result["decision_count"], 0)

    def test_missing_findings_is_malformed(self):
        result = decide_crypto_policy({})

        self.assertEqual(result["policy_verdict"], "MALFORMED")
        self.assertEqual(result["reason_codes"], ["MISSING_FINDINGS"])

    def test_finding_missing_algorithm_is_malformed(self):
        result = decide_crypto_policy({"findings": [{"category": "hash_algorithm"}]})

        self.assertEqual(result["policy_verdict"], "MALFORMED")
        self.assertEqual(result["reason_codes"], ["FINDING_MISSING_ALGORITHM"])

    def test_decision_is_deterministic(self):
        inventory = self.load_fixture()

        first = decide_crypto_policy(inventory)
        second = decide_crypto_policy(inventory)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
