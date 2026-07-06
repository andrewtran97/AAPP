from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CompartmentedResearchWorkstationTests(unittest.TestCase):
    def test_required_workstation_artifacts_exist(self):
        required = [
            "docs/COMPARTMENTED_RESEARCH_WORKSTATION_SOP.md",
            "docs/WORKSTATION_COMPARTMENT_MAP.md",
            "templates/WORKSTATION_SESSION_LOG.md",
            "templates/WORKSTATION_INCIDENT_NOTE.md",
            "checklists/WORKSTATION_PREFLIGHT_CHECKLIST.md",
            "checklists/WORKSTATION_SHUTDOWN_CHECKLIST.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_sop_names_required_compartments(self):
        text = (ROOT / "docs/COMPARTMENTED_RESEARCH_WORKSTATION_SOP.md").read_text(encoding="utf-8")
        required = [
            "C0-HOST-BASELINE",
            "C1-SCOPE-CONTROL",
            "C2-RESEARCH-SANDBOX",
            "C3-AAPP-TRACE",
            "C4-EVIDENCE-BUNDLE",
            "C5-REDACTION",
            "C6-DISCLOSURE",
            "C7-PUBLISHABLE",
            "C8-KEY-REFERENCE",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_sop_has_operational_rules_not_brand_claims(self):
        text = (ROOT / "docs/COMPARTMENTED_RESEARCH_WORKSTATION_SOP.md").read_text(encoding="utf-8")
        self.assertIn("No scope, no active recording.", text)
        self.assertIn("No signed action trail, no trusted agent.", text)
        self.assertIn("No verified bundle, no disclosure package.", text)
        self.assertIn("not a claim of Qubes affiliation", text)
        self.assertIn("not a claim of", text)

    def test_preflight_blocks_overclaims(self):
        text = (ROOT / "checklists/WORKSTATION_PREFLIGHT_CHECKLIST.md").read_text(encoding="utf-8")
        forbidden_checks = [
            "no Qubes affiliation claim",
            "no government-grade claim",
            "no military-grade claim",
            "no post-quantum secure claim",
            "no compliance guarantee",
        ]
        for item in forbidden_checks:
            self.assertIn(item, text)


if __name__ == "__main__":
    unittest.main()
