"""Unit tests for aa_audit.py report parsing — string/NaN cell coercion.

The aa-audit skill directory is hyphenated (skills/aa-audit/), so the module
is loaded via importlib rather than a package import.
"""
import importlib.util
import os
import unittest
from unittest import mock

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


# ============================================================================
# Interaction & Measurement-Integrity Capture (chg 2026-06-10)
# ============================================================================

class _FakeResponse:
    """Minimal stand-in for a requests.Response."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._payload


class _FakePost:
    """Records every requests.post call and returns canned report rows.

    Token requests (TOKEN_URL) get a token payload; report requests record the
    JSON body and return the next canned response (or an empty report).
    """

    def __init__(self, report_payload=None):
        self.calls = []  # list of (url, json_body)
        self._report_payload = report_payload or {"rows": [], "summaryData": {"totals": []}}

    def __call__(self, url, **kwargs):
        body = kwargs.get("json")
        self.calls.append((url, body))
        if url == aa_audit.AAClient.TOKEN_URL:
            return _FakeResponse({"access_token": "fake-token"})
        return _FakeResponse(self._report_payload)

    @property
    def report_bodies(self):
        return [b for (u, b) in self.calls if u != aa_audit.AAClient.TOKEN_URL]


def _client(config=None, env=None):
    """Build an AAClient with credentials stubbed in via env."""
    config = config or {"company_id": "co", "report_suite": "rs"}
    base_env = {
        "ADOBE_AA_CLIENT_ID": "cid",
        "ADOBE_AA_CLIENT_SECRET": "secret",
        "ADOBE_AA_ORG_ID": "org",
    }
    if env:
        base_env.update(env)
    with mock.patch.dict(os.environ, base_env, clear=False):
        return aa_audit.AAClient(config)


class TestResolveScope(unittest.TestCase):
    def test_segment_id_takes_precedence(self):
        cfg = {"scope": {"segment_id": "seg123", "prefixes": ["/store"]}}
        segs, search = aa_audit.resolve_scope(cfg)
        self.assertEqual(segs, ["seg123"])
        self.assertIsNone(search)

    def test_prefixes_build_single_broad_token_search(self):
        cfg = {"scope": {"prefixes": ["/store"], "prefix_dimension": "variables/entrypage"}}
        segs, search = aa_audit.resolve_scope(cfg)
        self.assertIsNone(segs)
        self.assertIsNotNone(search)
        # Single broad token only -- no colon contains, no multi-token clause.
        self.assertNotIn(":", search)
        self.assertIn("/store", search)

    def test_empty_scope_returns_none_none(self):
        self.assertEqual(aa_audit.resolve_scope({}), (None, None))
        self.assertEqual(
            aa_audit.resolve_scope({"scope": {"segment_id": "", "prefixes": []}}),
            (None, None),
        )


class TestRunReportPayloadScoping(unittest.TestCase):
    # Golden payload for an unscoped report -- byte-identical to pre-change shape.
    GOLDEN = {
        "rsid": "rs",
        "globalFilters": [{"type": "dateRange", "dateRange": "2026-01-01/2026-02-01"}],
        "metricContainer": {"metrics": [{"id": "metrics/visits", "columnId": "col_0"}]},
        "dimension": "variables/page",
        "settings": {"limit": 50, "page": 0, "nonesBehavior": "return-nones"},
    }

    def test_no_scope_payload_is_golden(self):
        fake = _FakePost()
        client = _client()
        with mock.patch.object(aa_audit, "requests", mock.Mock(post=fake)):
            client.run_report("variables/page", ["metrics/visits"], "2026-01-01/2026-02-01")
        self.assertEqual(fake.report_bodies[0], self.GOLDEN)
        # No segment filter, no search key when scope unset.
        body = fake.report_bodies[0]
        self.assertNotIn("search", body)
        self.assertEqual(len(body["globalFilters"]), 1)

    def test_default_segment_merged_into_every_report(self):
        fake = _FakePost()
        client = _client()
        client.default_segment_ids = ["seg123"]
        with mock.patch.object(aa_audit, "requests", mock.Mock(post=fake)):
            client.run_report("variables/page", ["metrics/visits"], "2026-01-01/2026-02-01")
        body = fake.report_bodies[0]
        seg_filters = [f for f in body["globalFilters"] if f["type"] == "segment"]
        self.assertEqual(seg_filters, [{"type": "segment", "segmentId": "seg123"}])

    def test_default_search_merged_into_every_report(self):
        fake = _FakePost()
        client = _client()
        client.default_search = "( CONTAINS '/store' )"
        with mock.patch.object(aa_audit, "requests", mock.Mock(post=fake)):
            client.run_report("variables/page", ["metrics/visits"], "2026-01-01/2026-02-01")
        body = fake.report_bodies[0]
        self.assertEqual(body["search"], {"clause": "( CONTAINS '/store' )"})

    def test_explicit_arg_overrides_default(self):
        fake = _FakePost()
        client = _client()
        client.default_segment_ids = ["seg-default"]
        with mock.patch.object(aa_audit, "requests", mock.Mock(post=fake)):
            client.run_report("variables/page", ["metrics/visits"], "2026-01-01/2026-02-01",
                              segment_ids=["seg-explicit"])
        body = fake.report_bodies[0]
        seg_filters = [f for f in body["globalFilters"] if f["type"] == "segment"]
        self.assertEqual(seg_filters, [{"type": "segment", "segmentId": "seg-explicit"}])


class TestResolveInteractionDimensions(unittest.TestCase):
    def test_default_three_dimension_list(self):
        dims = aa_audit.resolve_interaction_dimensions({"interaction_dimensions": [
            "variables/customlink", "variables/clickmaplink", "variables/clickmappage"]})
        self.assertEqual(len(dims), 3)
        self.assertIn("variables/customlink", dims)

    def test_legacy_link_text_fallback(self):
        dims = aa_audit.resolve_interaction_dimensions(
            {"dimensions": {"link_text": "variables/evar200"}})
        self.assertEqual(dims, ["variables/evar200"])

    def test_none_when_neither_configured(self):
        self.assertIsNone(aa_audit.resolve_interaction_dimensions({}))

    def test_array_takes_precedence_over_legacy(self):
        dims = aa_audit.resolve_interaction_dimensions({
            "interaction_dimensions": ["variables/customlink"],
            "dimensions": {"link_text": "variables/evar200"},
        })
        self.assertEqual(dims, ["variables/customlink"])


class TestFetchElementInteractions(unittest.TestCase):
    def test_one_query_per_dimension_broad_search_untruncated_limit(self):
        fake = _FakePost()
        client = _client()
        client.default_search = "( CONTAINS '/store' )"
        config = {"interaction_dimensions": ["variables/customlink", "variables/clickmaplink"]}
        with mock.patch.object(aa_audit, "requests", mock.Mock(post=fake)):
            result = aa_audit.fetch_element_interactions(client, config, "2026-01-01/2026-02-01")
        bodies = fake.report_bodies
        self.assertEqual(len(bodies), 2)  # one per dimension
        for body in bodies:
            self.assertGreaterEqual(body["settings"]["limit"], 400)  # untruncated
            # Broad single-token scope search threaded in (no colon contains).
            self.assertEqual(body["search"], {"clause": "( CONTAINS '/store' )"})
        self.assertEqual(set(result["dimensions"]),
                         {"variables/customlink", "variables/clickmaplink"})

    def test_none_when_no_dimensions(self):
        client = _client()
        self.assertIsNone(
            aa_audit.fetch_element_interactions(client, {}, "2026-01-01/2026-02-01"))


class TestFetchEventLiveness(unittest.TestCase):
    def test_zero_count_event_is_dead(self):
        # fetch_event_liveness requests only the event metrics, in config order:
        # totals[0] = event3 (dead, 0), totals[1] = event47 (live, 12).
        payload = {
            "rows": [],
            "summaryData": {"totals": [0, 12]},
        }
        fake = _FakePost(report_payload=payload)
        client = _client()
        config = {
            "conversion_events": [{"id": "metrics/event3", "name": "Form Complete"}],
            "engagement_events": [{"id": "metrics/event47", "name": "Click Event"}],
        }
        with mock.patch.object(aa_audit, "requests", mock.Mock(post=fake)):
            liveness = aa_audit.fetch_event_liveness(client, config, "2026-01-01/2026-02-01")
        by_event = {e["event"]: e for e in liveness}
        self.assertEqual(by_event["metrics/event3"]["status"], "dead")
        self.assertEqual(by_event["metrics/event47"]["status"], "live")

    def test_empty_when_no_events(self):
        client = _client()
        self.assertEqual(
            aa_audit.fetch_event_liveness(client, {}, "2026-01-01/2026-02-01"), [])


class TestClassifyRegression(unittest.TestCase):
    def test_present_then_zero_is_dark(self):
        self.assertEqual(aa_audit.classify_regression(0, 500), "dark")

    def test_zero_then_present_is_spiked(self):
        self.assertEqual(aa_audit.classify_regression(500, 0), "spiked")

    def test_large_jump_is_spiked(self):
        self.assertEqual(aa_audit.classify_regression(1000, 100), "spiked")

    def test_dead_in_both(self):
        self.assertEqual(aa_audit.classify_regression(0, 0), "dead")

    def test_stable_is_live(self):
        self.assertEqual(aa_audit.classify_regression(110, 100), "live")


class TestFrictionTokenMatch(unittest.TestCase):
    """Friction-token matching is script-owned (aa_audit.is_friction_token) and
    shared with the aa-audit SKILL's friction pass; these pin the production
    helper, not a test-local copy, so the token set cannot silently drift."""

    def test_friction_values_flagged(self):
        for v in ["Required field error", "INVALID email", "Submit failed", "Access denied"]:
            self.assertTrue(aa_audit.is_friction_token(v), v)

    def test_non_friction_values_not_flagged(self):
        for v in ["Request Demo", "Pricing", "Contact Sales"]:
            self.assertFalse(aa_audit.is_friction_token(v), v)

    def test_none_and_empty_safe(self):
        self.assertFalse(aa_audit.is_friction_token(""))
        self.assertFalse(aa_audit.is_friction_token(None))

    def test_fetch_element_interactions_tags_friction_rows(self):
        """fetch_element_interactions tags each row with a friction flag from the
        production helper, so the script (not just the agent) owns the signal."""
        from unittest import mock

        config = {"interaction_dimensions": ["variables/customlink"]}
        client = mock.Mock()
        client.run_report.return_value = {
            "rows": [
                {"value": "expert error required choice", "itemId": "1", "data": [10]},
                {"value": "Add to cart", "itemId": "2", "data": [20]},
            ],
            "summaryData": {"totals": [30]},
        }
        result = aa_audit.fetch_element_interactions(client, config, "range")
        rows = result["by_dimension"]["variables/customlink"]["rows"]
        flags = {r["value"]: r["friction"] for r in rows}
        self.assertTrue(flags["expert error required choice"])
        self.assertFalse(flags["Add to cart"])


if __name__ == "__main__":
    unittest.main()
