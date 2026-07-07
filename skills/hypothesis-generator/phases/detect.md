# Phase: Opportunity Detection

## Required Inputs

- Full body of `company-identity.md` (L0)
- Full body of all available L1 context files (including `performance-profile.md` if present)
- `modules/experiment-patterns.md` (the base library, loaded by orchestrator)
- The matched archetype pattern module (e.g., `modules/patterns-procurement.md`), if the orchestrator resolved one in SKILL.md Phase 1 `Archetype resolution`. Absent until an archetype module exists; detection runs on the base library alone when none is loaded.
- Any `modules/evidence-*.md` files (optional, loaded by orchestrator if present)
- `engagement-constraints` input (optional): delivery and governance state, consumed by Step 1d. Absent in most runs; Step 1d is skipped when absent. Never produces opportunities, only constraints.
- The structural observation artifact body (KB mode only, optional): the scope's `silver-structural-observation` artifact (`live-structure.md`), loaded by the orchestrator per SKILL.md `Read-side Mapping` when present. Consumed by the Step 1 structural extraction stanza and the Step 1e field-keyed triggers.
- The experiment-history input (KB mode only, optional): the bound experiment-history source -- either the external producer's `gold-experiment-index` plus the silver insight records it links, OR the in-output-KB `schema: experiment-history` silver artifact plus the per-experiment gold insight guides it summarizes -- loaded by the orchestrator per SKILL.md `Read-side Mapping` when bound. Consumed by the Step 1g experiment-history triggers. Absent in most runs; Step 1g is skipped when absent with no confidence consequence.
- Step 1f draws on the inputs already listed above: `performance-profile.md` (measurement inventory and the FM9 contamination flag), the other loaded silver artifacts (live-capability statements that augment the measurement inventory), and the structural observation artifact (staleness signals). It adds no new input file; each leg skips with no penalty when its backing artifact is absent.

In KB mode the orchestrator supplies the same context bodies, sourced from the scope's silver artifacts per the SKILL.md `KB Mode (Dual-Mode Output)` > `Read-side Mapping`. Trigger and detection logic below is source-agnostic and unchanged, with one addition: the structural observation artifact is KB-native (no legacy equivalent) and is consumed by Step 1 and Step 1e only.

## Depth Behavior

This phase does not vary by depth. All available context is scanned regardless of how it was produced.

## Graceful Degradation

| Missing Context | Impact |
|----------------|--------|
| positioning-scorecard.md | Skip scorecard-triggered patterns. Use gap inference from L0 + other L1 instead. |
| competitive-landscape.md | Skip competitive-pressure patterns (pricing transparency, differentiator crowding). |
| audience-messaging.md | Skip persona-dependent patterns (segment hero, industry proof, nav intent mismatch). |
| performance-profile.md | Skip all performance-driven triggers (Step 1c). Confidence capped at 4 globally. Add "Run /ga4-audit for data-calibrated scores and traffic-driven hypotheses" to Prerequisites. |
| Structural observation artifact (live-structure, KB mode) | Skip structural observation triggers (Step 1e). NO confidence penalty and NO global cap: absence means page structure was not assessed, not that structure is sound or broken. Element targeting falls back to context-inferred pages. Add "Run /live-capture for structure-driven triggers and observed current-state documentation" to Prerequisites. |
| Experiment-history input (not bound, KB mode -- no external producer AND no in-KB `schema: experiment-history` artifact) | Skip experiment-history triggers (Step 1g). NO confidence penalty and NO global cap: absence means no prior-experiment evidence was available. Add "Connect a completed-experiment knowledge base" to Prerequisites. |
| performance-profile.md (for Step 1f measurement inventory / FM9 contamination flag) | Skip the performance-profile source of the measurement-inventory leg and the contamination-flag leg (the live-capability source still scans the other loaded artifacts). NO confidence penalty beyond the existing performance-profile cap (row above): absence means measurement coverage was not assessed, not that every metric is dark. Validate's `metric_instrumented` keeps its no-performance-profile precedence (reads not-assessed, neutral, never a fail) regardless of any `live-elsewhere` entries; `powerable` reads not-assessed. |
| Structural observation artifact (for Step 1f staleness signals) | Skip the Step 1f staleness leg. NO confidence penalty and NO global cap (same rule as the structural-observation row above): absence means current-state freshness was not assessed. Validate's `control_stable` gate reads not-assessed (neutral, never a fail). |
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

**From the structural observation artifact (live-structure, KB mode, if loaded):**
- Site-level: form recurrence (`form_recurs_sitewide`, sitewide form field and required-field counts), site-wide primary CTA label, existence tri-states (`comparison_page_exists`, `roi_tool_exists`, `pricing_page_exists`), `nav_persona_segmented`
- Per-page (frontmatter pages digest plus body blocks): form presence, field and required-field counts, embed vendor; primary CTA label and `cta_count`; login presence, above-fold placement, nav rank; proof signals (`named_client_proof_present`, `proof_element_count`, `team_credibility_present`); sequential UI presence and item count; `chatbot_present`; `objection_faq_present`; `mobile_render_clean`; navigation labels
- Copy skeleton (headline, subhead, section heading text captured verbatim): feeds generic pattern matching in Step 2 exactly like website copy from L0 (e.g., service-page differentiation, specificity injection)
- Trust qualifiers: a `page_block_status` other than clean, a low `page_confidence`, or a viewport divergence note downgrades trigger strength to "partial" for signals from that page
- Tri-state fields (`present | absent | not_checked`) are never coerced to booleans. A field missing from a page record is treated as `not_checked`.
- Rendered page height and section count feed existing page-length patterns (e.g., PS-02) as ordinary signals; they need no dedicated trigger.

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

#### Profile Schema Equivalence

The trigger conditions below are written against the ga4-audit v2.x performance-profile field names. Profiles produced by other audit skills may carry equivalent data under different structure, and may lack `schema_version` entirely (common for KB-mode silver performance artifacts).

- When the profile carries `schema_version`, the SKILL.md Preconditions version gating applies unchanged.
- When `schema_version` is absent, bypass the version gate and evaluate each trigger by **content equivalence**: if the profile body carries semantically equivalent data, the trigger fires against that content. Equivalence examples:

| v2.x field condition | Equivalent profile content |
|---|---|
| `top_opportunities` with `estimated_monthly_impact` | A pre-sized opportunity table or list with impact buckets (e.g., Large / Medium / Small) |
| `trends.primary_cvr_change_pp`, `trends.bounce_rate_change_pp` | Period-delta or period-over-period trend tables for conversion and bounce metrics |
| Page sessions/bounce conditions (paid traffic, entry points, high-bounce pages) | A page-level traffic/bounce table with per-page volumes |
| Data-gap gating (what can't be measured) | Documented data-gap or measurement-constraint notes in the profile body |
| Site-level device gap (`device_mobile_pct` frontmatter + "Mobile vs Desktop Gap" body table) | A site-level device breakdown with bounce and/or conversion by device |

- Triggers whose data has no equivalent in the profile (e.g., `element_interactions_available`, `top_interactions`, `page_groups`, `failure_mode`, `new_vs_returning` when those structures are absent) self-gate off, exactly as absent frontmatter fields do today.
- The same self-gating applies to version-stamped profiles: when a profile carries a `schema_version` but a referenced structure is absent (e.g., a "2.1"-stamped profile with `element_interactions_available: true` but no `top_interactions` list), the trigger conditions cannot match and the trigger self-gates off, with no penalty. The version stamp gates eligibility, not firing; firing always requires the actual data.
- Equivalence is evaluated per trigger, not per profile: one profile may satisfy the opportunity-sizing and trend triggers while lacking element-interaction data entirely.

| Trigger Condition | Hypothesis Type | Example |
|---|---|---|
| Page gets >500 sessions/mo from paid traffic AND bounce >45% | Landing page messaging mismatch for paid visitors | "Paid traffic to /pricing bounces at 51% vs 39% organic. Ad promise doesn't match page reality." |
| Page has conversion rate <50% of site average AND >200 sessions/mo | Conversion friction on high-traffic page | "/solutions/enterprise gets 890 sessions but converts at 0.5% vs 2.0% site avg. Messaging or layout friction." |
| Site-level mobile bounce rate >10pp higher than desktop OR mobile CVR <50% of desktop (per the profile's "Mobile vs Desktop Gap" table), AND mobile share of sessions >=20% | Mobile UX/messaging friction | "Mobile bounces at 56% vs 42% desktop site-wide, with 45% of sessions on mobile. Above-fold content doesn't work on small screens. Target the highest-traffic mobile entry pages." |
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
| A single non-search, non-self-referral source contributes a large share of sessions AND its intent is unverified | Denominator / segmentation hypothesis, or a routed client question | "A partner/seller tool is the second-largest traffic source; should its arrivals sit in the buyer-funnel denominator at all? Route as a client question or a segmentation hypothesis, not a conversion experiment." |
| A cross-property referral (sister brand, parent domain) shows an elevated quickback rate vs other sources | Cross-property handoff-pathing hypothesis | "Referrals from a sister property quickback well above the site average; the handoff landing experience mismatches arriving intent. Test the landing/pathing for that referral segment." |

**Trigger evaluation rules:**
- Use the performance-profile.md frontmatter `top_pages` for quick lookups. Read body sections for full data when a trigger condition needs per-page detail.
- "Sessions/mo" = sessions in the profile's date range, normalized to 30 days if the range differs.
- Triggers that match a page already targeted by a positioning-derived hypothesis still fire. They produce a separate performance-driven opportunity that will merge with the positioning-derived one in Phase 3 (Step 7), enriching it with baseline data.
- Each performance-driven opportunity uses ICE baseline 3/3/3 (same as context-derived). The performance data provides evidence for scoring modifiers in Phase 4, not for inflating the baseline.
- The arrival-mix and cross-property triggers fire off the arrival-mix / source data in the performance profile. When the source's intent cannot be determined from context, prefer routing a client question over inventing a hypothesis about an unknown population.
- The device-gap trigger is site-level by design: no producer emits per-page device data (ga4-audit's device report is site-level only -- `device_mobile_pct` frontmatter plus the "Mobile vs Desktop Gap" body table; aa-audit likewise). Never condition a trigger on a per-page mobile-vs-desktop split. Target the resulting hypothesis at the highest-traffic mobile-relevant pages from `top_pages`, and state the gap as site-level in the hypothesis evidence.

**Output:** Performance-driven opportunities added to the opportunity list, tagged `type: "performance-driven"`.

### Step 1d: Engagement-Constraint Reasoning

Skip this step if no `engagement-constraints` input is present.

Read the engagement-constraints input. For each constraint, derive its experiment implication. This is reasoning, not extraction: do not copy the constraint into the roadmap. Derive what it means for timing, tiering, or feasibility, and carry only the derived implication forward.

Procedure:

1. **Release calendar:** for each experiment, does a committed release change a target surface during the test window? If yes, the experiment must read out fully before the release or start after it. A surface touched by a release cannot hold a baseline across it.
2. **Approval/governance bandwidth:** how many concurrent experiments can clear the client gate? Set a concurrency ceiling. On a freshly cautious gate (recent incidents, escalations), set a tier ceiling on high-risk surfaces.
3. **Measurement-infrastructure timeline:** when does the enablement that lifts a Confidence cap actually land? Set the earliest re-tier window and sequence readouts to mature into it, not before.
4. **Internal-tester/QA constraints:** does a test on an internally-visible surface need a tester-exclusion mechanism before launch? If yes, gate the experiment on that mechanism.
5. **Delivery-match risk:** does a delivery constraint (e.g., a customer network blocking the variant-delivery domain) dilute the test population? Flag as a launch-gate check.

The procedure generalizes beyond these five: for any constraint the input supplies, name the experiment property it bounds (timing, concurrency, tier, feasibility, or launch-gating), then carry the derived bound forward. The worked examples below show the reasoning applied; they are not the only constraints the step handles.

Worked example 1 (release calendar): an August release carries a PDP and cart redesign. An experiment targeting both PDP and cart faces double exposure, so it starts after the release and uses the pre-release window for integration-feasibility scoping only. An experiment targeting cart alone can read out fully before the release or start after. The reasoning, not the calendar entry, is what reaches the roadmap.

Worked example 2 (approval bandwidth): a series of injection-caused UX incidents leads to a governance escalation and a signalled preference for a more pragmatic pace. Plan two to three concurrent approvals at most. Copy-light, off-configurator experiments are the near-window candidates; configurator-touching experiments belong to the next pace conversation. The derived constraint is a concurrency ceiling plus a tier ceiling on the riskiest surface, not a restatement of the incident history.

**Output:** engagement-derived sequencing and tier constraints, carried to Phase 4 (sequencing) and to the Prerequisites section. These are constraints, NOT hypotheses. Do not add them to the opportunity list.

### Step 1e: Structural Observation Triggers

**Skip this step entirely if the structural observation artifact is not loaded.** Skipping has no confidence consequence: absence means structure was not assessed.

These triggers fire on directly observed page structure. They are field-keyed against the structural observation artifact (KB mode), mirroring how Step 1c keys against the performance profile. Run in parallel with pattern matching (Step 2). Structure-driven opportunities join the opportunity list with `signal_source: structural-observation`.

**Normative rules (binding for every trigger below):**

1. **Tri-state evaluation.** `present` fires presence-conditioned triggers and suppresses absence-conditioned ones. `absent` fires absence-conditioned triggers and suppresses presence-conditioned ones. `not_checked` does neither: the pattern may still fire from other sources exactly as it does today.
2. **Structure-vs-behavior boundary (no double-counting).** Structure supplies TARGETS and current-state confirmation. Performance supplies FIRING COUNTS for engagement patterns (EE-02, the EE-03 element leg, the NX-06 depth leg, the NX-07 return-rate leg). A structural field never re-fires a trigger that performance data already fired for the same page; it enriches that opportunity's element targeting instead (the merge happens in Phase 3 Step 8 as usual).
3. **Existence tri-states are observational input only.** For comparison/ROI/pricing existence fields, the firing logic stays competitive- or positioning-driven; the structural field confirms or suppresses the structural leg of the trigger, it does not fire the pattern alone.

| Trigger Condition | Pattern(s) | Example |
|---|---|---|
| Form present with 5+ fields or a high required-field count | FO-01, FO-02 | "Demo form has 13 fields, 11 required. Field reduction or multi-step candidates, confirmed by direct observation rather than inference." |
| Form present with no value reinforcement or trust signals observed near it | FO-03; FO-04 (partial unless field labels were captured) | "Contact form renders with no proof element in its section. Context reinforcement candidate." |
| High `cta_count` on one page OR a generic or high-commitment primary CTA label | NX-02; EE-03 | "Page shows 11 CTAs with equal visual weight; primary label is 'Submit'. Hierarchy and label clarity candidates." |
| `login_present` true AND (`login_above_fold` false OR low nav rank) | NX-07 (structural leg; full trigger only with the performance return-rate leg, else partial) | "Login sits at nav rank 7. With a high return-visitor share this fires fully; without return-rate data it is partial." |
| `sequential_ui_present` true with multiple items | EE-02 (targeting enrichment only; firing requires performance drop-off data) | "Tabs with 5 panels observed on a solutions page. If element data shows later-tab drop-off, this names the exact element to de-bury." |
| `named_client_proof_present: absent` OR low `proof_element_count` on an evaluation-stage page | HM-02, SP-01, SP-02, SP-03 | "Pricing page renders zero named-client proof elements. Proof injection candidates." |
| `team_credibility_present: absent` where expertise is a claimed differentiator | TC-01 | "Services page shows no team credibility surface despite expertise positioning." |
| `objection_faq_present: absent` on a decision-stage page | TC-02 | "No objection-handling content observed on a comparison-stage page." |
| `chatbot_present: present` or an overlay observed over a primary CTA | NX-06 (intervention-leg confirmation; depth leg stays performance-driven) | "Chat widget overlaps the primary CTA on mobile. Confirms the intervention surface for an interference test." |
| Navigation labels do not reflect persona segmentation AND audience context defines 2+ distinct personas (`nav_persona_segmented` false) | NX-01, PS-03 | "Nav is organized by product line while two personas with distinct jobs are defined. IA segmentation candidate." |
| `comparison_page_exists: absent` | CR-01 structural leg confirmed (`present` suppresses CR-01) | "No comparison page observed; competitive context showing 3+ direct competitors supplies the firing condition." |
| `roi_tool_exists: absent` | CR-02 / CR-03 structural leg confirmed (`present` suppresses) | "No ROI or assessment tool observed; proof registry and persona data supply the firing condition." |
| `pricing_page_exists: absent` | PZ-01 structural leg confirmed (`present` suppresses) | "No pricing page observed; competitor pricing transparency supplies the firing condition." |
| Copy skeleton on a service page reads generically against claimed differentiators | PS-04 | "Service page headline could describe any vendor in the category while the claim overlap map shows crowded claims." |

**Trigger evaluation rules:**
- Per-page conditions evaluate off the frontmatter pages digest; read the page's body block when a condition needs detail (labels, ordering, overlay position). Site-level fields evaluate once per run.
- Each structure-driven opportunity uses ICE baseline 3/3/3, the same as context-derived. Direct observation provides current-state evidence for Phase 4 modifiers, never an inflated baseline and never a fabricated performance baseline.
- Out of scope by design: personalization patterns (PE-01, PE-02) need cross-session variance a single capture cannot supply; exit-path patterns (NX-03) need behavioral data; value-before-commitment sequencing (NX-05) is deferred.

**Output:** Structure-driven opportunities added to the opportunity list, tagged `type: "structure-driven"`.

### Step 1f: Measurement Inventory and Staleness Signals

This step has two legs, each skipping with no penalty when its backing artifact is absent (mirroring the skip-with-no-penalty pattern of Step 1c and Step 1e):

- **Measurement-inventory leg:** the performance-profile source skips with no penalty when `performance-profile.md` is absent; the live-capability source (below) still scans the other loaded artifacts. The leg is fully inert only when neither a performance profile nor any artifact documenting a live capability is loaded.
- **Staleness leg:** skip with no penalty when the structural observation artifact is absent.

This step produces no opportunities. It produces three internal annotations carried forward to the validation phase (`phases/validate.md`, Phase 3.5) and to `phases/score.md`: a measurement inventory, a set of staleness signals, and (when present) an FM9 contamination flag. Run it after the trigger steps (1c, 1e) so the inventory can reference the same signal sources they read.

**Measurement inventory (performance-profile.md leg).** Derive two lists from the performance profile's tracked-event inventory and documented data gaps (the same signal sources Step 1 already lists at "Conversion event inventory and per-page funnel data" and "Data gaps noted in Key Metrics Summary"):

- `instrumented_metrics`: metrics the profile reports actual data for (events present in the conversion-event inventory, metrics with per-page values). These are safe to propose as a primary or guardrail metric.
- `dark_metrics`: metrics named in the profile's documented data gaps, or named anywhere in context as a desired metric but absent from the profile's event inventory. These are NOT safe to propose without an instrumentation prerequisite.

A metric appears in exactly one list. When the profile is present but silent on a metric (neither reports data for it nor flags it as a gap), first run the live-capability leg below: if any loaded artifact documents that metric as live, it goes to `instrumented_metrics` (tagged `live-elsewhere`), not `dark`. Only when no loaded artifact documents the capability as live does the conservative default apply: classify it `dark` (unconfirmed instrumentation is treated as not instrumented). Carry both lists forward; `phases/validate.md` `metric_instrumented` gate reads them.

**Live-capability leg (other loaded artifacts).** The measurement inventory is not built from `performance-profile.md` alone. Scan every other loaded silver artifact (a lead-lifecycle / attribution / measurement-reference artifact, strategy or audience context, the structural observation) for a statement that a metric or measurement capability is **live / in production / already reporting / already split per arm**. When found, add that metric to `instrumented_metrics` tagged `live-elsewhere` (instrumented per a non-performance-profile artifact; the residual is per-surface confirmation, not a build), even when the performance profile is silent on it. This leg is what prevents a metric that is live in production but documented outside the performance profile from being dark-defaulted and then mis-rendered as tracking the client must stand up. It skips with no penalty when no such artifact is loaded. A `live-elsewhere`-tagged metric is treated as instrumented by `phases/validate.md` Gate 2, which attaches a per-surface confirmation note rather than an instrumentation-build prerequisite. Read *current status*, not just current shape: a documented "live" / "in production" / "already reporting" status means instrumented, the same status-reading discipline `detect-strategic.md` criterion 7 applies on the strategic lane.

**Staleness signals (structural observation artifact leg).** Detect when the captured current-state may be out of date or contested:

- **Capture-date tagging:** read the structural artifact's capture date (frontmatter capture/observed date). Tag every structural fact with that date so the validation phase can attach a "verify current before launch" prerequisite to any hypothesis whose control depends on a structural fact.
- **Cross-artifact element-disagreement / redesign-in-progress:** when two loaded artifacts describe the same element differently (e.g., the structural capture records a 13-field form on /demo while the performance profile or audience context describes a short form on the same page), record an element-disagreement signal naming the element and the two sources. This is the redesign-in-progress signal: the page may be mid-change, so the captured control is contested.

Carry the staleness signals forward; `phases/validate.md` `control_stable` gate reads them. Per Boundary 2, a broken-render observation (`mobile_render_clean: false`) is NOT a staleness signal: it is CTR-14's rendering-defect reframe and is owned there. Step 1f records ONLY capture-date and element-disagreement signals; it never emits a `mobile_render_clean` signal as staleness.

**FM9 contamination flag (performance-profile.md leg).** When the performance profile documents bot traffic or synthetic-monitoring (uptime/availability pingers, headless-agent traffic) on a surface, extract a contamination flag for that surface: the surface, the contaminated figure (sessions or bounce), and the profile's stated or estimated contaminated share. This flag is carried forward as an opportunity-list annotation for `phases/score.md` to consume (it discounts the contaminated figure BEFORE the Step 4 Impact modifiers). Step 1f produces no opportunity from the flag itself; it only annotates.

**Output:** measurement inventory (`instrumented_metrics` -- including any `live-elsewhere`-tagged metrics from the live-capability leg -- and `dark_metrics`), staleness signals (capture-date tags + element-disagreement signals), and the FM9 contamination flag (when present), all carried forward to Phase 3.5 (validate) and Phase 4 (score). These are internal annotations, never written to disk and never rendered in the deliverable (see SKILL.md `Deliverable Purity Constraint`).

### Step 1g: Experiment-History Triggers

**Skip this step entirely if the experiment-history input is not bound.** Skipping has no confidence consequence: absence means no prior-experiment evidence was available.

These triggers fire on completed, measured experiment results read from the bound experiment-history source -- the external producer's `gold-experiment-index` plus the silver insight records it links, OR the in-output-KB `schema: experiment-history` silver artifact plus the per-experiment gold insight guides it summarizes (KB mode only), per SKILL.md `KB Mode (Dual-Mode Output)` > `Read-side Mapping`. The index is filtered to the run's `--scope` by default; documented cross-scope reads are allowed where a win on one scope legitimately informs another. Run in parallel with pattern matching (Step 2). Experiment-history-derived opportunities join the opportunity list with `signal_source: experiment-history`.

**All-outcome, type-aware minting.** Treat the bound experiment history as a backlog to advance, not just evidence to cite. For each in-scope record (filtered to `--scope` per the scope rule above, with the documented whole-index cross-scope read preserved), iterate the record's `next_experiments`; for **each item** whose `surfaces` map into the run scope AND whose `priority` is `recommended_lead` or `high`, emit one experiment-history-derived opportunity, **regardless of the parent record's `outcome`** (winner, loser, or flat). Items with `priority: medium` are emitted only if `--max` budget remains after Phase 4 tiering (the gate is enforced in `phases/score.md` Step 6; Step 1g emits `medium` items tagged for that downstream cut). Losers and flats carry the richest iteration fuel (discriminating tests, intent-segmentation splits, bolder iterations that the loss recommends); they are no longer skipped.

**Priority derivation for the in-KB prose source (MUST author).** The external producer path reads an explicit `priority: recommended_lead | high | medium` token off each `next_experiments` item. The in-output-KB `schema: experiment-history` source has no such tokens, so without a rubric the minting volume is subjective and non-reproducible. For that source, derive `priority` from the prose per this rubric before applying the minting gate:
- A per-experiment gold insight guide's designated **lead / recommended lead experiment** -> `recommended_lead`.
- A `Next Step` the history record names as its **primary** follow-up -> `high`.
- **Secondary / exploratory** Next Steps or gold-guide mentions -> `medium`.

The derived `priority` then feeds the SAME minting gate as the external path, unchanged: `recommended_lead` / `high` mint immediately; `medium` is emitted tagged for the `phases/score.md` Step 6 `--max`-budget cut. For the in-KB source, `parent_outcome` is derived from the record's `Outcome` prose per the **Outcome normalization table** in SKILL.md `Read-side Mapping` (not a producer `outcome` token), and `history_type` follows that table's posture column. All other minting logic, the all-outcome coverage, and the penalty-free skips are unchanged. Because in-KB-derived opportunities carry the identical provenance labels tagged below (`signal_source: experiment-history`, `history_type`, `parent_outcome`, `source_surfaces`, `source_priority`, ICE baseline 3/3/3), the mechanism-identity dedup predicate in the **Boundary** note below applies to them unchanged; no new dedup logic is added.

Tag each emitted opportunity:
- `type: "experiment-history-derived"`
- `signal_source: experiment-history`
- ICE baseline **3/3/3** (the same neutral midpoint as context-derived and performance-driven opportunities; the empirical validation provides evidence for the Phase 4 modifiers, never an inflated baseline)
- `history_type: <rollout | iteration | follow_up | discriminating_test>` (the producer item's `type`)
- `parent_outcome: <winner | loser | flat>` (the parent record's `outcome`)
- `source_surfaces: <surfaces>` (the item's in-scope target surfaces)
- `source_priority: <recommended_lead | high | medium>` (the item's `priority`)

These provenance fields are the consuming skill's own opportunity-record labels (distinct from the producer's raw silver tokens) and feed `phases/score.md` Step 4 (outcome-aware posture), Step 6 (`--max` within-tier retention), and Step 7 (continuation sequencing). They are analysis-only and are NEVER rendered in the deliverable body (see SKILL.md `Deliverable Purity Constraint`).

**Penalty-free skips.** An `next_experiments` item whose `surfaces` have no in-scope mapping is skipped penalty-free. A record carrying no `next_experiments` at all is skipped penalty-free. Neither skip applies a confidence penalty or a global cap.

**Boundary (same-mechanism merge test).** Experiment-history supplies a continuation TARGET and (for winners) a validated mechanism. An experiment-history-derived opportunity merges with an existing same-page opportunity in Phase 3 Step 8 **only when it is the same mechanism / change-under-test** (a true duplicate); it is emitted as its own first-class hypothesis when the surface is shared but the **test design differs**. **Same surface plus same change = merge. Same surface plus different change-under-test = separate experiment.** Different-design cases that MUST survive dedup: isolation / discriminating arm, intent-segmentation split, dosage / no-default variant, down-funnel-instrumented re-run, and new-surface rollout. The merge itself still executes in Phase 3 Step 8 (`construct.md` `Step 8: Deduplication and Filtering`) as today; only the merge **predicate** narrows from surface-occupancy to mechanism-identity.

**Output:** Experiment-history-derived opportunities added to the opportunity list, tagged `type: "experiment-history-derived"`.

### Step 2: Match Signals Against Patterns

For each signal extracted in Step 1, check against the trigger conditions ("Applies when") in `modules/experiment-patterns.md`.

**Matching rules:**
- A signal can trigger multiple patterns. This is expected and correct.
- A pattern can be triggered by signals from multiple context files. Use the strongest signal.
- If a pattern's trigger condition partially matches (e.g., "form has 5+ fields" and you found a form but can't confirm field count), create the opportunity but flag it as "trigger partially confirmed."
- If `--focus` flag was set, only evaluate patterns in the specified categories.
- **Archetype precedence (only when an archetype module was loaded; see SKILL.md Phase 1 `Archetype resolution`):** Check archetype patterns before base patterns. A base pattern still fires if it full-matches a page + mechanism that no archetype pattern covers. When a base pattern and an archetype pattern match the same page + mechanism, the Phase 3 Step 8 deduplication (`construct.md` `Step 8: Deduplication and Filtering`) merges them; on a tie of trigger strength, the archetype pattern's baseline (`ice_baseline`) wins, because it is more specific to the store type. No archetype module loaded means this rule is inert and matching runs on the base library exactly as before.

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
