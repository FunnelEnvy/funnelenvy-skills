---
name: claude-usage
document_type: fe-governance-deploy/rule-document
description: >
  Claude Code agent behavior conventions for all managed repos. Covers skill resolution priority,
  user-level vs. repo-level context ownership, and information lookup order.
version: "1.0.0"
created: 2026-03-08
updated: 2026-03-08
---

# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution, context ownership, and information lookup order.

## Skill Preference Priority

When multiple skills or plugins could handle an intent, resolve in this order:

1. Repo-specific skills (`skills/` directory in the current repo)
2. fe-sys-hq marketplace plugins (distributed governance and integrations)
3. Device-level configuration (user-level `~/.claude/CLAUDE.md`)

## User-Level vs. Repo-Level Context

- Generally avoid user-level features for project context — prefer repo-managed files (CLAUDE.md, rules, knowledge base, skills, change documents)
- User-level features are appropriate for truly device-specific config (OS, shell, paths, runtimes) and personal preferences (editor, keybindings)
- Generally avoid auto memory (`~/.claude/projects/*/memory/`) — if something is worth remembering, it belongs in a repo file
- Rationale: repo files are version-controlled, reviewable, and shared; user-level features are local and invisible to the team

## Context Hierarchy

When looking for information, search in this order:

1. Current repo files (CLAUDE.md, rules, knowledge base, skills)
2. Marketplace resources (fe-sys-hq distributed plugins)
3. User-level `~/.claude/CLAUDE.md`
4. Conversation context / session state
