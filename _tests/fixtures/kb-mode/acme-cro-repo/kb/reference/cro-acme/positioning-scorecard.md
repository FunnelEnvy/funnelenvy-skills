---
fe-managed: true
name: positioning-scorecard
title: Acme Positioning Scorecard
description: >
  Positioning health check for Acme: categorical ratings per dimension, gaps and priority
  recommendations. Test fixture input.
kb_layer: silver
governed_by: kb-type-acme-cro/silver-positioning-scorecard
managed_by: kb-type-acme-cro
scope: acme
confidence: 4
data_provenance: public
generated_by: positioning-framework
depends_on:
  - reference/cro-acme/competitive-analysis.md
  - reference/cro-acme/audience-analysis.md
tags:
  - positioning-scorecard
  - health-check
  - recommendations
version: "1.0.0"
created: 2026-10-01
updated: 2026-10-01
---
# Acme Positioning Scorecard

## Positioning Health Check

| Dimension | Rating | Key Finding |
|---|---|---|
| Clarity | Strong | The homepage states who Acme serves and what it does in one line. |
| Differentiation | Needs Work | "Fewer stockouts" is also claimed by both major competitors. |
| Proof | Needs Work | One strong named case study (P1); the rest is unaudited or unnamed. |
| Specificity | Strong | "Live in 14 days" is concrete and backed by P2. |
| Consistency | Needs Work | Pricing and product pages call the buyer "planner"; the homepage says "buyer". |
| Category Fit | Missing | Acme's category name does not match the terms buyers search. |

**Overall: 2 Strong, 3 Needs Work, 1 Missing**

## Gap Analysis

- The strongest claim, speed to value, sits below the fold on the homepage.
- The stockout claim is crowded, and only P1 proves it.
- The category name "demand planning for distributors" misses the search term "inventory forecasting software".

## Priority Recommendations

1. Lead the homepage hero with "live in 14 days" and P2.
2. Put P1 on the pricing page beside the per-warehouse price.
3. Retitle the category page around "inventory forecasting software for distributors".
