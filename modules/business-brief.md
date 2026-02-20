# Business Brief Module

Shared instructions for loading client-provided business context before research begins. Referenced by positioning-framework and future skills.

---

## What Is a Business Brief?

A business brief is an optional file at `.claude/business-brief.md` where the user front-loads domain knowledge that web research cannot discover: specific competitors they lose deals to, terminology preferences, regulatory constraints, audience nuances, and retired positioning they've moved away from.

The orchestrator reads this file during Pre-Flight intake (SKILL.md step 5) and threads its content into agent launch prompts. This reduces the number of intake questions and improves research accuracy from the start.

---

## Business Brief Template

The brief file lives at `.claude/business-brief.md`. Users fill in whichever sections they have context for and delete the rest.

```markdown
---
company: "[Company Name]"
url: "[company URL]"
last_updated: 2026-02-17
---

# Business Brief

## Known Competitors

List competitors you actually compete against in deals. Notes on why they matter are valuable.

- [Competitor Name] - [why they matter, e.g., "we lose deals to them on price", "they show up in every RFP"]

## Language Constraints

Terms to use, terms to avoid, industry jargon conventions.

- **Must use:** [preferred terms]
- **Must avoid:** [terms to avoid and why -- regulatory, legal, brand, or competitive reasons]

## Existing Docs

Links or references to positioning docs, sales decks, brand guidelines, or other internal materials. Paste inline or reference file paths.

## Additional Context

Anything else the skills should know: recent pivots, retired messaging, service boundaries, target audience nuances, regulatory environment, etc.

- **Service boundaries:** [what you do and explicitly do NOT do]
- **Retired positioning:** [past messaging you've moved away from]
- **Target audience:** [ICP details beyond what's on the website]
- **Other:** [freeform]
```

**Backward compatibility:** Older briefs without YAML frontmatter (flat markdown with "Regulatory / Compliance Context", "Target Audience", "Service Boundaries", "Retired Positioning", "Other Context" sections) are still consumed correctly. The orchestrator maps legacy section names to the current 4-section structure:
- "Regulatory / Compliance Context" + "Language Preferences" -> Language Constraints
- "Target Audience" + "Service Boundaries" + "Retired Positioning" + "Other Context" -> Additional Context
- "Known Competitors" -> Named Competitors (unchanged)

---

## Intake Protocol

The orchestrator (SKILL.md step 5) runs Pre-Flight intake and passes results to agents. Individual agents do NOT run their own intake.

### Orchestrator Behavior

1. **Check for `.claude/business-brief.md`.**
2. **If found:** Read it. Display summary. Offer user chance to add/override.
3. **If not found + standard/deep depth:** Present 4-question intake prompt (see SKILL.md step 5).
4. **If not found + quick depth:** Skip entirely. Zero prompts.
5. **Package answers into intake payload** and include in each agent's launch prompt.

See SKILL.md "Step 5: Pre-Flight Intake" for the full protocol, intake questions, and payload format.

### Agent Behavior

Agents receive the intake payload in their launch prompt and apply it per their phase instructions:
- **Agent 1 (research.md):** Named competitors become required competitive research targets. Existing docs are Tier 0. Language constraints thread into L0 Glossary + Constraints.
- **Agent 2 (competitive.md):** Named competitors are required analysis targets. Sales context (win/loss notes) informs battle card framing.
- **Agent 3 (messaging.md):** Language constraints are authoritative for Banned Terms and Language Bank. Voice preferences inform Voice Profile.
- **Agent 4 (scoring.md):** Full intake provides scoring context.

---

## Design Decisions

- **No brief = prompt at standard/deep, skip at quick.** Quick depth is zero-interaction. Standard/deep gets 4 focused questions.
- **Brief is optional, never required.** Skills work fine without it. The brief makes them work better.
- **YAML frontmatter added.** `company`, `url`, `last_updated` for machine readability. Old flat-markdown briefs still work.
- **Don't auto-create the brief file for "go" responses.** Only save when the user provided substantive answers worth reusing.
- **4 questions, not 6.** Consolidated from the original 6 Pre-Flight questions. Pricing model, service exclusions, and retired positioning folded into the "Additional Context" catch-all. Fewer questions = higher completion rate.
- **Orchestrator owns intake, not agents.** User answers flow directly to all agents, not indirectly through L0.
