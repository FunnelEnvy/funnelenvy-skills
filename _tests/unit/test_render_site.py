"""Unit tests for render-program-site render_site.py (deterministic core).

Covers the minimal YAML parser, the 7-check edge-contract gate, derived data
(reverse edges, intake, map coordinates, edge classes, tier grouping), the
display helpers, and end-to-end emit (page count, determinism, relative refs,
no client content). All fixtures are synthetic (non-client).
"""
import importlib.util
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
# Synthetic fixtures (non-client)
# --------------------------------------------------------------------------

STRATEGIC = """---
program:
  client: "Acme Robotics"
  name: "Acme Growth Program"
  program_version: "1.0.0"
  date: "2026-06-24"
  hero:
    eyebrow: "Acme Growth Program"
    headline: "Turning 50,000 trials into revenue."
    headline_num: "50,000"
    subhead: "Pairing program moves with the page tests that execute them."
bets:
  - id: sb-01
    title: "Speed to first value"
    lever: "Time to activation"
    decided_on: "trial-to-paid"
    run_tag: "Run first"
    delivery_surface: [routing]
    executor_status: off-page
    ice: {i: 5, c: 4, e: 2}
    keystone: false
    edges:
      - {target: p-02, type: informs}
  - id: sb-02
    title: "Proof and ROI"
    lever: "Named-customer proof"
    decided_on: "evaluation conversion"
    run_tag: "Keystone"
    delivery_surface: [proof, copy]
    executor_status: on-page
    ice: {i: 5, c: 4, e: 2}
    keystone: true
    edges:
      - {target: p-01, type: expresses}
      - {target: p-02, type: informs}
  - id: sb-03
    title: "Offer ladder"
    lever: "Commitment ladder"
    decided_on: "pipeline entry"
    delivery_surface: [offer]
    executor_status: unexpressed
    ice: {i: 4, c: 3, e: 3}
    keystone: false
    edges:
      - {target: p-02, type: gates}
---
# Acme: Strategic Experiment Roadmap

## SB-1. Speed to first value
**The lever.** Activation time is the dominant lever.

**The experiment / program.** Reduce time-to-first-value via routing.

## SB-2. Proof and ROI
**The lever.** Buyers need proof from peers like them.

**What must be stood up.** Named-customer outcome data.

## SB-3. Offer ladder
**The lever.** One high-commitment ask suppresses entry.

## Sequencing
Run speed-to-value first; build the proof asset in parallel.
"""

TACTICAL = """---
program_version: "1.0.0"
tests:
  - {id: p-01, title: "Proof block on pricing", mechanism_class: proof, tier: exploration, ice: {i: 3, c: 3, e: 3}, target_page: "Pricing", status: active, mockup: {screenshot: "mockups/p-01/screenshot.png", html: "mockups/p-01/mockup.html", mode: "chrome-devtools", target_url: "acme.example/pricing", insertion_point: "Below the fold", placement_summary: "Sits where doubt peaks."}}
  - {id: p-02, title: "Conversational signup form", mechanism_class: form, tier: strategic-bet, ice: {i: 4, c: 4, e: 3}, target_page: "Signup", status: active}
  - {id: p-03, title: "Intake-only CTA label test", mechanism_class: cta, tier: quick-win, ice: {i: 3, c: 4, e: 4}, target_page: "Sitewide", status: active}
  - {id: p-04, title: "Old form test", mechanism_class: form, tier: strategic-bet, ice: {i: 4, c: 3, e: 3}, target_page: "Signup", status: superseded, superseded_by: "v2.1"}
---
# Acme: Experiment Roadmap

### 1. Proof block on pricing
**The hypothesis.** Preempting objections lifts conversion.

### 2. Conversational signup form
**The hypothesis.** A conversational form reduces friction.

### 3. Intake-only CTA label test
**The hypothesis.** Clearer CTA labels raise click-through.
"""


def _write_pair(strategic=STRATEGIC, tactical=TACTICAL):
    d = tempfile.mkdtemp()
    sp = os.path.join(d, "strategic.md")
    tp = os.path.join(d, "tactical.md")
    with open(sp, "w") as f:
        f.write(strategic)
    with open(tp, "w") as f:
        f.write(tactical)
    return d, sp, tp


def _load_pair(strategic=STRATEGIC, tactical=TACTICAL):
    _, sp, tp = _write_pair(strategic, tactical)
    return rs.load_strategic(sp), rs.load_tactical(tp)


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------

class TestParser(unittest.TestCase):
    def test_nested_block_map(self):
        fm, _ = rs.parse_frontmatter(STRATEGIC)
        self.assertEqual(fm["program"]["client"], "Acme Robotics")
        self.assertEqual(fm["program"]["hero"]["headline_num"], "50,000")

    def test_block_seq_of_maps_and_inline_flow(self):
        fm, _ = rs.parse_frontmatter(STRATEGIC)
        bet = fm["bets"][1]
        self.assertEqual(bet["id"], "sb-02")
        self.assertEqual(bet["ice"], {"i": 5, "c": 4, "e": 2})
        self.assertEqual(bet["delivery_surface"], ["proof", "copy"])
        self.assertEqual(bet["edges"][0], {"target": "p-01", "type": "expresses"})
        self.assertTrue(bet["keystone"] is True)

    def test_inline_flow_test_with_nested_mockup(self):
        fm, _ = rs.parse_frontmatter(TACTICAL)
        t = fm["tests"][0]
        self.assertEqual(t["mechanism_class"], "proof")
        self.assertEqual(t["mockup"]["mode"], "chrome-devtools")

    def test_body_section_extraction(self):
        _, body = rs.parse_frontmatter(STRATEGIC)
        secs = rs.extract_sections(body, "bet")
        self.assertIn("sb-02", secs)
        self.assertEqual(secs["sb-02"]["labels"]["The lever"], "Buyers need proof from peers like them.")


# --------------------------------------------------------------------------
# Gate (7 checks)
# --------------------------------------------------------------------------

class TestGate(unittest.TestCase):
    def test_valid_passes(self):
        s, t = _load_pair()
        rs.run_gate(s, t)  # should not raise

    def _expect_violation(self, strategic, tactical, code):
        s, t = _load_pair(strategic, tactical)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t)
        self.assertTrue(any(code in v for v in cm.exception.violations),
                        "expected a %s violation, got: %s" % (code, cm.exception.violations))

    def test_check1_bad_edge_type(self):
        bad = STRATEGIC.replace("{target: p-02, type: informs}", "{target: p-02, type: bogus}")
        self._expect_violation(bad, TACTICAL, "[1]")

    def test_check2_dangling_target(self):
        bad = STRATEGIC.replace("{target: p-01, type: expresses}", "{target: p-99, type: expresses}")
        self._expect_violation(bad, TACTICAL, "[2]")

    def test_check3_mechanism_mismatch(self):
        # sb-01 (routing) expresses p-03 (cta) -> routing vs cta mismatch
        bad = STRATEGIC.replace("{target: p-02, type: informs}", "{target: p-03, type: expresses}")
        s, t = _load_pair(bad, TACTICAL)
        with self.assertRaises(rs.GateError) as cm:
            rs.run_gate(s, t)
        joined = " ".join(cm.exception.violations)
        self.assertIn("[3]", joined)
        self.assertIn("routing", joined)
        self.assertIn("cta", joined)

    def test_check4_executor_status_mismatch(self):
        # sb-01 declared off-page but given an expresses edge to a matching surface
        bad = STRATEGIC.replace("delivery_surface: [routing]", "delivery_surface: [proof]")
        bad = bad.replace("{target: p-02, type: informs}", "{target: p-01, type: expresses}")
        self._expect_violation(bad, TACTICAL, "[4]")

    def test_check6_tactical_authors_reverse(self):
        bad = TACTICAL.replace('"Signup", status: active}',
                               '"Signup", status: active, expressed_by: [sb-02]}')
        self._expect_violation(STRATEGIC, bad, "[6]")

    def test_check7_version_skew(self):
        bad = TACTICAL.replace('program_version: "1.0.0"', 'program_version: "1.0.1"')
        self._expect_violation(STRATEGIC, bad, "[7]")


# --------------------------------------------------------------------------
# Derivation
# --------------------------------------------------------------------------

class TestDerive(unittest.TestCase):
    def setUp(self):
        self.s, self.t = _load_pair()
        rs.run_gate(self.s, self.t)
        self.d = rs.derive(self.s, self.t)
        self.tests = {t["id"]: t for t in self.t["tests"]}

    def test_reverse_edges(self):
        p2 = self.tests["p-02"]
        self.assertEqual(p2["exp_by"], [])
        self.assertEqual(sorted(p2["inf_by"]), ["sb-01", "sb-02", "sb-03"])
        self.assertEqual(self.tests["p-01"]["exp_by"], ["sb-02"])

    def test_intake_flag(self):
        self.assertTrue(self.tests["p-03"]["intake_only"])
        self.assertFalse(self.tests["p-01"]["intake_only"])

    def test_map_coords_pure_function_of_ie(self):
        # base position is a pure lerp of (I, E); verify the un-dodged singleton.
        p1 = self.tests["p-01"]  # I3 E3 -> center
        self.assertEqual((p1["cx"], p1["cy"]), (int(round(rs.x_of(3))), int(round(rs.y_of(3)))))

    def test_tie_dodge_separates_shared_cell(self):
        bets = {b["id"]: b for b in self.s["bets"]}
        a, b = bets["sb-01"], bets["sb-02"]  # both I5 E2
        self.assertNotEqual((a["cx"], a["cy"]), (b["cx"], b["cy"]))

    def test_tier_grouping_and_superseded(self):
        g = self.d["tier_groups"]
        self.assertEqual([t["id"] for t in g["quick-win"]], ["p-03"])
        self.assertEqual([t["id"] for t in g["exploration"]], ["p-01"])
        self.assertEqual([t["id"] for t in self.d["superseded"]], ["p-04"])

    def test_edge_class_split(self):
        b2 = {b["id"]: b for b in self.s["bets"]}["sb-02"]
        self.assertEqual(b2["expresses"], ["p-01"])     # solid
        self.assertEqual(b2["influences"], ["p-02"])    # dashed (informs)


# --------------------------------------------------------------------------
# Display helpers
# --------------------------------------------------------------------------

class TestHelpers(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(rs.bet_label("sb-02"), "SB-2")
        self.assertEqual(rs.test_num("p-10"), "10")
        self.assertEqual(rs.ice_total({"i": 5, "c": 4, "e": 2}), 11)


# --------------------------------------------------------------------------
# End-to-end emit
# --------------------------------------------------------------------------

class TestEndToEnd(unittest.TestCase):
    def _render(self):
        d, sp, tp = _write_pair()
        out = os.path.join(d, "site")
        rc = rs.main(["--strategic", sp, "--tactical", tp, "--out", out])
        return rc, out

    def test_exit_zero_and_page_count(self):
        rc, out = self._render()
        self.assertEqual(rc, 0)
        files = set(os.listdir(out))
        # hub + 3 bets + 3 live tests + 2 assets; superseded p-04 omitted
        for f in ("index.html", "sb-01.html", "sb-02.html", "sb-03.html",
                  "p-01.html", "p-02.html", "p-03.html", "styles.css", "site.js"):
            self.assertIn(f, files)
        self.assertNotIn("p-04.html", files)

    def test_gate_failure_exit_nonzero(self):
        bad = TACTICAL.replace('program_version: "1.0.0"', 'program_version: "9.9.9"')
        d, sp, tp = _write_pair(STRATEGIC, bad)
        out = os.path.join(d, "site")
        self.assertNotEqual(rs.main(["--strategic", sp, "--tactical", tp, "--out", out]), 0)

    def test_deterministic_output(self):
        d, sp, tp = _write_pair()
        o1, o2 = os.path.join(d, "a"), os.path.join(d, "b")
        rs.main(["--strategic", sp, "--tactical", tp, "--out", o1])
        rs.main(["--strategic", sp, "--tactical", tp, "--out", o2])
        with open(os.path.join(o1, "index.html")) as a, open(os.path.join(o2, "index.html")) as b:
            self.assertEqual(a.read(), b.read())

    def test_relative_refs_no_client_content(self):
        rc, out = self._render()
        with open(os.path.join(out, "index.html")) as f:
            html = f.read()
        self.assertIn('href="styles.css"', html)
        self.assertIn('src="site.js"', html)
        self.assertNotIn("http://", html.replace("http://www.w3.org", ""))  # no external links but SVG ns
        # synthetic client present; a real-client denylist token (reassembled) absent
        self.assertIn("Acme Robotics", html)
        self.assertNotIn("S&P" + " Global", html)

    def test_absent_mockup_section_omitted(self):
        rc, out = self._render()
        with open(os.path.join(out, "p-02.html")) as f:
            self.assertNotIn("Proposed change", f.read())
        with open(os.path.join(out, "p-01.html")) as f:
            self.assertIn("Proposed change", f.read())


if __name__ == "__main__":
    unittest.main()
