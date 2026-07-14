#!/usr/bin/env python3
"""render_site.py -- deterministic two-altitude program-site generator.

Pipeline: parse two markdown inputs (strategic layer + tactical roadmap) ->
validate the cross-altitude edge contract (hard gate, fail-closed) -> derive
reverse edges, intake flags, Impact-by-Ease map coordinates, edge classes and
tier groups -> emit a static site (styles.css + site.js + index.html hub +
sb-NN/p-NN spokes) from templates.

This is the deterministic, drift-proof half of the render-program-site skill.
Everything here is a pure function of the input data: the gate, the map
coordinates, edge typing, the chrome, and all data-bound structure (badges,
ICE, chips, links). The script authors NO prose -- spoke prose regions are
emitted as labeled HTML-comment slots, pre-filled with the verbatim source
section text as raw material, that the skill's LLM curation pass rewrites.
The script never calls an LLM and never touches the network.

Stdlib only (no pip dependencies). Exit 0 on success, non-zero on gate failure.
"""

import argparse
import html
import os
import re
import sys

# --------------------------------------------------------------------------
# Contract constants
# --------------------------------------------------------------------------

EDGE_TYPES = ("expresses", "informs", "gates")
# Delivery surfaces that cannot be expressed on a page (operational only).
# A bet whose surfaces are all off-page and which ships no `expresses` edge is
# legitimately `off-page`; anything else with no expresses edge is `unexpressed`.
OFF_PAGE_SURFACES = frozenset({"routing"})
EXECUTOR_STATUSES = ("on-page", "off-page", "unexpressed")

# Tier metadata: key -> (display label, css suffix, count caption).
TIERS = {
    "quick-win": ("Quick Wins", "qw", "high confidence, fast signal"),
    "strategic-bet": ("Strategic Bets", "sb", "higher effort, higher payoff"),
    "exploration": ("Explorations", "ex", "lower confidence, high learning"),
}
TIER_ORDER = ("quick-win", "strategic-bet", "exploration")

# Type-label map, printed verbatim, never paraphrased (bet side / test side).
EDGE_LABEL_BET = {"expresses": "Expressed on-page by", "informs": "Informs", "gates": "Gates"}
EDGE_LABEL_TEST = {"expresses": "Expresses", "informs": "Informed by", "gates": "Gated by"}
SOLID_TYPES = frozenset({"expresses"})  # -> pf-link / chip ; others -> pf-link-soft / chip soft

# Impact-by-Ease plot geometry (matches the frozen comps' viewBox 0 0 760 470).
PLOT_LEFT, PLOT_RIGHT, PLOT_TOP, PLOT_BOTTOM = 88, 712, 60, 372
GRID_X = (88, 244, 400, 556, 712)   # E = 1..5
GRID_Y = (60, 138, 216, 294, 372)   # I = 5..1


def x_of(ease):
    return PLOT_LEFT + (ease - 1) / 4.0 * (PLOT_RIGHT - PLOT_LEFT)


def y_of(impact):
    return PLOT_TOP + (5 - impact) / 4.0 * (PLOT_BOTTOM - PLOT_TOP)


class GateError(Exception):
    """Raised when the edge-contract gate fails. Carries the offending records."""

    def __init__(self, violations):
        self.violations = violations
        super().__init__("edge-contract gate failed")


# --------------------------------------------------------------------------
# Minimal YAML frontmatter parser (constrained block subset + single-line flow)
# --------------------------------------------------------------------------
# Supports exactly what the migrated source frontmatter uses: nested block
# mappings, block sequences of scalars or mappings, single-line inline flow
# maps `{k: v, ...}` and flow sequences `[a, b]`, quoted/plain scalars, ints,
# floats and booleans. Multi-line flow is intentionally unsupported (the source
# migration is authored in this subset); anything unparseable raises, fail-loud.

def _scalar(tok):
    tok = tok.strip()
    if tok == "" or tok == "~" or tok == "null":
        return None
    if len(tok) >= 2 and tok[0] in "\"'" and tok[-1] == tok[0]:
        return tok[1:-1]
    low = tok.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if re.fullmatch(r"-?\d+\.\d+", tok):
        return float(tok)
    return tok


def _split_flow(body):
    """Split the inside of a flow collection on top-level commas only, ignoring
    commas inside quoted strings or nested brackets/braces."""
    parts, depth, cur, q = [], 0, "", None
    for ch in body:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in "\"'":
            q = ch
            cur += ch
        elif ch in "[{":
            depth += 1
            cur += ch
        elif ch in "]}":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def _parse_flow(tok):
    tok = tok.strip()
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        return [] if not inner else [_parse_flow(p) for p in _split_flow(inner)]
    if tok.startswith("{") and tok.endswith("}"):
        inner = tok[1:-1].strip()
        out = {}
        if inner:
            for p in _split_flow(inner):
                if ":" not in p:
                    raise ValueError("malformed flow map entry: %r" % p)
                k, v = p.split(":", 1)
                out[k.strip()] = _parse_flow(v)
        return out
    return _scalar(tok)


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def _parse_block(lines, idx, parent_indent):
    """Parse the child block of a key/list-item. Returns (value, next_idx).

    The child's own indent is discovered from its first content line and must be
    strictly greater than the parent's indent; otherwise there is no child.
    """
    while idx < len(lines) and (not lines[idx].strip() or lines[idx].lstrip().startswith("#")):
        idx += 1
    if idx >= len(lines):
        return None, idx
    ci = _indent(lines[idx])
    if ci <= parent_indent:
        return None, idx
    if lines[idx].lstrip().startswith("- "):
        return _parse_seq(lines, idx, ci)
    return _parse_map(lines, idx, ci)


def _parse_map(lines, idx, indent):
    out = {}
    while idx < len(lines):
        raw = lines[idx]
        if not raw.strip() or raw.lstrip().startswith("#"):
            idx += 1
            continue
        ind = _indent(raw)
        if ind < indent:
            break
        if ind > indent:
            raise ValueError("unexpected indent at line %d: %r" % (idx + 1, raw))
        if raw.lstrip().startswith("- "):
            break
        m = re.match(r"([^:]+):(.*)$", raw.strip())
        if not m:
            raise ValueError("expected 'key: value' at line %d: %r" % (idx + 1, raw))
        key, rest = m.group(1).strip(), m.group(2).strip()
        if rest in (">", "|", ">-", ">+", "|-", "|+"):
            # block scalar (folded `>` or literal `|`): consume the indented body
            style = rest[0]
            block, j = [], idx + 1
            while j < len(lines):
                ln = lines[j]
                if ln.strip() == "":
                    block.append("")
                    j += 1
                    continue
                if _indent(ln) <= indent:
                    break
                block.append(ln)
                j += 1
            nonblank = [l for l in block if l.strip()]
            base = min((_indent(l) for l in nonblank), default=0)
            dedented = [l[base:] if len(l) >= base else l.strip() for l in block]
            if style == ">":
                out[key] = " ".join(s.strip() for s in dedented if s.strip())
            else:
                out[key] = "\n".join(dedented).strip("\n")
            idx = j
        elif rest == "":
            child, idx = _parse_block(lines, idx + 1, indent)
            out[key] = child
        else:
            out[key] = _parse_flow(rest)
            idx += 1
    return out, idx


def _parse_seq(lines, idx, indent):
    out = []
    while idx < len(lines):
        raw = lines[idx]
        if not raw.strip() or raw.lstrip().startswith("#"):
            idx += 1
            continue
        ind = _indent(raw)
        if ind < indent or not raw.lstrip().startswith("- "):
            break
        if ind > indent:
            raise ValueError("unexpected indent at line %d: %r" % (idx + 1, raw))
        item = raw.lstrip()[2:]
        if item.strip() == "":
            child, idx = _parse_block(lines, idx + 1, indent)
            out.append(child)
        elif re.match(r"[^:]+:", item) and not item.strip().startswith("{"):
            # Inline mapping that begins on the dash line; treat the dash as a
            # 2-space indent bump and re-parse the mapping block.
            synthetic = [" " * (indent + 2) + item] + lines[idx + 1:]
            child, consumed = _parse_map(synthetic, 0, indent + 2)
            out.append(child)
            idx = idx + 1 + (consumed - 1)
        else:
            out.append(_parse_flow(item))
            idx += 1
    return out, idx


def parse_frontmatter(text, required=True):
    """Return (frontmatter_dict, body_text).

    With required=True (the default), a file that does not open with `---`
    raises: the sidecar is frontmatter-only, so its load stays strict. Roadmap
    and deliverable inputs pass required=False, because legacy-mode
    hypothesis-generator roadmaps carry no YAML frontmatter by design (the L2
    body-purity rule): such a file loads as ({}, full_text)."""
    if not text.startswith("---"):
        if not required:
            return {}, text
        raise ValueError("file has no YAML frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unterminated frontmatter block")
    fm = text[3:end].strip("\n")
    body = text[end + 4:]
    lines = fm.split("\n")
    for i, ln in enumerate(lines):
        if ln[:len(ln) - len(ln.lstrip())].find("\t") != -1:
            raise ValueError("frontmatter line %d uses tab indentation; this parser "
                             "supports space indentation only" % (i + 1))
    data, _ = _parse_map(lines, 0, 0)
    return data, body


# --------------------------------------------------------------------------
# Gold-roadmap body parsing (sections, tiers, Key, Scores -- raw material)
# --------------------------------------------------------------------------
# render-program-site consumes hypothesis-generator's prose gold roadmaps
# (gold-experiment-roadmap / gold-strategic-roadmap). Both altitudes use the
# same body shape: `### N. Title` experiment sections nested under tier H2s
# (`## Quick Wins` / `## Strategic Bets` / `## Explorations`), each carrying a
# `**Key:** <slug>` line, a `**Scores:** Impact X | Confidence Y | Ease Z` line,
# and bold-labeled prose paragraphs. The structured contract data (id, key,
# title, tier, ICE, page) is DERIVED from this body; only the cross-altitude
# edge binding is authored, in the sidecar.

# Tier H2 heading text -> tier key. Anything else is a non-tier H2.
TIER_HEADINGS = (
    ("quick win", "quick-win"),
    ("strategic bet", "strategic-bet"),
    ("exploration", "exploration"),
)


def _tier_key(heading):
    h = heading.strip().lower()
    for prefix, key in TIER_HEADINGS:
        if h.startswith(prefix):
            return key
    return None


def parse_scores(text):
    """Parse `Impact X | Confidence Y | Ease Z` (anywhere in `text`) -> {i,c,e}.

    The gold `**Scores:**` line is followed inline by a rationale sentence; the
    leading triple is matched and the trailing prose ignored. Returns None when
    no scores triple is present.
    """
    if not text:
        return None
    m = re.search(r"impact\s+(\d+)\s*\|\s*confidence\s+(\d+)\s*\|\s*ease\s+(\d+)", text, re.I)
    if not m:
        return None
    return {"i": int(m.group(1)), "c": int(m.group(2)), "e": int(m.group(3))}


def extract_sections(body, kind):
    """Split a gold-roadmap body into per-experiment sections keyed by canonical id.

    Returns {id: {"title", "key", "tier", "labels": {label: text}, "paras": [..]}}.
    `kind` is "bet" (id prefix `sb`), "test" (id prefix `p`), or "play" (id prefix
    `ap`, the account-program altitude). `tier` is the enclosing tier H2. Bold-labeled
    paragraphs (`**Label:** text` or `**Label.** text`) are collected into
    `labels` with the trailing `:`/`.` stripped; `**Key:**` is also surfaced as
    `key`. Numbered sections only appear under tier H2s in the gold format, so a
    numbered heading reached while no tier is active is still captured (tier None)
    and the gate reports it.

    Id assignment depends on `kind`. For "bet"/"test", a `### N.` section with no
    `**Key:**` label is a red-team **tombstone** (cro-roadmap-red-team keeps
    removed/recast slots in place so audit-trail "Experiment N" cross-references
    stay valid): it is skipped -- no item, no id -- and surviving sections receive
    contiguous ids assigned in document order (`sb-01, sb-02, ...`; `p-01, ...`),
    so a red-teamed roadmap still renders. For "play", the id is the raw `### N.`
    ordinal and no section is skipped (account plays legitimately carry no
    `**Key:**` by design).
    """
    prefix = {"bet": "sb", "test": "p", "play": "ap"}[kind]
    # Tombstone-skip + contiguous survivor ids apply only to the two numbered
    # roadmap altitudes. `kind == "play"` is exempt: account plays carry no
    # `**Key:**` by design and keep their raw-ordinal `ap-NN` ids.
    tombstone_kind = kind in ("bet", "test")
    lines = body.split("\n")
    cur_tier = None
    starts = []  # (line_idx, ordinal, title, tier)
    for idx, ln in enumerate(lines):
        if ln.startswith("### "):
            h3 = re.match(r"^###\s+0*(\d+)\.\s*(.*)$", ln)
            if h3:
                starts.append((idx, int(h3.group(1)), h3.group(2).strip(), cur_tier))
        elif ln.startswith("## "):
            cur_tier = _tier_key(ln[3:])
    out = {}
    seq = 0  # contiguous survivor counter (bet/test only)
    for k, (idx, ordn, title, tier) in enumerate(starts):
        nxt = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        block_lines = []
        for j in range(idx + 1, nxt):
            ln = lines[j]
            if ln.startswith("## ") and not ln.startswith("### "):
                break  # next top-level section ends this experiment's block
            block_lines.append(ln)
        # Line-based bold-label extraction. In the gold format several
        # `**Label:** value` lines sit consecutively in one paragraph (no blank
        # line between them), so labels are read per line, not per paragraph. A
        # label's value continues onto following plain lines until the next
        # label, a blank line, a blockquote (`>`), or a heading. Extracted BEFORE
        # the id is minted, because the tombstone-skip decision keys on `labels`.
        labels, paras = {}, []
        cur_label = None
        for raw in block_lines:
            stripped = raw.strip()
            if not stripped:
                cur_label = None
                continue
            if stripped.startswith("#") or stripped == "---":
                cur_label = None
                continue
            if stripped.startswith(">"):
                cur_label = None
                paras.append(stripped)
                continue
            paras.append(stripped)
            lm = re.match(r"\*\*(.+?)\*\*\s*(.*)$", stripped)
            if lm:
                cur_label = lm.group(1).strip().rstrip(":.").strip()
                labels[cur_label] = lm.group(2).strip()
            elif cur_label is not None:
                labels[cur_label] = (labels[cur_label] + " " + stripped).strip()
        # Red-team tombstone (bet/test only): a `### N.` section with no
        # `**Key:**` LINE is a removed/recast slot kept in place for audit-trail
        # continuity. Skip it -- emit no item, mint no id, never inspect
        # `**Scores:**`. The predicate is line ABSENCE (`"Key" not in labels`),
        # NOT a falsy value: a present-but-empty `**Key:**` keeps "Key" in
        # `labels` (value ""), is therefore not a tombstone, flows through with
        # `key` resolving to None, and must still hit load_*'s missing-Key raise
        # (an authoring bug, distinct from a tombstone).
        if tombstone_kind and "Key" not in labels:
            continue
        # Surviving bet/test ids are contiguous in document order (no holes),
        # matching the sidecar's key-based renumbering and the on-disk filenames.
        # Account plays keep the raw `### N.` ordinal.
        if tombstone_kind:
            seq += 1
            cid = "%s-%02d" % (prefix, seq)
        else:
            cid = "%s-%02d" % (prefix, ordn)
        out[cid] = {"title": title, "key": labels.get("Key") or None,
                    "tier": tier, "labels": labels, "paras": paras}
    return out


def parse_foundation(slice_text):
    """Parse the strategic roadmap's optional `## Measurement Foundation` slice
    into foundation entries: [{"label", "text"}] in source order.

    Foundation entries (hypothesis-generator SKILL.md > Strategic Roadmap Output
    Format) are unscored, keyless prerequisites: bold-labeled paragraphs or
    bullets (`**Label:** text` / `- **Label:** text`), each naming what gets
    defined or instrumented, the system, confirm-first vs build, and the
    dependent experiments. They carry no `### N.` heading, no `**Key:**`, no
    `**Scores:**`, no tier -- so they never become items, never enter the edge
    gate or the portfolio map, and get no spokes. An entry's text continues
    across following plain lines (including across blank lines) until the next
    bold-labeled entry or the end of the slice."""
    entries = []
    if not slice_text:
        return entries
    for raw in slice_text.split("\n"):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue
        # tolerate bullet form: strip a leading list marker before the label
        content = re.sub(r"^[-*]\s+", "", stripped)
        lm = re.match(r"\*\*(.+?)\*\*\s*(.*)$", content)
        if lm:
            entries.append({"label": lm.group(1).strip().rstrip(":.").strip(),
                            "text": lm.group(2).strip()})
        elif entries:
            entries[-1]["text"] = (entries[-1]["text"] + " " + content).strip()
    return entries


# --------------------------------------------------------------------------
# Load + normalize inputs
# --------------------------------------------------------------------------

def _require(d, key, where):
    if key not in d or d[key] is None:
        raise ValueError("%s: missing required field '%s'" % (where, key))
    return d[key]


_REVERSE_KEYS = ("edges", "inbound", "expressed_by", "informed_by", "gated_by")
_INTAKE_KEYS = ("intake_only", "intake")


def load_sidecar(path):
    """Load the render-owned edge sidecar ({scope}-program-edges.md).

    Carries the program/hero block plus the cross-altitude edge binding and the
    gate-classification fields the prose gold roadmaps cannot encode. Bets and
    tests are keyed by the gold `**Key:**` slug. Returns {"program", "bets",
    "tests"} where bets/tests are dicts keyed by gold Key.
    """
    with open(path, encoding="utf-8") as fh:
        fm, _ = parse_frontmatter(fh.read())
    program = _require(fm, "program", "sidecar frontmatter")
    bets = {}
    for b in (fm.get("bets") or []):
        key = _require(b, "key", "sidecar bet")
        edges = []
        for e in (b.get("edges") or []):
            edges.append({"target_key": _require(e, "target", "edge in sidecar bet %s" % key),
                          "type": _require(e, "type", "edge in sidecar bet %s" % key)})
        bets[key] = {
            "delivery_surface": b.get("delivery_surface") or [],
            "executor_status": _require(b, "executor_status", "sidecar bet %s" % key),
            "keystone": bool(b.get("keystone", False)),
            "run_tag": b.get("run_tag", ""),
            "decided_on": b.get("decided_on", ""),
            "edges": edges,
            "_reverse_keys": [k for k in _REVERSE_KEYS if k in b and k != "edges"],
        }
    tests = {}
    for t in (fm.get("tests") or []):
        key = _require(t, "key", "sidecar test")
        tests[key] = {
            "mechanism_class": t.get("mechanism_class"),
            "status": t.get("status", "active"),
            "superseded_by": t.get("superseded_by", ""),
            "mockup": t.get("mockup") if isinstance(t.get("mockup"), dict) else None,
            "_mockup_malformed": ("mockup" in t and t["mockup"] is not None
                                  and not isinstance(t["mockup"], dict)),
            # tests author no edges/inbound/reverse references (gate check 6)
            "_reverse_keys": [k for k in _REVERSE_KEYS if k in t],
            # intake_only is derived, never authored (gate check 5)
            "_authored_intake_keys": [k for k in _INTAKE_KEYS if k in t],
        }
    return {"program": program, "bets": bets, "tests": tests}


def load_strategic(path, sidecar):
    """Load the strategic gold roadmap, deriving bets from the body and merging
    the sidecar's per-bet edge binding + classification (keyed by gold Key).
    Also extracts the optional `## Measurement Foundation` section as foundation
    entries (unscored, keyless; see `parse_foundation`)."""
    with open(path, encoding="utf-8") as fh:
        fm, body = parse_frontmatter(fh.read(), required=False)
    # None = the roadmap carries no frontmatter version (legacy mode); gate 7
    # skips the lock for that file, with an explicit report.
    gold_version = str(fm["version"]) if fm.get("version") is not None else None
    foundation = parse_foundation(extract_named_section(body, "Measurement Foundation"))
    sections = extract_sections(body, "bet")
    sc_bets = sidecar["bets"]
    bets = []
    for cid in sorted(sections, key=lambda c: int(c.split("-")[1])):
        sec = sections[cid]
        if not sec["key"]:
            raise ValueError("strategic %s ('%s'): missing **Key:** line in gold body" % (cid, sec["title"]))
        ice = parse_scores(sec["labels"].get("Scores"))
        if not ice:
            raise ValueError("strategic %s: missing or unparseable **Scores:** line" % cid)
        sb = sc_bets.get(sec["key"])
        bets.append({
            "id": cid,
            "key": sec["key"],
            "title": sec["title"],
            "lever": sec["labels"].get("Lever", ""),
            "decided_on": (sb["decided_on"] if sb else ""),
            "run_tag": (sb["run_tag"] if sb else ""),
            "delivery_surface": (sb["delivery_surface"] if sb else []),
            "executor_status": (sb["executor_status"] if sb else None),
            "ice": ice,
            "keystone": bool(sb["keystone"]) if sb else False,
            "edges_raw": (sb["edges"] if sb else []),
            "_bound": sb is not None,
            "section": sec,
        })
    return {"program": sidecar["program"], "bets": bets, "gold_version": gold_version,
            "foundation": foundation}


def load_tactical(path, sidecar):
    """Load the tactical gold roadmap, deriving tests from the body and merging
    the sidecar's per-test mechanism_class + status (keyed by gold Key)."""
    with open(path, encoding="utf-8") as fh:
        fm, body = parse_frontmatter(fh.read(), required=False)
    # None = no frontmatter version (legacy mode); see load_strategic.
    gold_version = str(fm["version"]) if fm.get("version") is not None else None
    sections = extract_sections(body, "test")
    sc_tests = sidecar["tests"]
    tests = []
    for cid in sorted(sections, key=lambda c: int(c.split("-")[1])):
        sec = sections[cid]
        if not sec["key"]:
            raise ValueError("tactical %s ('%s'): missing **Key:** line in gold body" % (cid, sec["title"]))
        ice = parse_scores(sec["labels"].get("Scores"))
        if not ice:
            raise ValueError("tactical %s: missing or unparseable **Scores:** line" % cid)
        st = sc_tests.get(sec["key"])
        tests.append({
            "id": cid,
            "key": sec["key"],
            "title": sec["title"],
            "mechanism_class": (st["mechanism_class"] if st else None),
            "tier": sec["tier"],
            "ice": ice,
            "target_page": sec["labels"].get("Page", ""),
            "status": (st["status"] if st else "active"),
            "superseded_by": (st["superseded_by"] if st else ""),
            "mockup": (st["mockup"] if st else None),
            "_mockup_malformed": (st["_mockup_malformed"] if st else False),
            "_bound": st is not None,
            "section": sec,
        })
    return {"tests": tests, "gold_version": gold_version}


def _parse_cohort_table(slice_text):
    """Parse the account-cohort taxonomy markdown table into cohort dicts.

    Columns are: cohort name | approximate size | behavior description. The
    header row and the `|---|` separator row are skipped; `**` bold is stripped
    from the cohort name. Returns [{"name", "size", "behavior"}] in table order.
    """
    cohorts = []
    seen_header = False
    for raw in slice_text.split("\n"):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # separator row: every cell is dashes (optionally with :)
        if cells and all(set(c) <= set("-: ") and c for c in cells):
            continue
        if not seen_header:
            seen_header = True  # first pipe row is the header; skip it
            continue
        if len(cells) < 3:
            continue
        name = re.sub(r"\*\*(.+?)\*\*", r"\1", cells[0]).strip()
        cohorts.append({"name": name, "size": cells[1], "behavior": cells[2]})
    return cohorts


def load_account(path):
    """Load the optional account-program deliverable (a `gold-strategy-deliverable`
    of the account-program shape). Returns None when `path` is falsy.

    Account plays are off-store: they carry no `**Key:**`, no `**Scores:**`, no
    on-page mechanism, and no cross-altitude edge, so they never enter the edge
    gate or the portfolio map. The plays block is sliced with
    `extract_named_section("The Account-Level Plays")` and the taxonomy with
    `extract_named_section("The Account-Cohort Taxonomy")` before parsing, so
    `## Cohort Rosters` (`### <name>` headings) is never reached. Returns
    {"plays": [...], "cohorts": [...]} where each play is
    {"id": "ap-NN", "title", "labels", "section"}.
    """
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        _, body = parse_frontmatter(fh.read(), required=False)
    plays_slice = extract_named_section(body, "The Account-Level Plays")
    taxonomy_slice = extract_named_section(body, "The Account-Cohort Taxonomy")
    secs = extract_sections(plays_slice, "play")
    plays = []
    for cid in sorted(secs, key=lambda c: int(c.split("-")[1])):
        sec = secs[cid]
        plays.append({"id": cid, "title": sec["title"], "labels": sec["labels"], "section": sec})
    cohorts = _parse_cohort_table(taxonomy_slice)
    # Raw ordinals as authored (before dict-keying collapses duplicates). The
    # `ap-NN` keying dedupes by construction, so a genuine duplicate `### N.`
    # would silently vanish; the raw list lets the gate name the collision.
    raw_ordinals = [int(m.group(1)) for m in
                    re.finditer(r"^###\s+0*(\d+)\.", plays_slice, re.M)]
    return {"plays": plays, "cohorts": cohorts, "_raw_ordinals": raw_ordinals}


def link_edges(strategic, tactical):
    """Resolve each bet edge's target (a tactical gold Key) to a `p-NN` id.

    Sets `b["edges"]` = [{target, type, target_key, _resolved}]; an unresolved
    target keeps the raw key string so the gate names it. Reverse edges stay
    derived (see `derive`); the strategic side is the only authored end."""
    key2id = {t["key"]: t["id"] for t in tactical["tests"] if t["key"]}
    for b in strategic["bets"]:
        edges = []
        for e in b["edges_raw"]:
            tid = key2id.get(e["target_key"])
            edges.append({"target": tid if tid else e["target_key"],
                          "type": e["type"],
                          "target_key": e["target_key"],
                          "_resolved": tid is not None})
        b["edges"] = edges


# --------------------------------------------------------------------------
# The gate (7 checks, fail-closed)
# --------------------------------------------------------------------------

def run_gate(strategic, tactical, sidecar, account=None):
    # Measurement Foundation entries never enter this gate: they are keyless and
    # unscored, so they need no sidecar entries and are excluded by construction
    # from every sidecar-related check (binding completeness, dangling targets,
    # executor-status derivation, version-lock scope). A sidecar edge that names
    # a foundation entry as its target is a dangling target (check 2), because
    # edge targets resolve against tactical test Keys only.
    #
    # Returns a list of gate notes (non-violation reports the caller must
    # surface, e.g. a skipped version lock). Raises GateError on any violation.
    violations = []
    notes = []
    bets, tests = strategic["bets"], tactical["tests"]
    live_ids = {t["id"] for t in tests if t["status"] != "superseded"}
    test_by_id = {t["id"]: t for t in tests}
    gold_bet_keys = {b["key"] for b in bets}
    gold_test_keys = {t["key"] for t in tests}

    # Bind: every gold bet must have a sidecar entry (its edges + classification),
    # and every sidecar key must resolve to a gold Key (no orphan bindings).
    for b in bets:
        if not b["_bound"]:
            violations.append("[bind] strategic bet %s (key '%s') has no entry in the edge sidecar"
                              % (b["id"], b["key"]))
    for key in sidecar["bets"]:
        if key not in gold_bet_keys:
            violations.append("[bind] sidecar bet key '%s' resolves to no strategic gold Key" % key)
    for key in sidecar["tests"]:
        if key not in gold_test_keys:
            violations.append("[bind] sidecar test key '%s' resolves to no tactical gold Key" % key)

    for b in bets:
        for e in b["edges"]:
            # 1. edge.type in {expresses, informs, gates}
            if e["type"] not in EDGE_TYPES:
                violations.append("[1] bet %s: edge type '%s' not in %s (target key '%s')"
                                  % (b["id"], e["type"], list(EDGE_TYPES), e["target_key"]))
            # 2. edge.target (a tactical Key) resolves to a live test id
            if not e["_resolved"] or e["target"] not in live_ids:
                violations.append("[2] bet %s: edge target key '%s' resolves to no live test"
                                  % (b["id"], e["target_key"]))
            # 3. mechanism gate on `expresses`
            if e["type"] == "expresses" and e["_resolved"] and e["target"] in test_by_id:
                t = test_by_id[e["target"]]
                if t["mechanism_class"] and t["mechanism_class"] not in b["delivery_surface"]:
                    violations.append(
                        "[3] mechanism mismatch: bet %s expresses test %s, but test mechanism "
                        "'%s' is not in bet delivery_surface %s (lever: %s)"
                        % (b["id"], t["id"], t["mechanism_class"], b["delivery_surface"], b["lever"]))
        # 4. executor_status matches derived status
        has_expr = any(e["type"] == "expresses" for e in b["edges"])
        surfaces = b["delivery_surface"]
        off_only = bool(surfaces) and all(s in OFF_PAGE_SURFACES for s in surfaces)
        st = b["executor_status"]
        if st not in EXECUTOR_STATUSES:
            violations.append("[4] bet %s: executor_status '%s' not in %s"
                              % (b["id"], st, list(EXECUTOR_STATUSES)))
        elif st == "on-page" and not has_expr:
            violations.append("[4] bet %s: executor_status 'on-page' but no `expresses` edge" % b["id"])
        elif st == "off-page" and (has_expr or not off_only):
            violations.append("[4] bet %s: executor_status 'off-page' requires no `expresses` edge "
                              "and an off-page-only delivery_surface (got expresses=%s, surfaces=%s)"
                              % (b["id"], has_expr, surfaces))
        elif st == "unexpressed" and (has_expr or off_only):
            violations.append("[4] bet %s: executor_status 'unexpressed' requires no `expresses` edge "
                              "and at least one on-page surface (got expresses=%s, surfaces=%s)"
                              % (b["id"], has_expr, surfaces))

    # 5/6. the tactical side authors no reverse references and never authors the
    # derived intake_only flag. The gold tactical roadmap is prose (cannot carry
    # them); the only authorable tactical surface is the sidecar test entry.
    for key, t in sidecar["tests"].items():
        if t["_reverse_keys"]:
            violations.append("[6] sidecar test '%s': must not author inbound/reverse references "
                              "(found %s); reverse edges are derived from the strategic edges"
                              % (key, t["_reverse_keys"]))
        if t["_authored_intake_keys"]:
            violations.append("[5] sidecar test '%s': intake_only is derived, never authored "
                              "(found %s)" % (key, t["_authored_intake_keys"]))
        if t["_mockup_malformed"]:
            violations.append("[mockup] sidecar test '%s': malformed mockup block (expected a mapping)" % key)
        mk = t["mockup"]
        if mk and "control_screenshot" in mk and not isinstance(mk["control_screenshot"], str):
            violations.append("[mockup] sidecar test '%s': control_screenshot must be a string path" % key)

    # mechanism_class is required on every live test (the mechanism gate input).
    for t in tests:
        if t["status"] != "superseded" and not t["mechanism_class"]:
            violations.append("[mech] test %s (key '%s'): no mechanism_class in the edge sidecar "
                              "(required for the `expresses` mechanism gate)" % (t["id"], t["key"]))

    # 7. version lock: the sidecar records the gold roadmap versions it was
    # authored against; both must match the live gold roadmaps' frontmatter.
    # A roadmap whose gold_version is None carries no frontmatter `version`
    # (legacy-mode roadmaps carry no frontmatter at all), so there is nothing
    # to lock for that file: the lock is SKIPPED for it, and the skip is
    # reported explicitly in the gate notes -- never a silent pass. This holds
    # even when the sidecar declares a version for that file (the sidecar's
    # version fields are schema-required, so legacy sidecars still author them).
    prog = sidecar["program"]
    sv = str(prog.get("strategic_version", ""))
    tv = str(prog.get("tactical_version", ""))
    if strategic["gold_version"] is None:
        notes.append("version lock: skipped for strategic (roadmap carries no version)")
    elif sv != strategic["gold_version"]:
        violations.append("[7] strategic version lock: sidecar strategic_version '%s' != strategic "
                          "gold roadmap version '%s'" % (sv, strategic["gold_version"]))
    if tactical["gold_version"] is None:
        notes.append("version lock: skipped for tactical (roadmap carries no version)")
    elif tv != tactical["gold_version"]:
        violations.append("[7] tactical version lock: sidecar tactical_version '%s' != tactical "
                          "gold roadmap version '%s'" % (tv, tactical["gold_version"]))

    # Account-binding leg (separate from the seven edge checks; account plays carry
    # no edges, no mechanism, no ICE, so they never enter checks 1-7). Runs only
    # when an account program is present. Validates the plays on their own terms.
    if account is not None:
        plays = account["plays"]
        if not plays:
            violations.append("[account] the account program has no plays "
                              "(expected at least one `### N.` play under 'The Account-Level Plays')")
        # ordinal uniqueness: the `ap-NN` keying dedupes silently, so compare the
        # raw authored ordinals (from the plays slice) against their unique set.
        raw = account.get("_raw_ordinals", [ int(p["id"].split("-")[1]) for p in plays ])
        seen = set()
        for ordn in raw:
            if ordn in seen:
                violations.append("[account] duplicate play ordinal %d "
                                  "(two `### %d.` headings under 'The Account-Level Plays')"
                                  % (ordn, ordn))
            seen.add(ordn)
        for p in plays:
            for req in ("Cohort", "The play", "How it is measured"):
                if req not in p["labels"] or not p["labels"][req]:
                    violations.append("[account] play %s ('%s'): missing required label '%s'"
                                      % (p["id"], p["title"], req))

    if violations:
        raise GateError(violations)
    return notes


# --------------------------------------------------------------------------
# Derivation (reverse edges, intake, coordinates, classes, tiers)
# --------------------------------------------------------------------------

def derive(strategic, tactical):
    bets, tests = strategic["bets"], tactical["tests"]
    test_by_id = {t["id"]: t for t in tests}

    # forward (bet) edge buckets
    for b in bets:
        b["expresses"] = [e["target"] for e in b["edges"] if e["type"] == "expresses"]
        b["influences"] = [e["target"] for e in b["edges"] if e["type"] in ("informs", "gates")]

    # reverse edges per test, split by type
    for t in tests:
        t["inbound"] = {"expresses": [], "informs": [], "gates": []}
    for b in bets:
        for e in b["edges"]:
            if e["target"] in test_by_id:
                test_by_id[e["target"]]["inbound"][e["type"]].append(b["id"])
    for t in tests:
        t["intake_only"] = (t["status"] != "superseded"
                            and not any(t["inbound"][k] for k in EDGE_TYPES))
        t["exp_by"] = t["inbound"]["expresses"]
        t["inf_by"] = t["inbound"]["informs"] + t["inbound"]["gates"]

    # map coordinates: base lerp + deterministic tie-dodge for shared (I,E) cells
    nodes = ([("bet", b) for b in bets]
             + [("test", t) for t in tests if t["status"] != "superseded"])
    cells = {}
    for kind, n in nodes:
        cells.setdefault((n["ice"]["i"], n["ice"]["e"]), []).append((kind, n))
    import math
    for (impact, ease), group in cells.items():
        bx, by = x_of(ease), y_of(impact)
        group.sort(key=lambda kn: kn[1]["id"])
        count = len(group)
        radius = 18 if any(k == "bet" for k, _ in group) else 13
        for k, (kind, n) in enumerate(group):
            if count == 1:
                dx = dy = 0.0
            else:
                ang = -math.pi / 2 + 2 * math.pi * k / count
                dx, dy = radius * math.cos(ang), radius * math.sin(ang)
            n["cx"], n["cy"] = int(round(bx + dx)), int(round(by + dy))

    # tier groups for the backlog (active tests only; superseded shown dimmed last)
    grouped = {key: [] for key in TIER_ORDER}
    superseded = []
    for t in tests:
        if t["status"] == "superseded":
            superseded.append(t)
        elif t["tier"] in grouped:
            grouped[t["tier"]].append(t)
        else:
            grouped.setdefault(t["tier"], []).append(t)
    for key in grouped:
        grouped[key].sort(key=lambda t: t["id"])
    return {"tier_groups": grouped, "superseded": sorted(superseded, key=lambda t: t["id"])}


# --------------------------------------------------------------------------
# Display helpers
# --------------------------------------------------------------------------

def bet_label(bid):  # sb-02 -> SB-2
    return "SB-%d" % int(bid.split("-")[1])


def join_and(items):  # ["A","B","C"] -> "A, B, and C"
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return "%s and %s" % (items[0], items[1])
    return "%s, and %s" % (", ".join(items[:-1]), items[-1])


def test_num(tid):  # p-03 -> 3
    return str(int(tid.split("-")[1]))


def play_label(pid):  # ap-02 -> AP-2
    return "AP-%d" % int(pid.split("-")[1])


def ice_total(ice):
    return ice["i"] + ice["c"] + ice["e"]


def ice_str(ice):
    return "I%d C%d E%d" % (ice["i"], ice["c"], ice["e"])


def esc(s):
    return html.escape(str(s), quote=True)


def md_inline(s):
    """Minimal inline markdown -> HTML: escape, then bold and links."""
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


def slot(item_id, name, source_text):
    """Emit a labeled prose slot pre-filled with the verbatim source text.

    The curation pass rewrites the content between the markers; the markers and
    the structured chrome around them are never touched.
    """
    body = md_inline(source_text) if source_text else \
        '<span class="slot">[no source prose for %s; curation pass fills this]</span>' % esc(name)
    return "<!--PROSE id=%s slot=%s-->%s<!--/PROSE-->" % (item_id, name, body)


# --------------------------------------------------------------------------
# Emit: chrome fragments built from data
# --------------------------------------------------------------------------

def chips(ids, soft, link_spoke):
    out = []
    for i in ids:
        cls = "chip soft" if soft else "chip"
        href = "%s.html" % i if link_spoke else "index.html#%s" % i
        label = "%s %s" % (bet_label(i), "") if i.startswith("sb-") else "#%s" % test_num(i)
        out.append('<a class="%s" href="%s">%s</a>' % (cls, href, esc(label.strip())))
    return "".join(out)


def render(tpl, mapping):
    """Single-pass {{TOKEN}} substitution. One pass (not sequential replaces) so a
    substituted value that happens to contain a literal {{OTHER}} is never re-scanned
    -- the deterministic core must not let data content reach into the template."""
    def sub(m):
        key = m.group(1)
        return mapping[key] if key in mapping else m.group(0)
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", sub, tpl)


def build_map_svg(bets, tests):
    parts = ['<g>']
    for y in GRID_Y:
        cls = "pf-frame" if y in (GRID_Y[0], GRID_Y[-1]) else "pf-grid"
        parts.append('<line class="%s" x1="%d" y1="%d" x2="%d" y2="%d"></line>'
                     % (cls, PLOT_LEFT, y, PLOT_RIGHT, y))
    for x in GRID_X:
        cls = "pf-frame" if x in (GRID_X[0], GRID_X[-1]) else "pf-grid"
        parts.append('<line class="%s" x1="%d" y1="%d" x2="%d" y2="%d"></line>'
                     % (cls, x, PLOT_TOP, x, PLOT_BOTTOM))
    parts.append('</g>')
    parts.append('<text class="pf-quad" x="100" y="78">Programs: high impact, lower ease</text>')
    parts.append('<text class="pf-quad" x="712" y="360" text-anchor="end">Page tests: lighter, faster</text>')
    parts.append('<text class="pf-axis" x="400" y="404" text-anchor="middle">Ease to run &#8594;</text>')
    parts.append('<text class="pf-tick" x="88" y="390" text-anchor="middle">harder</text>')
    parts.append('<text class="pf-tick" x="712" y="390" text-anchor="middle">easier</text>')
    parts.append('<text class="pf-axis" x="30" y="216" text-anchor="middle" transform="rotate(-90 30 216)">Impact on qualified pipeline &#8594;</text>')
    parts.append('<text class="pf-tick" x="64" y="372" text-anchor="middle">low</text>')
    parts.append('<text class="pf-tick" x="64" y="64" text-anchor="middle">high</text>')
    parts.append('<g id="pf-links"></g>')
    for t in tests:
        if t["status"] == "superseded":
            continue
        intake = " intake" if t["intake_only"] else ""
        exp = " ".join(t["exp_by"])
        inf = " ".join(t["inf_by"])
        parts.append(
            '<a class="pf-node pf-test%s" data-node="%s" data-exp-by="%s" data-inf-by="%s" href="%s.html">'
            '<circle class="pf-dot" cx="%d" cy="%d" r="11"></circle>'
            '<text class="pf-lab" x="%d" y="%d">%s</text></a>'
            % (intake, t["id"], esc(exp), esc(inf), t["id"], t["cx"], t["cy"],
               t["cx"], t["cy"] + 3, test_num(t["id"])))
    for b in bets:
        parts.append(
            '<a class="pf-node pf-bet" data-node="%s" data-exp="%s" data-inf="%s" href="%s.html">'
            '<circle class="pf-ring" cx="%d" cy="%d" r="26"></circle>'
            '<circle class="pf-dot" cx="%d" cy="%d" r="19"></circle>'
            '<text class="pf-lab" x="%d" y="%d">%s</text></a>'
            % (b["id"], esc(" ".join(b["expresses"])), esc(" ".join(b["influences"])), b["id"],
               b["cx"], b["cy"], b["cx"], b["cy"], b["cx"], b["cy"] + 4, bet_label(b["id"])))
    return "\n".join(parts)


def build_bet_cards(bets):
    cards = []
    for b in bets:
        run = ""
        if b["run_tag"]:
            long_cls = " long" if b["run_tag"].lower() in ("long game", "long-game") else ""
            run = '<span class="b-run%s">%s</span>' % (long_cls, esc(b["run_tag"]))
        tag_cls = {"on-page": "on", "off-page": "off", "unexpressed": "gap"}[b["executor_status"]]
        tag_txt = {"on-page": "On-page", "off-page": "Off-page move", "unexpressed": "Unexpressed"}[b["executor_status"]]
        rels = []
        for typ in EDGE_TYPES:
            ids = [e["target"] for e in b["edges"] if e["type"] == typ]
            if ids:
                rels.append('<div class="rel"><span class="x-lab">%s</span><div class="chips">%s</div></div>'
                            % (EDGE_LABEL_BET[typ], chips(ids, typ not in SOLID_TYPES, link_spoke=False)))
        decided = ('<p class="b-decided">Decided on <b>%s</b></p>' % esc(b["decided_on"])) if b["decided_on"] else ""
        cards.append(
            '<div class="bet" id="%s">'
            '<div class="b-top"><span class="b-code">%s</span>%s</div>'
            '<h3><a href="%s.html">%s</a></h3>%s'
            '<p class="b-body">%s</p>'
            '<span class="ice"><span class="t mono">ICE %d</span><span class="mono">I%d &middot; C%d &middot; E%d</span></span>'
            '<div class="exec"><span class="x-tag %s">%s</span>%s<p class="x-note">%s</p></div>'
            '</div>'
            % (b["id"], bet_label(b["id"]), run, b["id"], esc(b["title"]), decided,
               slot(b["id"], "card-body", b["section"]["labels"].get("Lever", b["lever"])),
               ice_total(b["ice"]), b["ice"]["i"], b["ice"]["c"], b["ice"]["e"],
               tag_cls, tag_txt, "".join(rels),
               slot(b["id"], "exec-note", b["section"]["labels"].get("What a win proves", ""))))
    return "\n".join(cards)


def build_backlog(tier_groups, superseded):
    """Audit-style rows grouped under tier headers (not a card wall). Each row: mono
    number + title link (to the test spoke) + one-line page target + ICE + ladder chip
    + a mono `.tag` tier chip. Superseded rows are dimmed, unscored, non-linking."""
    out = []
    for key in TIER_ORDER:
        tests = tier_groups.get(key, [])
        if not tests:
            continue
        label, css, caption = TIERS[key]
        rows = []
        for t in tests:
            if t["intake_only"]:
                ladder = '<span class="ladder none">intake-only</span>'
            else:
                tops = t["exp_by"] + t["inf_by"]
                first = tops[0]
                extra = ", ".join(bet_label(x) for x in tops)
                ladder = '<a class="ladder" href="index.html#%s">&#8593; %s</a>' % (first, esc(extra))
            rows.append(
                '<div class="brow" id="%s"><span class="b-n">#%s</span>'
                '<span class="b-main"><a class="b-title" href="%s.html">%s</a>'
                '<span class="b-page">%s</span></span>'
                '<span class="b-meta"><span class="b-ice">ICE <b>%d</b> &middot; %s</span>'
                '%s<span class="tag %s">%s</span></span></div>'
                % (t["id"], test_num(t["id"]), t["id"], esc(t["title"]),
                   esc(t["target_page"]), ice_total(t["ice"]), ice_str(t["ice"]),
                   ladder, css, esc(label)))
        out.append('<div class="tier"><div class="tier-head %s"><h3>%s</h3>'
                   '<span class="ct mono">%s</span></div><div class="brows">%s</div></div>'
                   % (css, esc(label), esc(caption), "".join(rows)))
    if superseded:
        rows = []
        for t in superseded:
            note = (" %s" % t["superseded_by"]) if t["superseded_by"] else ""
            rows.append(
                '<div class="brow dim" id="%s"><span class="b-n">#%s</span>'
                '<span class="b-main"><span class="b-title">%s</span>'
                '<span class="b-page">%s</span></span>'
                '<span class="b-meta"><span class="b-ice">not scored</span>'
                '<span class="ladder none">superseded%s</span>'
                '<span class="tag sup">Superseded</span></span></div>'
                % (t["id"], test_num(t["id"]), esc(t["title"]), esc(t["target_page"]), esc(note)))
        out.append('<div class="tier"><div class="tier-head"><h3>Superseded</h3>'
                   '<span class="ct mono">shipped or replaced</span></div>'
                   '<div class="brows">%s</div></div>' % "".join(rows))
    return "\n".join(out)


def extract_named_section(body, name):
    """Return the text of a top-level `## {name}` section, or '' if absent."""
    m = re.search(r"^##\s+%s\b.*$" % re.escape(name), body, re.M | re.I)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+", body[start:], re.M)
    return body[start:start + nxt.start()].strip() if nxt else body[start:].strip()


# --------------------------------------------------------------------------
# Emit: hub + spokes
# --------------------------------------------------------------------------

def build_account_section(account, program):
    """Build the `<section id="account-program">` off-store altitude, or '' when
    `account` is None. Mirrors build_bet_cards/build_backlog: data-bound structure,
    prose through slots. Cohort name + size are data-bound facts; the behavior and
    the intro flow through slots so curation/humanizer own the prose. Each play is
    a `.test` card in a `.test-grid`, linking to `ap-NN.html`, with an off-store
    badge and its measured-by drawn from the `How it is measured` label."""
    if account is None:
        return ""
    cohort_cards = []
    for i, c in enumerate(account["cohorts"], start=1):
        cohort_cards.append(
            '<div class="cohort"><div class="c-top"><span class="c-name">%s</span>'
            '<span class="c-size mono">%s</span></div><p class="c-behavior">%s</p></div>'
            % (esc(c["name"]), esc(c["size"]),
               slot("program", "cohort-%d" % i, c["behavior"])))
    cohort_block = ('<div class="cohort-grid">%s</div>' % "".join(cohort_cards)) if cohort_cards else ""

    play_cards = []
    for p in account["plays"]:
        measured = p["labels"].get("How it is measured", "")
        play_cards.append(
            '<div class="test off" id="%s"><div class="t-top"><span class="t-n">%s</span>'
            '<span class="x-tag off">Off-store</span></div>'
            '<h4><a href="%s.html">%s</a></h4><p class="t-page">%s</p></div>'
            % (p["id"], play_label(p["id"]), p["id"], esc(p["title"]), esc(measured)))
    plays_block = ('<div class="test-grid">%s</div>' % "".join(play_cards)) if play_cards else ""

    return (
        '<section id="account-program">\n  <div class="container">\n'
        '    <span class="eyebrow">Off-store work</span>\n'
        '    <h2>The account program</h2>\n'
        '    <p class="section-lead">%s</p>\n'
        '    %s\n    %s\n  </div>\n</section>'
        % (slot("program", "account-lead",
                "Account-level plays that run off-store, measured by account-level "
                "designs rather than by splitting on-store traffic."),
           cohort_block, plays_block))


def build_foundation_section(foundation):
    """Build the `<section id="measurement-foundation">` hub section, or '' when
    the strategic gold roadmap carries no `## Measurement Foundation` section.
    Foundation entries are unscored, keyless prerequisites: the cards carry no
    ICE chips, no tier badge, no edges, and link to no spokes. The bold label is
    the data-bound entry title; the prose flows through slots for curation."""
    if not foundation:
        return ""
    cards = []
    for i, entry in enumerate(foundation, start=1):
        cards.append(
            '<div class="mf" id="mf-%d"><h3>%s</h3><p class="mf-body">%s</p></div>'
            % (i, esc(entry["label"]),
               slot("program", "foundation-%d" % i, entry["text"])))
    return (
        '<section id="measurement-foundation">\n  <div class="container">\n'
        '    <span class="eyebrow">Stand-up work</span>\n'
        '    <h2>%s</h2>\n'
        '    <p class="section-lead">%s</p>\n'
        '    <div class="mf-grid">%s</div>\n  </div>\n</section>'
        % (slot("program", "foundation-headline", "The measurement foundation"),
           slot("program", "foundation-lead",
                "Definition and instrumentation work the experiments below depend on. "
                "These are not scored experiments; they are prerequisites the analytics "
                "or operations team can stand up independently of the program."),
           "".join(cards)))


def build_stats_band(strategic, tactical, derived):
    """Build the hub `<section class="program-stats">` band, or '' when there are no
    active tests. Deterministic and LLM-free: each stat is derived from already-parsed
    data, the number is the star, and the caption carries a claim (it reframes, it does
    not just name). Bare-count boxes are dropped rather than padding the band. The band
    is fully code-authored -- it holds no PROSE slot, so a re-render reproduces it exactly.
    """
    bets = strategic["bets"]
    active = [t for t in tactical["tests"] if t["status"] != "superseded"]
    total = len(active)
    if total == 0:
        return ""
    boxes = []  # (color_class, number, claim_caption)

    # 1. How much of the backlog executes a strategic bet (strategy-led vs scattered).
    laddered = sum(1 for t in active if not t["intake_only"])
    if laddered:
        if laddered == total:
            cap = "every page test executes a strategic bet, so nothing in the backlog is a stray idea"
        else:
            cap = "page tests execute a strategic bet; the rest are standalone intake tests"
        boxes.append(("blue", "%d/%d" % (laddered, total), cap))

    # 2. Quick wins that can run before any stand-up work (front-loaded value).
    quick = len(derived["tier_groups"].get(TIER_ORDER[0], []))
    if quick:
        label = TIERS[TIER_ORDER[0]][0].lower()
        boxes.append(("green", "%d/%d" % (quick, total),
                      "are %s: high-confidence, high-ease tests that run before any stand-up work" % label))

    # 3. One further claim, only if the data supports a real one (never a bare count).
    mocked = sum(1 for t in active if t.get("mockup"))
    if mocked:
        boxes.append(("purple", "%d/%d" % (mocked, total),
                      "already carry a built visual mockup, so the change is specified, not hand-waved"))
    elif bets and all(b.get("decided_on") for b in bets):
        boxes.append(("blue", "%d" % len(bets),
                      "strategic bets, each decided on a down-funnel metric the business already tracks"))

    if not boxes:
        return ""
    cards = "".join(
        '<div class="statbox"><div class="n %s">%s</div><div class="k">%s</div></div>' % (color, num, cap)
        for color, num, cap in boxes)
    return ('<section class="program-stats">\n  <div class="container">\n'
            '    <span class="eyebrow">What the portfolio adds up to</span>\n'
            '    <div class="stat-grid">%s</div>\n  </div>\n</section>' % cards)


def build_hub(strategic, tactical, derived, templates, account=None):
    program = strategic["program"]
    bets, tests = strategic["bets"], tactical["tests"]
    hero = program.get("hero") or {}
    client = esc(program.get("client", ""))
    name = esc(program.get("name", ""))
    date = esc(str(program.get("date", "")))

    # hero h1: highlight the optional headline_num inside the headline
    headline = hero.get("headline", name)
    num = hero.get("headline_num", "")
    h1 = esc(headline)
    if num and num in headline:
        h1 = esc(headline).replace(esc(num), '<span class="num">%s</span>' % esc(num), 1)

    prov = ('<span class="mono">FunnelEnvy</span><span class="s">/</span>%s'
            '<span class="s">/</span><span class="mono">%s</span>'
            '<span class="s">/</span><span class="mono">%s</span>' % (client, name, date))

    keystone_html = ""
    if any(b["keystone"] for b in bets):
        ks = [bet_label(b["id"]) for b in bets if b["keystone"]]
        # Neutral, count-correct seed: name the keystone bet(s), assert no
        # relationship. The curation pass authors the actual rationale from the
        # bet's source, so the prefill only needs to be grammatical seed text.
        if len(ks) == 1:
            ks_seed = "%s is the keystone bet." % ks[0]
        else:
            ks_seed = "%s are the keystone bets." % join_and(ks)
        keystone_html = ('<div class="keystone"><span class="ks-mark">The keystone</span>'
                         '<p>%s</p></div>'
                         % slot("program", "keystone", ks_seed))

    seq_src = extract_named_section(strategic_body_cache.get("strategic", ""), "Sequencing")
    main = render(templates["hub"], {
        "PROVENANCE": prov,
        "HERO_H1": h1,
        "HERO_SUB": slot("program", "hero-sub", hero.get("subhead", "")),
        "PROGRAM_STATS": build_stats_band(strategic, tactical, derived),
        "ALT1": slot("program", "altitude-1", "Program-level moves decided on the business objective."),
        "ALT2": slot("program", "altitude-2", "Page-level tests decided on the metric each page can read."),
        "MAP_LEAD": slot("program", "map-lead", ""),
        "MAP_SVG": build_map_svg(bets, tests),
        "MAP_NOTE": slot("program", "map-note", ""),
        "STRATEGY_HEADLINE": slot("program", "strategy-headline", "The strategy"),
        "STRATEGY_LEAD": slot("program", "strategy-lead", ""),
        "KEYSTONE": keystone_html,
        "BET_CARDS": build_bet_cards(bets),
        "BACKLOG_HEADLINE": slot("program", "backlog-headline", "The experiment backlog"),
        "BACKLOG_LEAD": slot("program", "backlog-lead", ""),
        "BACKLOG": build_backlog(derived["tier_groups"], derived["superseded"]),
        "MEASUREMENT_FOUNDATION": build_foundation_section(strategic.get("foundation") or []),
        "ACCOUNT_PROGRAM": build_account_section(account, program),
        "SEQUENCE_HEADLINE": slot("program", "sequence-headline", "The sequence"),
        "SEQUENCE": slot("program", "sequence", seq_src),
        "DECISIONS_HEADLINE": slot("program", "decisions-headline",
                                   "Decisions we need from %s" % program.get("client", "")),
        "DECISIONS_LEAD": slot("program", "decisions-lead", ""),
        "DECISIONS": slot("program", "decisions", ""),
        "FOOT": "%s (%s) &middot; prepared by FunnelEnvy &middot; <span class=\"mono\">%s</span>"
                % (client, name, date),
    })
    foundation_nav = ('<a href="#measurement-foundation">Measurement foundation</a>'
                      if strategic.get("foundation") else "")
    account_nav = '<a href="#account-program">Account program</a>' if account is not None else ""
    nav_links = ('<a href="#map">Portfolio map</a><a href="#strategy">The strategy</a>'
                 '%s<a href="#backlog">Experiment backlog</a>%s<a href="#sequence">Sequence</a>'
                 '<a href="#decisions">Decisions</a>' % (foundation_nav, account_nav))
    return render(templates["base"], {
        "TITLE": "%s | FunnelEnvy" % esc(name),
        "BRAND_HREF": "#top",
        "CLIENT": client,
        "NAV_LINKS": nav_links,
        "SCRIPT_SRC": "site.js",
        "MAIN": main,
    })


def _spoke_base(templates, title, client, main):
    return render(templates["base"], {
        "TITLE": title,
        "BRAND_HREF": "index.html#top",
        "CLIENT": client,
        "NAV_LINKS": '<a href="index.html#map">Back to the program map</a>',
        "SCRIPT_SRC": "site.js",
        "MAIN": main,
    })


def build_spoke_strategic(b, program, templates):
    client = esc(program.get("client", ""))
    tag_cls = {"on-page": "on", "off-page": "off", "unexpressed": "gap"}[b["executor_status"]]
    tag_txt = {"on-page": "On-page", "off-page": "Off-page move", "unexpressed": "Unexpressed"}[b["executor_status"]]
    meta = '<span class="x-tag %s">%s</span>' % (tag_cls, tag_txt)
    if b["keystone"]:
        meta += '<span class="kw">Keystone</span>'
    meta += '<span class="ice mono">ICE %d &middot; %s</span>' % (ice_total(b["ice"]), ice_str(b["ice"]))

    conn = []
    for typ in EDGE_TYPES:
        ids = [e["target"] for e in b["edges"] if e["type"] == typ]
        if ids:
            conn.append('<div class="rel"><span class="x-lab">%s</span><div class="chips">%s</div></div>'
                        '<p class="cx">%s</p>'
                        % (EDGE_LABEL_BET[typ], chips(ids, typ not in SOLID_TYPES, link_spoke=False),
                           slot(b["id"], "cx-%s" % typ, "")))
    lab = b["section"]["labels"]
    main = render(templates["spoke_strategic"], {
        "CRUMB": ('<span class="mono">FunnelEnvy</span> / %s / <span class="mono">Strategic move %s</span>'
                  % (client, bet_label(b["id"]))),
        "META": meta,
        "TITLE_H1": esc(b["title"]),
        "LEAD": slot(b["id"], "lead", lab.get("Lever", b["lever"])),
        "LEVER": slot(b["id"], "lever", lab.get("Lever", "")),
        "MOVE": slot(b["id"], "move", lab.get("What to stand up", "")),
        "CONNECTIONS": "".join(conn),
        "EVIDENCE": slot(b["id"], "evidence", lab.get("Stand-up dependency / Requires", lab.get("What to stand up", ""))),
        "FOOT_ID": "%s &middot; %s" % (bet_label(b["id"]), esc(program.get("name", ""))),
    })
    return _spoke_base(templates, "%s %s | %s" % (bet_label(b["id"]), esc(b["title"]), esc(program.get("name", ""))),
                       client, main)


def build_spoke_tactical(t, program, templates, out_dir):
    client = esc(program.get("client", ""))
    meta = ('<span class="tier">%s</span><span class="ice mono">ICE %d &middot; %s</span>'
            '<span class="tgt">%s</span>'
            % (esc(TIERS.get(t["tier"], (t["tier"],))[0]), ice_total(t["ice"]), ice_str(t["ice"]),
               esc(t["target_page"])))

    # proposed-change (mockup) section -- conditional
    mockup_html = ""
    mk = t["mockup"]
    if mk:
        rels = copy_mockup_assets(t, mk, out_dir)
        ctrl_rel = rels.get("control_screenshot")
        shot_rel = rels.get("screenshot")
        url = esc(mk.get("target_url", ""))

        def _img(rel, alt):
            if rel:
                return '<img class="mockup-shot" src="%s" alt="%s">' % (esc(rel), esc(alt))
            return ('<div class="mockup-ph"><span class="lab">Mockup preview</span>'
                    '<span class="sub">no screenshot resolved for this hypothesis</span></div>')

        if ctrl_rel:
            # Before/After pair: two labeled figures in a responsive compare grid.
            def _frame(label, img_html):
                return ('<figure class="mockup-frame"><figcaption class="mockup-label">%s</figcaption>'
                        '<div class="mockup-bar"><span class="dot"></span><span class="dot"></span>'
                        '<span class="dot"></span><span class="url">%s</span></div>%s</figure>'
                        % (esc(label), url, img_html))
            preview = ('<div class="mockup-compare">%s%s</div>'
                       % (_frame("Before / Control", _img(ctrl_rel, "Control: %s" % t["title"])),
                          _frame("After / Proposed", _img(shot_rel, "Proposed: %s" % t["title"]))))
        else:
            # After-only: markup byte-identical to pre-control output.
            inner = _img(shot_rel, "Mockup of %s" % t["title"])
            preview = ('<div class="mockup-frame"><div class="mockup-bar"><span class="dot"></span>'
                       '<span class="dot"></span><span class="dot"></span><span class="url">%s</span></div>%s</div>'
                       % (url, inner))

        view = ('<a class="btn-mock" href="mockups/%s/mockup.html">View live mockup &#8599;</a>' % t["id"]) \
            if mk.get("html") else ""
        mockup_html = (
            '<section class="sec"><div class="container"><h2>Proposed change</h2>'
            '%s'
            '<div class="mockup-meta"><span class="mm"><span class="mm-k">Insertion</span>%s</span>'
            '<span class="mm"><span class="mm-k">Mode</span>%s</span>%s</div>'
            '<p class="cx">%s</p></div></section>'
            % (preview, esc(mk.get("insertion_point", "")),
               esc(mk.get("mode", "")), view,
               slot(t["id"], "placement", mk.get("placement_summary", ""))))

    conn = []
    for typ in EDGE_TYPES:
        ids = t["inbound"][typ]
        if ids:
            conn.append('<div class="rel"><span class="x-lab">%s</span><div class="chips">%s</div></div>'
                        '<p class="cx">%s</p>'
                        % (EDGE_LABEL_TEST[typ], chips(ids, typ not in SOLID_TYPES, link_spoke=False),
                           slot(t["id"], "cx-%s" % typ, "")))
    if not conn:
        conn.append('<p class="cx">%s</p>' % slot(t["id"], "intake-note",
                    "Intake-only: this test serves no strategic move directly."))
    lab = t["section"]["labels"]
    main = render(templates["spoke_tactical"], {
        "CRUMB": ('<span class="mono">FunnelEnvy</span> / %s / <span class="mono">Page test #%s</span>'
                  % (client, test_num(t["id"]))),
        "META": meta,
        "TITLE_H1": esc(t["title"]),
        "LEAD": slot(t["id"], "lead", lab.get("What to test", "")),
        "HYPOTHESIS": slot(t["id"], "hypothesis", lab.get("Why this should work", lab.get("What to test", ""))),
        "MOCKUP": mockup_html,
        "LADDER": "".join(conn),
        "SCORE": slot(t["id"], "score", lab.get("Test Feasibility",
                      "Scored ICE %d (%s)." % (ice_total(t["ice"]), ice_str(t["ice"])))),
        "FOOT_ID": "#%s &middot; %s" % (test_num(t["id"]), esc(program.get("name", ""))),
    })
    return _spoke_base(templates, "#%s %s | %s" % (test_num(t["id"]), esc(t["title"]), esc(program.get("name", ""))),
                       client, main)


def build_spoke_account(play, account, program, templates):
    """Build one `ap-NN.html` off-store play spoke. Mirrors build_spoke_strategic
    and reuses _spoke_base. The hero meta stays data-light (the off-store tag
    only, no truncated client prose in chrome); the cohort, measurement,
    dependencies, and roadmap relationship are full prose-slot sections below."""
    client = esc(program.get("client", ""))
    lab = play["labels"]
    meta = '<span class="x-tag off">Off-store</span>'
    main = render(templates["spoke_account"], {
        "CRUMB": ('<span class="mono">FunnelEnvy</span> / %s / <span class="mono">Account play %s</span>'
                  % (client, play_label(play["id"]))),
        "META": meta,
        "TITLE_H1": esc(play["title"]),
        "LEAD": slot(play["id"], "play-lead", lab.get("The play", "")),
        "PLAY": slot(play["id"], "play", lab.get("The play", "")),
        "COHORT": slot(play["id"], "play-cohort", lab.get("Cohort", "")),
        "RATIONALE": slot(play["id"], "play-rationale", lab.get("Rationale", "")),
        "MEASURE": slot(play["id"], "play-measure", lab.get("How it is measured", "")),
        "DEPENDS": slot(play["id"], "play-depends", lab.get("Dependencies", "")),
        "RELATIONSHIP": slot(play["id"], "play-relationship", lab.get("Relationship to the roadmaps", "")),
        "FOOT_ID": "%s &middot; %s" % (play_label(play["id"]), esc(program.get("name", ""))),
    })
    return _spoke_base(templates, "%s %s | %s" % (play_label(play["id"]), esc(play["title"]), esc(program.get("name", ""))),
                       client, main)


# --------------------------------------------------------------------------
# Asset handling + write
# --------------------------------------------------------------------------

strategic_body_cache = {}  # stash strategic body for hub sequence extraction


def copy_mockup_assets(t, mk, out_dir):
    """Copy a test's mockup assets into out/mockups/<id>/. Return a dict of
    resolved relative image paths keyed by source key ('control_screenshot',
    'screenshot') for whichever resolved to an on-disk file. A control_screenshot
    whose path is missing is silently skipped (degrades to after-only). Source
    paths are taken relative to the edge sidecar's directory (co-located with
    experiment-mockup output under the deliverables tree)."""
    src_base = strategic_body_cache.get("sidecar_dir", "")
    dest = os.path.join(out_dir, "mockups", t["id"])
    rels = {}
    for key, fname in (("control_screenshot", "control.png"),
                       ("screenshot", "screenshot.png"),
                       ("html", "mockup.html")):
        rel = mk.get(key)
        if not rel:
            continue
        src = rel if os.path.isabs(rel) else os.path.join(src_base, rel)
        if os.path.isfile(src):
            os.makedirs(dest, exist_ok=True)
            with open(src, "rb") as r, open(os.path.join(dest, fname), "wb") as w:
                w.write(r.read())
            if key in ("control_screenshot", "screenshot"):
                rels[key] = "mockups/%s/%s" % (t["id"], fname)
    return rels


def load_templates(tpl_dir):
    names = {"base": "base.html", "hub": "hub.html",
             "spoke_strategic": "spoke-strategic.html", "spoke_tactical": "spoke-tactical.html",
             "spoke_account": "spoke-account.html"}
    out = {}
    for key, fname in names.items():
        with open(os.path.join(tpl_dir, fname), encoding="utf-8") as fh:
            out[key] = fh.read()
    return out


def write_site(strategic, tactical, derived, out_dir, tpl_dir, account=None):
    os.makedirs(out_dir, exist_ok=True)
    # copy static assets
    for asset in ("styles.css", "site.js"):
        with open(os.path.join(tpl_dir, asset), encoding="utf-8") as r:
            data = r.read()
        with open(os.path.join(out_dir, asset), "w", encoding="utf-8") as w:
            w.write(data)
    templates = load_templates(tpl_dir)
    program = strategic["program"]
    written = []
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_hub(strategic, tactical, derived, templates, account))
    written.append("index.html")
    for b in strategic["bets"]:
        with open(os.path.join(out_dir, "%s.html" % b["id"]), "w", encoding="utf-8") as fh:
            fh.write(build_spoke_strategic(b, program, templates))
        written.append("%s.html" % b["id"])
    for t in tactical["tests"]:
        if t["status"] == "superseded":
            continue
        with open(os.path.join(out_dir, "%s.html" % t["id"]), "w", encoding="utf-8") as fh:
            fh.write(build_spoke_tactical(t, program, templates, out_dir))
        written.append("%s.html" % t["id"])
    if account is not None:
        for p in account["plays"]:
            with open(os.path.join(out_dir, "%s.html" % p["id"]), "w", encoding="utf-8") as fh:
                fh.write(build_spoke_account(p, account, program, templates))
            written.append("%s.html" % p["id"])
    return written


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministic two-altitude program-site generator.")
    ap.add_argument("--strategic", required=True, help="path to the strategic gold roadmap markdown")
    ap.add_argument("--tactical", required=True, help="path to the tactical gold roadmap markdown")
    ap.add_argument("--edges", required=True, help="path to the edge sidecar ({scope}-program-edges.md)")
    ap.add_argument("--out", required=True, help="output site root directory")
    ap.add_argument("--account-program", default=None,
                    help="optional path to the account-program deliverable ({scope}-account-program.md); "
                         "when present, renders the off-store account altitude (hub section + ap-NN spokes)")
    ap.add_argument("--templates", default=None, help="templates dir (default: ../templates next to this script)")
    args = ap.parse_args(argv)

    tpl_dir = args.templates or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
    tpl_dir = os.path.abspath(tpl_dir)

    sidecar = load_sidecar(args.edges)
    strategic = load_strategic(args.strategic, sidecar)
    tactical = load_tactical(args.tactical, sidecar)
    account = load_account(args.account_program)
    link_edges(strategic, tactical)
    # stash bodies/paths for hub sequence extraction + mockup asset resolution
    with open(args.strategic, encoding="utf-8") as fh:
        _, sbody = parse_frontmatter(fh.read(), required=False)
    strategic_body_cache["strategic"] = sbody
    strategic_body_cache["sidecar_dir"] = os.path.dirname(os.path.abspath(args.edges))

    try:
        gate_notes = run_gate(strategic, tactical, sidecar, account)
    except GateError as ge:
        sys.stderr.write("EDGE-CONTRACT GATE FAILED (%d violation%s):\n"
                         % (len(ge.violations), "" if len(ge.violations) == 1 else "s"))
        for v in ge.violations:
            sys.stderr.write("  - %s\n" % v)
        return 2

    derived = derive(strategic, tactical)
    written = write_site(strategic, tactical, derived, args.out, tpl_dir, account)
    bets, tests = len(strategic["bets"]), sum(1 for t in tactical["tests"] if t["status"] != "superseded")
    mockups = sum(1 for t in tactical["tests"] if t.get("mockup"))
    fnd = strategic.get("foundation") or []
    fnd_note = (" (%d foundation %s)" % (len(fnd), "entry" if len(fnd) == 1 else "entries")) if fnd else ""
    plays_note = (" (%d account plays)" % len(account["plays"])) if account is not None else ""
    for n in gate_notes:
        sys.stdout.write("note: %s\n" % n)
    sys.stdout.write("OK gate passed. Wrote %d pages to %s (%d bets, %d tests, %d with mockups).%s%s\n"
                     % (len(written), args.out, bets, tests, mockups, fnd_note, plays_note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
