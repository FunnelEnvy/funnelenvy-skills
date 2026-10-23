#!/usr/bin/env python3
"""
history_backlog - deterministic projection of a bound experiment history for the
hypothesis-generator skill.

Reads a `schema: experiment-history` file (an Experiment Log of per-experiment
entries plus its pattern, baseline, mechanism and coverage-gap sections) and zero or
more per-experiment insight records, and prints a compact markdown projection that
the skill reads INSTEAD of the raw files:

  - meta: schema version, stated and parsed experiment counts, outcome tallies as
    written and as mapped, the UNVERIFIED-qualifier count
  - the line ranges of the Cross-Experiment Patterns, Baseline Anchors, Discovered
    Mechanisms and Coverage Gaps sections, for a bounded follow-up read
  - one index line per record: heading, page, treatment category, outcome and its
    mapping, the primary metric's lift / p / n, delivered sample per day (Sample
    Size over Duration days), deployed-state cues (full-scale markers, "until
    <date>" end dates, still-live markers, "replaced by"), and the record's line
    range for a second-stage full-entry read
  - the last two Learning sentences (<= 300 chars) for each settled record, plus any
    explicit Next Steps field
  - every typed `next_experiments` item from the insight records, numbered I1..In,
    with type, priority, surfaces, hypothesis, description, if_true, if_false, the
    parent record's page and mapping, and the record's blockers
  - the coverage-ledger seed: lead/high items (must be accounted for), items whose
    priority is unstated or unrecognized (fail safe: also must be accounted for), and
    medium/low items (shown as considered)

Why a script: the raw read is several times the skill's token budget, and the
coverage ledger needs a reproducible list of typed items. Stdlib only.

Usage:
    python3 history_backlog.py --history <experiment-history.md> [--insights <insight.md> ...]

Exit codes:
    0  projection printed on stdout
    1  history parse error: message on stderr, nothing on stdout. The skill falls back
       to a bounded read and notes the fallback in its completion message. An insight
       record that cannot be read or parsed does NOT fail the run: it is skipped, named
       on stderr, and reported in the projection as partial coverage.
    2  usage error (argparse)
    3  the --history file does not declare `schema: experiment-history` in its
       frontmatter. The skill treats the history as unbound.

Field scoping: a field value belongs to the entry whose heading precedes it and never
leaks into the next entry. Unknown fields are ignored. Only `- **Name:** value`
bullets at column 0 are fields. A field's value is its inline text joined with its
indented child bullets; a wrapped continuation line (indented, or at column 0 directly
under the field) is appended to it. A stated experiment_count that differs from the
parsed count prints a WARNING line.

Outcome mapping (mirrors SKILL.md > Read-side Mapping > Outcome mapping):
    win / loss, stated primary p <= 0.05, no UNVERIFIED qualifier  -> winner / loser
    win / loss, stated primary p above 0.05 and below 0.20         -> directional_win / directional_loss
    directional-win / directional-loss label                       -> directional_win / directional_loss
    inconclusive, stated primary p < 0.20, positive / negative lift -> directional_win / directional_loss
    any settled outcome with the UNVERIFIED qualifier              -> flat
    win or loss with no stated p <= 0.05                           -> flat
    inconclusive (other)                                           -> flat
    monitoring                                                     -> not minted (deployed state only)
    in-progress                                                    -> not minted (occupied slot)
"Stated primary p" is the p on the `(primary)` metric line. Only when a record has no
primary line at all does the Outcome Source p count, and then only to confirm a win or
loss at p <= 0.05; it never drives a directional mapping.

Insight records: the fenced yaml blocks are read, in order, for experiment_id,
result_classification, design_type, blockers and next_experiments; for each key the
first block that carries it wins, at top level or nested under a root key. A supported
YAML subset covers block mappings and sequences, quoted scalars (including multi-line),
inline flow lists, and `>-` / `|` block scalars. A record with no yaml block or no
next_experiments key contributes no items and is not an error. A priority other than
recommended_lead, high, medium or low (unstated, P1, critical, a typo) is seeded with
the lead/high items, so it must be dispositioned.
"""
import argparse
import datetime
import os
import re
import sys

SETTLED = ("winner", "loser", "directional_win", "directional_loss", "flat")
LEAD_HIGH = ("recommended_lead", "high")

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
FIELD_RE = re.compile(r"^[-*]\s+\*\*(.+?):\*\*\s*(.*)$")
SUB_RE = re.compile(r"^\s+[-*]\s+(.*)$")
UNVERIFIED_RE = re.compile(r"\[\s*UNVERIFIED\b[^\]]*\]", re.I)
P_RE = re.compile(r"\bp\s*(<=|>=|=|<|>|≤|≥)\s*(\d*\.\d+|\d+)", re.I)
LIFT_RE = re.compile(r"\blift\s*([+\-−]?)\s*(\d+(?:\.\d+)?)\s*%", re.I)
COUNT_PAIR_RE = re.compile(r"\(\s*\d[\d,]*\s*/\s*(\d[\d,]*)\s*\)")
INT_RE = re.compile(r"\d[\d,]*")
DAYS_RE = re.compile(r"(\d[\d,]*)\s*days?\b", re.I)
DATE = r"\d{4}-\d{2}-\d{2}"
UNTIL_RE = re.compile(r"\buntil\s+(" + DATE + r")", re.I)
LIVE_SINCE_RE = re.compile(r"\blive since\s+(" + DATE + r")", re.I)
STILL_LIVE_RE = re.compile(r"\bstill live\b(?:[^)]*?as of\s+(" + DATE + r"))?", re.I)
REPLACED_RE = re.compile(r"\breplaced by\s+([^),;]+)", re.I)
FULL_SCALE_RE = re.compile(r"\bfull[\s-]*scal", re.I)
VERDICT_RE = re.compile(r"\b(NOT SIG|SIG|DIRECTIONAL)\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")

SECTION_KEYS = (
    ("Cross-Experiment Patterns", re.compile(r"cross[\s-]*experiment\s+patterns", re.I)),
    ("Baseline Anchors", re.compile(r"baseline\s+anchors", re.I)),
    ("Discovered Mechanisms", re.compile(r"discovered\s+mechanisms", re.I)),
    ("Coverage Gaps", re.compile(r"coverage\s+gaps", re.I)),
)

OUTCOME_TOKENS = (
    "directional-win", "directional-loss", "in-progress", "inconclusive",
    "monitoring", "win", "loss",
)


class ParseError(Exception):
    """A file could not be read as the contract expects. Maps to exit code 1."""


class NotHistory(Exception):
    """The --history file does not declare `schema: experiment-history`. Exit code 3."""


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def read_lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise ParseError("cannot read %s: %s" % (path, exc))


def to_int(text):
    if text is None:
        return None
    try:
        return int(text.replace(",", ""))
    except ValueError:
        return None


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def split_frontmatter(lines):
    """Return (frontmatter lines or None, index of the first body line)."""
    if not lines or lines[0].strip() != "---":
        return None, 0
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return lines[1:i], i + 1
    return None, 0


def top_level_scalars(fm_lines):
    out = {}
    for line in fm_lines:
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if m and m.group(2):
            value = m.group(2)
            if value[:1] not in "\"'":
                value = _strip_comment(value).strip()
            out[m.group(1)] = unquote(value)
    return out


def norm_field(name):
    name = re.sub(r"\(.*?\)", "", name)
    return re.sub(r"\s+", " ", name).strip().lower()


def p_value(text):
    """Return (op, value) for the first p statement in text, or None."""
    if not text:
        return None
    m = P_RE.search(text)
    if not m:
        return None
    op = {"≤": "<=", "≥": ">="}.get(m.group(1), m.group(1))
    try:
        return op, float(m.group(2))
    except ValueError:
        return None


def p_at_most(p, bound):
    if p is None:
        return False
    op, value = p
    if op in ("=", "<", "<="):
        return value <= bound
    return False


def p_below(p, bound):
    if p is None:
        return False
    op, value = p
    if op == "=":
        return value < bound
    if op in ("<", "<="):
        return value <= bound
    return False


def fmt_p(p):
    if p is None:
        return None
    op, value = p
    text = ("%.4f" % value).rstrip("0").rstrip(".") if value else "0"
    return "p%s%s" % (op, text)


def sentence_tail(text, limit=300):
    """Last two sentences, at most `limit` chars, end-weighted."""
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return ""
    sents = [s for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    tail = " ".join(sents[-2:])
    if len(tail) > limit:
        tail = sents[-1]
    if len(tail) > limit:
        tail = tail[: limit - 3].rstrip() + "..."
    return tail


def clip(text, limit):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) > limit:
        return text[: limit - 3].rstrip() + "..."
    return text


# ---------------------------------------------------------------------------
# History file
# ---------------------------------------------------------------------------

def scan_headings(lines, start):
    """Headings outside fenced code blocks: list of (index, level, text)."""
    heads = []
    in_fence = False
    for i in range(start, len(lines)):
        line = lines[i]
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    return heads


def find_sections(lines, heads):
    """Line ranges (0-based, inclusive) of the four named sections."""
    starts = {}
    for idx, (i, level, text) in enumerate(heads):
        if level not in (2, 3):
            continue
        for label, rx in SECTION_KEYS:
            if label not in starts and rx.search(text):
                starts[label] = idx
                break
    section_lines = set(heads[idx][0] for idx in starts.values())
    ranges = {}
    for label, idx in starts.items():
        i, level, _ = heads[idx]
        end = len(lines) - 1
        for j in range(idx + 1, len(heads)):
            hj, lj, _ = heads[j]
            if lj <= level or hj in section_lines:
                end = hj - 1
                break
        while end > i and not lines[end].strip():
            end -= 1
        ranges[label] = (i, end)
    return ranges


def parse_fields(lines, first, last):
    """Fields of one entry: {normalized name: {"value", "children", "line"}}."""
    fields = {}
    cur = None
    in_fence = False
    prev_blank = False
    for i in range(first, last + 1):
        text = lines[i]
        if FENCE_RE.match(text):
            in_fence = not in_fence
            cur = None
            continue
        if in_fence:
            continue
        if not text.strip():
            prev_blank = True
            continue
        after_blank, prev_blank = prev_blank, False
        if HEADING_RE.match(text):
            cur = None
            continue
        m = FIELD_RE.match(text)
        if m:
            key = norm_field(m.group(1))
            cur = {"value": m.group(2).strip(), "children": [], "line": i}
            fields.setdefault(key, cur)
            continue
        sub = SUB_RE.match(text)
        if sub and cur is not None:
            cur["children"].append(sub.group(1).strip())
            continue
        # A wrapped continuation: an indented line, or a column-0 line directly under the field
        # (no blank line between; after a blank line a column-0 paragraph is new text).
        if cur is not None and not text.lstrip().startswith(("-", "*")) and \
                (text[0].isspace() or not after_blank):
            if cur["children"]:
                cur["children"][-1] += " " + text.strip()
            else:
                cur["value"] = (cur["value"] + " " + text.strip()).strip()
            continue
        cur = None
    return fields


def field_text(entry):
    """A field's inline text joined with its indented child bullets."""
    parts = [entry["value"]] if entry["value"] else []
    parts += entry["children"]
    return "; ".join(p for p in parts if p) or None


def field(fields, *names):
    for name in names:
        if name in fields:
            return field_text(fields[name])
    return None


def parse_primary(fields):
    """The `(primary)` metric line: lift, p, n, verdict. None when absent."""
    for entry in fields.values():
        for text in [entry["value"]] + entry["children"]:
            if "(primary)" not in text.lower():
                continue
            lift = None
            lm = LIFT_RE.search(text)
            if lm:
                lift = float(lm.group(2))
                if lm.group(1) in ("-", "−"):
                    lift = -lift
            pairs = [to_int(x) for x in COUNT_PAIR_RE.findall(text)]
            n = sum(x for x in pairs if x) if pairs else None
            vm = VERDICT_RE.search(text)
            return {
                "lift": lift,
                "p": p_value(text),
                "n": n or None,
                "verdict": vm.group(1) if vm else None,
            }
    return None


def outcome_token(raw):
    text = UNVERIFIED_RE.sub(" ", raw or "").strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    for token in OUTCOME_TOKENS:
        if text == token or text.startswith(token + "-") or text.startswith(token + "("):
            return token
    for token in OUTCOME_TOKENS:
        if re.search(r"(?<![a-z-])" + re.escape(token) + r"(?![a-z])", text):
            return token
    return text or "unknown"


def map_outcome(token, unverified, primary_p, lift, fallback_p=None):
    """Return (mapping, reason).

    `primary_p` is the p stated on the `(primary)` metric line. `fallback_p` is the
    Outcome Source p, passed only when the record has no primary line at all; it can
    confirm a win or loss at p <= 0.05 but never drives the directional rule.
    """
    if token == "monitoring":
        return "not_minted", "monitoring: no control group, feeds deployed state only"
    if token == "in-progress":
        return "not_minted", "in-progress: occupied slot"
    if token not in ("win", "loss", "directional-win", "directional-loss", "inconclusive"):
        return "not_minted", "outcome not recognized"
    if unverified:
        return "flat", "UNVERIFIED qualifier"
    if token in ("win", "loss"):
        strong, lean = ("winner", "directional_win") if token == "win" else ("loser", "directional_loss")
        if primary_p is not None:
            if p_at_most(primary_p, 0.05):
                return strong, None
            if p_below(primary_p, 0.20):
                return lean, "stated primary p above 0.05 and below 0.20"
            return "flat", "stated primary p at or above 0.20"
        if fallback_p is not None and p_at_most(fallback_p, 0.05):
            return strong, "p from the Outcome Source (no primary line)"
        return "flat", "no stated p <= 0.05"
    if token == "directional-win":
        return "directional_win", None
    if token == "directional-loss":
        return "directional_loss", None
    if p_below(primary_p, 0.20) and lift is not None and lift != 0:
        if lift > 0:
            return "directional_win", "primary p < 0.20, positive lift"
        return "directional_loss", "primary p < 0.20, negative lift"
    return "flat", None


def delivered(fields):
    total = None
    sample = field(fields, "sample size")
    if sample and not re.search(r"no data", sample, re.I):
        m = INT_RE.search(sample)
        total = to_int(m.group(0)) if m else None
    days = None
    duration = field(fields, "duration") or ""
    dm = DAYS_RE.search(duration)
    if dm:
        days = to_int(dm.group(1))
    if days is None:
        try:
            launch = datetime.date.fromisoformat((field(fields, "launch date") or "").strip()[:10])
            end = datetime.date.fromisoformat((field(fields, "end date") or "").strip()[:10])
            if end >= launch:
                days = (end - launch).days
        except ValueError:
            days = None
    per_day = round(total / days, 1) if total and days else None
    return total, days, per_day


def deployed_cues(fields):
    texts = [field(fields, "duration") or ""]
    for name, entry in fields.items():
        if any(k in name for k in ("deploy", "full-scale", "full scale", "shipped")):
            texts.append(field_text(entry) or "")
    blob = " ".join(texts)
    cues = []
    if FULL_SCALE_RE.search(blob):
        cues.append("full-scaled")
    m = UNTIL_RE.search(blob)
    if m:
        cues.append("until " + m.group(1))
    m = LIVE_SINCE_RE.search(blob)
    if m:
        cues.append("live since " + m.group(1))
    m = STILL_LIVE_RE.search(blob)
    if m:
        cues.append("still live" + (" as of " + m.group(1) if m.group(1) else ""))
    m = REPLACED_RE.search(blob)
    if m:
        cues.append("replaced by " + m.group(1).strip())
    status = (field(fields, "status") or "").strip().lower()
    if status and status != "completed":
        cues.append("status " + status)
    return cues


def parse_history(path):
    return parse_history_lines(read_lines(path), path)


def parse_history_lines(lines, path):
    fm_lines, body_start = split_frontmatter(lines)
    if fm_lines is None:
        raise NotHistory("%s has no frontmatter block" % path)
    meta = top_level_scalars(fm_lines)
    if meta.get("schema", "").strip().lower() != "experiment-history":
        raise NotHistory("%s does not declare schema: experiment-history" % path)

    heads = scan_headings(lines, body_start)
    sections = find_sections(lines, heads)
    section_spans = list(sections.values())
    section_heads = set(start for start, _ in section_spans)

    def inside_section(i):
        return any(start <= i <= end for start, end in section_spans)

    records = []
    for idx, (i, level, text) in enumerate(heads):
        if level < 2 or level > 4 or i in section_heads or inside_section(i):
            continue
        next_any = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines) - 1
        direct = parse_fields(lines, i + 1, next_any)
        if "outcome" not in direct and "status" not in direct:
            continue
        end = len(lines) - 1
        for j in range(idx + 1, len(heads)):
            if heads[j][1] <= level or heads[j][0] in section_heads:
                end = heads[j][0] - 1
                break
        while end > i and not lines[end].strip():
            end -= 1
        fields = parse_fields(lines, i + 1, end)
        records.append(build_record(text, i, end, fields))

    stated = to_int(meta.get("experiment_count"))
    if stated and not records:
        raise ParseError("%s states %d experiments but no entries parsed" % (path, stated))
    return {"path": path, "meta": meta, "stated": stated, "records": records,
            "sections": sections, "lines": len(lines)}


def build_record(heading, start, end, fields):
    raw_outcome = field(fields, "outcome") or ""
    unverified = bool(UNVERIFIED_RE.search(raw_outcome))
    token = outcome_token(raw_outcome) if raw_outcome else (
        outcome_token(field(fields, "status")) if field(fields, "status") else "unknown")
    primary = parse_primary(fields)
    primary_p = primary["p"] if primary else None
    fallback_p = None if primary else p_value(field(fields, "outcome source"))
    p = primary_p or fallback_p
    p_from = "primary" if primary_p else ("outcome source" if fallback_p else None)
    lift = primary["lift"] if primary else None
    mapping, reason = map_outcome(token, unverified, primary_p, lift, fallback_p)
    total, days, per_day = delivered(fields)
    return {
        "heading": heading,
        "start": start,
        "end": end,
        "page": field(fields, "page", "pages"),
        "category": field(fields, "treatment category"),
        "status": field(fields, "status"),
        "outcome": token,
        "unverified": unverified,
        "mapping": mapping,
        "reason": reason,
        "primary": primary,
        "p": p,
        "p_from": p_from,
        "total": total,
        "days": days,
        "per_day": per_day,
        "deployed": deployed_cues(fields),
        "learning": field(fields, "learning"),
        "next_steps": field(fields, "next steps", "next step"),
    }


# ---------------------------------------------------------------------------
# Insight records: a supported YAML subset
# ---------------------------------------------------------------------------

MAP_KEY_RE = re.compile(r"^([^\s:#\"'\[\]{}-][^:#]*?|\"[^\"]*\"|'[^']*'):(?:\s+(.*)|\s*)$")
BLOCK_INDICATORS = ("|", "|-", "|+", ">", ">-", ">+")


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def _blank(line):
    s = line.strip()
    return not s or s.startswith("#")


def _skip(lines, pos):
    while pos < len(lines) and _blank(lines[pos]):
        pos += 1
    return pos


def _strip_comment(text):
    m = re.search(r"\s+#", text)
    return text[: m.start()] if m else text


def _decode_double(body):
    out = []
    i = 0
    escapes = {"n": "\n", "t": "\t", "\"": "\"", "\\": "\\", "/": "/", "r": "\r", "0": "\0"}
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            if nxt in escapes:
                out.append(escapes[nxt])
                i += 2
                continue
            if nxt == "u" and i + 6 <= len(body):
                try:
                    out.append(chr(int(body[i + 2:i + 6], 16)))
                    i += 6
                    continue
                except ValueError:
                    pass
        out.append(c)
        i += 1
    return "".join(out)


def _close_quote(text, quote):
    """Index of the closing quote in text (text excludes the opening quote), or -1."""
    i = 0
    while i < len(text):
        c = text[i]
        if quote == "\"" and c == "\\":
            i += 2
            continue
        if c == quote:
            if quote == "'" and i + 1 < len(text) and text[i + 1] == "'":
                i += 2
                continue
            return i
        i += 1
    return -1


def _parse_quoted(rest, lines, pos, where):
    quote = rest[0]
    buf = rest[1:]
    while True:
        k = _close_quote(buf, quote)
        if k >= 0:
            tail = buf[k + 1:].strip()
            if tail and not tail.startswith("#"):
                raise ParseError("%s: unexpected text after a quoted value" % where)
            body = buf[:k]
            break
        if pos >= len(lines):
            raise ParseError("%s: unterminated quoted value" % where)
        buf = buf.rstrip() + " " + lines[pos].strip()
        pos += 1
    body = re.sub(r"\s*\n\s*", " ", body)
    value = _decode_double(body) if quote == "\"" else body.replace("''", "'")
    return value, pos


def _split_flow(text):
    items, buf, depth, quote = [], "", 0, None
    i = 0
    while i < len(text):
        c = text[i]
        if quote:
            buf += c
            if c == "\\" and quote == "\"" and i + 1 < len(text):
                buf += text[i + 1]
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            buf += c
        elif c in "[{":
            depth += 1
            buf += c
        elif c in "]}":
            depth -= 1
            buf += c
        elif c == "," and depth == 0:
            items.append(buf.strip())
            buf = ""
        else:
            buf += c
        i += 1
    if buf.strip():
        items.append(buf.strip())
    return items


def _flow_scalar(item):
    item = item.strip()
    if len(item) >= 2 and item[0] == "\"" and item[-1] == "\"":
        return _decode_double(item[1:-1])
    if len(item) >= 2 and item[0] == "'" and item[-1] == "'":
        return item[1:-1].replace("''", "'")
    if item in ("", "~", "null", "Null", "NULL"):
        return None
    return item


def _parse_flow(rest, lines, pos, where):
    open_c = rest[0]
    close_c = "]" if open_c == "[" else "}"
    buf = rest
    while True:
        depth, quote, end = 0, None, -1
        i = 0
        while i < len(buf):
            c = buf[i]
            if quote:
                if c == "\\" and quote == "\"":
                    i += 2
                    continue
                if c == quote:
                    quote = None
            elif c in "\"'":
                quote = c
            elif c in "[{":
                depth += 1
            elif c in "]}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        if end >= 0:
            break
        if pos >= len(lines):
            raise ParseError("%s: unterminated flow collection" % where)
        buf = buf + " " + lines[pos].strip()
        pos += 1
    tail = buf[end + 1:].strip()
    if tail and not tail.startswith("#"):
        raise ParseError("%s: unexpected text after a flow collection" % where)
    inner = buf[1:end]
    if open_c == "[":
        return [_flow_scalar(x) for x in _split_flow(inner)], pos
    out = {}
    for pair in _split_flow(inner):
        if ":" not in pair:
            raise ParseError("%s: flow mapping entry without a colon" % where)
        k, v = pair.split(":", 1)
        out[_flow_scalar(k)] = _flow_scalar(v)
    return out, pos


def _parse_block_scalar(indicator, lines, pos, parent_indent):
    body = []
    while pos < len(lines) and (not lines[pos].strip() or _indent(lines[pos]) > parent_indent):
        body.append(lines[pos])
        pos += 1
    content = [b for b in body if b.strip()]
    if not content:
        return "", pos
    base = min(_indent(b) for b in content)
    stripped = [b[base:] if b.strip() else "" for b in body]
    if indicator.startswith("|"):
        return "\n".join(stripped).rstrip("\n"), pos
    paras, cur = [], []
    for s in stripped:
        if s.strip():
            cur.append(s.strip())
        else:
            if cur:
                paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n".join(paras).strip(), pos


def _parse_scalar(rest, lines, pos, indent, where):
    rest = rest.strip()
    if rest in BLOCK_INDICATORS:
        return _parse_block_scalar(rest, lines, pos, indent)
    if rest[:1] in "\"'":
        return _parse_quoted(rest, lines, pos, where)
    if rest[:1] in "[{":
        return _parse_flow(rest, lines, pos, where)
    value = _strip_comment(rest).strip()
    while pos < len(lines) and not _blank(lines[pos]) and _indent(lines[pos]) > indent \
            and not lines[pos].strip().startswith("- ") and not MAP_KEY_RE.match(lines[pos].strip()):
        value += " " + _strip_comment(lines[pos].strip()).strip()
        pos += 1
    return _flow_scalar(value), pos


def _parse_node(lines, pos, min_indent, where):
    pos = _skip(lines, pos)
    if pos >= len(lines) or _indent(lines[pos]) < min_indent:
        return None, pos
    indent = _indent(lines[pos])
    text = lines[pos].strip()
    if text == "-" or text.startswith("- "):
        return _parse_seq(lines, pos, indent, where)
    if MAP_KEY_RE.match(text):
        return _parse_map(lines, pos, indent, where)
    return _parse_scalar(text, lines, pos + 1, indent - 1, where)


def _parse_seq(lines, pos, indent, where):
    items = []
    while True:
        pos = _skip(lines, pos)
        if pos >= len(lines) or _indent(lines[pos]) != indent:
            break
        text = lines[pos].strip()
        if not (text == "-" or text.startswith("- ")):
            break
        rest = text[1:].lstrip()
        if not rest:
            value, pos = _parse_node(lines, pos + 1, indent + 1, where)
        elif MAP_KEY_RE.match(rest):
            col = len(lines[pos]) - len(lines[pos].lstrip(" ")) + (len(text) - len(rest))
            lines[pos] = " " * col + rest
            value, pos = _parse_map(lines, pos, col, where)
        else:
            value, pos = _parse_scalar(rest, lines, pos + 1, indent, where)
        items.append(value)
    return items, pos


def _parse_map(lines, pos, indent, where):
    out = {}
    while True:
        pos = _skip(lines, pos)
        if pos >= len(lines):
            break
        ind = _indent(lines[pos])
        if ind < indent:
            break
        if ind > indent:
            raise ParseError("%s: unexpected indentation at block line %d" % (where, pos + 1))
        text = lines[pos].strip()
        if text.startswith("- ") or text == "-":
            break
        m = MAP_KEY_RE.match(text)
        if not m:
            raise ParseError("%s: cannot read block line %d" % (where, pos + 1))
        key = unquote(m.group(1).strip())
        rest = (m.group(2) or "").strip()
        pos += 1
        if not rest or rest.startswith("#"):
            nxt = _skip(lines, pos)
            if nxt < len(lines) and _indent(lines[nxt]) == indent and \
                    (lines[nxt].strip() == "-" or lines[nxt].strip().startswith("- ")):
                value, pos = _parse_seq(lines, nxt, indent, where)
            else:
                value, pos = _parse_node(lines, pos, indent + 1, where)
        else:
            value, pos = _parse_scalar(rest, lines, pos, indent, where)
        out[key] = value
    return out, pos


def yaml_blocks(lines, where):
    """Every fenced yaml block, in file order. An unclosed yaml fence is a parse error."""
    blocks, start = [], None
    for i, line in enumerate(lines):
        if start is None:
            if re.match(r"^\s*```\s*ya?ml\s*$", line, re.I):
                start = i + 1
        elif re.match(r"^\s*```\s*$", line):
            blocks.append(lines[start:i])
            start = None
    if start is not None:
        raise ParseError("%s: yaml block opened at line %d is never closed" % (where, start))
    return blocks


def key_block(block, key):
    """Lines of one key and its nested lines, dedented to column 0, or None.

    A top-level key wins; otherwise the first nested occurrence (the key under a root
    mapping) is used.
    """
    for nested in (False, True):
        for i, line in enumerate(block):
            m = re.match(r"^( *)" + re.escape(key) + r":(\s|$)", line)
            if not m or (len(m.group(1)) > 0) != nested:
                continue
            base = len(m.group(1))
            j = i + 1
            while j < len(block):
                s = block[j]
                if s.strip() and not s.lstrip().startswith("#"):
                    ind = _indent(s)
                    if ind < base or (ind == base and not (s.strip() == "-" or s.strip().startswith("- "))):
                        break
                j += 1
            return [ln[base:] if ln.strip() else "" for ln in block[i:j]]
    return None


INSIGHT_KEYS = ("experiment_id", "result_classification", "design_type", "blockers",
                "next_experiments")


def parse_insight(path):
    return parse_insight_lines(read_lines(path), path)


def parse_insight_lines(lines, path):
    fm_lines, _ = split_frontmatter(lines)
    fm = top_level_scalars(fm_lines) if fm_lines else {}
    where = os.path.basename(os.path.dirname(path)) or path
    blocks = yaml_blocks(lines, where)
    rec = {"path": path, "experiment_id": fm.get("experiment_id"), "classification": None,
           "design_type": None, "blockers": [], "items": None, "note": None, "error": None}
    if not blocks:
        rec["note"] = "no yaml block"
        return rec
    values = {}
    for key in INSIGHT_KEYS:
        for block in blocks:
            sub = key_block(block, key)
            if sub is None:
                continue
            parsed, _ = _parse_map(sub, 0, 0, "%s %s" % (where, key))
            values[key] = parsed.get(key)
            break
    if values.get("experiment_id"):
        rec["experiment_id"] = str(values["experiment_id"])
    rec["classification"] = values.get("result_classification")
    rec["design_type"] = values.get("design_type")
    blockers = values.get("blockers") or []
    if isinstance(blockers, list):
        for b in blockers:
            if isinstance(b, dict) and b.get("description"):
                rec["blockers"].append(str(b["description"]))
            elif isinstance(b, str):
                rec["blockers"].append(b)
    if "next_experiments" not in values:
        rec["note"] = "no next_experiments"
        return rec
    raw_items = values["next_experiments"] or []
    if not isinstance(raw_items, list):
        raise ParseError("%s: next_experiments is not a list" % where)
    items = []
    for n, item in enumerate(raw_items, 1):
        if not isinstance(item, dict):
            raise ParseError("%s: next_experiments item %d is not a mapping" % (where, n))
        surfaces = item.get("surfaces")
        if isinstance(surfaces, str):
            surfaces = [surfaces]
        items.append({
            "type": str(item.get("type") or "unstated"),
            "priority": norm_priority(item.get("priority")),
            "surfaces": [str(s) for s in (surfaces or []) if s],
            "hypothesis": item.get("hypothesis"),
            "description": item.get("description"),
            "if_true": item.get("if_true"),
            "if_false": item.get("if_false"),
        })
    rec["items"] = items
    return rec


KNOWN_OTHER = ("medium", "low")


def norm_priority(value):
    text = re.sub(r"[\s-]+", "_", str(value or "").strip().lower())
    if text in ("recommended_lead", "lead", "recommended"):
        return "recommended_lead"
    return text or "unstated"


def ledger_class(priority):
    """lead (must be dispositioned), unrecognized (fail safe: also must be), or other."""
    if priority in LEAD_HIGH:
        return "lead"
    if priority in KNOWN_OTHER:
        return "other"
    return "unrecognized"


# ---------------------------------------------------------------------------
# Projection
# ---------------------------------------------------------------------------

def match_parent(records, experiment_id):
    if not experiment_id:
        return None
    rx = re.compile(r"(?<![A-Za-z0-9])" + re.escape(experiment_id) + r"(?![A-Za-z0-9])", re.I)
    for rec in records:
        if rx.search(rec["heading"]):
            return rec
    return None


def record_line(rec):
    outcome = rec["outcome"] + (" [UNVERIFIED]" if rec["unverified"] else "")
    mapping = rec["mapping"] if rec["mapping"] != "not_minted" else "not minted"
    if rec["reason"] and rec["mapping"] != "not_minted" and not rec["unverified"]:
        mapping += " (%s)" % rec["reason"]
    prim = rec["primary"]
    if prim:
        parts = []
        if prim["lift"] is not None:
            parts.append("%+.1f%%" % prim["lift"])
        if prim["p"]:
            parts.append(fmt_p(prim["p"]))
        if prim["n"]:
            parts.append("n=%d" % prim["n"])
        read = "primary " + (" ".join(parts) if parts else "line without figures")
    elif rec["p"]:
        read = "%s (outcome source)" % fmt_p(rec["p"])
    else:
        read = "no primary"
    if rec["total"] and rec["days"]:
        sample = "%s/day (%d in %dd)" % (rec["per_day"], rec["total"], rec["days"])
    elif rec["total"]:
        sample = "%d, days n/a" % rec["total"]
    else:
        sample = "sample n/a"
    cues = "; ".join(rec["deployed"]) if rec["deployed"] else "no cue"
    return "- %s | %s | %s | %s -> %s | %s | %s | %s | L%d-%d" % (
        rec["heading"], rec["page"] or "page n/a", rec["category"] or "-",
        outcome, mapping, read, sample, cues, rec["start"] + 1, rec["end"] + 1)


def build_projection(history, insights):
    recs = history["records"]
    out = ["# Experiment history projection", ""]
    out.append("Built by `scripts/history_backlog.py` from `%s`. Read this instead of the raw "
               "files. Second-stage reads use the line ranges below (cap: 20 full entries)."
               % history["path"])
    out += ["", "## Meta", ""]
    meta = history["meta"]
    out.append("- Schema version: %s" % (meta.get("schema_version") or "not stated"))
    out.append("- Experiments: %s stated, %d parsed" % (
        history["stated"] if history["stated"] is not None else "not", len(recs)))
    if history["stated"] is not None and history["stated"] != len(recs):
        out.append("- WARNING: experiment_count states %d but %d entries parsed. Read the "
                   "Experiment Log headings directly to find the unparsed entries; coverage is "
                   "partial until they are read." % (history["stated"], len(recs)))
    written = {}
    for r in recs:
        key = r["outcome"] + (" [UNVERIFIED]" if r["unverified"] else "")
        written[key] = written.get(key, 0) + 1
    out.append("- Outcomes as written: " + ", ".join(
        "%s %d" % (k, v) for k, v in sorted(written.items(), key=lambda kv: (-kv[1], kv[0]))))
    mapped = {}
    for r in recs:
        key = r["mapping"] if r["mapping"] != "not_minted" else "not minted (" + r["outcome"] + ")"
        mapped[key] = mapped.get(key, 0) + 1
    order = list(SETTLED)
    out.append("- Mapped: " + ", ".join(
        "%s %d" % (k, mapped[k]) for k in sorted(
            mapped, key=lambda k: (order.index(k) if k in order else len(order), k))))
    out.append("- UNVERIFIED qualifier: %d records (never mapped above flat)"
               % sum(1 for r in recs if r["unverified"]))
    all_items = []
    for ins in insights:
        for item in ins["items"] or []:
            all_items.append((ins, item))
    lead = [x for x in all_items if ledger_class(x[1]["priority"]) == "lead"]
    unknown = [x for x in all_items if ledger_class(x[1]["priority"]) == "unrecognized"]
    other = [x for x in all_items if ledger_class(x[1]["priority"]) == "other"]
    failed = [ins for ins in insights if ins.get("error")]
    out.append("- Insight records: %d supplied (%d failed to parse), %d typed items "
               "(%d lead/high, %d priority unrecognized, %d medium/low)"
               % (len(insights), len(failed), len(all_items), len(lead), len(unknown), len(other)))
    if failed:
        out.append("- COVERAGE PARTIAL: %d insight record(s) could not be parsed; read each "
                   "one's next_experiments block directly: %s" % (
                       len(failed), "; ".join("%s (%s)" % (f["path"], f["error"]) for f in failed)))
    with_next = sum(1 for r in recs if r["next_steps"])
    out.append("- Records with an explicit Next Steps field: %d" % with_next)

    out += ["", "## Sections", ""]
    for label, _ in SECTION_KEYS:
        span = history["sections"].get(label)
        if span:
            out.append("- %s: lines %d-%d" % (label, span[0] + 1, span[1] + 1))
        else:
            out.append("- %s: not present" % label)

    out += ["", "## Record index", "",
            "One line per record: heading | page | treatment category | outcome -> mapping | "
            "primary read | delivered sample | deployed-state cues | line range.", ""]
    for r in recs:
        out.append(record_line(r))
        if r["mapping"] in SETTLED and r["learning"]:
            out.append("  - Learning: " + sentence_tail(r["learning"]))
        if r["next_steps"]:
            out.append("  - Next steps: " + clip(r["next_steps"], 400))

    out += ["", "## Typed insight items", ""]
    if not insights:
        out.append("No insight records supplied.")
    counter = 0
    ids = {}
    for ins in insights:
        if ins.get("error"):
            out.append("### %s (could not be parsed: %s; read its next_experiments block "
                       "directly, coverage is partial)" % (ins["path"], ins["error"]))
            out.append("")
            continue
        parent = match_parent(recs, ins["experiment_id"])
        head = "### %s (experiment %s" % (ins["path"], ins["experiment_id"] or "not stated")
        if parent:
            head += "; parent: %s; page %s; parent mapping %s" % (
                parent["heading"], parent["page"] or "n/a",
                parent["mapping"] if parent["mapping"] != "not_minted" else "not minted")
        else:
            head += "; parent record not found in the history"
        out.append(head + ")")
        if ins["classification"] or ins["design_type"]:
            out.append("- Classification: %s | design: %s" % (
                ins["classification"] or "n/a", ins["design_type"] or "n/a"))
        if ins["blockers"]:
            out.append("- Blockers: " + " ".join(
                "(%d) %s" % (k, clip(b, 220)) for k, b in enumerate(ins["blockers"], 1)))
        if ins["note"]:
            out.append("- %s: contributes no typed items" % ins["note"].capitalize())
        for item in ins["items"] or []:
            counter += 1
            ids[id(item)] = "I%d" % counter
            out.append("- I%d [%s] %s | surfaces: %s" % (
                counter, item["priority"], item["type"],
                "; ".join(item["surfaces"]) if item["surfaces"] else "none stated"))
            for label, key in (("Hypothesis", "hypothesis"), ("Description", "description"),
                               ("If true", "if_true"), ("If false", "if_false")):
                if item[key]:
                    out.append("  - %s: %s" % (label, clip(str(item[key]), 600)))
        out.append("")

    out += ["## Coverage ledger seed", ""]
    if lead:
        out.append("- Lead/high items the roadmap must account for (adopted, merged, folded, "
                   "strategic, or not advanced with grounds): " +
                   ", ".join("%s [%s]" % (ids[id(i)], i["priority"]) for _, i in lead) +
                   " (%d)" % len(lead))
    else:
        out.append("- Lead/high items: none")
    if unknown:
        out.append("- Priority unrecognized, treated as lead/high until dispositioned: " +
                   ", ".join("%s [%s]" % (ids[id(i)], i["priority"]) for _, i in unknown) +
                   " (%d)" % len(unknown))
    if other:
        out.append("- Medium/low items, shown as considered: " +
                   ", ".join("%s [%s]" % (ids[id(i)], i["priority"]) for _, i in other) +
                   " (%d)" % len(other))
    else:
        out.append("- Medium/low items: none")
    if failed:
        out.append("- Coverage partial: %d insight record(s) failed to parse and are not seeded "
                   "here (listed in Meta)." % len(failed))
    text = "\n".join(out)
    est = (len(text) + 60) // 4
    out += ["", "---", "Projection: %d lines, ~%d tokens (chars/4)." % (len(out) + 3, est)]
    return "\n".join(out) + "\n"


def project(history_path, history_lines, insights):
    """Build the projection from already-read lines.

    `insights` is a list of (path, content) pairs processed in path order, where content is
    the file's lines, or an error message when the file could not be read. A history parse
    error fails the run (exit 1); an insight-record error is isolated to that record, which is
    reported in the projection as a partial-coverage warning.
    Returns (exit_code, stdout_text, stderr_text) per the module exit-code contract.
    """
    try:
        history = parse_history_lines(history_lines, history_path)
    except NotHistory as exc:
        return 3, "", "history_backlog: %s\n" % exc
    except ParseError as exc:
        return 1, "", "history_backlog: parse error: %s\n" % exc
    parsed, warnings = [], []
    for path, content in sorted(insights, key=lambda pair: pair[0]):
        try:
            if isinstance(content, str):
                raise ParseError(content)
            parsed.append(parse_insight_lines(content, path))
        except ParseError as exc:
            parsed.append({"path": path, "experiment_id": None, "classification": None,
                           "design_type": None, "blockers": [], "items": None, "note": None,
                           "error": str(exc)})
            warnings.append("history_backlog: insight record skipped: %s\n" % exc)
    return 0, build_projection(history, parsed), "".join(warnings)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Project an experiment history for hypothesis-generator.")
    ap.add_argument("--history", required=True, help="schema: experiment-history file")
    ap.add_argument("--insights", nargs="*", default=[], help="per-experiment insight records")
    args = ap.parse_args(argv)
    try:
        history_lines = read_lines(args.history)
    except ParseError as exc:
        sys.stderr.write("history_backlog: parse error: %s\n" % exc)
        return 1
    insights = []
    for path in sorted(set(args.insights)):
        try:
            insights.append((path, read_lines(path)))
        except ParseError as exc:
            insights.append((path, str(exc)))
    code, out, err = project(args.history, history_lines, insights)
    if err:
        sys.stderr.write(err)
    if out:
        sys.stdout.write(out)
    return code


if __name__ == "__main__":
    sys.exit(main())
