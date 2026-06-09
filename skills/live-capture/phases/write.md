# Phase 3: Write (assembly + dual-mode output)

This file is the AUTHORITATIVE schema for `live-observation.md` and `live-copy.md`. The `schemas/` copies are human reference only; if they diverge, this file wins.

Read `agent-header.md` first. Facts + the two permitted mechanical derivations only.

## Authoritative schema: live-observation.md

The frontmatter `pages:` digest lets a consumer decide "does pattern X fire on page Y?" without loading the body.

```yaml
---
schema: live-observation
schema_version: "1.1"
company: str
url: str
capture_date: YYYY-MM-DD              # governs staleness + Wayback supersession
capture_method: chrome-devtools | playwright | static   # site-level dominant method
pages_captured: int
viewports: [desktop, mobile]
confidence: 1-5                       # coverage-weighted aggregate (see Confidence Model), NOT a min()
# --- site-level pattern fast-path (facts + mechanical derivations only) ---
form_recurs_sitewide: bool
sitewide_form_required_field_count: int | null
sitewide_primary_cta_label: str | null
comparison_page_exists: present | absent | not_checked   # CR-01
roi_tool_exists: present | absent | not_checked          # CR-02 / CR-03
pricing_page_exists: present | absent | not_checked       # PZ-01
nav_persona_segmented: bool           # DERIVED: nav labels match /for-|by-(role|use-case)/. Hint only.
# --- per-page firing digest (one entry per captured page) ---
pages:
  - path: str
    form_present: bool
    form_field_count: int | null               # FO-01/02 (perceived length)
    form_required_field_count: int | null       # FO-01/02 (actual friction)
    form_embed: marketo | hubspot | native | other | null
    primary_cta_label: str | null               # NX-02, EE-03
    cta_count: int                               # NX-02
    login_present: bool                          # NX-07
    login_above_fold: bool                       # NX-07
    login_nav_rank: int | null                   # NX-07 (ordinal in nav)
    named_client_proof_present: present | absent | not_checked   # HM-02, SP-* (tri-state: depends on below-fold lazy content)
    team_credibility_present: present | absent | not_checked     # TC-01 (tri-state: depends on below-fold lazy content)
    proof_element_count: int                     # SP-*
    sequential_ui_present: bool                  # EE-02
    sequential_ui_items: int                     # EE-02
    objection_faq_present: present | absent | not_checked   # TC-02
    chatbot_present: present | absent | not_checked          # NX-06 / overlay
    mobile_render_clean: bool                    # DERIVED: mobile console_errors + failed_requests == 0
    content_hash: str                            # hash(H1 + structural skeleton)
    page_block_status: clean | akamai-403 | challenge | partial
    page_confidence: 1-5
generated_by: live-capture
last_updated: str
last_updated_by: str
---
```

Derived frontmatter fields are limited to `mobile_render_clean` and `nav_persona_segmented`, each with the stated deterministic rule. Do NOT add comparative judgment fields (`login_competes_with_prospect_cta`, `primary_cta_verb_strength`, `sequential_ui_burial`); those are consumer computations.

`page_block_status` values: `clean` | `akamai-403` | `challenge` | `partial`. `akamai-403` is the vendor-neutral catch-all for any WAF 403 (Akamai, Cloudflare, DataDome, PerimeterX, Imperva); `challenge` is a bot-challenge interstitial; `partial` is a page that rendered but did not fully settle. A systemic WAF block on a headless browser stops the run rather than emitting these per page (see `capture.md` Step 1).

### live-observation.md body

**Site-level section (top):** recurring site-wide form (full field detail captured once, referenced by pages that show it), universal primary CTA, global nav structure; routing facts for comparison/"vs" pages, ROI tools, pricing (each maps to its tri-state frontmatter field; body carries the URL when `present`).

**Per-page sections, blocks A-I + K** (definitions in `capture.md`):
- **K. Page metadata** -- URL, capture timestamp, viewports, capture method, block status, page confidence.
- **A. Above-the-fold** -- H1, subhead, primary CTA presence, value-prop specificity (per viewport via the divergence block).
- **B. CTA inventory** -- each CTA: label, verb, treatment, position (fold/ordinal/region), destination, count. Primary prospect CTA by fact.
- **C. Login / account path** -- presence, count, position, label, new-tab behavior.
- **D. Forms** -- presence, embed type (+ third-party domain), total + required field counts, ordered labels, step count, modal/inline. FO-03 sub-block (value summary, trust elements near submit, next step stated).
- **E. Sequential UI / content burial** -- accordion/tab/carousel counts, `nested_content` extract, `nested_content_available`, static-ATF vs interaction-gated ratio.
- **F. Proof / trust** -- named-client outcomes (tri-state + extract); logo walls (client vs award/partner, count); stats; awards; partnerships; ordering/relative weight as facts; team credibility surface (TC-01, tri-state). Captured after scroll-load; `not_checked` when the page block status is `partial` or scroll-load did not complete (never a bare `false` for below-fold proof).
- **G. Navigation / IA** -- top-nav labels, footer structure, login placement (raw labels).
- **H. Render / technical (per viewport)** -- console_error_count, page_error_count, failed_request_count, rendered_page_height, render_correctness. Static mode: `[NOT AVAILABLE: static mode]`.
- **I. Chatbot / overlays** -- presence, system count, fire trigger, offer text, `overlays_cta`.

**`viewport_divergence` block (per page, fixed set):** `atf_visible_before_scroll`, `render_correctness`, `rendered_page_height`, `atf_primary_cta_present`. Everything else captured once and shared.

## Authoritative schema: live-copy.md

```yaml
---
schema: live-copy
schema_version: "1.1"
company: str
url: str
capture_date: YYYY-MM-DD              # positioning trusts this over any older snapshot
capture_method: chrome-devtools | playwright | static
supersedes_source: str | null         # e.g. "wayback-2026-01"
pages_captured: int
confidence: 1-5
pages:
  - path: str
    h1: str
    hero_subhead_present: bool
    content_hash: str
    page_block_status: clean | akamai-403 | challenge | partial
generated_by: live-capture
last_updated: str
last_updated_by: str
---
```

### live-copy.md body

Per page, timestamped, provenance-tagged: H1, hero subhead/H2, value-prop (verbatim); copy skeleton (all H2/H3 headings in document order + the lead sentence under each, mechanical extraction); proof statements (verbatim); optional candidate compliance/banned-term strings flagged for the consumer (flag only; the consumer applies the banned list).

## Confidence Model

Per-page confidence (the primary, actionable signal):

| Score | Meaning |
|---|---|
| 5 | chrome-devtools (full DOM + computed styles + console + network), both viewports, clean |
| 4 | playwright (managed DOM, screenshot iteration), both viewports, clean |
| 3 | mixed/static-on-some, or single viewport, or partial-block, or no-profile selection |
| 2 | static fallback dominant (~70% fidelity, no console/network/render), or multi-page Akamai-403 |
| 1 | mostly blocked/static, single viewport, caveated |

**File-level `confidence` = coverage-weighted aggregate** of per-page confidence, weighting each page by its leverage/traffic share, reported alongside the count of pages at each capture method and block status. Do NOT collapse to a single `min()`: pages are independent; one Akamai-partial page among nine clean captures must not drag the artifact to 2. If the no-profile fallback ran (Phase 1), cap the file-level confidence at 3 regardless.

## Write procedure

### Legacy mode

Write both artifacts to `.claude/context/live-observation.md` and `.claude/context/live-copy.md`. No frontmatter beyond the schema digest above. These are L0 context files; on re-run, overwrite (a capture is a point-in-time snapshot).

### KB mode

1. Read the three artifact-type defs resolved in Phase 0 for authoritative paths + frontmatter.
2. Write `live-copy.md` as `bronze-research-extraction` at `captures/research-extractions/{scope}-live-copy.md`.
3. Write `live-observation.md` as `bronze-note-capture` at `captures/notes/{capture_date}_{scope}-live-observation.md`.
4. Write the silver enrichment `live-structure.md` as `silver-structural-observation` at `reference/cro-{scope}/live-structure.md`. Its body is the `live-observation.md` structural content (the bronze note is the raw capture; the silver is the conformed projection). Frontmatter adds `kb_layer: silver`, `data_provenance: public`, `depends_on` (the two bronze paths, KB-root-relative), and the coverage-weighted `confidence`.
5. Apply the KB frontmatter contract and prior-work supersede from `SKILL.md` > `KB Mode`. Run the post-write validation gate on each artifact.

KB enrichment is additive. Never write to `silver-performance-analysis` / `performance-profile.md`.

## Output

The written artifacts (legacy paths or KB paths), passed to the orchestrator for the completion summary (and KB validation gate).
