---
fe-managed: true
name: claude-usage
document_type: fe-governance-deploy/rule-document
preload_instructions: >
  Before taking further action with this document, you MUST read the document-management skill, the fe-governance-deploy skill and all skills dependent to it, and the rule-document-template.md template file.
description: >
  Claude Code agent behavior conventions for all managed repos. Covers skill resolution priority
  and user-level vs. repo-level context ownership.
version: "1.0.0"
created: 2026-03-08
updated: 2026-03-12
---

# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution and context ownership.

## Skill Preference Priority (MANDATORY)

Skipping this priority order causes inconsistent behavior across conversations — the agent picks whichever skill loads fastest instead of the correct one.

When multiple skills or plugins could handle an intent, you MUST resolve in this order. Do not skip to a lower-priority source because it is faster or already loaded.

1. Repo-specific skills (`skills/` directory in the current repo)
2. fe-sys-hq marketplace plugins (distributed governance and integrations)
3. Other marketplace plugins
4. Device-level configuration (user-level `~/.claude/CLAUDE.md`)

If a repo-specific skill exists for the intent, you MUST use it even if a marketplace plugin also matches.

## User-Level vs. Repo-Level Context

- You MUST use repo-managed files (CLAUDE.md, rules, knowledge base, skills, change documents) for project context. You MUST NOT store project context in a user-level location without first alerting the user and explaining why a repo file may be more appropriate.
- You MUST use repo files over auto memory (`~/.claude/projects/*/memory/`) for project information. You MUST NOT write auto memory for something that could live in a repo file without flagging it to the user first.
- User-level features are appropriate ONLY for truly device-specific config (OS, shell, paths, runtimes) and personal preferences (editor, keybindings).
