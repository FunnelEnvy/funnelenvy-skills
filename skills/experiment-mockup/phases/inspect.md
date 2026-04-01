# Phase 1: Inspect -- Live Mode Only

**Purpose:** Navigate to the target page, locate the exact DOM region where the change should be injected, and extract the computed styles of surrounding elements so the injected content matches the site's design language.

**Applies to:** Live mode only. Static mode skips this phase entirely.

---

## Required Inputs

- Target URL (from orchestrator)
- Hypothesis text (from orchestrator): page, proposed change, current state, before/after copy

## Outputs

- Design tokens (held in working memory for Phase 2)
- DOM insertion path (held in working memory for Phase 2)
- Content block patterns identified on the page (held in working memory for Phase 2)
- Target section HTML (held in working memory for Phase 2)

**No files written to disk in this phase.** All outputs are operational state passed to Phase 2.

---

## Steps

### Step 1: Navigate to Target Page

Use the browser MCP to open the target URL.

- Chrome DevTools mode: navigate using DevTools MCP tools (the page opens in the user's Chrome)
- Playwright mode: navigate using Playwright MCP tools (browser_navigate; the page opens in managed Chromium)

Wait for full page load:
- Document ready state
- Network idle (no pending requests for 500ms+)

If the page fails to load (timeout, 404, connection refused): STOP. Report the error to the user. Do not proceed.

### Step 2: Locate Target Section

The hypothesis specifies a page and a general placement (e.g., "above or adjacent to the form on /contact," "hero section headline on /pricing").

Use the browser MCP to locate the target area:

1. **Find the primary conversion element** on the page. Query the DOM for:
   - `form` elements (contact forms, signup forms, demo request forms)
   - Elements with CTA-like attributes: buttons with submit-related text, links with class names containing "cta," "btn-primary," "demo," "trial," "contact"
   - If the hypothesis mentions a specific element type, prioritize that

2. **Identify the containing section.** Walk up the DOM tree from the conversion element to find the semantic container:
   - Look for `<section>`, `<div>` with a semantic class name, or `<main>` children
   - The containing section is the unit we'll work within

3. **Map surrounding content blocks.** For the containing section, identify:
   - What content block is directly above it
   - What content block is directly below it
   - Whether there's a sidebar or adjacent column
   - The DOM path to each: e.g., `main > section:nth-child(3) > div.form-wrapper`

4. **Note the DOM insertion path.** Record the specific CSS selector or DOM path where the new content block should be inserted. Format: parent selector + position (e.g., "Insert as first child of `section.contact-area`" or "Insert before `div.form-container` inside `section.contact-area`").

### Step 3: Load Brand Design System (if available)

Glob the context directory (`.claude/context/`) for brand files matching `brand*`, `design-system*`, `style-guide*`. Also check for `brand-components*` (HTML component libraries).

If brand files are found, read them in full. Extract:
- Color palette (primary, accent, background, text colors with hex values and usage rules)
- Typography (font families, size scale, weight rules)
- Spacing system (section padding, inter-block spacing, content max-width)
- Button/CTA styles (background, color, radius, padding, hover states)
- Component patterns (callout boxes, cards, trust bars, testimonial blocks)
- Any color pairing rules or restrictions

**Brand tokens are authoritative.** When Step 4 extracts computed styles, brand file values take precedence. Computed styles only fill gaps where the brand file is silent (e.g., a specific element's margin that the brand system doesn't define).

If no brand files are found, proceed. All design tokens will come from computed styles in Step 4.

### Step 4: Extract Design Tokens

For the elements surrounding the insertion point, read computed styles via the browser MCP. Extract:

**Colors:**
- `background-color` of the parent section
- `background-color` of adjacent content blocks
- `color` of headings (h1, h2, h3) within the target section
- `color` of body text (p elements) within the target section
- `border-color` of any bordered elements (cards, callout boxes)
- `background-color` and `color` of the primary CTA button

**Typography:**
- `font-family` for headings and body text
- `font-size` for h1, h2, h3, p, and button/a.cta within the target section
- `font-weight` for headings vs body text
- `line-height` for body text
- `letter-spacing` if non-default on headings

**Spacing:**
- `padding` on the parent section
- `margin` between adjacent content blocks
- `gap` if the section uses flexbox or grid

**Layout:**
- `display`, `flex-direction`, `grid-template-columns` if applicable
- `max-width` of the content container (important for matching content width)

**Borders and effects:**
- `border-radius` on cards, callout boxes, or content containers
- `border-width` and `border-style` on bordered elements
- `box-shadow` on elevated elements

**CTA styling (critical: we must NOT compete with this):**
- Full computed style of the primary CTA button: `background-color`, `color`, `font-size`, `font-weight`, `padding`, `border-radius`, `border`, `box-shadow`, `text-transform`
- This is extracted so Phase 2 can ensure the injected element uses LOWER visual weight

**Playwright mode note:** Computed styles are extracted via browser_evaluate() executing window.getComputedStyle() in the page context. The output is functionally identical to Chrome DevTools' direct CDP access. Extract all tokens in a single evaluate() call to minimize tool call overhead:

```javascript
browser_evaluate(`
  JSON.stringify({
    body: window.getComputedStyle(document.body),
    heading: window.getComputedStyle(document.querySelector('h2')),
    // ... additional elements per the token categories above
  })
`)
```

### Step 5: Identify Existing Content Block Patterns

Look for reusable visual patterns already on the page that could serve as structural templates for the new element. The goal: the injected content should feel native to the site, not inserted.

Scan for:
- **Callout boxes:** Elements with a distinct background color, border, or border-left accent containing a heading + short text
- **Trust badges / logo bars:** Rows of logos or icons with optional label text
- **Testimonial cards:** Quoted text with attribution (name, title, company)
- **Info blocks with icons:** Icon + heading + description in a grid or flex layout
- **Sidebar panels:** Narrow content blocks adjacent to the main content area
- **Feature cards:** Bordered or shadowed containers with icon + title + description

For each pattern found, note:
- The DOM structure (tag hierarchy)
- Key CSS properties that define the pattern (background, border, padding, layout)
- Where on the page it appears

If no suitable pattern exists on the target page, check the homepage and about page for patterns (navigate to them, scan, return to the target page).

### Step 6: Compile Working State

Organize the extracted data into a structured working state for Phase 2:

```
BRAND SYSTEM: [brand-design-system.md found | brand-components.html found | none]

TARGET SECTION:
- DOM path: [selector]
- Insertion point: [where to insert relative to what element]
- Section HTML (outer): [the outerHTML of the target section]

DESIGN TOKENS (brand = from brand file, computed = from DevTools):
- Primary font: [family]
- Heading font: [family, if different]
- Body text: [size]px / [weight] / [line-height] / [color]
- H2: [size]px / [weight] / [color]
- H3: [size]px / [weight] / [color]
- Section background: [color]
- Content container max-width: [value]
- Content padding: [value]
- Inter-block spacing: [value]
- CTA button: bg [color], text [color], [size]px, [weight], radius [value], shadow [value]

CONTENT BLOCK PATTERNS:
- Pattern 1: [name] -- [DOM structure summary] -- [key CSS]
- Pattern 2: [name] -- [DOM structure summary] -- [key CSS]
- [none found on target page -- checked homepage: Pattern X found]

SURROUNDING CONTEXT:
- Above: [description of content block above insertion point]
- Below: [description of content block below insertion point]
- Adjacent: [sidebar or column content, if any]
```

This working state is passed to Phase 2. Not written to disk.
