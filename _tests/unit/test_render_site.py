"""Unit tests for render-program-site render_site.py (deterministic core).

Covers the minimal YAML parser, gold-roadmap body parsing (`### N.` sections,
tiers, `**Key:**`, `**Scores:**`), the edge-contract gate, derived data (reverse
edges, intake, map coordinates, edge classes, tier grouping), the display
helpers, and end-to-end emit. The skill consumes hypothesis-generator's prose
gold roadmaps (strategic + tactical) plus a render-owned edge sidecar; all three
fixtures here are synthetic (non-client).
"""
import contextlib
import importlib.util
import io
import os
import re
import tempfile
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "render-program-site", "scripts", "render_site.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("render_site", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rs = _load()

# --------------------------------------------------------------------------
# Synthetic fixtures (non-client): two prose gold roadmaps + one edge sidecar.
# Per-item structured data (id/key/title/tier/ICE/page) is DERIVED from the gold
# bodies; only the edge binding + classification live in the sidecar.
# --------------------------------------------------------------------------

STRATEGIC = """---
kb_layer: gold
generated_by: hypothesis-generator
version: "1.0.0"
---
# Acme: Strategic Experiment Roadmap

## How to Read This Roadmap
Synthetic strategic roadmap for testing.

## Strategic Bets

### 1. Speed to first value
**Key:** speed-to-first-value
**Lever:** Activation time is the dominant lever for trial-to-paid.
**What to stand up:** A routing change that shortens time to first value.
**Scores:** Impact 5 | Confidence 4 | Ease 2
Impact is 5 because activation is the dominant lever.
**What a win proves:** That speed, not packaging, governs activation.

### 2. Proof and ROI
**Key:** proof-and-roi
**Lever:** Buyers need proof from peers like them.
**What to stand up:** Named-customer outcome data and a proof asset.
**Scores:** Impact 5 | Confidence 4 | Ease 2
Impact is 5 because proof is the top evaluation blocker.
**What a win proves:** That peer proof moves evaluation conversion.

## Explorations

### 3. Offer ladder
**Key:** offer-ladder
**Lever:** One high-commitment ask suppresses pipeline entry.
**What to stand up:** A lower-commitment offer tier.
**Scores:** Impact 4 | Confidence 3 | Ease 3
Impact is 4 because the single ask is a known drop point.
**What a win proves:** That a commitment ladder lifts entry.

## Sequencing Rationale
Run speed-to-value first; build the proof asset in parallel.
"""

TACTICAL = """---
kb_layer: gold
generated_by: hypothesis-generator
version: "1.0.0"
---
# Acme: Experiment Roadmap

## How to Read This Roadmap
Synthetic tactical roadmap for testing.

## Quick Wins

### 1. Intake-only CTA label test
**Key:** cta-label-test
**Page:** Sitewide
**What to test:** Clearer, more specific CTA labels.
**Why this should work:** Specific labels raise click-through.
**Scores:** Impact 3 | Confidence 4 | Ease 4
Ease is 4 because it is a copy change.

## Strategic Bets

### 2. Conversational signup form
**Key:** conversational-signup-form
**Page:** Signup
**What to test:** A conversational multi-step signup form.
**Why this should work:** A conversational form reduces friction.
**Scores:** Impact 4 | Confidence 4 | Ease 3
Ease is 3 because it is a form rebuild.

### 3. Old form test
**Key:** old-form-test
**Page:** Signup
**What to test:** The prior single-screen form variant.
**Scores:** Impact 4 | Confidence 3 | Ease 3
This variant has been replaced by a later iteration.

## Explorations

### 4. Proof block on pricing
**Key:** proof-block-on-pricing
**Page:** Pricing
**What to test:** A proof block placed near the price.
**Why this should work:** Preempting objections lifts conversion.
**Scores:** Impact 3 | Confidence 3 | Ease 3
Ease is 3 because it is a content block.
"""

SIDECAR = """---
program:
  client: "Acme Robotics"
  name: "Acme Growth Program"
  date: "2026-06-24"
  strategic_version: "1.0.0"
  tactical_version: "1.0.0"
  hero:
    eyebrow: "Acme Growth Program"
    headline: "Turning 50,000 trials into revenue."
    headline_num: "50,000"
    subhead: "Pairing program moves with the page tests that execute them."
bets:
  - key: speed-to-first-value
    delivery_surface: [routing]
    executor_status: off-page
    run_tag: "Run first"
    decided_on: "trial-to-paid"
    keystone: false
    edges:
      - {target: conversational-signup-form, type: informs}
  - key: proof-and-roi
    delivery_surface: [proof, copy]
    executor_status: on-page
    run_tag: "Keystone"
    decided_on: "evaluation conversion"
    keystone: true
    edges:
      - {target: proof-block-on-pricing, type: expresses}
      - {target: conversational-signup-form, type: informs}
  - key: offer-ladder
    delivery_surface: [offer]
    executor_status: unexpressed
    decided_on: "pipeline entry"
    keystone: false
    edges:
      - {target: conversational-signup-form, type: gates}
tests:
  - key: cta-label-test
    mechanism_class: cta
  - key: conversational-signup-form
    mechanism_class: form
  - key: old-form-test
    mechanism_class: form
    status: superseded
    superseded_by: "v2.1"
  - key: proof-block-on-pricing
    mechanism_class: proof
    mockup: {screenshot: "mockups/proof-block-on-pricing/screenshot.png", html: "mockups/proof-block-on-pricing/mockup.html", mode: "chrome-devtools", target_url: "acme.example/pricing", insertion_point: "Below the fold", placement_summary: "Sits where doubt peaks."}
---
"""


# --------------------------------------------------------------------------
# Synthetic account-program fixture (non-client). The account-program deliverable
# is an off-store altitude: plays carry no **Key:** / **Scores:**, and there is a
# cohort-taxonomy table plus a cohort-rosters block (whose `### <name>` headings
# must NOT parse as plays). The plays live under `## The Account-Level Plays`.
# --------------------------------------------------------------------------

ACCOUNT = """---
kb_layer: gold
generated_by: hypothesis-generator
version: "1.0.0"
---
# Acme: Account Program

## How to Read This Program
Off-store plays measured by account-level designs, not on-store splits.

## The Account-Cohort Taxonomy

| Cohort | Approximate size | Behavior |
|---|---|---|
| **Dormant enterprise** | ~180 accounts | Signed up, never activated a seat. |
| **Expansion-ready** | ~60 accounts | High usage on a single team, no expansion. |
| **At-risk renewal** | ~40 accounts | Usage decline in the last quarter. |

## Cohort Rosters

### Dormant enterprise
Northwind, Contoso, Example Corp.

### Expansion-ready
The client's two largest teams.

## The Account-Level Plays

### 1. Dormant reactivation sequence
**Cohort:** Dormant enterprise.
**The play:** A guided reactivation offer routed to dormant admins.
**Rationale:** Dormant accounts already carry intent; reactivation is cheaper than net-new.
**How it is measured:** Reactivated-account rate over a matched control window.
**Dependencies:** Admin contact list and an offline offer channel.
**Relationship to the roadmaps:** Feeds the activation bet without an on-store split.

### 2. Expansion motion for high-usage teams
**Cohort:** Expansion-ready.
**The play:** An account-level expansion motion for concentrated high-usage teams.
**Rationale:** Concentrated usage is the strongest expansion signal in the base.
**How it is measured:** Seat-expansion rate against a holdout cohort.
**Dependencies:** Usage-by-team read and a sales-assist handoff.
**Relationship to the roadmaps:** Informs the proof bet with expansion evidence.

## Boundaries
These plays run off-store and are not A/B tests.
"""


# --------------------------------------------------------------------------
# Frontmatter-less legacy fixtures. hypothesis-generator's LEGACY-mode roadmaps
# carry no YAML frontmatter by design (the L2 body-purity rule); the generator
# must load them as body-only files.
# --------------------------------------------------------------------------

STRATEGIC_LEGACY = STRATEGIC.split("---\n", 2)[2]
TACTICAL_LEGACY = TACTICAL.split("---\n", 2)[2]


def _write_triple(strategic=STRATEGIC, tactical=TACTICAL, sidecar=SIDECAR):
    d = tempfile.mkdtemp()
    sp = os.path.join(d, "strategic.md")
    tp = os.path.join(d, "tactical.md")
    ep = os.path.join(d, "edges.md")
    for path, text in ((sp, strategic), (tp, tactical), (ep, sidecar)):
        with open(path, "w") as f:
            f.write(text)
    return d, sp, tp, ep


def _write_quad(strategic=STRATEGIC, tactical=TACTICAL, sidecar=SIDECAR, account=ACCOUNT):
    """Like _write_triple, but also writes the optional account-program file.
    Returns (dir, strategic_path, tactical_path, edges_path, account_path)."""
    d, sp, tp, ep = _write_triple(strategic, tactical, sidecar)
    ap = os.path.join(d, "account.md")
    with open(ap, "w") as f:
        f.write(account)
    return d, sp, tp, ep, ap


def _load_all(strategic=STRATEGIC, tactical=TACTICAL, sidecar=SIDECAR):
    _, sp, tp, ep = _write_triple(strategic, tactical, sidecar)
    sc = rs.load_sidecar(ep)
    s = rs.load_strategic(sp, sc)
    t = rs.load_tactical(tp, sc)
    rs.link_edges(s, t)
    return s, t, sc


# --------------------------------------------------------------------------
# Parser + gold-body extraction
# --------------------------------------------------------------------------

class TestParser(unittest.TestCase):
    def test_nested_block_map(self):
        fm, _ = rs.parse_frontmatter(SIDECAR)
        self.assertEqual(fm["program"]["client"], "Acme Robotics")
        self.assertEqual(fm["program"]["hero"]["headline_num"], "50,000")

    def test_block_seq_of_maps_and_inline_flow(self):
        fm, _ = rs.parse_frontmatter(SIDECAR)
        bet = fm["bets"][1]
        self.assertEqual(bet["key"], "proof-and-roi")
        self.assertEqual(bet["delivery_surface"], ["proof", "copy"])
        self.assertEqual(bet["executor_status"], "on-page")
        self.assertEqual(bet["edges"][0], {"target": "proof-block-on-pricing", "type": "expresses"})
        self.assertTrue(bet["keystone"] is True)

    def test_flow_map_quoted_commas_and_colons(self):
        v = rs._parse_flow('{id: p-1, insertion_point: "a, b, c", url: "https://x.io/p"}')
        self.assertEqual(v["insertion_point"], "a, b, c")
        self.assertEqual(v["url"], "https://x.io/p")
        self.assertEqual(v["id"], "p-1")

    def test_inline_flow_test_with_nested_mockup(self):
        fm, _ = rs.parse_frontmatter(SIDECAR)
        mocked = [t for t in fm["tests"] if "mockup" in t][0]
        self.assertEqual(mocked["key"], "proof-block-on-pricing")
        self.assertEqual(mocked["mechanism_class"], "proof")
        self.assertEqual(mocked["mockup"]["mode"], "chrome-devtools")

    def test_tab_indentation_clear_error(self):
        with self.assertRaises(ValueError) as cm:
            rs.parse_frontmatter("---\nprogram:\n\tclient: x\n---\nbody\n")
        self.assertIn("tab", str(cm.exception).lower())

    def test_folded_block_scalar(self):
        fm, _ = rs.parse_frontmatter(
            '---\n'
            'description: >\n'
            '  A folded description that spans\n'
            '  two lines into one.\n'
            'kb_layer: gold\n'
            'tags: [a, b]\n'
            '---\nbody\n')
        self.assertEqual(fm["description"], "A folded description that spans two lines into one.")
        self.assertEqual(fm["kb_layer"], "gold")
        self.assertEqual(fm["tags"], ["a", "b"])

    def test_frontmatter_optional_returns_empty_and_full_text(self):
        fm, body = rs.parse_frontmatter(STRATEGIC_LEGACY, required=False)
        self.assertEqual(fm, {})
        self.assertEqual(body, STRATEGIC_LEGACY)

    def test_frontmatter_required_still_raises(self):
        # the sidecar load stays strict: no frontmatter is still an error
        with self.assertRaises(ValueError):
            rs.parse_frontmatter(STRATEGIC_LEGACY)

    def test_parse_scores(self):
        self.assertEqual(rs.parse_scores("Impact 5 | Confidence 4 | Ease 2\nrationale"),
                         {"i": 5, "c": 4, "e": 2})
        self.assertIsNone(rs.parse_scores("no scores here"))

    def test_body_section_extraction(self):
        _, body = rs.parse_frontmatter(STRATEGIC)
        secs = rs.extract_sections(body, "bet")
        self.assertIn("sb-02", secs)
        self.assertEqual(secs["sb-02"]["key"], "proof-and-roi")
        self.assertEqual(secs["sb-02"]["tier"], "strategic-bet")
        self.assertEqual(secs["sb-02"]["labels"]["Lever"], "Buyers need proof from peers like them.")

    def test_tactical_tier_and_page_derivation(self):
        _, body = rs.parse_frontmatter(TACTICAL)
        secs = rs.extract_sections(body, "test")
        self.assertEqual(secs["p-01"]["tier"], "quick-win")
        self.assertEqual(secs["p-04"]["tier"], "exploration")
        self.assertEqual(secs["p-01"]["labels"]["Page"], "Sitewide")


# --------------------------------------------------------------------------
# Gate
# --------------------------------------------------------------------------

class TestGate(unittest.TestCase):
    def test_valid_passes(self):
        s, t, sc = _load_all()
        rs.run_gate(s, t, sc)  # should not raise

    def _expect_violation(self, code, strategic=STRATEGIC, tactical=TACTICAL, sidecar=SIDECAR):
        s, t, sc = _load_all(strategic, tactical, sidecar)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t, sc)
        self.assertTrue(any(code in v for v in cm.exception.violations),
                        "expected a %s violation, got: %s" % (code, cm.exception.violations))

    def test_check1_bad_edge_type(self):
        bad = SIDECAR.replace("{target: conversational-signup-form, type: gates}",
                              "{target: conversational-signup-form, type: bogus}")
        self._expect_violation("[1]", sidecar=bad)

    def test_check2_dangling_target(self):
        bad = SIDECAR.replace("{target: proof-block-on-pricing, type: expresses}",
                              "{target: nonexistent-test, type: expresses}")
        self._expect_violation("[2]", sidecar=bad)

    def test_check3_mechanism_mismatch(self):
        # sb-01 (routing) expresses cta-label-test (cta) -> routing vs cta mismatch
        bad = SIDECAR.replace("{target: conversational-signup-form, type: informs}",
                              "{target: cta-label-test, type: expresses}")
        s, t, sc = _load_all(sidecar=bad)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t, sc)
        joined = " ".join(cm.exception.violations)
        self.assertIn("[3]", joined)
        self.assertIn("routing", joined)
        self.assertIn("cta", joined)

    def test_check4_executor_status_mismatch(self):
        # sb-01 declared off-page but given an expresses edge to a matching surface
        bad = SIDECAR.replace("delivery_surface: [routing]", "delivery_surface: [proof]")
        bad = bad.replace("{target: conversational-signup-form, type: informs}",
                          "{target: proof-block-on-pricing, type: expresses}")
        self._expect_violation("[4]", sidecar=bad)

    def test_check5_authored_intake_rejected(self):
        bad = SIDECAR.replace("  - key: cta-label-test\n    mechanism_class: cta",
                              "  - key: cta-label-test\n    mechanism_class: cta\n    intake_only: true")
        self._expect_violation("[5]", sidecar=bad)

    def test_check6_sidecar_test_authors_reverse(self):
        bad = SIDECAR.replace("  - key: conversational-signup-form\n    mechanism_class: form",
                              "  - key: conversational-signup-form\n    mechanism_class: form\n    expressed_by: [sb-02]")
        self._expect_violation("[6]", sidecar=bad)

    def test_check7_version_skew(self):
        bad = SIDECAR.replace('tactical_version: "1.0.0"', 'tactical_version: "1.0.1"')
        self._expect_violation("[7]", sidecar=bad)

    def test_bind_unknown_sidecar_key(self):
        bad = SIDECAR.replace("  - key: offer-ladder", "  - key: offer-ladder-typo")
        self._expect_violation("[bind]", sidecar=bad)

    def test_missing_mechanism_class(self):
        bad = SIDECAR.replace("  - key: conversational-signup-form\n    mechanism_class: form",
                              "  - key: conversational-signup-form")
        self._expect_violation("[mech]", sidecar=bad)

    def test_malformed_mockup_rejected(self):
        bad = SIDECAR.replace("  - key: cta-label-test\n    mechanism_class: cta",
                              "  - key: cta-label-test\n    mechanism_class: cta\n    mockup: \"oops\"")
        self._expect_violation("[mockup]", sidecar=bad)


# --------------------------------------------------------------------------
# Legacy (frontmatter-less) roadmaps + the version-lock skip semantics
# --------------------------------------------------------------------------
# Legacy-mode roadmaps carry no frontmatter, so they have no `version` to lock:
# gate check 7 skips the lock per versionless file and reports the skip
# explicitly in the gate notes (never a silent pass, never a gate failure).
# Gold roadmaps always carry `version`, so the KB lane locks exactly as before.

class TestLegacyFrontmatterless(unittest.TestCase):
    def test_frontmatterless_roadmaps_load(self):
        s, t, _ = _load_all(strategic=STRATEGIC_LEGACY, tactical=TACTICAL_LEGACY)
        self.assertEqual([b["id"] for b in s["bets"]], ["sb-01", "sb-02", "sb-03"])
        self.assertEqual([x["id"] for x in t["tests"]], ["p-01", "p-02", "p-03", "p-04"])
        self.assertIsNone(s["gold_version"])
        self.assertIsNone(t["gold_version"])

    def test_version_lock_skip_reported_in_notes(self):
        # the sidecar still declares both versions (schema-required); with no
        # roadmap version to check against, the lock skips with a report
        s, t, sc = _load_all(strategic=STRATEGIC_LEGACY, tactical=TACTICAL_LEGACY)
        notes = rs.run_gate(s, t, sc)  # must not raise
        self.assertIn("version lock: skipped for strategic (roadmap carries no version)", notes)
        self.assertIn("version lock: skipped for tactical (roadmap carries no version)", notes)

    def test_gold_path_unchanged_no_notes(self):
        s, t, sc = _load_all()
        self.assertEqual(rs.run_gate(s, t, sc), [])

    def test_mixed_pair_skips_only_the_versionless_file(self):
        # strategic keeps its version (locked as before); tactical carries none
        s, t, sc = _load_all(tactical=TACTICAL_LEGACY)
        self.assertEqual(rs.run_gate(s, t, sc),
                         ["version lock: skipped for tactical (roadmap carries no version)"])

    def test_mixed_pair_still_fails_closed_on_real_skew(self):
        # the versioned file's lock still fails even while the other is skipped
        bad = SIDECAR.replace('strategic_version: "1.0.0"', 'strategic_version: "9.9.9"')
        s, t, sc = _load_all(tactical=TACTICAL_LEGACY, sidecar=bad)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t, sc)
        self.assertTrue(any("[7] strategic" in v for v in cm.exception.violations),
                        "expected a [7] strategic violation, got: %s" % cm.exception.violations)

    def test_end_to_end_legacy_renders_and_reports_skip(self):
        d, sp, tp, ep = _write_triple(strategic=STRATEGIC_LEGACY, tactical=TACTICAL_LEGACY)
        out = os.path.join(d, "site")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep, "--out", out])
        self.assertEqual(rc, 0)
        stdout = buf.getvalue()
        self.assertIn("note: version lock: skipped for strategic (roadmap carries no version)", stdout)
        self.assertIn("note: version lock: skipped for tactical (roadmap carries no version)", stdout)
        self.assertIn("OK gate passed.", stdout)
        self.assertIn("index.html", os.listdir(out))


# --------------------------------------------------------------------------
# Derivation
# --------------------------------------------------------------------------

class TestDerive(unittest.TestCase):
    def setUp(self):
        self.s, self.t, self.sc = _load_all()
        rs.run_gate(self.s, self.t, self.sc)
        self.d = rs.derive(self.s, self.t)
        self.tests = {t["id"]: t for t in self.t["tests"]}

    def test_reverse_edges(self):
        p2 = self.tests["p-02"]
        self.assertEqual(p2["exp_by"], [])
        self.assertEqual(sorted(p2["inf_by"]), ["sb-01", "sb-02", "sb-03"])
        self.assertEqual(self.tests["p-04"]["exp_by"], ["sb-02"])

    def test_intake_flag(self):
        self.assertTrue(self.tests["p-01"]["intake_only"])
        self.assertFalse(self.tests["p-04"]["intake_only"])

    def test_map_coords_pure_function_of_ie(self):
        p4 = self.tests["p-04"]  # I3 E3 -> center singleton
        self.assertEqual((p4["cx"], p4["cy"]), (int(round(rs.x_of(3))), int(round(rs.y_of(3)))))

    def test_tie_dodge_separates_shared_cell(self):
        bets = {b["id"]: b for b in self.s["bets"]}
        a, b = bets["sb-01"], bets["sb-02"]  # both I5 E2
        self.assertNotEqual((a["cx"], a["cy"]), (b["cx"], b["cy"]))

    def test_tier_grouping_and_superseded(self):
        g = self.d["tier_groups"]
        self.assertEqual([t["id"] for t in g["quick-win"]], ["p-01"])
        self.assertEqual([t["id"] for t in g["exploration"]], ["p-04"])
        self.assertEqual([t["id"] for t in self.d["superseded"]], ["p-03"])

    def test_edge_class_split(self):
        b2 = {b["id"]: b for b in self.s["bets"]}["sb-02"]
        self.assertEqual(b2["expresses"], ["p-04"])     # solid
        self.assertEqual(b2["influences"], ["p-02"])    # dashed (informs)


# --------------------------------------------------------------------------
# Display helpers
# --------------------------------------------------------------------------

class TestHelpers(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(rs.bet_label("sb-02"), "SB-2")
        self.assertEqual(rs.test_num("p-10"), "10")
        self.assertEqual(rs.ice_total({"i": 5, "c": 4, "e": 2}), 11)

    def test_join_and(self):
        self.assertEqual(rs.join_and(["SB-2"]), "SB-2")
        self.assertEqual(rs.join_and(["SB-1", "SB-2"]), "SB-1 and SB-2")
        self.assertEqual(rs.join_and(["SB-1", "SB-2", "SB-3"]), "SB-1, SB-2, and SB-3")

    def test_render_single_pass_no_token_clobber(self):
        out = rs.render("A={{A}} B={{B}}", {"A": "x {{B}} y", "B": "ZZZ"})
        self.assertEqual(out, "A=x {{B}} y B=ZZZ")

    def test_render_unknown_token_left_intact(self):
        self.assertEqual(rs.render("{{KNOWN}} {{MISSING}}", {"KNOWN": "k"}), "k {{MISSING}}")


# --------------------------------------------------------------------------
# End-to-end emit
# --------------------------------------------------------------------------

class TestEndToEnd(unittest.TestCase):
    def _render(self):
        d, sp, tp, ep = _write_triple()
        out = os.path.join(d, "site")
        rc = rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep, "--out", out])
        return rc, out

    def test_exit_zero_and_page_count(self):
        rc, out = self._render()
        self.assertEqual(rc, 0)
        files = set(os.listdir(out))
        # hub + 3 bets + 3 live tests + assets; superseded p-03 omitted
        for f in ("index.html", "sb-01.html", "sb-02.html", "sb-03.html",
                  "p-01.html", "p-02.html", "p-04.html", "styles.css", "site.js"):
            self.assertIn(f, files)
        self.assertNotIn("p-03.html", files)

    def test_gate_failure_exit_nonzero(self):
        bad = SIDECAR.replace('tactical_version: "1.0.0"', 'tactical_version: "9.9.9"')
        d, sp, tp, ep = _write_triple(STRATEGIC, TACTICAL, bad)
        out = os.path.join(d, "site")
        self.assertNotEqual(rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep, "--out", out]), 0)

    def test_deterministic_output(self):
        d, sp, tp, ep = _write_triple()
        o1, o2 = os.path.join(d, "a"), os.path.join(d, "b")
        rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep, "--out", o1])
        rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep, "--out", o2])
        with open(os.path.join(o1, "index.html")) as a, open(os.path.join(o2, "index.html")) as b:
            self.assertEqual(a.read(), b.read())

    def test_relative_refs_no_client_content(self):
        rc, out = self._render()
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn('href="styles.css"', html)
        self.assertIn('src="site.js"', html)
        self.assertNotIn("http://", html.replace("http://www.w3.org", ""))  # no external links but SVG ns
        # output reflects only the synthetic fixture client; the generator emits no
        # hardcoded client identity of its own (all client data comes from the inputs)
        self.assertIn("Acme Robotics", html)

    def test_keystone_prefill_single_is_grammatical_and_claim_free(self):
        # Fixture has exactly one keystone bet (proof-and-roi -> SB-2).
        rc, out = self._render()
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn("SB-2 is the keystone bet.", html)
        # the old hardcoded, client-specific claim must be gone
        self.assertNotIn("shared asset", html)
        self.assertNotIn("converge", html)
        # the slot stays a curation slot
        self.assertIn("<!--PROSE id=program slot=keystone-->", html)

    def test_keystone_prefill_multiple_is_count_correct(self):
        # Flip a second bet to keystone (speed-to-first-value -> SB-1).
        multi = SIDECAR.replace(
            'decided_on: "trial-to-paid"\n    keystone: false',
            'decided_on: "trial-to-paid"\n    keystone: true')
        d, sp, tp, ep = _write_triple(STRATEGIC, TACTICAL, multi)
        out = os.path.join(d, "site")
        self.assertEqual(rs.main(["--strategic", sp, "--tactical", tp,
                                  "--edges", ep, "--out", out]), 0)
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn("SB-1 and SB-2 are the keystone bets.", html)
        self.assertNotIn("shared asset", html)

    def test_absent_mockup_section_omitted(self):
        rc, out = self._render()
        with open(os.path.join(out, "p-02.html")) as f:
            self.assertNotIn("Proposed change", f.read())
        with open(os.path.join(out, "p-04.html")) as f:
            self.assertIn("Proposed change", f.read())


# --------------------------------------------------------------------------
# Account-program altitude
# --------------------------------------------------------------------------

class TestAccountParser(unittest.TestCase):
    def test_plays_parse_as_ap_ids_no_tier_no_key(self):
        _, body = rs.parse_frontmatter(ACCOUNT)
        plays_slice = rs.extract_named_section(body, "The Account-Level Plays")
        secs = rs.extract_sections(plays_slice, "play")
        self.assertIn("ap-01", secs)
        self.assertIn("ap-02", secs)
        self.assertEqual(secs["ap-01"]["title"], "Dormant reactivation sequence")
        # plays carry no tier (no `## ` tier heading in the slice) and no Key
        self.assertIsNone(secs["ap-01"]["tier"])
        self.assertIsNone(secs["ap-01"]["key"])
        # the six bold labels are present
        for lbl in ("Cohort", "The play", "Rationale", "How it is measured",
                    "Dependencies", "Relationship to the roadmaps"):
            self.assertIn(lbl, secs["ap-01"]["labels"])

    def test_roster_headings_outside_slice_not_parsed_as_plays(self):
        _, body = rs.parse_frontmatter(ACCOUNT)
        plays_slice = rs.extract_named_section(body, "The Account-Level Plays")
        secs = rs.extract_sections(plays_slice, "play")
        # exactly the two ordinal plays; the `### <name>` roster headings are
        # outside the slice and are not ordinal form, so they never appear
        self.assertEqual(sorted(secs.keys()), ["ap-01", "ap-02"])


class TestAccountLoader(unittest.TestCase):
    def test_load_account_none_when_no_path(self):
        self.assertIsNone(rs.load_account(None))
        self.assertIsNone(rs.load_account(""))

    def test_load_account_plays_and_cohorts(self):
        _, _, _, _, ap = _write_quad()
        acct = rs.load_account(ap)
        self.assertEqual([p["id"] for p in acct["plays"]], ["ap-01", "ap-02"])
        # plays derive without requiring Key/Scores
        self.assertNotIn("Key", acct["plays"][0]["labels"])
        self.assertNotIn("Scores", acct["plays"][0]["labels"])
        # taxonomy table parsed: name (bold stripped) + size + behavior
        self.assertEqual(len(acct["cohorts"]), 3)
        self.assertEqual(acct["cohorts"][0]["name"], "Dormant enterprise")
        self.assertEqual(acct["cohorts"][0]["size"], "~180 accounts")
        self.assertIn("never activated", acct["cohorts"][0]["behavior"])


class TestAccountGate(unittest.TestCase):
    def _expect_account_violation(self, account_text):
        s, t, sc = _load_all()
        d = tempfile.mkdtemp()
        ap = os.path.join(d, "account.md")
        with open(ap, "w") as f:
            f.write(account_text)
        acct = rs.load_account(ap)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t, sc, acct)
        self.assertTrue(any("[account]" in v for v in cm.exception.violations),
                        "expected an [account] violation, got: %s" % cm.exception.violations)

    def test_valid_account_passes(self):
        s, t, sc = _load_all()
        _, _, _, _, ap = _write_quad()
        rs.run_gate(s, t, sc, rs.load_account(ap))  # should not raise

    def test_missing_required_label_fails(self):
        bad = ACCOUNT.replace("**How it is measured:** Reactivated-account rate over a matched control window.\n", "")
        self._expect_account_violation(bad)

    def test_empty_plays_block_fails(self):
        bad = ACCOUNT.replace(
            "### 1. Dormant reactivation sequence", "#### not-a-play").replace(
            "### 2. Expansion motion for high-usage teams", "#### also-not")
        self._expect_account_violation(bad)

    def test_duplicate_ordinals_fail(self):
        bad = ACCOUNT.replace("### 2. Expansion motion for high-usage teams",
                              "### 1. Expansion motion for high-usage teams")
        self._expect_account_violation(bad)


class TestAccountEndToEnd(unittest.TestCase):
    def test_no_account_byte_identical_seam(self):
        d, sp, tp, ep = _write_triple()
        out = os.path.join(d, "site")
        self.assertEqual(rs.main(["--strategic", sp, "--tactical", tp,
                                  "--edges", ep, "--out", out]), 0)
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        # the seam between #backlog close and #sequence open is byte-identical to
        # the pre-change render (empty {{ACCOUNT_PROGRAM}} reproduces the blank line)
        self.assertIn('</section>\n\n<section id="sequence">', html)
        self.assertNotIn("account-program", html)
        # no ap-*.html emitted
        self.assertFalse(any(f.startswith("ap-") for f in os.listdir(out)))

    def test_with_account_renders(self):
        d, sp, tp, ep, ap = _write_quad()
        out = os.path.join(d, "site")
        self.assertEqual(rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep,
                                  "--out", out, "--account-program", ap]), 0)
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn('id="account-program"', html)
        self.assertIn('href="#account-program">Account program</a>', html)
        # one cohort card per taxonomy row, one play card per play
        self.assertEqual(html.count('class="cohort"'), 3)
        self.assertEqual(html.count('class="test off"'), 2)
        # one ap-NN.html per play, each linking back to the account section
        files = set(os.listdir(out))
        self.assertIn("ap-01.html", files)
        self.assertIn("ap-02.html", files)
        with open(os.path.join(out, "ap-01.html")) as f:
            spoke = f.read()
        self.assertIn('href="index.html#account-program"', spoke)
        self.assertIn("Dormant reactivation sequence", spoke)

    def test_account_plays_not_on_map(self):
        d, sp, tp, ep, ap = _write_quad()
        out = os.path.join(d, "site")
        rs.main(["--strategic", sp, "--tactical", tp, "--edges", ep,
                 "--out", out, "--account-program", ap])
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        m = re.search(r'<svg id="pf-map".*?</svg>', html, re.S)
        self.assertIsNotNone(m)
        self.assertNotIn("ap-", m.group(0))


# --------------------------------------------------------------------------
# Measurement Foundation (unscored, keyless foundation entries)
# --------------------------------------------------------------------------
# The strategic gold roadmap may carry a `## Measurement Foundation` section
# (hypothesis-generator's Strategic Roadmap Output Format): bold-labeled
# entries, no `### N.` headings, no **Key:** / **Scores:**. Entries render as a
# hub section only: no spokes, no map presence, no gate participation.

STRATEGIC_MF = STRATEGIC.replace(
    "## Strategic Bets",
    """## Measurement Foundation

**Qualified-lead definition:** Define the qualified-lead event in the analytics
property. Step one: confirm whether the existing lead event already carries the
qualifying fields. Experiments 1 and 2 below depend on it.

- **Form-step instrumentation:** Instrument per-step form abandonment in the tag
manager; no step-level events exist today. Experiment 2 depends on it.

## Strategic Bets""", 1)


class TestFoundationParser(unittest.TestCase):
    def test_foundation_parsed_two_entries(self):
        s, _, _ = _load_all(strategic=STRATEGIC_MF)
        fnd = s["foundation"]
        self.assertEqual(len(fnd), 2)
        self.assertEqual(fnd[0]["label"], "Qualified-lead definition")
        self.assertIn("qualifying fields", fnd[0]["text"])
        # bullet form parses the same as paragraph form
        self.assertEqual(fnd[1]["label"], "Form-step instrumentation")
        self.assertIn("per-step form abandonment", fnd[1]["text"])
        # entries are keyless and unscored: label + text only, no item fields
        self.assertEqual(sorted(fnd[0].keys()), ["label", "text"])

    def test_no_foundation_section_empty_list(self):
        s, _, _ = _load_all()
        self.assertEqual(s["foundation"], [])

    def test_bets_unaffected_by_foundation_section(self):
        s, _, _ = _load_all(strategic=STRATEGIC_MF)
        self.assertEqual([b["id"] for b in s["bets"]], ["sb-01", "sb-02", "sb-03"])
        self.assertEqual(s["bets"][0]["key"], "speed-to-first-value")


class TestFoundationGate(unittest.TestCase):
    def test_foundation_entries_need_no_sidecar_binding(self):
        # The unchanged sidecar has no entries for the foundation entries; the
        # gate must pass (foundation entries are excluded from binding checks).
        s, t, sc = _load_all(strategic=STRATEGIC_MF)
        rs.run_gate(s, t, sc)  # should not raise

    def test_sidecar_edge_naming_foundation_entry_dangles(self):
        # An edge target naming a foundation entry is a dangling target (check
        # 2): foundation entries carry no keys, so nothing resolves.
        bad = SIDECAR.replace("{target: conversational-signup-form, type: gates}",
                              "{target: qualified-lead-definition, type: gates}")
        s, t, sc = _load_all(strategic=STRATEGIC_MF, sidecar=bad)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t, sc)
        self.assertTrue(any("[2]" in v and "qualified-lead-definition" in v
                            for v in cm.exception.violations),
                        "expected a [2] dangling-target violation naming the foundation "
                        "entry, got: %s" % cm.exception.violations)


class TestFoundationEndToEnd(unittest.TestCase):
    def _render(self, strategic=STRATEGIC, account=None):
        d, sp, tp, ep = _write_triple(strategic=strategic)
        out = os.path.join(d, "site")
        argv = ["--strategic", sp, "--tactical", tp, "--edges", ep, "--out", out]
        if account is not None:
            ap = os.path.join(d, "account.md")
            with open(ap, "w") as f:
                f.write(account)
            argv += ["--account-program", ap]
        rc = rs.main(argv)
        return rc, out

    def test_hub_foundation_section_between_strategy_and_backlog(self):
        rc, out = self._render(strategic=STRATEGIC_MF)
        self.assertEqual(rc, 0)
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn('id="measurement-foundation"', html)
        self.assertIn('href="#measurement-foundation">Measurement foundation</a>', html)
        self.assertEqual(html.count('class="mf"'), 2)
        self.assertIn("Qualified-lead definition", html)
        self.assertIn("Form-step instrumentation", html)
        # placed between the strategy section and the backlog section
        self.assertLess(html.index('id="strategy"'), html.index('id="measurement-foundation"'))
        self.assertLess(html.index('id="measurement-foundation"'), html.index('id="backlog"'))
        # no score chips inside the foundation section
        mf = re.search(r'<section id="measurement-foundation">.*?</section>', html, re.S).group(0)
        self.assertNotIn("ICE", mf)
        # entries get no spokes and no map presence
        self.assertFalse(any(f.startswith("mf-") for f in os.listdir(out)))
        svg = re.search(r'<svg id="pf-map".*?</svg>', html, re.S).group(0)
        self.assertNotIn("mf-", svg)

    def test_no_foundation_byte_identical_seam(self):
        rc, out = self._render()
        self.assertEqual(rc, 0)
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        # the seam between #strategy close and #backlog open is byte-identical
        # to the pre-change render (empty {{MEASUREMENT_FOUNDATION}} reproduces
        # the blank line), and no foundation chrome appears anywhere
        self.assertIn('</section>\n\n<section id="backlog">', html)
        self.assertNotIn("measurement-foundation", html)
        self.assertNotIn('class="mf"', html)

    def test_foundation_composes_with_account_program(self):
        rc, out = self._render(strategic=STRATEGIC_MF, account=ACCOUNT)
        self.assertEqual(rc, 0)
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn('id="measurement-foundation"', html)
        self.assertIn('id="account-program"', html)
        # ordering: strategy -> foundation -> backlog -> account program
        self.assertLess(html.index('id="measurement-foundation"'), html.index('id="backlog"'))
        self.assertLess(html.index('id="backlog"'), html.index('id="account-program"'))
        # both conditional nav links present
        self.assertIn('href="#measurement-foundation">Measurement foundation</a>', html)
        self.assertIn('href="#account-program">Account program</a>', html)


if __name__ == "__main__":
    unittest.main()
