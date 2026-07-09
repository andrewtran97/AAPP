import json
import unittest
from pathlib import Path

from aapp.tenant_boundary import (
    ALLOWED,
    CROSS_TENANT_EXPORT_NOT_ALLOWED,
    CROSS_TENANT_TRAINING_NOT_ALLOWED,
    GOVERNANCE_VERDICT_REQUIRED,
    MALFORMED,
    TENANT_BOUNDARY_VIOLATION,
    evaluate_tenant_boundary,
)


FIXTURE = Path("tests/fixtures/tenant_boundary/sample_request.json")


class TenantBoundaryTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_allows_same_tenant_request(self):
        payload = self.load_fixture()
        result = evaluate_tenant_boundary(payload)

        self.assertEqual(result["verdict"], ALLOWED)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])
        self.assertFalse(result["cross_tenant"])

    def test_rejects_missing_required_field_as_malformed(self):
        payload = self.load_fixture()
        del payload["source_tenant"]

        result = evaluate_tenant_boundary(payload)

        self.assertEqual(result["verdict"], MALFORMED)
        self.assertIn("source_tenant", result["missing_fields"])

    def test_rejects_cross_tenant_access_without_approval(self):
        payload = self.load_fixture()
        payload["destination_tenant"] = "tenant_b"
        payload["action"] = "read"

        result = evaluate_tenant_boundary(payload)

        self.assertEqual(result["verdict"], TENANT_BOUNDARY_VIOLATION)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_requires_governance_for_cross_tenant_evidence_release(self):
        payload = self.load_fixture()
        payload["destination_tenant"] = "tenant_b"
        payload["action"] = "evidence_release"
        payload["has_governance_verdict"] = False

        result = evaluate_tenant_boundary(payload)

        self.assertEqual(result["verdict"], GOVERNANCE_VERDICT_REQUIRED)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_blocks_cross_tenant_export_without_approval(self):
        payload = self.load_fixture()
        payload["destination_tenant"] = "tenant_b"
        payload["action"] = "export"
        payload["has_governance_verdict"] = True

        result = evaluate_tenant_boundary(payload)

        self.assertEqual(result["verdict"], CROSS_TENANT_EXPORT_NOT_ALLOWED)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])

    def test_blocks_cross_tenant_training(self):
        payload = self.load_fixture()
        payload["destination_tenant"] = "tenant_b"
        payload["action"] = "train"
        payload["has_governance_verdict"] = True
        payload["approval_ref"] = "approval-001"

        result = evaluate_tenant_boundary(payload)

        self.assertEqual(result["verdict"], CROSS_TENANT_TRAINING_NOT_ALLOWED)
        self.assertEqual(result["evidence_digest"], payload["evidence_digest"])


if __name__ == "__main__":
    unittest.main()
