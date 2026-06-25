# Cross-altitude edge contract

The contract that binds the strategic layer (bets) to the tactical layer (page
tests) and lets `render_site.py` validate the two inputs as a single program
before any HTML is written. The gate is mechanical and fails closed: any
violation halts the build with a non-zero exit and prints the offending records.

The strategic file is the only place edges are authored. The tactical file
authors no inbound or reverse references; every test's inbound edges are
**derived** by inverting the bet edges. Authoring only one end keeps the two
ends from drifting.

## Input schemas

Both inputs are markdown files: YAML frontmatter (the structured contract data)
plus a body whose per-item sections supply the prose the curation pass rewrites.

The frontmatter is authored in a **constrained block-YAML subset** that
`render_site.py`'s built-in parser supports: nested block mappings, block
sequences, single-line inline flow maps `{k: v, ...}` and flow sequences
`[a, b]`, quoted/plain scalars, ints, floats, and booleans. Multi-line flow is
not supported. Anything the parser cannot read raises, fail-loud.

### Strategic (program narrative + bets + edges)

```yaml
program:
  client: "..."            # rendered in nav + provenance + foot
  name: "..."              # program name
  program_version: "X.Y.Z" # MUST match the tactical file (gate check 7)
  date: "YYYY-MM-DD"        # provenance + foot date (authored, never Date.now)
  hero:
    eyebrow: "..."
    headline: "..."         # hub H1
    headline_num: "..."     # optional: a substring of headline to highlight
    subhead: "..."          # raw material for the hero-subhead prose slot
bets:
  - id: sb-01               # canonical id; anchor, filename, edge target key
    title: "..."
    lever: "..."            # short lever phrase
    decided_on: "..."       # optional: the metric the bet is decided on (card)
    run_tag: "..."          # optional badge: "Run first" | "Keystone" | "Long game"
    delivery_surface: [proof, copy]   # surfaces the bet can ship on
    executor_status: on-page          # on-page | off-page | unexpressed (gate 4)
    ice: {i: 5, c: 4, e: 2}           # 1-5 each; ICE total = i + c + e
    keystone: true|false
    edges:
      - {target: p-10, type: expresses}   # type in {expresses, informs, gates}
      - {target: p-03, type: informs}
```

Body: one `## SB-N. Title` section per bet, with bold-labeled paragraphs
(`**The lever.**`, `**The experiment / program.**`, `**What must be stood up.**`,
`**How this connects to the page-level roadmap.**`, ...). The generator maps
these to spoke prose slots; the curation pass rewrites them.

### Tactical (tests + mechanism + optional mockup)

```yaml
program_version: "X.Y.Z"   # MUST match the strategic file (gate check 7)
tests:
  - {id: p-01, title: "...", mechanism_class: copy, tier: quick-win,
     ice: {i: 3, c: 4, e: 4}, target_page: "Homepage", status: active}
  - {id: p-04, title: "...", mechanism_class: form, tier: strategic-bet,
     ice: {i: 4, c: 3, e: 3}, target_page: "Demo", status: superseded, superseded_by: "MI-2.1"}
  - {id: p-10, title: "...", mechanism_class: proof, tier: exploration,
     ice: {i: 3, c: 3, e: 3}, target_page: "...", status: active,
     mockup: {screenshot: "mockups/p-10/screenshot.png", html: "mockups/p-10/mockup.html",
              mode: "chrome-devtools", target_url: "...",
              insertion_point: "...", placement_summary: "..."}}
```

- `tier` in `{quick-win, strategic-bet, exploration}` (drives backlog grouping + badge).
- `status: superseded` drops the test from the map and spokes and dims its backlog card.
- `mockup` is optional; only tests that carry it render the tactical "Proposed change"
  section. Asset paths are resolved relative to the tactical file's directory and
  copied into `<site>/mockups/<id>/`. Maps one-to-one onto `/experiment-mockup` output.
- The tactical file MUST NOT author `edges`/`inbound`/`expressed_by`/`informed_by`/
  `gated_by` (gate check 6) -- reverse edges are derived.

## Build gate (7 checks, hard fail, non-zero exit)

1. Every `edge.type` is in `{expresses, informs, gates}`.
2. Every `edge.target` resolves to a live (non-superseded) test id.
3. Every `expresses` edge passes the mechanism gate: `test.mechanism_class in
   bet.delivery_surface`. On failure, prints bet id, test id, lever, mechanism,
   and delivery_surface.
4. `executor_status` matches the derived status:
   - `on-page` -> the bet has at least one `expresses` edge.
   - `off-page` -> no `expresses` edge AND every `delivery_surface` is off-page-only
     (off-page surfaces: `{routing}`).
   - `unexpressed` -> no `expresses` edge AND at least one on-page surface.
5. `intake_only` is derived, never authored (a test with zero inbound edges).
6. The tactical file authors no inbound / reverse references.
7. `program_version` matches across both inputs.

Acceptance probe: feeding `sb-01 expresses p-06` (a `routing` bet expressing a
`cta` test) must exit non-zero with a message naming the `routing` vs `cta`
mismatch.

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
