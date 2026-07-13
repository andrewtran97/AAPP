import ast
import copy
import json
import unittest
from pathlib import Path

from aapp.attestation_provider_adapter import (
    DIGEST_MISMATCH,
    IDENTITY_MISMATCH,
    MALFORMED,
    NONCE_MISMATCH,
    STALE,
    UNTRUSTED,
    UNSUPPORTED,
    VERIFIED,
    evidence_digest,
    evaluate_attestation_provider,
)

FIXTURE = Path(
    "tests/fixtures/attestation_provider_adapter/sample_attestation.json"
)
MODULE = Path("aapp/attestation_provider_adapter.py")
OTHER_DIGEST = "sha256:" + ("2" * 64)


class AttestationProviderAdapterTests(unittest.TestCase):
    def load_case(self, name="local_static"):
        case = json.loads(FIXTURE.read_text(encoding="utf-8"))[name]
        return copy.deepcopy(case["request"]), copy.deepcopy(case["evidence"])

    def rebind(self, request, evidence):
        digest = evidence_digest(evidence)
        evidence["evidence_digest"] = digest
        request["expected_evidence_digest"] = digest

    def assert_outcome(self, request, evidence, verdict, reason):
        result = evaluate_attestation_provider(request, evidence)
        self.assertEqual((result["verdict"], result["reason_codes"]), (verdict, [reason]))
        return result

    def test_supported_fixtures_verify_deterministically(self):
        for provider in ("local_static", "tee_attestation_shape"):
            with self.subTest(provider=provider):
                request, evidence = self.load_case(provider)
                request_before = copy.deepcopy(request)
                evidence_before = copy.deepcopy(evidence)
                self.assertEqual(evidence_digest(evidence), evidence["evidence_digest"])
                result = self.assert_outcome(
                    request, evidence, VERIFIED, "ALL_CHECKS_PASSED"
                )
                self.assertTrue(all(result["checks"].values()))
                self.assertEqual(
                    result["source_evidence_digest"], evidence["evidence_digest"]
                )
                self.assertEqual((request, evidence), (request_before, evidence_before))
                self.assertEqual(
                    evaluate_attestation_provider(request, evidence), result
                )

    def test_shape_schema_and_provider_boundaries(self):
        request, evidence = self.load_case()
        direct = (
            (None, evidence, MALFORMED, "REQUEST_NOT_OBJECT"),
            (request, [], MALFORMED, "EVIDENCE_NOT_OBJECT"),
        )
        for case_request, case_evidence, verdict, reason in direct:
            self.assert_outcome(case_request, case_evidence, verdict, reason)

        cases = (
            (
                lambda r, e: r.pop("request_id"),
                MALFORMED,
                "MISSING_REQUIRED_FIELD:request.request_id",
            ),
            (
                lambda r, e: r.__setitem__("max_age_seconds", True),
                MALFORMED,
                "INVALID_FIELD_TYPE:request.max_age_seconds",
            ),
            (
                lambda r, e: e.__setitem__("trusted", "true"),
                MALFORMED,
                "INVALID_FIELD_TYPE:evidence.trusted",
            ),
            (
                lambda r, e: r.__setitem__(
                    "schema_version", "unsupported.request.v1"
                ),
                UNSUPPORTED,
                "UNSUPPORTED_SCHEMA_VERSION:request",
            ),
            (
                lambda r, e: r.__setitem__("provider_type", "unknown_provider"),
                UNSUPPORTED,
                "UNSUPPORTED_PROVIDER:request",
            ),
            (
                lambda r, e: e.__setitem__(
                    "schema_version", "unsupported.evidence.v1"
                ),
                UNSUPPORTED,
                "UNSUPPORTED_SCHEMA_VERSION:evidence",
            ),
            (
                lambda r, e: e.__setitem__("provider_type", "unknown_provider"),
                UNSUPPORTED,
                "UNSUPPORTED_PROVIDER:evidence",
            ),
        )
        for mutate, verdict, reason in cases:
            with self.subTest(reason=reason):
                request, evidence = self.load_case()
                mutate(request, evidence)
                self.assert_outcome(request, evidence, verdict, reason)

    def test_digest_trust_and_timestamp_boundaries(self):
        cases = (
            (
                lambda r, e: e.__setitem__(
                    "evidence_digest", "sha256:" + ("f" * 64)
                ),
                False,
                DIGEST_MISMATCH,
                "EVIDENCE_DIGEST_MISMATCH",
            ),
            (
                lambda r, e: e.__setitem__(
                    "provider_type", "tee_attestation_shape"
                ),
                True,
                DIGEST_MISMATCH,
                "PROVIDER_TYPE_MISMATCH",
            ),
            (
                lambda r, e: e.__setitem__("trusted", False),
                True,
                UNTRUSTED,
                "EVIDENCE_UNTRUSTED",
            ),
            (
                lambda r, e: r.__setitem__(
                    "evaluated_at", "2026-07-13 12:00:00Z"
                ),
                False,
                MALFORMED,
                "INVALID_TIMESTAMP:request.evaluated_at",
            ),
            (
                lambda r, e: e.__setitem__(
                    "attestation_timestamp", "2026-07-13 12:00:00Z"
                ),
                True,
                MALFORMED,
                "INVALID_TIMESTAMP:evidence.attestation_timestamp",
            ),
            (
                lambda r, e: e.__setitem__(
                    "attestation_timestamp", "2026-07-13T11:54:59Z"
                ),
                True,
                STALE,
                "EVIDENCE_STALE",
            ),
            (
                lambda r, e: e.__setitem__(
                    "attestation_timestamp", "2026-07-13T12:00:31Z"
                ),
                True,
                STALE,
                "EVIDENCE_FROM_FUTURE",
            ),
        )
        for mutate, rebind, verdict, reason in cases:
            with self.subTest(reason=reason):
                request, evidence = self.load_case()
                mutate(request, evidence)
                if rebind:
                    self.rebind(request, evidence)
                self.assert_outcome(request, evidence, verdict, reason)

        for timestamp in ("2026-07-13T11:55:00Z", "2026-07-13T12:00:30Z"):
            request, evidence = self.load_case()
            evidence["attestation_timestamp"] = timestamp
            self.rebind(request, evidence)
            self.assert_outcome(request, evidence, VERIFIED, "ALL_CHECKS_PASSED")

        request, evidence = self.load_case()
        evidence["unserializable"] = {1, 2}
        self.assert_outcome(
            request, evidence, MALFORMED, "EVIDENCE_CANONICALIZATION_FAILED"
        )

    def test_binding_mismatches(self):
        cases = (
            ("nonce", "nonce-other", NONCE_MISMATCH, "NONCE_MISMATCH"),
            (
                "workload_identity_ref",
                "workload:other:v1",
                IDENTITY_MISMATCH,
                "WORKLOAD_IDENTITY_MISMATCH",
            ),
            (
                "artifact_digest",
                OTHER_DIGEST,
                DIGEST_MISMATCH,
                "ARTIFACT_DIGEST_MISMATCH",
            ),
            (
                "runtime_digest",
                OTHER_DIGEST,
                DIGEST_MISMATCH,
                "RUNTIME_DIGEST_MISMATCH",
            ),
            (
                "policy_version",
                "policy-v2",
                DIGEST_MISMATCH,
                "POLICY_VERSION_MISMATCH",
            ),
        )
        for field, value, verdict, reason in cases:
            with self.subTest(field=field):
                request, evidence = self.load_case()
                evidence[field] = value
                self.rebind(request, evidence)
                self.assert_outcome(request, evidence, verdict, reason)

    def test_runtime_excludes_network_and_subprocess_imports(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"), filename=str(MODULE))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        forbidden = {
            "aiohttp",
            "ftplib",
            "http",
            "httpx",
            "requests",
            "socket",
            "subprocess",
            "urllib",
        }
        self.assertTrue(forbidden.isdisjoint(imported))


if __name__ == "__main__":
    unittest.main()
