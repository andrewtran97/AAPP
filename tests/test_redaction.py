import unittest

from aapp.redaction import contains_secret_like_value, redact_text

class RedactionTests(unittest.TestCase):
    def test_secret_like_value_is_redacted(self):
        redacted, changed = redact_text("api_key=sk-1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertTrue(changed)
        self.assertNotIn("sk-1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", redacted)
        self.assertIn("<REDACTED>", redacted)

    def test_contains_secret_like_value(self):
        self.assertTrue(contains_secret_like_value("token=ghp_1234567890ABCDEFGHIJKLMNOPQRST"))
        self.assertFalse(contains_secret_like_value("normal safe text"))

if __name__ == "__main__":
    unittest.main()
