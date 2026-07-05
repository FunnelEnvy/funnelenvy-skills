# Contributing

Thanks for your interest in contributing to FunnelEnvy Skills.

## Getting Started

1. Fork the repo and clone locally
2. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
3. Read `CLAUDE.md` for the full architecture (three-layer model, schema contracts, skill format)

## Developing Skills

Each skill lives in `skills/<skill-name>/` with a `SKILL.md` as the entry point.

**Requirements for new skills:**

- YAML frontmatter with `name`, `version`, `description`
- Declare context dependencies (which L0/L1 files the skill reads and writes)
- Include a Preconditions section
- Implement Prior Work Detection (check for existing context files before researching)
- Follow schemas in `/schemas/` for any context files produced
- Include quality checks
- Test against a real company URL before submitting

**Skill format reference:** Look at any existing `SKILL.md` for the expected structure, or start from the scaffold below.

### SKILL.md scaffold

Every element below is required unless marked optional. `scripts/registry_check.py` (run in CI) enforces registration and changelog consistency, so skipping the checklist fails the PR.

```markdown
---
name: my-skill                    # must equal the directory name
version: 0.1.0                    # semver; bump on every content change
description: "When the user wants to <job>. Also use when the user mentions '<trigger>,' '<trigger>,' or '<trigger>.' <One-paragraph summary of what it reads, does, and produces.>"
updated: YYYY-MM-DD
---

# My Skill

<One-paragraph role statement: what the agent is and what it produces.>

**Output location:** <where artifacts land>
**Token budget:** ~<range>
**Runtime:** ~<estimate>
**Agents:** <single agent | N sequential agents | orchestrator + phase agents>
**Model:** Opus

## Invocation

/my-skill <args> [--flag]
<Flag table: flag, default, description.>

## Preconditions

**Hard requirements (fail or stop if missing):** ...
**Soft requirements (degrade if missing):** ...
**Reads:** <L0/L1 context files or KB artifacts consumed>
**Writes:** <files produced; declare prior-work behavior: extend vs overwrite>
**Concurrency:** do not run alongside another producing skill (no locking).

## <Workflow sections: phases or steps>

## Agent Model Selection          # required when the skill spawns subagents

| Agent | Phase | Model |
|-------|-------|-------|
| ...   | ...   | opus  |

## Quality Checks                 # keep as the last substantive section

- [ ] <verifiable check tied to this skill's output contract>
- [ ] Every claim in the output traces to a loaded input; nothing invented
- [ ] Output landed at the declared path with valid frontmatter
```

**Changelog:** add a `CHANGELOG.md` next to SKILL.md (Keep-a-Changelog style, `## [x.y.z] - YYYY-MM-DD` entries). The top entry must match the frontmatter version.

**Registration is a package deal.** A new or version-bumped skill must update, in the same PR: the skill's changelog, `README.md` (skills table + Quick Start example if user-facing), `CLAUDE.md` (repo structure tree + Available Skills entry), and `.claude-plugin/marketplace.json` (skills list + count in the plugin description).

**Dual-mode (KB) skills:** if the skill reads or writes knowledge-base artifacts, follow the canonical contract in `modules/kb-mode.md` and add the skill to that module's table. The registry check enforces the invariant sentences.

## No client references (hard rule)

This repo is **public**. Never write a real company or client name, engagement codename, or account
identifier in any file or commit message. Use a generic placeholder (`Acme`, `Example Corp`,
`the client`, `a private consumer engagement`) or omit it. This applies to everyone, including AI
agents working in the repo, and it is applied by inference: you already know a real company name when
you write one, so don't.

A mechanical guard backstops the rule. Install it once per clone:

```
./scripts/install-hooks.sh
```

That points `core.hooksPath` at the tracked `hooks/` dir. There is nothing else to set up: the guard
is self-contained (no list to maintain, no secret).

How it works:

- `hooks/pre-commit` scans staged content and `hooks/commit-msg` scans your commit message. It flags
  the shape of client data (a run of capitalized words followed by a corporate legal suffix, e.g.
  `Acme Corp` or `Example GmbH` if those were not placeholders) and blocks the commit, reporting the
  file and line but never the matched text (CI logs can be public).
- It does not detect bare money figures (this repo cites them constantly as instructional examples) or
  bare codenames with no company shape. Those are on you and review to catch, per the rule above.
- False positives are intentionally tolerated. If a legitimate line trips the guard, rephrase it or use
  a placeholder token.
- CI (`.github/workflows/client-ref-guard.yml`) runs `scripts/client_ref_guard.py scan-tree` as a
  backstop for commits made without the local hooks installed.
- Manual audit any time: `python scripts/client_ref_guard.py scan-tree`.

## Submitting Changes

1. Create a branch: `yourname_description`
2. Make your changes
3. Test the skill end-to-end against a real URL
4. Open a PR with a clear description of what the skill does and sample output

## Conventions

- Filenames: lowercase, kebab-case
- Python files: snake_case
- Dates: YYYY-MM-DD
- No credentials in repo files (use `.env`)
- See `.claude/rules/` for the full set of repo conventions

## Questions?

Open an issue. We'll get back to you.
