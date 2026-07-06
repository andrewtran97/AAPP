import copy
import unittest

from aapp.crypto import attach_signature, verify_chain
from aapp.record import create_record

def build_chain():
    key = b"chain-key"
    records = []
    parent_hash = None

    for tool_id in ["read_file", "edit_file", "run_tests"]:
        record = create_record(
            session_id="s1",
            parent_hash=parent_hash,
            actor_id="agent",
            actor_type="agent",
            tool_id=tool_id,
            tool_type="file_read" if tool_id == "read_file" else "artifact",
            scope_id="scope",
            authorization_status="authorized",
            policy_id="policy",
            decision="allow",
            reason="test",
            input_payload=tool_id,
            output_payload="ok",
        )
        signed = attach_signature(record, key)
        records.append(signed)
        parent_hash = signed["record_hash"]

    return records, key

class RecordHashChainTests(unittest.TestCase):
    def test_hash_chain_passes(self):
        records, key = build_chain()
        ok, messages = verify_chain(records, key)
        self.assertTrue(ok, messages)

    def test_tampering_fails(self):
        records, key = build_chain()
        tampered = copy.deepcopy(records)
        tampered[1]["policy"]["decision"] = "block"
        ok, messages = verify_chain(tampered, key)
        self.assertFalse(ok)
        self.assertIn("record_hash mismatch", messages[-1])

    def test_parent_hash_break_fails(self):
        records, key = build_chain()
        tampered = copy.deepcopy(records)
        tampered[2]["parent_hash"] = "sha384:bad"
        ok, messages = verify_chain(tampered, key)
        self.assertFalse(ok)
        self.assertIn("parent_hash mismatch", messages[-1])

if __name__ == "__main__":
    unittest.main()
