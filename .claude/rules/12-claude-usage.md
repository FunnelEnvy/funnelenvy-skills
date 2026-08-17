---
version: "1.10.0"
updated: 2026-08-14
---
# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution, context ownership, approval doctrine, and concurrency posture.

- If multiple skills or plugins could handle an intent, you MUST resolve in this priority order: (1) repo-specific skills, (2) fe-sys-hq marketplace plugins, (3) other marketplace plugins, (4) device-level configuration. If a repo-specific skill exists, you MUST use it even if a marketplace plugin also matches.
- If you are about to write auto memory (`~/.claude/projects/*/memory/`), stop and ask: does this belong in a repo-managed document instead? If the information is project context, architectural decisions, resource state, or workflow knowledge, you MUST use a repo file. Auto memory is ONLY for truly personal user preferences that have no repo-level home.
- If you are about to store project context in a user-level location (`~/.claude/CLAUDE.md`, user settings), you MUST alert the user and explain why a repo file may be more appropriate.
- If governance rules, skill instructions, or hook-injected instructions require loading context before proceeding, you MUST complete those steps before responding — even if the user's question appears simple. Skipping governance steps to answer faster degrades output quality.
- When executing a multi-step operation (4+ numbered procedural steps), you MUST use step or task tracking to create an entry for each step before starting step 1. Mark each complete as you finish it. This prevents later steps from being silently skipped. In Claude Code, use `TaskCreate` and `TaskUpdate`.
- When executing tracked steps, limit narration of step or task transitions in text output. The TaskCreate/TaskUpdate terminal UI provides progress visibility — prefer it over text narration. Only surface text output when the agent would benefit from chain-of-thought or the task requires user input, approval, or a decision. If the user explicitly requests full narration, provide it.
- You MUST apply the `human-content-transform` base layer at the `internal/technical` default to all user-facing prose you produce — whether or not the user asked to "humanize." It is an always-on readability floor, not a step that waits to be invoked. The always-present floor, in brief: prefer shorter sentences and rewrite any runaway past ~30 words; reduce clause-nesting and hedging; cut parenthetical and em-dash nesting; keep structure navigable and lead with the point. Guard against over-stripping — keep load-bearing terms, numbers, names, and caveats; readability is not dumbing-down. This is a compact projection of the skill's floor, not the full ruleset: the complete readability floor and the AI-tell catalog stay single-homed in the base layer at `fe-sys-hq:plugins/fe-governance/skills/human-content-transform/SKILL.md` — apply from there for external audiences, `message` shaping, or a deeper scrub, and do not restate the catalog here. This inline projection and that skill's readability floor are a synced pair: an edit to one must flag the other.

## Approval Doctrine

- If the intent involves where an approval belongs (a native `settings.json` rule vs a `PreToolUse` hook), constructing the ask/deny/allow safety set, authoring the deployed `settings.json` `permissions` block, writing a fail-closed deny or auto-approve hook, reconciling `settings.local.json`, or covering subagent/remote approvals, you MUST load the `permissions-management` skill (in the `claude-code-management` plugin) before acting.
- `permissions-management` owns the approval-doctrine model and the composition rule; per-integration MCP tool classification is owned by the fe-integrations skills. You MUST treat those as the authorities rather than re-deriving approval layering here.

## Concurrency Posture

- You SHOULD proactively detect independent work — pieces with no ordering dependency between them — and default to running it concurrently rather than serially. This applies equally to in-session sub-agent fan-out and to cross-session/remote dispatch: concurrency is the default posture for independent work, not a mode you switch on only when explicitly asked.
- For the single-writer ownership of the shared working tree and the index/pathspec safety mechanics that concurrent execution depends on, see [14-git-operations](14-git-operations.md#git-operation-ownership-shared-working-tree).
