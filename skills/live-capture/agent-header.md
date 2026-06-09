# live-capture -- Shared Agent Rules

These rules apply to every agent the live-capture skill spawns. Read this file first, before any phase-specific instructions.

---

## 1. Factual Artifact, Interpretive Consumer

This skill captures FACTS and mechanical derivations only. It never writes judgments. The consuming skills (hypothesis-generator's detect phase, experiment-mockup, positioning-framework) compute the judgments.

- Record what exists, its label, its position, its count, its render state.
- Never write "login competes with the prospect CTA", "the verb is weak", "value is buried", "the form is too long". Those are consumer judgments.
- Two mechanical derivations are permitted in frontmatter because each has a stated deterministic rule:
  - `mobile_render_clean` = `true` only when the mobile capture recorded `console_error_count == 0` AND `failed_request_count == 0`.
  - `nav_persona_segmented` = `true` only when top-nav labels match `/for-|by-(role|use-case)/`. This is a hint; NX-01 also reads L1 personas.
- The comparative fields the design floated (`login_competes_with_prospect_cta`, `primary_cta_verb_strength`, `sequential_ui_burial`) are deliberately ABSENT. Do not add them.

**Precedence:** accuracy > capture fidelity > completeness. A missing fact flagged honestly beats an invented one.

---

## 2. Tri-State Existence Discipline

Anything whose detection depends on a pass that may not have run is recorded as `present | absent | not_checked`, never a bare boolean. A bare `false` from a pass that never ran misfires consumer patterns (e.g. CR-01).

- `comparison_page_exists`, `roi_tool_exists`, `pricing_page_exists`, `objection_faq_present`, `chatbot_present`: tri-state.
- `named_client_proof_present`, `team_credibility_present`: tri-state. These depend on below-fold lazy content, so when the scroll-load (capture Step 1b) did not complete or the page block status is `partial`, record `not_checked`, never a bare `false` (a false would read as "no proof exists" when it simply did not load).
- Genuinely lazy-loaded or interaction-gated content that was not expanded: mark `nested_content_available: not_checked`, not a false `absent`.
- Booleans are reserved for facts observable in the rendered DOM of a captured page (e.g. `form_present`, `login_above_fold`).

**Content-blocked pages assert nothing.** When a page's capture is content-blocked (`page_block_status: akamai-403` or `challenge`, or any zero-content result), no page content was ever rendered, so the detection passes never ran. EVERY pass-dependent tri-state field for that page MUST be `not_checked`, never `absent`. A pass that never saw rendered content cannot confirm absence, that is the exact false assertion the tri-state design exists to prevent. Counts that those passes would populate (`cta_count`, `proof_element_count`, `form_field_count`, `form_required_field_count`) are `null` for the blocked page, not an observed-looking `0`. This is distinct from `partial` (the page rendered but did not fully settle): a `partial` page's real observations stand as captured and must NOT be blanked, the consumer already downgrades partial-page signal strength. Only the below-fold-dependent proof fields follow their own narrower `partial` rule above.

---

## 3. Position Encoding Is Portable

Never record absolute pixels (they break on layout change and differ per viewport). Each positioned element carries three coordinates:

- **fold**: `above_fold | below_fold` (per viewport)
- **ordinal**: integer order within its region
- **region**: `header | hero | body | footer`

The primary prospect CTA is identified by FACT (largest visual weight + highest fold position), not by judgment about quality.

---

## 4. Two Provenance Axes (Do Not Conflate)

- **Capture provenance** (`capture_method`: `chrome-devtools | playwright | static`): how the fact was read. A DOM read (devtools/playwright) is direct observation; static is weaker (~70% fidelity, no computed styles, console, network, or render data). Block H in static mode writes `[NOT AVAILABLE: static mode]`, never a false `clean`.
- **Headless browsers get WAF-blocked.** Enterprise bot management (Akamai/Cloudflare/etc.) 403s headless Chrome before content loads. A WAF-protected target requires a real (non-headless) Chrome (see SKILL.md `Browser-Mode Detection`). Static is NOT a WAF remedy. If the first page is WAF-blocked on a headless browser, the run stops and advises a real Chrome (SKILL.md Phase 0 + capture.md Step 1), rather than producing a near-empty low-confidence artifact.
- **KB `data_provenance`** (`public | client`): buyer-validation status. Live observation is always `public` (inferred from public sources without buyer validation).

A DOM-read fact is high capture fidelity yet still `public`. Keep the two fields separate.

---

## 5. Multi-Viewport

Capture desktop and mobile by default. Most fields are captured once and shared. Only the fixed `viewport_divergence` block differs per viewport: `atf_visible_before_scroll`, `render_correctness`, `rendered_page_height`, `atf_primary_cta_present`.

---

## 6. Output Files

| File | Mode | How used |
|------|------|----------|
| `.claude/context/live-observation.md` | legacy | Write: structural facts (L0) |
| `.claude/context/live-copy.md` | legacy | Write: verbatim copy (L0) |
| `{kb_root}/captures/.../live-observation.md` | KB | Write: bronze (`bronze-note-capture`) |
| `{kb_root}/captures/.../live-copy.md` | KB | Write: bronze (`bronze-research-extraction`) |
| `{kb_root}/reference/cro-{scope}/live-structure.md` | KB | Write: silver enrichment (`silver-structural-observation`) |
| `performance-profile.md` / `silver-performance-analysis` | both | Read only: page-selection input. NEVER written. |

The authoritative artifact schema (frontmatter + body) lives inline in `phases/write.md`. The `schemas/` copies are human reference only.

---

## 7. Confidence Is Coverage, Not Quantity

Confidence reflects capture completeness and method fidelity, never how much data a page has. Per-page confidence is the primary, actionable signal. File-level confidence is a coverage-weighted aggregate of per-page confidence (weight by each page's leverage/traffic share), NOT a `min()`. One Akamai-blocked page among nine clean captures must not drag the whole artifact down. See `phases/write.md` for the rubric.

---

## 8. Em Dashes

Never use em dashes. Use colons, commas, periods, or separate sentences.
