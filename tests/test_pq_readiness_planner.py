import json
import unittest
from pathlib import Path

from aapp.pq_readiness_planner import (
    INCOMPLETE,
    MALFORMED,
    MIGRATION_GAP,
    NEEDS_INVENTORY,
    PQ_MIGRATION_REQUIRED,
    READY,
    UNSUPPORTED_ALGORITHM,
    plan_pq_readiness,
)


FIXTURE = Path("tests/fixtures/pq_readiness_planner/sample_crypto_context.json")


class PQReadinessPlannerTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_ready_for_pq_ready_inventory(self):
        payload = self.load_fixture()

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], READY)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_needs_inventory_when_inventory_empty(self):
        payload = self.load_fixture()
        payload["crypto_inventory"] = []

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], NEEDS_INVENTORY)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_classical_asymmetric_long_lived_requires_pq_migration(self):
        payload = self.load_fixture()
        payload["long_lived_confidentiality"] = True
        payload["crypto_inventory"] = [
            {
                "asset": "api:auth",
                "algorithm": "RSA",
                "usage": "key_transport"
            }
        ]
        payload["migration_paths"] = {"RSA": "ML-KEM"}

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], PQ_MIGRATION_REQUIRED)
        self.assertIn("RSA", result["algorithms"])
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_missing_migration_path_is_gap(self):
        payload = self.load_fixture()
        payload["long_lived_confidentiality"] = True
        payload["crypto_inventory"] = [
            {
                "asset": "api:auth",
                "algorithm": "ECDSA",
                "usage": "signature"
            }
        ]
        payload["migration_paths"] = {}

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], MIGRATION_GAP)
        self.assertIn("ECDSA", result["algorithms"])
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_unsupported_algorithm_is_rejected(self):
        payload = self.load_fixture()
        payload["crypto_inventory"] = [
            {
                "asset": "legacy:unknown",
                "algorithm": "CUSTOM-CRYPTO",
                "usage": "unknown"
            }
        ]

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], UNSUPPORTED_ALGORITHM)
        self.assertIn("CUSTOM-CRYPTO", result["unsupported_algorithms"])

    def test_missing_required_field_is_malformed(self):
        payload = self.load_fixture()
        del payload["evidence_digest"]

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], MALFORMED)
        self.assertIn("evidence_digest", result["missing_fields"])

    def test_missing_algorithm_classification_is_incomplete(self):
        payload = self.load_fixture()
        payload["crypto_inventory"] = [
            {
                "asset": "artifact:missing-classification",
                "usage": "signature"
            }
        ]

        result = plan_pq_readiness(payload)

        self.assertEqual(result["verdict"], INCOMPLETE)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])


if __name__ == "__main__":
    unittest.main()
