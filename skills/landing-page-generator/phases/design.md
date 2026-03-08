# Phase 3: Design Agent

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/conversion-playbook.md (sections 1-6 only), templates/wireframe.jsx (structural reference)
> **Input:** `.claude/deliverables/campaigns/<slug>/copy.md` (Phase 2 output)
> **Output:** `.claude/deliverables/campaigns/<slug>/page.html`

---

## Required Inputs

- `copy.md` in the campaign directory -- HARD REQUIREMENT. If missing: `[PRECONDITION FAILED]: Run Phase 2 (copy) first.`
- `modules/conversion-playbook.md` sections 1-6: Navigation, CTA Strategy, Form Strategy, Post-Submit Flow, Page Section Order, Mobile.
- `templates/wireframe.jsx` -- structural reference for layout, section ordering, interaction patterns, annotation notes.

## Optional Inputs

- Brand style guide in the campaign directory or provided by the human. If found, use it for colors, fonts, logo.
- If no brand guide exists, ask the human for: primary color (hex), secondary/accent color (hex), font preference, logo URL or file path.

## What NOT to Read

- Do NOT read positioning context files (company-identity.md, audience-messaging.md, etc.)
- Do NOT read the brief.md
- Do NOT read playbook sections 7+ (benchmarks, testing priorities, positioning docs integration)
- Stage isolation: the design agent builds from copy.md only. If something seems wrong with the copy, flag it but do not change it.

---

## Workflow

### Step 1: Read Copy

Read the full `copy.md` including frontmatter. Extract:
- All section copy (hero, social proof, problem/solution, proof, CTAs, FAQ, footer, lightbox, post-submit)
- CTA button text (must be identical in all 3 placements)
- Form field count and type (from frontmatter or lightbox section)
- Any `[GAP]` markers (flag these to the human but still build the page)

### Step 2: Read Structural References

**From `modules/conversion-playbook.md` (sections 1-6 only):**
- Section 1: Navigation rules (no nav, logo only)
- Section 2: CTA placement (3 locations, lightbox interaction)
- Section 3: Form strategy (field count, multi-step rules, UX)
- Section 4: Post-submit flow (which option the brief specified)
- Section 5: Section order (the 9-section sequence)
- Section 6: Mobile rules (mobile-first, tap targets, load time)

**From `templates/wireframe.jsx`:**
- Section layout patterns (grid columns, spacing, alignment)
- Lightbox modal structure (overlay, blur, close button, form layout)
- Mobile vs. desktop responsive behavior (max-width toggle pattern)
- Component patterns: annotation tags, strategy notes (strip these from production output), section labels, wireframe boxes (replace with real content), CTA buttons
- Post-submit flow layout (3-step grid)
- FAQ accordion pattern (expand/collapse)

The wireframe is an annotated reference. Use its spatial composition and interaction patterns. Strip all annotation components (AnnotationTag, StrategyNote, SectionLabel, WireframeBox placeholders) and replace with real content and production styling.

### Step 3: Resolve Brand Styling

Check for a brand style guide. If not found, ask the human for:
1. Primary brand color (hex)
2. Secondary/accent color (hex)
3. Font preference (or use a clean sans-serif default: Inter, DM Sans, or system fonts)
4. Logo: URL, file path, or "use placeholder"

Map brand colors to the wireframe's color roles:
- `#1A1A18` (dark/primary) -> primary brand dark or keep as-is for high contrast
- `#E85D3A` (accent/CTA) -> primary brand color for CTAs and highlights
- `#F5F0E8` / `#FFFDF9` (light backgrounds) -> adjust to complement brand palette
- `#8C8575` (muted text) -> keep neutral or adjust for brand warmth/coolness

### Step 4: Build HTML

Produce a single HTML file with all CSS and JS inline. No external dependencies except Google Fonts (if a specific font is requested).

**Structural requirements:**
- Mobile-first responsive design (single breakpoint at 768px)
- Single-column layout on mobile, appropriate grid on desktop
- No external CSS frameworks, no external JS libraries
- All images referenced as placeholders (with alt text and dimensions) unless the human provides URLs
- Semantic HTML5 elements (header, main, section, footer)
- Page weight target: under 50KB HTML (before images)

**Section build order (matches playbook Section 5):**

1. **Header**: Logo only. No navigation links. Logo is non-clickable or links to `#` (not the main site).

2. **Hero**: Headline + subheadline + CTA button. Button triggers lightbox (JS onclick). If copy.md has 3 headline options, use the recommended one. Include the other two as HTML comments for A/B testing.

3. **Social Proof Bar**: "Trusted by" + logo placeholders. Flex layout, centered. 2-row max on mobile (reduce to 3-4 logos if needed for mobile fit).

4. **Problem/Solution**: 3-card grid (1-column mobile, 3-column desktop). Pain headline + fix body per card.

5. **Quantified Proof**: Large-type stat numbers + testimonial. 2-column grid on desktop, stacked on mobile. Testimonial fully attributed.

6. **Mid-Page CTA**: Centered, background-differentiated section. Same CTA button text. Supporting micro-copy.

7. **How It Works** (if present in copy): 3-step numbered process. Horizontal on desktop, vertical on mobile.

8. **FAQ/Objections**: Accordion with expand/collapse. JS-powered toggle. Only first item expanded by default. All others collapsed.

9. **Final CTA Block**: High-contrast dark background. CTA button uses accent color. Strong visual break from prior sections.

10. **Footer**: Minimal. Logo + copyright + legal links + required disclaimers.

**Lightbox form:**
- Triggered by any CTA button click (shared JS handler)
- Fixed overlay with backdrop blur
- Centered modal card (max-width 440px)
- Close on backdrop click and close button
- Form fields per copy.md lightbox section
- Submit button echoes CTA value
- Micro-copy below submit
- On submit: prevent default, show confirmation state (in production this would POST to a form handler; for the prototype, show a success message or redirect placeholder)

**Post-submit flow:**
- If calendar: placeholder for calendar embed with comment explaining integration point
- If asset: immediate download link placeholder
- If thank-you: confirmation message with specific timeframe + nurture content link

### Step 5: Mobile Optimization Check

Before writing, verify:
- [ ] Single-column layout below 768px
- [ ] CTA buttons: full-width on mobile, minimum 44px height
- [ ] Form fields: full-width, minimum 44px height for tap targets
- [ ] Logo bar: wraps gracefully on mobile (2 rows max)
- [ ] Font sizes: minimum 14px body, 11px fine print
- [ ] No horizontal scrolling on any viewport width
- [ ] FAQ accordions are touch-friendly (full-width tap target)
- [ ] Lightbox: full-screen on mobile (no side margins cutting off content)

### Step 6: Copy Integrity Check

Verify all copy from copy.md is present and unmodified in the HTML:
- [ ] Hero headline matches exactly
- [ ] All 3 CTA button instances use identical text
- [ ] Testimonial quote, name, title, company match exactly
- [ ] Stats match exactly (numbers, units, formatting)
- [ ] FAQ questions and answers match exactly
- [ ] Footer disclaimers match exactly
- [ ] No copy was added that isn't in copy.md
- [ ] `[GAP]` markers converted to visible placeholder comments in HTML (e.g., `<!-- GAP: no named testimonial -->`)

### Step 7: Write Output

Write to `.claude/deliverables/campaigns/<slug>/page.html`

No frontmatter (it's HTML). Instead, include a comment block at the top:

```html
<!--
  Generated by: landing-page-generator/design
  Client: [name]
  Campaign: [slug]
  Date: [ISO-8601]
  Source: copy.md v[schema_version]

  A/B Test Headlines:
  - Option A (recommended): [headline]
  - Option B: [headline]
  - Option C: [headline]

  Gaps carried forward:
  - [any gaps from copy.md]
-->
```

### Step 8: Confirm

Tell the human:
- Page saved to `.claude/deliverables/campaigns/<slug>/page.html`
- Open in a browser to review
- Flag any `[GAP]` markers that appear as placeholders
- "Run `/landing-page-generator <company> <slug> --stage qa` to validate."

---

## CSS Architecture

Use CSS custom properties for brand theming. This makes A/B testing color variants trivial:

```css
:root {
  --color-primary: #1A1A18;
  --color-accent: #E85D3A;     /* Override with brand color */
  --color-bg: #FFFDF9;
  --color-bg-alt: #F5F0E8;
  --color-text: #1A1A18;
  --color-text-muted: #6B6B6B;
  --color-border: #E5E5E5;
  --font-heading: 'DM Sans', system-ui, sans-serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;
  --max-width: 780px;
  --section-gap: 64px;
  --mobile-break: 768px;
}
```

## Performance Rules

- No images embedded as base64 (use placeholder `<img>` with src comments)
- No external JS libraries
- Inline all CSS in a `<style>` tag in `<head>`
- Inline all JS in a `<script>` tag before `</body>`
- Minify nothing (human-readable output for review and editing)
- Target: page functional and styled with zero external requests (except Google Fonts if specified)
