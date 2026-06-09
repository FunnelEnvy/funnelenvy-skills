#!/usr/bin/env python3
"""
content_hash - deterministic recapture-diff hash for a captured page.

Hashes a page's H1 plus its structural skeleton (the ordered list of H2/H3
headings) so a later capture can cheaply detect whether the page changed.
Stdlib only. Invoked by the live-capture skill's capture phase.

Usage:
    content_hash.py --h1 "Welcome" --skeleton "Features\\nPricing\\nFAQ"
    echo "Features\\nPricing" | content_hash.py --h1 "Welcome" --skeleton -

Output (JSON to stdout): {"content_hash": "<16-hex>"}

The hash is stable across runs and machines: inputs are whitespace-normalized
(each line trimmed, blank lines dropped, CRLF/CR normalized to LF) before
hashing, so cosmetic whitespace churn does not change the hash but a real
heading change does.
"""
import argparse
import hashlib
import json
import sys

HASH_LEN = 16  # hex chars; 64 bits of sha256 is ample for change detection


def _normalize(text):
    """Trim each line, drop blank lines, normalize newlines. Deterministic."""
    if text is None:
        text = ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def content_hash(h1, skeleton):
    """Return a stable short hex hash of the normalized H1 + skeleton.

    h1 and skeleton are normalized independently then joined with a record
    separator that cannot appear in normalized line content, so that moving a
    line between the two inputs still changes the hash.
    """
    payload = _normalize(h1) + "\x1e" + _normalize(skeleton)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest[:HASH_LEN]


def _read_arg(value):
    """A literal '-' means read this argument's value from stdin."""
    if value == "-":
        return sys.stdin.read()
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deterministic page recapture-diff hash.")
    parser.add_argument("--h1", default="", help="Page H1 text (or '-' to read from stdin).")
    parser.add_argument(
        "--skeleton",
        default="",
        help="Ordered H2/H3 headings, newline-separated (or '-' to read from stdin).",
    )
    args = parser.parse_args(argv)

    h1 = _read_arg(args.h1)
    skeleton = _read_arg(args.skeleton)
    print(json.dumps({"content_hash": content_hash(h1, skeleton)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
