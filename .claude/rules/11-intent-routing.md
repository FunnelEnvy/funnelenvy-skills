---
name: intent-routing
document_type: fe-governance-deploy/rule-document
description: >
  Intent to plugin routing for all managed repos. Maps user intent categories to the appropriate
  plugin, with skills handling fine-grained matching via trigger descriptions.
version: "1.0.0"
created: 2026-03-06
updated: 2026-03-06
---

# Intent Routing

Route user intent to the appropriate plugin. Skills within each plugin handle fine-grained matching via their trigger descriptions.

## Routing Table

| Intent | Plugin |
|---|---|
| Change lifecycle, versioning, changelogs, releases | `fe-governance` |
| Document creation, editing, review, standards | `fe-governance` |
| Marketplace, plugin, or skill authoring | `claude-code-management` |
| Integration planning, setup, API connections, MCP | `fe-integrations` |
| Knowledge base artifacts, layer transitions | `fe-knowledge-base` |

## Prerequisite Loading

Always load `claude-code-management:skill-management` before invoking any skill, so that skill dependencies resolve correctly.

When reading files, load the governing skill to ensure relevant standards are in context:

| Signal | Load |
|---|---|
| File contains YAML frontmatter with `document_type` field | `document-management` skill (which then parses `document_type` to load the owning skill) |
| File is named `SKILL.md` | `skill-management` skill |
