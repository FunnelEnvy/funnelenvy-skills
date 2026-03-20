# Experiment Mockup -- Shared Agent Rules

These rules apply to all agents spawned by the experiment-mockup skill. Read this file first before any phase-specific instructions.

---

## 1. Accuracy Over Completeness

- Never fabricate page structure, DOM selectors, or design token values. If you cannot determine a value, flag it explicitly.
- Every CSS property in the mockup must come from computed styles (live mode) or parsed stylesheets (static mode). Do not guess colors, fonts, or spacing.
- Every CRO placement decision must reference a specific principle from `modules/conversion-playbook.md` or `modules/lp-audit-taxonomy.md`. No unsourced placement rationale.
- If the hypothesis copy is too long for the insertion context, distill it. Document what was kept and cut in `placement.md`.

**Precedence:** accuracy > visual fidelity > completeness

---

## 2. Context Files

This skill does NOT read L0/L1 context files. The hypothesis from `experiment-roadmap.md` is the single source of truth for what to mock up. Re-reading context files risks contradicting the hypothesis.

**Exception: brand design files.** If brand files (`brand-design-system.md`, `brand-components.html`, or similar `brand*`/`design-system*`/`style-guide*` files) exist in the context directory, read them. These are visual references, not positioning context. They do not conflict with the hypothesis. Brand file tokens are authoritative for colors, typography, spacing, and component patterns. Computed/parsed styles fill gaps where the brand file is silent.

| File | Layer | How Used |
|------|-------|----------|
| `.claude/deliverables/experiment-roadmap.md` | Deliverable | Read: hypothesis source (page, change, copy, scores) |
| `.claude/context/brand-design-system.md` | Visual reference | Read (if exists): authoritative design tokens, color palette, typography, spacing |
| `.claude/context/brand-components.html` | Visual reference | Read (if exists): ready-to-use HTML/CSS component patterns |
| `.claude/deliverables/experiments/<slug>/mockup.html` | Deliverable | Write: standalone HTML mockup |
| `.claude/deliverables/experiments/<slug>/mockup-screenshot.png` | Deliverable | Write: browser screenshot (live mode only) |
| `.claude/deliverables/experiments/<slug>/placement.md` | Deliverable | Write: CRO placement rationale |

---

## 3. Module Dependencies

| Module | Sections | Used By |
|--------|----------|---------|
| `modules/conversion-playbook.md` | Sections 1-6 (navigation, CTA, form, post-submit, page section order, mobile) | inject.md, static-build.md |
| `modules/lp-audit-taxonomy.md` | D1 (Awareness-Stage Alignment), D3 (Message Match), D5 (Social Proof Strategy), D8 (Copy Quality) | inject.md, static-build.md, annotate.md |
| `modules/web-extract.md` | Full pipeline | static-build.md only |
| `modules/slugify.md` | Full rules | SKILL.md (hypothesis title to directory slug) |

Read modules at the start of the phase that needs them. Do not pre-load all modules.

---

## 4. Frontmatter Rules

All output files use YAML frontmatter (placement.md) or HTML comment metadata blocks (mockup.html). Required fields:

- `schema`: the schema name (`experiment-mockup` or `experiment-placement`)
- `schema_version`: `"1.0"`
- `hypothesis`: hypothesis number from experiment-roadmap.md
- `target_url`: the URL that was mocked up
- `mode`: `live` or `static`
- `generated_by`: `experiment-mockup v1.0.0`
- `last_updated`: ISO-8601 date

---

## 5. Content Integrity

- One hypothesis per invocation. Do not combine or batch.
- The hypothesis "Before"/"After" copy is the starting point, not the final copy. Distillation for the mockup context is expected and documented.
- The injected element must look native to the site. Style it to blend with the site's existing design patterns. No annotation borders, labels, or badges on the mockup itself.
- Match the target site's own design system. If brand files exist in the context directory, they ARE the authoritative design system. Do not impose your own aesthetic preferences.

---

## 6. Em Dashes

Never use em dashes. Use colons, commas, periods, or separate sentences.
