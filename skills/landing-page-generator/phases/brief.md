# Phase 1: Brief Builder

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/campaign-brief-template.md (template structure)
> **Input:** `.claude/context/` (L0+L1 files) + `.claude/deliverables/` (rendered deliverables) + human campaign seed
> **Output:** `.claude/deliverables/campaigns/<slug>/brief.md`

---

## Required Inputs

- `company-identity.md` (L0, confidence >= 3) -- HARD REQUIREMENT
- Human-provided campaign seed (service line, target buyer, keywords)

## Soft Inputs (degrade gracefully if missing)

- `audience-messaging.md` (L1) -- persona messaging, proof points, voice rules
- `competitive-landscape.md` (L1) -- competitive framing
- `positioning-scorecard.md` (L1) -- positioning gaps to address
- `performance-profile.md` (L1) -- traffic data, keyword insights, conversion baseline
- Rendered deliverables: executive-summary.md, messaging-guide.md, battle cards

---

## Graceful Degradation

| Missing Context | Impact | Mitigation |
|----------------|--------|------------|
| audience-messaging.md | No persona data, no proof library, no voice rules | Ask human for all persona, proof, and voice info. Brief builder becomes fully interactive. |
| competitive-landscape.md | No competitive framing | Skip competitive positioning. Note in brief. |
| positioning-scorecard.md | No gap analysis | Skip gap-based recommendations. |
| performance-profile.md | No traffic/keyword data | Ask human for keywords and traffic baseline. |
| All L1 files missing | Only L0 facts available | Brief builder runs in fully interactive mode. Every section except company facts must be provided by the human. Flag this: "Only company facts are available. Consider running /positioning-framework at standard depth before building landing pages." |

---

## Workflow

### Step 1: Collect Campaign Seed

If not already provided in the invocation, ask the human for:

1. **Service line or offer** -- What is this landing page selling? (e.g., "Interim CFO Services")
2. **Target buyer** -- Who is the primary persona? (title/role, e.g., "CFO at a PE-backed mid-market company")
3. **Target keywords** -- What search terms or ad themes drive traffic? (e.g., "interim cfo," "outsourced cfo," "cfo transition")
4. **Traffic source** -- What is the primary channel driving traffic to this LP? (paid_search, paid_social_cold, paid_social_retargeting, email, organic, referral, direct)
5. **Traffic awareness stage** -- How aware is the target audience of your product? Use the classification table below to infer from the traffic source:

   | If traffic source is... | Default to... |
   |------------------------|---------------|
   | paid_search (branded) | product_aware |
   | paid_search (non-branded, solution terms) | solution_aware |
   | paid_search (non-branded, problem terms) | problem_aware |
   | paid_social_cold | problem_aware |
   | paid_social_retargeting | product_aware |
   | email | product_aware |
   | organic | solution_aware |
   | referral (G2, Capterra) | product_aware |
   | direct | solution_aware |

   If the human is unsure, infer from the traffic source using the defaults above. Write the classification to `traffic_awareness_stage` and `traffic_source` in the brief frontmatter. These fields drive headline approach selection in Phase 2.
6. **Offer type** -- What is the CTA goal? (demo, consultation, content download, quote)

If the human provides a fuller description, use it. But still validate against the context files.

### Step 2: Load Context

Read frontmatter of all available context files. Build an inventory of what's available.

Then load full bodies of:
- `company-identity.md` -- always (needed for company facts, segments, proof point registry)
- `audience-messaging.md` -- always if present (persona grid, proof library, voice, objections, language guidance)
- `competitive-landscape.md` -- frontmatter only unless the campaign specifically needs competitive framing
- `performance-profile.md` -- frontmatter only for traffic adequacy; full body if the human asks about keyword data

If rendered deliverables exist in `.claude/deliverables/`, also scan:
- `messaging-guide.md` or equivalent -- for curated proof points and objection handling
- `executive-summary.md` or equivalent -- for differentiators and case study outcomes

### Step 3: Extract Into Brief Template

Read `modules/campaign-brief-template.md` for the template structure. For each section, attempt extraction using this map:

**Campaign Context section:**
- Client name: from `company-identity.md` frontmatter `company.name`
- Service line: from campaign seed
- Target keywords: from campaign seed. Cross-reference with `performance-profile.md` if available (top landing pages, top channels).
- Ad copy: NOT in context files. Always a gap. Ask human.

**Audience section:**
- Primary buyer persona: match campaign seed's target buyer against persona grid in `audience-messaging.md`. Extract the full persona section for the matching role.
- Buyer's trigger event: from persona "who they are" description or buying triggers. If not explicit in context, draft from available signals and ask human to confirm.
- What they're measured on: from persona description if available. Otherwise ask human.
- Emotional state: infer from trigger event. Always ask human to confirm.

**Page Pillars (3 max):**
- Extract from the matched persona's "key messages" in `audience-messaging.md`. Each key message maps to a pain/fix card.
- If the human provided pillars in their seed, validate against messaging context. Flag mismatches.
- If neither source has clear pillars, propose 3 based on available context and ask human to pick.

**Headline Strategy:**
- Apply the three approaches from `modules/conversion-playbook.md` Section 5 (Hero): pain-forward, keyword-forward, proof-forward.
- Use persona messaging + proof points as raw material.
- Propose 1 headline per approach. Ask human which they prefer or if they want all 3 for A/B testing.

**CTA text:**
- Not in context files. Propose 2-3 options based on the offer type from the campaign seed. Ask human to pick.
- Match to conversion playbook CTA rules: specific, benefit-oriented, names what happens next.

**Proof Points:**
- Metrics: extract from proof points library (strong + moderate tiers) in `audience-messaging.md`. Filter to this persona and service line.
- Case studies: same source. Match to service line. If no direct match, propose closest alternative and flag the gap.
- Testimonials: same source. Must have name, title, company. If no persona-matched testimonial, flag as critical gap.
- Client logos: extract from proof points library or company-identity.md. Pick 5 most recognizable.

**Objection Handling:**
- Extract from objection handling table in `audience-messaging.md`. Reframe as buyer questions.
- Every answer must include a proof point reference. Flag any answer that's assertion-only.

**Client-Specific Overrides:**
- Form field overrides: NOT in context files. Ask human about enrichment tool availability and field count preference.
- Post-submit flow: NOT in context files. Ask human about calendar tool, SDR follow-up process.
- Regulatory/compliance: extract from language guidance in `audience-messaging.md`. Include banned terms, required terms, required disclaimers.

### Step 4: Present Extraction + Gaps

Present findings in two sections:

**SECTION A: What I extracted (confirm or correct)**

Show the filled-in brief template with source attribution for each extraction (e.g., "from audience-messaging.md, CFO persona"). Format as a clean draft.

**SECTION B: Gaps I need you to fill**

Group by priority:

**BLOCKING (cannot generate the brief without these):**
- Target keywords / ad copy (never in positioning context)
- Post-submit flow (calendar tool? SDR follow-up? What happens today?)
- Form strategy (enrichment tool? desired field count?)
- CTA text preference

**IMPORTANT (brief will be weaker without these):**
- Case study match for this specific service line (flag if none found)
- Named testimonial match for this persona (flag if none found)
- Ad copy for message-matching (if not yet written)

**NICE TO HAVE:**
- Video asset availability
- Specific competitor to position against on this page
- Additional proof points not in context files

### Step 5: Resolve Gaps

Ask blocking gaps first. Batch questions when choices are bounded (e.g., "Which of these 3 case studies fits best?"). Use open-ended questions for things like ad copy.

Do NOT ask all questions at once if there are more than 5 gaps. Blocking first, then important, then nice-to-have.

### Step 6: Assemble and Write

Once all blocking gaps are resolved, assemble the completed brief.

Create the campaign directory if needed:
```
mkdir -p .claude/deliverables/campaigns/<slug>/
```

Write to `.claude/deliverables/campaigns/<slug>/brief.md` with this frontmatter:

```yaml
---
schema: campaign-brief
schema_version: "1.1"
client: <company-name>
campaign: <campaign-slug>
service_line: <service-line>
target_persona: <persona-title>
target_keywords:
  - <keyword-1>
  - <keyword-2>
traffic_awareness_stage: <unaware|problem_aware|solution_aware|product_aware|most_aware>
traffic_source: <paid_search|paid_social_cold|paid_social_retargeting|email|organic|referral|direct>
offer_type: <demo|consultation|content|quote>
form_strategy:
  fields: <int>
  type: <lightbox|embedded|multi-step>
  enrichment_tool: <true|false>
post_submit: <calendar|asset|thankyou>
proof_points_count: <int>
gaps:
  - <any unresolved IMPORTANT gaps>
depth: <standard|deep>
generated_by: "landing-page-generator/brief"
last_updated: <ISO-8601>
---
```

Body follows the `modules/campaign-brief-template.md` structure exactly. Clean output: no extraction notes, no source citations, no agent commentary. Just the brief.

Exception: if a gap was flagged as IMPORTANT but the human chose not to fill it, note it inline:
```
**[GAP]**: No case study directly matches this service line. Using [closest fit] per human confirmation. Copy Agent should handle with care.
```

### Step 7: Confirm

Tell the human:
- Brief saved to `.claude/deliverables/campaigns/<slug>/brief.md`
- Summary of key decisions (persona selected, headline approach, proof points used)
- Any remaining gaps
- "Run `/landing-page-generator <company> <slug> --stage copy` when ready for Phase 2."

---

## Gap Detection Rules

Always check for these even if the human doesn't mention them:

**Proof gaps:**
- No named testimonial for this persona
- No case study matching this service line (flag mismatch explicitly)
- Stale or conflicting metrics across context files
- No quantified outcomes (case studies with "helped improve" instead of specific numbers)

**Voice gaps:**
- No brand voice data in context (propose voice from available signals, ask to confirm)
- Regulatory constraints not documented (ask: "Any terms you can't use or disclaimers required?")

**Structural gaps:**
- Pillars with no proof points mapped to them
- Objection answers that are assertion-only (no proof backing)
