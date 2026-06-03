"""Unit tests for aa_audit.py report parsing — string/NaN cell coercion.

The aa-audit skill directory is hyphenated (skills/aa-audit/), so the module
is loaded via importlib rather than a package import.
"""
import importlib.util
import os
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "aa-audit", "aa_audit.py"
)


def _load_aa_audit():
    spec = importlib.util.spec_from_file_location("aa_audit", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


aa_audit = _load_aa_audit()


class TestCoerceCell(unittest.TestCase):
    def test_numeric_passthrough(self):
        self.assertEqual(aa_audit._coerce_cell("visits", 42), 42.0)
        self.assertEqual(aa_audit._coerce_cell("visits", 0.5), 0.5)

    def test_numeric_string(self):
        self.assertEqual(aa_audit._coerce_cell("visits", "42"), 42.0)
        self.assertEqual(aa_audit._coerce_cell("bouncerate", "0.5"), 0.5)

    def test_nan_string(self):
        self.assertEqual(aa_audit._coerce_cell("bouncerate", "NaN"), 0.0)

    def test_nan_float(self):
        self.assertEqual(aa_audit._coerce_cell("bouncerate", float("nan")), 0.0)

    def test_garbage_string(self):
        self.assertEqual(aa_audit._coerce_cell("visits", "not-a-number"), 0.0)

    def test_none(self):
        self.assertEqual(aa_audit._coerce_cell("visits", None), 0.0)


class TestNormalizeValue(unittest.TestCase):
    def test_bouncerate_fraction_normalized(self):
        self.assertEqual(aa_audit._normalize_value("bouncerate", 0.314), 31.4)

    def test_bouncerate_string_fraction_normalized(self):
        self.assertEqual(aa_audit._normalize_value("bouncerate", "0.314"), 31.4)

    def test_bouncerate_nan_string_no_crash(self):
        # The live 2026-06-03 crash case: string cell hit the bounds check.
        self.assertEqual(aa_audit._normalize_value("bouncerate", "NaN"), 0.0)

    def test_non_bouncerate_unchanged(self):
        self.assertEqual(aa_audit._normalize_value("visits", 0.5), 0.5)


def _response(rows, totals):
    return {
        "rows": [
            {"value": v, "itemId": str(i), "data": data}
            for i, (v, data) in enumerate(rows)
        ],
        "summaryData": {"totals": totals},
    }


class TestParseReportRows(unittest.TestCase):
    METRICS = ["visits", "bouncerate"]

    def test_string_and_nan_cells(self):
        resp = _response(
            rows=[("page-a", [100, "NaN"]), ("page-b", ["250", 0.5])],
            totals=[350, 0.4],
        )
        rows = aa_audit.parse_report_rows(resp, self.METRICS)
        self.assertEqual(rows[0]["visits"], 100)
        self.assertEqual(rows[0]["bouncerate"], 0.0)
        self.assertEqual(rows[1]["visits"], 250.0)
        self.assertEqual(rows[1]["bouncerate"], 50.0)

    def test_short_data_row_defaults_zero(self):
        resp = _response(rows=[("page-a", [100])], totals=[100, 0])
        rows = aa_audit.parse_report_rows(resp, self.METRICS)
        self.assertEqual(rows[0]["bouncerate"], 0.0)


class TestExtractSummary(unittest.TestCase):
    def test_string_totals_coerced(self):
        resp = _response(rows=[], totals=["1000", "NaN"])
        summary = aa_audit.extract_summary(resp, ["visits", "bouncerate"])
        self.assertEqual(summary["visits"], 1000.0)
        self.assertEqual(summary["bouncerate"], 0.0)


if __name__ == "__main__":
    unittest.main()
