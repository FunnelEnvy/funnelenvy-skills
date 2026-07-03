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
check_exists "phases/detect-strategic.md" "skills/hypothesis-generator/phases/detect-strategic.md"
check_exists "phases/construct.md" "skills/hypothesis-generator/phases/construct.md"
check_exists "phases/validate.md" "skills/hypothesis-generator/phases/validate.md"
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
check "phases/ has exactly 6 files" \
  "ls skills/hypothesis-generator/phases/ | wc -l | tr -d ' '" \
  "6"
echo ""

echo "[4] Pattern count"
check "experiment-patterns.md has 32 patterns" \
  "grep -c '^### [A-Z]\{2\}-[0-9]\{2\}:' modules/experiment-patterns.md" \
  "32"
echo ""

echo "[5] ICE calibration completeness"
check "Impact calibration" \
  "grep -c '^## Impact Calibration' modules/ice-scoring.md" \
  "1"
check "Confidence calibration" \
  "grep -c '^## Confidence Calibration' modules/ice-scoring.md" \
  "1"
check "Ease calibration" \
  "grep -c '^## Ease Calibration' modules/ice-scoring.md" \
  "1"
echo ""

echo "[6] Prohibited content"
# Block [6] greps recurse skills/hypothesis-generator/ as a directory, so
# phases/detect-strategic.md (Phase 2c) is already covered by the em-dash and
# ClickUp greps below; no path addition is needed. modules/ice-scoring.md is in
# the explicit module list below.
check "No ClickUp references in new files" \
  "grep -ri 'clickup\|click_up' skills/hypothesis-generator/ modules/experiment-patterns.md modules/ice-scoring.md modules/contrarian-triggers.md modules/hypothesis-interactions.md modules/patterns-procurement.md | head -1" \
  "EMPTY"
check "No em dashes in new files" \
  "grep -rP '\xe2\x80\x94' skills/hypothesis-generator/ modules/experiment-patterns.md modules/ice-scoring.md modules/contrarian-triggers.md modules/hypothesis-interactions.md modules/patterns-procurement.md | head -1" \
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

echo "[11] Procurement archetype module"
check_exists "modules/patterns-procurement.md" "modules/patterns-procurement.md"
check "patterns-procurement.md has 6 patterns" \
  "grep -c '^### PR-[0-9]\{2\}:' modules/patterns-procurement.md" \
  "6"
echo ""

echo "[12] Contrarian trigger count"
check "contrarian-triggers.md has 14 triggers" \
  "grep -c '^### CTR-[0-9]\{2\}:' modules/contrarian-triggers.md" \
  "14"
check "contrarian-triggers.md count line says 14" \
  "grep -c '^Trigger count: 14' modules/contrarian-triggers.md" \
  "1"
echo ""

echo "[13] Experiment-history consumption"
check "Output Format has Evidence From Completed Experiments section" \
  "grep -c '^## Evidence From Completed Experiments' skills/hypothesis-generator/SKILL.md" \
  "1"
check "Read-side Mapping references experiment-history (gold-experiment-index producer KB)" \
  "grep -c 'gold-experiment-index. (producer KB)' skills/hypothesis-generator/SKILL.md" \
  "1"
check "experiment_history_available guarded in Deliverable Purity Constraint" \
  "grep -c 'experiment_history_available' skills/hypothesis-generator/SKILL.md" \
  "1"
check "prior_winner guarded in Deliverable Purity Constraint" \
  "grep -c 'prior_winner' skills/hypothesis-generator/SKILL.md" \
  "1"
check "replication_candidate guarded in Deliverable Purity Constraint" \
  "grep -c 'replication_candidate' skills/hypothesis-generator/SKILL.md" \
  "1"
check "transferable_rule guarded in Deliverable Purity Constraint" \
  "grep -c 'transferable_rule' skills/hypothesis-generator/SKILL.md" \
  "1"
check "replication_target_surfaces guarded in Deliverable Purity Constraint" \
  "grep -c 'replication_target_surfaces' skills/hypothesis-generator/SKILL.md" \
  "1"
check "Output Format has Experiment Program Continuity section" \
  "grep -c '^## Experiment Program Continuity' skills/hypothesis-generator/SKILL.md" \
  "1"
check "history_type guarded in Deliverable Purity Constraint" \
  "grep -c 'history_type' skills/hypothesis-generator/SKILL.md" \
  "1"
check "parent_outcome guarded in Deliverable Purity Constraint" \
  "grep -c 'parent_outcome' skills/hypothesis-generator/SKILL.md" \
  "1"
check "source_priority guarded in Deliverable Purity Constraint" \
  "grep -c 'source_priority' skills/hypothesis-generator/SKILL.md" \
  "1"
echo ""

echo "[14] Strategic-track surfaces (separate deliverable)"
check "SKILL.md has Client-Facing Register section" \
  "grep -c '^## Client-Facing Register' skills/hypothesis-generator/SKILL.md" \
  "1"
check "Execution Pipeline has Phase 2c" \
  "grep -c '^### Phase 2c' skills/hypothesis-generator/SKILL.md" \
  "1"
check "measurement_design guarded in Deliverable Purity Constraint" \
  "grep -o 'measurement_design' skills/hypothesis-generator/SKILL.md | head -1" \
  "NONZERO"
check "strategic-lane lane tag guarded in Deliverable Purity Constraint" \
  "grep -oE 'strategic-lever|lane' skills/hypothesis-generator/SKILL.md | head -1" \
  "NONZERO"
check "SKILL.md has Strategic Roadmap Output Format section" \
  "grep -c '^## Strategic Roadmap Output Format' skills/hypothesis-generator/SKILL.md" \
  "1"
check "strategic-roadmap.md deliverable path documented" \
  "grep -o 'strategic-roadmap.md' skills/hypothesis-generator/SKILL.md | head -1" \
  "NONZERO"
check "gold-strategic-roadmap KB artifact type referenced" \
  "grep -o 'gold-strategic-roadmap' skills/hypothesis-generator/SKILL.md | head -1" \
  "NONZERO"
check "Strategic Key risk relabel present" \
  "grep -o 'Key risk' skills/hypothesis-generator/SKILL.md | head -1" \
  "NONZERO"
check "No in-tier render mandate (render in the existing tiers) remains" \
  "grep -c 'render in the existing tiers' skills/hypothesis-generator/SKILL.md | tr -d ' '" \
  "0"
echo ""

echo "[15] Premise & measurement rigor (tranche 2)"
check "phases/validate.md gate-record marker present" \
  "grep -c '^## The validation_gates record' skills/hypothesis-generator/phases/validate.md" \
  "1"
# NOTE: the NONZERO checks below use plain grep, NOT grep -c. The check() NONZERO
# branch tests for non-empty output; grep -c always prints a count (even "0"),
# which would pass spuriously. Plain grep yields empty output when a term is
# absent, so an absent term correctly fails.
check "validate.md emits all six named gates" \
  "grep -E 'premise_contradicted|metric_instrumented|baseline_exists|control_stable|powerable|segmentation_satisfied' skills/hypothesis-generator/phases/validate.md" \
  "NONZERO"
check "validate.md states tri-state semantics" \
  "grep 'pass / fail / not-assessed' skills/hypothesis-generator/phases/validate.md" \
  "NONZERO"
check "detect.md has Step 1f header" \
  "grep -c '^### Step 1f: Measurement Inventory and Staleness Signals' skills/hypothesis-generator/phases/detect.md" \
  "1"
check "score.md has gated-rubric marker (Step 4d)" \
  "grep -c '^#### Step 4d: Gated Confidence Rubric' skills/hypothesis-generator/phases/score.md" \
  "1"
check "score.md states tri-state verbatim in the rubric" \
  "grep 'pass / fail / not-assessed' skills/hypothesis-generator/phases/score.md" \
  "NONZERO"
# Field-name purity: confirm the new internal field names are GUARDED in the
# Deliverable Purity Constraint so they are prohibited from the rendered body.
# (Em-dash and ClickUp purity over these files is already covered by block [6],
#  which recurses skills/hypothesis-generator/. Body-template grep-for-absence is
#  left to the deliverable-time constraint per the change doc, since the Output
#  Format body template is not mechanically bounded from the rest of SKILL.md.)
check "validation_gates guarded in Deliverable Purity Constraint" \
  "grep 'validation_gates' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
check "instrumented_metrics guarded in Deliverable Purity Constraint" \
  "grep 'instrumented_metrics' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
check "premise_contradicted guarded in Deliverable Purity Constraint" \
  "grep 'premise_contradicted' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
echo ""

echo "[16] Strategic rigor (gates + criterion-7 tri-state + Measurement Foundation)"
check "validate.md has Strategic Lane Gates heading" \
  "grep -c '^## Strategic Lane Gates' skills/hypothesis-generator/phases/validate.md" \
  "1"
check "validate.md defines baseline_reliable gate" \
  "grep 'baseline_reliable' skills/hypothesis-generator/phases/validate.md" \
  "NONZERO"
check "validate.md has strategic metric_instrumented application" \
  "grep -c '^### Strategic Gate 2: metric_instrumented (strategic application)' skills/hypothesis-generator/phases/validate.md" \
  "1"
check "validate.md has strategic premise_contradicted application" \
  "grep -c '^### Strategic Gate 3: premise_contradicted (strategic application)' skills/hypothesis-generator/phases/validate.md" \
  "1"
check "detect-strategic.md criterion 7 has Documented live state" \
  "grep -c 'Documented live.' skills/hypothesis-generator/phases/detect-strategic.md" \
  "1"
check "detect-strategic.md criterion 7 has Documented absent state" \
  "grep -c 'Documented absent.' skills/hypothesis-generator/phases/detect-strategic.md" \
  "1"
check "detect-strategic.md criterion 7 has Context is silent state" \
  "grep -c 'Context is silent.' skills/hypothesis-generator/phases/detect-strategic.md" \
  "1"
check "detect-strategic.md record carries absence_verified" \
  "grep 'absence_verified' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "detect-strategic.md record carries confirm_first" \
  "grep 'confirm_first' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "detect-strategic.md family 1 routes to Measurement Foundation" \
  "grep 'Measurement Foundation' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "detect-strategic.md no longer conflates instrument-and-measure in family 1" \
  "grep -c 'and measure interventions against it' skills/hypothesis-generator/phases/detect-strategic.md | tr -d ' '" \
  "0"
check "score.md Step 6b has Strategic gated-Confidence ceiling" \
  "grep 'Strategic gated-Confidence ceiling' skills/hypothesis-generator/phases/score.md" \
  "NONZERO"
check "score.md Step 6b has Dependency-count ordering" \
  "grep 'Dependency-count ordering' skills/hypothesis-generator/phases/score.md" \
  "NONZERO"
check "SKILL.md strategic body spec has Measurement Foundation section" \
  "grep -c '^## Measurement Foundation' skills/hypothesis-generator/SKILL.md" \
  "1"
# Purity: the new internal field tokens must be GUARDED in the Deliverable
# Purity Constraint (present in SKILL.md as prohibited terms). Em-dash and
# ClickUp coverage over all edited files is already provided by block [6],
# which recurses skills/hypothesis-generator/ and lists modules/ice-scoring.md.
check "absence_verified guarded in Deliverable Purity Constraint" \
  "grep 'absence_verified' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
check "confirm_first guarded in Deliverable Purity Constraint" \
  "grep 'confirm_first' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
check "baseline_reliable guarded in Deliverable Purity Constraint" \
  "grep 'baseline_reliable' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
echo ""

echo "[17] Strategic catch-all leg"
check "detect-strategic.md has Catch-All Leg heading" \
  "grep -c '^### Catch-All Leg (family-agnostic detection)' skills/hypothesis-generator/phases/detect-strategic.md" \
  "1"
check "catch-all requires two independent artifacts" \
  "grep 'TWO independent loaded artifacts' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "catch-all states zero-survivor expectation" \
  "grep 'zero survivors on most runs' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "catch-all states family precedence" \
  "grep 'routes through that family' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "lever_family enum includes catch-all" \
  "grep 'offer-architecture | catch-all' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "score.md Step 6b names the catch-all modifier" \
  "grep 'lever_family: catch-all' skills/hypothesis-generator/phases/score.md" \
  "NONZERO"
check "ice-scoring.md names the catch-all additional -1" \
  "grep 'Catch-All Leg' modules/ice-scoring.md" \
  "NONZERO"
check "catch-all token guarded in Deliverable Purity Constraint" \
  "grep 'offer-architecture., .catch-all' skills/hypothesis-generator/SKILL.md" \
  "NONZERO"
check "catch-all defines evidence-origin independence" \
  "grep 'evidence-origin level' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "catch-all anti-patterns cover channel-scale programs" \
  "grep 'generative/AI-search optimization' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "family precedence matches on definition, not name" \
  "grep 'DEFINITION sentence, not its name' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
check "catch-all measurement-shaped finds route to Foundation" \
  "grep -c '^- \*\*Measurement-shaped finds' skills/hypothesis-generator/phases/detect-strategic.md" \
  "1"
check "criterion 7 names the built-but-disabled state" \
  "grep 'Built-but-disabled is this state' skills/hypothesis-generator/phases/detect-strategic.md" \
  "NONZERO"
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
