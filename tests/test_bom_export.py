import ast
import copy
import json
import unittest
from pathlib import Path

from aapp.bom_export import (
    CYCLONEDX_JSON,
    EXPORTED,
    INCOMPLETE,
    LICENSE_UNKNOWN,
    MALFORMED,
    PROVENANCE_MISSING,
    SPDX_JSON,
    UNSUPPORTED_FORMAT,
    bom_digest,
    evaluate_bom_export,
)


class BomExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture_path = Path(
            "tests/fixtures/bom_export/sample_inventory.json"
        )
        payload = json.loads(
            fixture_path.read_text(encoding="utf-8")
        )
        cls.base_request = payload["valid"]["request"]

    def request(self):
        return copy.deepcopy(self.base_request)

    def test_supported_formats_export_deterministically(self):
        cases = (
            (CYCLONEDX_JSON, "bomFormat", "CycloneDX"),
            (SPDX_JSON, "spdxVersion", "SPDX-2.3"),
        )

        for output_format, field, expected in cases:
            with self.subTest(output_format=output_format):
                request = self.request()
                request["output_format"] = output_format
                before = copy.deepcopy(request)

                first = evaluate_bom_export(request)
                second = evaluate_bom_export(request)

                self.assertEqual(EXPORTED, first["verdict"])
                self.assertEqual(["ALL_CHECKS_PASSED"], first["reason_codes"])
                self.assertTrue(all(first["checks"].values()))
                self.assertEqual(expected, first["bom"][field])
                self.assertEqual(
                    bom_digest(first["bom"]),
                    first["bom_digest"],
                )
                self.assertEqual(
                    request["source_evidence_digest"],
                    first["source_evidence_digest"],
                )
                self.assertEqual(
                    request["inventory"]["provenance_refs"],
                    first["provenance_refs"],
                )
                self.assertEqual(
                    request["inventory"]["evidence_refs"],
                    first["evidence_refs"],
                )
                self.assertEqual(first, second)
                self.assertEqual(before, request)

    def test_fail_closed_verdicts(self):
        missing_inventory = self.request()
        missing_inventory["inventory"].pop("components")

        unknown_license = self.request()
        unknown_license["inventory"]["components"][0][
            "license"
        ] = "NOASSERTION"

        missing_provenance = self.request()
        missing_provenance["inventory"].pop("provenance_refs")

        unsupported_format = self.request()
        unsupported_format["output_format"] = "XML"

        cases = (
            (missing_inventory, INCOMPLETE),
            (unknown_license, LICENSE_UNKNOWN),
            (missing_provenance, PROVENANCE_MISSING),
            (unsupported_format, UNSUPPORTED_FORMAT),
            (None, MALFORMED),
        )

        for request, expected_verdict in cases:
            with self.subTest(expected_verdict=expected_verdict):
                result = evaluate_bom_export(request)
                self.assertEqual(expected_verdict, result["verdict"])
                self.assertNotIn("bom", result)
                self.assertNotIn("bom_digest", result)

    def test_identity_dependency_and_digest_boundaries(self):
        duplicate = self.request()
        duplicate["inventory"]["components"][1]["id"] = "app"
        self.assertEqual(
            MALFORMED,
            evaluate_bom_export(duplicate)["verdict"],
        )

        unknown_dependency = self.request()
        unknown_dependency["inventory"]["dependencies"][0][
            "to"
        ] = "missing-component"
        self.assertEqual(
            INCOMPLETE,
            evaluate_bom_export(unknown_dependency)["verdict"],
        )

        invalid_digest = self.request()
        invalid_digest["source_evidence_digest"] = "sha256:invalid"
        self.assertEqual(
            MALFORMED,
            evaluate_bom_export(invalid_digest)["verdict"],
        )

        invalid_refs = self.request()
        invalid_refs["inventory"]["evidence_refs"] = "not-a-list"
        self.assertEqual(
            MALFORMED,
            evaluate_bom_export(invalid_refs)["verdict"],
        )

    def test_input_is_never_mutated(self):
        request = self.request()
        before = copy.deepcopy(request)

        evaluate_bom_export(request)

        self.assertEqual(before, request)

    def test_runtime_excludes_network_and_subprocess_imports(self):
        runtime_path = Path("aapp/bom_export.py")
        tree = ast.parse(
            runtime_path.read_text(encoding="utf-8"),
            filename=str(runtime_path),
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

        self.assertFalse(
            imported
            & {
                "httpx",
                "requests",
                "socket",
                "subprocess",
                "urllib",
            }
        )


if __name__ == "__main__":
    unittest.main()
