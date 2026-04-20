# Phase: Opportunity Detection

## Required Inputs

- Full body of `company-identity.md` (L0)
- Full body of all available L1 context files (including `performance-profile.md` if present)
- `modules/experiment-patterns.md` (loaded by orchestrator)
- Any `modules/evidence-*.md` files (optional, loaded by orchestrator if present)

## Depth Behavior

This phase does not vary by depth. All available context is scanned regardless of how it was produced.

## Graceful Degradation

| Missing Context | Impact |
|----------------|--------|
| positioning-scorecard.md | Skip scorecard-triggered patterns. Use gap inference from L0 + other L1 instead. |
| competitive-landscape.md | Skip competitive-pressure patterns (pricing transparency, differentiator crowding). |
| audience-messaging.md | Skip persona-dependent patterns (segment hero, industry proof, nav intent mismatch). |
| performance-profile.md | Skip all performance-driven triggers (Step 1c). Confidence capped at 4 globally. Add "Run /ga4-audit for data-calibrated scores and traffic-driven hypotheses" to Prerequisites. |
| All L1 files | Detect from L0 only. Limited to patterns triggered by website copy, proof points, and structural signals. |

---

## Detection Process

### Step 1: Extract Testable Signals

Scan each context file for specific, concrete signals that indicate a testable opportunity. A signal is NOT a vague observation ("messaging could be better"). A signal is a specific, observable condition ("homepage headline uses category language 'Revenue Intelligence Platform' instead of outcome language").

**Signal sources by context file:**

**From company-identity.md (L0):**
- Homepage headline and subhead copy (exact text)
- Stated differentiators vs. proof points supporting them
- Target segments and personas listed
- Pricing model presence or absence
- Proof point registry: count, strength distribution, which pages they appear on
- Website structure: which pages exist, what's missing
- Form fields observed during research
- CTA language observed

**From positioning-scorecard.md (L1):**
- Dimensions rated "Needs Work" or "Missing" (direct triggers)
- Gap analysis narrative (specific observations about what's weak and why)
- Top gap and top opportunity fields from frontmatter

**From competitive-landscape.md (L1):**
- Claim overlap map: which differentiators are crowded vs. unique
- White spaces: positioning territories no competitor has claimed
- Competitor pricing transparency vs. target company
- Competitor proof strength vs. target company

**From audience-messaging.md (L1):**
- Persona definitions: how many, how distinct
- Channel adaptations: recommended messaging per page/touchpoint
- Voice profile: current tone vs. recommended tone
- Banned terms list: language currently used that should be avoided
- Message hierarchy: primary, secondary, tertiary messages and where they should appear

**From performance-profile.md (L1, if present):**
- Page-level traffic volumes (sessions per page)
- Bounce rates per page (especially high-bounce pages >50%)
- Per-page conversion rates and site-wide conversion rate
- Mobile traffic percentage and mobile vs desktop engagement gap
- Channel-level bounce rate gaps (e.g., paid vs organic on same pages)
- Landing page bounce rates (first-impression signals)
- Conversion event inventory and per-page funnel data
- Data gaps noted in Key Metrics Summary (what can't be measured)
- Page group performance (group-level bounce, CVR, session volumes)
- Source x page mismatches (channel-specific performance gaps)
- New vs returning cohort data (familiarity dependence signal)
- Period-over-period trends (urgency weighting for worsening metrics)
- Failure mode per page (shallow vs deep engagement)
- Pre-sized opportunity list with impact buckets
- Session-depth distribution (pages/session for high-engagement segments)
- Paid vs organic traffic split per page
- Element-level interaction data (when `element_interactions_available: true`):
  - Per-element click rates on key pages (CTA engagement signal)
  - CTA hierarchy dominance (one element gets disproportionate clicks)
  - Sequential content drop-off (carousel/tab engagement decay)
  - Discovered parameter types (what element tracking exists)

### Step 1b: Context Quality Flags

Run in parallel with signal extraction (Step 1). Scan all loaded context files for quality indicators that affect downstream scoring and pattern coverage.

**Flag types:**

1. **Incomplete sections.** Sections marked with `[NEEDS CLIENT INPUT]` or `[NEEDS CONFIRMATION]` in any context file. Record: file, section, marker type.

2. **Low-confidence context.** Context files with overall confidence < 3, or individual sections where the frontmatter flags low confidence. Record: file, confidence score, which sections are affected.

3. **Unverified proof.** Proof points in L0's proof registry with strength "claimed" (not "verified" or "supported"). Record: proof point, current strength, which patterns would benefit from verification.

4. **Missing context files.** Context files that don't exist but would enable additional patterns. Record: file name, which pattern categories are disabled.

5. **Protected brand elements.** Terms, concepts, or positioning language that may carry executive, legal, or brand-guideline authority. Check these sources:
   - L0 `company-identity.md`: brand guidelines section listing required terminology, mandated taglines, or legally required disclaimers
   - L0 `company-identity.md`: glossary entries marked "always use" or "required"
   - `brand-voice.md`: mandated vocabulary, non-negotiable voice elements, or required framing
   - L0 constraints section: regulatory language requirements, trademark usage rules

   Record for each flagged element:
   - Term or concept
   - Protection type: `legal` (trademark, regulatory, compliance), `brand` (executive mandate, brand guidelines, voice rules), `regulatory` (industry-specific required language)
   - Source: file and section where the protection signal was found

   If none of these sources exist or contain protected elements, this flag type produces no output. That is expected for companies without formal brand governance.

   These flags feed into construct.md Step 3c (Protected Element Handling). They do NOT filter opportunities in this phase.

These flags are NOT used for filtering in this phase. They feed into the Prerequisites and Data Gaps compilation in Phase 4 (Step 8).

**Output:** Context quality flag list, carried forward alongside opportunity list.

### Step 1c: Performance-Driven Triggers

**Skip this step entirely if `performance-profile.md` is not present.**

These triggers fire only when quantitative GA4 data exists. They produce net-new opportunities that positioning analysis alone cannot surface. Each trigger is concrete and data-dependent.

Run these in parallel with pattern matching (Step 2). Performance-driven opportunities join the opportunity list with `signal_source: performance-profile.md`.

| Trigger Condition | Hypothesis Type | Example |
|---|---|---|
| Page gets >500 sessions/mo from paid traffic AND bounce >45% | Landing page messaging mismatch for paid visitors | "Paid traffic to /pricing bounces at 51% vs 39% organic. Ad promise doesn't match page reality." |
| Page has conversion rate <50% of site average AND >200 sessions/mo | Conversion friction on high-traffic page | "/solutions/enterprise gets 890 sessions but converts at 0.5% vs 2.0% site avg. Messaging or layout friction." |
| Mobile bounce rate >10pp higher than desktop on same page | Mobile UX/messaging friction | "Mobile bounce on homepage is 56% vs 42% desktop. Above-fold content doesn't work on small screens." |
| Landing page bounce >55% AND page is top-5 entry point | First-impression failure | "/blog/guide-x is 3rd highest entry point but 68% bounce. Content-to-CTA path is broken." |
| Top conversion page has no positioning-derived hypothesis targeting it | Untested high-value page | "/demo converts at 11.9% but no positioning gap targets it. Test proof placement or form copy." |
| Channel X has 2x+ bounce rate vs Channel Y on same page | Channel-specific messaging mismatch | "Google Ads traffic bounces at 52% vs organic at 38% on homepage. Paid visitors need different messaging." |
| Form conversion event exists but page conversion <5% | Form optimization opportunity | "generate_lead fires on /contact but only 3.2% of visitors complete it. Form friction signal." |
| `source_page_mismatches` has entries with `gap_type: "bounce"` | Channel-specific landing page mismatch | "Paid search bounces 15pp above organic on /pricing. Channel-specific messaging needed." |
| `new_vs_returning.signal` = `"familiarity_dependent"` | First-visit conversion failure / nurture gap | "Returning:new ratio is 5.2x. First-visit experience is failing. Nurture or first-impression intervention needed." |
| `trends.primary_cvr_change_pp` < -0.5 | Worsening conversion trend | "Primary CVR declined 0.8pp vs prior period. Urgent: identify what changed." |
| `trends.bounce_rate_change_pp` > +5 | Worsening bounce trend | "Bounce rate increased 6.2pp vs prior period. Recent change may have degraded experience." |
| Page has `failure_mode: "shallow_engagement"` | Messaging mismatch (not layout) | "/blog/guide-x has shallow engagement (1.1 pages/session, 62% bounce). Messaging doesn't match visitor intent." |
| Page has `failure_mode: "deep_engagement"` | Funnel friction (CTA/pricing/trust, not messaging) | "/pricing has deep engagement (3.8 pages/session) but 0.4% CVR. Visitors explore but don't convert." |
| `page_groups` group has CVR < 25% of top group | Structural content-to-conversion gap | "Blog group converts at 0.19% vs Product group at 2.0%. Blog-to-conversion path is a structural opportunity." |
| `top_opportunities` has entries with `estimated_monthly_impact: "large"` | Pre-sized high-impact opportunity | "/pricing has a 'large' sized opportunity (bounce_reduction). Pre-validated by opportunity sizing." |
| Paid traffic >200 sessions/mo to a page AND no dedicated landing page variant exists | Ad-message match / paid landing page opportunity | "Google Ads sends 340 sessions/mo to /solutions but page has full site nav and generic headline. No ad-specific landing page." |
| `element_interactions_available: true` AND page >500 sessions/mo AND primary CTA interaction rate <3% | CTA visibility/clarity issue | "/pricing gets 5,600 sessions but 'Request Demo' CTA click rate is 1.8%. CTA underperforming." |
| `top_interactions` shows one element gets >5x clicks of next element for same event on same page | CTA hierarchy dominance | "On /pricing, 'Request Demo' gets 245 clicks vs 'View Plans' at 42. Secondary CTA nearly invisible." |
| `top_interactions` shows sequential items (carousel, tabs) where later items get <20% of first item interactions | Content below first view invisible | "Homepage carousel: slide 1 gets 890 interactions, slide 3 gets 67 (7.5%). Content after first slide is effectively hidden." |
| Element data exists for a page already targeted by a positioning-derived hypothesis | Enrichment: adds interaction baseline | "Element data shows 'Get Started' CTA on / has 1.5% click rate. Adds baseline to existing homepage messaging hypothesis." |

**Trigger evaluation rules:**
- Use the performance-profile.md frontmatter `top_pages` for quick lookups. Read body sections for full data when a trigger condition needs per-page detail.
- "Sessions/mo" = sessions in the profile's date range, normalized to 30 days if the range differs.
- Triggers that match a page already targeted by a positioning-derived hypothesis still fire. They produce a separate performance-driven opportunity that will merge with the positioning-derived one in Phase 3 (Step 7), enriching it with baseline data.
- Each performance-driven opportunity uses ICE baseline 3/3/3 (same as context-derived). The performance data provides evidence for scoring modifiers in Phase 4, not for inflating the baseline.

**Output:** Performance-driven opportunities added to the opportunity list, tagged `type: "performance-driven"`.

### Step 2: Match Signals Against Patterns

For each signal extracted in Step 1, check against the trigger conditions ("Applies when") in `modules/experiment-patterns.md`.

**Matching rules:**
- A signal can trigger multiple patterns. This is expected and correct.
- A pattern can be triggered by signals from multiple context files. Use the strongest signal.
- If a pattern's trigger condition partially matches (e.g., "form has 5+ fields" and you found a form but can't confirm field count), create the opportunity but flag it as "trigger partially confirmed."
- If `--focus` flag was set, only evaluate patterns in the specified categories.

### Step 3: Evidence Augmentation

If any `modules/evidence-*.md` files were loaded, apply their contents now:

- Additional trigger conditions from evidence modules are checked against context signals
- Scoring calibration data is attached to matching opportunities (passed to Phase 4)
- Evidence modules may introduce patterns not in the base library. Process identically.

If no evidence modules exist, skip this step entirely. The skill functions normally without them.

### Step 4: Build Opportunity List

For each pattern match, produce an opportunity record:

```
Opportunity:
  pattern: [pattern ID and name]
  category: [headline | form | navigation | personalization | layout | pricing | social-proof | content | trust | element-engagement]
  trigger_signal: [the specific signal from context that matched]
  signal_source: [which context file and section]
  trigger_strength: [full | partial]
  ice_baseline: [I/C/E from pattern definition]
  calibration_data: [from evidence modules, if any]
  notes: [anything relevant to downstream phases]
```

These records are internal only. Never written to disk, never appear in deliverables.

### Step 5: Preliminary Filtering

Remove opportunities where:
- Trigger is "partial" AND no other signal supports the same pattern
- Pattern category was excluded by `--focus` flag
- Same page + mechanism combination appears twice (keep stronger trigger)

Do NOT filter based on ICE scores. That happens in Phase 4.

### Step 6: Unmatched Signal Collection

After Step 5 filtering, collect all signals from Step 1 that did NOT trigger any pattern match (neither full nor partial). These are signals that represent potentially testable conditions but don't map to any pattern in `modules/experiment-patterns.md`.

For each unmatched signal, produce a raw signal record:

```
Unmatched Signal:
  source_file: [context file name]
  source_section: [specific section within the file]
  signal_text: [the concrete, observable condition]
  signal_type: [gap | mismatch | opportunity | structural]
```

**Signal types:**
- `gap`: Something expected is missing (e.g., no case studies on a page that would benefit from them)
- `mismatch`: Two pieces of context contradict (e.g., audience-messaging recommends outcome language but a key page uses feature language)
- `opportunity`: An unused asset or underexploited strength (e.g., verified proof points not displayed)
- `structural`: A site architecture or UX pattern that could be improved (e.g., navigation doesn't reflect persona segmentation)

Do NOT filter these signals for quality. That happens in Phase 2b. Pass all unmatched signals forward.

**Output to Phase 2b:** Unmatched signal list.

**Output to Phase 3:** Complete opportunity list from Steps 1-5, typically 15-25 items. If fewer than 8, note this for the orchestrator's completion summary.
