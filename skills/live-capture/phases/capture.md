# Phase 2: Capture (browser modes)

For static mode, use `static-capture.md` instead.

## Goal

For each selected page, for each viewport, navigate, wait for full load, and PASSIVELY read the rendered DOM. Record the structural facts (blocks A-I + K) and verbatim copy. No DOM injection, no mutation. This is observation, not manipulation.

Read `agent-header.md` first. Facts only, tri-state for pass-dependent existence, portable position encoding, two provenance axes.

## Per-page, per-viewport procedure

### Step 1: Navigate and settle

- Chrome DevTools mode: navigate with the DevTools MCP (page opens in the user's Chrome).
- Playwright mode: `browser_navigate` (managed Chromium).
- **Set the viewport with device emulation, NOT a window resize.** A window resize clamps to the attached browser's real minimum width (observed ~666px), so it cannot produce a true phone viewport and silently yields a wrong mobile capture. Use device-metrics emulation:
  - Chrome DevTools mode: `emulate` with `viewport: "1280x900x1"` for desktop and `viewport: "390x844x3,mobile,touch"` for mobile.
  - Playwright mode: a mobile browser context / `browser_resize` to true device metrics (Playwright honors sub-window viewports).
  - If neither path can set a true sub-window mobile viewport, capture desktop only, set `viewports: [desktop]`, and record the mobile gap in Capture Caveats (do not emit fabricated or window-clamped mobile data).
- Wait for document ready. Network idle is best-effort: tracker-heavy sites may never idle. Cap the idle wait (~10-15s); if it does not settle, set `page_block_status: partial` and proceed (do not abort). If the page genuinely fails to load (404, connection refused, bot challenge), record `page_block_status` (`akamai-403`, `challenge`, or `partial`), capture whatever rendered, and continue. An isolated blocked page never aborts the run. For a content-blocked record (`akamai-403` / `challenge` / zero content rendered), write every pass-dependent tri-state field as `not_checked` and the pass-dependent counts as `null`, never `absent` or `0`: no detection pass ran against rendered content, so the record asserts nothing (per `agent-header.md` > Tri-State Existence Discipline). A `partial` page that did render keeps its real observations.

**Systemic WAF block (first-page rule).** A WAF block is: HTTP `403` with an `Access Denied` / `errors.edgesuite.net` (Akamai) body, or a Cloudflare / DataDome / PerimeterX / Imperva challenge interstitial, or any bot-challenge page in place of content. Distinguish systemic from isolated:

- **First captured page is WAF-blocked AND the browser is headless** (`browser_headless` true from SKILL Phase 0 step 5): this is systemic, the browser itself is the problem. **STOP the run.** Do not iterate the rest of the page set producing Access-Denied captures. Report the systemic block and the remedy: attach a real (non-headless) Chrome per `SKILL.md` > `Browser-Mode Detection` (Chrome DevTools `--browserUrl`/`--wsEndpoint`, or Playwright headful / `connectOverCDP`; WSLg/Xvfb on headless hosts). State explicitly that `--static` is NOT a remedy.
- **First page is WAF-blocked but the browser is real (not headless):** likely IP/geo/rate, not a headless fingerprint. Report it and ask the user how to proceed rather than grinding the full set.
- **A WAF block appears on some pages while others capture cleanly:** isolated. Keep the per-page behavior (record `page_block_status`, continue, never abort on one page).

The signal is: first-page / all-pages blocked = systemic (abort, advise); isolated among clean captures = per-page (continue).

### Step 1b: Scroll-load (REQUIRED before extraction)

Modern pages defer below-fold content via lazy-loading and IntersectionObserver. Extracting without scrolling produces false-negatives on proof, logos, testimonials, and team surfaces (Block F) because that content is not yet in the DOM. Before any extraction:

1. Scroll from top to bottom in viewport-height steps, pausing briefly at each step to let lazy content and observers fire.
2. Scroll back to the top.
3. Then run the batched extraction (Step 2).

If a dismissable consent/cookie overlay is blocking content load, note it; do not click through it unless content is genuinely gated (passive capture). Record overlay presence in Block I either way.

### Step 2: Batched extraction

Extract everything in as few `evaluate_script` / `browser_evaluate` calls as possible (one batched call per viewport is the target, mirroring experiment-mockup's inspect pattern). Run `window.getComputedStyle` and DOM queries inside the page context and return a single JSON object. Do not guess values you cannot read; mark them `not_checked` or omit per the tri-state rule.

Capture these blocks (full definitions in `write.md` > authoritative schema):

- **K. Page metadata** -- URL, capture timestamp, viewport, `capture_method`, `page_block_status`.
- **A. Above-the-fold** -- H1 text, subhead presence, primary CTA presence, value-prop text. Per viewport (see the divergence block).
- **B. CTA inventory** -- every CTA: label text, verb, visual treatment (filled/ghost, color), position (fold + ordinal + region), destination, total `cta_count`. Identify the primary prospect CTA by FACT (largest visual weight + highest fold position).
- **C. Login / account path** -- `login_present`, `login_above_fold`, `login_nav_rank` (ordinal in nav), count, label text, new-tab behavior.
- **D. Forms** -- `form_present`, embed type (marketo / hubspot / native / other) + third-party domain, `form_field_count` (perceived), `form_required_field_count` (actual friction), ordered field labels, step count, modal-vs-inline. FO-03 sub-block: `value_summary_present`, `trust_elements_near_submit` (badge / privacy-link / lock-icon / microcopy), `next_step_stated`.
- **E. Sequential UI / content burial** -- count DISTINCT top-level sequential components, not every descendant matching a class substring. Target component roots only (e.g. `[role=tablist]`, a carousel/slider root such as `.swiper`/`.slick-slider`/`[data-carousel]`, an accordion root), and de-duplicate nested matches. A permissive `[class*=...]` sweep over-counts wildly (one component yields dozens of hits). Record `sequential_ui_present`, `sequential_ui_items` (distinct roots), `nested_content` extract when in the DOM, `nested_content_available: in_dom | lazy_loaded | not_checked`. Do NOT click to expand (passive read); mark genuinely lazy content `not_checked`.
- **F. Proof / trust** -- run AFTER Step 1b scroll-load. `named_client_proof_present` (tri-state); logo walls (client vs award/partner, count); stats; awards; partnerships; ordering / relative visual weight as facts; `proof_element_count`; `team_credibility_present` (tri-state: team / leadership / headshot / bio surface). These are tri-state because they depend on below-fold lazy content: if the scroll-load did not complete or the page block status is `partial`, record `not_checked`, never a bare `false`.
- **G. Navigation / IA** -- top-nav item labels (raw; note many enterprise mega-navs are button-driven, so capture nav `<button>` labels too, not only anchors), login placement in nav. Detect the footer by `footer, [role=contentinfo]` OR a recognizable footer region (sites often omit the semantic `<footer>` landmark); record footer presence by region, and separately whether a semantic landmark exists. Leave persona-vs-feature classification to the consumer; record raw labels.
- **H. Render / technical (per viewport)** -- `console_error_count`, `page_error_count`, `failed_request_count`, `rendered_page_height`, `render_correctness`. Read console + network signals from the browser MCP. (Static mode cannot populate these; see static-capture.md.)
- **I. Chatbot / overlays** -- `chatbot_present` (tri-state), number of systems, fire trigger, offer text, `overlays_cta` bool.

`objection_faq_present` (TC-02) has no dedicated detection pass yet. Emit it explicitly as `not_checked` for every page rather than omitting it: omission would read to the consumer as missing-equals-not_checked anyway, but an explicit value keeps the artifact schema-complete and honest about the absent pass. Do not write `absent` (no pass looked) and do not infer it from headings here.

### Step 3: Viewport divergence

Most fields are captured once (on desktop) and shared. For the mobile pass, re-emulate the mobile viewport (Step 1) and re-run Step 1b scroll-load before reading, since fold position and lazy-load behavior differ at phone width. Capture the fixed `viewport_divergence` block per viewport: `atf_visible_before_scroll`, `render_correctness`, `rendered_page_height`, `atf_primary_cta_present`. If a field genuinely differs across viewports, the per-viewport value lives here. If a true mobile viewport could not be emulated, omit mobile from `viewports` and note it in Capture Caveats rather than recording window-clamped values.

### Step 4: Copy capture (for live-copy.md)

In the same read, capture verbatim copy for `live-copy.md`: `h1`, hero subhead / H2 (`hero_subhead_present` + text), value-prop (verbatim), the copy skeleton (all H2/H3 headings in document order + the lead sentence under each, mechanical extraction), and proof statements (verbatim). Flag candidate compliance / banned-term strings for the consumer; do not apply a banned list here.

### Step 5: content_hash

Compute the per-page `content_hash` deterministically:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY skills/live-capture/scripts/content_hash.py --h1 "<H1 text>" --skeleton "<ordered H2/H3 headings joined by newlines>"
```

Record the returned hash on both the `live-observation.md` and `live-copy.md` page entries.

### Step 6: Per-page confidence

Assign per-page confidence per the rubric in `write.md`:
- 5: chrome-devtools, both viewports, clean.
- 4: playwright, both viewports, clean.
- 3: mixed / single viewport / partial block / no-profile selection.
- 2: static dominant, or multi-page Akamai-403.
- 1: mostly blocked, single viewport.

## Output

Per-page captured facts (blocks A-I/K + viewport_divergence) and verbatim copy, with per-page `content_hash`, `page_block_status`, and `page_confidence`, carried in-session to Phase 3 (`write.md`).
