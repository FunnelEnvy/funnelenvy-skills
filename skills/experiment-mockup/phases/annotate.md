# Phase 4: Annotate -- Both Modes

**Purpose:** Write the CRO rationale document explaining placement decisions, attention strategy, alternative placements, and implementation notes for the dev team.

**Applies to:** Both live and static modes. This phase runs after capture (live) or static-build (static).

---

## Required Inputs

- Hypothesis number, name, target URL, page name (from orchestrator)
- Change type and its source (roadmap `**Change type:**` value, or locally classified; passed from the orchestrator / inject phase)
- Final insertion point / DOM path (from Phase 2/3 or static-build)
- Iteration history (live mode: what was tried and changed)
- Candidate-pass scoring (from inject Step 1a: the losing candidates and their pros/cons, or the skip reason)
- Which variation was mocked (when the hypothesis carried a Variation block)
- Final mockup copy, verbatim (from the approved injection or static build)
- Overlays hidden for capture (from capture.md Step 0; live/playwright only)
- Resolved target region and gate outcome (from inject.md Target-Fidelity Gate, or static-build.md Step 2)
- Salience-framing decision (from capture.md Step 1: resolved scale and whether the size backstop fired; live/playwright only)
- Spot-the-diff outcome (from inject.md Step 2b; live/playwright only)
- Execution mode: live or static
- `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)

## Output

- `<output-dir>/placement.md` (the orchestrator-provided output directory: legacy `.claude/deliverables/experiments/<slug>/`; KB mode `{kb_root}/deliverables/experiments/<slug>/`)

---

## Steps

### Step 1: Write placement.md

Create the file with YAML frontmatter and 7 body sections.

**Frontmatter:**

```yaml
---
schema: experiment-placement
schema_version: "1.2"
hypothesis: [number]
hypothesis_title: "[from roadmap]"
target_url: "[url]"
target_page: "[page name, e.g., Contact, Pricing, Homepage]"
change_type: "[insert | replace-copy | modify | remove | reorder; comma-separated for a bundled test]"
change_type_source: "[roadmap | local]"
insertion_point: "[DOM path or descriptive location]"
mode: [live|static]
generated_by: experiment-mockup v1.6.0
last_updated: [YYYY-MM-DD]
---
```

**Body sections:**

### Section 1: Placement Decision

**Type framing.** For `insert`, "placement" means where the net-new element was placed. For `replace-copy` and `modify`, "placement" means the existing element that was edited (name it and its location); there is no new element to place. For `remove`, describe what was removed and where it sat. For `reorder`, describe the old and new positions. Write the section against the active change type.

Write where the element was placed (or which element was edited) and the CRO reasoning behind it.

Required content:
- Physical location on the page (e.g., "Directly above the contact form, inside the `section.contact-area` container")
- Proximity rationale: why this distance from the conversion element is optimal. Reference the proximity-to-intent-signal principle.
- Visual hierarchy position: where this element sits in the page's attention hierarchy relative to the primary CTA. Reference D8 (Copy Quality and Readability) from lp-audit-taxonomy.
- Objection timing rationale: why the user encounters this content at this point in their scroll journey. Reference D5 (Social Proof Strategy) or D1 (Awareness-Stage Alignment) from lp-audit-taxonomy as applicable.
- If the user changed placement during iteration (live mode only): document what was tried first, what feedback the user gave, and why the final position won.

### Section 2: Attention Strategy

**Type framing.** For `insert`, cover how the element draws attention without cannibalizing the primary CTA (subordination). For `replace-copy` and `modify` whose target IS the primary CTA (a prominence or label test), cover the prominence delta instead: how the edited element's visual weight changed and why that serves the hypothesis, not how it stays subordinate. For `remove`/`reorder`, cover how attention redistributes across the remaining/resequenced elements.

Write how the treatment handles attention, per the framing above.

Required content:
- Visual devices used: list each attention mechanism (background contrast, border accent, heading weight, icon) with the specific CSS values
- CTA subordination: how the element's visual weight compares to the primary CTA. Reference the specific CTA styles extracted in Phase 1 (or parsed in static-build) and explain why the new element is subordinate (smaller font, lighter background, no box-shadow vs CTA's box-shadow, etc.)
- Scannability assessment: can a user absorb the key message in under 3 seconds of scanning? Count words in the headline and body. If headline > 8 words or body > 40 words, flag it.

### Section 3: Content Distillation

Document how the hypothesis copy was adapted for the mockup context.

Required content:
- **Variation mocked (when applicable):** if the hypothesis carried a Variation block, state which variation was mocked (the Recommended one by default), name the others, and note that re-running can build a different variation. If the hypothesis had no variations, omit this line.
- The original "After" copy from the hypothesis (verbatim quote)
- The final mockup copy (verbatim quote)
- What was kept and why (the core reframe, the key proof point, the emotional anchor). Per the Distillation Contract, quantified claims from the hypothesis copy are immutable: they are never cut, altered, or rounded, and no claim/number/outcome absent from the hypothesis copy is introduced.
- What was cut and why (word count constraints near a conversion point, headline hierarchy, redundancy with existing page content)
- If the copy was not distilled (used as-is): note why it was already appropriate for the context. For `remove`/`reorder`/`modify` treatments that change no copy, state "No copy change" and omit the distillation detail.

### Section 4: Alternative Placements

Document the alternatives that were actually considered. This section consumes the candidate pass from inject Step 1a: the losing candidates and their internal scoring, so this is documentation of a comparison that happened, not a retrospective justification invented after the fact.

For each candidate the pass rejected:
- Where it would go (DOM location description)
- What it would look like (brief structural description)
- Pros (what this option offered, from the internal scoring)
- Cons (why it lost to the chosen treatment, from the internal scoring)

If the candidate pass was skipped (the hypothesis fully pinned the treatment, e.g., `replace-copy` with exact copy on a single element), state the skip reason and that no placement discretion existed, rather than inventing alternatives.

If the hypothesis suggested a specific location and the skill chose differently, explain why in a dedicated paragraph referencing the specific CRO principles that drove the divergence.

In live mode: if placements were also tried during user iteration, document those with the user's actual feedback as the "cons."

### Section 5: Implementation Notes

Write concrete implementation guidance for the dev team.

Required content:
- **DOM insertion point:** CSS selector path or descriptive location that a developer can find in the source code
- **CSS properties:** List every CSS property and value needed for the new element. Not "match the site's styles" but explicit values: `background: #f8f9fa; border-left: 3px solid #2563eb; padding: 24px 32px; font-family: Inter, sans-serif; font-size: 16px; line-height: 1.6;`
- **SPA detection:** If the site appears to be a single-page application (React, Next.js, Vue, Angular indicators in the DOM or script tags), note: "This site uses [framework]. DOM injection will not work in production. The change requires component-level implementation in the [framework] source."
- **JS behavior:** List any JavaScript needed (collapsible content, scroll-triggered visibility, conditional display based on referrer or URL parameter). If none needed, state "No JavaScript required."
- **Responsive behavior:**
  - **Live and playwright modes (observed):** Report how the treatment DID behave at 390px, from the mobile self-review (inject Step 2b) and the mobile screenshot pair (`control-screenshot-mobile.png` / `mockup-screenshot-mobile.png`). Cite what was observed: stacking, padding, whether it stayed visible and coherent, any horizontal-overflow issue and how it was resolved. This is observed behavior, not a recommendation.
  - **Static mode (speculative):** No browser, so state how the element SHOULD behave on mobile (stack below the form, collapse to a single-line summary, reduce padding, maintain full width) and mark it explicitly as a recommendation not yet verified in a browser.
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

### Section 7: Capture Fidelity Notes

Record the four capture-fidelity decisions as labeled prose entries, each a verdict plus brief reasoning. This section is mode-aware: P4 (target-fidelity) populates in ALL modes; the three screenshot-dependent items populate in live/playwright only and state "not applicable (static mode, no screenshots)" in static.

- **Overlays hidden for capture (P1):** the floating overlays dismissed/hidden for the shots (e.g., "cookie-consent banner, chat widget"), or "none present". Live/playwright only; in static mode state "not applicable (static mode, no screenshots)".
- **Resolved target region and gate outcome (P4):** the hypothesis's named region, the resolved element, and the gate outcome (clean pass; or stopped-and-asked, naming both candidates and the user's choice; or static Risk-Flag on an unresolved discrepancy). Populated in ALL modes: static resolves it via DOM structure through static-build.md Step 2.
- **Salience-framing decision (P2):** the resolved scale (element/copy-scale or section-scale) and whether the one-directional size backstop fired. Live/playwright only; static states "not applicable (static mode, no screenshots)".
- **Spot-the-diff outcome (P3):** pass, or the re-frame it forced. Live/playwright only; static states "not applicable (static mode, no screenshots)".

### Step 2: Write to Disk

Write `placement.md` to the orchestrator-provided output directory (legacy `.claude/deliverables/experiments/<slug>/placement.md`; KB mode `{kb_root}/deliverables/experiments/<slug>/placement.md`).

Confirm: "Placement rationale written to [path]."
