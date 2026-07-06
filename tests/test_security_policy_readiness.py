from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SecurityPolicyReadinessTests(unittest.TestCase):
    def test_security_policy_exists_and_has_reporting_boundary(self):
        path = ROOT / "SECURITY.md"
        self.assertTrue(path.is_file(), "SECURITY.md missing")
        text = path.read_text(encoding="utf-8")

        required = [
            "Supported versions",
            "Do not report security vulnerabilities in public GitHub issues.",
            "AAPP evidence bundle",
            "Do not create fake advisories for drills.",
            "No live target testing without written scope.",
            "No exploit weaponization.",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_issue_template_blocks_public_security_reports(self):
        path = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md"
        self.assertTrue(path.is_file(), "bug_report.md missing")
        text = path.read_text(encoding="utf-8")

        required = [
            "Do not report security vulnerabilities here.",
            "Do not include:",
            "secrets",
            "tokens",
            "private keys",
            "exploit steps",
            "For security issues, use `SECURITY.md`.",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_issue_template_config_disables_blank_issues(self):
        path = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
        self.assertTrue(path.is_file(), "issue template config missing")
        text = path.read_text(encoding="utf-8")

        self.assertIn("blank_issues_enabled: false", text)
        self.assertIn("Security vulnerability report", text)
        self.assertIn("Do not disclose vulnerabilities in public issues.", text)


if __name__ == "__main__":
    unittest.main()
