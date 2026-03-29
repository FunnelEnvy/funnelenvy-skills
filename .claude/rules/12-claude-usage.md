---
version: "1.2.0"
updated: 2026-03-29
---
# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution and context ownership.

- If multiple skills or plugins could handle an intent, you MUST resolve in this priority order: (1) repo-specific skills, (2) fe-sys-hq marketplace plugins, (3) other marketplace plugins, (4) device-level configuration. If a repo-specific skill exists, you MUST use it even if a marketplace plugin also matches.
- If you are about to write auto memory (`~/.claude/projects/*/memory/`), stop and ask: does this belong in a repo-managed document instead? If the information is project context, architectural decisions, resource state, or workflow knowledge, you MUST use a repo file. Auto memory is ONLY for truly personal user preferences that have no repo-level home.
- If you are about to store project context in a user-level location (`~/.claude/CLAUDE.md`, user settings), you MUST alert the user and explain why a repo file may be more appropriate.
- If governance rules, skill instructions, or hook-injected instructions require loading context before proceeding, you MUST complete those steps before responding — even if the user's question appears simple. Skipping governance steps to answer faster degrades output quality.
- When executing a multi-step operation (5+ numbered procedural steps), you MUST use a step-tracking mechanism to track each step. Create all step entries upfront before starting step 1, mark each as you complete it. This prevents later steps from being silently skipped. In Claude Code, use `TaskCreate` and `TaskUpdate`; in other environments, use the equivalent task or checklist tooling available.
