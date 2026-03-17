---
fe-managed: true
name: intent-routing
document_type: fe-governance-deploy/rule-document
preload_instructions: >
  Before taking further action with this document, you MUST read the document-management skill, the fe-governance-deploy skill and all skills dependent to it, and the rule-document-template.md template file.
description: >
  Intent to plugin routing for all managed repos. Maps user intent categories to the appropriate
  plugin, with skills handling fine-grained matching via trigger descriptions.
version: "1.0.0"
created: 2026-03-06
updated: 2026-03-12
---

# Intent Routing

Route skill loading based on file signals. Skills within each plugin handle fine-grained intent matching via their trigger descriptions.

## Markdown File Gate (MANDATORY)

Without this gate, answers may be structurally correct but semantically wrong within the governance model — even for simple tasks like a grep or reference check.

When the user message contains a managed markdown file path — whether as a target for reading, editing, deleting, moving, searching, or searching *for references to it* — you MUST complete the following gate before performing any other action:

1. Read the file's YAML frontmatter
2. Complete all applicable rows in the Prerequisite Loading table below
3. Only then proceed to the intended action

DO NOT skip this gate. Skipping is a rule violation even if the task appears simple enough to not need it. A "just grep for it" shortcut is still a violation.

## Prerequisite Loading

Load the governing skill to ensure relevant standards are in context. All applicable rows MUST be completed — they are not mutually exclusive.

| Signal | Load |
|---|---|
| File contains YAML frontmatter (`---` block) | `document-management` skill (which then parses `document_type`, if present, to load the owning skill) |
| File is in a `_dev/` directory or filename starts with `chg_` | `change-management` skill |
| User intent is to create a new managed resource (plugin, skill, knowledge base, etc.) or plan a change to an existing one | `change-management` skill |
| Any skill is being invoked | `skill-management` skill (so that skill dependencies resolve correctly) |
