# Changelog

## [Unreleased]

### Added
- Dual-mode I/O (KB mode): reads the scope's silver CRO artifacts from a bound knowledge base instead of .claude/context/ and writes a typed gold-experiment-roadmap artifact; --scope and --no-kb flags; mode resolution with loud legacy fallback; gold frontmatter contract with gold-to-silver depends_on; supersede-in-place re-runs; post-write validation gate; Profile Schema Equivalence rule in detect.md Step 1c (content-equivalence trigger evaluation for performance profiles lacking schema_version); legacy .claude/context/ behavior unchanged (chg_2026-06-03_hypothesis-generator-kb-native)
