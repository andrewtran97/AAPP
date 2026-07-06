import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "adapters" / "vscode-evidence-panel"


class VSCodeEvidencePanelTests(unittest.TestCase):
    def test_package_json_registers_command(self):
        pkg = json.loads((EXT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["name"], "agent-black-box-evidence-panel")
        self.assertIn("onCommand:agentBlackBox.openEvidencePanel", pkg["activationEvents"])

        commands = pkg["contributes"]["commands"]
        self.assertEqual(commands[0]["command"], "agentBlackBox.openEvidencePanel")

    def test_typescript_extension_reads_bundle_and_uses_webview(self):
        src = (EXT / "src" / "extension.ts").read_text(encoding="utf-8")
        self.assertIn("AGENT-BLACK-BOX-BUNDLE", src)
        self.assertIn("manifest.json", src)
        self.assertIn("session.report.md", src)
        self.assertIn("createWebviewPanel", src)
        self.assertIn("enableScripts: false", src)

    def test_no_builder_attribution_in_extension_files(self):
        files = [
            EXT / "package.json",
            EXT / "tsconfig.json",
            EXT / "src" / "extension.ts",
        ]
        forbidden = [
            "generated" + " with",
            "co-" + "authored-by:",
            "an" + "thropic",
            "cla" + "ude",
        ]

        for file in files:
            text = file.read_text(encoding="utf-8").lower()
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
