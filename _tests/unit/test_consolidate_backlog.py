"""Unit tests for hypothesis-generator consolidate_backlog.py (card consolidation, sizing, keys, rank).

Fixtures are synthetic and in-memory: card lists and a Decision Posture table string for
a fictional "Acme". Case design: hypothesis-generator-opportunity-backlog-rebuild (R2-R8).
"""
import importlib.util
import os
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "hypothesis-generator", "scripts",
    "consolidate_backlog.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("consolidate_backlog", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cb = _load()

POSTURE_TABLE = """# Skill

## Decision Posture

| Constant | Default | Cited by |
|---|---|---|
| Significance (two-sided confidence) | 0.90: a result counts at p < 0.10. Two-sided only. | sizing |
| Power | 0.80 | sizing |
| Multiplier M = 2(z_sig + z_power)^2 | 12.37 | sizing |
| Relative MDE | 0.20 | sizing |
| Maximum A/B read window | 26 weeks | sizing |
| Hard gates | 100 conversions per variant; 7-day minimum | sizing |

## Next Section
"""

POSTURE = cb.parse_posture(POSTURE_TABLE)


def card(**overrides):
    """Return a valid tactical card with `overrides` applied."""
    base = {
        "lens": "surface",
        "altitude": "tactical",
        "title": "Pricing proof strip",
        "surfaces": ["/pricing"],
        "mechanism_key": "proof-near-cta",
        "mechanism": "Proof beside the CTA lowers perceived risk.",
        "evidence": ["performance profile, pricing page row"],
    }
    base.update(overrides)
    return base


def strategic_card(**overrides):
    """Return a valid strategic card with `overrides` applied."""
    base = card(lens="strategic", altitude="strategic", title="Nurture program",
                surfaces=["nurture program"], mechanism_key="lifecycle-nurture",
                mechanism="A nurture track recovers stalled leads.", lever_family="lifecycle-nurture",
                design="holdout")
    base.update(overrides)
    return base


def run(cards, **kwargs):
    return cb.consolidate(cards, POSTURE, **kwargs)


def sized(sessions, rate, **kwargs):
    return cb.size_row("ab", 2, {"monthly_sessions": sessions, "rate": rate,
                                 "window_start": kwargs.pop("start", None)}, POSTURE, **kwargs)


class TestPosture(unittest.TestCase):

    def test_posture_reads_constants(self):
        p = POSTURE
        self.assertEqual((p["significance"], p["power"], p["relative_mde"]), (0.90, 0.80, 0.20))
        self.assertEqual(round(p["M"], 2), 12.37)
        self.assertEqual((p["max_ab_weeks"], p["min_conversions_per_variant"], p["min_days"]),
                         (26, 100, 7))

    def test_posture_missing_row_fails(self):
        text = "\n".join(ln for ln in POSTURE_TABLE.split("\n") if not ln.startswith("| Relative MDE"))
        with self.assertRaisesRegex(cb.PostureError, "Relative MDE"):
            cb.parse_posture(text)

    def test_posture_m_mismatch_fails(self):
        text = POSTURE_TABLE.replace("| 12.37 |", "| 15.70 |")
        with self.assertRaisesRegex(cb.PostureError, "Multiplier M"):
            cb.parse_posture(text)


class TestSizing(unittest.TestCase):

    def test_ab_at_window_edge(self):
        model, sizing, _ = sized(5000, 0.02)
        self.assertEqual(model, "ab")
        self.assertEqual(sizing["n_per_variant"], 15148)
        self.assertAlmostEqual(sizing["weeks"], 25.97, places=2)
        self.assertEqual(sized(4990, 0.02)[0], "directional")

    def test_directional_worked_example(self):
        model, sizing, _ = sized(3000, 0.02)
        self.assertEqual(model, "directional")
        self.assertAlmostEqual(sizing["mde_achievable"], 0.258, places=3)

    def test_pre_post_below_hard_gate(self):
        model, sizing, _ = sized(1000, 0.02)
        self.assertEqual(model, "pre-post")
        self.assertLess(sizing["conversions_per_variant"], 100)

    def test_holdout_unsized(self):
        row = run([strategic_card()])["rows"][0]
        self.assertEqual((row["read_model"], row["sizing"]), ("holdout", None))

    def test_no_baseline_unsized(self):
        row = run([card()])["rows"][0]
        self.assertEqual((row["read_model"], row["unsized_reason"]), ("unsized", "no-baseline"))

    def test_refused_window(self):
        boundary = "2026-06-22"
        self.assertEqual(sized(5000, 0.02, start="2026-05-01", boundary=boundary)[2], "refused-window")
        self.assertEqual(sized(5000, 0.02, start=None, boundary=boundary)[2], "refused-window")
        self.assertEqual(sized(5000, 0.02, start="2026-06-22", boundary=boundary)[0], "ab")


class TestMerges(unittest.TestCase):

    def test_same_surface_mechanism_merges(self):
        first = card(title="Coined title", evidence=["scorecard proof gap"])
        second = card(lens="competitive-proof", title="Pattern title", pattern=True,
                      evidence=["competitive landscape proof row"])
        out = run([first, second])
        self.assertEqual(out["rows_out"], 1)
        row = out["rows"][0]
        self.assertEqual(row["title"], "Pattern title")
        self.assertEqual(row["merged_from"], 2)
        self.assertEqual(row["lenses"], ["surface", "competitive-proof"])
        self.assertEqual(row["evidence"], ["scorecard proof gap", "competitive landscape proof row"])

    def test_surface_overlap_merges_two_page_card(self):
        out = run([card(surfaces=["/a", "/b"]), card(surfaces=["/B/"])])
        self.assertEqual(out["rows_out"], 1)
        self.assertEqual(out["rows"][0]["surfaces"], ["/a", "/b"])

    def test_different_mechanism_stays_separate(self):
        out = run([card(), card(mechanism_key="cta-specificity", title="CTA label")])
        self.assertEqual(out["rows_out"], 2)

    def test_strategic_absorbs_same_design(self):
        tactical = card(mechanism_key="lifecycle-nurture", design="holdout", surfaces=["/resources"])
        out = run([tactical, strategic_card()])
        self.assertEqual(out["rows_out"], 1)
        row = out["rows"][0]
        self.assertEqual(row["altitude"], "strategic")
        self.assertIn("page expression: /resources", row["annotations"])

    def test_strategic_keeps_different_design(self):
        tactical = card(mechanism_key="lifecycle-nurture", title="Resource page nurture CTA")
        out = run([tactical, strategic_card()])
        self.assertEqual(out["rows_out"], 2)
        notes = dict((r["altitude"], r["annotations"]) for r in out["rows"])
        self.assertIn("shares a mechanism with Nurture program; sequence the reads apart",
                      notes["tactical"])
        self.assertIn("shares a mechanism with Resource page nurture CTA; sequence the reads apart",
                      notes["strategic"])


PRIOR_TACTICAL = """# Acme: Experiment Roadmap

## Ready Now

### 1. Pricing proof strip
**Key:** pricing-proof
**Page:** /pricing
**Mechanism:** proof near cta

### 2. Old headline test
**Key:** old-headline
**Page:** /
**Mechanism:** headline clarity

## Backlog

| Key | Title | Surface | Mechanism | Readiness | Read model | ICE | Evidence |
|---|---|---|---|---|---|---|---|
| demo-form-trim | Demo form trim | /demo | form field reduction | Ready now | A/B | I3 C3 E4 (10) | profile |
"""


def priors(text=PRIOR_TACTICAL):
    altitude, entries = cb.parse_prior(text, "prior.md")
    return {altitude: entries}


class TestKeys(unittest.TestCase):

    def test_key_title_pass(self):
        row = run([card(title="  pricing PROOF strip ")], priors=priors())["rows"][0]
        self.assertEqual((row["key"], row["key_source"]), ("pricing-proof", "title"))

    def test_key_mechanism_pass(self):
        row = run([card(title="Proof beside the pricing CTA", surfaces=["/pricing/"])],
                  priors=priors())["rows"][0]
        self.assertEqual((row["key"], row["key_source"]), ("pricing-proof", "mechanism"))

    def test_key_from_backlog_row(self):
        new = card(title="Shorter demo form", surfaces=["/demo"], mechanism_key="form-field-reduction")
        row = run([new], priors=priors())["rows"][0]
        self.assertEqual((row["key"], row["key_source"]), ("demo-form-trim", "mechanism"))

    def test_key_mint_collision(self):
        out = run([card(title="Hero test!"), card(title="Hero Test", mechanism_key="headline-clarity")])
        self.assertEqual(sorted(r["key"] for r in out["rows"]), ["hero-test", "hero-test-2"])
        self.assertEqual(set(r["key_source"] for r in out["rows"]), {"minted"})

    def test_dropped_prior_keys(self):
        out = run([card()], priors=priors())
        self.assertEqual(out["dropped_prior_keys"],
                         [{"key": "old-headline", "title": "Old headline test"},
                          {"key": "demo-form-trim", "title": "Demo form trim"}])


class TestCardsAndLenses(unittest.TestCase):

    def test_card_missing_evidence_rejected(self):
        bad = card()
        del bad["evidence"]
        with self.assertRaisesRegex(cb.InputError, r"card 1: field 'evidence'"):
            run([card(), bad])

    def test_lens_counts_and_shortfalls(self):
        cards = [card(title="t%d" % i, mechanism_key="m%d" % i) for i in range(3)]
        cards.append(strategic_card())
        out = run(cards, floor=2)
        self.assertEqual(out["lens_counts"], {"surface": 3, "persona-journey": 0, "history": 0,
                                              "strategic": 1, "competitive-proof": 0})
        self.assertEqual([s["lens"] for s in out["lens_shortfalls"]],
                         ["persona-journey", "history", "strategic", "competitive-proof"])


def row(key, ice, altitude="tactical", read_model="ab", blockers=(), history=()):
    i, c, e = ice
    return {"key": key, "altitude": altitude, "read_model": read_model, "blockers": list(blockers),
            "history_items": list(history), "ice": {"i": i, "c": c, "e": e}}


def by_key(result):
    return dict((r["key"], r) for r in result["rows"])


class TestRank(unittest.TestCase):

    def test_readiness_precedence(self):
        out = by_key(cb.rank([
            row("a", (3, 3, 3), blockers=["metric-not-tracked", "client-decision"]),
            row("b", (3, 3, 3), blockers=["design-change"]),
            row("c", (3, 3, 3), read_model="unsized", blockers=["design-change"]),
        ], 8))
        self.assertEqual(out["a"]["readiness"], "needs-client-decision")
        self.assertEqual(out["b"]["readiness"], "needs-design-change")
        self.assertEqual(out["c"]["readiness"], "needs-measurement")

    def test_rank_order_isolates_keys(self):
        rows = [
            row("a-lower-tier", (5, 5, 5), blockers=["design-change"]),
            row("b-low-ice", (1, 2, 1)),
            row("c-high-ice-low-c", (5, 2, 5)),
            row("d-low-c-early-key", (4, 3, 4)),
            row("e-high-c-late-key", (3, 5, 3)),
            row("f-full-tie-later-key", (3, 5, 3)),
        ]
        rows.reverse()
        order = [r["key"] for r in cb.rank(rows, 8)["rows"]]
        self.assertEqual(order, ["c-high-ice-low-c", "e-high-c-late-key", "f-full-tie-later-key",
                                 "d-low-c-early-key", "b-low-ice", "a-lower-tier"])

    def test_write_up_selection_per_altitude(self):
        rows = [row("t%02d" % n, (3, 3, 3)) for n in range(10)]
        rows += [row("s%02d" % n, (3, 3, 3), altitude="strategic") for n in range(9)]
        out = cb.rank(rows, 8)["rows"]
        for altitude, total in (("tactical", 10), ("strategic", 9)):
            flags = [r["write_up"] for r in out if r["altitude"] == altitude]
            self.assertEqual(flags, [True] * 8 + [False] * (total - 8))
            self.assertEqual([r["rank"] for r in out if r["altitude"] == altitude],
                             list(range(1, total + 1)))

    def test_unscored_row_rejected(self):
        bad = row("x", (3, 3, 3))
        del bad["ice"]
        with self.assertRaisesRegex(cb.InputError, r"row 0: field 'ice'"):
            cb.rank([bad], 8)

    def test_history_unaccounted(self):
        out = cb.rank([row("x", (3, 3, 3), history=["I1"])], 8, ["I1", "I2", "I3"], ["I3"])
        self.assertEqual(out["history_ledger"], {"I1": "x", "I3": "excluded"})
        self.assertEqual(out["history_unaccounted"], ["I2"])


if __name__ == "__main__":
    unittest.main()
