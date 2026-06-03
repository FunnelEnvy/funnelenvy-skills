---
fe-managed: true
name: public-repo-client-reference-guard
description: >
  Add a mechanical guard (pre-commit hook or CI check) that scans staged content and commit
  metadata for client-identifying strings before they land in this public repo, replacing manual
  sanitization and after-the-fact branch-history rewrites.
governed_by: change-management/change-document
status: Backlog
resource_name: repo
resource_version: "TBD"
impact: 3
confidence: 3
ease: 3
version: "0.1.0"
created: 2026-06-03
updated: 2026-06-03
---

# Public-Repo Client-Reference Sweep Guard

## Open Issues

**Source:** Approach OQ
**Generated:** 2026-06-03 11:00 PT

### Findings Detail

| # | Source | Finding | Description | Recommendation |
|---|---|---|---|---|
| 1 | Approach OQ | Denylist sourcing | The guard needs a list of client-identifying strings, but the list itself cannot live in this public repo (it would contain exactly the names it guards against). | Source the pattern list from outside the repo: an untracked local file (gitignored, e.g. `.client-denylist`), an environment variable, or a private shared location each contributor syncs. Decide during Discovery. |
| 2 | Approach OQ | Enforcement point | Pre-commit hook (local, can be skipped) vs CI check (server-side, catches everything but after push, when the leak already left the machine). | Both: local pre-commit as the primary guard, CI as backstop. For a public repo, post-push detection is already too late, so the local hook is the one that matters most. Decide during Discovery. |

## Background

This repo is public. During the positioning-framework Path B adaptation (2026-06-03 session),
client references had to be manually sanitized from a change document and branch history rewritten
to remove client strings from commits before anything was pushed. That was reactive and
error-prone. The Path B initiative keeps introducing client-adjacent content (each skill
adaptation references client engagements), so the leak risk recurs with every change doc and
commit in this repo.

## Current State

- No automated guard exists. `.gitignore` covers credential files but nothing scans content or
  commit messages for client identifiers.
- Sanitization is manual: grep sweeps and history rewrites performed ad hoc per session.

## Approach

To be developed in Discovery. Sketch: a small script (stdlib Python or shell) run as a pre-commit
hook and optionally in CI that greps staged files and the commit message against an
externally-sourced pattern list, blocking the commit on a hit. Zero external dependencies per repo
conventions.

## Requirements

Stub — filled during Design after Approach approval.

## Validation

Stub — at minimum: a staged file containing a denylisted string blocks the commit; a clean commit
passes; the denylist itself is verifiably absent from tracked content.

## Changelog

| Version | Changes |
|---|---|
| 0.1.0 | Initial backlog creation from change-capture proposal (Discovery → Design transition of positioning-framework-kb-native-writes) |
