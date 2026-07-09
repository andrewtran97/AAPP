import json
import unittest
from pathlib import Path

from aapp.policy_backend_adapter import adapt_policy_backend_request


FIXTURE = Path("tests/fixtures/policy_backend_adapter/sample_policy_request.json")


class PolicyBackendAdapterTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_local_static_backend_preserves_policy_input_digest(self):
        request = self.load_fixture()

        result = adapt_policy_backend_request(request, "local_static")

        self.assertEqual(result["adapter_verdict"], "ADAPTED")
        self.assertEqual(result["backend"], "local_static")
        self.assertEqual(result["policy_input_digest"], request["policy_input_digest"])
        self.assertEqual(
            result["decision"]["policy_input_digest"],
            request["policy_input_digest"],
        )
        self.assertEqual(result["decision"]["verdict"], "ALLOW")

    def test_opa_json_shape_backend_preserves_policy_input_digest(self):
        request = self.load_fixture()

        result = adapt_policy_backend_request(request, "opa_json_shape")

        self.assertEqual(result["adapter_verdict"], "ADAPTED")
        self.assertEqual(result["backend"], "opa_json_shape")
        self.assertEqual(
            result["decision"]["result"]["policy_input_digest"],
            request["policy_input_digest"],
        )
        self.assertTrue(result["decision"]["result"]["allow"])
        self.assertFalse(result["decision"]["result"]["deny"])

    def test_require_approval_maps_to_opa_shape(self):
        request = self.load_fixture()
        request["requested_verdict"] = "REQUIRE_APPROVAL"
        request["obligations"] = ["human_approval"]

        result = adapt_policy_backend_request(request, "opa_json_shape")

        self.assertEqual(result["adapter_verdict"], "ADAPTED")
        self.assertFalse(result["decision"]["result"]["allow"])
        self.assertTrue(result["decision"]["result"]["require_approval"])
        self.assertIn("human_approval", result["decision"]["result"]["obligations"])

    def test_unsupported_backend_is_deterministic(self):
        request = self.load_fixture()

        result = adapt_policy_backend_request(request, "live_opa")

        self.assertEqual(result["adapter_verdict"], "UNSUPPORTED")
        self.assertEqual(result["backend"], "live_opa")
        self.assertEqual(result["reason_codes"], ["UNSUPPORTED_BACKEND"])
        self.assertIsNone(result["decision"])

    def test_missing_required_field_is_malformed(self):
        request = self.load_fixture()
        del request["policy_input_digest"]

        result = adapt_policy_backend_request(request, "local_static")

        self.assertEqual(result["adapter_verdict"], "MALFORMED")
        self.assertEqual(result["backend"], "local_static")
        self.assertEqual(result["missing_fields"], ["policy_input_digest"])
        self.assertIn("MISSING_REQUIRED_FIELD", result["reason_codes"])
        self.assertIsNone(result["decision"])

    def test_unsupported_requested_verdict_defaults_to_deny(self):
        request = self.load_fixture()
        request["requested_verdict"] = "MAYBE"

        result = adapt_policy_backend_request(request, "local_static")

        self.assertEqual(result["adapter_verdict"], "ADAPTED")
        self.assertEqual(result["decision"]["verdict"], "DENY")
        self.assertIn(
            "UNSUPPORTED_REQUESTED_VERDICT_DEFAULT_DENY",
            result["reason_codes"],
        )


if __name__ == "__main__":
    unittest.main()
