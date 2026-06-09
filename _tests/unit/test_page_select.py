"""Unit tests for live-capture page_select.py (Section 8 leverage selection)."""
import importlib.util
import os
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "live-capture", "scripts", "page_select.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("page_select", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ps = _load()


class TestComputeLeverage(unittest.TestCase):
    def test_traffic_normalization(self):
        page = {"sessions": 500}
        self.assertAlmostEqual(ps.compute_leverage(page, 1000, None), 0.35 * 0.5, places=4)

    def test_conversion_gap_below_benchmark(self):
        # cvr 0.4 vs benchmark 2.0 -> gap (2.0-0.4)/2.0 = 0.8
        page = {"sessions": 0, "cvr": 0.4}
        self.assertAlmostEqual(ps.compute_leverage(page, 1000, 2.0), 0.30 * 0.8, places=4)

    def test_conversion_gap_above_benchmark_clamps_to_zero(self):
        # A high-converting page must not score as leverage.
        page = {"sessions": 0, "cvr": 3.0}
        self.assertEqual(ps.compute_leverage(page, 1000, 2.0), 0.0)

    def test_missing_cvr_contributes_zero(self):
        page = {"sessions": 0, "cvr": None}
        self.assertEqual(ps.compute_leverage(page, 1000, 2.0), 0.0)

    def test_bounce_and_device_gap(self):
        page = {"sessions": 0, "bounce": 50.0, "mobile_bounce": 60.0, "desktop_bounce": 40.0}
        expected = 0.20 * 0.5 + 0.15 * 0.2
        self.assertAlmostEqual(ps.compute_leverage(page, 1000, None), round(expected, 4), places=4)


class TestSelect(unittest.TestCase):
    def _metrics(self):
        return {
            "benchmark_cvr": 2.0,
            "pages": [
                {"path": "/", "sessions": 10000, "cvr": 1.5, "bounce": 40.0, "lane": "conversion"},
                {"path": "/pricing", "sessions": 5600, "cvr": 0.4, "bounce": 51.0,
                 "mobile_bounce": 58.0, "desktop_bounce": 44.0, "lane": "conversion"},
                {"path": "/solutions", "sessions": 3000, "cvr": 0.8, "bounce": 48.0, "lane": "conversion"},
                {"path": "/blog/a", "sessions": 4000, "cvr": None, "bounce": 62.0, "lane": "content"},
                {"path": "/blog/b", "sessions": 1500, "cvr": None, "bounce": 70.0, "lane": "content"},
            ],
        }

    def test_homepage_always_first(self):
        sel = ps.select(self._metrics())
        self.assertEqual(sel[0]["path"], "/")
        self.assertEqual(sel[0]["always_capture"], "homepage")

    def test_positive_control_injected_when_distinct_from_homepage(self):
        # Homepage has a high bounce; /solutions is the healthiest (lowest bounce) page,
        # so it should be injected as the positive control.
        m = {
            "benchmark_cvr": 2.0,
            "pages": [
                {"path": "/", "sessions": 10000, "cvr": 1.0, "bounce": 65.0, "lane": "conversion"},
                {"path": "/solutions", "sessions": 3000, "cvr": 1.8, "bounce": 30.0, "lane": "conversion"},
                {"path": "/pricing", "sessions": 5600, "cvr": 0.4, "bounce": 51.0, "lane": "conversion"},
            ],
        }
        sel = ps.select(m)
        flags = {e["path"]: e["always_capture"] for e in sel}
        self.assertEqual(flags["/"], "homepage")
        self.assertEqual(flags["/solutions"], "positive_control")

    def test_positive_control_collapses_into_homepage(self):
        # When the healthiest page IS the homepage, no separate positive-control entry exists;
        # the homepage keeps its homepage flag.
        sel = ps.select(self._metrics())  # "/" has the lowest bounce (40.0)
        home = next(e for e in sel if e["path"] == "/")
        self.assertEqual(home["always_capture"], "homepage")
        self.assertNotIn("positive_control", [e["always_capture"] for e in sel])

    def test_two_lane_split_and_content_by_sessions(self):
        sel = ps.select(self._metrics(), conversion_slots=8, content_slots=1)
        content = [e for e in sel if e["lane"] == "content"]
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["path"], "/blog/a")  # higher sessions than /blog/b

    def test_conversion_slots_respected(self):
        sel = ps.select(self._metrics(), conversion_slots=1, content_slots=0)
        conv = [e for e in sel if e["lane"] == "conversion"]
        # Homepage is always present; with 1 conversion slot the top-leverage conversion page
        # (/pricing) is included. No duplicate paths.
        paths = [e["path"] for e in sel]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("/", paths)
        self.assertIn("/pricing", paths)

    def test_no_duplicates(self):
        sel = ps.select(self._metrics())
        paths = [e["path"] for e in sel]
        self.assertEqual(len(paths), len(set(paths)))

    def test_homepage_synthesized_when_absent(self):
        m = {"benchmark_cvr": 2.0, "pages": [
            {"path": "/pricing", "sessions": 100, "cvr": 0.5, "bounce": 50.0, "lane": "conversion"}]}
        sel = ps.select(m)
        self.assertEqual(sel[0]["path"], "/")
        self.assertEqual(sel[0]["always_capture"], "homepage")


if __name__ == "__main__":
    unittest.main()
