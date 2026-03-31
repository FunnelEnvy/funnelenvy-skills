# Phase 2: Inject -- Live Mode Only

**Purpose:** Build the proposed content block using the site's design tokens and inject it into the live DOM. Iterate with the user on placement, styling, and content until they approve.

**Applies to:** Live mode only. Static mode uses `static-build.md` instead.

---

## Required Inputs

- Design tokens, DOM insertion path, content block patterns, target section HTML (from Phase 1)
- Hypothesis text: proposed change, before/after copy (from orchestrator)
- `modules/conversion-playbook.md` (sections 1-6)
- `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)

## Outputs

- Injected content block visible in user's Chrome browser
- User approval of final placement and styling
- Final injection state (held in working memory for Phase 3)

**No files written to disk in this phase.** User iteration happens in the live browser.

---

## CRO Placement Principles

Apply these principles BEFORE building the content block. They determine where and how the element is placed.

### Visual Hierarchy (D8: Copy Quality and Readability)

The new element must NOT have higher visual weight than the primary CTA. It supports the conversion action, it does not compete with it.

Rules:
- Use the site's **secondary** emphasis patterns: lighter background shade, smaller heading size (h3 not h2), muted accent color
- Do NOT use the primary CTA color for any part of the injected element
- Do NOT use the site's largest heading size (h1) for the injected element's headline
- The CTA button extracted in Phase 1 defines the visual ceiling. Stay below it.

### Proximity to Intent Signal

Objection-handling content belongs NEAR the conversion point (form, CTA), not mid-page or in a disconnected sidebar.

Rules:
- "Near" means within 1 scroll-viewport of the conversion element, ideally visible simultaneously on desktop
- For /contact pages: immediately above or beside the form. NOT below the form (user has already scrolled past the decision point)
- For pricing pages: adjacent to the pricing table or tier comparison, not in a separate section
- For product pages: near the primary CTA, not buried in feature descriptions

### Attention Without Disruption (D1: Awareness-Stage Alignment)

The content block must be scannable. Users near a conversion point are in decision mode, not reading mode.

Rules:
- Short headline (under 8 words)
- 1-2 short sentences maximum (under 40 words total)
- Optional: one icon or visual anchor for scannability
- No paragraphs. No bullet lists longer than 3 items.
- The hypothesis may have a long "After" example. Distill it to the essential reframe. Document the distillation in placement.md (Phase 4).

### Contrast Calibration

The element must be noticed without looking like an ad, an alert, or an error message.

Rules:
- Use a DIFFERENT background from the surrounding section (subtle contrast: 5-15% lightness difference)
- OR use a subtle left border accent (3-4px, in a secondary brand color or neutral blue/gray)
- Do NOT use high-saturation backgrounds (red, orange, bright yellow)
- Do NOT use the site's warning/error color palette
- Do NOT use the exact same background as the surrounding section (the element would be invisible)

### Using Existing Patterns

If Phase 1 identified a content block pattern on the site (callout box, trust badge row, info block with icon), use that pattern's structure and styling as the base for the new element. Modifications:
- Keep the structural pattern (same border treatment, same padding, same layout)
- Replace the content with the hypothesis copy
- Adjust sizing if needed to fit the insertion context

If no suitable pattern was found: build a simple callout block with left border accent, using the site's secondary heading size and body text size.

---

## Steps

### Step 1: Build HTML/CSS for Content Block

Using the design tokens from Phase 1 (brand tokens take precedence over computed styles) and the CRO placement principles above:

1. Choose the structural pattern (existing site pattern or default callout block)
2. Write the HTML for the content block:
   - Semantic markup: `<div>` with a descriptive class (e.g., `proposed-change-block`)
   - Headline in the appropriate heading level (h3 or h4, never h1 or h2)
   - Body text in `<p>` tags
   - Optional icon or visual anchor if the site uses them
3. Write inline CSS matching the site's design tokens:
   - Use exact font-family, font-size, line-height from Phase 1 extractions
   - Use exact padding/margin values from the site's content blocks
   - Apply contrast calibration rules for background and border
4. Ensure the element uses native site styling only. No annotation borders, labels, or badges. The mockup should look like a real page element.

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
   - Final insertion point (may have changed during iteration)
   - Final DOM path
   - Iteration history: what was tried and what feedback led to each change (for placement.md)
