---
version: "1.6.0"
updated: 2026-08-04
---
# Skill Loading Requirements

Mandatory skill loading requirements triggered by file and intent signals. Skills within each plugin handle fine-grained intent matching via their trigger descriptions.

- When the managed-document hook injects instructions after a Read, you MUST follow those instructions before responding to the user or taking any other action — even for read-only operations. Do not rationalize skipping injected instructions because the operation doesn't modify anything.
- If a file is in a `_dev/` directory or its filename starts with `chg_`, you MUST load the `change-management` skill
- If a file is within a knowledge base directory (at any depth) or has `kb_layer` frontmatter, you MUST load the KB type skill and the `kb-start` skill
- If the user intent involves querying, exploring, or learning about a knowledge base — even without referencing a specific file — you MUST load `kb-start` and the KB type skill (resolved from the KB root CLAUDE.md) before responding
- If the user intent is to create, rename, edit, or plan any change for a skill, plugin, marketplace, or any managed resource, you MUST load the resource-specific management skill and the `change-management` skill
- If the user intent is to create or request a *new* change specifically — a new backlog item, or "log a change" / "file this upstream" — you MUST additionally load the `change-capture` skill, so its redundancy investigation runs before a duplicate change document is written. This narrower create/request-a-change signal is the only one that loads `change-capture`; renaming, editing, or planning an existing change does not.
