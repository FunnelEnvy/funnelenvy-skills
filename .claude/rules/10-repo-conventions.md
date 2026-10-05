---
version: "1.6.0"
updated: 2026-10-05
---
# Repo Conventions

Shared file, directory, credential, and resource naming conventions for all managed repos.

## Credentials (MANDATORY — Security Boundary)

Violating any credential rule is a security incident — leaked secrets cannot be unrotated. These rules have zero exceptions.

- NEVER store credentials, API keys, tokens, or secrets in repo files
- Store credentials in `.env` files or in a dedicated secret store, such as a password manager
- NEVER commit `.env` files — ensure `.gitignore` includes `.env` and all credential file patterns
- NEVER prompt a user to input credentials into chat — set up `.env` with placeholders and let the user fill them in directly

## Files and Directories

You MUST NOT deviate even when creating "temporary" or "one-off" files. This holds even when the environment provides a session scratchpad and instructs you to prefer it: this rule governs, so these files MUST NOT go in the scratchpad.

- Temporary, scratch, and one-off files, including disposable migration scripts, MUST be created in the repo-root `tmp/` directory of the repo they support. Never create them elsewhere on the local device: the home directory, system temp, the harness session scratchpad, the desktop, or an unrelated repo. This bullet applies except where a governing skill specifies otherwise. Each such file MUST begin with a `YYYY-MM-DD_` creation-date prefix, then the name in whatever convention otherwise applies (snake_case for Python scripts, kebab-case otherwise). Under `tmp/`, a dated directory carries the prefix and the entries inside it carry none of their own. Examples: `tmp/2026-08-07_migrate_links.py`, `tmp/2026-09-25_deploy/<repo-name>`.
- All directory and filenames MUST be lowercase
- Default to kebab-case; use underscore ONLY when prefixed or suffixed by date (e.g., `2026-02-19_file-a`)
- Python files use snake_case matching skill name
- Multi-word frontmatter keys use snake_case (e.g., `resource_name`, `blocked_by`)
- All dates MUST be represented as YYYY-MM-DD
- **Underscore-prefixed directories** (e.g., `_dev/`, `_templates/`): Reserved for directories injected by a cross-cutting governance skill into a resource it doesn't own. The underscore prefix provides visual separation and sorts these above content directories. Directories owned by the resource itself use plain names without underscore prefix (e.g., `references/`, `operations/`, `transforms/`).
- `.claude/rules/` is managed by fe-sys-hq rule deployment — you MUST NOT manually edit, add, or remove rule files from this directory. If you believe a rule needs changing, edit the source in `.claude/skills/fe-governance-deploy/rules/` instead.

## Python

- When invoking Python scripts, use the probe-then-run pattern for interpreter portability:
  `PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python); $PY "script.py" args`.
  This detects a working interpreter once and runs the script once with errors un-suppressed.
  Avoid `python "script" || python3 "script"` — when the first interpreter runs the script and
  the script errors, the fallback masks the real error behind whatever the second interpreter
  says (notably the "Python was not found" Microsoft Store stub on default-config Windows).

## .gitignore

- Every repo MUST have a `.gitignore` that covers: `.env`, credential files, `tmp/`, OS artifacts, editor files
- You MUST verify `.gitignore` coverage before adding any integration that uses credentials — do not assume it is already covered
