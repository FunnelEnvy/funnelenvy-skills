---
version: "1.0.1"
updated: 2026-05-01
---
# Repo Conventions

Shared file, directory, git, credential, and resource naming conventions for all managed repos.

## Credentials (MANDATORY — Security Boundary)

Violating any credential rule is a security incident — leaked secrets cannot be unrotated. These rules have zero exceptions.

- NEVER store credentials, API keys, tokens, or secrets in repo files
- Store all credentials in `.env` files
- NEVER commit `.env` files — ensure `.gitignore` includes `.env` and all credential file patterns
- NEVER prompt a user to input credentials into chat — set up `.env` with placeholders and let the user fill them in directly

## Files and Directories

You MUST NOT deviate even when creating "temporary" or "one-off" files.

- All directory and filenames MUST be lowercase
- Default to kebab-case; use underscore ONLY when prefixed or suffixed by date (e.g., `2026-02-19_file-a`)
- Python files use snake_case matching skill name
- Multi-word frontmatter keys use snake_case (e.g., `resource_name`, `blocked_by`)
- All dates MUST be represented as YYYY-MM-DD
- **Underscore-prefixed directories** (e.g., `_dev/`, `_templates/`): Reserved for directories injected by a cross-cutting governance skill into a resource it doesn't own. The underscore prefix provides visual separation and sorts these above content directories. Directories owned by the resource itself use plain names without underscore prefix (e.g., `references/`, `operations/`, `transforms/`).
- `.claude/rules/` is managed by fe-sys-hq rule deployment — you MUST NOT manually edit, add, or remove rule files from this directory. If you believe a rule needs changing, edit the source in `.claude/skills/fe-governance-deploy/rules/` instead.

## Git

- Branch names MUST follow the pattern `{user-prefix}_{description}`
- Commit messages and PR descriptions are concise and bulleted
- Significant changes go through a branch with PR creation

## Python

- When invoking Python scripts, use the probe-then-run pattern for interpreter portability:
  `PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python); $PY "script.py" args`.
  This detects a working interpreter once and runs the script once with errors un-suppressed.
  Avoid `python "script" || python3 "script"` — when the first interpreter runs the script and
  the script errors, the fallback masks the real error behind whatever the second interpreter
  says (notably the "Python was not found" Microsoft Store stub on default-config Windows).

## .gitignore

- Every repo MUST have a `.gitignore` that covers: `.env`, credential files, OS artifacts, editor files
- You MUST verify `.gitignore` coverage before adding any integration that uses credentials — do not assume it is already covered
