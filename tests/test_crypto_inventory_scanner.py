import unittest
from pathlib import Path

from aapp.crypto_inventory_scanner import scan_crypto_inventory


FIXTURE = Path("tests/fixtures/crypto_inventory_scanner/sample_source.py")


class CryptoInventoryScannerTests(unittest.TestCase):
    def load_fixture(self):
        return FIXTURE.read_text(encoding="utf-8")

    def test_detects_crypto_inventory_findings(self):
        source = self.load_fixture()

        result = scan_crypto_inventory(source, source_ref="sample_source.py")

        self.assertEqual(result["scanner_verdict"], "INVENTORIED")
        self.assertGreaterEqual(result["finding_count"], 5)

        algorithms = {finding["algorithm"] for finding in result["findings"]}
        self.assertIn("SHA-256", algorithms)
        self.assertIn("RSA", algorithms)
        self.assertIn("AES", algorithms)
        self.assertIn("MD5", algorithms)
        self.assertIn("PRIVATE_KEY_MARKER", algorithms)

    def test_findings_are_reason_coded(self):
        result = scan_crypto_inventory(self.load_fixture())

        reason_codes = set(result["reason_codes"])

        self.assertIn("HASH_ALGORITHM_REFERENCE", reason_codes)
        self.assertIn("SIGNATURE_OR_PUBLIC_KEY_REFERENCE", reason_codes)
        self.assertIn("SYMMETRIC_ENCRYPTION_REFERENCE", reason_codes)
        self.assertIn("WEAK_OR_DEPRECATED_CRYPTO", reason_codes)
        self.assertIn("CERTIFICATE_OR_KEY_MARKER", reason_codes)

    def test_private_key_marker_does_not_export_raw_marker_text(self):
        result = scan_crypto_inventory(self.load_fixture())

        key_marker_findings = [
            finding for finding in result["findings"]
            if finding["algorithm"] == "PRIVATE_KEY_MARKER"
        ]

        self.assertTrue(key_marker_findings)
        self.assertTrue(
            all(finding["matched_text"] == "[KEY_MARKER]" for finding in key_marker_findings)
        )

    def test_unsupported_input_is_deterministic(self):
        result = scan_crypto_inventory(b"sha256")

        self.assertEqual(result["scanner_verdict"], "UNSUPPORTED")
        self.assertEqual(result["reason_codes"], ["INPUT_NOT_STRING"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["finding_count"], 0)

    def test_empty_input_is_malformed(self):
        result = scan_crypto_inventory("   ")

        self.assertEqual(result["scanner_verdict"], "MALFORMED")
        self.assertEqual(result["reason_codes"], ["EMPTY_INPUT"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["finding_count"], 0)

    def test_scan_is_deterministic(self):
        source = self.load_fixture()

        first = scan_crypto_inventory(source)
        second = scan_crypto_inventory(source)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
