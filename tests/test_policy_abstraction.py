import json
import unittest
from pathlib import Path

from aapp.policy_abstraction import abstract_policy


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "policy_abstraction"


class PolicyAbstractionTests(unittest.TestCase):
    def assert_fixture(self, name):
        fixture = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
        self.assertEqual(abstract_policy(fixture["input"]), fixture["expected"])

    def test_allow_read(self):
        self.assert_fixture("allow_read.json")

    def test_destructive_write(self):
        self.assert_fixture("destructive_write.json")

    def test_unknown_action(self):
        self.assert_fixture("unknown_action.json")


if __name__ == "__main__":
    unittest.main()
