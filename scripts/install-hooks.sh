#!/usr/bin/env bash
# Install the client-reference guard git hooks by pointing core.hooksPath at the tracked hooks/ dir.
# Idempotent. Run once per clone. No client data, no local setup needed (the guard is self-contained).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git config core.hooksPath hooks
chmod +x hooks/pre-commit hooks/commit-msg scripts/client_ref_guard.py 2>/dev/null || true

echo "client-ref-guard: hooks installed (core.hooksPath -> hooks/)."
echo "The guard scans staged content and commit messages for company-shaped strings."
echo "Rule: never write a real company name in this public repo -- use a fake placeholder or omit it."
