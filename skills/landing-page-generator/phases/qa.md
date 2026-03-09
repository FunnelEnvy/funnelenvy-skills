# Phase 4: QA Validator

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/conversion-playbook.md (Section 9: QA Checklist)
> **Input:** `.claude/deliverables/campaigns/<slug>/brief.md` + `copy.md` + `page.html` (whichever exist)
> **Output:** `.claude/deliverables/campaigns/<slug>/qa-report.md`

---

## Required Inputs

At least one of `copy.md` or `page.html` must exist in the campaign directory. If neither exists: `[PRECONDITION FAILED]: Nothing to QA. Run Phase 2 (copy) or Phase 3 (design) first.`

`brief.md` must exist for reference (target keywords, CTA text, banned terms, required disclaimers, form strategy).

---

## Workflow

### Step 1: Load Files

1. Read `brief.md` frontmatter + full body. Extract: target keywords, CTA text, banned terms list, required disclaimers, form field count, post-submit type.
2. Read `copy.md` if it exists.
3. Read `page.html` if it exists.
4. Read `modules/conversion-playbook.md` Section 9 (QA Checklist) for the complete checklist.

### Step 2: Run Copy QA (against copy.md)

Skip this section if copy.md does not exist.

| # | Check | How to Verify | Result |
|---|-------|--------------|--------|
| C1 | Headline message-matches target keywords | Compare hero headlines against brief's `target_keywords`. At least one keyword must appear in the recommended headline (exact match or close semantic match). | PASS / FAIL |
| C2 | Proof points in 4+ sections | Count sections containing at least one named metric, case study, or testimonial. Required in: hero, problem/solution, quantified proof, FAQ. | PASS / FAIL + count |
| C3 | Same CTA text in 3 locations | Search for the brief's `cta_text` in hero, mid-page, and final CTA sections. Must be identical in all 3. | PASS / FAIL + locations found |
| C4 | Zero banned terms | Search copy for every term in the brief's banned terms list. Case-insensitive. | PASS / FAIL + terms found |
| C5 | Required disclaimers present | Check footer section for each required disclaimer from the brief. | PASS / FAIL + missing items |
| C6 | Named testimonial with full attribution | At least one testimonial with name + title + company. All three required. | PASS / FAIL |
| C7 | Headlines under 10 words | Count words in each headline option. All must be under 10. | PASS / FAIL + word counts |
| C8 | No competing CTAs | Search for secondary action language ("Learn more," "Read our blog," "Download," etc.) alongside the primary CTA. One action only. | PASS / FAIL |
| C9 | Voice consistency | Spot-check 3 sections against the brief's voice rules. Flag any "Doesn't Sound Like" language. | PASS / FAIL + flagged phrases |
| C10 | [GAP] markers documented | List all `[GAP]` markers remaining in copy.md. These are known weaknesses, not failures. | INFO |

### ATF Copy Checks (6 checks)

These checks apply to the above-the-fold section of copy.md and/or page.html.

**ATF-1: Header Specificity**
Does the H1 contain a concrete, specific benefit? Flag if it uses any banned vague patterns: "Transform," "Revolutionize," "Unlock," "Empower," "Streamline," "Next-generation," "World-class," "Cutting-edge," "Best-in-class."
Run the litmus test: could a competitor use this exact headline? If yes, FAIL.
- Pass: Specific benefit named
- Fail: Vague or generic language detected

**ATF-2: Bold Claim Sourced**
If the H1, hook line, or subheader makes a quantitative claim (percentage, time saved, cost reduction, multiplier), is it traceable to a proof point ID in the brief or L0?
- Pass: Claim traces to a verified or supported proof point
- Pass (no claim): No quantitative claim present (not required, just checked when present)
- Fail: Quantitative claim with no traceable source

**ATF-3: Objection Addressed**
Does the ATF copy (headline, hook, or subheader) address the target persona's primary challenge or a likely buying objection?
Cross-reference: brief.md target_persona -> audience-messaging.md persona primary_challenge.
- Pass: Primary objection addressed in ATF
- Warn: No objection handling detected (acceptable if bold claim is strong)
- Fail: ATF copy doesn't connect to persona's challenges at all

**ATF-4: CTA Narrative Test**
Read the primary CTA button text in isolation. Is it generic?
Flag any of: "Get Started," "Learn More," "Request Demo," "Contact Us," "Sign Up," "Submit."
Then read the CTA after the headline. Does it feel like the natural next step?
- Pass: CTA is specific and continues the headline narrative
- Fail: CTA is generic or disconnected from headline

**ATF-5: Persona Alignment**
Does the ATF copy use the target persona's language and reference their world?
Cross-reference: brief.md target_persona -> audience-messaging.md persona role, segment.
- Pass: Copy speaks to a specific role/context
- Fail: Copy addresses "everyone" or uses internal product terminology instead of buyer language

**ATF-6: Subheader Completeness**
Does the subheader accomplish both jobs: (1) explain what the product is (category) and (2) explain how the headline's claim is achievable (mechanism/features)?
- Pass: Both jobs covered in 1-2 sentences
- Warn: Only one job covered
- Fail: Subheader is missing, vague, or longer than 2 sentences

### Step 3: Run Design QA (against page.html)

Skip this section if page.html does not exist.

| # | Check | How to Verify | Result |
|---|-------|--------------|--------|
| D1 | No site navigation | Search for `<nav>` elements or link clusters in the header. Only a logo should be present. | PASS / FAIL |
| D2 | No footer links beyond legal | Check footer for links. Only Privacy Policy, Terms, and required disclaimers allowed. No sitemap, social, blog links. | PASS / FAIL + extra links found |
| D3 | CTA buttons in 3 locations | Search for CTA button elements. Must appear in hero, mid-page, and final block sections. | PASS / FAIL + count |
| D4 | CTA triggers lightbox | Check for JS event handler on CTA buttons that shows a modal/overlay. Look for onclick handlers, modal toggle functions, or equivalent. | PASS / FAIL |
| D5 | Correct form field count | Count input/select elements in the lightbox form. Must match brief's `form_strategy.fields`. | PASS / FAIL + expected vs actual |
| D6 | Single-column on mobile | Check CSS media queries for mobile layout rules. Look for grid-template-columns, flex-direction changes at mobile breakpoint. | PASS / FAIL |
| D7 | Full-width CTA on mobile | Check CSS for CTA button width rules at mobile breakpoint. Should be 100% or full-width. | PASS / FAIL |
| D8 | Copy matches copy.md | Spot-check: hero headline, testimonial quote, 2 stat numbers, 1 FAQ question, footer disclaimer. All must match exactly. | PASS / FAIL + mismatches |
| D9 | Required disclaimers in footer | Check HTML footer for each required disclaimer. | PASS / FAIL + missing items |
| D10 | FAQ accordion functional | Check for JS expand/collapse logic on FAQ section. | PASS / FAIL |
| D11 | Lightbox close behavior | Check for close-on-backdrop-click and close button handlers. | PASS / FAIL |
| D12 | A/B headline variants preserved | Check HTML comments for alternative headline options. | PASS / FAIL |

### Step 4: Cross-Check (when both copy.md and page.html exist)

| # | Check | How to Verify | Result |
|---|-------|--------------|--------|
| X1 | All copy.md content in HTML | Systematically compare each section's text content. Flag any additions, deletions, or modifications. | PASS / FAIL + diffs |
| X2 | No copy added by design agent | Search HTML for text content not present in copy.md (excluding structural labels and HTML comments). | PASS / FAIL |

### Step 5: Write Report

Write to `.claude/deliverables/campaigns/<slug>/qa-report.md`:

```yaml
---
schema: qa-report
schema_version: "1.0"
client: <company-name>
campaign: <campaign-slug>
files_checked:
  - copy.md
  - page.html
copy_checks: <pass-count>/<total>
design_checks: <pass-count>/<total>
cross_checks: <pass-count>/<total>
overall: <PASS|FAIL>
generated_by: "landing-page-generator/qa"
last_updated: <ISO-8601>
---
```

Body format:

```markdown
# QA Report: [Client] / [Campaign]

## Summary

[X] of [Y] checks passed. [Overall PASS or FAIL with specific failures listed.]

## Copy QA

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Headline message match | PASS | "interim cfo" appears in Option B |
| C2 | ... | ... | ... |

## Design QA

| # | Check | Result | Notes |
|---|-------|--------|-------|

## Cross-Check

| # | Check | Result | Notes |
|---|-------|--------|-------|

## Gaps Carried Forward

[List all [GAP] markers from copy.md and page.html]

## Recommended Fixes

[For each FAIL, explain exactly what's wrong and which file to edit]
```

### Step 6: Confirm

Present results summary to the human:
- Overall PASS or FAIL
- Count of passed/failed checks
- For any FAILs: explain the fix
- If all pass: "Page is ready for review and deployment."

---

## QA Does Not Run as a Subagent

QA is lightweight enough to run inline in the orchestrator context. No need to spawn a separate agent. This saves ~20K tokens of agent overhead. The orchestrator loads agent-header.md + this file and executes directly.
