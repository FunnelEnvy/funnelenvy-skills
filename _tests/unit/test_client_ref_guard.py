"""Unit tests for scripts/client_ref_guard.py (the public-repo client-reference guard).

The guard is heuristic (no client list): it flags the SHAPES of client data (corporate legal
suffixes, large money figures), exempts generic placeholders, and reports leak-safe locations only.
Covers the detectors, the allowlist, the leak-safe output contract, and each subcommand against a
temp git repo. All sample "client" strings here are synthetic.
"""
import importlib.util
import os
import subprocess
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stderr

_MODULE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "client_ref_guard.py")


def _load():
    spec = importlib.util.spec_from_file_location("client_ref_guard", _MODULE_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


g = _load()


def _hits(text):
    h = []
    g.scan_text("f.md", text, h)
    return h


class TestDetectors(unittest.TestCase):
    def test_corporate_suffix_flagged(self):
        for s in ("Northwind Traders Ltd", "Contoso Corporation", "Fabrikam GmbH",
                  "Globex N.V.", "Initech LLC", "Wingtip Toys Holdings"):
            self.assertTrue(_hits("we onboarded %s last quarter" % s), s)

    def test_detector_name_recorded(self):
        h = _hits("Contoso Corporation signed the SOW\n")
        self.assertEqual({d for _, _, d in h}, {"corporate-suffix"})

    def test_money_is_not_detected(self):
        # money is deliberately not a detector (instructional content cites it constantly)
        for s in ("value was $636.6M in window", "deal size >$25K ACV", "ARR is $12M not $8M",
                  "revenue_range: \"$50M-$5B\""):
            self.assertEqual(_hits(s), [], s)

    def test_common_words_not_flagged_in_prose(self):
        # the FP that motivated the run-requirement: a suffix word after lowercase prose
        for s in ("Detect from L0 only. Limited to patterns triggered by copy",
                  "these holdings are limited and incorporated into the plan",
                  "the company group co-owns the corp strategy"):
            self.assertEqual(_hits(s), [], s)

    def test_clean_prose_passes(self):
        clean = ("This skill reads L0 context and emits a roadmap. It uses Google Analytics "
                 "and Chrome DevTools. Benchmarks are relative, not absolute.\n")
        self.assertEqual(_hits(clean), [])

    def test_generic_placeholders_allowlisted(self):
        self.assertEqual(_hits("Acme Corp is our example client"), [])
        self.assertEqual(_hits("Example Corporation and FunnelEnvy"), [])


class TestLeakSafeOutput(unittest.TestCase):
    def test_report_never_echoes_matched_text(self):
        buf = StringIO()
        with redirect_stderr(buf):
            rc = g.report([("skills/x.md", 12, "corporate-suffix")])
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("skills/x.md:12", out)
        self.assertIn("corporate-suffix", out)
        # the flagged company-shaped text must never be in the output
        self.assertNotIn("Corporation", out)
        self.assertNotIn("Contoso", out)

    def test_report_clean(self):
        self.assertEqual(g.report([]), 0)


class _TempGitRepo:
    def __enter__(self):
        self.d = tempfile.mkdtemp()
        self.env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        subprocess.check_call(["git", "init", "-q"], cwd=self.d)
        return self

    def write(self, rel, content):
        p = os.path.join(self.d, rel)
        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
        return p

    def git(self, *args):
        subprocess.check_call(["git"] + list(args), cwd=self.d, env=self.env)

    def __exit__(self, *a):
        import shutil
        shutil.rmtree(self.d, ignore_errors=True)


def _run(argv, cwd):
    old = os.getcwd()
    try:
        os.chdir(cwd)
        buf = StringIO()
        with redirect_stderr(buf):
            try:
                rc = g.main(argv)
            except SystemExit as e:
                rc = e.code
        return rc, buf.getvalue()
    finally:
        os.chdir(old)


class TestSubcommands(unittest.TestCase):
    def test_scan_tree_hit_and_clean(self):
        with _TempGitRepo() as repo:
            repo.write("clean.md", "a generic note about the client\n")
            repo.git("add", "clean.md")
            self.assertEqual(_run(["scan-tree"], repo.d)[0], 0)
            repo.write("leak.md", "Contoso Corporation booked $636.6M\n")
            repo.git("add", "leak.md")
            rc, out = _run(["scan-tree"], repo.d)
            self.assertEqual(rc, 1)
            self.assertIn("leak.md:1", out)
            self.assertNotIn("Contoso", out)

    def test_scan_staged_only_sees_staged(self):
        with _TempGitRepo() as repo:
            repo.write("leak.md", "Initech LLC signed\n")
            self.assertEqual(_run(["scan-staged"], repo.d)[0], 0)  # unstaged -> clean
            repo.git("add", "leak.md")
            self.assertEqual(_run(["scan-staged"], repo.d)[0], 1)

    def test_scan_msg(self):
        with _TempGitRepo() as repo:
            ok = repo.write("MSG1", "fix: tidy the parser\n")
            self.assertEqual(_run(["scan-msg", ok], repo.d)[0], 0)
            bad = repo.write("MSG2", "feat: onboarding for Fabrikam GmbH\n")
            rc, out = _run(["scan-msg", bad], repo.d)
            self.assertEqual(rc, 1)
            self.assertIn("<commit-message>:1", out)


class TestSelfSkip(unittest.TestCase):
    def test_guard_test_file_is_skipped(self):
        # This very file carries synthetic company-shaped fixtures, so it must be exempt from scanning.
        self.assertTrue(g._skip("_tests/unit/test_client_ref_guard.py"))
        self.assertTrue(g._skip("a/b/_tests/unit/test_client_ref_guard.py"))
        self.assertFalse(g._skip("skills/foo/SKILL.md"))


class TestUsage(unittest.TestCase):
    def test_bad_subcommand(self):
        rc, out = _run(["bogus"], os.getcwd())
        self.assertEqual(rc, 2)
        self.assertIn("usage", out)


if __name__ == "__main__":
    unittest.main()
