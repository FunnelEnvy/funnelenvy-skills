---
name: repo-conventions
document_type: fe-governance-deploy/rule-document
description: >
  File/directory naming, git conventions, credentials, .gitignore, and resource naming patterns
  for all managed repos.
version: "1.0.0"
created: 2026-03-06
updated: 2026-03-08
---

# Repo Conventions

Shared file, directory, git, credential, and resource naming conventions for all managed repos.

## Files and Directories

- All directory and filenames are lowercase
- Default to kebab-case; use underscore only when prefixed or suffixed by date (e.g., `2026-02-19_file-a`)
- Python files use snake_case matching skill name
- Multi-word frontmatter keys use snake_case (e.g., `resource_name`, `blocked_by`)
- All dates represented as YYYY-MM-DD
- **Underscore-prefixed directories** (`_dev/`, `_templates/`, `_transforms/`): Used for directories injected by a cross-cutting governance skill into a resource it doesn't own. The underscore prefix provides visual separation and sorts these above content directories. Examples: `_dev/` (change-management), `_templates/` (document-management), `_transforms/` (knowledge-base).
- `.claude/rules/` is managed by fe-sys-hq rule deployment — do not manually edit, add, or remove rule files from this directory

## Git

- Branch names follow the pattern `{user-prefix}_{description}`
- Commit messages and PR descriptions are concise and bulleted
- Significant changes go through a branch with PR creation

## Credentials

- Never store credentials, API keys, tokens, or secrets in repo files
- Store all credentials in `.env` files
- Never commit `.env` files — ensure `.gitignore` includes `.env` and all credential file patterns
- Never prompt a user to input credentials into chat — set up `.env` with placeholders instead

## .gitignore

- Every repo must have a `.gitignore` that covers: `.env`, credential files, OS artifacts, editor files
- Verify `.gitignore` coverage before adding any integration that uses credentials

## Resources

- Rule files use a two-digit numbered prefix: `{NN}-{topic}.md`
