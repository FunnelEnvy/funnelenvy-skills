---
version: "1.10.0"
updated: 2026-11-11
---
# Repo Conventions

Shared conventions for all managed repos: credentials; client data; scratch and temp files; file names, keys and dates; reserved directories; managed resources; Python invocation; and `.gitignore` coverage.

## Credentials (MANDATORY — Security Boundary)

Violating any credential rule is a security incident — leaked secrets cannot be unrotated. These rules have zero exceptions.

- NEVER store credentials, API keys, tokens, or secrets in repo files
- Store credentials in `.env` files or in a dedicated secret store, such as a password manager
- NEVER commit `.env` files — ensure `.gitignore` includes `.env` and all credential file patterns
- If you find a credential-shaped file that is neither tracked nor ignored, such as a private key, certificate, token file or `.env` variant, you MUST stop and tell the user. You MUST NOT commit it or change `.gitignore` for it until the user decides. For such a file, this bullet takes precedence over the other `.gitignore` instructions in this rule.
- NEVER prompt a user to input credentials into chat — set up `.env` with placeholders and let the user fill them in directly

## Client Data (MANDATORY)

**This section binds in two repos: `fe-sys-hq` and `steward-agent`.** Both are shared ground. Every managed repo takes its governance from the first, and every client instance runs the second, so a client's data written in either reaches readers with no connection to that client, and nothing downstream pulls it back. Elsewhere in the network a repo holds what its own purpose calls for. Each bar below holds even when the value is already on your screen and the sentence reads better with it.

In a tracked file in either repo:

- A client's measured values MUST NOT be written. Counts, rates, amounts, distinct-value counts, distributions and dates drawn from their systems are all measured values.
- A person on the client's side MUST NOT be named.
- A client's pricing or contract terms with FunnelEnvy MUST NOT be written: a price, rate, fee, discount, contract term, renewal date or other commercial condition. These are not drawn from the client's systems, so the first bar does not reach them.
- A field's declared value set is out of bounds, even though a describe call returns it without touching the client's records. It says what that client's process does, which is the thing this rule keeps in one place.
- A schema identifier naming a person on the client's side is out of bounds. It fails on the name, not on being an identifier.

In bounds in both repos:

- Schema identifiers. A field, object or API name may be written wherever a rule needs it — `Example_Source__c`, and the object it sits on.
- A client **organization**'s name. It is who FunnelEnvy works with, not anything drawn from their systems.
- A FunnelEnvy business figure aggregated across clients, such as an average engagement length, **when no single client's value can be recovered from it**. Aggregation is the whole test, and it is what clears the third bar as well as the first. An average over two clients is one subtraction away from each of them, which makes it a commercial term in an average's clothes.
- A repo name from `repo-registry.yaml`, and a `{repo-name}:path` cross-repo link. They name network infrastructure.
- Whatever this section admits is still subject to [fe-sys-hq:client-content-standard](fe-sys-hq:plugins/fe-knowledge-base/skills/kb-type-stack-monitor/references/client-content-standard.md) wherever that standard applies. In bounds here is not cleared for a surface a client reads.

Two clauses for work that crosses into these repos:

- When a change document, finding or requirement needs a measured value to make its point, state the rule the value demonstrates and cite the `{repo-name}:path` of the client's own repo that holds the measurement.
- A requirement routed into either repo carries the rule, not the values. Strip them before the dispatch, not after.

## Scratch and Temp Files

You MUST NOT deviate even when creating "temporary" or "one-off" files, or when the file will be deleted moments later. This holds even when the environment provides a session scratchpad and instructs you to prefer it: this rule governs, so these files MUST NOT go in the scratchpad.

- Temporary, scratch, and one-off files, including disposable migration scripts, MUST be created in the repo-root `tmp/` directory of the repo they support.
- Never create them anywhere else on the local device, including:
  - system temp, such as `/tmp/`
  - the harness session scratchpad
  - the home directory or the desktop
  - an unrelated repo
- This section applies except where a governing skill specifies otherwise.
- Each such file MUST begin with a `YYYY-MM-DD_` creation-date prefix, then the name in whatever convention otherwise applies (snake_case for Python scripts, kebab-case otherwise). Under `tmp/`, a dated directory carries the prefix and the entries inside it carry none of their own. Examples: `tmp/2026-08-07_migrate_links.py`, `tmp/2026-09-25_deploy/<repo-name>`.

## File Names, Keys and Dates

- All directory and filenames MUST be lowercase
- Default to kebab-case; use underscore ONLY when prefixed or suffixed by date (e.g., `2026-02-19_file-a`)
- Python files use snake_case
- Multi-word frontmatter keys use snake_case (e.g., `resource_name`, `blocked_by`)
- All dates MUST be represented as YYYY-MM-DD

## Reserved Directories

- **Underscore-prefixed directories** (e.g., `_dev/`, `_templates/`): Reserved for directories injected by a cross-cutting governance skill into a resource it doesn't own. Directories owned by the resource itself use plain names without underscore prefix (e.g., `references/`, `operations/`, `transforms/`).
- `.claude/rules/` is managed by fe-sys-hq rule deployment — you MUST NOT manually edit, add, or remove rule files from this directory. If you believe a rule needs changing, edit the source in `.claude/skills/fe-governance-deploy/rules/` instead.

## Managed Resources

A managed resource is a directory the system governs as one unit. The first row below whose signature a directory matches gives its type and governing skill.

| Type | Signature | Governing skill |
|---|---|---|
| Marketplace | `.claude-plugin/marketplace.json` | marketplace-management |
| Plugin | `.claude-plugin/plugin.json` | plugin-management |
| Skill | `SKILL.md` | skill-management |
| Knowledge base | `CLAUDE.md` whose frontmatter `governed_by` ends in `/kb-claude-md` | kb-start, plus the KB type skill that value names |
| Repo root | The repo's top-level directory | repo-standards |
| Component | `CHANGELOG.md` | change-management |

- Directories under `_tests/fixtures/` and `_evals/fixtures/` are not resources, whatever signature they carry.
- A path belongs to its nearest enclosing resource. A resource at the repo root covers only its signature file and the root's `README.md`, `CLAUDE.md` and `CHANGELOG.md`.
- A resource is versioned when it carries its own `CHANGELOG.md`. A marketplace, plugin or skill MUST carry one.
- A resource is distributed when a channel beyond the merge to `main`, such as the plugin marketplace or a governance deploy, ships it, a file in it or a resource enclosing it.

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
