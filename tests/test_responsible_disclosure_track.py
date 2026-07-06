from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ResponsibleDisclosureTrackTests(unittest.TestCase):
    def test_required_disclosure_artifacts_exist(self):
        required = [
            "docs/RESPONSIBLE_DISCLOSURE_TRACK.md",
            "templates/DISCLOSURE_EMAIL.md",
            "templates/PRIVATE_VULNERABILITY_REPORT.md",
            "templates/EMBARGO_CHECKLIST.md",
            "templates/PUBLICATION_CHECKLIST.md",
            "checklists/RESPONSIBLE_DISCLOSURE_CHECKLIST.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_disclosure_track_blocks_bad_publication_behavior(self):
        text = (ROOT / "docs/RESPONSIBLE_DISCLOSURE_TRACK.md").read_text(encoding="utf-8")
        required = [
            "No coercion",
            "No extortion",
            "No exploit weaponization",
            "No raw secrets",
            "Private disclosure before public release",
            "Public release requires redaction gate and disclosure gate",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_private_report_requires_evidence_artifacts(self):
        text = (ROOT / "templates/PRIVATE_VULNERABILITY_REPORT.md").read_text(encoding="utf-8")
        required = [
            "evidence.bundle.json",
            "hashes.txt",
            "verification_result.md",
            "replay_report.md",
            "redaction_log.md",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_publication_checklist_blocks_unsupported_release(self):
        text = (ROOT / "templates/PUBLICATION_CHECKLIST.md").read_text(encoding="utf-8")
        required = [
            "No raw secrets",
            "No private keys",
            "No exploit weaponization",
            "No unsupported security claims",
            "Limitations included",
        ]
        for item in required:
            self.assertIn(item, text)


if __name__ == "__main__":
    unittest.main()
