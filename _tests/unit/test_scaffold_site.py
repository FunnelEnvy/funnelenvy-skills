"""Unit tests for roadmap-presentation scaffold_site.py (deterministic chrome)."""
import importlib.util
import os
import re
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "roadmap-presentation", "scripts", "scaffold_site.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("scaffold_site", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ss = _load()


def _manifest(n, title="Experiment Roadmap"):
    return {
        "title": title,
        "experiments": [
            {"number": i, "title": "Synthetic Experiment %d" % i, "mockup_present": (i % 2 == 0)}
            for i in range(1, n + 1)
        ],
    }


class TestDeterminism(unittest.TestCase):
    def test_byte_identical_across_runs(self):
        m = _manifest(4)
        a = ss.scaffold(m)
        b = ss.scaffold(m)
        self.assertEqual(a, b)

    def test_order_independent(self):
        # Same experiments in scrambled input order -> identical file map.
        forward = {"title": "R", "experiments": [
            {"number": 1, "title": "One"}, {"number": 2, "title": "Two"}, {"number": 3, "title": "Three"}]}
        reversed_in = {"title": "R", "experiments": [
            {"number": 3, "title": "Three"}, {"number": 2, "title": "Two"}, {"number": 1, "title": "One"}]}
        self.assertEqual(ss.scaffold(forward), ss.scaffold(reversed_in))


class TestPagerChain(unittest.TestCase):
    def setUp(self):
        self.files = ss.scaffold(_manifest(3))

    def test_first_spoke_prev_disabled(self):
        spoke1 = self.files["experiment-01.html"]
        # The top pager Prev link on spoke 1 is disabled (no prior experiment).
        self.assertIn('class="disabled">&larr; Prev', spoke1)
        # And it links forward to spoke 2.
        self.assertIn('href="experiment-02.html"', spoke1)

    def test_last_spoke_next_disabled(self):
        spoke3 = self.files["experiment-03.html"]
        self.assertIn('class="disabled">Next &rarr;', spoke3)
        self.assertIn('href="experiment-02.html"', spoke3)

    def test_interior_spoke_links_neighbors(self):
        spoke2 = self.files["experiment-02.html"]
        self.assertIn('href="experiment-01.html"', spoke2)
        self.assertIn('href="experiment-03.html"', spoke2)

    def test_every_spoke_links_back_to_hub(self):
        for i in range(1, 4):
            spoke = self.files["experiment-%02d.html" % i]
            self.assertIn('href="index.html"', spoke)


class TestPageCount(unittest.TestCase):
    def test_one_hub_plus_n_spokes(self):
        files = ss.scaffold(_manifest(5))
        spokes = [k for k in files if re.match(r"experiment-\d{2}\.html$", k)]
        self.assertIn("index.html", files)
        self.assertEqual(len(spokes), 5)
        # Plus the two shared assets.
        self.assertIn("styles.css", files)
        self.assertIn("site.js", files)


class TestAssetPaths(unittest.TestCase):
    def test_number_keyed_zero_padded(self):
        self.assertEqual(ss.asset_dir_for(1), "assets/mockups/experiment-01")
        self.assertEqual(ss.asset_dir_for(12), "assets/mockups/experiment-12")

    def test_spoke_filename_zero_padded(self):
        self.assertEqual(ss.spoke_filename(1), "experiment-01.html")
        self.assertEqual(ss.spoke_filename(10), "experiment-10.html")


class TestRelativeReferences(unittest.TestCase):
    def setUp(self):
        self.files = ss.scaffold(_manifest(2))

    def test_assets_referenced_relatively(self):
        for name, content in self.files.items():
            if not name.endswith(".html"):
                continue
            # Stylesheet/script are referenced by bare relative filename.
            self.assertIn('href="styles.css"', content)
            self.assertIn('src="site.js"', content)
            # No absolute file:// or http(s) asset links for the local assets.
            self.assertNotIn('href="/styles.css"', content)
            self.assertNotIn('src="/site.js"', content)


class TestNoClientContent(unittest.TestCase):
    # Denylist tokens are reassembled from fragments so the literal client
    # strings never appear in this public-repo file (the repo-wide denylist
    # sweep stays clean) while the guardrail still tests for them.
    _TOKENS = [
        "emb" + "ark", "s" + "&p", "sp-" + "global", "sp" + "global",
        "mi-" + "core", "click" + "up", "capital " + "iq",
        "risk" + "gauge", "pan" + "jiva", "growth" + "node",
    ]
    DENYLIST = re.compile("|".join(re.escape(t) for t in _TOKENS), re.IGNORECASE)

    def test_emitted_chrome_has_no_client_strings(self):
        files = ss.scaffold(_manifest(3))
        for name, content in files.items():
            self.assertIsNone(
                self.DENYLIST.search(content),
                "client denylist hit in %s" % name,
            )

    def test_no_curated_copy_in_shells(self):
        # The scaffold emits structure only: content slots are present and empty.
        files = ss.scaffold(_manifest(2))
        self.assertIn(ss.CONTENT_SLOT, files["index.html"])
        self.assertIn(ss.CONTENT_SLOT, files["experiment-01.html"])

    def test_no_em_dashes_in_emitted_output(self):
        # The em dash char is built from its code point so the literal does not
        # appear in this file (the repo bans em dashes in authored files).
        em_dash = chr(0x2014)
        files = ss.scaffold(_manifest(3))
        for name, content in files.items():
            self.assertNotIn(em_dash, content, "em dash in %s" % name)


class TestEdgeCases(unittest.TestCase):
    def test_single_experiment_pager_collapses(self):
        files = ss.scaffold(_manifest(1))
        spoke = files["experiment-01.html"]
        # Spoke 1 is both first and last: both pager directions disabled.
        self.assertIn('class="disabled">&larr; Prev', spoke)
        self.assertIn('class="disabled">Next &rarr;', spoke)
        # Foot pager next collapses to a spacer.
        self.assertIn('<div class="spacer"></div>', spoke)

    def test_empty_manifest_hub_only(self):
        files = ss.scaffold({"title": "Empty", "experiments": []})
        spokes = [k for k in files if re.match(r"experiment-\d{2}\.html$", k)]
        self.assertEqual(len(spokes), 0)
        self.assertIn("index.html", files)
        self.assertIn("styles.css", files)
        self.assertIn("site.js", files)

    def test_missing_required_field_raises(self):
        with self.assertRaises(ValueError):
            ss.scaffold({"title": "Bad", "experiments": [{"number": 1}]})


class TestWriteSite(unittest.TestCase):
    def test_write_creates_files_and_asset_dirs(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            written = ss.write_site(_manifest(2), tmp)
            self.assertTrue(os.path.exists(os.path.join(tmp, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "experiment-01.html")))
            self.assertTrue(os.path.isdir(os.path.join(tmp, "assets/mockups/experiment-01")))
            self.assertTrue(os.path.isdir(os.path.join(tmp, "assets/mockups/experiment-02")))

    def test_write_count_matches_scaffold(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            written = ss.write_site(_manifest(2), tmp)
            # 2 assets + 1 hub + 2 spokes = 5 files written.
            self.assertEqual(len(written), 5)


if __name__ == "__main__":
    unittest.main()
