---
version: "1.2.0"
updated: 2026-10-05
---
# Git Operations

Cross-cutting git conventions for all managed repos — how git work is structured, and who may commit to a shared working tree.

## Git Work Conventions

- Branch names MUST follow the pattern `{user-prefix}_{description}`.
- Commit messages and PR descriptions MUST be concise and bulleted.
- Implementation changes MUST go through a branch with PR creation — there is no trivial-change exception.
- The one exception is **fe-governance-deploy output** — the rules, `settings.json` and managed workflow files it distributes — which commits direct to `main` in each target repo. The approval that stands in for the PR is the `[User] Approve deploy strategy` gate the deploy takes before writing anything; a deploy that skipped that gate has no exception to rely on.

## Git-Operation Ownership (Shared Working Tree)

Concurrent agents committing to one shared working tree stop the main agent from trusting its own view of `HEAD`, the index, and the tree, forcing wasteful defensive re-checking and conflict-hedging; a single-writer convention removes that overhead.

- Only the orchestrating (main) agent MUST commit or push to the shared working tree — a subagent or background task MUST NOT run `git commit` or `git push` against the checkout the main agent is using.
- Every subagent and background task MUST either (a) **isolate** — run in its own git worktree, where it may commit, with the main agent landing that work (e.g. a merge); or (b) **return work** — hand its result (edits left in the tree, a diff, or a structured result) back to the main agent, which performs the commit. These are the only two sanctioned patterns.
- There is NO sequential exception: even a blocking, one-at-a-time subagent MUST NOT self-commit to the shared tree — committing to the shared tree is never a subagent or background-task responsibility, whether it runs concurrently or in sequence.
- The orchestrator MUST treat its own git view as authoritative and MUST NOT add defensive re-checking or conflict-hedging that exists only to guard against concurrent unowned commits.
- When subagents write **disjoint paths** and the orchestrator holds a pre-commit barrier as **sole committer**, that parallelism needs no worktree — but the sole committer MUST commit by **explicit pathspec** (`git add <path>` / `git commit -- <paths>`), never a blanket `git add -A`, because the index is shared state. This is the 2026-08-03 incident invariant: a bare commit captured a third file another subagent had staged. An explicit pathspec may list several paths and should list every path the change touches, both halves of a rename included. A multi-path `git add` or `git fetch` applies nothing if any one argument fails to match.
