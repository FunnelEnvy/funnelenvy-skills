# Phase 4: QA Validator

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/conversion-playbook.md (Section 9: ATF rules, Section 10: Line-Level Rules and Feature Blocks, Section 11: QA Checklist), modules/lp-audit-taxonomy.md (10-dimension scoring framework), modules/section-taxonomy.md (ordering constraints, selection signal validation)
> **Input:** `.claude/deliverables/campaigns/<slug>/brief.md` + `copy.md` + `page.html` (whichever exist)
> **Output:** `.claude/deliverables/campaigns/<slug>/qa-report.md`

---

## Required Inputs

At least one of `copy.md` or `page.html` must exist in the campaign directory. If neither exists: `[PRECONDITION FAILED]: Nothing to QA. Run Phase 2 (copy) or Phase 3 (design) first.`

`brief.md` must exist for reference (target keywords, CTA text, banned terms, required disclaimers, form strategy).

`modules/section-taxonomy.md` -- for variant-signal alignment validation and ordering constraint reference.

---

## Workflow

### Step 1: Load Files

1. Read `brief.md` frontmatter + full body. Extract: target keywords, CTA text, banned terms list, required disclaimers, form field count, post-submit type.
2. Read `copy.md` if it exists.
3. Read `page.html` if it exists.
4. Read `modules/conversion-playbook.md` Section 11 (QA Checklist) for the complete checklist, and Sections 9 and 10 for the rules Step 4e audits against.
5. Read `modules/section-taxonomy.md` for section selection signals and ordering constraints.

### Step 2: Run Copy QA (against copy.md)

Skip this section if copy.md does not exist.

| # | Check | How to Verify | Result |
|---|-------|--------------|--------|
| C1 | Headline message-matches target keywords | Compare hero headlines against brief's `target_keywords`. At least one keyword must appear in the recommended headline (exact match or close semantic match). | PASS / FAIL |
| C2 | Proof points in 4+ sections | Count selected sections containing at least one named metric, case study, or testimonial. Proof required in Hero and any Quantified Proof, Testimonial, or Objection Handling sections present. | PASS / FAIL + count |
| C3 | Same CTA text in all CTA locations | Search for the brief's `cta_text` in all CTA sections listed in copy.md frontmatter `sections` array (Hero, Mid-Page CTA, Final CTA). Must be identical in all. | PASS / FAIL + locations found |
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
First, the header-only litmus test (conversion-playbook.md Rule 1, test 1): cover everything but the H1. Read alone, does it say exactly what is sold? A question, slogan or pain statement on its own FAILS here, whatever the subheader says.
Then: does the H1 contain a concrete, specific benefit? Flag if it uses any banned vague patterns: "Transform," "Revolutionize," "Unlock," "Empower," "Streamline," "Next-generation," "World-class," "Cutting-edge," "Best-in-class."
Run the litmus test: could a competitor use this exact headline? If yes, FAIL.
- Pass: Read alone, the H1 says what is sold, and names a specific benefit
- Fail: The H1 alone does not say what is sold, or vague or generic language detected

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
| D3 | CTA buttons in expected locations | Search for CTA button elements. Must appear in all CTA sections from copy.md frontmatter `sections` array. | PASS / FAIL + count |
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
| X1 | All copy.md content in HTML | For each section in copy.md frontmatter `sections` array, compare the section's text content against the corresponding `<section>` in page.html. Flag any additions, deletions, or modifications. | PASS / FAIL + diffs |
| X2 | No copy added by design agent | Search HTML for text content not present in copy.md (excluding structural labels and HTML comments). No section in page.html should exist that is not in copy.md `sections` array. | PASS / FAIL |

### Step 4b: Composable Section Validation

Six checks that validate the composable section system across copy.md and page.html.

**CS-1: Section Parity Check**
- Every section in copy.md frontmatter `sections` array has a corresponding rendered `<section>` in page.html
- No `<section>` in page.html exists that is NOT in copy.md `sections` array (prevents design agent from freelancing)
- Section order in page.html matches copy.md `sections` array exactly
- Result: PASS or FAIL

**CS-2: Variant-Signal Alignment Check**
For each section in copy.md `sections` array, verify the selected variant is consistent with the brief's context signals and L0/L1 frontmatter. Read brief.md frontmatter + L0/L1 frontmatter for this check.

Flag examples:
- Hero variant is `proof-lead` but proof_points verified < 2 -> FLAG
- Social Proof Bar included but no recognizable logos indicated in L0 proof point registry -> FLAG
- Problem Framing included but `traffic_awareness_stage` = product_aware or most_aware -> FLAG
- Pricing Preview omitted but company has public pricing or `offer_type` = quote -> FLAG
- Comparison Table included but no competitive keywords in brief and no competitive search intent -> FLAG

Read `modules/section-taxonomy.md` selection signals as the reference for what signals each section/variant requires.
- Result: count of flags (0 = clean)

**CS-3: Ordering Constraint Check**
Validate all 10 hard rules from `modules/section-taxonomy.md` / `modules/conversion-playbook.md` Section 5 against the actual section sequence in copy.md and page.html.
- Any hard rule violation = QA FAIL
- Validate 6 soft rules. Soft rule violations = flagged as warnings, not failures
- Result: hard violation count + warning count

**CS-4: Objection Coverage Check**
Read `audience-messaging.md` objection inventory (body section). Verify every objection is either:
- (a) addressed inline in a section body (identified by `<!-- Inline objection: addresses "..." -->` HTML comment in copy.md), OR
- (b) included in the Objection Handling section (Pattern B), OR
- (c) explicitly noted as out-of-scope in the brief's `gaps` field

Unaddressed objections = FLAG
- Result: "X/Y addressed" (X addressed out of Y total)

**CS-5: CTA Consistency Check**
- All CTA button text instances on the page use the same action text
- No competing CTAs (different goals/actions on the same page)
- Validates hard rule #10 from ordering constraints
- Result: PASS or FAIL

**CS-6: Proof Adjacency Check**
- Proof elements (logos, stats, testimonials) near CTA blocks do not visually compete
- Social proof bar uses grayscale/muted treatment (not colorful logos)
- This is a design check on page.html, not a copy check
- Validates hard rule #9 from ordering constraints
- Result: PASS or FLAG (visual inspection)

### Step 4c: Taxonomy Dimension Scoring

After completing the Section 11 checklist, run the generated LP artifacts through the 10-dimension audit taxonomy. This is a holistic quality assessment layered on top of the prescriptive checklist.

**Inputs for scoring:**
- `brief.md` (for D1 awareness stage, D3 message match, D6 form strategy)
- `copy.md` (for D2 value prop, D4 structure, D5 social proof, D7 persuasion, D8 copy quality, D10 differentiation)
- `page.html` (for D4 structure, D6 CTA visibility, D9 visual/UX)
- `.claude/context/` L0 + L1 frontmatter (for context-dependent checks in D5, D7, D10)

**Scoring process:**
1. Classify page type from the brief (paid search LP, paid social LP, homepage, product page, long-form sales page, pricing page).
2. Apply context-dependent weighting from the taxonomy's weighting table. Priority dimensions get full assessment. Deprioritized dimensions get a quick pass.
3. Score each of the 10 dimensions as Strong / Needs Work / Missing.
4. For each "Needs Work" or "Missing" dimension, write one specific recommendation with a reference to the artifact and line/section where the issue appears.
5. Any dimension scoring "Missing" is a QA blocker. Set `overall: FAIL` if any dimension is Missing.

**Scoring does NOT re-read context file bodies.** Read frontmatter only (~200 tokens per file) for D5/D7/D10 context checks. The copy and brief artifacts contain enough information for the remaining dimensions.

**Token budget:** The taxonomy module is ~4,800 tokens plus ~3K for section-taxonomy.md. QA runs inline, so this is absorbed by the orchestrator's context window. Total QA token cost: ~25K with composable section checks, before Step 4e. The two gate subagents add an estimated 30-50K (not measured).

### Step 4d: Brand Component Validation (conditional)

**Gate:** Read copy.md frontmatter. If `brand_design_system` field is present, run this step. If absent, skip entirely -- no brand constraints apply.

When running, also read:
- The `brand-design-system.md` file named in copy.md frontmatter `brand_design_system` field (from `.claude/context/` or client context directory)
- The `brand-components.html` file named in copy.md frontmatter `brand_components_html` field

| Check | What | How | Pass/Fail |
|-------|------|-----|-----------|
| BC-1 | CSS class compliance | Every `<section>` in page.html that has a corresponding `<!-- BRAND COMPONENT: ... -->` comment in copy.md uses CSS classes from `brand-components.html`. Grep page.html for brand component class names. | FAIL if any section uses generic/invented classes when a brand component was matched |
| BC-2 | No generic fallback when brand exists | No section in page.html uses generic styles from `templates/section-catalog.html` when a brand component match exists for that section in copy.md | FAIL if design agent mixed catalogs |
| BC-3 | Constraint compliance | For each section with constraints noted in the `<!-- BRAND COMPONENT: ... | CONSTRAINTS: ... -->` comment: verify page.html respects the constraint (item counts, approximate character limits reflected in rendered content) | FAIL if a card grid exceeds max items, if text visibly overflows component boundaries |
| BC-4 | Design token compliance | Compare CSS custom properties and inline styles in page.html against `brand-design-system.md` frontmatter tokens: colors (primary, secondary, neutral), font families, font sizes, border-radius values, spacing units | FAIL if page.html uses colors, fonts, or radii not in the brand design system |
| BC-5 | Anti-pattern compliance | Read `brand-design-system.md` for any `anti_patterns` or `prohibited` section. Check page.html does not violate listed prohibitions (e.g., no red background fills, no casual language in CTAs, specific radius values) | FAIL if any anti-pattern present in page.html |
| BC-6 | Degradation rationale | Read `component_degradations` from copy.md frontmatter. Each entry must have a non-empty `reason` field that explains why the degradation occurred. Cross-reference: if a degradation says `level: variant_degradation`, verify page.html uses the `resolved_variant`, not the `original_variant` | FAIL if any degradation lacks rationale or if page.html contradicts the resolution |
| BC-7 | Inferred value flagging | If `brand-design-system.md` contains any values marked `[INFERRED]` or with confidence qualifiers, check that the corresponding page.html usage is flagged in the QA report for client verification | WARN (not FAIL) -- these are flagged, not blocked |

**Scoring:** BC-1 through BC-6 are pass/fail. BC-7 is warn-only. Record results in the QA report alongside existing check groups.

### Step 4e: Independent Review Gates

The checks above verify the playbook. These four gates judge the copy. Every copy pass gets all four, and they run again every time the copy changes.

They exist because a writer's own review rubber-stamps its work. The writer knows the brief, so it cannot see a name the page never introduced. And a review that asks "is this line understood?" passes lines that are perfectly clear and add nothing. The gates ask the questions the writer cannot.

**Independence rule.** No gate runs in the QA context. It may have written or revised copy this session, and it has read the brief. QA dispatches two fresh subagents with the Task tool (opus) and records their results:

- **The cold reader** runs Gate 1. It gets the page text only.
- **The gate reviewer** runs gates 2 to 4 and judges Gate 1's result. It gets agent-header.md, this step, `modules/conversion-playbook.md` Sections 5, 9 and 10, brief.md, copy.md, page.html (when it exists), the body of `company-identity.md` (Proof Point Registry) and `audience-messaging.md` (objection inventory), and the cold reader's report. It gets no QA results from Steps 2 to 4d. Dispatch it after the cold reader returns.

If a subagent cannot be dispatched (for example, QA is itself running inside a subagent), mark the gates it would run BLOCKED, set `overall: FAIL`, and say why. Never run a gate in the QA context as a substitute.

**Build the page text first.** The cold reader and Gate 4 read the visitor-visible text in scroll order:

- From page.html when it exists: every visible text node in document order, including headings, body copy, button labels, form labels and microcopy, captions, and image alt text. Exclude HTML comments, scripts, styles and hidden elements. Append the lightbox form text at the end, labeled as the form.
- From copy.md otherwise: the recommended headline variant only, then each section body in manifest order. Strip frontmatter, HTML comments, `## Type: variant` headings, proof point IDs, `[OPTIONAL]` and `[GAP]` markers, and alternate headline variants.

**Gate 1: Cold reader.** The prompt carries the page text and these instructions, nothing else: no brief, no context files, no copy.md frontmatter, no campaign name, and no description of the product. Ask the cold reader to return:

1. **Header-only read.** From the H1 alone: what is being sold? Then from the hero (everything before the first section break): what is sold, to whom, and what is the next step?
2. **Used before introduced.** Every person's name, product or feature term, and acronym that appears before the page says what it is. Give the line, and where it is introduced, if anywhere. Claims are out of scope here: a hook states a claim first and backs it up later, by design. Unsupported claims go under item 4.
3. **Open questions.** What a first-time visitor still needs to know before acting.
4. **Disbelief.** Any claim or line that reads as unsupported sales talk by the end of the page.

The gate reviewer, not the cold reader, compares item 1 with the brief's offer. Pass: the header-only answer matches what the brief sells, and item 2 is empty. Otherwise FAIL. Items 3 and 4 feed Gate 3 and the recommended fixes. The cold reader is the agent stand-in for Julian Shapiro's "People not in your market" reviewer. It does not replace testing with real prospects.

**Gate 2: Julian audit.** The gate reviewer runs ATF-1 to ATF-6 itself, then three whole-page checks against copy.md and page.html:

- **Order.** The section sequence satisfies conversion-playbook.md Section 5 hard rules, including the Social Proof Bar at Section 2 or 3 and visible without scrolling on desktop (hard rule 3).
- **Feature blocks.** Each section that pitches a value prop has a blunt value header and a paragraph that handles the objection the value raises, and ties back to the hero's value prop (conversion-playbook.md Feature Blocks). In page.html, each also carries a visual of the product in action or, for a service, of the deliverable. In copy-only runs, check that each block names the visual it needs.
- **Desire, labor, confusion.** One line each: what on the page raises desire, what costs the visitor labor, what could confuse them. Recorded for the fixes list, not scored.

Pass: ATF-1 passes, ATF-6 does not fail, no Section 5 hard rule is broken, and every feature block is complete. Otherwise FAIL.

**Gate 3: Truth check.** Against brief.md, the Proof Point Registry and the objection inventory, plus the cold reader's disbelief list:

- **Every claim traces.** Each number, name, quote, logo, customer and capability statement maps to a proof point ID or a named source line. Record the source beside it.
- **One story.** Wherever two parts of the page describe the same event or capability (a demo and a case study, a hero claim and a proof block, two objection answers), they agree. A contradiction fails even when each line is sourced on its own.
- **The offer is the offer.** The page promises only what the offer delivers: duration, deliverable, post-submit step. A disclosure tied to an offer the brief no longer includes is flagged for removal.

Pass: no untraceable claim and no contradiction. Otherwise FAIL.

**Gate 4: Delete test.** For every line of visible copy (headings, sentences, list items, button labels, form microcopy, captions), write one phrase naming what the visitor would lose if it were cut. A line whose honest answer is "nothing" goes on the cut list with an action: cut it, or merge it into a named line. Typical entries: a line that restates another, process copy, a name the visitor has no reason to care about yet, a caption that repeats its heading.

Pass: the cut list is empty. Otherwise FAIL.

**After fixes, rerun.** Copy fixes go through Phase 2, re-run with this report as feedback; stage isolation keeps Phase 3 from changing copy. Then re-run Phase 3 so page.html matches, and Phase 4 in full, because a fix can break another line. Use new subagents every time. A cold reader that has seen an earlier draft is no longer cold.

**Result.** Any gate FAIL or BLOCKED sets `overall: FAIL`.

### Step 5: Write Report

Write to `.claude/deliverables/campaigns/<slug>/qa-report.md`:

```yaml
---
schema: qa-report
schema_version: "2.1"
client: <company-name>
campaign: <campaign-slug>
files_checked:
  - copy.md
  - page.html
copy_checks: <pass-count>/<total>
design_checks: <pass-count>/<total>
cross_checks: <pass-count>/<total>
section_count: <int, from copy.md sections array>
section_parity: <PASS|FAIL>
ordering_violations: <int, CS-3 hard rule violations, 0 = pass>
ordering_warnings: <int, CS-3 soft rule deviations>
variant_alignment_flags: <int, CS-2 flag count>
objection_coverage: <"X/Y", CS-4 result>
cta_consistency: <PASS|FAIL>
review_gates:
  cold_reader: <PASS|FAIL|BLOCKED>
  julian_audit: <PASS|FAIL|BLOCKED>
  truth_check: <PASS|FAIL|BLOCKED>
  delete_test: <PASS|FAIL|BLOCKED>
cold_reader_header_read: <one line: what the cold reader said is sold, from the H1 alone>
delete_test_cuts: <int, lines on the cut list>
dimension_ratings:
  awareness_stage_alignment: <strong|needs_work|missing>
  value_proposition_clarity: <strong|needs_work|missing>
  message_match: <strong|needs_work|missing>
  page_structure: <strong|needs_work|missing>
  social_proof_strategy: <strong|needs_work|missing>
  cta_and_form_design: <strong|needs_work|missing>
  persuasion_psychology: <strong|needs_work|missing>
  copy_quality_readability: <strong|needs_work|missing>
  visual_design_ux: <strong|needs_work|missing>
  competitive_differentiation: <strong|needs_work|missing>
strong_count: <int>
needs_work_count: <int>
missing_count: <int>
top_issue: <dimension_name>
overall: <PASS|FAIL>
# Brand component fields (present only when brand design system detected)
brand_component_checks: str   # "X/Y" pass count, omit if no brand files
brand_component_violations: int  # count of BC- check failures, omit if no brand files
brand_component_warnings: int    # count of BC-7 warnings, omit if no brand files
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

## Composable Section Validation

| # | Check | Result | Notes |
|---|-------|--------|-------|
| CS-1 | Section Parity | PASS/FAIL | [sections matched / mismatches] |
| CS-2 | Variant-Signal Alignment | X flags | [flag details] |
| CS-3 | Ordering Constraints | X hard / Y soft | [violations] |
| CS-4 | Objection Coverage | X/Y addressed | [unaddressed list] |
| CS-5 | CTA Consistency | PASS/FAIL | [mismatches] |
| CS-6 | Proof Adjacency | PASS/FLAG | [visual notes] |

## Brand Component Validation

| # | Check | Result | Notes |
|---|-------|--------|-------|
| Brand Component | BC-1 through BC-7 | X/Y pass + Z warnings | (conditional: only when brand files detected) |

## Independent Review Gates

| Gate | Result | Notes |
|------|--------|-------|
| 1: Cold reader | PASS/FAIL/BLOCKED | [header-only read; names or terms used before introduced] |
| 2: Julian audit | PASS/FAIL/BLOCKED | [ATF-1 and ATF-6 results; order, feature-block and desire/labor/confusion findings] |
| 3: Truth check | PASS/FAIL/BLOCKED | [untraceable claims; contradictions] |
| 4: Delete test | PASS/FAIL/BLOCKED | [cut count] |

### Cold Reader Report

[The cold reader's four answers, verbatim]

### Delete-Test Cut List

| # | Line | Section | What the visitor loses if cut | Action |
|---|------|---------|-------------------------------|--------|

## Taxonomy Dimension Scores

| Dimension | Rating | Recommendation |
|-----------|--------|---------------|
| D1: Awareness-Stage Alignment | Strong/Needs Work/Missing | [specific recommendation if not Strong] |
| D2: Value Proposition Clarity | ... | ... |
| D3: Message Match | ... | ... |
| D4: Page Structure | ... | ... |
| D5: Social Proof Strategy | ... | ... |
| D6: CTA and Form Design | ... | ... |
| D7: Persuasion Psychology | ... | ... |
| D8: Copy Quality / Readability | ... | ... |
| D9: Visual Design / UX | ... | ... |
| D10: Competitive Differentiation | ... | ... |

**Dimension summary:** [X] Strong, [Y] Needs Work, [Z] Missing
**Top issue:** [dimension name and one-line description]

## Gaps Carried Forward

[List all [GAP] markers from copy.md and page.html]

## Recommended Fixes

[For each FAIL, explain exactly what's wrong and which file to edit]
```

### Step 6: Confirm

Present results summary to the human:
- Overall PASS or FAIL
- Count of passed/failed checks
- For any FAILs: explain the fix, including every delete-test cut and every name or term the cold reader flagged
- If every check and all four gates pass: "Page is ready for review and deployment."

---

## QA Runs Inline; the Review Gates Do Not

QA is lightweight enough to run inline in the orchestrator context. The orchestrator loads agent-header.md + this file and executes directly, which saves ~20K tokens of agent overhead.

The Step 4e gates are the exception. They always run in two fresh subagents, the cold reader and the gate reviewer. The orchestrator has read the brief, so it cannot read the page cold, and it may have revised the copy itself, so it cannot grade it.
