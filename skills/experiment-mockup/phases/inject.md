# Phase 2: Inject -- Live Mode Only

**Purpose:** Build the proposed content block using the site's design tokens and inject it into the live DOM. Iterate with the user on placement, styling, and content until they approve.

**Applies to:** Live mode only. Static mode uses `static-build.md` instead.

---

## Required Inputs

- Design tokens, DOM insertion path, content block patterns, target section HTML (from Phase 1)
- Hypothesis text: proposed change, before/after copy (from orchestrator)
- Change type (from orchestrator: the roadmap's `**Change type:**` value, or "classify locally" when the roadmap predates the field)
- Variation set and recommended variation (from orchestrator, when the hypothesis carries a Variation block)
- `modules/conversion-playbook.md` (sections 1-6)
- `modules/lp-audit-taxonomy.md` (base dimensions D1, D3, D5, D8, plus any conditional dimensions the orchestrator loaded per the change type)
- `modules/copy-craft.md` (evidence-graded copy rules; governs any rewrite of the hypothesis copy, see the Distillation Contract below)

## Outputs

- Injected content block visible in user's Chrome browser
- User approval of final placement and styling
- Final injection state (held in working memory for Phase 3)

**No files written to disk in this phase.** User iteration happens in the live browser.

---

## Treatment Principles by Change Type

The treatment doctrine is type-conditional. The cross-type invariants below apply to every treatment. Then read ONLY the branch for the active change type: it governs what shape the treatment takes and how it is built. hypothesis-generator owns WHAT changes; these branches constrain HOW it manifests visually.

### Resolving the change type

Use the change type the orchestrator passed (the roadmap's `**Change type:**` value). If the orchestrator says "classify locally" (a legacy roadmap that predates the field), classify from the hypothesis's What-to-test + Proposed-change using this enum, and record that you did so (placement.md notes "change type classified locally; roadmap predates the Change type field"):

- `insert` -- add a net-new element (objection callout, trust bar, social proof block, added microcopy line).
- `replace-copy` -- change the text of an existing element, the element itself unchanged (headline, subhead, CTA label, form labels/microcopy).
- `modify` -- change the style, structure, or behavior of an existing element (CTA prominence, form field layout, sticky behavior, image swap).
- `remove` -- remove or hide an existing element (nav links, distractor blocks, form fields).
- `reorder` -- resequence existing sections or elements, nothing added or removed.

When the type is comma-separated (a bundled test spanning types), apply each named branch to the part of the treatment it governs. The primary (first-listed) type governs the dominant change.

### Cross-type invariants (apply to every branch)

- **Primary-action prominence.** The page's primary conversion action must remain the most visually prominent action after the change, UNLESS the hypothesis's target IS the primary CTA. When the hypothesis targets the primary CTA (a `modify` prominence test or a `replace-copy` CTA-label test), the hypothesis defines the intended prominence and this invariant yields to it.
- **Native styling only.** Use extracted/brand tokens. No annotation artifacts (no "PROPOSED" labels, fidelity banners, or annotation borders). The mockup must look like a real page element.
- **Change only what the hypothesis specifies.** A `replace-copy` treatment does not also restyle; a `modify` treatment does not also rewrite copy beyond what the hypothesis states; an `insert` does not silently edit adjacent elements. Scope the treatment to the hypothesis.

### Branch: insert

Add a net-new element. These are the placement rules for an inserted block (the historical treatment doctrine, now scoped to this branch).

**Visual hierarchy (D8: Copy Quality and Readability).** The new element must NOT have higher visual weight than the primary CTA. It supports the conversion action, it does not compete with it.
- Use the site's **secondary** emphasis patterns: lighter background shade, smaller heading size (h3 not h2), muted accent color.
- Do NOT use the primary CTA color for any part of the injected element.
- Do NOT use the site's largest heading size (h1) for the injected element's headline.
- The CTA button extracted in Phase 1 defines the visual ceiling. Stay below it.

**Proximity to intent signal.** Objection-handling content belongs NEAR the conversion point (form, CTA), not mid-page or in a disconnected sidebar.
- "Near" means within 1 scroll-viewport of the conversion element, ideally visible simultaneously on desktop.
- For /contact pages: immediately above or beside the form. NOT below the form (user has already scrolled past the decision point).
- For pricing pages: adjacent to the pricing table or tier comparison, not in a separate section.
- For product pages: near the primary CTA, not buried in feature descriptions.

**Attention without disruption (D1: Awareness-Stage Alignment).** The content block must be scannable. Users near a conversion point are in decision mode, not reading mode.
- Short headline (under 8 words).
- 1-2 short sentences maximum (under 40 words total).
- Optional: one icon or visual anchor for scannability.
- No paragraphs. No bullet lists longer than 3 items.
- The hypothesis may have a long "After" example. Distill it to the essential reframe per the Distillation Contract below. Document the distillation in placement.md (Phase 4).

**Contrast calibration.** The element must be noticed without looking like an ad, an alert, or an error message.
- Use a DIFFERENT background from the surrounding section (subtle contrast: 5-15% lightness difference), OR a subtle left border accent (3-4px, in a secondary brand color or neutral blue/gray).
- Do NOT use high-saturation backgrounds (red, orange, bright yellow) or the site's warning/error color palette.
- Do NOT use the exact same background as the surrounding section (the element would be invisible).

**Using existing patterns.** If Phase 1 identified a content block pattern on the site (callout box, trust badge row, info block with icon), use that pattern's structure and styling as the base: keep the structural pattern (same border treatment, padding, layout), replace the content with the hypothesis copy, adjust sizing to fit. If no suitable pattern was found, build a simple callout block with a left border accent, using the site's secondary heading size and body text size.

### Branch: replace-copy

Edit the target element's text in place. The element itself does not change.
- Preserve the tag level exactly. An h1 headline test stays an h1; a CTA label stays the same button element. The insert branch's h3/h4 heading ceiling and word-count limits do NOT apply here.
- Preserve all computed styles exactly. Zero container, layout, color, or spacing changes. Only the text content changes.
- Copy is governed by `modules/copy-craft.md` for the target element type: headline rules for H1s/headlines, subhead rules for subheads, CTA rules for CTA labels, form-microcopy rules for form labels/errors/privacy text. Apply the Distillation Contract below.

### Branch: modify

Change only the properties the hypothesis names (style, structure, or behavior of an existing element).
- Touch only the named properties. Do not rewrite copy (that is `replace-copy`) or add elements (that is `insert`) unless the change type is comma-bundled with those.
- **Primary-CTA prominence exception.** When the target IS the primary CTA and the hypothesis is about prominence, exceeding the element's prior visual weight is the point. The prominence invariant yields (see Cross-type invariants). Do not subordinate the element you were asked to make more prominent.
- Record the before/after computed-style delta per property (e.g., `background: #eee -> #2563eb`, `font-size: 14px -> 18px`) so placement.md Section 5 (Implementation Notes) can list explicit values.

### Branch: remove

Remove or hide the element the hypothesis names, then verify the page still holds together.
- Remove/hide the element and verify layout reflow: no orphaned gaps, no collapsed grid/flex tracks, no `nth-child` styling breakage on sibling elements.
- The control screenshot is the primary evidence for this type: the pair shows what was present (control) versus removed (after).

### Branch: reorder

Move existing DOM nodes without altering them.
- Move the nodes; do not restyle or rewrite them.
- Verify no CSS depends on source order (`nth-child`, adjacent-sibling `+`, general-sibling `~` selectors) such that the reorder silently changes styling.
- Check the spacing seams at BOTH the old boundary (where the node left) and the new boundary (where it landed).

---

## Distillation Contract

This governs ANY rewrite of the hypothesis copy for the mockup context (most relevant to `insert` distillation and `replace-copy` element edits). Read `modules/copy-craft.md` before rewriting copy.

1. **Never cut, alter, or round a quantified claim** present in the hypothesis "After" copy. Those numbers passed construct.md Step 4b proof-integrity upstream; this skill has no proof-registry access and must treat them as immutable. If space forces cuts, keep the specific and cut elsewhere.
2. **Never introduce a claim, number, or named outcome** not present in the hypothesis copy.
3. **Preserve front-loading:** the load-bearing word stays first (copy-craft Rule 3).
4. **For `replace-copy` treatments, apply the copy-craft element rules** for the target element type. The insert branch's distillation limits (heading ceiling, word counts) do NOT apply to a `replace-copy` edit.
5. **Document distillation deltas** in placement.md Section 3 (Content Distillation): the original "After" copy verbatim, the final mockup copy verbatim, what was kept and cut.

---

## Steps

### Step 1a: Candidate Pass (before building)

When you have genuine discretion over the treatment (placement, pattern, or layout is NOT pinned by the hypothesis), do a quick internal comparison before committing to one build:

1. Sketch 2-3 candidate treatments internally (in reasoning only).
2. Score each against a short checklist derived from the loaded taxonomy dimensions and the active type branch above (e.g., for `insert`: subordination to the primary CTA, proximity to the intent signal, scannability, contrast calibration; for `modify`: whether the prominence delta reads without breaking hierarchy).
3. Pick the winner and build only that one (Step 1).
4. The losing candidates become placement.md Section 4 (Alternative Placements) content, with your internal scoring as the pros/cons. Section 4 is now documentation of a comparison that actually happened, not a retrospective justification.

**Skip condition.** When the hypothesis fully pins the treatment (e.g., a `replace-copy` test with exact "After" copy on a single named element, or a `remove` of one named element), skip the candidate pass and note the skip reason for placement.md (e.g., "candidate pass skipped: replace-copy with exact copy on a single element leaves no placement discretion").

**Bounds.** Internal reasoning only. No subagents, no user interaction, no additional tool calls. This pass costs nothing but thinking.

### Step 1: Build the Treatment

Build ONLY the winning candidate from Step 1a, branching on the active change type (read the matching branch under Treatment Principles by Change Type). Design tokens from Phase 1 apply throughout (brand tokens take precedence over computed styles). When the hypothesis carries a Variation block, build the **Recommended** variation (the orchestrator names it); the other variations are named at first presentation and can be swapped during iteration.

**For `insert`:**
1. Choose the structural pattern (existing site pattern or default callout block).
2. Write the HTML for the content block:
   - Semantic markup: `<div>` with a descriptive class (e.g., `proposed-change-block`).
   - Headline in the appropriate heading level (h3 or h4, never h1 or h2).
   - Body text in `<p>` tags.
   - Optional icon or visual anchor if the site uses them.
3. Write inline CSS matching the site's design tokens: exact font-family, font-size, line-height from Phase 1; exact padding/margin from the site's content blocks; contrast calibration rules for background and border.

**For `replace-copy`:** locate the target element; change only its text content (governed by copy-craft + the Distillation Contract); leave the tag, container, and every computed style untouched.

**For `modify`:** apply only the named style/structure/behavior properties to the target element; record the per-property before/after computed-style delta.

**For `remove`:** remove or hide the named element; leave everything else intact for the reflow check in Step 2b.

**For `reorder`:** move the named DOM nodes to their new position without altering them.

In all branches: the element uses native site styling only. No annotation borders, labels, or badges. The mockup should look like a real page element.

### Step 2: Inject into Live DOM

Use the browser MCP to insert the element:

- Chrome DevTools mode: use Puppeteer DOM manipulation tools
- Playwright mode: use browser_evaluate() with insertAdjacentHTML:

  ```javascript
  browser_evaluate(`
    document.querySelector('[target-selector]')
      .insertAdjacentHTML('beforebegin', \`[injection HTML]\`)
  `)
  ```

1. Locate the insertion point identified in Phase 1 (DOM selector)
2. Insert the element using `insertAdjacentHTML` or equivalent DOM manipulation:
   - If inserting BEFORE an element: use `beforebegin` position
   - If inserting AS FIRST CHILD: use `afterbegin` position
   - If inserting AFTER an element: use `afterend` position
3. Verify the injection rendered (the element should be visible in the viewport)
4. If the element is not in the viewport, scroll to it

### Step 2b: Screenshot Self-Review Gate (live and playwright modes, before first presentation)

Before presenting to the user, screenshot the injected state and review it yourself. This catches obvious defects the human should never have to point out.

**Desktop check.** Screenshot the injected viewport and verify:
- The element (or the edited element for `replace-copy`/`modify`, or the reflowed region for `remove`/`reorder`) is fully visible, not clipped by overflow or a sticky header.
- No text-wrapping artifacts or layout breakage.
- Contrast per the active branch's rules.
- Primary-CTA prominence invariant holds (or the `modify`/`replace-copy` CTA-target exception is in effect).
- Alignment with the site's content grid; spacing consistent with the inter-block rhythm.

**Mobile check (390px).** Resize the browser to 390px width, screenshot, and verify responsive behavior:
- Correct stacking and padding at narrow width.
- No horizontal overflow.
- The treatment is still visible and coherent (not collapsed, clipped, or overlapping).

Then restore the desktop viewport before presenting.

**On failure:** fix the treatment and re-screenshot. Maximum 2 self-fix cycles total (across desktop and mobile). If issues remain after 2 cycles, present anyway and state the remaining known issues explicitly to the user.

### Step 3: Present to User

Present the change to the user.

**Chrome DevTools mode:**
Tell the user to look at their browser. Be specific about what was added and where:

"I've injected a [description of content block] [position relative to landmark element] on [page path]. Check your browser."

**Playwright mode:**
Take a screenshot of the current viewport (scroll to center the injected element if needed). Present the screenshot to the user:

"I've injected a [description of content block] [position relative to landmark element] on [page path]. Here's how it looks:"

[present screenshot]

Then ask for feedback (same in both modes):
"Does this placement work? I can:"
"- Move it (above/below/beside different elements)"
"- Restyle it (different size, color, spacing, pattern)"
"- Revise the copy (shorter, different headline, reframe)"
"- Try a completely different content block style"

### Step 4: Iterate

Based on user feedback, modify the injection. Each iteration:

1. **Remove the previous injection.** Use the browser MCP to find and remove the `proposed-change-block` element (or whatever class name was used).
   - Chrome DevTools: use Puppeteer DOM removal
   - Playwright: `browser_evaluate('document.querySelector(".proposed-change-block").remove()')`
2. **Apply the requested change:**
   - Reposition: change the insertion point, re-inject
   - Restyle: modify CSS properties, re-inject
   - Revise copy: update the headline or body text, re-inject
   - Change pattern: rebuild using a different content block structure, re-inject
3. **Present again.**
   - Chrome DevTools: describe what changed and ask for feedback.
   - Playwright: take a new screenshot, present it, describe what changed, ask for feedback.

Continue until the user:
- Approves: "Looks good," "That works," "Lock it," or similar affirmation
- Moves on: "Good enough," "Let's capture this," or similar

There is no maximum iteration count. The user controls when to stop.

### Step 5: Lock Final State

When the user approves:

1. Confirm: "Locking this version. I'll capture it as a standalone file and write the placement rationale."
2. Note the final state for Phase 3:
   - Final HTML of the injected element (including inline CSS)
   - The injected element's class/id (the selector Phase 3 uses to remove then re-inject it for the control screenshot, e.g. `proposed-change-block`)
   - Final insertion point (may have changed during iteration)
   - Final DOM path
   - If the change modified or replaced existing elements (not just inserted one), the original markup of those elements (so Phase 3 can restore the true unmodified control)
   - Iteration history: what was tried and what feedback led to each change (for placement.md)
