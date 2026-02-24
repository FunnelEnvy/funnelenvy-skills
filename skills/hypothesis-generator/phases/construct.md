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

## Construction Process

### Step 1: Page and Element Identification

For each opportunity, identify the specific page and element the experiment targets.

**Specificity requirements:**
- Page must be named (e.g., "Homepage," "Pricing page," "/solutions/enterprise"), not categorized ("a landing page")
- Element must be identified (e.g., "Hero headline," "Primary CTA," "Lead capture form," "Navigation menu"), not vague ("the top of the page")
- If the exact page can't be determined from context, use the most likely page based on the pattern's typical deployment and note the assumption

### Step 2: Current State Documentation

Document what exists now. This is the control in the experiment.

**For copy experiments:**
- Pull exact copy from company-identity.md's Homepage Messaging section, stated differentiators, or proof points
- If exact copy isn't available, describe the observed pattern ("Homepage headline uses category language rather than outcome language")
- NEVER fabricate current-state copy. If you don't have it, say what you know about it

**For structural experiments:**
- Describe the current layout, form structure, navigation pattern, or page architecture based on what context files reveal
- Flag when your understanding of current state is inferred rather than directly observed

**For personalization experiments:**
- Document the current one-size-fits-all experience: what all visitors see regardless of segment

**Baseline data (when performance-profile.md exists):**
- Look up the target page in performance-profile.md's Page Performance and Conversion Events sections
- Record: sessions/mo, bounce rate, conversion rate (for primary conversion event), and top traffic source
- This data populates the `**Baseline:**` line in the deliverable template
- If the target page doesn't appear in performance-profile.md (low traffic or not tracked), note "No baseline data for this page" and skip the Baseline line

### Step 3: Proposed Change

Define the specific variant to test.

**Rules:**
- One variable per experiment. If the hypothesis changes headline AND CTA, split into two experiments or clearly define the primary variable.
- Proposed changes must be grounded in context. For copy changes, adapt from audience-messaging.md channel adaptations, value themes, or persona-specific messaging. For structural changes, apply the pattern's typical test from experiment-patterns.md.
- Do NOT invent new creative from scratch. The proposed change should be traceable to either the pattern library or the messaging analysis.
- Be concrete enough that a developer or copywriter could implement the variant without clarifying questions.

**For copy experiments, produce before/after pairs:**

```
Before: "The Revenue Intelligence Platform for Modern Sales Teams"
After: "Close 40% More Deals by Knowing What Your Buyers Actually Want"
```

The "before" comes from context files. The "after" adapts messaging from audience-messaging.md. If audience-messaging.md doesn't exist, adapt from L0's strongest proof points and value propositions.

### Step 4: Causal Mechanism

Every hypothesis requires a "why." This is the CRO reasoning that separates a rigorous hypothesis from a guess.

**Structure the causal chain:**
1. **Observation:** What specific condition exists now (from context)
2. **Principle:** What behavioral, psychological, or UX principle applies
3. **Prediction:** What change in behavior the variant should produce
4. **Metric:** How that behavior change manifests in measurable terms

**Example:**
> Visitors from paid search land on the homepage and see a category-defining headline ("Revenue Intelligence Platform"). These visitors already know the category: they searched for it. Repeating category language wastes the highest-attention moment on information they already have. Replacing with outcome language ("Close 40% more deals") immediately communicates value, reducing bounce rate and increasing demo request clicks. The primary metric is demo request rate; secondary metric is bounce rate.

**Causal mechanism quality check:**
- Does it reference a specific behavioral principle? (cognitive load, commitment bias, social proof, loss aversion, etc.)
- Is the prediction falsifiable? (If you can't imagine a negative result, the mechanism is too vague)
- Does it connect the change to a measurable metric through a logical chain?

Pull the causal mechanism from the matched pattern in `modules/experiment-patterns.md` as a starting point, then adapt to the specific context. Don't copy the pattern's mechanism verbatim when the specific context adds nuance.

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

### Step 6: Win/Loss Learning

Every experiment must articulate what a positive AND negative result teaches.

**"What a win proves":** Not "the new version is better." What specifically does a positive result validate about positioning, messaging, or audience? Example: "Validates that outcome-oriented messaging resonates more than category language with paid search traffic, informing all paid landing pages."

**"What a loss teaches":** Not "we were wrong." What does a negative result reveal? Example: "Suggests this audience values category credibility over outcome claims, indicating the brand isn't yet established enough to lead with results. Pivot to proof-first messaging instead."

A hypothesis where a loss teaches nothing is either poorly formed or too safe to be worth running.

### Step 7: Deduplication and Filtering

Before passing to Phase 4:

1. **Merge overlapping hypotheses.** If two opportunities target the same page with the same mechanism, merge into one hypothesis with both triggering signals noted.

2. **Remove unsubstantiated hypotheses.** If the current state can't be confirmed or reasonably inferred from any context file, remove entirely. Don't guess.

3. **Remove trivially obvious fixes.** "Add a CTA to a page that has no CTA" is implementation, not experimentation. Flag these as "just do it" items in the "What's Not Here" section of the final roadmap.

4. **Cap handling.** If more hypotheses survive than `--max`, pass all to Phase 4 for scoring. Cut the lowest-ICE hypotheses after scoring, not before. Don't pre-filter based on gut feel.

---

## Context-Derived Hypothesis Construction

Context-derived opportunities (from Phase 2b) follow the same 7-step process above with these adjustments:

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

**Step 7 (Deduplication):** Context-derived hypotheses that overlap with pattern-matched hypotheses on the same page + mechanism should be merged into the pattern-matched version (the pattern-matched version has a stronger scoring foundation).

**Output to Phase 4:** Filtered hypothesis list with full construction details.
