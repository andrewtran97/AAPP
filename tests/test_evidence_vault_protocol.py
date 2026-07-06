from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class EvidenceVaultProtocolTests(unittest.TestCase):
    def test_required_vault_docs_exist(self):
        required = [
            "docs/EVIDENCE_VAULT_PROTOCOL.md",
            "templates/EVIDENCE_VAULT_README.md",
            "templates/VAULT_AUDIT_LOG.md",
            "templates/REDACTION_LOG.md",
            "templates/DISCLOSURE_TIMELINE.md",
            "checklists/EVIDENCE_VAULT_CHECKLIST.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_vault_protocol_names_required_compartments(self):
        text = (ROOT / "docs/EVIDENCE_VAULT_PROTOCOL.md").read_text(encoding="utf-8")
        compartments = [
            "00-INBOX",
            "01-SCOPE",
            "02-TRACE",
            "03-BUNDLES",
            "04-REDACTION",
            "05-DISCLOSURE",
            "06-PUBLISHABLE",
            "07-KEYS-REFERENCES-ONLY",
            "08-AUDIT-LOG",
        ]
        for item in compartments:
            self.assertIn(item, text)

    def test_vault_protocol_blocks_public_claim_overreach(self):
        text = (ROOT / "docs/EVIDENCE_VAULT_PROTOCOL.md").read_text(encoding="utf-8")
        forbidden_claims = [
            "post-quantum secure",
            "Qubes-certified",
            "government-grade",
            "military-grade",
            "unbreakable",
            "compliance guaranteed",
            "AI safety solved",
        ]
        for claim in forbidden_claims:
            self.assertIn(claim, text)

    def test_public_material_requires_redaction_and_disclosure_gate(self):
        text = (ROOT / "docs/EVIDENCE_VAULT_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("Before anything moves to 06-PUBLISHABLE", text)
        self.assertIn("Before contacting a maintainer", text)
        self.assertIn("No raw secrets in reports", text)


if __name__ == "__main__":
    unittest.main()
