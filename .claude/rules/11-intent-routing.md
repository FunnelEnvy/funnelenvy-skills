---
version: "1.4.0"
updated: 2026-03-26
---
# Intent Routing

Route skill loading based on file and intent signals. Skills within each plugin handle fine-grained intent matching via their trigger descriptions.

- When the managed-document hook injects preload instructions after a Read, you MUST follow those instructions before responding to the user or taking any other action. The hook output is a blocking prerequisite, not advisory context.
- If a file is in a `_dev/` directory or its filename starts with `chg_`, you MUST load the `change-management` skill
- If a file's `governed_by` field value contains `knowledge-base`, you MUST load the `knowledge-base` skill
- If the user intent is to create, rename, or edit a skill, plugin, or marketplace resource, you MUST load the resource-specific management skill and the `change-management` skill
- If the user intent is to create or edit a knowledge base, or asks questions about files in a knowledge base, you MUST load the KB type skill and the `knowledge-base` skill
- If the user intent is to plan a change to a managed resource, you MUST load the `change-management` skill
