---
version: "1.8.0"
updated: 2026-10-09
---
# Skill Loading Requirements

Mandatory skill loading requirements triggered by file and intent signals. Skills within each plugin handle fine-grained intent matching via their trigger descriptions.

You MUST complete every load below before responding or acting, even when the question appears simple. The same holds for any skill, reference or file that another rule, a skill or a hook-injected instruction requires you to load.

- When the managed-document hook injects instructions after a Read, you MUST follow those instructions before responding to the user or taking any other action — even for read-only operations. Do not rationalize skipping injected instructions because the operation doesn't modify anything.
- If a file is in a `_dev/` directory or its filename starts with `chg_`, load the `change-management` skill.
- If a file is within a knowledge base directory (at any depth) or has `kb_layer` frontmatter, load the KB type skill and the `kb-start` skill.
- If the user intent involves querying, exploring, or learning about a knowledge base — even without referencing a specific file — load `kb-start` and the KB type skill named in the knowledge base's own `CLAUDE.md`.
- If the user intent involves reading from or writing to an external service, load that service's `*-start` skill, which integration-start's `Known Integrations` names. Do this even when a connector tool for the service is already available. When `Known Integrations` names no skill for the service, or does not list it, load `integration-start`. In a repo that does not enable the `fe-integrations` plugin, skip this load.
- If the user intent is to create a managed document, or to review one the session has not read, load the `document-management` skill. The hook covers a Read.
- If the user intent is to create, rename, edit, or plan any change for a skill, plugin, marketplace, or any managed resource, load the resource-specific management skill and the `change-management` skill.
- If the user intent is to create or request a *new* change specifically — a new backlog item, or "log a change" / "file this upstream" — additionally load the `change-capture` skill, so its redundancy investigation runs before a duplicate change document is written. This narrower create/request-a-change signal is the only one that loads `change-capture`; renaming, editing, or planning an existing change does not.
