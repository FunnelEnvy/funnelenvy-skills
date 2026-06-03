---
fe-managed: true
name: aa-audit-performance-profile-schema-conformance
description: >
  Make aa-audit's KB-native silver-performance-analysis output conform to the documented
  performance-profile schema contract: emit schema_version and the shared GA4-shape frontmatter
  (top_pages et al.) so downstream consumers (hypothesis-generator detect.md performance
  triggers) fire identically regardless of which audit skill produced the profile.
governed_by: change-management/change-document
status: Backlog
resource_name: aa-audit
resource_version: "TBD"
impact: 4
confidence: 4
ease: 4
initiative: cro-kb-path-b
version: "0.1.0"
created: 2026-06-03
updated: 2026-06-03
---
# AA-Audit Performance-Profile Schema Conformance

## Background

The first KB-native silver-performance-analysis artifact (piloted 2026-06-03) was hand-written from an aa-audit run and diverges from aa-audit's own documented output contract: it carries no `schema_version` field and uses an AA-specific body shape instead of the shared GA4-shape frontmatter (`top_pages` et al.). aa-audit's SKILL.md documents `schema_version: "2.0"` and claims "the same schema as ga4-audit output," so the live artifact is a data/conformance defect, not just a consumer-tolerance problem. [hypothesis-generator's detect.md](../../skills/hypothesis-generator/phases/detect.md) Step 1c performance triggers key off the GA4-shaped profile; non-conformant profiles silently reduce or mis-fire performance-driven coverage. The consumer side gains a content-equivalence tolerance rule via [chg_2026-06-03_hypothesis-generator-kb-native](../6-qa/chg_2026-06-03_hypothesis-generator-kb-native.md); this doc fixes the producer.

## Current State

- aa-audit SKILL.md documents `schema_version: "2.0"` output; ga4-audit emits `"2.2"` (version skew tracked in [chg_2026-06-03_audit-skills-kb-native-writes](chg_2026-06-03_audit-skills-kb-native-writes.md)).
- The live piloted silver-performance-analysis artifact has neither `schema_version` nor the shared `top_pages` shape.
- aa-audit has no KB-native write path yet; the artifact was manually authored during the pilot.

## Approach

When aa-audit gains its KB-native write path (per audit-skills-kb-native-writes), the emitted silver-performance-analysis frontmatter must include `schema_version` and the GA4-shape structured fields the documented contract specifies. Regenerate or migrate the piloted artifact to conformance. Exact field set resolves against the cross-skill schema contract owned by audit-skills-kb-native-writes.

## Requirements

Stub — filled during Design.

## Validation

Stub — filled during Design. Must include an aa-audit KB-native artifact carrying `schema_version` and GA4-shape fields that hypothesis-generator's detect.md triggers consume without the content-equivalence fallback.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document — surfaced by change-capture at the hypothesis-generator-kb-native Backlog → Discovery transition. |
