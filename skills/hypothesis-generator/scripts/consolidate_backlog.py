#!/usr/bin/env python3
"""
consolidate_backlog - deterministic consolidation, sizing, key carry-forward and
ranking of lens candidate cards for the hypothesis-generator skill.

The lens subagents each return a JSON array of candidate cards. This script turns the
pooled cards into one row per distinct opportunity, sizes every row against the
SKILL.md `Decision Posture`, carries prior roadmap keys forward, and later ranks the
scored rows into readiness tiers. Stdlib only, Python 3.8+.

Usage:
    python3 consolidate_backlog.py consolidate --cards <path|-> [--prior <roadmap.md> ...]
        [--boundary YYYY-MM-DD] [--posture <SKILL.md>] [--floor N]
    python3 consolidate_backlog.py rank --rows <path|-> --write-ups N
        [--history-items ID,...] [--excluded-history ID,...]

Both subcommands print one JSON object on stdout. Errors go to stderr.

Exit codes:
    0  OK
    1  input error: invalid card or row JSON, two rank rows sharing a key, or an
       unreadable --prior file. stderr names the card or row index and the field.
    2  usage error (argparse), including --write-ups outside 8 to 12 and a malformed
       --boundary date
    3  posture unreadable: the --posture file has no `## Decision Posture` table, a
       row is missing, a number is unreadable or out of range, or the stated M
       disagrees with the M computed from the significance and power rows. stderr
       names the row.

Posture (consolidate only). Read at run time from the `## Decision Posture` table in
--posture, which defaults to ../SKILL.md beside this script's real path. Each row is
found by the start of its Constant cell, and the first number in its Default cell is
taken: Significance, Power, Relative MDE, Maximum A/B read window (weeks), and Hard
gates (two numbers: conversions per variant, then minimum days). Significance, Power
and Relative MDE accept a fraction (0.20) or a percent (20%, read as 0.20) and must
lie strictly between 0 and 1; the other numbers must be positive. Swapped Hard gates
numbers are not detected. M is computed as
2 * (z(1 - (1 - significance) / 2) + z(power))^2 and used unrounded; rounded to two
decimals it must equal the first number in the `Multiplier M` row. Cards are
validated before the posture is read, so a bad card exits 1 even when the posture
would exit 3.

Card schema (consolidate input, a JSON array of objects). Required: lens (surface,
persona-journey, history, strategic, competitive-proof), altitude (tactical,
strategic), title, surfaces (non-empty list), mechanism_key (kebab-case), mechanism,
evidence (non-empty list of non-empty strings). lever_family is required on a
strategic card; the script checks it is a kebab-case token and does not hold the
family list. Optional: design (ab default, holdout, pre-post), arms (integer >= 2,
default 2), baseline {monthly_sessions, rate, window_start, source}, blockers (values
metric-not-tracked, no-baseline, verify-current-state, design-change,
client-decision), annotations, pattern (boolean), history_items, spec_items. Unknown
fields are ignored.

Merging. Cards merge when they share altitude and mechanism_key and their normalized
surface sets intersect (lowercased, trimmed, one trailing "/" dropped); merging is
transitive. A merged row unions surfaces, evidence, lenses, blockers, annotations,
history_items and spec_items in first-seen order. Its representative card is the
first card with pattern true in input order, else the first card in lens order
(surface, persona-journey, history, strategic, competitive-proof) then input order.
title, mechanism and design come from the representative. lever_family, arms and
baseline come from the first card in that same order that carries them. merged_from
is the card count. Then a tactical row whose mechanism_key matches a strategic row
with the same design folds into the first such strategic row: its surfaces become the
annotation "page expression: <surfaces>" and its other lists union in. When only
strategic rows with a different design match, both rows stay and each carries
"shares a mechanism with <other title>; sequence the reads apart".

Sizing and read model, first match wins:
    design holdout                                  -> holdout, no sizing
    design pre-post                                 -> pre-post, no sizing
    no baseline, missing rate or monthly_sessions   -> unsized, reason no-baseline
      (a rate outside (0, 1) or sessions <= 0 count as missing)
    --boundary B and window_start null or before B  -> unsized, reason refused-window
    weeks <= Maximum A/B read window                -> ab: n_per_variant, weeks
    conversions per variant over the window >= gate -> directional: mde_achievable
    otherwise                                       -> pre-post: conversions per variant
where n_per_variant = ceil(M * p * (1 - p) / (p * relative_mde)^2),
weeks = max(arms * n_per_variant / (monthly_sessions / 30) / 7, min_days / 7),
n_window = (monthly_sessions / 30) * window_weeks * 7 / arms, and
mde_achievable = sqrt(M * p * (1 - p) / n_window) / p. Every sizing object echoes
monthly_sessions and rate. weeks rounds to 2 decimals and mde_achievable to 4 in the
output; comparisons use the unrounded values.

Key carry-forward, per altitude. Each --prior file is assigned to an altitude by its
H1 (an H1 containing "Strategic Experiment Roadmap" is strategic, any other H1 is
tactical); two priors for one altitude, or a prior with no H1, exit 1. Prior entries
are every `### N.` section carrying a `**Key:**` line plus every `## Backlog` table
row, in document order. (1) Title pass: a row whose title, trimmed and lowercased,
equals a prior entry's title takes that entry's key. (2) Mechanism pass: a remaining
row takes the key of a remaining prior entry whose mechanism words equal its
mechanism_key and whose surfaces intersect its own. Mechanism words come from the
`**Mechanism:**` label or the `Mechanism` column, lowercased with runs of whitespace
replaced by hyphens and a trailing period dropped; surfaces come from `**Page:**`,
`**Lever:**` or the `Surface` column, split on commas. (3) Mint: slugify(title) per
modules/slugify.md, with -2, -3 and so on appended on a collision with a key already
assigned in the run or with any prior key, dropped ones included. Each prior key is
used at most once: when a key repeats across prior entries (a write-up and a backlog
row, say), the first entry stands (tactical prior first, then document order) and the
later ones are ignored. Within a pass, a row takes the first unused entry in document
order.

consolidate output keys: posture, rows, lens_counts, lens_shortfalls, cards_in,
rows_out, dropped_prior_keys. Rows are ordered by altitude (tactical first), then key.

rank input: the consolidate rows (a JSON array, or the whole consolidate object) with
ice {i, c, e} (integers 1 to 5) added to every row; keys must be unique across the
input. Readiness, first match wins:
client-decision blocker -> needs-client-decision; metric-not-tracked or no-baseline
blocker, or read_model unsized -> needs-measurement; design-change blocker ->
needs-design-change; otherwise ready-now. A verify-current-state blocker records a
pre-launch check and does not set the tier: a row whose only blocker it is ranks
ready-now. Each row gets prelaunch_check, true when its blockers contain
verify-current-state; the blocker itself stays on the row. Within each
altitude rows sort by readiness tier (ready-now, needs-design-change,
needs-measurement, needs-client-decision), then ICE total descending, then Confidence
descending, then key ascending. Each row gets rank (1-based within its altitude) and
write_up (true for the first --write-ups rows of each altitude). history_ledger maps
each --history-items id to the key of the first ranked row carrying it, else to
"excluded" when the id is in --excluded-history; history_unaccounted lists the ids
with neither. rank output keys: rows, history_ledger, history_unaccounted.
"""
import argparse
import datetime
import json
import math
import os
import re
import statistics
import sys

LENSES = ("surface", "persona-journey", "history", "strategic", "competitive-proof")
ALTITUDES = ("tactical", "strategic")
DESIGNS = ("ab", "holdout", "pre-post")
BLOCKERS = ("metric-not-tracked", "no-baseline", "verify-current-state", "design-change",
            "client-decision")
READ_MODELS = ("ab", "directional", "pre-post", "holdout", "unsized")
READINESS = ("ready-now", "needs-design-change", "needs-measurement", "needs-client-decision")
MEASUREMENT_BLOCKERS = ("metric-not-tracked", "no-baseline")
LIST_FIELDS = ("surfaces", "evidence", "lenses", "blockers", "annotations", "history_items",
               "spec_items")

KEBAB_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NUMBER_RX = re.compile(r"\d+(?:\.\d+)?")
PERCENT_RX = re.compile(r"(\d+(?:\.\d+)?)\s*(%)?")
SECTION_RX = re.compile(r"^###\s+\d+\.\s+(.*?)\s*$")
LABEL_RX = re.compile(r"^\s*(?:[-*]\s+)?\*\*(Key|Mechanism|Page|Lever):\*\*\s*(.*?)\s*$")


class InputError(Exception):
    """Invalid card, row or prior input (exit 1)."""


class PostureError(Exception):
    """Unreadable Decision Posture table (exit 3)."""


# --------------------------------------------------------------------------
# Posture
# --------------------------------------------------------------------------

def parse_posture(text):
    """Return the posture constants read from a `## Decision Posture` table.

    The dict carries significance, power, relative_mde, M (unrounded), max_ab_weeks,
    min_conversions_per_variant and min_days. Raises PostureError naming the row when
    the section or a row is missing, a number is unreadable or out of range, or the
    stated M disagrees with the computed M at two decimals.
    """
    lines = text.split("\n")
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Decision Posture":
            start = idx
            break
    if start is None:
        raise PostureError("no '## Decision Posture' section")
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 2:
            rows.append(cells)

    def numbers(name, count, percent=False):
        for cells in rows:
            if cells[0].startswith(name):
                found = (PERCENT_RX if percent else NUMBER_RX).findall(cells[1])
                if len(found) < count:
                    raise PostureError("row '%s': no readable number in its Default cell" % name)
                if not percent:
                    return [float(n) for n in found[:count]]
                return [float(n) / 100 if pct else float(n) for n, pct in found[:count]]
        raise PostureError("row '%s' is missing from the Decision Posture table" % name)

    significance = numbers("Significance", 1, percent=True)[0]
    power = numbers("Power", 1, percent=True)[0]
    relative_mde = numbers("Relative MDE", 1, percent=True)[0]
    max_ab_weeks = numbers("Maximum A/B read window", 1)[0]
    min_conv, min_days = numbers("Hard gates", 2)
    stated_m = numbers("Multiplier M", 1)[0]
    for name, value in (("Significance", significance), ("Power", power),
                        ("Relative MDE", relative_mde)):
        if not 0 < value < 1:
            raise PostureError("row '%s': value %s is outside (0, 1)" % (name, value))
    for name, value in (("Maximum A/B read window", max_ab_weeks),
                        ("Hard gates", min_conv), ("Hard gates", min_days)):
        if value <= 0:
            raise PostureError("row '%s': value %s is not positive" % (name, value))
    normal = statistics.NormalDist()
    m = 2 * (normal.inv_cdf(1 - (1 - significance) / 2) + normal.inv_cdf(power)) ** 2
    if round(m, 2) != round(stated_m, 2):
        raise PostureError("row 'Multiplier M': states %.2f but significance %s and power %s "
                           "give %.2f" % (stated_m, significance, power, m))
    return {
        "significance": significance,
        "power": power,
        "relative_mde": relative_mde,
        "M": m,
        "max_ab_weeks": max_ab_weeks,
        "min_conversions_per_variant": int(min_conv),
        "min_days": int(min_days),
    }


def read_posture(path):
    """Return parse_posture's dict for the file at `path`; an unreadable file raises PostureError."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        raise PostureError("cannot read posture file %s: %s" % (path, exc))
    return parse_posture(text)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_date(value):
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return False
    try:
        datetime.date(int(value[:4]), int(value[5:7]), int(value[8:10]))
    except ValueError:
        return False
    return True


def _string_list(obj, field, fail, required=False):
    value = obj.get(field)
    if value is None:
        if required:
            fail(field, "is required")
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        fail(field, "must be a list of non-empty strings")
    if required and not value:
        fail(field, "needs at least one entry")
    return [v.strip() for v in value]


def validate_card(card, idx):
    """Return a normalized copy of one card, or raise InputError naming its index and field."""
    def fail(field, why):
        raise InputError("card %d: field '%s' %s" % (idx, field, why))

    if not isinstance(card, dict):
        raise InputError("card %d: not a JSON object" % idx)
    for field, allowed in (("lens", LENSES), ("altitude", ALTITUDES)):
        if card.get(field) not in allowed:
            fail(field, "must be one of %s" % ", ".join(allowed))
    for field in ("title", "mechanism"):
        if not isinstance(card.get(field), str) or not card[field].strip():
            fail(field, "must be a non-empty string")
    if not isinstance(card.get("mechanism_key"), str) or not KEBAB_RX.match(card["mechanism_key"]):
        fail("mechanism_key", "must be a kebab-case slug")
    out = {
        "lens": card["lens"],
        "altitude": card["altitude"],
        "title": card["title"].strip(),
        "mechanism": card["mechanism"].strip(),
        "mechanism_key": card["mechanism_key"],
        "surfaces": _string_list(card, "surfaces", fail, required=True),
        "evidence": _string_list(card, "evidence", fail, required=True),
        "annotations": _string_list(card, "annotations", fail),
        "history_items": _string_list(card, "history_items", fail),
        "spec_items": _string_list(card, "spec_items", fail),
        "blockers": _string_list(card, "blockers", fail),
    }
    for blocker in out["blockers"]:
        if blocker not in BLOCKERS:
            fail("blockers", "has unknown value '%s'" % blocker)
    family = card.get("lever_family")
    if family is None:
        if out["altitude"] == "strategic":
            fail("lever_family", "is required on a strategic card")
    elif not isinstance(family, str) or not KEBAB_RX.match(family):
        fail("lever_family", "must be a kebab-case family token")
    out["lever_family"] = family
    design = card.get("design")
    if design is not None and design not in DESIGNS:
        fail("design", "must be one of %s" % ", ".join(DESIGNS))
    out["design"] = design
    arms = card.get("arms")
    if arms is not None and (not _is_int(arms) or arms < 2):
        fail("arms", "must be an integer of at least 2")
    out["arms"] = arms
    pattern = card.get("pattern", False)
    if not isinstance(pattern, bool):
        fail("pattern", "must be a boolean")
    out["pattern"] = pattern
    baseline = card.get("baseline")
    if baseline is not None:
        if not isinstance(baseline, dict):
            fail("baseline", "must be an object")
        sessions = baseline.get("monthly_sessions")
        if sessions is not None and (not _is_number(sessions) or sessions < 0):
            fail("baseline.monthly_sessions", "must be a non-negative number")
        rate = baseline.get("rate")
        if rate is not None and (not _is_number(rate) or not 0 <= rate <= 1):
            fail("baseline.rate", "must be a number from 0 to 1")
        start = baseline.get("window_start")
        if start is not None and not _valid_date(start):
            fail("baseline.window_start", "must be YYYY-MM-DD or null")
        source = baseline.get("source")
        if source is not None and not isinstance(source, str):
            fail("baseline.source", "must be a string")
    out["baseline"] = baseline
    return out


def validate_cards(data):
    """Return the validated card list; a non-array input or any bad card raises InputError."""
    if not isinstance(data, list):
        raise InputError("cards input must be a JSON array")
    cards = []
    for idx, card in enumerate(data):
        valid = validate_card(card, idx)
        valid["_idx"] = idx
        cards.append(valid)
    return cards


# --------------------------------------------------------------------------
# Dedup and merges
# --------------------------------------------------------------------------

def norm_surface(surface):
    """Return a surface lowercased and trimmed, with one trailing "/" dropped."""
    s = surface.strip().lower()
    if s.endswith("/"):
        s = s[:-1]
    return s


def _union(target, values, normalize=None):
    seen = set(normalize(v) if normalize else v for v in target)
    for value in values:
        mark = normalize(value) if normalize else value
        if mark not in seen:
            seen.add(mark)
            target.append(value)


def _representative_order(cards):
    pattern = [c for c in cards if c["pattern"]]
    rest = sorted((c for c in cards if not c["pattern"]),
                  key=lambda c: (LENSES.index(c["lens"]), c["_idx"]))
    return pattern + rest


def merge_group(cards):
    """Return one row built from a group of cards already sorted in input order."""
    ordered = _representative_order(cards)
    rep = ordered[0]

    def first(field):
        for card in ordered:
            if card.get(field) is not None:
                return card[field]
        return None

    row = {
        "title": rep["title"],
        "altitude": rep["altitude"],
        "mechanism_key": rep["mechanism_key"],
        "mechanism": rep["mechanism"],
        "design": rep["design"] or "ab",
        "lever_family": first("lever_family"),
        "arms": first("arms") or 2,
        "baseline": first("baseline"),
        "merged_from": len(cards),
        "_first": cards[0]["_idx"],
    }
    for field in LIST_FIELDS:
        row[field] = []
    for card in cards:
        _union(row["surfaces"], card["surfaces"], norm_surface)
        _union(row["lenses"], [card["lens"]])
        for field in ("evidence", "blockers", "annotations", "history_items", "spec_items"):
            _union(row[field], card[field])
    return row


def merge_cards(cards):
    """Return rows after the same-mechanism merge and the strategic-absorbs-tactical fold."""
    parent = list(range(len(cards)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    surfaces = [set(norm_surface(s) for s in c["surfaces"]) for c in cards]
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            if (cards[i]["altitude"] == cards[j]["altitude"]
                    and cards[i]["mechanism_key"] == cards[j]["mechanism_key"]
                    and surfaces[i] & surfaces[j]):
                parent[find(j)] = find(i)
    groups = {}
    for i, card in enumerate(cards):
        groups.setdefault(find(i), []).append(card)
    rows = [merge_group(g) for g in sorted(groups.values(), key=lambda g: g[0]["_idx"])]

    strategic = [r for r in rows if r["altitude"] == "strategic"]
    kept = []
    for row in rows:
        if row["altitude"] != "tactical":
            kept.append(row)
            continue
        matches = [s for s in strategic if s["mechanism_key"] == row["mechanism_key"]]
        same = [s for s in matches if s["design"] == row["design"]]
        if same:
            target = same[0]
            _union(target["annotations"], ["page expression: %s" % ", ".join(row["surfaces"])])
            _union(target["lenses"], row["lenses"])
            for field in ("evidence", "blockers", "annotations", "history_items", "spec_items"):
                _union(target[field], row[field])
            target["merged_from"] += row["merged_from"]
            continue
        for other in matches:
            _union(row["annotations"],
                   ["shares a mechanism with %s; sequence the reads apart" % other["title"]])
            _union(other["annotations"],
                   ["shares a mechanism with %s; sequence the reads apart" % row["title"]])
        kept.append(row)
    return kept


# --------------------------------------------------------------------------
# Sizing
# --------------------------------------------------------------------------

def size_row(design, arms, baseline, posture, boundary=None):
    """Return (read_model, sizing, unsized_reason) for one row, per the module's sizing table."""
    if design == "holdout":
        return "holdout", None, None
    if design == "pre-post":
        return "pre-post", None, None
    base = baseline or {}
    sessions = base.get("monthly_sessions")
    rate = base.get("rate")
    if sessions is None or rate is None or sessions <= 0 or not 0 < rate < 1:
        return "unsized", None, "no-baseline"
    if boundary is not None:
        start = base.get("window_start")
        if start is None or start < boundary:
            return "unsized", None, "refused-window"
    m = posture["M"]
    daily = sessions / 30.0
    variance = m * rate * (1 - rate)
    n_per_variant = int(math.ceil(variance / (rate * posture["relative_mde"]) ** 2))
    weeks = max(arms * n_per_variant / daily / 7, posture["min_days"] / 7.0)
    echo = {"monthly_sessions": sessions, "rate": rate}
    if weeks <= posture["max_ab_weeks"]:
        sizing = {"n_per_variant": n_per_variant, "weeks": round(weeks, 2)}
        sizing.update(echo)
        return "ab", sizing, None
    window_weeks = posture["max_ab_weeks"]
    n_window = daily * window_weeks * 7 / arms
    conversions = n_window * rate
    if conversions >= posture["min_conversions_per_variant"]:
        sizing = {
            "mde_achievable": round(math.sqrt(variance / n_window) / rate, 4),
            "window_weeks": window_weeks,
            "n_window": int(round(n_window)),
            "conversions_per_variant": round(conversions, 1),
        }
        sizing.update(echo)
        return "directional", sizing, None
    sizing = {"conversions_per_variant": round(conversions, 1), "window_weeks": window_weeks}
    sizing.update(echo)
    return "pre-post", sizing, None


# --------------------------------------------------------------------------
# Key carry-forward
# --------------------------------------------------------------------------

def slugify(name):
    """Return the modules/slugify.md Python Fallback slug for `name`."""
    s = name.lower().strip()
    s = re.sub(r'^(the|a|an)\s+', '', s)
    s = re.sub(r'\s+(inc\.?|llc|llp|ltd\.?|corp\.?|co\.|plc)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def _norm_mechanism(text):
    if not text:
        return None
    return re.sub(r"\s+", "-", text.strip().lower().rstrip(".").strip())


def _split_surfaces(text):
    return set(norm_surface(s) for s in (text or "").split(",") if s.strip())


def _clean_key(text):
    return text.strip().strip("`").strip()


def parse_prior(text, path):
    """Return (altitude, entries) for a prior roadmap body.

    entries is a list of {key, title, mechanism, surfaces} in document order, from
    `### N.` sections with a `**Key:**` line and `## Backlog` table rows. Raises
    InputError when the file has no H1.
    """
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                lines = lines[idx + 1:]
                break
    h1 = next((ln for ln in lines if ln.startswith("# ")), None)
    if h1 is None:
        raise InputError("prior %s: no H1 heading" % path)
    altitude = "strategic" if "strategic experiment roadmap" in h1.lower() else "tactical"
    entries = []
    section = None
    in_backlog = False
    header = None

    def close():
        if section is not None and section["key"]:
            entries.append(section)

    for line in lines:
        if line.startswith("#"):
            close()
            section = None
            match = SECTION_RX.match(line)
            if match:
                section = {"key": "", "title": match.group(1), "mechanism": None, "surfaces": set()}
            if line.startswith("## "):
                in_backlog = line[3:].strip().lower().startswith("backlog")
                header = None
            continue
        if section is not None:
            label = LABEL_RX.match(line)
            if label:
                name, value = label.group(1), label.group(2)
                if name == "Key":
                    section["key"] = _clean_key(value)
                elif name == "Mechanism":
                    section["mechanism"] = _norm_mechanism(value)
                else:
                    section["surfaces"] |= _split_surfaces(value)
            continue
        if in_backlog and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = [c.lower() for c in cells]
                continue
            if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                continue
            record = dict(zip(header, cells))
            key = _clean_key(record.get("key", ""))
            if key:
                entries.append({
                    "key": key,
                    "title": record.get("title", ""),
                    "mechanism": _norm_mechanism(record.get("mechanism")),
                    "surfaces": _split_surfaces(record.get("surface")),
                })
    close()
    return altitude, entries


def assign_keys(rows, priors):
    """Set key and key_source on every row; return the dropped prior keys.

    `priors` maps altitude to that altitude's prior entries. A repeated prior key is used
    once: the first entry stands (tactical prior first, then document order) and later
    ones are ignored. A minted key never equals any prior key, dropped ones included.
    """
    dropped = []
    prior_keys = set()
    for altitude in ALTITUDES:
        alt_rows = [r for r in rows if r["altitude"] == altitude]
        prior = []
        for entry in priors.get(altitude, []):
            if entry["key"] not in prior_keys:
                prior_keys.add(entry["key"])
                prior.append(entry)
        taken = [False] * len(prior)
        for row in alt_rows:
            title = row["title"].strip().lower()
            for j, entry in enumerate(prior):
                if not taken[j] and entry["title"].strip().lower() == title:
                    row["key"], row["key_source"] = entry["key"], "title"
                    taken[j] = True
                    break
        for row in alt_rows:
            if row.get("key"):
                continue
            surfaces = set(norm_surface(s) for s in row["surfaces"])
            for j, entry in enumerate(prior):
                if (not taken[j] and entry["mechanism"] == row["mechanism_key"]
                        and entry["surfaces"] & surfaces):
                    row["key"], row["key_source"] = entry["key"], "mechanism"
                    taken[j] = True
                    break
        dropped.extend({"key": e["key"], "title": e["title"]}
                       for j, e in enumerate(prior) if not taken[j])
    used = set(r["key"] for r in rows if r.get("key")) | prior_keys
    for altitude in ALTITUDES:
        for row in rows:
            if row["altitude"] != altitude or row.get("key"):
                continue
            base = slugify(row["title"]) or "item"
            key, n = base, 2
            while key in used:
                key, n = "%s-%d" % (base, n), n + 1
            used.add(key)
            row["key"], row["key_source"] = key, "minted"
    return dropped


# --------------------------------------------------------------------------
# Subcommands
# --------------------------------------------------------------------------

ROW_FIELDS = ("key", "key_source", "title", "altitude", "surfaces", "mechanism_key", "mechanism",
              "lever_family", "lenses", "evidence", "design", "arms", "read_model", "sizing",
              "unsized_reason", "blockers", "annotations", "history_items", "spec_items",
              "merged_from")


def consolidate(cards_data, posture, priors=None, boundary=None, floor=10):
    """Return the consolidate output object for raw card JSON data.

    `priors` maps altitude to prior entries (see parse_prior). Raises InputError on a
    bad card.
    """
    cards = validate_cards(cards_data)
    rows = merge_cards(cards)
    for row in rows:
        row["read_model"], row["sizing"], row["unsized_reason"] = size_row(
            row["design"], row["arms"], row["baseline"], posture, boundary)
    dropped = assign_keys(rows, priors or {})
    rows.sort(key=lambda r: (ALTITUDES.index(r["altitude"]), r["key"]))
    counts = dict((lens, 0) for lens in LENSES)
    for card in cards:
        counts[card["lens"]] += 1
    return {
        "posture": posture,
        "rows": [dict((f, r[f]) for f in ROW_FIELDS) for r in rows],
        "lens_counts": counts,
        "lens_shortfalls": [{"lens": lens, "count": counts[lens]}
                            for lens in LENSES if counts[lens] < floor],
        "cards_in": len(cards),
        "rows_out": len(rows),
        "dropped_prior_keys": dropped,
    }


def validate_row(row, idx):
    """Raise InputError naming the row index and field when a rank input row is invalid."""
    def fail(field, why):
        raise InputError("row %d: field '%s' %s" % (idx, field, why))

    if not isinstance(row, dict):
        raise InputError("row %d: not a JSON object" % idx)
    if not isinstance(row.get("key"), str) or not row["key"].strip():
        fail("key", "must be a non-empty string")
    if row.get("altitude") not in ALTITUDES:
        fail("altitude", "must be one of %s" % ", ".join(ALTITUDES))
    if row.get("read_model") not in READ_MODELS:
        fail("read_model", "must be one of %s" % ", ".join(READ_MODELS))
    blockers = row.get("blockers") or []
    if not isinstance(blockers, list) or any(b not in BLOCKERS for b in blockers):
        fail("blockers", "must be a list of %s" % ", ".join(BLOCKERS))
    items = row.get("history_items") or []
    if not isinstance(items, list) or not all(isinstance(i, str) for i in items):
        fail("history_items", "must be a list of strings")
    ice = row.get("ice")
    if not isinstance(ice, dict):
        fail("ice", "must be an object {i, c, e}")
    for part in ("i", "c", "e"):
        value = ice.get(part)
        if not _is_int(value) or not 1 <= value <= 5:
            fail("ice.%s" % part, "must be an integer from 1 to 5")


def readiness(row):
    """Return the readiness tier for a scored row, first match wins."""
    blockers = row.get("blockers") or []
    if "client-decision" in blockers:
        return "needs-client-decision"
    if any(b in blockers for b in MEASUREMENT_BLOCKERS) or row["read_model"] == "unsized":
        return "needs-measurement"
    if "design-change" in blockers:
        return "needs-design-change"
    return "ready-now"


def rank(rows_data, write_ups, history_items=(), excluded_history=()):
    """Return the rank output object for scored rows.

    A bad row, or a row repeating an earlier row's key, raises InputError.
    """
    if isinstance(rows_data, dict) and "rows" in rows_data:
        rows_data = rows_data["rows"]
    if not isinstance(rows_data, list):
        raise InputError("rows input must be a JSON array or a consolidate object")
    seen = {}
    for idx, row in enumerate(rows_data):
        validate_row(row, idx)
        if row["key"] in seen:
            raise InputError("row %d: field 'key' repeats key '%s' from row %d"
                             % (idx, row["key"], seen[row["key"]]))
        seen[row["key"]] = idx
    ranked = []
    for altitude in ALTITUDES:
        alt_rows = [dict(r) for r in rows_data if r["altitude"] == altitude]
        for row in alt_rows:
            row["readiness"] = readiness(row)
            row["prelaunch_check"] = "verify-current-state" in (row.get("blockers") or [])
        alt_rows.sort(key=lambda r: (READINESS.index(r["readiness"]),
                                     -(r["ice"]["i"] + r["ice"]["c"] + r["ice"]["e"]),
                                     -r["ice"]["c"], r["key"]))
        for pos, row in enumerate(alt_rows, 1):
            row["rank"] = pos
            row["write_up"] = pos <= write_ups
        ranked.extend(alt_rows)
    ledger = {}
    unaccounted = []
    excluded = set(excluded_history)
    for item in history_items:
        carrier = next((r["key"] for r in ranked if item in (r.get("history_items") or [])), None)
        if carrier is not None:
            ledger[item] = carrier
        elif item in excluded:
            ledger[item] = "excluded"
        else:
            unaccounted.append(item)
    return {"rows": ranked, "history_ledger": ledger, "history_unaccounted": unaccounted}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _write_ups(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer from 8 to 12")
    if not 8 <= value <= 12:
        raise argparse.ArgumentTypeError("must be an integer from 8 to 12")
    return value


def _date(text):
    if not _valid_date(text):
        raise argparse.ArgumentTypeError("must be a YYYY-MM-DD date")
    return text


def _floor(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    if value < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return value


def _id_list(text):
    return [part.strip() for part in (text or "").split(",") if part.strip()]


def _load_json(path, what):
    try:
        if path == "-":
            return json.load(sys.stdin)
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s file %s: %s" % (what, path, exc))
    except ValueError as exc:
        raise InputError("%s input is not valid JSON: %s" % (what, exc))


def build_parser():
    """Return the argparse parser for both subcommands."""
    default_posture = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "SKILL.md")
    parser = argparse.ArgumentParser(
        description="Consolidate, size and rank hypothesis-generator lens cards.")
    sub = parser.add_subparsers(dest="command")
    sub.required = True
    cons = sub.add_parser("consolidate", help="merge, size and key the pooled cards")
    cons.add_argument("--cards", required=True, help="card JSON array file, or - for stdin")
    cons.add_argument("--prior", action="append", default=[], help="prior roadmap, one per altitude")
    cons.add_argument("--boundary", type=_date, help="measurement-regime boundary date")
    cons.add_argument("--posture", default=default_posture, help="file holding the Decision Posture")
    cons.add_argument("--floor", type=_floor, default=10, help="per-lens card floor (default 10)")
    rnk = sub.add_parser("rank", help="tier, order and select write-ups from scored rows")
    rnk.add_argument("--rows", required=True, help="scored row JSON file, or - for stdin")
    rnk.add_argument("--write-ups", required=True, type=_write_ups, help="write-ups per roadmap, 8 to 12")
    rnk.add_argument("--history-items", default="", help="comma-separated ledger ids")
    rnk.add_argument("--excluded-history", default="", help="comma-separated ids in Exclusions")
    return parser


def main(argv=None):
    """Run the CLI and return the exit code (0, 1 or 3; argparse exits 2 itself)."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "consolidate":
            cards = _load_json(args.cards, "cards")
            validate_cards(cards)
            priors = {}
            for path in args.prior:
                try:
                    with open(path, encoding="utf-8") as handle:
                        text = handle.read()
                except OSError as exc:
                    raise InputError("cannot read prior %s: %s" % (path, exc))
                altitude, entries = parse_prior(text, path)
                if altitude in priors:
                    raise InputError("prior %s: a second %s prior roadmap" % (path, altitude))
                priors[altitude] = entries
            posture = read_posture(args.posture)
            result = consolidate(cards, posture, priors, args.boundary, args.floor)
        else:
            rows = _load_json(args.rows, "rows")
            result = rank(rows, args.write_ups, _id_list(args.history_items),
                          _id_list(args.excluded_history))
    except InputError as exc:
        sys.stderr.write("consolidate_backlog: %s\n" % exc)
        return 1
    except PostureError as exc:
        sys.stderr.write("consolidate_backlog: posture unreadable: %s\n" % exc)
        return 3
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
