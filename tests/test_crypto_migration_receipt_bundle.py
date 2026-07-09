import copy
import json
import unittest
from pathlib import Path

from aapp.crypto_migration_receipt_bundle import (
    BUNDLE_SCHEMA_VERSION,
    ReceiptBundleError,
    create_crypto_migration_receipt_bundle,
    verify_crypto_migration_receipt_bundle,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "crypto_migration_receipt_bundle"
    / "sample_dry_run_result.json"
)


class CryptoMigrationReceiptBundleTests(unittest.TestCase):
    def load_sample(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_create_bundle_and_verify(self):
        sample = self.load_sample()
        bundle = create_crypto_migration_receipt_bundle(sample)

        self.assertEqual(bundle["schema_version"], BUNDLE_SCHEMA_VERSION)
        self.assertEqual(bundle["receipt_status"], "ISSUED")
        self.assertEqual(bundle["dry_run_verdict"], "READY")
        self.assertFalse(bundle["execution_allowed"])
        self.assertFalse(bundle["production_safety_claimed"])
        self.assertFalse(bundle["compliance_certification_claimed"])
        self.assertEqual(
            bundle["upstream_evidence_digests"]["dry_run"],
            sample["source_refs"]["dry_run"]["evidence_digest"],
        )
        self.assertTrue(bundle["bundle_digest"].startswith("sha256:"))

        verification = verify_crypto_migration_receipt_bundle(bundle)
        self.assertEqual(verification["verification_status"], "VALID")

    def test_bundle_digest_is_deterministic(self):
        sample = self.load_sample()
        first = create_crypto_migration_receipt_bundle(sample)
        second = create_crypto_migration_receipt_bundle(copy.deepcopy(sample))

        self.assertEqual(first["bundle_digest"], second["bundle_digest"])
        self.assertEqual(first, second)

    def test_missing_source_ref_rejected(self):
        sample = self.load_sample()
        del sample["source_refs"]["policy_decision"]

        with self.assertRaisesRegex(ReceiptBundleError, "source_refs.policy_decision"):
            create_crypto_migration_receipt_bundle(sample)

    def test_subject_mismatch_rejected(self):
        sample = self.load_sample()
        sample["source_refs"]["inventory"]["subject_ref"] = "subject:attacker"

        with self.assertRaisesRegex(ReceiptBundleError, "inventory_subject_ref_mismatch"):
            create_crypto_migration_receipt_bundle(sample)

    def test_resource_mismatch_rejected(self):
        sample = self.load_sample()
        sample["source_refs"]["dry_run"]["resource_ref"] = "crypto:keyset:other"

        with self.assertRaisesRegex(ReceiptBundleError, "dry_run_resource_ref_mismatch"):
            create_crypto_migration_receipt_bundle(sample)

    def test_blocked_dry_run_verdict_rejected(self):
        sample = self.load_sample()
        sample["dry_run_verdict"] = "BLOCKED"

        with self.assertRaisesRegex(ReceiptBundleError, "dry_run_verdict_not_ready"):
            create_crypto_migration_receipt_bundle(sample)

    def test_tampered_bundle_is_invalid(self):
        sample = self.load_sample()
        bundle = create_crypto_migration_receipt_bundle(sample)
        bundle["source_refs"]["dry_run"]["ref"] = "b37:tampered"

        verification = verify_crypto_migration_receipt_bundle(bundle)
        self.assertEqual(verification["verification_status"], "INVALID")
        self.assertEqual(verification["reason_codes"], ["bundle_digest_mismatch"])


if __name__ == "__main__":
    unittest.main()
