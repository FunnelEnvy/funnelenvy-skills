# Phase: Hypothesis Construction

## Required Inputs

- Opportunity list from Phase 2 (detect)
- Full body of all loaded context files (carried forward from Phase 1)
- `modules/experiment-patterns.md` (for causal mechanisms and common mistakes)

## Depth Behavior

This phase does not vary by depth.

## Graceful Degradation

| Condition | Impact |
|-----------|--------|
| No "before" copy available for a copy experiment | Hypothesis is marked "needs site verification" in the roadmap footnotes. Still included but Confidence is capped at 3. |
| No audience-messaging.md for "after" copy | Adapt from L0's stated value propositions and differentiators instead. Note reduced specificity. |
| Partial trigger (from Phase 2) | Include hypothesis but add footnote recommending manual verification of the trigger condition before testing. |

---

## Experiment Scope Rule

**The unit of testing is the hypothesis, not the variable.**

This is not a traffic optimization. It is correct experiment design. An experiment tests whether a strategic idea works. Page elements (headline, subhead, proof strip, CTA copy, form structure, testimonial placement) are not independent ideas. They are components of an idea. Testing them separately does not tell you whether the idea works, because the untouched elements may be undermining or distorting the result.

Example: if you test a differentiation-led H1 while the subhead still says "faster, with better results," you have not tested differentiation-led messaging. You have tested one line of differentiation-led copy in a generic context. A loss is uninterpretable: did differentiation fail, or did the generic subhead dilute it?

**Bundling rule:** When multiple page elements all serve the same testable idea, they MUST be combined into a single experiment variant. You are testing whether a messaging strategy, proof approach, or structural pattern works. Not which DOM element contributed most.

**Examples of correct bundling:**
- Hypothesis: "Differentiation-led messaging outperforms generic category language" -> Change the H1, subhead, and hero CTA copy together. One experiment.
- Hypothesis: "Customer-attributed proof increases trust on evaluation pages" -> Add proof strip, logo bar, and testimonial quote together. One experiment.
- Hypothesis: "Reducing form friction increases completion" -> Multi-step form, progress indicator, value reinforcement, and field reduction together. One experiment.

**Examples of incorrect splitting:**
- "Test H1 first, then test subhead separately, then test CTA" when all three serve the same hypothesis. You have not tested the hypothesis. You have tested fragments of it in hostile contexts.
- "Test proof strip on /pricing first, then separately on /hire-tech-candidates" when the hypothesis is identical. Run on both pages simultaneously.

This constraint applies throughout the construction process below. When evaluating opportunities from Phase 2, actively look for opportunities targeting the same page with the same underlying hypothesis and merge them before constructing individual experiments.

**Strategic-unit allowance.** The unit of testing may be a program, offer, audience-motion, or asset, not only a page element. The bundling discipline is unchanged and applies within each lane: bundle the elements (or the asset plus its placement plus its supporting copy) that serve one strategic idea into one experiment; do not bundle two independent strategic ideas. A strategic experiment's "elements" are its intervention components (the asset, where it is published, the routing change), and the same one-nameable-failure-mode test governs whether they are one experiment or several.

- Correct strategic bundling: "A named-client ROI proof asset raises the qualified-demo rate" -> build the ROI one-pager, publish it on the evaluation pages, and add the supporting proof copy that frames it, measured as one experiment via a holdout. The asset, its placement, and its framing serve one idea, and a flat qualified-demo rate is one nameable failure of that idea. Do not fold an unrelated speed-to-lead routing change into the same experiment; that is a second strategic idea with its own failure mode.

**Cross-surface bundling rule.** Bundle elements that serve one idea on the same page or section. Across different surfaces, bundle only if a single failure mode can be named for a combined loss. If a combined loss would list three or more independent things that could have failed on different surfaces, sequence the experiments instead of bundling them. A bundle whose loss-analysis cannot name one failure mode is not one experiment; it is several wearing one name. (This rule is shared verbatim with `modules/hypothesis-interactions.md` > `Same-Page Interaction Analysis Process`; keep the two copies in sync.)

---

## Pre-Construction Red-Flag Checks

Run these before building any hypothesis. Each check targets a class of errors that produces plausible-looking but invalid experiments.

### Form experiments

**Before proposing any form swap or form variant test:** confirm the two forms are not identical in content, fields, and structure. Forms that share the same fields under different names (e.g., "AI Hub Form" vs "AI Solutions Form" pointing to the same Marketo/HubSpot form ID) cannot be A/B tested against each other - there is no variant. If the forms are identical, discard the form swap hypothesis and redirect to form placement, two-step flow, or CTA label tests instead.

### Mobile bounce rate hypotheses

**Before attributing mobile bounce to a technical or rendering failure:** check traffic source composition for mobile in `performance-profile.md`. If one channel represents more than 60% of mobile traffic and that channel has a high bounce rate across ALL devices (e.g., direct traffic bounces at 60%+ on desktop too), the mobile bounce rate is a messaging problem for that channel, not a rendering problem. The fix is the same messaging intervention as desktop, not a Core Web Vitals or layout audit. A 9x device bounce gap does not by itself indicate a technical problem - it indicates the dominant mobile channel is failing for the same reason it fails on desktop.

**Structural render check (when the structural observation artifact is loaded):** read `mobile_render_clean` for the target page before constructing any mobile hypothesis. `false` (broken render, console errors, or failed requests observed on the mobile viewport): do NOT construct an A/B test; route the item to fix-and-monitor, consistent with CTR-14's gate, with a note that the rendering defect must be fixed and the device gap re-measured before any messaging or layout test is interpretable. `true` (clean render directly observed): the rendering-defect explanation is ruled out, and the mobile hypothesis proceeds as a layout, content, or messaging test. Field not assessed for the target page: the channel-composition check above governs alone.

### Conversion path selection bias

**Before proposing routing changes based on a higher-converting dedicated page or path:** check absolute volume. A dedicated form page that converts at 5x the rate of the embedded form may simply be receiving self-selected higher-intent visitors who navigated there deliberately. The higher CVR reflects visitor intent, not page quality. The correct experiment is reducing friction on the primary path (two-step form, progressive disclosure), not routing all traffic to the dedicated page. Flag this distinction in the hypothesis: is the mechanism "better page" or "higher-intent visitor"?

### CVR vs completion rate

**Always distinguish:**
- **Completion rate** = submits / form initiates. Measures how well the form converts visitors who started it.
- **CVR (conversion rate)** = submits / page visitors. Measures how many visitors the page converts end-to-end.

A 47% completion rate with a 0.076% CVR means the form works once started but almost no one starts it. The bottleneck is initiation, not completion. Optimizing form fields (completion) when the problem is form initiation is solving the wrong problem. Always state both metrics when discussing form performance and specify which one the experiment targets.

---

## Construction Process

### Step 1: Page and Element Identification

For each opportunity, identify the specific page and element the experiment targets.

**Specificity requirements:**
- Page must be named (e.g., "Homepage," "Pricing page," "/solutions/enterprise"), not categorized ("a landing page")
- Element must be identified (e.g., "Hero headline," "Primary CTA," "Lead capture form," "Navigation menu"), not vague ("the top of the page")
- If the exact page can't be determined from context, use the most likely page based on the pattern's typical deployment and note the assumption

**Site-wide scope check (when the structural observation artifact is loaded):** if `form_recurs_sitewide` is true and the hypothesis targets the recurring form, the experiment target is the full set of form instances site-wide, named as such (e.g., "the global demo-request form, all instances"), not a single page; a per-page form hypothesis on a site-wide form understates both reach and implementation surface. Likewise, if `sitewide_primary_cta_label` is set and the hypothesis tests CTA verb or label, the target is the site-wide CTA instance set. For performance-fired engagement opportunities (EE-02, EE-03, NX-06) on pages the structural observation covers, use the observed element identifiers (sequential UI items, CTA labels, overlay tooling) to name the exact element: observation satisfies the specificity requirement directly, where inference only approximates it.

### Step 2: Current State Documentation

Document what exists now. This is the control in the experiment.

**For copy experiments:**
- Pull exact copy from company-identity.md's Homepage Messaging section, stated differentiators, or proof points
- If exact copy isn't available, describe the observed pattern ("Homepage headline uses category language rather than outcome language")
- NEVER fabricate current-state copy. If you don't have it, say what you know about it

**For structural experiments:**
- Describe the current layout, form structure, navigation pattern, or page architecture based on what context files reveal
- Flag when your understanding of current state is inferred rather than directly observed
- When the structural observation artifact covers the target page, the current state is directly observed: cite the observation (field counts, CTA labels, element presence) and do not flag it as inferred
- **Do not assume a page has no conversion mechanism just because context files don't mention one.** Context files may not document every form, CTA, or interactive element. When claiming "no conversion path exists" for a page, note that this is based on available context and may need verification. If performance-profile.md shows 0 conversions for a page, that could mean no mechanism exists OR that an existing mechanism is not firing/tracked. State the ambiguity rather than asserting absence.

**For personalization experiments:**
- Document the current one-size-fits-all experience: what all visitors see regardless of segment

**Baseline data (when performance-profile.md exists):**
- Look up the target page in performance-profile.md's Page Performance and Conversion Events sections
- Record: sessions/mo, bounce rate, conversion rate (for primary conversion event), and top traffic source
- This data populates the `**Baseline:**` line in the deliverable template
- If the target page doesn't appear in performance-profile.md (low traffic or not tracked), note "No baseline data for this page" and skip the Baseline line
- The structural observation artifact never supplies baseline metrics. Baseline lines come only from performance data; structure supplies current-state facts and element identity, exactly as before

### Step 3: Proposed Change

Define the specific variant to test.

**Rules:**
- One hypothesis per experiment. Multiple elements (headline, subhead, CTA, proof strip) can change in a single experiment as long as they all serve the same hypothesis. Don't artificially constrain variants to a single DOM element -- constrain them to a single testable idea. See the **B2B Experiment Design Constraint** section above: the unit of testing is the hypothesis, not the variable.
- Proposed changes must be grounded in context. For copy changes, adapt from audience-messaging.md channel adaptations, value themes, or persona-specific messaging. For structural changes, apply the pattern's typical test from experiment-patterns.md.
- Do NOT invent new creative from scratch. The proposed change should be traceable to either the pattern library or the messaging analysis.
- Be concrete enough that a developer or copywriter could implement the variant without clarifying questions.

**For copy experiments, produce before/after pairs:**

```
Before: "The Revenue Intelligence Platform for Modern Sales Teams"
After: "Close 40% More Deals by Knowing What Your Buyers Actually Want"
```

The "before" comes from context files. The "after" adapts messaging from audience-messaging.md. If audience-messaging.md doesn't exist, adapt from L0's strongest proof points and value propositions.

### Step 3b: Multi-Variation Copy

**Scope:** This step applies ONLY to hypotheses in categories `headline`, `hero`, `positioning`, or `value-proposition`. For all other categories (form, layout, navigation, personalization, pricing, social-proof, content, trust, element-engagement), skip this step and keep the single before/after from Step 3.

For qualifying hypotheses, produce **2-3 variation pairs** instead of a single proposed change. A strategist needs options anchored to different strategic directions because they have client context the skill cannot see.

**Each variation must:**

1. Anchor to a different element of the brand positioning architecture. Pull anchors from:
   - Verified differentiators from the positioning scorecard
   - Value propositions from L0
   - Channel adaptations from audience-messaging.md
   - Competitive white spaces from competitive-landscape.md
   - Proof points from L0 registry (one proof point per variation to avoid braiding)

2. Use a different lead strategy. Example anchors:
   - **Specialization-led:** What only this company does
   - **Proof-led:** Lead with the strongest verified number
   - **Outcome-led:** Transformation promised to the buyer
   - **Positioning-statement-led:** Brand positioning statement verbatim or closely adapted
   - **Exclusivity-led:** What this company has that others cannot replicate

3. Be internally consistent. If the hypothesis bundles H1 + subhead + CTA (per the Experiment Scope Rule), all three elements within a single variation must work together under the same strategic anchor.

4. Be concrete enough that a developer or copywriter could implement without clarifying questions.

**Output format (replaces the single before/after block from Step 3 for qualifying categories):**

```
variations:
  - id: A
    anchor: "[strategic anchor label]"
    source: "[audience-messaging section, L0 proof point, or competitive white space reference]"
    copy:
      h1: "[proposed headline]"
      subhead: "[proposed subhead, if hypothesis bundles it]"
      cta: "[proposed CTA, if hypothesis bundles it]"
  - id: B
    anchor: "[different strategic anchor]"
    source: "[different reference]"
    copy:
      h1: "[proposed headline]"
      subhead: "[proposed subhead]"
      cta: "[proposed CTA]"
  - id: C  # optional, only when a genuinely distinct third angle exists
    anchor: "[third strategic anchor]"
    source: "[third reference]"
    copy:
      h1: "[proposed headline]"
      subhead: "[proposed subhead]"
      cta: "[proposed CTA]"
recommended_variation: "[A|B|C]"
recommendation_reason: "[1-2 sentences: strongest verified proof, lowest legal risk, best alignment with scorecard gaps, etc.]"
```

**Do not pad.** Two strong variations beat three where the third is a word swap. Only include Variation C when a genuinely distinct third strategic angle exists.

**Trade-off notes.** For each variation, state what it optimizes for and what it trades off in 1 sentence. Example: "Variation C activates the brand positioning statement verbatim but asks readers to accept abstract framing before committing."

### Step 3c: Protected Brand Element Handling

Check each proposed variation (from Step 3 or Step 3b) against the protected brand elements flagged in detect.md Step 1b (flag type 5).

**Skip condition:** If detect.md produced no protected brand element flags, this step is a no-op.

**For each variation:**

1. Identify whether the variation preserves or removes/modifies any protected element.

2. **Legal or regulatory protection:** Hard block. The variation cannot modify this element. Either rewrite the variation to preserve the element or suppress the variation entirely. If the hypothesis is fundamentally about changing a legally protected element, route to Prerequisites with the note: "Requires legal review before testing."

3. **Brand protection:** Soft warning. The variation can propose the change but must carry a flag. When ANY variation removes a brand-protected element, require at least one additional variation that preserves it. The strategist must have both options.

4. Mark variations that remove protected elements with `removes_protected_element: [term]`.

5. Add to hypothesis notes:

   ```
   Protected brand element detected: [term]
   Protection type: [legal | brand | regulatory]
   Source: [file and section]

   [Variation A] preserves this element.
   [Variation B] removes this element.

   Client confirmation recommended before testing variations that remove
   brand-protected elements. The term may reflect executive mandate, board
   guidance, or investor narrative commitments not visible in written context.
   ```

6. For `brand` protection, present both preserving and removing variations equally and defer to strategist judgment. For `legal`/`regulatory` protection, default recommendation must preserve the element.

**Output field added to hypothesis record:**

- `protected_elements_affected`: array of `{element, protection_type, action_taken: "preserved"|"removed"|"blocked"}` (empty array if no protected elements are involved)

### Step 4: Causal Mechanism

Every hypothesis requires a "why." This is the CRO reasoning that separates a rigorous hypothesis from a guess.

**Structure the causal chain:**
1. **Observation:** What specific condition exists now (from context)
2. **Principle:** What behavioral, psychological, or UX principle applies
3. **Prediction:** What change in behavior the variant should produce
4. **Metric:** How that behavior change manifests in measurable terms

The Prediction must carry a read threshold, not just a direction. State the condition under which the variant ships and the condition under which it is abandoned. For proxy-only scopes with no CVR baseline, the honest form is: "ship if the variant proxy beats control by the test's MDE at full sample; abandon if flat at full sample." Do not fabricate a point estimate ("+X%") when no baseline supports one. This read threshold renders in the deliverable as the `Expected effect and read threshold` line.

**Example:**
> Visitors from paid search land on the homepage and see a category-defining headline ("Revenue Intelligence Platform"). These visitors already know the category: they searched for it. Repeating category language wastes the highest-attention moment on information they already have. Replacing with outcome language ("Close 40% more deals") immediately communicates value, reducing bounce rate and increasing demo request clicks. The primary metric is demo request rate; secondary metric is bounce rate.

**Causal mechanism quality check:**
- Does it reference a specific behavioral principle? (cognitive load, commitment bias, social proof, loss aversion, etc.)
- Is the prediction falsifiable? (If you can't imagine a negative result, the mechanism is too vague)
- Does it connect the change to a measurable metric through a logical chain?

Pull the causal mechanism from the matched pattern in `modules/experiment-patterns.md` as a starting point, then adapt to the specific context. Don't copy the pattern's mechanism verbatim when the specific context adds nuance.

**LIFT Classification:**

Classify the hypothesis into exactly one LIFT category based on what conversion barrier it addresses:

| LIFT Category | Conversion Barrier | Sequence Priority | Examples |
|---|---|---|---|
| Relevance | Page content doesn't match visitor intent or traffic source promise | 1 (highest) | Ad-message mismatch, keyword-headline disconnect, wrong audience landing on page |
| Clarity | Value proposition is present but unclear, buried, or poorly communicated | 2 | Vague headlines, feature-first framing, confusing page hierarchy, jargon |
| Anxiety | Visitor understands the value but perceives risk in taking action | 3 | Missing trust signals, no social proof near form, unclear post-submit experience, privacy concerns |
| Distraction | Competing elements dilute attention from the primary conversion path | 4 | Multiple CTAs, navigation on landing pages, secondary offers, visual clutter |
| Urgency | No reason to act now rather than later | 5 (lowest) | No time-bound element, no cost-of-delay framing, no capacity signal |

**Classification rules:**
- A hypothesis addresses the EARLIEST barrier in the chain where the problem exists. If the page has a relevance problem AND a clarity problem, both hypotheses are classified correctly (Relevance and Clarity respectively). The LIFT ordering ensures the Relevance hypothesis runs first.
- If a hypothesis addresses multiple barriers (e.g., ATF overhaul that fixes both clarity and distraction), classify by the primary barrier. The primary barrier is the one that, if fixed alone, would produce the larger conversion impact.
- Urgency hypotheses in enterprise B2B contexts should already be caught by the contrarian filter (CTR-05). Any urgency hypothesis that survives the filter is genuine (e.g., budget-cycle alignment, cohort-based enrollment).

Add the `lift_category` field to the hypothesis record: one of `relevance`, `clarity`, `anxiety`, `distraction`, `urgency`.

### Step 4b: Proof Point Integrity Check

Before finalizing any hypothesis whose proposed change or causal mechanism references a statistic, percentage, or specific proof point from L0, verify the claim against the proof point registry in `company-identity.md`.

**Verification process:**

1. **Locate verbatim.** Match the proposed claim against L0's proof point registry. The number AND the source language must be traceable to a single registry entry. If the registry has P2 = "32% of members not active on generalist career sites" and P26 = "46% have not indicated active job searching on LinkedIn, Indeed, Monster, ZipRecruiter, CareerBuilder," these are separate claims with different scopes. Do not combine them.

2. **Verify scope match.** The claim being made in the proposed copy must match the proof point's scope. Example: P2 uses "generalist career sites" (plural, generic). If the proposed copy names specific competitors (e.g., "not on LinkedIn or Indeed"), the scope has shifted beyond what P2 supports. The copy must be rewritten to match the registry language or cite a different proof point that supports the specific claim.

3. **Check for proof braiding.** If the proposed copy combines elements from two or more proof points into a single sentence or claim, set `proof_braid: true`. Require explicit justification: both proof points must independently support the combined claim. If they do not, split into separate variations (if Step 3b applies) or rewrite to align with one source.

4. **Comparative advertising check.** If the proposed copy names specific competitors or uses language like "unlike [competitor]" or "compared to [competitor]," set `comparative_advertising: true`. Add this note to the hypothesis record: "Comparative claim naming [competitors]. Legal review recommended before launch. Lanham Act and FTC comparative advertising standards apply."

**Output fields added to hypothesis record:**

- `proof_integrity_passed`: `true` if all referenced proof points are verified or supported in the registry and scope matches. `false` if any claim is unverifiable, scope-shifted, or braided without justification.
- `proof_braid`: `true` if the proposed copy combines elements from 2+ proof points. `false` otherwise.
- `comparative_advertising`: `true` if the copy names specific competitors. `false` otherwise.

**Fail states:**

- If `proof_integrity_passed` is false: the hypothesis remains in the roadmap but Confidence is capped at 3 (cannot score higher without verified proof). The specific unverifiable claims are added to Prerequisites and Data Gaps (Phase 4 Step 8) under "Context Verification Needed."
- If `comparative_advertising` is true and the cited proof point has strength "claimed" (not "verified"): add a hard gate note: "Comparative claim with unverified data. Must verify before deployment."

**Skip condition:** If the hypothesis does not reference any quantified claims or proof points (e.g., a layout or form experiment), this step produces no output. Set `proof_integrity_passed: true` by default for non-proof-dependent hypotheses.

### Step 4c: Measurement Design (strategic-lane hypotheses)

**This step applies only to `lane: "strategic"` hypotheses.** Tactical hypotheses (pattern-matched and context-derived) skip it; their measurement is the standard on-page A/B handled by Step 5b. A strategic hypothesis carries a candidate `measurement_design` from Phase 2c; here you finalize it.

Select an explicit `measurement_design` from this enum:

- `randomized_ab` (on-page A/B). Still the default when the lever happens to be on-page-testable (e.g., a proof asset placed on a high-traffic evaluation page).
- `holdout` (a randomized or matched group that does not receive the intervention).
- `pre_post` (before/after the intervention goes live, same population).
- `cohort` (compare cohorts defined by entry period or segment).
- `geo_split` (region split: some regions get the intervention, others do not).
- `switchback` (alternate the intervention on and off over time windows).
- `operational_metric` (track an operational metric directly, e.g., speed-to-lead, where the intervention is a process change rather than a page variant).

For the selected design, state all of:

1. **The design**, named in plain terms.
2. **The business metric it reads** (qualified pipeline, qualified-demo rate, stage progression, retention, speed-to-lead), distinct from a page-level micro-conversion.
3. **The read condition and window** (how long the design needs to run and what counts as a read).
4. **The design's honesty limits**: what it can and cannot causally isolate. Name the specific threat (pre/post seasonality and concurrent-change confounds; holdout contamination or matching error; cohort composition shifts; geo heterogeneity). This is the strategic analogue of Step 5a's proxy-guardrail honesty: state the limit, do not hide it.

**Baseline-reliability design check.** Before finalizing `pre_post`, `cohort`, or a matched holdout, check the loaded performance context for an affirmative unreliable-baseline statement bearing on the comparison window (the same conditions `phases/validate.md` Strategic Gate 1 reads). If one exists, do not finalize a design that consumes the disqualified baseline: re-finalize toward a forward-only read, a randomized `holdout`, `geo_split`, `switchback`, or `operational_metric`. Only when no alternative design can read the lever does the original design stand, with the gate's Confidence cap and a read condition that names the comparison window as directional only. The gate improves the experiment where it can; it caps the score only where it must.

**Confirm-first sequencing shape.** When the hypothesis record carries `confirm_first: true` (from `phases/detect-strategic.md` criterion 7, the context-is-silent state), the stand-up dependency list begins with the existence check: verifying whether the capability already exists in the named client-side system is sequenced as step one, the build is conditional on that check finding nothing, and the read window starts only after the check resolves. Render the check in natural language per the SKILL.md template line, never as a field token.

**Two-stage reads.** When a lever honestly reads at two stages (a randomized on-page read available now, plus an operational or qualified-layer read that becomes available once a Measurement Foundation stand-up lands), finalize the single `measurement_design` token for the readable-today primary leg and describe the second leg in prose as a Foundation-gated enrichment of the read; never invent a second design token.

Record `measurement_design` on the hypothesis record (internal field; it renders in the deliverable as natural language only, per the Deliverable Purity Constraint, e.g., "Measurement: regional holdout, 8-week read"). When the finalized design is `randomized_ab`, the hypothesis proceeds through Step 5b's standard A/B feasibility formula like any tactical hypothesis.

### Step 5: Target Metric and Audience

**Metric selection:**
- Primary metric: The most direct behavioral indicator of the hypothesis being correct
- Secondary metric (optional): A leading or lagging indicator that adds context
- Avoid vanity metrics. "Page views" is almost never the right primary metric.
- When performance-profile.md exists, reference the current baseline for the target metric. Example: "Primary metric: demo request rate (currently 1.2% on this page, 1.97% site-wide)." This grounds the expected improvement in reality.

**Audience identification:**
- If the experiment targets a specific persona from audience-messaging.md, name them
- If the experiment applies to all visitors, say "all visitors"
- For personalization experiments, specify both the targeting criteria and the segment

**Segmentation pre-registration (FM6).** Decide the primary read audience HERE, before scoring, not at the post-hoc "if inconclusive" path (Step 6). When the performance profile shows the persuadable audience is a diluted minority of the page's traffic, pre-register the primary read as that segment rather than running all-visitors and hoping to rescue a flat result by segmenting afterward.

Pre-register the segment as the primary read when ANY of these dilution thresholds holds for the target surface (thresholds are one-engagement heuristics per `modules/ice-scoring.md`; treat them as defaults, not constants):
- Direct traffic > 75% of the surface's sessions (the page is dominated by audience whose intent the experiment is not built for).
- Bounce rate > 60% on the surface (most arrivals never see the stimulus, so an all-visitors denominator dilutes the effect).
- New visitors > 80% of the surface's sessions when the mechanism depends on familiarity or return behavior (or, symmetrically, a returning-user mechanism on a >80%-new surface targets a minority).
- The causal mechanism is sub-audience-only by construction (a returning-user login fix on a page whose audience is overwhelmingly new; a procurement-stage proof asset on a top-of-funnel page).

When a segment is pre-registered:
- Name the segment as the primary read audience and state the dilution signal that justified it ("primary read: paid-search arrivals; Direct is 81% of this surface and is not the audience this hypothesis addresses").
- The segmented (not pooled) denominator is what `Step 5b (Test Feasibility)` powers against. Carry the segment forward so Step 5b uses it.
- A pre-registered segment that CANNOT be isolated or instrumented (no way to deliver the variant to only that segment, or no way to read the metric for that segment alone) becomes an instrumentation block: route it to Prerequisites and carry it forward; `phases/validate.md` `segmentation_satisfied` gate fails on it.

**Viewport / scroll-reach dilution flag.** When the thesis-bearing stimulus sits below the fold (a proof strip, a section heading, a secondary CTA that most visitors never scroll to), flag it: an all-visitors denominator dilutes a below-fold stimulus because most of the denominator never saw it. If structural or element-interaction data shows the stimulus's scroll-reach or view rate, state it; otherwise flag the risk for the feasibility note. This flag does not by itself pre-register a segment, but it feeds the same dilution concern into Step 5b's denominator choice and into the bundle-interpretability check (Step 5c).

This pre-registration adjusts WHERE segmentation is decided (up front, as the primary design) rather than removing the Step 6 inconclusive-path `segment_check`. The Step 6 segment_check stays: it remains the fallback for hypotheses correctly run all-visitors that still come back flat.

### Step 5a: Proxy Metric Guardrails

Classify the primary metric selected in Step 5.

**Metric classification:**

| Class | Definition | Examples |
|-------|-----------|----------|
| **Direct** | Directly measures the hypothesis outcome | Demo request rate, form submission rate, purchase completion |
| **Proxy** | Leading indicator that correlates with but does not directly measure the outcome | CTA click-through rate, pricing page navigation rate, scroll depth past key section |
| **Vanity** | Looks good but has no validated causal relationship to business outcomes | Raw page views, time on page (without qualification), social shares |

**Rules:**

1. **Vanity metrics are rejected.** If the primary metric is classified as Vanity, replace it with the nearest Direct or Proxy metric. Do not leave a vanity metric as primary under any circumstances.

2. **Proxy metrics require guardrails.** When a Proxy metric is the primary (common for low-traffic pages or early-funnel experiments):

   a. Name the downstream Direct metric the proxy is expected to predict. Example: "CTA click-through rate proxies for demo request completion."

   b. Add a guardrail metric: a business-outcome metric that must not degrade for the proxy win to be valid. Example: "Guardrail: demo request rate must not decrease by more than 10% relative."

   c. State the decision rule. Choose one:
      - **Additive:** "Win = proxy up (stat-sig) AND guardrail not significantly down."
      - **Guardrail-primary:** "Win = guardrail up (stat-sig) even if proxy flat or down. Proxy is a leading indicator; guardrail is ground truth."

   d. Document filter risk when the experiment might change traffic composition:
      ```
      Proxy metric risk: This change may reduce [proxy metric] by filtering
      wrong-fit traffic while improving [guardrail metric] for right-fit traffic.
      Do not declare loss on proxy alone. Do not declare win on proxy alone
      if guardrail is flat or down.
      ```

   e. If no evidence exists that the proxy predicts the guardrail on this page, add to Prerequisites: "Validate leading-indicator relationship between [proxy] and [guardrail] on [page] using historical data before treating proxy-win as conclusive."

3. **Direct metrics need no guardrails.** Optionally add a quality guardrail (e.g., if primary is "form submission," guardrail might be "SQL rate from submissions" to guard against low-quality conversion inflation). Not required.

**Output fields added to hypothesis record:**

- `metric_classification`: `"direct"` or `"proxy"`
- `guardrail_metric`: metric name (null for direct metrics)
- `proxy_correlation`: description of expected relationship (null for direct metrics)
- `decision_rule`: `"additive"` or `"guardrail_primary"` (null for direct metrics)
- `filter_risk_note`: filter risk description (null when not applicable)

### Step 5b: Test Feasibility Estimation

**Skip this step entirely if `performance-profile.md` is not present.**

**Non-A/B measurement-design branch (strategic-lane hypotheses).** If the hypothesis carries a non-A/B `measurement_design` (holdout / pre_post / cohort / geo_split / switchback / operational_metric, from Step 4c), do NOT run the two-proportion z-test below and do NOT auto-route it to "What's Not Here" for failing an A/B formula it was never meant to satisfy. Instead, state the design's feasibility in its own terms: data availability for the holdout or baseline, the length of the pre/post window, the instrumentation the operational metric needs, and a defined read window. A measurable strategic lever is feasible if its design can be stood up and read; it routes to a tier, not to "What's Not Here." Keep the A/B formula below intact for `randomized_ab` and for all tactical hypotheses. The 7-day-minimum and 100-conversions-per-variant hard gates apply only to designs that produce per-variant conversion counts (A/B and switchback); for pre/post, cohort, and operational-metric designs, replace those gates with a "sufficient pre-period baseline plus a defined read window" feasibility statement.

For each hypothesis that has a Baseline (from Step 2), estimate whether the target page has enough traffic to run a statistically valid A/B test.

**Formula (standard two-proportion z-test, 80% power, 95% significance):**

```
n_per_variant = 16 * p * (1 - p) / (p * relative_mde)^2
duration_weeks = (K * n_per_variant) / (monthly_sessions / 30) / 7
```

Where:
- `K` = number of test arms (control + variants). For standard A/B tests: K = 2. For multi-variation hypotheses (Step 3b produced 2-3 variations): K = number of variations + 1. Using all variations in a single test requires more traffic; if duration becomes infeasible, note that running variations sequentially as separate A/B tests is an option.
- `p` = current conversion rate for the target page (from Baseline data). If Step 5a classified the primary metric as `proxy`, use the proxy metric's baseline rate, not the downstream direct metric's rate.
- `relative_mde` = 0.15 (15% relative minimum detectable effect). Not configurable. Conservative for CRO.
- `monthly_sessions` = sessions for the target page from performance-profile.md, normalized to 30 days if the profile's date range differs

**Power-check extension (FM3).** The base formula above powers the primary metric on the pooled page denominator. Extend it on three axes so the power determination matches the actual test design:

1. **Guardrail / secondary metric.** When Step 5a named a guardrail metric (proxy-primary hypotheses) or Step 5 named a secondary metric the read depends on, run the same z-test for that metric's base rate. A test that is powerable on the proxy but cannot read its guardrail within the window is not actually decidable: report the guardrail's separate duration, and if the guardrail is unpowerable, say so explicitly ("primary powerable in ~6 weeks; guardrail [metric] unpowerable at this traffic, so a proxy win cannot be validated against it here").
2. **Segmented (not pooled) denominator.** When Step 5 pre-registered a segment as the primary read (FM6), set `monthly_sessions` to the segment's sessions, NOT the page's pooled sessions. Powering a segmented read on the pooled denominator overstates feasibility. State the denominator used ("powered on paid-search arrivals: ~1,200 sessions/mo, not the 6,400 pooled").
3. **Explicit MDE or "unpowerable".** Emit a per-variant determination, not just a tier label: either the per-variant MDE achievable in the window ("~6 weeks to detect a 15% relative lift at 5,600 samples/variant") OR an explicit "unpowerable on the thesis metric at current traffic" when no feasible/extended window reaches a readable per-variant sample on the primary metric (or on the segmented denominator). The `phases/validate.md` `powerable` gate consumes this determination: an "unpowerable" thesis metric fails the gate and `score.md` Step 5b routes it to "What's Not Here."

The 100-conversion and 7-day hard gates below stay intact and apply on top of the extension. The extension changes WHAT is powered (guardrail too, segmented denominator) and WHAT is emitted (explicit MDE or unpowerable); it does not relax the hard gates.

**Feasibility tiers:**

| Duration | Label | Action |
|----------|-------|--------|
| <= 4 weeks | **Feasible** | No annotation needed beyond the Test Feasibility line |
| 5-12 weeks | **Extended** | Add note: "Consider micro-conversion metric for faster signal" |
| 13-26 weeks | **Challenging** | Add note: "Consider proxy metric or pre/post analysis" |
| >26 weeks OR <100 sessions/mo | **Infeasible** | Route to "What's Not Here" with explanation. Do not include in roadmap. |

**Output format (added after the Baseline line in the deliverable):**

```markdown
**Baseline:** 5,600 sessions/mo, 38.5% bounce, 3.0% CVR
**Test Feasibility:** ~8 weeks at 15% MDE (2 variants, 5.6K samples/variant). Extended. Consider micro-conversion metric for faster signal.
```

**Edge cases:**
- **CVR available:** Compute duration normally using the page's conversion rate for the primary conversion event.
- **CVR not available but a variant-instrumented proxy is definable:** Estimate feasibility on the proxy metric's expected base rate and the surface's traffic. Output: "~N weeks on [proxy] at this traffic." Do not output "Cannot estimate" when a proxy is instrumentable.
- **CVR not available and no proxy is instrumentable:** Output: "Cannot estimate (no conversion rate baseline). If testing engagement metric, feasibility depends on effect size."
- **No performance data at all:** Omit both Baseline and Test Feasibility lines (same as current behavior for Baseline).
- **Page not in performance-profile.md:** Omit Baseline and Test Feasibility (page has insufficient data).

**Hard gates (check before finalizing any hypothesis):**
- **100 conversions per variant minimum.** Below this threshold, effect sizes are unreliable regardless of statistical significance. If the page cannot produce 100 conversions per variant within the feasibility tier's time window, route to the next longer tier or to "What's Not Here" with a traffic requirement note.
- **7 days minimum test duration.** One full business cycle to capture day-of-week variation. Never declare a result before 7 days regardless of sample size.
- **Low-traffic page prioritization conflict.** If 3+ hypotheses in the roadmap target the same page with <500 sessions/mo, flag as a prioritization conflict. Only the highest-ICE hypothesis should run; others queue behind it. Note in sequencing: "Page [X] supports only one concurrent test at current traffic levels. [Hypothesis A] runs first; [B] and [C] queue."

**Infeasible routing:** Mark infeasible hypotheses with `feasibility: "infeasible"` and the reason. These are passed to Phase 4 for routing to "What's Not Here" instead of ICE scoring.

### Step 5c: Bundled Variable Disclosure

**This step complements the Experiment Scope Rule (top of this document). Bundling multiple elements that serve one hypothesis remains correct and required. This step adds transparency about what the bundled test can and cannot isolate, so stakeholders understand the tradeoff. It never suggests unbundling as the default action.**

Count the distinct page elements being changed in the hypothesis:
- Headline (H1)
- Subhead
- Primary CTA copy
- Primary CTA destination
- Hero image or visual
- Layout or structural changes
- Social proof elements (testimonials, logos, stats)
- Form fields or form structure

**If `changed_elements_count == 1`:** Set `bundled_test: false`. No additional disclosure required. Proceed to Step 6.

**If `changed_elements_count > 1`:** Set `bundled_test: true` and produce the bundled variable disclosure:

```
bundled_test: true
changed_elements:
  - element: "[e.g., Headline (H1)]"
    role: "primary"  # the element most directly testing the hypothesis
  - element: "[e.g., Subhead]"
    role: "supporting"  # changed to maintain consistency with the primary change
  - element: "[e.g., Primary CTA copy]"
    role: "supporting"
bundled_disclosure:
  bundling_rationale: "[Why these elements must change together. Reference the Experiment Scope Rule: they serve one testable idea.]"
  will_teach: "[What the bundled test definitively proves or disproves about the hypothesis.]"
  wont_teach: "[Which individual element contributions cannot be isolated. This is a known limitation, not a flaw.]"
  unbundling_criteria: "[Under what conditions follow-up element-level tests would make sense. Typically: only after the bundled test wins and the team wants to optimize individual components.]"
```

**Relationship to the Experiment Scope Rule:** The Scope Rule says "the unit of testing is the hypothesis, not the variable." This disclosure operationalizes that principle by making the bundling rationale explicit. If you cannot articulate a single unified idea that all changed elements serve, the hypothesis may actually be two hypotheses. In that case, split per the Scope Rule, not per this disclosure step.

**Bundle interpretability check (FM7).** Beyond documenting the bundle, verify the bundle can actually be interpreted before emission. The disclosure above documents the tradeoff; this check blocks two specific ways a bundle becomes uninterpretable:

1. **The thesis-bearing element must be the dominant change.** The element that carries the hypothesis's thesis (the specific-claim H1 under a "specificity" thesis, the proof strip under a "trust" thesis) must be the dominant change in the bundle, not a minor one carried along by larger edits. When the thesis element is NOT dominant (e.g., a "specificity" thesis whose H1 carries no specific claim while the bundle's real change is a layout overhaul), a win or loss cannot be attributed to the thesis at all. Restructure so the thesis element is the dominant change, or re-name the hypothesis to the thesis the dominant change actually tests.
2. **A bundled element must be seen by most visitors.** When a bundled element sits below the fold or is otherwise seen by few visitors (use the Step 5 viewport / scroll-reach flag), a flat result is uninterpretable: did the idea fail, or did most of the denominator never see the element carrying it? When a thesis-bearing element is low-reach, either pre-register the segment that does see it (Step 5 / FM6), move the element into view, or split it out and sequence it.

If neither restructure nor split resolves the interpretability problem, the bundle is not one experiment; flag it for strategist review rather than emitting an uninterpretable bundle. This strengthens the disclosure (which documents but never blocks); it does not change the Experiment Scope Rule's bundling mandate (bundle elements that serve one idea remains correct and required).

### Step 6: Win/Loss Learning

Every experiment must articulate what a positive AND negative result teaches.

**"What a win proves":** Not "the new version is better." What specifically does a positive result validate about positioning, messaging, or audience? Example: "Validates that outcome-oriented messaging resonates more than category language with paid search traffic, informing all paid landing pages."

For multi-variation hypotheses (Step 3b): address what a win for the *recommended* variation proves about the strategic anchor, and what it means if a different variation wins instead. The learning is about which messaging strategy resonates, not which copy is "better."

**"What a loss teaches":** Not "we were wrong." What does a negative result reveal? Example: "Suggests this audience values category credibility over outcome claims, indicating the brand isn't yet established enough to lead with results. Pivot to proof-first messaging instead."

For bundled tests (Step 5c, `bundled_test: true`): reference the `wont_teach` field from the bundled disclosure. A loss in a bundled test means the combined strategy underperformed, but does not isolate which individual element contributed. State this explicitly.

For hypotheses with proxy metrics (Step 5a, `metric_classification: proxy`): address the scenario where the proxy metric wins but the guardrail is flat or down. That is not a clear win. State the interpretation and next step.

A hypothesis where a loss teaches nothing is either poorly formed or too safe to be worth running.

**Inconclusive outcome guidance:**

For each hypothesis, also define what to do if the test produces no statistically significant result. This is not a failure state. It is the most common outcome (41-50% of A/B tests) and should have a predefined response.

**Construct the "If inconclusive" action using this decision framework:**

1. **Identify the most likely informative segment split.** Based on the hypothesis's causal mechanism and target audience, name the single most useful segmentation dimension to check first. Examples:
   - If the hypothesis targets paid traffic visitors: segment paid vs. organic
   - If the hypothesis involves mobile UX: segment desktop vs. mobile
   - If the hypothesis targets a specific persona: segment by traffic source that correlates with that persona (e.g., LinkedIn ads = senior decision-makers)
   - If the hypothesis involves new visitor experience: segment new vs. returning

2. **Define the "iterate bolder" path.** If the hypothesis was data-backed (performance-profile signal, pattern match with full trigger), and the test is flat, the causal mechanism may be correct but the variation too subtle. Define what a bolder version of the same hypothesis looks like. Example: "If the headline change is flat, test a full ATF overhaul including subhead and hero image, not just the H1."

3. **Define the "move on" signal.** If the test is flat AND segment analysis shows no meaningful differences AND the hypothesis was opinion-based (partial trigger, context-derived): recommend moving on to the next hypothesis. Velocity beats persistence for weakly-supported hypotheses.

4. **Identify the micro-conversion to check.** Name a leading indicator that should move even if the macro conversion is flat. If the micro-conversion improved but macro didn't, the hypothesis is directionally correct but there's downstream friction. Name what to test next. Example: "If CTA click-through improves but form submissions are flat, the messaging resonated but form friction is the next bottleneck. Test FO-01 or FO-03 next."

**Output format per hypothesis:**

```
if_inconclusive:
  segment_check: "[dimension] -- [what to look for]"
  iterate_path: "[bolder variation description]" | null
  move_on_signal: "[condition under which to abandon this line of testing]"
  micro_conversion: "[leading indicator to check]"
  next_hypothesis: "[which experiment to run next if this line is abandoned]"
```

This data populates the "If Tests Are Inconclusive" section in the final deliverable.

5. **Post-Deployment Causal Impact Validation.** For hypotheses targeting pages with variable external traffic sources (seasonal campaigns, PR spikes, affiliate bursts), define a 30-day post-deployment monitoring strategy. After deploying a winning variant, compare a 30-day pre/post time series to confirm the observed lift holds outside the test environment. If the page receives >30% of traffic from a single volatile source (paid campaigns with variable spend, PR-driven spikes), flag the hypothesis with: "Winner requires causal impact validation. Run 30-day pre/post time-series comparison after deployment. Monitor traffic source composition weekly during the validation period. If the dominant traffic source shifts >20% in volume or composition during validation, extend the window or re-run the test." This catches false positives where the winning variant coincided with favorable traffic mix rather than genuine behavioral change.

6. **Directional Significance Soft-Coding.** When a test reaches p < 0.15 but not p < 0.05, and the pattern has prior validation in the experiment-patterns library or a high-confidence match from a calibrated evidence module: recommend conditional deployment with continued monitoring. Output: "Directionally significant (p < [value]). Pattern has prior validation via [pattern ID or evidence source]. Recommend soft-coding (deploy with monitoring) and re-evaluating at 2x the original sample size. If the effect holds at 2x sample, hard-code. If it reverses, revert." This strategy applies ONLY when: (a) the pattern has prior empirical validation (not context-derived hypotheses), AND (b) the directional result aligns with the predicted direction from the causal mechanism. Do not soft-code counter-directional results or results from novel hypotheses.

### Step 7: Contrarian Filter

Before deduplication, run every constructed hypothesis through the contrarian trigger matrix.

**Process:**

1. Load `modules/contrarian-triggers.md`
2. For each hypothesis, check all thirteen trigger conditions (CTR-01 through CTR-13) against loaded context files
3. Apply the specified action for each match:
   - **Reframe:** Replace the hypothesis's proposed change, causal mechanism, and before/after examples with the alternative from the trigger matrix. Preserve the original trigger signal (the original pattern match is still valid, just the recommendation changes). Update the "Why this should work" section to reflect the reframed mechanism.
   - **Suppress:** Remove the hypothesis from the active list. Add to an internal "suppressed" list with the trigger ID and explanation. These are rendered in the "What's Not Here" section during Phase 5.
   - **Gate:** Keep the hypothesis but: (a) add the verification note to the hypothesis record, (b) set a tier ceiling of Strategic Bet (cannot be Quick Win regardless of ICE scores), (c) add the prerequisite to the Prerequisites section.
4. Run the anti-cargo-cult check on all surviving hypotheses. For any hypothesis that fails (applies generically to any B2B site), either add a context-grounding statement or suppress.

**Output:** Modified hypothesis list with reframed/gated/suppressed annotations. Suppressed hypotheses passed separately to Phase 5 for "What's Not Here" rendering.

**Interaction with existing modifiers:** Contrarian reframing happens BEFORE ICE scoring. The reframed hypothesis gets scored on its own merits. Do not apply the original pattern's ICE baseline to a reframed hypothesis. Instead:
- Reframed hypotheses use the contrarian trigger's recommended alternative as the basis for scoring
- If the alternative maps to a different pattern (e.g., CTR-01 reframes FO-01 into a qualifying-friction test), use that pattern's ICE baseline
- If the alternative has no matching pattern, start at 3/3/3 (same as context-derived)

### Step 8: Deduplication and Filtering

Before passing to Phase 4:

1. **Merge overlapping hypotheses.** If two opportunities target the same page with the same mechanism, merge into one hypothesis with both triggering signals noted. This intra-list merge is unchanged for tactical-vs-tactical and strategic-vs-strategic pairs. **Cross-lane (strategic vs tactical) reconciliation is NOT done here:** it is governed by the cross-deliverable dedup rule in `detect-strategic.md` Step 3 (same-idea + same-measurement-altitude means the strategic record supersedes the tactical one; same-idea + different-altitude means both stand, one per deliverable). Do not duplicate that rule body here; the two lanes render into separate deliverables.

2. **Remove unsubstantiated hypotheses.** If the current state can't be confirmed or reasonably inferred from any context file, remove entirely. Don't guess.

3. **Remove trivially obvious fixes.** Flag as "just do it" in the "What's Not Here" section when the action is obvious and the only question is whether to do it. Example: updating a stale metric, adding a generic "Contact us" link to a page that has none.

   **Do NOT apply this filter when the page's conversion role is itself the hypothesis.** A brand page, culture page, content hub, or office locator with no CTA is not automatically a "just do it." The structural fix (add some CTA) may be obvious, but whether the page can function as a conversion asset, and what conversion mechanism fits, is a testable question. In these cases, construct the experiment around the conversion role hypothesis, not the CTA addition.

   When such a hypothesis targets a page with <200 sessions/mo, route it through Step 5b feasibility estimation rather than killing it here. Low-traffic pages with legitimate hypotheses belong in "What's Not Here" under the infeasible framing (with alternative measurement suggestions like pre/post analysis), not in the "just do it" list.

4. **Cap handling.** If more hypotheses survive than `--max`, pass all to Phase 4 for scoring. Cut the lowest-ICE hypotheses after scoring, not before. Don't pre-filter based on gut feel.

---

## Context-Derived Hypothesis Construction

Context-derived opportunities (from Phase 2b) follow the same construction process above (Steps 1 through 10, including all lettered sub-steps) with these adjustments:

**Step 3 (Proposed Change):** Since there is no pattern template to adapt from, construct the proposed change from:
- Audience-messaging channel adaptations (if the signal relates to messaging)
- Competitive landscape white spaces (if the signal relates to positioning gaps)
- Positioning scorecard gap analysis recommendations (if the signal relates to a scored dimension)
- First principles UX or behavioral reasoning (if none of the above apply)

The proposed change must still be concrete enough that a developer or copywriter could implement it without clarifying questions.

**Step 4 (Causal Mechanism):** Construct the causal mechanism from first principles. You cannot pull from a pattern template because none exists. The mechanism must:
- Reference a specific behavioral, psychological, or UX principle by name
- Connect the proposed change to a measurable outcome through a logical chain
- Be falsifiable (you can imagine a scenario where the prediction is wrong)

Context-derived mechanisms tend to be more novel than pattern-based ones. This is expected. Novel doesn't mean weaker, but it does mean lower structural certainty, which is reflected in the Confidence penalty during scoring.

**Step 8 (Deduplication):** Context-derived hypotheses that overlap with pattern-matched hypotheses on the same page + mechanism should be merged into the pattern-matched version (the pattern-matched version has a stronger scoring foundation).

### Step 9: Interaction Analysis

After deduplication, analyze interactions between surviving hypotheses.

**Process:**

1. Load `modules/hypothesis-interactions.md`
2. Group hypotheses by target page
3. For each page with 2+ hypotheses:
   a. Look up each category pair in the interaction matrix
   b. Check exception conditions
   c. Apply interaction ruling:
      - **Multiplicative + same section:** Merge into a single bundled hypothesis. Combine the proposed changes, unify the causal mechanism, recalculate ICE baseline using the bundling rules (higher Impact, lower Confidence, lower Ease). Write a combined before/after, combined "What a win/loss proves."
      - **Multiplicative + different sections:** Keep as separate hypotheses. Add an `interaction_dependency` field: `{depends_on: "[hypothesis ID]", type: "multiplicative", rationale: "[from matrix]"}`. This field is consumed by Phase 4 for sequencing.
      - **Additive:** No action. Hypotheses remain independent.
4. For cross-page learning dependencies, add an `informs` field: `{informs: "[hypothesis ID]", relationship: "[description]"}`. Consumed by Phase 4 for Sequencing Rationale.
5. For any page where a Personalization hypothesis exists alongside non-personalization hypotheses: set `interaction_dependency` on the personalization hypothesis pointing to ALL other hypotheses on that page, with rationale: "Personalization amplifies the base experience. Resolve base experience hypotheses before testing personalization."

**Bundled hypothesis construction rules:**
- The bundled hypothesis gets a new name that reflects the combined strategy (e.g., "Homepage ATF Overhaul: Differentiation-Led Messaging + Proof Hierarchy" instead of two separate names)
- The causal mechanism must explain why both changes together test a single idea. If you cannot articulate a single unified idea, do not bundle. Keep as sequenced multiplicative pair instead.
- Before/after must show the combined variant, not two separate before/afters
- "What a win proves" addresses the combined strategy
- "What a loss teaches" must distinguish: "If the combined variant loses, it could mean [strategy A] failed, [strategy B] failed, or the combination created a negative interaction. To disambiguate, next test [A] or [B] in isolation."
- **Render check (hard gate):** a bundled hypothesis MUST carry the bundle-disclosure block with a non-empty "This test will not isolate" line. A bundled hypothesis whose loss-analysis states a single verdict without naming what the test cannot isolate fails the render and must be revised before output.

**Output annotations carried to Phase 4:**
- `interaction_type`: "bundled" | "multiplicative_dependency" | "additive" | "none"
- `interaction_dependency`: {depends_on, type, rationale} (for multiplicative pairs not bundled)
- `informs`: {informs, relationship} (for cross-page learning dependencies)

**Output to Phase 4:** Filtered hypothesis list with full construction details, interaction annotations, suppressed hypothesis list (from Step 7 contrarian filter), and self-critique records (from Step 10).

### Step 10: Self-Critique Meta-Pass

Before emitting the final hypothesis list, generate the strongest counterarguments to each hypothesis and check the writeup for internal consistency. This step catches reasoning weaknesses that targeted rules (Steps 3b, 3c, 4b, 5a, 5c) miss: inconsistencies between the skill's own arguments, evidence claims that overstate their support, and causal reasoning that doesn't survive scrutiny.

This is a required pass. It runs on all hypotheses, and the self-critique section is rendered for every hypothesis regardless of tier. The pass itself runs unconditionally.

**Procedure:**

**1. Generate three counterarguments.** For each hypothesis, produce:

- **Counter-A (thesis-level):** The strongest argument that the causal thesis is wrong. Not a strawman. The best version of why this hypothesis might fail for reasons the thesis doesn't anticipate. Example: "The thesis assumes content near the form is distracting, but the removed content was benefit-framing that set expectations. Removal may increase submissions while degrading lead quality."

- **Counter-B (test-design-level):** The strongest argument that even if the thesis is correct, this test won't prove it. Example: "The intervention bundles removal of existing content and addition of new proof elements. A win cannot isolate which mattered. A loss is ambiguous between 'wrong thesis' and 'right thesis, wrong execution.'" Skip if Step 5c (Bundled Variable Disclosure) already covers the same test-design concern. Do not duplicate what Step 5c documents.

- **Counter-C (business-outcome-level):** The strongest argument that even if the test wins on the primary metric, the business outcome could be neutral or negative. Example: "Removing expectation-setting content may increase form fills from visitors who don't understand what they're requesting, reducing show-rate and SQL conversion downstream." Skip if Step 5a (Proxy Metric Guardrails) already names a guardrail that addresses this exact risk. Reference the guardrail instead of restating.

**2. Internal consistency check.** Scan the complete hypothesis record for contradictions between its own arguments:

- Does the hypothesis cite the same prior data as evidence for AND against the intervention? (e.g., citing experiment results as "the pattern to replicate" in one section and "the pattern to avoid" in another)
- Does the thesis claim X is harmful while the intervention adds X (or a variant of X)?
- Does the evidence-strength language vary for the same data point across sections? (e.g., "pattern" in the rationale but "signal" in the feasibility notes)
- Are precedent claims consistent? A single experiment result is a "prior signal," not a "pattern." Three or more in the same direction with controlled variance is a "pattern."

Any contradiction must be resolved before the hypothesis is emitted. "Acknowledging the tension" is not resolution. Either reconcile the arguments or pick one and explain why the other is wrong.

**3. Evidence-strength audit.** For each causal claim in the hypothesis, verify that the language is proportionate to the evidence:

| Evidence Strength | Appropriate Language | Inappropriate Language |
|---|---|---|
| 1 data point | "prior signal," "suggestive," "one experiment indicates" | "pattern," "established," "proven," "consistently" |
| 2-3 data points, same direction | "emerging signal," "directional evidence," "early pattern" | "established pattern," "strong precedent," "unambiguous" |
| 4+ data points, same direction, controlled | "pattern," "precedent," "reliable signal" | "proven," "guaranteed," "always" |
| Behavioral principle, no experiment data | "principle-based hypothesis," "theoretical basis" | "proof," "evidence shows," "data confirms" |
| No specific evidence | "assumption," "working hypothesis" | any claim of evidence or proof |

Downgrade any language that exceeds what the evidence supports. This is not optional hedging. It is accuracy.

**4. Document counterarguments in hypothesis record.** Add a `self_critique` field:

```
self_critique:
  counter_thesis: "[Counter-A, stated fairly, 1-3 sentences]"
  counter_thesis_response: "[Rebuttal with evidence, or acknowledgment with interpretation implications, 1-2 sentences]"
  counter_design: "[Counter-B, 1-3 sentences. 'Covered by Step 5c' if already addressed.]"
  counter_design_response: "[Rebuttal or acknowledgment, 1-2 sentences]"
  counter_outcome: "[Counter-C, 1-3 sentences. 'Covered by guardrail [metric]' if Step 5a addresses it.]"
  counter_outcome_response: "[Rebuttal or acknowledgment + guardrail reference, 1-2 sentences]"
  consistency_issues_found: [true|false]
  evidence_downgrades: ["[claim X downgraded from 'pattern' to 'prior signal'}", ...]
  score_effect:
    counter_thesis_unmitigated: [true|false]   # Counter-A still stands after the response
    counter_outcome_unmitigated: [true|false]  # Counter-C still stands after the response
    confidence_delta: [0 | -1]                 # -1 when counter_thesis_unmitigated
    impact_delta: [0 | -1]                     # -1 when counter_outcome_unmitigated AND no guardrail added
    guardrail_added: "[metric name, or null]"  # when a guardrail is added instead of taking the Impact -1
```

**4b. Consequential self-critique (FM8).** A self-critique that names a decisive weakness must CHANGE something. For each counterargument, decide whether the response actually mitigates it (rebutted with evidence, or the design was changed) or merely acknowledges it. An UNMITIGATED counterargument has a consequence, emitted in the `score_effect` block above for `phases/score.md` to apply:

- **Counter-A (thesis-level) unmitigated:** set `counter_thesis_unmitigated: true` and `confidence_delta: -1`. If the thesis itself is materially weaker than the writeup claims, also rewrite the causal mechanism (Step 4) and win/loss learning (Step 6) per fail state 1 below; the Confidence reduction applies regardless.
- **Counter-C (business-outcome-level) unmitigated:** the hypothesis must EITHER add a guardrail metric that covers the outcome risk (set `guardrail_added` and `impact_delta: 0`) OR take `impact_delta: -1`. Adding a guardrail is the preferred mitigation; the Impact reduction is the fallback when no guardrail can cover the risk.
- **Counter-B (test-design-level):** if unmitigated and not already covered by Step 5c, it is a design defect, not a score modifier; resolve it by restructuring the test (Step 5b / 5c) or flag for strategist review per fail state 2 below. It does not emit an ICE delta (a broken design is fixed or flagged, not scored down).

The deltas are emitted here and applied by `score.md` Step 4 as soft modifiers on the raw Confidence / Impact (clamped 1-5), upstream of the gated rubric's hard ceiling. This closes the gap where a self-critique named the decisive weakness and left the score unchanged: the named weakness now reduces the relevant ICE component or adds a guardrail, every time it is unmitigated.

**5. Fail states.** If the self-critique reveals:

- The thesis is substantially weaker than the writeup implied: rewrite the causal mechanism (Step 4) and win/loss learning (Step 6) to match the actual evidence strength. Do not emit overconfident language that the self-critique just disproved.
- The test design cannot prove what the hypothesis claims: add an explicit limitation note to the hypothesis record. If the limitation is severe enough that a win would be uninterpretable, flag for strategist review.
- A business-outcome risk is not mitigated by any existing guardrail (Step 5a): either add a guardrail or add the risk to the hypothesis notes with a note: "No guardrail covers this risk. Recommend monitoring [downstream metric] during and after the test."

**Length discipline:** Each counterargument is 1-3 sentences. Each response is 1-2 sentences. The full self-critique section per hypothesis should not exceed ~150 words. If it's longer than the hypothesis itself, it's too long.
