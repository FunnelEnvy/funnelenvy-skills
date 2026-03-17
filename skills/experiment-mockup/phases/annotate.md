# Phase 4: Annotate -- Both Modes

**Purpose:** Write the CRO rationale document explaining placement decisions, attention strategy, alternative placements, and implementation notes for the dev team.

**Applies to:** Both live and static modes. This phase runs after capture (live) or static-build (static).

---

## Required Inputs

- Hypothesis number, name, target URL, page name (from orchestrator)
- Final insertion point / DOM path (from Phase 2/3 or static-build)
- Iteration history (live mode: what was tried and changed)
- Final mockup copy, verbatim (from the approved injection or static build)
- Execution mode: live or static
- `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)

## Output

- `.claude/deliverables/experiments/<slug>/placement.md`

---

## Steps

### Step 1: Write placement.md

Create the file with YAML frontmatter and 6 body sections.

**Frontmatter:**

```yaml
---
schema: experiment-placement
schema_version: "1.0"
hypothesis: [number]
hypothesis_title: "[from roadmap]"
target_url: "[url]"
target_page: "[page name, e.g., Contact, Pricing, Homepage]"
insertion_point: "[DOM path or descriptive location]"
mode: [live|static]
generated_by: experiment-mockup v1.0.0
last_updated: [YYYY-MM-DD]
---
```

**Body sections:**

### Section 1: Placement Decision

Write where the element was placed and the CRO reasoning behind it.

Required content:
- Physical location on the page (e.g., "Directly above the contact form, inside the `section.contact-area` container")
- Proximity rationale: why this distance from the conversion element is optimal. Reference the proximity-to-intent-signal principle.
- Visual hierarchy position: where this element sits in the page's attention hierarchy relative to the primary CTA. Reference D8 (Copy Quality and Readability) from lp-audit-taxonomy.
- Objection timing rationale: why the user encounters this content at this point in their scroll journey. Reference D5 (Social Proof Strategy) or D1 (Awareness-Stage Alignment) from lp-audit-taxonomy as applicable.
- If the user changed placement during iteration (live mode only): document what was tried first, what feedback the user gave, and why the final position won.

### Section 2: Attention Strategy

Write how the element draws attention without cannibalizing the primary CTA.

Required content:
- Visual devices used: list each attention mechanism (background contrast, border accent, heading weight, icon) with the specific CSS values
- CTA subordination: how the element's visual weight compares to the primary CTA. Reference the specific CTA styles extracted in Phase 1 (or parsed in static-build) and explain why the new element is subordinate (smaller font, lighter background, no box-shadow vs CTA's box-shadow, etc.)
- Scannability assessment: can a user absorb the key message in under 3 seconds of scanning? Count words in the headline and body. If headline > 8 words or body > 40 words, flag it.

### Section 3: Content Distillation

Document how the hypothesis copy was adapted for the mockup context.

Required content:
- The original "After" copy from the hypothesis (verbatim quote)
- The final mockup copy (verbatim quote)
- What was kept and why (the core reframe, the key proof point, the emotional anchor)
- What was cut and why (word count constraints near a conversion point, headline hierarchy, redundancy with existing page content)
- If the copy was not distilled (used as-is): note why it was already appropriate for the context

### Section 4: Alternative Placements

Document at least 2 other placement options.

For each alternative:
- Where it would go (DOM location description)
- What it would look like (brief structural description)
- Pros (what this position offers)
- Cons (why it's worse than the chosen placement)

If the hypothesis suggested a specific location and the skill chose differently, explain why in a dedicated paragraph referencing the specific CRO principles that drove the divergence.

In live mode: if placements were actually tried during iteration, document those as alternatives with the user's actual feedback as the "cons."

### Section 5: Implementation Notes

Write concrete implementation guidance for the dev team.

Required content:
- **DOM insertion point:** CSS selector path or descriptive location that a developer can find in the source code
- **CSS properties:** List every CSS property and value needed for the new element. Not "match the site's styles" but explicit values: `background: #f8f9fa; border-left: 3px solid #2563eb; padding: 24px 32px; font-family: Inter, sans-serif; font-size: 16px; line-height: 1.6;`
- **SPA detection:** If the site appears to be a single-page application (React, Next.js, Vue, Angular indicators in the DOM or script tags), note: "This site uses [framework]. DOM injection will not work in production. The change requires component-level implementation in the [framework] source."
- **JS behavior:** List any JavaScript needed (collapsible content, scroll-triggered visibility, conditional display based on referrer or URL parameter). If none needed, state "No JavaScript required."
- **Responsive behavior:** How should this element behave on mobile? Common patterns: stack below the form (if it was beside it on desktop), collapse to a single-line summary, reduce padding, maintain full width. Specify the approach.
- **A/B test platform compatibility:** Can this change be injected client-side via Optimizely/VWO/Convert/Google Optimize? Conditions: if the change is a simple DOM insertion with no conditional logic, it's client-side compatible. If it requires server-side data, personalization logic, or modifies the initial page render, it needs server-side implementation. State which.

### Section 6: Risk Flags

List anything that might not survive real implementation.

Check for and flag:
- **CMS constraints:** If the page appears CMS-managed (WordPress, HubSpot, Webflow, Contentful indicators), note that the change may require CMS template or module modifications rather than direct HTML editing.
- **Dynamic content:** If the target section contains dynamic elements (sliders, carousels, A/B test variations already running, personalization blocks), note the interaction risk.
- **Z-index/overlay issues:** If the site uses overlays, sticky headers, or modals that might cover the new element, flag it.
- **Third-party scripts:** If the target area is managed by a third-party tool (chat widget, form builder like Typeform/HubSpot Forms, embedded booking calendar), note that DOM injection in that area may be fragile.
- **Content freshness:** If the injected content references specific data (pricing, customer count, percentage) that may change, flag the maintenance requirement.

If no risk flags are identified, write: "No significant implementation risks identified for this placement."

### Step 2: Write to Disk

Write `placement.md` to `.claude/deliverables/experiments/<slug>/placement.md`.

Confirm: "Placement rationale written to [path]."
