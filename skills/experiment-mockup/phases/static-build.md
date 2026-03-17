# Static Build -- Fallback Mode

**Purpose:** Combined extract + build phase for when Chrome DevTools MCP is not available. Produces `mockup.html` without live iteration. Lower fidelity than live mode.

**Applies to:** Static mode only (DevTools MCP unavailable or `--static` flag set).

---

## Required Inputs

- Target URL (from orchestrator)
- Hypothesis text: proposed change, before/after copy (from orchestrator)
- Hypothesis number, name (from orchestrator)
- Output directory path (from orchestrator)
- `modules/web-extract.md` (extraction pipeline)
- `modules/conversion-playbook.md` (sections 1-6, CRO placement principles)
- `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)

## Outputs

- `.claude/deliverables/experiments/<slug>/mockup.html` (standalone self-contained HTML)
- Working state for Phase 4 (annotate.md): insertion point, design tokens, placement rationale

**No screenshot in static mode** (no browser to screenshot).

---

## Steps

### Step 1: Fetch Page HTML

Use `modules/web-extract.md` but prioritize raw HTML over markdown conversion. For this skill, we need the actual HTML structure and linked stylesheets, not a markdown summary.

Extraction approach:
1. **First try:** `curl -sL --max-time 15 [url]` to get raw HTML
2. If curl fails or returns empty/error: fall through to `modules/web-extract.md` Tier 0 (markdown.new) for at least a structural understanding of the page
3. If all tiers fail: STOP. Report: "Could not fetch [url]. The page may require authentication, be behind a firewall, or block automated requests."

From the raw HTML, also extract linked stylesheets:
- Find all `<link rel="stylesheet" href="...">` tags
- `curl` each stylesheet URL (resolve relative URLs against the page's base URL)
- Store the CSS content for Step 3

### Step 2: Identify Target Section

Parse the fetched HTML to find the section referenced in the hypothesis.

1. Search for conversion elements matching the hypothesis description:
   - `<form>` elements (look at action URL, input names, submit button text)
   - CTA buttons/links (class names with "cta", "btn", "demo", "trial", "contact"; text content matching conversion language)
   - Specific page regions mentioned in the hypothesis (e.g., "hero section", "pricing table", "testimonial area")

2. If multiple candidates found: ask the user for clarification. Example: "I found two forms on this page: a contact form in the main content area and a newsletter signup in the footer. Which one is the target for this hypothesis?"

3. If no candidates found: ask the user to describe the target area. Example: "I couldn't identify the target section from the HTML. Can you describe what's on the page near where the change should go?"

4. Once identified, extract:
   - The target section HTML (the `<section>` or container `<div>` that holds the conversion element)
   - The section above it (for surrounding context in the mockup)
   - The section below it (for surrounding context in the mockup)

### Step 3: Load Brand Design System (if available)

Glob the context directory (`.claude/context/`) for brand files matching `brand*`, `design-system*`, `style-guide*`. Also check for `brand-components*` (HTML component libraries).

If brand files are found, read them in full. Extract:
- Color palette (primary, accent, background, text colors with hex values and usage rules)
- Typography (font families, size scale, weight rules)
- Spacing system (section padding, inter-block spacing, content max-width)
- Button/CTA styles (background, color, radius, padding, hover states)
- Component patterns (callout boxes, cards, trust bars, testimonial blocks)
- Any color pairing rules or restrictions

**Brand tokens are authoritative.** When Step 4 parses CSS, brand file values take precedence. Parsed CSS only fills gaps where the brand file is silent. If a brand component library (HTML file) exists, prefer its component patterns over generic callout blocks.

If no brand files are found, proceed. All design tokens will come from parsed CSS in Step 4.

### Step 4: Extract Design Tokens from Stylesheets

Parse the site's CSS (from Step 1) to extract design tokens. This is less accurate than computed styles from DevTools.

**Colors:**
- Look for CSS custom properties (variables): `--color-primary`, `--color-secondary`, `--bg-*`, `--text-*`
- If no custom properties: find the most-used color values in the stylesheet (body color, heading color, link color, button background)
- Extract background colors for sections, cards, and callout elements

**Typography:**
- `font-family` declarations on `body`, `h1`-`h3`, and `.btn`/button selectors
- `font-size` values for headings and body text
- `font-weight` values for headings vs body

**Spacing:**
- Most common `padding` and `margin` values on section and container elements
- `gap` values if flexbox/grid is used

**Button/CTA styles:**
- Find the primary button style (`.btn-primary`, `[type="submit"]`, or the most prominently styled button class)
- Extract: background-color, color, font-size, padding, border-radius, box-shadow

**Uncertainty handling:** For any token you cannot confidently extract, use a reasonable default and flag it:
- Default body font: `system-ui, -apple-system, sans-serif`
- Default body size: `16px`
- Default heading weight: `700`
- Default section padding: `48px 24px`
- Flag each default in a comment: `/* DEFAULT - could not extract from stylesheet */`

### Step 5: Build mockup.html

Apply the same CRO placement principles as live mode (from `modules/conversion-playbook.md` and `modules/lp-audit-taxonomy.md`):

- Visual hierarchy: new element subordinate to CTA
- Proximity: near the conversion element, not mid-page
- Attention: scannable, short headline, 1-2 sentences
- Contrast: subtle background or border accent, not an alert

Build the content block:
1. Choose a structural pattern. If a brand component library was loaded in Step 3, use its component patterns. Otherwise, if the extracted HTML contains callout boxes, trust blocks, or info cards, replicate that pattern. Otherwise, use a simple left-border callout.
2. Write the HTML for the hypothesis's proposed change, distilled for scannability.
3. Style using brand tokens (Step 3) first, then extracted design tokens (Step 4) for gaps. Use flagged defaults where both sources are silent.
4. Ensure the element uses native site styling only. No annotation borders, labels, or badges.

Assemble the standalone HTML file:

```html
<!--
  schema: experiment-mockup
  schema_version: "1.0"
  hypothesis: [number]
  hypothesis_title: "[name]"
  target_url: "[url]"
  insertion_point: "[descriptive location]"
  mode: static
  generated_by: experiment-mockup v1.0.0
  last_updated: [YYYY-MM-DD]
-->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mockup: [hypothesis name] (static)</title>
  <style>
    /* Reset */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: [extracted or default font];
      font-size: [extracted or default size];
      line-height: [extracted or default line-height];
      color: [extracted or default color];
      background-color: [extracted or default bg];
    }

    .mockup-container {
      max-width: [extracted or 1200px default];
      margin: 0 auto;
    }

    /* Section styles from extracted CSS */
    [section-specific CSS]
  </style>
</head>
<body>
  <div class="mockup-container">
    <!-- Section above (surrounding context) -->
    [cleaned HTML of section above]

    <!-- Target section with proposed change -->
    [cleaned HTML of target section with injected content block]

    <!-- Section below (surrounding context) -->
    [cleaned HTML of section below]
  </div>
</body>
</html>
```

Requirements:
- ALL CSS inline. Zero external references.
- Remove `<script>` tags from extracted HTML.
- Keep image `src` as absolute URLs.
- Under 50KB HTML (excluding image URLs).

### Step 6: Write Files and Report

1. Create the output directory: `.claude/deliverables/experiments/<slug>/`
2. Write `mockup.html` to the output directory.
3. Report to the user:

"Static mockup built for hypothesis #[N]: [name]"
"Written to: [output directory]/mockup.html"
""
"Open the file in a browser to see the proposed change in context."
""
"Note: This mockup was built from static HTML extraction, so some visual details may differ from the live site. For interactive mockups with real computed styles, configure Chrome DevTools MCP."

### Step 7: Prepare State for Phase 4

Pass to annotate.md:
- Insertion point description (where the element was placed)
- Design tokens used (with flags for defaults)
- Which CRO principles drove placement
- The final mockup copy (verbatim)
- That this was static mode (affects what annotate.md writes about iteration history)
