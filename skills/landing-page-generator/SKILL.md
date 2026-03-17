---
name: landing-page-generator
version: 1.0.0
description: "When the user wants to generate a B2B paid landing page from existing positioning context. Also use when the user mentions 'landing page,' 'LP generator,' 'campaign page,' 'paid landing page,' 'landing page copy,' 'hero section,' or 'conversion page.' Four-phase pipeline: brief builder, copy agent, design agent, QA validator. Consumes L0+L1 context files from .claude/context/ and produces campaign deliverables in .claude/deliverables/campaigns/."
---

# Landing Page Generator

> **Version:** 1.0.0
> **Type:** Multi-phase pipeline with human review gates
> **Model:** opus (all phases)
> **Depends on:** modules/conversion-playbook.md, modules/campaign-brief-template.md, modules/lp-audit-taxonomy.md (construct mode)

Generates B2B paid landing pages from existing positioning context. Four phases: Brief Builder, Copy Agent, Design Agent, QA Validator. Each phase produces a file that the next phase consumes.

---

## Invocation

```
/landing-page-generator <company-url-or-name> <campaign-slug> [--stage <stage>] [--depth standard|deep]
```

**Arguments:**
- `<company-url-or-name>`: Company URL or name. Must match an existing `.claude/context/company-identity.md` OR be resolvable to one.
- `<campaign-slug>`: Kebab-case campaign identifier (e.g., `interim-cfo`, `erp-implementation`, `audit-readiness`).
- `--stage`: Run a single phase. Values: `brief`, `copy`, `design`, `qa`, `all`. Default: prompt user.
- `--depth`: Controls copy depth. `standard` (default) produces 3 headline options + full section copy. `deep` adds variant copy for A/B test sections.

**Examples:**
```
/landing-page-generator Acme Corp interim-cfo --stage brief
/landing-page-generator Acme Corp interim-cfo --stage copy
/landing-page-generator Acme Corp interim-cfo --stage design
/landing-page-generator Acme Corp interim-cfo --stage qa
/landing-page-generator Acme Corp interim-cfo --stage all
```

---

## Preconditions

**Hard requirements (fail if missing):**
- `.claude/context/company-identity.md` must exist with confidence >= 3. If missing, report `[PRECONDITION FAILED]: Run /positioning-framework first to build company context.`

**Soft requirements (degrade if missing):**
- `.claude/context/audience-messaging.md` -- needed for persona messaging, proof points, voice. Without it, brief builder must ask the human for all persona and proof data manually.
- `.claude/context/competitive-landscape.md` -- used for competitive framing in copy. Without it, skip competitive positioning sections.
- `.claude/context/positioning-scorecard.md` -- used to identify gaps. Without it, skip gap-based recommendations.
- `.claude/deliverables/` -- executive summary, messaging guide, battle cards. Used to enrich brief building. Without them, rely on L0+L1 context files only.
- `.claude/context/performance-profile.md` -- used to inform keyword strategy and page pillar prioritization. Without it, ask human for all keyword and traffic data.

---

## Output Location

All campaign outputs go to:

```
.claude/deliverables/campaigns/<campaign-slug>/
  brief.md          # Phase 1 output
  copy.md           # Phase 2 output
  page.html         # Phase 3 output
  qa-report.md      # Phase 4 output
```

---

## Orchestrator Logic

### Step 1: Parse Arguments

Extract company identifier, campaign slug, stage flag, and depth flag. Validate campaign slug is kebab-case (lowercase, hyphens only, no spaces).

### Step 2: Resolve Company Context

Glob `.claude/context/` and read frontmatter of all files found. Build an inventory:

| File | Status | Confidence |
|------|--------|------------|
| company-identity.md | present/missing | 1-5 |
| audience-messaging.md | present/missing | 1-5 |
| competitive-landscape.md | present/missing | 1-5 |
| positioning-scorecard.md | present/missing | 1-5 |
| performance-profile.md | present/missing | 1-5 |

Also glob `.claude/deliverables/` for rendered deliverables (executive summary, messaging guide, battle cards).

If `company-identity.md` is missing or confidence < 3: stop. Print `[PRECONDITION FAILED]` with instructions to run `/positioning-framework` first.

### Step 3: Prior Work Detection

Check if `.claude/deliverables/campaigns/<campaign-slug>/` exists. If it does, read frontmatter of any files present:

- If `brief.md` exists and user requested `--stage brief`: ask "A brief already exists for this campaign. Overwrite, extend, or skip?"
- If `copy.md` exists and user requested `--stage copy`: ask "Copy already exists. Overwrite or skip?"
- If `page.html` exists and user requested `--stage design`: ask "HTML page already exists. Overwrite or skip?"

Never silently overwrite. Always ask.

### Step 4: Route to Phase

If `--stage` is specified, run that phase only (with precondition checks).
If `--stage all`, run the full pipeline with human review gates between each phase.
If no `--stage` flag, ask the user:

"Which stage do you want to run?"
- Brief (Phase 1): Build the campaign brief from positioning context
- Copy (Phase 2): Generate landing page copy from the brief
- Design (Phase 3): Build HTML page from the copy
- QA (Phase 4): Validate copy and HTML against the playbook
- All: Run the full pipeline with review gates between stages

### Step 5: Launch Phase Agent

Each phase runs as a subagent. Load:
1. `agent-header.md` (shared rules, ~1.5K tokens)
2. The relevant `phases/<phase>.md` file
3. Any modules referenced by that phase

**Phase routing:**

| Stage | Agent loads | Preconditions |
|-------|-----------|---------------|
| brief | agent-header.md + phases/brief.md | company-identity.md confidence >= 3 |
| copy | agent-header.md + phases/copy.md | brief.md must exist in campaign directory |
| design | agent-header.md + phases/design.md | copy.md must exist in campaign directory |
| qa | agent-header.md + phases/qa.md | At least one of copy.md or page.html must exist |

### Step 6: Review Gate (--stage all only)

After each phase completes:
1. Present a summary of what was produced
2. Ask the human to review and confirm before proceeding
3. If the human requests changes, re-run the phase with their feedback
4. Only advance to the next phase after explicit confirmation

```
Phase 1 complete. Brief saved to .claude/deliverables/campaigns/{slug}/brief.md
Review the brief. When you're ready, say "continue" to generate copy, or tell me what to change.
```

### Step 7: Completion

After the final phase (or single phase), summarize what was produced:
- Files written (with paths)
- Any gaps or warnings flagged during execution
- Next step recommendation

---

## Token Budget

| Phase | Estimated Tokens | Notes |
|-------|-----------------|-------|
| Brief (Phase 1) | ~50-80K | Reads L0+L1 context, interactive gap filling |
| Copy (Phase 2) | ~85-125K | Reads brief + playbook module + taxonomy construct mode (D1,D2,D3,D5,D7,D8,D10) + positioning context |
| Design (Phase 3) | ~105-155K | Reads copy + structural rules + taxonomy construct mode (D4,D6,D9) + wireframe reference + brand design system (if available) |
| QA (Phase 4) | ~30-50K | Validation pass, no generation |
| Full pipeline | ~260-400K | All four phases with review gates |

---

## Design Decisions

**Why separate phases instead of a single agent?**
LP generation has natural human review points. You review the brief before writing copy. You review copy before building HTML. Forcing this into a monolithic agent with checkpoints adds complexity for zero benefit. Separate phases also mean you can re-run Phase 2 (copy) without re-running Phase 1 (brief) after the brief is finalized.

**Why consume .claude/context/ directly?**
The positioning-framework skill produces structured context files with frontmatter. This skill reads them directly instead of maintaining a parallel client directory. No manual file copying. The positioning-framework IS the client onboarding step.

**Why outputs in .claude/deliverables/campaigns/?**
Campaign briefs and copy are deliverables, not reusable analysis context. They are campaign-specific and consumed by exactly one downstream phase. Putting them in `.claude/context/` would be a layer violation. The `campaigns/` subdirectory keeps multiple campaigns organized under one client's deliverables.

**Why the wireframe is a template, not a module?**
Modules are shared markdown instructions read by agents. The wireframe is a React component used as a structural reference by exactly one phase (design). It lives in `templates/` within the skill directory because it is skill-specific, not cross-skill.
