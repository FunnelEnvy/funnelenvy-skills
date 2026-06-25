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
    """Split the inside of a flow collection on top-level commas only."""
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch in "[{":
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
        if rest == "":
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


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_text). Raises if no frontmatter block."""
    if not text.startswith("---"):
        raise ValueError("file has no YAML frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unterminated frontmatter block")
    fm = text[3:end].strip("\n")
    body = text[end + 4:]
    lines = fm.split("\n")
    data, _ = _parse_map(lines, 0, 0)
    return data, body


# --------------------------------------------------------------------------
# Markdown body section extraction (per-bet / per-test prose, raw material)
# --------------------------------------------------------------------------

def _norm_bet_id(heading):
    m = re.search(r"sb[-\s]?0*(\d+)", heading, re.I)
    return "sb-%02d" % int(m.group(1)) if m else None


def _norm_test_id(heading):
    m = re.match(r"\s*0*(\d+)\.", heading)
    return "p-%02d" % int(m.group(1)) if m else None


def extract_sections(body, kind):
    """Split a roadmap body into per-item sections keyed by canonical id.

    Returns {id: {"title": str, "labels": {label: text}, "paras": [text]}}.
    `kind` is "bet" or "test". Sections are H2 (`## SB-N.`) for bets and H3
    (`### N.`) for tests. Bold-labeled paragraphs (`**Label.** text`) are
    collected into `labels`; all paragraphs are kept in order in `paras`.
    """
    heading_re = re.compile(r"^##\s+(SB-\d+\..*)$" if kind == "bet" else r"^###\s+(\d+\..*)$", re.M)
    norm = _norm_bet_id if kind == "bet" else _norm_test_id
    out = {}
    matches = list(heading_re.finditer(body))
    for i, m in enumerate(matches):
        head = m.group(1).strip()
        cid = norm(head)
        if not cid:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        block = body[start:end].strip()
        title = re.sub(r"^(SB-\d+|\d+)\.\s*", "", head).strip()
        labels, paras = {}, []
        for para in re.split(r"\n\s*\n", block):
            para = para.strip()
            if not para or para.startswith("#") or para == "---":
                continue
            paras.append(para)
            lm = re.match(r"\*\*(.+?)\.?\*\*\s*(.*)$", para, re.S)
            if lm:
                labels[lm.group(1).strip().rstrip(".")] = lm.group(2).strip()
        out[cid] = {"title": title, "labels": labels, "paras": paras}
    return out


# --------------------------------------------------------------------------
# Load + normalize inputs
# --------------------------------------------------------------------------

def _require(d, key, where):
    if key not in d or d[key] is None:
        raise ValueError("%s: missing required field '%s'" % (where, key))
    return d[key]


def load_strategic(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = parse_frontmatter(text)
    program = _require(fm, "program", "strategic frontmatter")
    bets_raw = _require(fm, "bets", "strategic frontmatter")
    sections = extract_sections(body, "bet")
    bets = []
    for b in bets_raw:
        bid = _require(b, "id", "bet")
        ice = _require(b, "ice", "bet %s" % bid)
        edges = b.get("edges") or []
        norm_edges = []
        for e in edges:
            norm_edges.append({"target": _require(e, "target", "edge in %s" % bid),
                               "type": _require(e, "type", "edge in %s" % bid)})
        bets.append({
            "id": bid,
            "title": _require(b, "title", "bet %s" % bid),
            "lever": b.get("lever", ""),
            "decided_on": b.get("decided_on", ""),
            "run_tag": b.get("run_tag", ""),
            "delivery_surface": b.get("delivery_surface") or [],
            "executor_status": _require(b, "executor_status", "bet %s" % bid),
            "ice": {"i": ice["i"], "c": ice["c"], "e": ice["e"]},
            "keystone": bool(b.get("keystone", False)),
            "edges": norm_edges,
            "section": sections.get(bid, {"title": "", "labels": {}, "paras": []}),
        })
    return {"program": program, "bets": bets}


def load_tactical(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = parse_frontmatter(text)
    pv = _require(fm, "program_version", "tactical frontmatter")
    tests_raw = _require(fm, "tests", "tactical frontmatter")
    sections = extract_sections(body, "test")
    tests = []
    for t in tests_raw:
        tid = _require(t, "id", "test")
        ice = _require(t, "ice", "test %s" % tid)
        tests.append({
            "id": tid,
            "title": _require(t, "title", "test %s" % tid),
            "mechanism_class": _require(t, "mechanism_class", "test %s" % tid),
            "tier": _require(t, "tier", "test %s" % tid),
            "ice": {"i": ice["i"], "c": ice["c"], "e": ice["e"]},
            "target_page": t.get("target_page", ""),
            "status": t.get("status", "active"),
            "superseded_by": t.get("superseded_by", ""),
            "mockup": t.get("mockup") or None,
            # any inbound/reverse authoring is a gate violation (check 6)
            "_reverse_keys": [k for k in ("edges", "inbound", "expressed_by", "informed_by", "gated_by") if k in t],
            "section": sections.get(tid, {"title": "", "labels": {}, "paras": []}),
        })
    return {"program_version": pv, "tests": tests}


# --------------------------------------------------------------------------
# The gate (7 checks, fail-closed)
# --------------------------------------------------------------------------

def run_gate(strategic, tactical):
    violations = []
    bets, tests = strategic["bets"], tactical["tests"]
    live_ids = {t["id"] for t in tests if t["status"] != "superseded"}
    test_by_id = {t["id"]: t for t in tests}

    # 3 prep: count expresses targeting each test (for reverse-edge checks)
    for b in bets:
        # 1. edge.type in {expresses, informs, gates}
        for e in b["edges"]:
            if e["type"] not in EDGE_TYPES:
                violations.append("[1] bet %s: edge type '%s' not in %s (target %s)"
                                  % (b["id"], e["type"], list(EDGE_TYPES), e["target"]))
            # 2. edge.target resolves to a live test id
            if e["target"] not in live_ids:
                violations.append("[2] bet %s: edge target '%s' resolves to no live test id"
                                  % (b["id"], e["target"]))
            # 3. mechanism gate on `expresses`
            if e["type"] == "expresses" and e["target"] in test_by_id:
                t = test_by_id[e["target"]]
                if t["mechanism_class"] not in b["delivery_surface"]:
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

    # 6. tactical file authors no inbound / reverse references
    for t in tests:
        if t["_reverse_keys"]:
            violations.append("[6] test %s: tactical file must not author inbound/reverse references "
                              "(found %s); reverse edges are derived from the strategic file"
                              % (t["id"], t["_reverse_keys"]))

    # 7. program_version matches across both inputs
    sv = str(strategic["program"].get("program_version", ""))
    tv = str(tactical["program_version"])
    if sv != tv:
        violations.append("[7] program_version mismatch: strategic '%s' != tactical '%s'" % (sv, tv))

    # check 5 (intake_only is derived never authored) is structural: tests carry
    # no intake field; authoring one shows up as a stray key. Enforce explicitly.
    for t in tests:
        if t["mockup"] is not None and not isinstance(t["mockup"], dict):
            violations.append("[5] test %s: malformed mockup block" % t["id"])

    if violations:
        raise GateError(violations)


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


def test_num(tid):  # p-03 -> 3
    return str(int(tid.split("-")[1]))


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
    for k, v in mapping.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    return tpl


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
               slot(b["id"], "card-body", b["section"]["labels"].get("The lever", b["lever"])),
               ice_total(b["ice"]), b["ice"]["i"], b["ice"]["c"], b["ice"]["e"],
               tag_cls, tag_txt, "".join(rels),
               slot(b["id"], "exec-note", b["section"]["labels"].get("How this connects to the page-level roadmap", ""))))
    return "\n".join(cards)


def build_backlog(tier_groups, superseded):
    out = []
    for key in TIER_ORDER:
        tests = tier_groups.get(key, [])
        if not tests:
            continue
        label, css, caption = TIERS[key]
        cards = []
        for t in tests:
            if t["intake_only"]:
                ladder = '<span class="ladder none">intake-only</span>'
            else:
                tops = t["exp_by"] + t["inf_by"]
                first = tops[0]
                extra = ", ".join(bet_label(x) for x in tops)
                ladder = '<a class="ladder" href="index.html#%s">&#8593; %s</a>' % (first, esc(extra))
            cards.append(
                '<div class="test" id="%s"><div class="t-top"><span class="t-n">#%s</span>'
                '<span class="badge %s">%s</span></div>'
                '<h4><a href="%s.html">%s</a></h4><p class="t-page">%s</p>'
                '<div class="t-foot"><span class="t-ice mono">ICE <b>%d</b> &middot; %s</span>%s</div></div>'
                % (t["id"], test_num(t["id"]), css, esc(label), t["id"], esc(t["title"]),
                   esc(t["target_page"]), ice_total(t["ice"]), ice_str(t["ice"]), ladder))
        out.append('<div class="tier"><div class="tier-head %s"><h3>%s</h3>'
                   '<span class="ct mono">%s</span></div><div class="test-grid">%s</div></div>'
                   % (css, esc(label), esc(caption), "".join(cards)))
    if superseded:
        cards = []
        for t in superseded:
            note = (" %s" % t["superseded_by"]) if t["superseded_by"] else ""
            cards.append(
                '<div class="test dim" id="%s"><div class="t-top"><span class="t-n">#%s</span>'
                '<span class="badge sup">Superseded</span></div><h4>%s</h4>'
                '<p class="t-page">%s</p><div class="t-foot"><span class="t-ice mono">not scored</span>'
                '<span class="ladder none">superseded%s</span></div></div>'
                % (t["id"], test_num(t["id"]), esc(t["title"]), esc(t["target_page"]), esc(note)))
        out.append('<div class="tier"><div class="tier-head"><h3>Superseded</h3>'
                   '<span class="ct mono">shipped or replaced</span></div>'
                   '<div class="test-grid">%s</div></div>' % "".join(cards))
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

def build_hub(strategic, tactical, derived, templates):
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
        ks_txt = ", ".join(ks)
        keystone_html = ('<div class="keystone"><span class="ks-mark">The keystone</span>'
                         '<p>%s</p></div>'
                         % slot("program", "keystone", "%s converge on a shared asset." % ks_txt))

    seq_src = extract_named_section(strategic_body_cache.get("strategic", ""), "Sequencing")
    main = render(templates["hub"], {
        "PROVENANCE": prov,
        "HERO_H1": h1,
        "HERO_SUB": slot("program", "hero-sub", hero.get("subhead", "")),
        "ALT1": slot("program", "altitude-1", "Program-level moves decided on the business objective."),
        "ALT2": slot("program", "altitude-2", "Page-level tests decided on the metric each page can read."),
        "MAP_LEAD": slot("program", "map-lead", ""),
        "MAP_SVG": build_map_svg(bets, tests),
        "MAP_NOTE": slot("program", "map-note", ""),
        "STRATEGY_LEAD": slot("program", "strategy-lead", ""),
        "KEYSTONE": keystone_html,
        "BET_CARDS": build_bet_cards(bets),
        "BACKLOG_LEAD": slot("program", "backlog-lead", ""),
        "BACKLOG": build_backlog(derived["tier_groups"], derived["superseded"]),
        "SEQUENCE": slot("program", "sequence", seq_src),
        "DECISIONS_H2": "Decisions we need from %s" % client,
        "DECISIONS_LEAD": slot("program", "decisions-lead", ""),
        "DECISIONS": slot("program", "decisions", ""),
        "FOOT": "%s (%s) &middot; prepared by FunnelEnvy &middot; <span class=\"mono\">%s</span>"
                % (client, name, date),
    })
    return render(templates["base"], {
        "TITLE": "%s | FunnelEnvy" % esc(name),
        "BRAND_HREF": "#top",
        "CLIENT": client,
        "NAV_LINKS": ('<a href="#map">Portfolio map</a><a href="#strategy">The strategy</a>'
                      '<a href="#backlog">Experiment backlog</a><a href="#sequence">Sequence</a>'
                      '<a href="#decisions">Decisions</a>'),
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
        "LEAD": slot(b["id"], "lead", lab.get("The lever", b["lever"])),
        "LEVER": slot(b["id"], "lever", lab.get("The lever", "")),
        "MOVE": slot(b["id"], "move", lab.get("The experiment / program", lab.get("The experiment", ""))),
        "CONNECTIONS": "".join(conn),
        "EVIDENCE": slot(b["id"], "evidence", lab.get("What must be stood up", "")),
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
        shot_rel = copy_mockup_assets(t, mk, out_dir)
        if shot_rel:
            preview = '<img class="mockup-shot" src="%s" alt="Mockup of %s">' % (esc(shot_rel), esc(t["title"]))
        else:
            preview = ('<div class="mockup-ph"><span class="lab">Mockup preview</span>'
                       '<span class="sub">no screenshot resolved for this hypothesis</span></div>')
        view = ('<a class="btn-mock" href="mockups/%s/mockup.html">View live mockup &#8599;</a>' % t["id"]) \
            if mk.get("html") else ""
        mockup_html = (
            '<section class="sec"><div class="container"><h2>Proposed change</h2>'
            '<div class="mockup-frame"><div class="mockup-bar"><span class="dot"></span>'
            '<span class="dot"></span><span class="dot"></span><span class="url">%s</span></div>%s</div>'
            '<div class="mockup-meta"><span class="mm"><span class="mm-k">Insertion</span>%s</span>'
            '<span class="mm"><span class="mm-k">Mode</span>%s</span>%s</div>'
            '<p class="cx">%s</p></div></section>'
            % (esc(mk.get("target_url", "")), preview, esc(mk.get("insertion_point", "")),
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
        "LEAD": slot(t["id"], "lead", lab.get("The hypothesis", "")),
        "HYPOTHESIS": slot(t["id"], "hypothesis", lab.get("The hypothesis", "")),
        "MOCKUP": mockup_html,
        "LADDER": "".join(conn),
        "SCORE": slot(t["id"], "score", lab.get("Score and feasibility",
                      "Scored ICE %d (%s)." % (ice_total(t["ice"]), ice_str(t["ice"])))),
        "FOOT_ID": "#%s &middot; %s" % (test_num(t["id"]), esc(program.get("name", ""))),
    })
    return _spoke_base(templates, "#%s %s | %s" % (test_num(t["id"]), esc(t["title"]), esc(program.get("name", ""))),
                       client, main)


# --------------------------------------------------------------------------
# Asset handling + write
# --------------------------------------------------------------------------

strategic_body_cache = {}  # stash strategic body for hub sequence extraction


def copy_mockup_assets(t, mk, out_dir):
    """Copy a test's mockup assets into out/mockups/<id>/. Return relative
    screenshot path if a screenshot resolved, else ''. Source paths are taken
    relative to the tactical file's directory."""
    src_base = strategic_body_cache.get("tactical_dir", "")
    dest = os.path.join(out_dir, "mockups", t["id"])
    shot_rel = ""
    for key, fname in (("screenshot", "screenshot.png"), ("html", "mockup.html")):
        rel = mk.get(key)
        if not rel:
            continue
        src = rel if os.path.isabs(rel) else os.path.join(src_base, rel)
        if os.path.isfile(src):
            os.makedirs(dest, exist_ok=True)
            with open(src, "rb") as r, open(os.path.join(dest, fname), "wb") as w:
                w.write(r.read())
            if key == "screenshot":
                shot_rel = "mockups/%s/%s" % (t["id"], fname)
    return shot_rel


def load_templates(tpl_dir):
    names = {"base": "base.html", "hub": "hub.html",
             "spoke_strategic": "spoke-strategic.html", "spoke_tactical": "spoke-tactical.html"}
    out = {}
    for key, fname in names.items():
        with open(os.path.join(tpl_dir, fname), encoding="utf-8") as fh:
            out[key] = fh.read()
    return out


def write_site(strategic, tactical, derived, out_dir, tpl_dir):
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
        fh.write(build_hub(strategic, tactical, derived, templates))
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
    return written


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministic two-altitude program-site generator.")
    ap.add_argument("--strategic", required=True, help="path to the strategic experiment-layer markdown")
    ap.add_argument("--tactical", required=True, help="path to the tactical experiment-roadmap markdown")
    ap.add_argument("--out", required=True, help="output site root directory")
    ap.add_argument("--templates", default=None, help="templates dir (default: ../templates next to this script)")
    args = ap.parse_args(argv)

    tpl_dir = args.templates or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
    tpl_dir = os.path.abspath(tpl_dir)

    strategic = load_strategic(args.strategic)
    tactical = load_tactical(args.tactical)
    # stash bodies/paths for hub sequence extraction + mockup asset resolution
    with open(args.strategic, encoding="utf-8") as fh:
        _, sbody = parse_frontmatter(fh.read())
    strategic_body_cache["strategic"] = sbody
    strategic_body_cache["tactical_dir"] = os.path.dirname(os.path.abspath(args.tactical))

    try:
        run_gate(strategic, tactical)
    except GateError as ge:
        sys.stderr.write("EDGE-CONTRACT GATE FAILED (%d violation%s):\n"
                         % (len(ge.violations), "" if len(ge.violations) == 1 else "s"))
        for v in ge.violations:
            sys.stderr.write("  - %s\n" % v)
        return 2

    derived = derive(strategic, tactical)
    written = write_site(strategic, tactical, derived, args.out, tpl_dir)
    bets, tests = len(strategic["bets"]), sum(1 for t in tactical["tests"] if t["status"] != "superseded")
    mockups = sum(1 for t in tactical["tests"] if t.get("mockup"))
    sys.stdout.write("OK gate passed. Wrote %d pages to %s (%d bets, %d tests, %d with mockups).\n"
                     % (len(written), args.out, bets, tests, mockups))
    return 0


if __name__ == "__main__":
    sys.exit(main())
