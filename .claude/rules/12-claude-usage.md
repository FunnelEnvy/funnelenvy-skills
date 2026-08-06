---
version: "1.7.0"
updated: 2026-08-05
---
# Claude Usage

Claude Code agent behavior conventions for all managed repos. Covers skill resolution, context ownership, and git-operation ownership.

- If multiple skills or plugins could handle an intent, you MUST resolve in this priority order: (1) repo-specific skills, (2) fe-sys-hq marketplace plugins, (3) other marketplace plugins, (4) device-level configuration. If a repo-specific skill exists, you MUST use it even if a marketplace plugin also matches.
- If you are about to write auto memory (`~/.claude/projects/*/memory/`), stop and ask: does this belong in a repo-managed document instead? If the information is project context, architectural decisions, resource state, or workflow knowledge, you MUST use a repo file. Auto memory is ONLY for truly personal user preferences that have no repo-level home.
- If you are about to store project context in a user-level location (`~/.claude/CLAUDE.md`, user settings), you MUST alert the user and explain why a repo file may be more appropriate.
- If governance rules, skill instructions, or hook-injected instructions require loading context before proceeding, you MUST complete those steps before responding — even if the user's question appears simple. Skipping governance steps to answer faster degrades output quality.
- When executing a multi-step operation (4+ numbered procedural steps), you MUST use step or task tracking to create an entry for each step before starting step 1. Mark each complete as you finish it. This prevents later steps from being silently skipped. In Claude Code, use `TaskCreate` and `TaskUpdate`.
- When executing tracked steps, limit narration of step or task transitions in text output. The TaskCreate/TaskUpdate terminal UI provides progress visibility — prefer it over text narration. Only surface text output when the agent would benefit from chain-of-thought or the task requires user input, approval, or a decision. If the user explicitly requests full narration, provide it.
- You SHOULD phrase responses in plain, direct, concise language and include a concrete example where it aids understanding. Strongly favor plain phrasing by default, but do not sacrifice technical precision, required terminology, or completeness to satisfy this rule. For the canonical ruleset this bullet serves — the specific AI-writing patterns to avoid and the plain-language principles (ISO 24495-1-aligned) to apply — see the `human-content-transform` skill's base-rules layer at `fe-sys-hq:plugins/fe-governance/skills/human-content-transform/SKILL.md`.

## Git-Operation Ownership (Shared Working Tree)

Concurrent agents committing to one shared working tree stop the main agent from trusting its own view of `HEAD`, the index, and the tree, forcing wasteful defensive re-checking and conflict-hedging; a single-writer convention removes that overhead.

- Only the orchestrating (main) agent MUST commit or push to the shared working tree — a subagent or background task MUST NOT run `git commit` or `git push` against the checkout the main agent is using.
- Every subagent and background task MUST either (a) **isolate** — run in its own git worktree, where it may commit, with the main agent orchestrating the landing of that work (e.g. a merge); or (b) **return work** — hand its result (edits left in the tree, a diff, or a structured result) back to the main agent, which performs the commit. These are the only two sanctioned patterns.
- There is NO sequential exception: even a blocking, one-at-a-time subagent MUST NOT self-commit to the shared tree. Committing to the shared tree is never a subagent or background-task responsibility, whether it runs concurrently or in sequence.
- With one writer to the shared tree, the main agent MUST treat its own git view as authoritative and MUST NOT add defensive re-checking or conflict-hedging that exists only to guard against concurrent unowned commits.
- If you are directed to advance two or more change docs concurrently in one shared working tree, follow the `Interactive Concurrent Multi-Doc Execution` recipe in [fe-sys-hq:plugins/fe-governance/skills/change-management/SKILL.md](fe-sys-hq:plugins/fe-governance/skills/change-management/SKILL.md) rather than defaulting to serial execution. It composes the two primitives above; it does not add a third.
