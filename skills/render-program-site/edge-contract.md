# Cross-altitude edge contract

The contract that binds the strategic layer (bets) to the tactical layer (page
tests) and lets `render_site.py` validate the inputs as a single program before
any HTML is written. The gate is mechanical and fails closed: any violation
halts the build with a non-zero exit and prints the offending records.

render-program-site consumes the **gold roadmap artifacts** hypothesis-generator
produces, in place. It derives every per-item field from the gold structure and
authors nothing into those artifacts. The one net-new input is a small
render-owned **sidecar** that carries the cross-altitude edge binding plus the
gate-classification fields the prose gold roadmaps cannot encode.

The sidecar's strategic (bet) entries are the only place edges are authored. The
sidecar's tactical (test) entries author no inbound or reverse references; every
test's inbound edges are **derived** by inverting the bet edges. Authoring only
one end keeps the two ends from drifting.

## Inputs

Three files, all markdown:

| Input | Role | Authored by |
|---|---|---|
| tactical gold roadmap | `gold-experiment-roadmap`, read in place | hypothesis-generator |
| strategic gold roadmap | `gold-strategic-roadmap`, read in place | hypothesis-generator |
| edge sidecar | the edge binding + classification + program/hero block | render-program-site (curation) |

### Derived from each gold roadmap body (never authored)

Both gold roadmaps share the same body shape: `### N. Title` experiment sections
nested under tier H2s (`## Quick Wins` / `## Strategic Bets` / `## Explorations`),
each carrying a `**Key:**` line, a `**Scores:**` line, and bold-labeled prose.
`render_site.py` derives:

- `id` — from the `### N.` section ordinal: strategic `### N.` -> `sb-NN`,
  tactical `### N.` -> `p-NN`. (The Key is the stable human-facing join key; the
  id is the deterministic positional handle used for anchors, filenames, and
  map nodes.)
- `key` — the `**Key:** <slug>` value. Stable and immutable across re-renders
  (hypothesis-generator's Key carry-forward rule). The sidecar binds by Key.
- `title` — the `### N. Title` heading text.
- `tier` — the enclosing tier H2 (`quick-win` / `strategic-bet` / `exploration`).
- `ice` — parsed from `**Scores:** Impact X | Confidence Y | Ease Z` (trailing
  rationale on the line is ignored).
- `target_page` — the tactical `**Page:**` label.
- prose slots — the bold-labeled paragraphs, mapped to spoke prose regions and
  rewritten by the curation pass.

The gold frontmatter `version` of each roadmap is read for the version lock
(gate check 7).

### Edge sidecar schema (`{scope}-program-edges.md`)

Frontmatter only (a body is optional documentation). Authored in the same
constrained block-YAML subset `render_site.py`'s parser supports (nested block
mappings, block sequences, single-line inline flow maps `{k: v}` and sequences
`[a, b]`, quoted/plain scalars, ints, floats, booleans; multi-line flow is not
supported; anything unparseable raises, fail-loud).

```yaml
program:
  client: "..."              # rendered in nav + provenance + foot
  name: "..."                # program name (hub title)
  date: "YYYY-MM-DD"          # provenance + foot date (authored, never Date.now)
  strategic_version: "X.Y.Z"  # MUST match the strategic gold roadmap's version (gate 7)
  tactical_version: "X.Y.Z"   # MUST match the tactical gold roadmap's version (gate 7)
  hero:
    eyebrow: "..."
    headline: "..."           # hub H1
    headline_num: "..."       # optional: a substring of headline to highlight
    subhead: "..."            # raw material for the hero-subhead prose slot
bets:                         # one per strategic gold bet, keyed by its **Key:**
  - key: speed-to-first-value
    delivery_surface: [routing]       # surfaces the bet can ship on
    executor_status: off-page         # on-page | off-page | unexpressed (gate 4)
    decided_on: "trial-to-paid"       # optional: the metric the bet is decided on (card)
    run_tag: "Run first"              # optional badge: "Run first" | "Keystone" | "Long game"
    keystone: false
    edges:
      - {target: conversational-signup-form, type: informs}   # target is a tactical Key
tests:                        # one per tactical gold test, keyed by its **Key:**
  - key: conversational-signup-form
    mechanism_class: form             # required (the gate-3 input)
  - key: old-form-test
    mechanism_class: form
    status: superseded                # OPTIONAL render-side program state (default active)
    superseded_by: "v2.1"
  - key: proof-block-on-pricing
    mechanism_class: proof
    mockup: {control_screenshot: "experiments/proof-block-on-pricing/control-screenshot.png", screenshot: "experiments/proof-block-on-pricing/mockup-screenshot.png", html: "experiments/proof-block-on-pricing/mockup.html", mode: "chrome-devtools", target_url: "...", insertion_point: "...", placement_summary: "..."}
```

The `mockup` value above is shown on one line: the sidecar parser supports only
single-line inline flow maps `{k: v, ...}`. Do not wrap it across lines.

- `edge.type` in `{expresses, informs, gates}`; `edge.target` is a tactical Key,
  resolved to a `p-NN` id by the generator.
- `mechanism_class` is required on every live test (the mechanism gate input).
- `status: superseded` drops the test from the map and spokes and dims its
  backlog card. It is render-side program state (a test that has since shipped or
  been replaced), authored here because the gold roadmaps carry no per-test
  supersede marker (hypothesis-generator supersedes whole roadmaps, not tests).
- `mockup` is optional; only tests that carry it render the tactical "Proposed
  change" section. Asset paths resolve relative to the sidecar's directory and
  are copied into `<site>/mockups/<id>/`. Maps one-to-one onto `/experiment-mockup`
  output, keyed by the same Key.
- `mockup.control_screenshot` is optional and maps one-to-one onto
  experiment-mockup's `control-screenshot.png` (the unmodified "before" state).
  When present, the spoke renders a labeled Before/After pair; when absent, the
  spoke renders the after screenshot alone (unchanged, backward compatible). It
  resolves relative to the sidecar directory like the other assets; a path that
  points at a missing file degrades to after-only (no error). A present-but-non-string
  `control_screenshot` is rejected by the binding checks.
- The sidecar's test entries MUST NOT author `edges`/`inbound`/`expressed_by`/
  `informed_by`/`gated_by`/`intake_only`/`intake` (gate checks 5 and 6) -- reverse
  edges and intake are derived.

## Build gate (hard fail, non-zero exit)

Run over the derived data:

1. Every `edge.type` is in `{expresses, informs, gates}`.
2. Every `edge.target` Key resolves to a live (non-superseded) test.
3. Every `expresses` edge passes the mechanism gate: `test.mechanism_class in
   bet.delivery_surface`. On failure, prints bet id, test id, lever, mechanism,
   and delivery_surface.
4. `executor_status` matches the derived status:
   - `on-page` -> the bet has at least one `expresses` edge.
   - `off-page` -> no `expresses` edge AND every `delivery_surface` is off-page-only
     (off-page surfaces: `{routing}`).
   - `unexpressed` -> no `expresses` edge AND at least one on-page surface.
5. `intake_only` is derived, never authored (a sidecar test authoring it is a
   violation).
6. The sidecar's test entries author no inbound / reverse references.
7. The version lock holds: the sidecar's `strategic_version` / `tactical_version`
   match the live gold roadmaps' frontmatter `version` (catches edges authored
   against a since-revised roadmap).

Binding checks (alongside the seven): every strategic gold bet has a sidecar
entry; every sidecar Key resolves to a gold Key; every live test has a
`mechanism_class`. A malformed `mockup` (non-mapping) is rejected. A `mockup`
carrying a non-string `control_screenshot` is rejected.

Acceptance probe: feeding `sb-01 expresses p-06` where `sb-01` is a `routing` bet
and the target test's mechanism is `cta` must exit non-zero with a message naming
the `routing` vs `cta` mismatch.

## Derived data (computed, never authored)

- **Reverse edges** -- invert every bet edge into each test's inbound list, split
  by type (`expresses` / `informs` / `gates`).
- **`intake_only`** -- a live test with zero inbound edges; renders with the dashed
  hollow map marker and the "intake-only" backlog tag and ladders-up section.
- **Map coordinates** -- `x = lerp(E, plot_left, plot_right)`, `y = lerp(I,
  plot_bottom, plot_top)` on the 1-5 scales. Bets render as the large markers,
  tests as small, intake tests dashed-hollow. No coordinate is hand-placed. When
  several nodes share an (I, E) cell they are spread by a deterministic dodge (a
  small circle, ordered by id) so they do not overlap -- still a pure function of
  the data.
- **Edge line class** -- `expresses` -> `pf-link` (solid); `informs` and `gates`
  -> `pf-link-soft` (dashed). Chips follow the same split (`chip` vs `chip soft`).
- **Tier grouping** for the backlog, and **superseded** dimming.

## Type-label map (printed verbatim, never paraphrased)

| type | bet side | test side |
|------|----------|-----------|
| `expresses` | Expressed on-page by | Expresses |
| `informs` | Informs | Informed by |
| `gates` | Gates | Gated by |

## Account program (optional off-store altitude)

The account-program deliverable (`--account-program <path>`, a `gold-strategy-deliverable`
of the account-program shape) is a THIRD input, parsed standalone. It has **no sidecar
binding, no cross-altitude edge, and no place on the portfolio map**. Its plays carry no
`**Key:**`, no `**Scores:**`, no ICE, and no on-page mechanism: each is measured by an
account-level design (cohort reactivation, offline-conversion gap closure, account-level
reads, program delivery) rather than by splitting on-store traffic, so the plays cannot
enter any of the seven edge checks or receive map coordinates. The input is optional; a
missing file simply omits the altitude, and output is byte-identical to a two-altitude render.

### Parsed standalone (never authored)

- The plays block is sliced with `extract_named_section("The Account-Level Plays")` and the
  taxonomy with `extract_named_section("The Account-Cohort Taxonomy")` BEFORE parsing. Slicing
  first means the `## Cohort Rosters` block (whose children are `### <descriptive name>`
  headings, not `### N.` ordinals) is never reached; even unsliced it would be inert, because
  `extract_sections` keys strictly on the ordinal `### N.` form (validated against a live
  reference deliverable).
- Each play: `id` from the `### N.` ordinal -> `ap-NN`; `title` from the heading; `labels`
  from the bold-labeled paragraphs (`Cohort`, `The play`, `Rationale`, `How it is measured`,
  `Dependencies`, `Relationship to the roadmaps`). `tier` is `None` (no tier H2 in the slice);
  `key` is `None` (plays carry no `**Key:**`).
- Each cohort: parsed from the taxonomy markdown table (skip the header row and the `|---|`
  separator; strip `**` bold from the name) into `{name, size, behavior}`. Name + size are
  data-bound facts; the behavior flows through a prose slot.

### Account-binding checks (separate leg, runs only when an account program is present)

These append to the same violation list and fail closed (non-zero exit), but are wholly
separate from the seven edge checks (which never see account data):

1. At least one play exists under `The Account-Level Plays`.
2. Play ordinals are unique (a duplicate `### N.` is named; the `ap-NN` keying would otherwise
   silently collapse it).
3. Every play carries the required labels `Cohort`, `The play`, and `How it is measured`.

Message style matches the edge gate, e.g. `[account] play ap-02 ('...'): missing required
label 'How it is measured'`.

Synthetic example (non-client): a taxonomy table of two or three cohorts plus two `### N.`
plays each carrying the six labels, no `**Key:**`/`**Scores:**`, renders a `#account-program`
hub section (cohort cards + one play card per play) and one `ap-NN.html` spoke per play, each
linking back to `index.html#account-program`.
