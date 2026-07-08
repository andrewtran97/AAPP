import json
import unittest
from pathlib import Path

from aapp.deterministic_risk_signals import generate_risk_signals


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "deterministic_risk_signals"


class DeterministicRiskSignalsTests(unittest.TestCase):
    def assert_fixture(self, name):
        fixture = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
        self.assertEqual(generate_risk_signals(fixture["input"]), fixture["expected"])

    def test_repeated_deny(self):
        self.assert_fixture("repeated_deny.json")

    def test_risk_escalation(self):
        self.assert_fixture("risk_escalation.json")

    def test_data_egress_risk(self):
        self.assert_fixture("data_egress_risk.json")


if __name__ == "__main__":
    unittest.main()
