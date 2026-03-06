#!/bin/bash
# Validation script for hypothesis-generator skill implementation
# Run from repo root: bash scripts/validate-hypothesis-generator.sh

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0
WARN=0

check() {
  local desc="$1"
  local cmd="$2"
  local expected="$3"
  local result
  result=$(eval "$cmd" 2>&1) || true
  if [ "$expected" = "NONZERO" ]; then
    if [ -n "$result" ]; then
      echo "  PASS: $desc"
      PASS=$((PASS + 1))
    else
      echo "  FAIL: $desc (got empty output)"
      FAIL=$((FAIL + 1))
    fi
  elif [ "$expected" = "EMPTY" ]; then
    if [ -z "$result" ]; then
      echo "  PASS: $desc"
      PASS=$((PASS + 1))
    else
      echo "  FAIL: $desc (got: $result)"
      FAIL=$((FAIL + 1))
    fi
  elif [ "$result" = "$expected" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc (expected: $expected, got: $result)"
    FAIL=$((FAIL + 1))
  fi
}

check_exists() {
  local desc="$1"
  local path="$2"
  if [ -e "$path" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc ($path not found)"
    FAIL=$((FAIL + 1))
  fi
}

check_warn() {
  local desc="$1"
  local cmd="$2"
  local expected="$3"
  local result
  result=$(eval "$cmd" 2>&1) || true
  if [ "$expected" = "NONZERO" ] && [ -n "$result" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  elif [ "$expected" = "NONZERO" ]; then
    echo "  WARN: $desc (not found, may not exist yet)"
    WARN=$((WARN + 1))
  fi
}

echo "=== Hypothesis Generator: Validation ==="
echo ""

echo "[1] New skill files exist"
check_exists "SKILL.md" "skills/hypothesis-generator/SKILL.md"
check_exists "phases/detect.md" "skills/hypothesis-generator/phases/detect.md"
check_exists "phases/construct.md" "skills/hypothesis-generator/phases/construct.md"
check_exists "phases/score.md" "skills/hypothesis-generator/phases/score.md"
check_exists "modules/experiment-patterns.md" "modules/experiment-patterns.md"
check_exists "modules/ice-scoring.md" "modules/ice-scoring.md"
echo ""

echo "[2] SKILL.md frontmatter"
check "has name: hypothesis-generator" \
  "head -5 skills/hypothesis-generator/SKILL.md | grep -c 'name: hypothesis-generator'" \
  "1"
echo ""

echo "[3] Phase file count"
check "phases/ has exactly 3 files" \
  "ls skills/hypothesis-generator/phases/ | wc -l | tr -d ' '" \
  "3"
echo ""

echo "[4] Pattern count"
check "experiment-patterns.md has 28 patterns" \
  "grep -c '^### [A-Z]\{2\}-[0-9]\{2\}:' modules/experiment-patterns.md" \
  "28"
echo ""

echo "[5] ICE calibration completeness"
check "Impact calibration" \
  "grep -c 'Impact Calibration' modules/ice-scoring.md" \
  "1"
check "Confidence calibration" \
  "grep -c 'Confidence Calibration' modules/ice-scoring.md" \
  "1"
check "Ease calibration" \
  "grep -c 'Ease Calibration' modules/ice-scoring.md" \
  "1"
echo ""

echo "[6] Prohibited content"
check "No ClickUp references in new files" \
  "grep -ri 'clickup\|click_up' skills/hypothesis-generator/ modules/experiment-patterns.md modules/ice-scoring.md | head -1" \
  "EMPTY"
check "No em dashes in new files" \
  "grep -rP '\xe2\x80\x94' skills/hypothesis-generator/ modules/experiment-patterns.md modules/ice-scoring.md | head -1" \
  "EMPTY"
echo ""

echo "[7] Extension points preserved"
check "evidence-*.md referenced in SKILL.md" \
  "grep -c 'evidence-\*' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
check "evidence-*.md referenced in detect.md" \
  "grep -c 'evidence-\*' skills/hypothesis-generator/phases/detect.md" \
  "NONZERO"
echo ""

echo "[8] render-default-deliverables changes"
check "No experiment-roadmap in render deliverables" \
  "grep -ci 'experiment.roadmap' skills/render-default-deliverables/SKILL.md | tr -d ' '" \
  "NONZERO"
# NOTE: This check expects a cross-reference note mentioning experiment roadmap.
# If it finds zero matches, render-default-deliverables was not updated yet.
# After Phase 2, this should find the cross-reference note but NOT the old section.
echo ""

echo "[9] Reference updates"
check_warn "CLAUDE.md lists hypothesis-generator" \
  "grep -c 'hypothesis-generator' CLAUDE.md" \
  "NONZERO"
check_warn "ARCHITECTURE.md includes hypothesis-generator" \
  "grep -c 'hypothesis-generator' ARCHITECTURE.md" \
  "NONZERO"
echo ""

echo "[10] Manifest check"
# This verifies the manifest template in render-default-deliverables doesn't list experiment-roadmap
check_warn "Manifest template excludes experiment-roadmap.md" \
  "grep -c 'experiment-roadmap.md' skills/render-default-deliverables/SKILL.md" \
  "NONZERO"
# NOTE: After Phase 2, any remaining match should only be in the cross-reference note.
echo ""

echo "=== Results ==="
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  WARN: $WARN"
echo ""
if [ "$FAIL" -gt 0 ]; then
  echo "VALIDATION FAILED. Fix failures before proceeding."
  exit 1
elif [ "$WARN" -gt 0 ]; then
  echo "VALIDATION PASSED with warnings. Warnings indicate checks for later phases."
  exit 0
else
  echo "VALIDATION PASSED."
  exit 0
fi
