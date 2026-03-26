---
version: "1.3.2"
updated: 2026-03-25
---
# Intent Routing

Route skill loading based on file signals. Skills within each plugin handle fine-grained intent matching via their trigger descriptions.

## Managed Document Gate

Skipping this gate means the governing skill context is missing — edits will miss required standards, searches will miss relevant files, reviews will apply the wrong criteria, and informational answers will miss architectural context that only the governing skill provides.

When the user message references a managed markdown file path or directory that contains markdown files — for reading, editing, deleting, moving, searching, or searching *for references to it* — complete this gate before any next step, including responding to the user:

1. Read the file — for `fe-managed: true` documents, the managed-document hook injects preload instructions as a system reminder after the Read
2. Follow the injected preload instructions — these load the governing skill, its dependencies, and any lifecycle skill. The hook output is not advisory; treat it as a blocking prerequisite
3. Complete all applicable rows in the Prerequisite Loading tables below — these cover signals the hook does not handle
4. Then proceed with the original task

## Prerequisite Loading

Load the governing skill to ensure relevant standards are in context. All applicable rows MUST be completed — they are not mutually exclusive.

### File Signals

| Signal                                                        | Load                                                                                                                                                            |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File contains `fe-managed: true` frontmatter field            | Follow the preload instructions injected by the managed-document hook (loads `document-management` skill, governing skill, dependencies, and lifecycle skill) |
| File is in a `_dev/` directory or filename starts with `chg_` | `change-management` skill                                                                                                                                     |
| `governed_by` field value contains `knowledge-base`           | `knowledge-base` skill                                                                                                                                        |

### Intent Signals

| Signal                                                                                            | Load                                                                          |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| User intent is to create, rename, or edit a skill, plugin, or marketplace resource                | The resource-specific management skill ("what") and `change-management` skill |
| User intent is to create or edit a knowledge base or asks questions about files in a knowledge base | The KB type skill ("what") and `knowledge-base` skill                         |
| User intent is to plan a change to a managed resource                                             | `change-management` skill                                                     |
| Any skill is being invoked                                                                        | `skill-management` skill (so that skill dependencies resolve correctly)       |
