"""Unit tests for hypothesis-generator history_backlog.py (experiment-history projection).

Fixtures are synthetic and in-memory: a fictional "Acme" history and insight records.
"""
import importlib.util
import os
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "hypothesis-generator", "scripts",
    "history_backlog.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("history_backlog", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hb = _load()

HISTORY = """---
schema: experiment-history
schema_version: "1.2"
client: "acme"
experiment_count: 7
---
# Acme Experiment History

## Experiment Log

### EXP-001: ACME-101 - Pricing Hero Claim
- **Status:** completed
- **Page:** /pricing
- **Treatment Category:** messaging
- **Launch Date:** 2026-01-01
- **End Date:** 2026-01-31
- **Duration:** 30 days (then full-scaled as FS-101 until 2026-05-01)
- **Sample Size:** 3,000 unique visitors / Control: 1500 / V1: 1500
- **Outcome:** win
- **Outcome Source:** analytics API
- **Key Metrics (from analytics):**
  - Clicks per visitor: Control 2.0 vs V1 2.1, lift +5.0%
  - Converting visitors (primary): Control 5.00% (75/1500) vs V1 7.00% (105/1500), lift +40.0%, p<0.001, SIG [analytics]
- **Learning:** A specific claim beat the generic hero. Visitors read the claim as proof. The next test rolls the claim out to the solutions page.
- **Next Steps:** Roll the claim out to the solutions page.
### EXP-002: ACME-102 - Contact Form Helper Text
- **Status:** completed
- **Page:** /contact
- **Treatment Category:** form-optimization
- **Duration:** 40 days
- **Sample Size:** 2000 unique visitors
- **Outcome:** win [UNVERIFIED BY ACME DATA TEAM]
- **Outcome Source:** hand-copied readout
- **Learning:** Helper text looked positive on a hand-copied readout.
### EXP-003: ACME-103 - Demo CTA Label
- **Status:** completed
- **Page:** /demo
- **Duration:** 28 days
- **Sample Size:** 1400 unique visitors / Control: 700 / V1: 700
- **Outcome:** inconclusive
- **Key Metrics:**
  - Demo requests (primary): Control 4.00% (28/700) vs V1 5.43% (38/700), lift +35.7%, p=0.140, NOT SIG
- **Learning:** The label leaned positive without reaching significance.
### EXP-004: ACME-104 - Homepage Banner
- **Status:** monitoring
- **Page:** Sitewide
- **Duration:** 14 days
- **Sample Size:** 7000 exposed visitors
- **Outcome:** monitoring
- **Learning:** No control group.
### EXP-005: ACME-105 - Trial Page Layout
- **Status:** in-progress
- **Page:** /trial
- **Duration:** 12 days (still live as of 2026-10-01)
- **Sample Size:** [NO DATA]
- **Outcome:** in-progress
### EXP-006: ACME-106 - Pricing Toggle
- **Status:** completed
- **Page:** /pricing
- **Launch Date:** 2026-02-01
- **End Date:** 2026-03-03
- **Duration:** Unknown
- **Sample Size:** 6000 unique visitors
- **Outcome:** loss
- **Outcome Source:** auto-classified, no p recorded
- **Learning:** The toggle lost.
### EXP-007: ACME-107 - Plan Comparison Table
- **Status:** completed
- **Page:** /pricing
- **Duration:** 35 days
- **Sample Size:** 3500 unique visitors
- **Outcome:** directional-loss
- **Learning:** The table leaned negative.

## Cross-Experiment Patterns

### Pattern 1: Specific Claims Win
- **Experiments:** EXP-001
- **Outcome:** a pattern bullet, not an experiment record

### Baseline Anchors
- Pricing converts at about 5%.

## Discovered Mechanisms

### Claim Specificity
- **Definition:** Specific claims read as proof.

## Experiment Coverage Gaps

- /about has not been tested.
"""

INSIGHT_101 = """---
experiment_id: ACME-101
---
# ACME-101: Experiment Insight

```yaml
experiment_id: ACME-101
design_type: ab_test
result_classification: "Type 1: Clear Winner"
blockers:
  - description: "Confirm the winning hero is still live before any follow-on."
    owner: "joint"
next_experiments:
  - type: rollout
    hypothesis: >-
      I believe the specific claim will lift the solutions page
      because the mechanism does not depend on the page.
    surfaces: ["/solutions", '/solutions/teams']
    priority: recommended_lead
    if_true: "The claim is a sitewide lever."
    if_false: "The pricing win was page-specific."
  - type: new_hypothesis
    hypothesis: "I believe a proof strip will help
      evaluation-stage visitors."
    surfaces:
      - /customers
    priority: high
  - type: follow_up
    hypothesis: 'A smaller claim test.'
    surfaces: []
    priority: low
```
"""

INSIGHT_103_NO_NEXT = """# ACME-103: Experiment Insight

```yaml
experiment_id: ACME-103
design_type: ab_test
result_classification: "Type 3: No Significant Result"
```
"""

INSIGHT_BAD = """```yaml
experiment_id: ACME-106
next_experiments:
  - type: iteration
    hypothesis: "never closed
```
"""


def _lines(text):
    return text.splitlines()


def _one(outcome, metrics="", extra=""):
    """A one-record history: `outcome` as written, optional metric sub-bullets and fields."""
    body = ("---\nschema: experiment-history\nexperiment_count: 1\n---\n## Experiment Log\n\n"
            "### EXP-001: ACME-201 - Probe\n- **Page:** /probe\n- **Outcome:** %s\n" % outcome)
    if metrics:
        body += "- **Key Metrics:**\n" + "".join("  - %s\n" % m for m in metrics.split("|"))
    return hb.parse_history_lines(_lines(body + extra), "probe.md")["records"][0]


def _insight(items_yaml, wrapper=None):
    block = "next_experiments:\n" + items_yaml
    if wrapper:
        block = wrapper + ":\n" + "".join("  " + ln + "\n" for ln in block.splitlines())
    return "```yaml\nexperiment_id: ACME-101\n```\n\n```yaml\n" + block + "```\n"


def _history(text=HISTORY):
    return hb.parse_history_lines(_lines(text), "acme-history.md")


def _by_id(history, token):
    for rec in history["records"]:
        if token in rec["heading"]:
            return rec
    raise AssertionError("no record " + token)


class TestFieldScoping(unittest.TestCase):
    def test_fields_do_not_leak_into_the_next_entry(self):
        # EXP-001 carries Next Steps and an "until" end date; EXP-002 carries neither.
        h = _history()
        self.assertEqual(_by_id(h, "ACME-101")["next_steps"], "Roll the claim out to the solutions page.")
        nxt = _by_id(h, "ACME-102")
        self.assertIsNone(nxt["next_steps"])
        self.assertFalse(any(c.startswith("until") for c in nxt["deployed"]))

    def test_pattern_subsection_with_an_outcome_bullet_is_not_a_record(self):
        h = _history()
        self.assertEqual(len(h["records"]), 7)
        self.assertFalse(any(r["heading"].startswith("Pattern") for r in h["records"]))


class TestOutcomeMapping(unittest.TestCase):
    def test_p_below_0001_primary_line_maps_to_winner(self):
        rec = _by_id(_history(), "ACME-101")
        self.assertEqual(rec["primary"]["lift"], 40.0)
        self.assertEqual(rec["primary"]["p"], ("<", 0.001))
        self.assertEqual(rec["primary"]["n"], 3000)
        self.assertEqual(rec["mapping"], "winner")

    def test_unverified_qualifier_caps_a_win_at_flat(self):
        rec = _by_id(_history(), "ACME-102")
        self.assertTrue(rec["unverified"])
        self.assertEqual(rec["outcome"], "win")
        self.assertEqual(rec["mapping"], "flat")

    def test_inconclusive_in_directional_band_maps_to_directional_win(self):
        self.assertEqual(_by_id(_history(), "ACME-103")["mapping"], "directional_win")

    def test_inconclusive_outside_directional_band_stays_flat(self):
        h = _history(HISTORY.replace("p=0.140", "p=0.300"))
        self.assertEqual(_by_id(h, "ACME-103")["mapping"], "flat")

    def test_loss_without_a_stated_p_maps_to_flat(self):
        self.assertEqual(_by_id(_history(), "ACME-106")["mapping"], "flat")

    def test_directional_loss_maps_to_directional_loss(self):
        self.assertEqual(_by_id(_history(), "ACME-107")["mapping"], "directional_loss")

    def test_monitoring_and_in_progress_are_not_minted(self):
        h = _history()
        self.assertEqual(_by_id(h, "ACME-104")["mapping"], "not_minted")
        self.assertEqual(_by_id(h, "ACME-105")["mapping"], "not_minted")


class TestDeliveredAndDeployed(unittest.TestCase):
    def test_delivered_per_day_is_sample_over_duration_days(self):
        rec = _by_id(_history(), "ACME-101")
        self.assertEqual((rec["total"], rec["days"], rec["per_day"]), (3000, 30, 100.0))

    def test_days_fall_back_to_launch_and_end_dates(self):
        rec = _by_id(_history(), "ACME-106")
        self.assertEqual((rec["days"], rec["per_day"]), (30, 200.0))

    def test_full_scale_marker_and_until_date(self):
        cues = _by_id(_history(), "ACME-101")["deployed"]
        self.assertIn("full-scaled", cues)
        self.assertIn("until 2026-05-01", cues)

    def test_still_live_marker_and_no_data_sample(self):
        rec = _by_id(_history(), "ACME-105")
        self.assertIn("still live as of 2026-10-01", rec["deployed"])
        self.assertIsNone(rec["per_day"])


class TestSections(unittest.TestCase):
    def test_named_section_ranges_are_reported_without_overlap(self):
        sections = _history()["sections"]
        self.assertEqual(set(sections), {"Cross-Experiment Patterns", "Baseline Anchors",
                                         "Discovered Mechanisms", "Coverage Gaps"})
        pat, base = sections["Cross-Experiment Patterns"], sections["Baseline Anchors"]
        self.assertLess(pat[1], base[0])
        lines = _lines(HISTORY)
        self.assertEqual(lines[base[0]], "### Baseline Anchors")


class TestInsightRecords(unittest.TestCase):
    def test_folded_block_inline_list_block_list_and_multiline_quote(self):
        rec = hb.parse_insight_lines(_lines(INSIGHT_101), "acme-101/insight.md")
        first, second, third = rec["items"]
        self.assertEqual(first["hypothesis"], "I believe the specific claim will lift the solutions "
                                              "page because the mechanism does not depend on the page.")
        self.assertEqual(first["surfaces"], ["/solutions", "/solutions/teams"])
        self.assertEqual(second["surfaces"], ["/customers"])
        self.assertEqual(second["hypothesis"], "I believe a proof strip will help evaluation-stage visitors.")
        self.assertEqual(third["surfaces"], [])
        self.assertEqual(rec["blockers"], ["Confirm the winning hero is still live before any follow-on."])

    def test_missing_next_experiments_contributes_no_items(self):
        rec = hb.parse_insight_lines(_lines(INSIGHT_103_NO_NEXT), "acme-103/insight.md")
        self.assertIsNone(rec["items"])
        code, out, _ = hb.project("h.md", _lines(HISTORY), [("acme-103/insight.md", _lines(INSIGHT_103_NO_NEXT))])
        self.assertEqual(code, 0)
        self.assertIn("No next_experiments: contributes no typed items", out)

    def test_ledger_seed_separates_lead_high_from_considered(self):
        code, out, _ = hb.project("h.md", _lines(HISTORY), [("acme-101/insight.md", _lines(INSIGHT_101))])
        self.assertEqual(code, 0)
        self.assertIn("I1 [recommended_lead], I2 [high] (2)", out)
        self.assertIn("Medium/low items, shown as considered: I3 [low] (1)", out)
        self.assertIn("parent mapping winner", out)


class TestExitCodes(unittest.TestCase):
    def test_non_schema_file_exits_3(self):
        text = HISTORY.replace("schema: experiment-history", "schema: something-else")
        code, out, err = hb.project("h.md", _lines(text), [])
        self.assertEqual((code, out), (3, ""))
        self.assertIn("does not declare schema: experiment-history", err)

    def test_bad_insight_record_is_isolated_and_reported_as_partial_coverage(self):
        code, out, err = hb.project("h.md", _lines(HISTORY), [
            ("acme-106/insight.md", _lines(INSIGHT_BAD)), ("acme-101/insight.md", _lines(INSIGHT_101))])
        self.assertEqual(code, 0)
        self.assertIn("unterminated quoted value", err)
        self.assertIn("COVERAGE PARTIAL: 1 insight record(s) could not be parsed", out)
        self.assertIn("I1 [recommended_lead], I2 [high] (2)", out)

    def test_unclosed_yaml_fence_is_reported_rather_than_dropping_items_silently(self):
        text = INSIGHT_101.rsplit("```", 1)[0]
        code, out, err = hb.project("h.md", _lines(HISTORY), [("acme-101/insight.md", _lines(text))])
        self.assertEqual(code, 0)
        self.assertIn("never closed", out)
        self.assertIn("Coverage partial: 1 insight record(s) failed to parse", out)

    def test_unreadable_insight_file_is_isolated(self):
        code, out, _ = hb.project("h.md", _lines(HISTORY), [("gone/insight.md", "cannot read gone/insight.md")])
        self.assertEqual(code, 0)
        self.assertIn("could not be parsed: cannot read gone/insight.md", out)

    def test_missing_required_argument_exits_2(self):
        with self.assertRaises(SystemExit) as ctx:
            hb.main(["--insights", "a.md"])
        self.assertEqual(ctx.exception.code, 2)

    def test_trailing_comment_on_schema_line_still_binds(self):
        text = HISTORY.replace("schema: experiment-history", "schema: experiment-history  # producer note")
        code, _, _ = hb.project("h.md", _lines(text), [])
        self.assertEqual(code, 0)

    def test_stated_count_with_no_parsed_entries_exits_1(self):
        text = HISTORY.split("## Experiment Log")[0]
        code, out, err = hb.project("h.md", _lines(text), [])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("no entries parsed", err)


class TestOutcomeMappingEdges(unittest.TestCase):
    PRIMARY = "Converting (primary): Control 5.0%% (50/1000) vs V1 6.0%% (60/1000), lift %s, p=%s"

    def test_literal_directional_win_label(self):
        self.assertEqual(_one("directional-win")["mapping"], "directional_win")

    def test_unverified_directional_and_inconclusive_cap_at_flat(self):
        self.assertEqual(_one("directional-win [UNVERIFIED BY ACME DATA TEAM]")["mapping"], "flat")
        rec = _one("inconclusive [UNVERIFIED]", self.PRIMARY % ("+20.0%", "0.120"))
        self.assertEqual(rec["mapping"], "flat")

    def test_labelled_win_and_loss_between_005_and_020_are_directional(self):
        self.assertEqual(_one("win", self.PRIMARY % ("+20.0%", "0.070"))["mapping"], "directional_win")
        self.assertEqual(_one("loss", self.PRIMARY % ("-20.0%", "0.070"))["mapping"], "directional_loss")
        self.assertEqual(_one("win", self.PRIMARY % ("+20.0%", "0.300"))["mapping"], "flat")

    def test_inconclusive_negative_lift_in_band_is_directional_loss(self):
        self.assertEqual(_one("inconclusive", self.PRIMARY % ("-18.0%", "0.150"))["mapping"], "directional_loss")

    def test_outcome_source_p_confirms_a_win_only_when_no_primary_line_exists(self):
        extra = "- **Outcome Source:** auto-classified, p=0.010\n"
        self.assertEqual(_one("win", extra=extra)["mapping"], "winner")
        with_primary = _one("win", "Converting (primary): Control 5.0% (50/1000) vs V1 6.0% (60/1000), lift +20.0%", extra)
        self.assertEqual(with_primary["mapping"], "flat")

    def test_outcome_source_p_never_drives_the_directional_rule(self):
        extra = "- **Outcome Source:** clicks per visitor p=0.010\n"
        rec = _one("inconclusive", "Converting (primary): Control 5.0% (50/1000) vs V1 5.1% (51/1000), lift +2.0%", extra)
        self.assertEqual(rec["mapping"], "flat")


class TestBracketedQualifiers(unittest.TestCase):
    # Each primary line would earn winner / loser / directional_loss without a qualifier.
    CASES = (
        ("win", "Converting (primary): Control 5.0% (50/1000) vs V1 7.0% (70/1000), lift +40.0%, p=0.010"),
        ("loss", "Converting (primary): Control 7.0% (70/1000) vs V1 5.0% (50/1000), lift -28.6%, p=0.010"),
        ("inconclusive", "Converting (primary): Control 6.0% (60/1000) vs V1 5.0% (50/1000), lift -18.0%, p=0.150"),
    )

    def _assert_capped(self, qualifier):
        for token, primary in self.CASES:
            with self.subTest(token=token):
                rec = _one("%s [%s]" % (token, qualifier), primary)
                self.assertEqual(rec["mapping"], "flat")
                self.assertIn("[%s]" % qualifier, hb.record_line(rec))

    def test_unreadable_qualifier_caps_win_loss_and_inconclusive_at_flat(self):
        self._assert_capped("UNREADABLE: sample ratio mismatch")

    def test_contradictory_qualifier_caps_win_loss_and_inconclusive_at_flat(self):
        self._assert_capped("CONTRADICTORY: downstream checkout starts fell")

    def test_meta_tally_labels_every_qualifier_and_keeps_the_unverified_count(self):
        text = HISTORY.replace("- **Outcome:** loss\n", "- **Outcome:** loss [CONTRADICTORY: meetings rose]\n")
        _, out, _ = hb.project("h.md", _lines(text), [])
        self.assertIn("- Bracketed qualifier: 2 records (never mapped above flat): CONTRADICTORY 1, UNVERIFIED 1", out)
        self.assertIn("- UNVERIFIED qualifier: 1 records", out)
        self.assertIn("loss [CONTRADICTORY] 1", out)


class TestFieldShapes(unittest.TestCase):
    def test_next_steps_as_sub_bullets_reach_the_record_and_the_count(self):
        extra = "- **Next Steps:**\n  - Roll out to the solutions page.\n  - Test a shorter form.\n"
        rec = _one("win", extra=extra)
        self.assertEqual(rec["next_steps"], "Roll out to the solutions page.; Test a shorter form.")
        text = "---\nschema: experiment-history\nexperiment_count: 1\n---\n### EXP-001: X\n- **Outcome:** win\n" + extra
        _, out, _ = hb.project("h.md", _lines(text), [])
        self.assertIn("Records with an explicit Next Steps field: 1", out)

    def test_column_0_wrapped_learning_line_is_kept(self):
        extra = "- **Learning:** The first line wraps\nonto a second line at column 0.\n\nA separate paragraph.\n"
        rec = _one("win", extra=extra)
        self.assertEqual(rec["learning"], "The first line wraps onto a second line at column 0.")

    def test_stated_and_parsed_count_mismatch_prints_a_warning(self):
        text = HISTORY.replace("experiment_count: 7", "experiment_count: 9")
        _, out, _ = hb.project("h.md", _lines(text), [])
        self.assertIn("WARNING: experiment_count states 9 but 7 entries parsed", out)


class TestInsightShapes(unittest.TestCase):
    ITEM = "  - type: rollout\n    priority: %s\n    surfaces: [\"/solutions\"]\n"

    def test_unrecognized_priority_is_seeded_with_the_lead_high_items(self):
        text = _insight(self.ITEM % "P1" + self.ITEM % "medium")
        _, out, _ = hb.project("h.md", _lines(HISTORY), [("acme-101/insight.md", _lines(text))])
        self.assertIn("Priority unrecognized, treated as lead/high until dispositioned: I1 [p1] (1)", out)
        self.assertIn("Medium/low items, shown as considered: I2 [medium] (1)", out)

    def test_next_experiments_in_a_second_block_is_read(self):
        rec = hb.parse_insight_lines(_lines(_insight(self.ITEM % "high")), "acme-101/insight.md")
        self.assertEqual([i["priority"] for i in rec["items"]], ["high"])
        self.assertEqual(rec["experiment_id"], "ACME-101")

    def test_next_experiments_nested_under_a_root_key_is_read(self):
        rec = hb.parse_insight_lines(_lines(_insight(self.ITEM % "high", wrapper="insight")),
                                     "acme-101/insight.md")
        self.assertEqual([i["surfaces"] for i in rec["items"]], [["/solutions"]])


class TestProjectionContract(unittest.TestCase):
    def test_output_does_not_depend_on_insight_argument_order(self):
        a = ("acme-101/insight.md", _lines(INSIGHT_101))
        b = ("acme-103/insight.md", _lines(INSIGHT_103_NO_NEXT))
        self.assertEqual(hb.project("h.md", _lines(HISTORY), [a, b]),
                         hb.project("h.md", _lines(HISTORY), [b, a]))

    def test_learning_tail_keeps_the_last_two_sentences_within_300_chars(self):
        text = "First sentence. " + ("Long middle clause " * 20) + "ends here. Final short sentence."
        tail = hb.sentence_tail(text)
        self.assertLessEqual(len(tail), 300)
        self.assertTrue(tail.endswith("Final short sentence."))

    def test_script_source_never_names_the_task_tracker(self):
        # The skill validator greps the skill directory for this string; it must stay absent.
        with open(_MODULE_PATH, encoding="utf-8") as f:
            self.assertNotIn("click" + "up", f.read().lower())


if __name__ == "__main__":
    unittest.main()
