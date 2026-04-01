# Phase 3: Design Agent

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/conversion-playbook.md (sections 1-6 only), modules/lp-audit-taxonomy.md (construct mode: D4, D6, D9), templates/section-catalog.html (structural reference)
> **Input:** `.claude/deliverables/campaigns/<slug>/copy.md` (Phase 2 output)
> **Output:** `.claude/deliverables/campaigns/<slug>/page.html`

---

## Required Inputs

- `copy.md` in the campaign directory -- HARD REQUIREMENT. If missing: `[PRECONDITION FAILED]: Run Phase 2 (copy) first.`
- `modules/conversion-playbook.md` sections 1-6: Navigation, CTA Strategy, Form Strategy, Post-Submit Flow, Page Section Order, Mobile.
- `templates/section-catalog.html` -- structural reference for section layout patterns, CSS architecture, responsive behavior, and interaction patterns. Contains one HTML block per section type:variant combination.

## Optional Inputs

- Brand style guide in the campaign directory or provided by the human. If found, use it for colors, fonts, logo.
- If no brand guide exists, ask the human for: primary color (hex), secondary/accent color (hex), font preference, logo URL or file path.

## What NOT to Read

- Do NOT read positioning context files (company-identity.md, audience-messaging.md, etc.)
- Do NOT read the brief.md
- Do NOT read `modules/section-taxonomy.md` (section selection is the copy agent's job, not the design agent's)
- Do NOT read playbook sections 7+ (benchmarks, testing priorities, positioning docs integration)
- Stage isolation: the design agent builds from copy.md only. If something seems wrong with the copy, flag it but do not change it.

---

## Workflow

### Step 1: Read Copy

Read the full `copy.md` including frontmatter. Extract:
- The `sections` array from frontmatter (determines which sections to render and in what order)
- All section copy (each `## SectionName: variant-slug` heading and its body content)
- CTA button text (must be identical in all CTA placements)
- Form field count and type (from frontmatter or lightbox section)
- Any `[GAP]` markers (flag these to the human but still build the page)

### Step 2: Read Structural References

**From `modules/conversion-playbook.md` (sections 1-6 only):**
- Section 1: Navigation rules (no nav, logo only)
- Section 2: CTA placement (3 locations, lightbox interaction)
- Section 3: Form strategy (field count, multi-step rules, UX)
- Section 4: Post-submit flow (which option the brief specified)
- Section 5: Ordering constraints (hard rules and soft rules for section ordering)
- Section 6: Mobile rules (mobile-first, tap targets, load time)

**From `modules/lp-audit-taxonomy.md` (construct mode: D4, D6, D9):**

Read the Construct Mode section (table at bottom) plus the full dimension text for D4, D6, and D9. These dimensions contain best-practice constraints that apply during page construction:

| Dimension | Construct-mode constraint |
|-----------|--------------------------|
| D4: Page Structure | ATF must include all 5 elements: headline, subheader, visual, CTA, social proof micro-signal. BTF follows logical persuasion arc (value -> proof -> objections -> action). Subheadings must tell a coherent story when scanned independently. CTA at every 2-3 scroll heights. No navigation leaks on campaign LPs. |
| D6: CTA and Form Design | CTA must be the highest-contrast interactive element above the fold. Button text must pass the "I want to ___" test. Form fields: 3-5 ideal for lead gen, 7+ is an abandonment cliff. If brief specifies more fields (client override), implement but note the friction risk. Touch targets >= 44px on mobile. Inline validation preferred. |
| D9: Visual Design / UX | Clear visual eye path: headline -> visual -> subheader -> CTA. CTA button must be the most visually distinct element on page. Use product screenshots or dashboard visuals, not stock photography. Whitespace between sections prevents cognitive overload. Mobile-first: content adapts (not just reflows). Alt text on images, logical heading hierarchy (H1 > H2 > H3), keyboard navigability. |

These are construction constraints, not just QA checks. Apply them as you build each section.

**From `templates/section-catalog.html`:**
- Section layout patterns per type:variant combination (grid columns, spacing, alignment)
- Lightbox modal structure (overlay, blur, close button, form layout)
- Mobile vs. desktop responsive behavior (breakpoint patterns, responsive grid)
- CSS custom properties architecture (brand-overridable tokens)
- Component patterns: CTA buttons, form inputs, accordion, stat blocks, card grids
- Post-submit flow layout
- FAQ accordion pattern (expand/collapse)

The section catalog contains one HTML block per section type:variant. Each block includes HTML comment annotations explaining design rationale and variant-specific notes. Use the catalog's HTML patterns as structural starting points. Populate with copy content from copy.md. Adapt CSS custom properties to match the campaign's brand styling.

### ATF Design Constraints

These constraints apply to the hero/above-the-fold section of the HTML output.

**Negative space:** ATF elements (headline, hook line, subheadline, CTA, hero image) must have generous spacing. Minimum 16px vertical gap between text elements. Minimum 32px gap between the text column and the image/visual column. Background must not compete with text. No busy patterns, no low-contrast overlays. If the background is an image, it must have a solid or gradient overlay ensuring text contrast ratio >= 4.5:1.

**Hero image:** Should show the product in action (screenshot, GIF, or short video). If copy.md does not specify a hero image, use a dashed placeholder box matching the section-catalog.html hero pattern. Do not substitute abstract illustrations or stock photography. A clean placeholder is better than a misleading image.

**Nav bar (paid LP):** Zero navigation links. Logo only. No escape routes. Every element serves the single conversion goal specified in the brief.

**Nav bar (non-paid LP):** Maximum 2-4 navigation links + 1 primary CTA button. The primary CTA gets the greatest visual emphasis (filled button, contrasting color). Other nav links are text-only or outlined. Don't trigger analysis paralysis with excessive options.

**Which nav rule applies:** If the brief specifies `target_keywords` (indicating paid traffic), use the paid LP nav rule. If the brief does not specify keywords or explicitly notes organic/direct traffic, use the non-paid LP rule. When in doubt, default to zero nav (paid LP rule).

**Hook line rendering:** If copy.md includes a hook line (marked `[OPTIONAL]` in copy output), render it as a separate element between the headline and subheadline. Visually: smaller than the headline, larger than the subheadline, same color as headline. See section-catalog.html hero section for sizing reference. If copy.md does not include a hook line, omit the element entirely. Do not generate a hook line in the design phase.

**CTA button:** Must be the most visually prominent interactive element above the fold. Use the primary button style (filled, high contrast). If the wireframe specifies a lightbox trigger, the CTA onClick opens the lightbox. Do not render the form inline in the hero unless copy.md or the brief explicitly specifies inline form placement.

### Step 3: Resolve Brand Styling

Search for a brand style guide or design system. Check these locations in order:

1. **Context directory:** Glob the context directory (`.claude/context/` or the project's context path) for files matching `brand*`, `design-system*`, `style-guide*`, `brand-design*`. Also check for a companion `brand-components.html` file (exact name or matching `brand-components*`). This is an **exception to stage isolation** -- brand/design files are visual references, not positioning context.
2. **Campaign directory:** Check `.claude/deliverables/campaigns/<slug>/` for a brand guide provided alongside other campaign files.
3. **Human-provided:** If the human mentioned a brand file or design system path, read it.

If a brand file is found, read it in full. Extract and apply:
- Color palette (primary, secondary, neutral/grey scale, status colors)
- Typography (font family, size scale, weight rules, line-height, letter-spacing)
- Button component specs (sizes, padding, border-radius, hover/pressed/disabled states)
- Form input styles (height, padding, border, focus state, error state)
- Spacing system (grid base, section padding, content max-width)
- Border radius tokens
- Shadow tokens
- Navigation patterns (if brand has a standard nav structure like a corporate bar)
- Logo assets (URLs, variants for light/dark backgrounds)
- Anti-patterns (explicitly prohibited design choices)

If no brand file is found, ask the human for:
1. Primary brand color (hex)
2. Secondary/accent color (hex)
3. Font preference (or use a clean sans-serif default: Inter, DM Sans, or system fonts)
4. Logo: URL, file path, or "use placeholder"
5. "Do you have a brand design system or style guide file I should reference?"

Map brand colors to the section catalog's color roles:
- `#1A1A18` (dark/primary) -> primary brand dark or keep as-is for high contrast
- `#E85D3A` (accent/CTA) -> primary brand color for CTAs and highlights
- `#F5F0E8` / `#FFFDF9` (light backgrounds) -> adjust to complement brand palette
- `#8C8575` (muted text) -> keep neutral or adjust for brand warmth/coolness

If a brand design system specifies exact component specs (button heights, padding, radius, form input styles), use those values exactly. Do not approximate or "modernize" brand specs. The brand system is authoritative for all visual properties it defines.

**Brand component catalog detection:**

If a `brand-components.html` file was found during the glob above:
- This file IS the section catalog for this build. It replaces `templates/section-catalog.html` entirely.
- Read `brand-components.html` in full. It contains ready-to-use HTML/CSS snippets for the client's design system.
- Do NOT also read `templates/section-catalog.html`. The brand component library is authoritative. Using both would create competing pattern sources.
- The design agent assembles pages by selecting and adapting snippets from `brand-components.html`, following the component's CSS classes and structural patterns.

If no `brand-components.html` file was found:
- Use `templates/section-catalog.html` as the section catalog (default behavior, no change).

### Step 4: Build HTML

Produce a single HTML file with all CSS and JS inline. No external dependencies except Google Fonts (if a specific font is requested).

**Structural requirements:**
- Mobile-first responsive design (single breakpoint at 768px)
- Single-column layout on mobile, appropriate grid on desktop
- No external CSS frameworks, no external JS libraries
- All images referenced as placeholders (with alt text and dimensions) unless the human provides URLs
- Semantic HTML5 elements (header, main, section, footer)
- Page weight target: under 50KB HTML (before images)

**Section Rendering Loop (driven by copy.md frontmatter `sections` array):**

For each entry in copy.md frontmatter `sections` array:

1. Look up `{type}:{variant}` in the active section catalog:
      - If `brand-components.html` was detected in Step 3: match against brand component snippets using the `<!-- BRAND COMPONENT: ... -->` HTML comments from copy.md to identify the target component class(es). For compositions (multiple components), combine the relevant snippets.
      - If no brand component library: look up in `templates/section-catalog.html` (match via `data-variant` attribute or section comment block)
2. Read the catalog's HTML pattern for that variant. When using brand components, preserve the component's CSS classes exactly (e.g., `spg-hero`, `spg-card-grid--3`, `spg-btn--primary`). Do not rename or abstract brand classes.
3. Populate with copy content from the matching `## SectionName: variant-slug` heading in copy.md body
4. Apply brand colors, fonts, spacing from brand files in context directory
5. Apply responsive rules from conversion-playbook.md Section 6 (mobile)
6. Validate against ordering constraints in conversion-playbook.md Section 5 (flag violations but do NOT reorder -- reordering requires re-running Phase 2)
7. Write section HTML to page output

If a section `type:variant` combination does not exist in the active catalog:
- **Brand catalog active:** Check copy.md for a `<!-- BRAND COMPONENT: none ... -->` comment on this section. If present, build the section using only design tokens from `brand-design-system.md` (colors, typography, spacing, radii). Do not invent brand component classes. Flag the gap for brand system update.
- **Generic catalog active:** Build a reasonable HTML pattern following the catalog's annotation convention and CSS architecture. Flag the gap for catalog update.

The design agent validates that the section order in the final page.html matches copy.md's `sections` array exactly. If the design agent detects an ordering constraint violation, it flags the violation but does NOT reorder. Reordering is a Phase 2 (copy) concern.

**Per-section rendering notes:**

- **Header**: Logo only. No navigation links. Logo is non-clickable or links to `#` (not the main site).
- **Hero**: Use the recommended headline. Include other variants as HTML comments for A/B testing. Button triggers lightbox (JS onclick).
- **Lightbox form**: Triggered by any CTA button click (shared JS handler). Fixed overlay with backdrop blur. See section-catalog.html lightbox pattern.
- **FAQ/Objections**: Accordion with expand/collapse. JS-powered toggle. Only first item expanded by default.
- **Footer**: Minimal. Logo + copyright + legal links + required disclaimers.

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
- [ ] Every section in copy.md `sections` array has a rendered counterpart in page.html
- [ ] No section in page.html exists that is not in copy.md `sections` array
- [ ] Section order in page.html matches copy.md `sections` array exactly
- [ ] Hero headline matches exactly
- [ ] All CTA button instances use identical text
- [ ] Testimonial quote, name, title, company match exactly (if Testimonial section present)
- [ ] Stats match exactly (numbers, units, formatting) (if Quantified Proof section present)
- [ ] FAQ questions and answers match exactly (if Objection Handling section present)
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
