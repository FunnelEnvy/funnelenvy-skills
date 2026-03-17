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
