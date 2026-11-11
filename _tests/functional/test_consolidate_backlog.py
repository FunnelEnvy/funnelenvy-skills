"""Functional tests for hypothesis-generator consolidate_backlog.py (CLI contract).

Card, row and posture files are written with tempfile for a fictional "Acme". Case
design: hypothesis-generator-opportunity-backlog-rebuild (R1, R2, R7, R8).
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "skills", "hypothesis-generator", "scripts",
    "consolidate_backlog.py"
)

POSTURE = """## Decision Posture

| Constant | Default | Cited by |
|---|---|---|
| Significance (two-sided confidence) | 0.90 | sizing |
| Power | 0.80 | sizing |
| Multiplier M = 2(z_sig + z_power)^2 | 12.37 | sizing |
| Relative MDE | 0.20 | sizing |
| Maximum A/B read window | 26 weeks | sizing |
| Hard gates | 100 conversions per variant; 7-day minimum | sizing |
"""

CARD = {
    "lens": "surface",
    "altitude": "tactical",
    "title": "Pricing proof strip",
    "surfaces": ["/pricing"],
    "mechanism_key": "proof-near-cta",
    "mechanism": "Proof beside the CTA lowers perceived risk.",
    "evidence": ["performance profile, pricing page row"],
    "baseline": {"monthly_sessions": 5000, "rate": 0.02, "window_start": None, "source": "profile"},
}

R7_KEYS = {"posture", "rows", "lens_counts", "lens_shortfalls", "cards_in", "rows_out",
           "dropped_prior_keys"}


class TestCli(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, content):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content if isinstance(content, str) else json.dumps(content))
        return path

    def cli(self, *args):
        return subprocess.run([sys.executable, _SCRIPT] + list(args), capture_output=True,
                              encoding="utf-8")

    def test_cli_consolidate_json(self):
        result = self.cli("consolidate", "--cards", self.write("cards.json", [CARD]),
                          "--posture", self.write("posture.md", POSTURE))
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(set(out), R7_KEYS)
        self.assertEqual(out["rows"][0]["read_model"], "ab")

    def test_cli_bad_card_exit_1(self):
        bad = dict(CARD, lens="unknown")
        result = self.cli("consolidate", "--cards", self.write("cards.json", [CARD, bad]),
                          "--posture", self.write("posture.md", POSTURE))
        self.assertEqual(result.returncode, 1)
        self.assertIn("card 1", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cli_posture_unreadable_exit_3(self):
        result = self.cli("consolidate", "--cards", self.write("cards.json", [CARD]),
                          "--posture", self.write("posture.md", "# No posture table here\n"))
        self.assertEqual(result.returncode, 3)
        self.assertIn("Decision Posture", result.stderr)

    def test_cli_rank_json(self):
        row = {"key": "pricing-proof", "altitude": "tactical", "read_model": "ab", "blockers": [],
               "history_items": ["I1"], "ice": {"i": 3, "c": 3, "e": 3}}
        result = self.cli("rank", "--rows", self.write("rows.json", [row]), "--write-ups", "8",
                          "--history-items", "I1")
        self.assertEqual(result.returncode, 0, result.stderr)
        ranked = json.loads(result.stdout)["rows"][0]
        self.assertEqual((ranked["readiness"], ranked["rank"], ranked["write_up"]),
                         ("ready-now", 1, True))

    def test_cli_write_ups_out_of_range(self):
        result = self.cli("rank", "--rows", self.write("rows.json", []), "--write-ups", "13")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--write-ups", result.stderr)

    def test_posture_reads_shipped_skill_md(self):
        result = self.cli("consolidate", "--cards", self.write("cards.json", [CARD]))
        self.assertEqual(result.returncode, 0, result.stderr)
        p = json.loads(result.stdout)["posture"]
        self.assertEqual((p["significance"], p["power"], p["relative_mde"]), (0.90, 0.80, 0.20))
        self.assertEqual((p["max_ab_weeks"], p["min_conversions_per_variant"], p["min_days"]),
                         (26, 100, 7))


if __name__ == "__main__":
    unittest.main()
