import unittest

from aapp.crypto import attach_signature, verify_chain
from aapp.record import create_record

class SignatureVerificationTests(unittest.TestCase):
    def test_signature_verifies_with_correct_key(self):
        key = b"test-key"
        record = create_record(
            session_id="s1",
            parent_hash=None,
            actor_id="agent",
            actor_type="agent",
            tool_id="read_file",
            tool_type="file_read",
            scope_id="scope",
            authorization_status="authorized",
            policy_id="policy",
            decision="allow",
            reason="test",
            input_payload="README.md",
            output_payload="digest",
        )
        signed = attach_signature(record, key)
        ok, messages = verify_chain([signed], key)
        self.assertTrue(ok, messages)

    def test_signature_fails_with_wrong_key(self):
        record = create_record(
            session_id="s1",
            parent_hash=None,
            actor_id="agent",
            actor_type="agent",
            tool_id="read_file",
            tool_type="file_read",
            scope_id="scope",
            authorization_status="authorized",
            policy_id="policy",
            decision="allow",
            reason="test",
            input_payload="README.md",
            output_payload="digest",
        )
        signed = attach_signature(record, b"correct-key")
        ok, messages = verify_chain([signed], b"wrong-key")
        self.assertFalse(ok)
        self.assertIn("signature mismatch", messages[-1])

if __name__ == "__main__":
    unittest.main()
