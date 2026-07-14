from __future__ import annotations

import ast
import copy
import json
import unittest
from pathlib import Path

import aapp.supply_chain_provenance as provenance


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "supply_chain_provenance"
    / "sample_build.json"
)
RUNTIME_PATH = (
    Path(__file__).parents[1]
    / "aapp"
    / "supply_chain_provenance.py"
)


class SupplyChainProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.valid_request = payload["valid"]["request"]
        cls.valid_build = payload["valid"]["build_record"]

    def setUp(self) -> None:
        self.request = copy.deepcopy(self.valid_request)
        self.build = copy.deepcopy(self.valid_build)

    def assert_verdict(
        self,
        result: dict[str, object],
        verdict: str,
        reason_code: str,
    ) -> None:
        self.assertEqual(result["verdict"], verdict)
        self.assertEqual(result["reason_codes"], [reason_code])

    def evaluate_build_change(
        self,
        path: tuple[str, ...],
        value: object,
    ) -> dict[str, object]:
        build = copy.deepcopy(self.valid_build)
        target = build
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        build["provenance_digest"] = provenance.provenance_digest(build)
        return provenance.evaluate_supply_chain_provenance(
            self.request,
            build,
        )

    def test_valid_fixture_verifies_deterministically(self) -> None:
        request_before = copy.deepcopy(self.request)
        build_before = copy.deepcopy(self.build)

        first = provenance.evaluate_supply_chain_provenance(
            self.request,
            self.build,
        )
        second = provenance.evaluate_supply_chain_provenance(
            self.request,
            self.build,
        )

        self.assert_verdict(
            first,
            provenance.VERIFIED,
            "ALL_CHECKS_PASSED",
        )
        self.assertEqual(first["schema_version"], provenance.RESULT_SCHEMA)
        self.assertEqual(first, second)
        self.assertTrue(all(first["checks"].values()))
        self.assertEqual(
            first["source_evidence_digest"],
            self.request["expected_source_evidence_digest"],
        )
        self.assertEqual(
            self.build["provenance_digest"],
            provenance.provenance_digest(self.build),
        )
        self.assertEqual(self.request, request_before)
        self.assertEqual(self.build, build_before)

    def test_required_fields_and_malformed_inputs_fail_closed(self) -> None:
        request_not_object = provenance.evaluate_supply_chain_provenance(
            None,
            self.build,
        )
        self.assert_verdict(
            request_not_object,
            provenance.MALFORMED,
            "REQUEST_NOT_OBJECT",
        )

        build_not_object = provenance.evaluate_supply_chain_provenance(
            self.request,
            None,
        )
        self.assert_verdict(
            build_not_object,
            provenance.MALFORMED,
            "BUILD_RECORD_NOT_OBJECT",
        )

        missing_request_id = copy.deepcopy(self.request)
        missing_request_id.pop("request_id")
        missing_result = provenance.evaluate_supply_chain_provenance(
            missing_request_id,
            self.build,
        )
        self.assert_verdict(
            missing_result,
            provenance.INCOMPLETE,
            "MISSING_REQUIRED_FIELD:request.request_id",
        )

        integer_trust = copy.deepcopy(self.build)
        integer_trust["builder"]["trusted"] = 1
        integer_trust["provenance_digest"] = provenance.provenance_digest(
            integer_trust
        )
        trust_result = provenance.evaluate_supply_chain_provenance(
            self.request,
            integer_trust,
        )
        self.assert_verdict(
            trust_result,
            provenance.MALFORMED,
            "INVALID_FIELD_TYPE:build.builder.trusted",
        )

    def test_schema_source_builder_and_workflow_boundaries(self) -> None:
        unsupported_request = copy.deepcopy(self.request)
        unsupported_request["schema_version"] = "unsupported.request.v1"
        unsupported_request_result = (
            provenance.evaluate_supply_chain_provenance(
                unsupported_request,
                self.build,
            )
        )
        self.assert_verdict(
            unsupported_request_result,
            provenance.UNSUPPORTED,
            "UNSUPPORTED_SCHEMA_VERSION:request",
        )

        cases = (
            (
                "unsupported_build",
                ("schema_version",),
                "unsupported.build.v1",
                provenance.UNSUPPORTED,
                "UNSUPPORTED_SCHEMA_VERSION:build",
            ),
            (
                "source_repository",
                ("source", "repository"),
                "https://example.invalid/other/repo",
                provenance.SOURCE_MISMATCH,
                "SOURCE_REPOSITORY_MISMATCH",
            ),
            (
                "source_commit",
                ("source", "commit"),
                "fedcba9876543210fedcba9876543210fedcba98",
                provenance.SOURCE_MISMATCH,
                "SOURCE_COMMIT_MISMATCH",
            ),
            (
                "builder_untrusted",
                ("builder", "trusted"),
                False,
                provenance.BUILDER_UNTRUSTED,
                "BUILDER_UNTRUSTED",
            ),
            (
                "builder_identity",
                ("builder", "id"),
                "builder:other:v1",
                provenance.BUILDER_UNTRUSTED,
                "BUILDER_ID_MISMATCH",
            ),
            (
                "workflow_identity",
                ("workflow", "id"),
                "workflow:other:v1",
                provenance.DIGEST_MISMATCH,
                "WORKFLOW_ID_MISMATCH",
            ),
        )

        for name, path, value, verdict, reason_code in cases:
            with self.subTest(name=name):
                result = self.evaluate_build_change(path, value)
                self.assert_verdict(result, verdict, reason_code)

    def test_material_artifact_and_evidence_boundaries(self) -> None:
        empty_materials = copy.deepcopy(self.build)
        empty_materials["materials"] = []
        empty_materials["provenance_digest"] = (
            provenance.provenance_digest(empty_materials)
        )
        self.assert_verdict(
            provenance.evaluate_supply_chain_provenance(
                self.request,
                empty_materials,
            ),
            provenance.INCOMPLETE,
            "EMPTY_REQUIRED_LIST:build.materials",
        )

        duplicate = copy.deepcopy(self.build)
        duplicate["materials"].append(
            copy.deepcopy(duplicate["materials"][0])
        )
        duplicate["provenance_digest"] = provenance.provenance_digest(
            duplicate
        )
        self.assert_verdict(
            provenance.evaluate_supply_chain_provenance(
                self.request,
                duplicate,
            ),
            provenance.MALFORMED,
            "DUPLICATE_MATERIAL:build.materials[1]",
        )

        conflict = copy.deepcopy(self.build)
        conflict["materials"].append(
            {
                "uri": conflict["materials"][0]["uri"],
                "digest": "sha256:" + "e" * 64,
            }
        )
        conflict["provenance_digest"] = provenance.provenance_digest(
            conflict
        )
        self.assert_verdict(
            provenance.evaluate_supply_chain_provenance(
                self.request,
                conflict,
            ),
            provenance.DIGEST_MISMATCH,
            "MATERIAL_DIGEST_CONFLICT:build.materials[1]",
        )

        cases = (
            (
                "artifact_name",
                ("artifact", "name"),
                "dist/other.tar.gz",
                "ARTIFACT_NAME_MISMATCH",
            ),
            (
                "artifact_digest",
                ("artifact", "digest"),
                "sha256:" + "d" * 64,
                "ARTIFACT_DIGEST_MISMATCH",
            ),
            (
                "source_evidence",
                ("source_evidence_digest",),
                "sha256:" + "f" * 64,
                "SOURCE_EVIDENCE_DIGEST_MISMATCH",
            ),
        )

        for name, path, value, reason_code in cases:
            with self.subTest(name=name):
                result = self.evaluate_build_change(path, value)
                self.assert_verdict(
                    result,
                    provenance.DIGEST_MISMATCH,
                    reason_code,
                )

    def test_provenance_digest_and_timestamp_boundaries(self) -> None:
        tampered = copy.deepcopy(self.build)
        tampered["artifact"]["digest"] = "sha256:" + "d" * 64
        self.assert_verdict(
            provenance.evaluate_supply_chain_provenance(
                self.request,
                tampered,
            ),
            provenance.DIGEST_MISMATCH,
            "PROVENANCE_DIGEST_MISMATCH",
        )

        invalid_timestamp = self.evaluate_build_change(
            ("started_at",),
            "2026-07-13T12:00:00+00:00",
        )
        self.assert_verdict(
            invalid_timestamp,
            provenance.MALFORMED,
            "INVALID_TIMESTAMP:build.started_at",
        )

        reversed_time = copy.deepcopy(self.build)
        reversed_time["started_at"] = "2026-07-13T12:00:02Z"
        reversed_time["finished_at"] = "2026-07-13T12:00:01Z"
        reversed_time["provenance_digest"] = (
            provenance.provenance_digest(reversed_time)
        )
        self.assert_verdict(
            provenance.evaluate_supply_chain_provenance(
                self.request,
                reversed_time,
            ),
            provenance.MALFORMED,
            "INVALID_TIMESTAMP_ORDER",
        )

    def test_runtime_excludes_network_and_subprocess_imports(self) -> None:
        tree = ast.parse(
            RUNTIME_PATH.read_text(encoding="utf-8"),
            filename=str(RUNTIME_PATH),
        )
        imported = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(
                    alias.name.split(".", 1)[0]
                    for alias in node.names
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
        self.assertTrue(
            forbidden.isdisjoint(imported),
            forbidden.intersection(imported),
        )


if __name__ == "__main__":
    unittest.main()
