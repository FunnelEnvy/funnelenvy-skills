---
version: "1.3.0"
updated: 2026-03-30
---
# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution and context ownership.

- If multiple skills or plugins could handle an intent, you MUST resolve in this priority order: (1) repo-specific skills, (2) fe-sys-hq marketplace plugins, (3) other marketplace plugins, (4) device-level configuration. If a repo-specific skill exists, you MUST use it even if a marketplace plugin also matches.
- If you are about to write auto memory (`~/.claude/projects/*/memory/`), stop and ask: does this belong in a repo-managed document instead? If the information is project context, architectural decisions, resource state, or workflow knowledge, you MUST use a repo file. Auto memory is ONLY for truly personal user preferences that have no repo-level home.
- If you are about to store project context in a user-level location (`~/.claude/CLAUDE.md`, user settings), you MUST alert the user and explain why a repo file may be more appropriate.
- If governance rules, skill instructions, or hook-injected instructions require loading context before proceeding, you MUST complete those steps before responding — even if the user's question appears simple. Skipping governance steps to answer faster degrades output quality.
- When executing a multi-step operation (4+ numbered procedural steps), you MUST use step or task tracking to create an entry for each step before starting step 1. Mark each complete as you finish it. This prevents later steps from being silently skipped. In Claude Code, use `TaskCreate` and `TaskUpdate`.
- When executing tracked steps, limit narration of step or task transitions in text output. The TaskCreate/TaskUpdate terminal UI provides progress visibility — prefer it over text narration. Only surface text output when the agent would benefit from chain-of-thought or the task requires user input, approval, or a decision. If the user explicitly requests full narration, provide it.
