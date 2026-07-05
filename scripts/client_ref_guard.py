#!/usr/bin/env python3
"""client_ref_guard.py -- block client-identifying content from entering this public repo.

This repo is public. The governing rule (see CLAUDE.md / CONTRIBUTING.md) is simple and absolute:
never write a real company or client name here. Use a generic placeholder (Acme, Example Corp,
"the client", "a private consumer engagement") or omit it. Humans and agents apply that rule by
inference on every line; this scanner is the mechanical backstop.

A backstop cannot "know" every company name without a world model, so it does NOT carry a list of
client names to maintain. Instead it flags the STRUCTURAL SHAPE that real client data takes here: a
run of capitalized words followed by a corporate legal suffix (e.g. "Acme Traders Ltd",
"Acme Corporation", "Example GmbH", "Sample N.V." if those were not placeholders). That catches the leak (account
rosters of named entities) with nothing to maintain.

Deliberately NOT detected: bare money figures. This repo teaches CRO/positioning and cites dollar
amounts constantly as instructional examples ($50K ACV, "$50M-$5B" ranges, "$12M ARR"), so a money
detector would flag legitimate content on nearly every skill doc. A revenue figure that IS a leak
almost always sits on a line with the company's name, which the suffix detector catches. Also not
detected: a bare codename or unsuffixed name -- only the authoring rule and review catch those, since
recognizing an arbitrary company name needs a human/agent, not a regex.

Leak-safe: on a hit the scanner reports the file, the line number, and which detector fired -- never
the matched text. CI logs and terminals can be public; echoing the flagged string would re-leak it.

Subcommands:
  scan-staged      scan the staged blob of each added/copied/modified tracked path (pre-commit)
  scan-msg <file>  scan a commit-message file (commit-msg hook)
  scan-tree        scan every tracked file (CI backstop and manual audits)

Stdlib only. Exit 0 clean, 1 on a hit, 2 on usage error.
"""

import os
import re
import subprocess
import sys

# --------------------------------------------------------------------------
# Heuristic detectors (no client list; match the SHAPE of client data)
# --------------------------------------------------------------------------

# Corporate legal suffixes. Matched only after a contiguous run of Capitalized words, so real
# company names ("Example GmbH", "Sample N.V.") fire but ordinary prose that merely contains a
# word like "Limited" or "Holdings" does not (that word won't be preceded by a capitalized run).
# Each capitalized token may carry a trailing comma so the dominant US legal style
# ("Acme, Inc.", "Acme Traders, LLC") is caught, not just the comma-less form.
_SUFFIX = (r"Inc|Incorporated|LLC|L\.L\.C|Ltd|Limited|Corp|Corporation|Co|GmbH|AG|PLC|"
           r"N\.V\.|S\.A\.|S\.p\.A|A/S|S\.?[àa]\.?r\.?l|Sarl|Aktiengesellschaft|Holdings?")
CORP_SUFFIX_RX = re.compile(
    r"\b(?:[A-Z][\w.&'À-ſ\-]*,?\s+){1,5}(?:%s)\.?(?![A-Za-z0-9])" % _SUFFIX)

DETECTORS = (("corporate-suffix", CORP_SUFFIX_RX),)

# Generic placeholders / this org's own names: a match containing one of these is exempt. These are
# not client names and are safe to hardcode. False positives are acceptable, so this stays minimal.
ALLOW = ("acme", "example", "sample", "placeholder", "funnelenvy", "growthnode", "your company",
         "company name", "companyname", "widget")


def _allowed(matched_text):
    low = matched_text.lower()
    return any(tok in low for tok in ALLOW)


# The guard's own test file must contain synthetic, non-placeholder company names (fictional ones
# that are not on the allowlist) to prove the detector fires -- so it is the one tracked file exempt
# from scanning. The names in it are fictional; the file is small and reviewed. Nothing else is exempt.
SKIP_SUFFIXES = ("_tests/unit/test_client_ref_guard.py",)


def _skip(path):
    return any(path.endswith(s) for s in SKIP_SUFFIXES)


def scan_text(label, text, hits):
    """Append (label, line_number, detector_name) for every detector match on every line.
    Leak-safe: records the detector name and location, never the matched substring."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, rx in DETECTORS:
            for m in rx.finditer(line):
                if not _allowed(m.group(0)):
                    hits.append((label, lineno, name))
                    break  # one hit per detector per line is enough to flag it


# --------------------------------------------------------------------------
# git plumbing
# --------------------------------------------------------------------------

def repo_root():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                      stderr=subprocess.DEVNULL)
        return out.decode("utf-8", "replace").strip()
    except (subprocess.CalledProcessError, OSError):
        return os.getcwd()


def _git_lines(args):
    out = subprocess.check_output(["git"] + args, stderr=subprocess.DEVNULL)
    return [l for l in out.decode("utf-8", "replace").splitlines() if l]


def _git_show(spec):
    try:
        raw = subprocess.check_output(["git", "show", spec], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    if b"\x00" in raw:  # skip binary blobs
        return None
    return raw.decode("utf-8", "replace")


def scan_staged():
    hits = []
    for path in _git_lines(["diff", "--cached", "--name-only", "--diff-filter=ACM"]):
        if _skip(path):
            continue
        content = _git_show(":" + path)
        if content is not None:
            scan_text(path, content, hits)
    return hits


def scan_tree():
    hits = []
    root = repo_root()
    for path in _git_lines(["ls-files"]):
        if _skip(path):
            continue
        try:
            with open(os.path.join(root, path), "rb") as fh:
                raw = fh.read()
        except OSError:
            continue
        if b"\x00" in raw:
            continue
        scan_text(path, raw.decode("utf-8", "replace"), hits)
    return hits


def scan_msg(msg_path):
    if not os.path.isfile(msg_path):
        sys.stderr.write("client-ref-guard: commit-message file not found: %s\n" % msg_path)
        return []
    with open(msg_path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    hits = []
    scan_text("<commit-message>", text, hits)
    return hits


def report(hits):
    """Print leak-safe hit locations to stderr. Returns exit code."""
    if not hits:
        return 0
    sys.stderr.write("client-ref-guard: BLOCKED %d likely client-reference hit%s "
                     "(matched text withheld; open the file at the line to see it):\n"
                     % (len(hits), "" if len(hits) == 1 else "s"))
    for label, line_no, detector in hits:
        sys.stderr.write("  - %s:%d flagged by %s\n" % (label, line_no, detector))
    sys.stderr.write("  Rule: never write a real company name in this public repo -- use a fake "
                     "placeholder (Acme, Example Corp, \"the client\") or remove it.\n"
                     "  If this is a genuine false positive, rephrase or add a placeholder token.\n")
    return 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("scan-staged", "scan-msg", "scan-tree"):
        sys.stderr.write("usage: client_ref_guard.py {scan-staged|scan-msg <file>|scan-tree}\n")
        return 2
    cmd = argv[0]
    if cmd == "scan-staged":
        return report(scan_staged())
    if cmd == "scan-tree":
        return report(scan_tree())
    if cmd == "scan-msg":
        if len(argv) < 2:
            sys.stderr.write("usage: client_ref_guard.py scan-msg <commit-msg-file>\n")
            return 2
        return report(scan_msg(argv[1]))
    return 2


if __name__ == "__main__":
    sys.exit(main())
