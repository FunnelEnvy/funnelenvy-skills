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

**Skill format reference:** Look at any existing `SKILL.md` for the expected structure.

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
