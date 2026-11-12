#!/bin/bash
# Validation script for the hypothesis-generator skill.
# Run from repo root: bash scripts/validate-hypothesis-generator.sh
#
# Every check falls in one of six classes:
#   [1] Files              the skill, its phase files and its scripts exist
#   [2] Kept hard rules    each hard rule's anchor text sits in its home; Decision Posture holds every row the script reads
#   [3] Output shape       both output formats name their sections and required write-up labels
#   [4] Removed rules      searches for deleted 1.x rule text print nothing
#   [5] Fixture            every source file the synthetic fixture's planted list names exists
#   [6] Prohibited content content hygiene over the skill and its modules
# Behavior is tested by _tests/ (consolidate_backlog.py, history_backlog.py); this script checks text.
# Limit: the hard-rule checks confirm each rule's anchor text is present in its home file.
# They do not read meaning, so a reworded rule body can pass. The fixture run and the
# red team (cro-roadmap-red-team) are the checks that read meaning.

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

# Print the body of the first heading in file $1 matching regex $2, up to the next heading at
# the same or a higher level. Lines inside ``` fences are never read as headings, so a section
# that holds a fenced markdown template keeps the template's own headings as content.
sect() {
  awk -v pat="$2" '
    function lvl(s) { match(s, /^#+/); return RLENGTH }
    /^```/ { fence = !fence }
    !on && !fence && /^#/ && $0 ~ pat { on = 1; L = lvl($0); next }
    on && !fence && /^#/ && lvl($0) <= L { exit }
    on { print }' "$1"
}

HG=skills/hypothesis-generator
SKILL=$HG/SKILL.md
PH=$HG/phases
# The hypothesis-generator file set: the skill, its phase files and the five modules only it loads.
HG_SET="$SKILL $PH modules/ice-scoring.md modules/contrarian-triggers.md modules/experiment-patterns.md modules/hypothesis-interactions.md modules/patterns-procurement.md"
FIX=_tests/fixtures/hypothesis-generator/synthetic-scope

echo "=== Hypothesis Generator: Validation ==="
echo ""

echo "[1] Files"
check_exists "SKILL.md" "$SKILL"
for f in detect.md detect-strategic.md validate.md score.md construct.md; do
  check_exists "phases/$f" "$PH/$f"
done
check "phases/ holds exactly the five phase files" \
  "ls $PH/*.md | wc -l | tr -d ' '" \
  "5"
check_exists "scripts/consolidate_backlog.py" "$HG/scripts/consolidate_backlog.py"
check_exists "scripts/history_backlog.py" "$HG/scripts/history_backlog.py"
check_exists "modules/experiment-patterns.md (lens prompt library)" "modules/experiment-patterns.md"
check_exists "modules/ice-scoring.md" "modules/ice-scoring.md"
echo ""

echo "[2] Kept hard rules"
check "Documented-live lever: no build card (detect-strategic.md Gap Status)" \
  "sect $PH/detect-strategic.md '^## Gap Status' | grep 'Documented live' | grep 'Hard rule: no build card'" \
  "NONZERO"
check "Identical forms: no form-swap test (detect.md)" \
  "grep -F '**Hard rule, identical forms:**' $PH/detect.md" \
  "NONZERO"
check "Hard-rule discards go to Exclusions (detect.md Return Format)" \
  "sect $PH/detect.md '^### Return Format' | grep 'Exclusions:' | grep 'hard-rule discard'" \
  "NONZERO"
check "Never size on a refused window (Measurement-Regime Boundary)" \
  "sect $SKILL '^## Measurement-Regime Boundary' | grep -F '**Hard rule: never size on a refused window.**'" \
  "NONZERO"
check "Size only from the Decision Posture (Decision Posture)" \
  "sect $SKILL '^## Decision Posture' | grep -F '**Hard rule: size only from this table.**'" \
  "NONZERO"
check "Pre/post reads state their detectable change from the sizing object (construct.md Read Model and Read Threshold)" \
  "sect $PH/construct.md '^### Read Model and Read Threshold' | grep -F '*Pre/post with a sizing object:*' | grep -F 'mde_achievable' | grep -F 'Count read'" \
  "NONZERO"
check "History ledger blocks the write while any id is unaccounted (score.md)" \
  "sect $PH/score.md '^## Step 3: Close the History Ledger' | grep 'Hard rule' | grep 'not written while .history_unaccounted. is non-empty'" \
  "NONZERO"
check "Dropped prior write-ups block the write while any is unaccounted (score.md)" \
  "sect $PH/score.md '^## Step 4: Account for Dropped Prior Write-Ups' | grep -F '**Hard rule:** no roadmap is written while any dropped prior write-up has neither outcome'" \
  "NONZERO"
check "Standing engagement exclusions go to Exclusions (detect.md Engagement Constraints)" \
  "sect $PH/detect.md '^### Engagement Constraints' | grep -F '**Standing exclusion:**' | grep 'Exclusions:'" \
  "NONZERO"
check "History full-entry cap of 20 (Phase 1 step 5b)" \
  "sect $SKILL '^### Phase 1: ' | grep 'Full-entry cap (hard rule)' | grep 'at most 20 full record entries'" \
  "NONZERO"
check "Write-up evidence must resolve (construct.md Evidence and Scores)" \
  "sect $PH/construct.md '^### Evidence and Scores' | grep -F '**Correctness rule, evidence must resolve:**'" \
  "NONZERO"
check "Unresolved evidence returns the row to the backlog (construct.md Evidence and Scores)" \
  "sect $PH/construct.md '^### Evidence and Scores' | grep -F 'evidence did not resolve'" \
  "NONZERO"
check "Deliverable purity names no internal identifier" \
  "sect $SKILL '^## Deliverable Purity Constraint' | grep 'name no internal identifier'" \
  "NONZERO"
for row in 'Significance' 'Power' 'Multiplier M' 'Relative MDE' 'Maximum A/B read window' 'Hard gates'; do
  check "Decision Posture has the '$row' row consolidate_backlog.py reads" \
    "sect $SKILL '^## Decision Posture' | grep '^| $row'" \
    "NONZERO"
done
echo ""

echo "[3] Output shape"
OF="sect $SKILL '^## Output Format'"
SOF="sect $SKILL '^## Strategic Roadmap Output Format'"
for h in 'Ready Now' 'Needs a Design Change' 'Needs Measurement' 'Needs a Client Decision' 'Backlog' 'Exclusions' 'Method'; do
  check "Output Format names '## $h'" \
    "$OF | grep -x '## $h'" \
    "NONZERO"
done
check "Output Format carries the exact Backlog header" \
  "$OF | grep -xF '| Key | Title | Surface | Mechanism | Readiness | Read model | ICE | Evidence |'" \
  "NONZERO"
for label in 'Key' 'Page' 'Mechanism' 'What to test' 'Change type' 'Current state' 'Proposed change' \
             'Read model' 'Why this should work' 'Target metric' 'Expected effect and read threshold' \
             'Evidence' 'Scores' 'What a win proves' 'What a loss teaches'; do
  check "Output Format template carries required label '$label'" \
    "$OF | grep '^\\*\\*$label:\\*\\* '" \
    "NONZERO"
done
check "Output Format adds a Readiness line outside Ready Now" \
  "$OF | grep -F '**Readiness:**'" \
  "NONZERO"
check "Strategic Roadmap Output Format names '## Measurement Foundation'" \
  "$SOF | grep -x '## Measurement Foundation'" \
  "NONZERO"
check "Strategic Roadmap Output Format names '### Levers Reviewed'" \
  "$SOF | grep -x '### Levers Reviewed'" \
  "NONZERO"
echo ""

echo "[4] Removed rules"
check "No --max flag (skill and phase files)" \
  "grep -rn -- '--max\\b' $SKILL $PH" \
  "EMPTY"
check "No 1.x tier names" \
  "grep -rnE 'Quick[- ]Wins?|Strategic[- ]Bets?|Explorations?\\b' $HG_SET" \
  "EMPTY"
check "No self-critique or FM8" \
  "grep -rnE 'Self-critique|self-critique|Key risk|FM8' $HG_SET" \
  "EMPTY"
check "No evidence-module ceiling" \
  "grep -rnE 'evidence-\\*|evidence modules?' $HG_SET" \
  "EMPTY"
check "No route-out instruction" \
  "grep -rn 'Do not include in roadmap' $HG_SET" \
  "EMPTY"
check "No What's Not Here routing" \
  "grep -rn \"What's Not Here\" $HG_SET" \
  "EMPTY"
check "No input bars on minting" \
  "grep -rnE 'never mint|never mints|cannot mint' $HG_SET" \
  "EMPTY"
check "No Quick-Win-eligible modifiers (procurement module)" \
  "grep -n 'Quick-Win-eligible' modules/patterns-procurement.md" \
  "EMPTY"
echo ""

echo "[5] Fixture"
fixture_sources() {
  grep -E '^\| P[0-9]+ ' "$FIX/planted-opportunities.md" | awk -F'|' '{print $4}' | tr -d ' `'
}
check "planted-opportunities.md names source files" \
  "fixture_sources" \
  "NONZERO"
check "Every planted source file exists" \
  "for f in \$(fixture_sources); do [ -e \"$FIX/\$f\" ] || echo \"\$f\"; done" \
  "EMPTY"
echo ""

echo "[6] Prohibited content"
# These greps recurse skills/hypothesis-generator/ as a directory, so every phase file is
# covered without listing it. The modules are listed explicitly.
check "No ClickUp references in new files" \
  "grep -ri 'clickup\|click_up' skills/hypothesis-generator/ modules/experiment-patterns.md modules/ice-scoring.md modules/contrarian-triggers.md modules/hypothesis-interactions.md modules/patterns-procurement.md | head -1" \
  "EMPTY"
check "No em dashes in new files" \
  "grep -rP '\xe2\x80\x94' skills/hypothesis-generator/ modules/experiment-patterns.md modules/ice-scoring.md modules/contrarian-triggers.md modules/hypothesis-interactions.md modules/patterns-procurement.md | head -1" \
  "EMPTY"
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
