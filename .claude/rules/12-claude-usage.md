---
version: "1.13.0"
updated: 2026-10-06
---
# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution, context ownership, step tracking, approval doctrine, and concurrency posture.

- If multiple skills or plugins could handle an intent, you MUST resolve in this priority order: (1) repo-specific skills, (2) fe-sys-hq marketplace plugins, (3) other marketplace plugins, (4) device-level configuration. If a repo-specific skill exists, you MUST use it even if a marketplace plugin also matches.
- If you are about to write auto memory (`~/.claude/projects/*/memory/`), stop and ask: does this belong in a repo-managed document instead? If the information is project context, architectural decisions, resource state, or workflow knowledge, you MUST use a repo file. Auto memory is ONLY for truly personal user preferences that have no repo-level home.
- If you are about to store project context in a user-level location (`~/.claude/CLAUDE.md`, user settings), you MUST alert the user and explain why a repo file may be more appropriate.
- All prose you write follows [15-writing-standards](15-writing-standards.md).

## Step Tracking

- When executing a multi-step operation (4+ numbered procedural steps), you MUST track it: create one entry per step before starting step 1, then mark each entry complete as you finish that step. This holds even when the operation looks simple. Tracking is what stops later steps from being silently skipped.
- If a tracking tool is available, use it. A tool is available when it is in your tool list or a deferred-tool search finds it. In a top-level Claude Code session those tools are `TaskCreate` and `TaskUpdate`, but any tool that keeps a per-step list meets the rule.
- If no tracking tool is available, as in a dispatched sub-agent, write the numbered step list in your response before step 1. Then report each step's completion in one line as you finish it. This discharges the same MUST in prose. Do not treat a missing tool as a reason to skip tracking.
- If a sub-operation runs inside a step that already has its own entry, it MAY run without entries of its own when its steps are short. Nested tracking can degrade performance.
- Keep narration of step transitions brief. If a tool's UI shows progress, prefer it over text narration. If none does, the one-line completion reports are the tracking, so keep each to one line. Surface more text only when the agent would benefit from chain-of-thought or the task requires user input, approval, or a decision. If the user explicitly requests full narration, provide it.

## Approval Doctrine

- If the intent involves where an approval belongs (a native `settings.json` rule vs a `PreToolUse` hook), constructing the ask/deny/allow safety set, authoring the deployed `settings.json` `permissions` block, writing a fail-closed deny or auto-approve hook, reconciling `settings.local.json`, or covering subagent/remote approvals, you MUST load the `permissions-management` skill (in the `claude-code-management` plugin) before acting.
- `permissions-management` owns the approval-doctrine model and the composition rule; per-integration MCP tool classification is owned by the fe-integrations skills. You MUST treat those as the authorities rather than re-deriving approval layering here.

## Concurrency Posture

- You SHOULD proactively detect independent work — pieces with no ordering dependency between them — and default to running it concurrently rather than serially. This applies equally to in-session sub-agent fan-out and to cross-session/remote dispatch: concurrency is the default posture for independent work, not a mode you switch on only when explicitly asked.
- For the single-writer ownership of the shared working tree and the index/pathspec safety mechanics that concurrent execution depends on, see [14-git-operations](14-git-operations.md#git-operation-ownership-shared-working-tree).
