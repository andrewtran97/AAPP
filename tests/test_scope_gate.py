import json
import tempfile
import unittest
from pathlib import Path

from aapp.scope import ScopeError, load_scope, require_authorized_scope, scope_id

VALID_SCOPE = {
    "schema_version": "0.1.0",
    "scope_id": "scope-test",
    "authorization_status": "authorized",
    "allowed_actor_types": ["agent"],
    "allowed_tool_types": ["file_read", "shell"],
    "active_operations_enabled": True,
}

class ScopeGateTests(unittest.TestCase):
    def write_scope(self, value):
        temp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        json.dump(value, temp)
        temp.close()
        return Path(temp.name)

    def test_valid_scope_allows_authorized_operation(self):
        path = self.write_scope(VALID_SCOPE)
        scope = load_scope(path)
        require_authorized_scope(scope=scope, actor_type="agent", tool_type="file_read")
        self.assertEqual(scope_id(scope), "scope-test")

    def test_blocked_scope_blocks_operation(self):
        blocked = dict(VALID_SCOPE)
        blocked["authorization_status"] = "blocked"
        path = self.write_scope(blocked)
        scope = load_scope(path)
        with self.assertRaises(ScopeError):
            require_authorized_scope(scope=scope, actor_type="agent", tool_type="file_read")

    def test_disallowed_tool_type_blocks_operation(self):
        path = self.write_scope(VALID_SCOPE)
        scope = load_scope(path)
        with self.assertRaises(ScopeError):
            require_authorized_scope(scope=scope, actor_type="agent", tool_type="api_call")

    def test_missing_scope_file_blocks_operation(self):
        with self.assertRaises(ScopeError):
            load_scope("/tmp/aapp-missing-scope-file.json")

if __name__ == "__main__":
    unittest.main()
