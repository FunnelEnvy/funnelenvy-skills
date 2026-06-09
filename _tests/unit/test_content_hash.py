"""Unit tests for live-capture content_hash.py.

The live-capture scripts live in skills/live-capture/scripts/, so the module is
loaded via importlib rather than a package import.
"""
import importlib.util
import os
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "live-capture", "scripts", "content_hash.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("content_hash", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


content_hash = _load()


class TestContentHash(unittest.TestCase):
    def test_deterministic(self):
        a = content_hash.content_hash("Welcome", "Features\nPricing\nFAQ")
        b = content_hash.content_hash("Welcome", "Features\nPricing\nFAQ")
        self.assertEqual(a, b)

    def test_hash_length(self):
        h = content_hash.content_hash("H1", "skeleton")
        self.assertEqual(len(h), content_hash.HASH_LEN)
        self.assertTrue(all(c in "0123456789abcdef" for c in h))

    def test_whitespace_normalized(self):
        base = content_hash.content_hash("Welcome", "Features\nPricing")
        # Leading/trailing whitespace, blank lines, CRLF must not change the hash.
        noisy = content_hash.content_hash("  Welcome  ", "\r\n  Features  \r\n\r\nPricing\n\n")
        self.assertEqual(base, noisy)

    def test_h1_change_changes_hash(self):
        a = content_hash.content_hash("Welcome", "Features\nPricing")
        b = content_hash.content_hash("Welcome Home", "Features\nPricing")
        self.assertNotEqual(a, b)

    def test_skeleton_change_changes_hash(self):
        a = content_hash.content_hash("Welcome", "Features\nPricing")
        b = content_hash.content_hash("Welcome", "Features\nPricing\nFAQ")
        self.assertNotEqual(a, b)

    def test_line_move_between_inputs_changes_hash(self):
        # The record separator means moving a line from skeleton into h1 differs.
        a = content_hash.content_hash("Welcome", "Features\nPricing")
        b = content_hash.content_hash("Welcome\nFeatures", "Pricing")
        self.assertNotEqual(a, b)

    def test_empty_inputs_stable(self):
        self.assertEqual(content_hash.content_hash("", ""), content_hash.content_hash(None, None))


if __name__ == "__main__":
    unittest.main()
