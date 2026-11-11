---
schema: experiment-history
schema_version: "1.2"
client: "acme"
experiment_count: 2
---
# Acme Experiment History

Synthetic fixture for a fictional company.

## Experiment Log

### EXP-001: ACME-101 - Pricing Hero Claim
- **Status:** completed
- **Page:** /pricing
- **Treatment Category:** messaging
- **Launch Date:** 2026-05-04
- **End Date:** 2026-07-27
- **Duration:** 84 days
- **Sample Size:** 16,800 unique visitors / Control: 8400 / V1: 8400
- **Outcome:** win
- **Outcome Source:** analytics API
- **Key Metrics (from analytics):**
  - Scoping calls booked (primary): Control 1.90% (160/8400) vs V1 2.40% (202/8400), lift +26.3%, p=0.03, SIG [analytics]
- **Learning:** A specific outcome claim beat the method-led hero. Buyers read the outcome as the reason to book. The next test carries the outcome claim to the solutions page.
- **Next Steps:** Roll the outcome claim out to /solutions.

### EXP-002: ACME-102 - Demo Form Length
- **Status:** completed
- **Page:** /demo
- **Treatment Category:** form-optimization
- **Duration:** 56 days
- **Sample Size:** 1,900 unique visitors
- **Outcome:** inconclusive
- **Outcome Source:** analytics API
- **Key Metrics (from analytics):**
  - Scoping calls booked (primary): Control 2.0% (19/950) vs V1 2.3% (22/950), lift +15.8%, p=0.62 [analytics]
- **Learning:** Removing two fields did not move booked calls at this sample. The page may need a longer pre/post read.

## Cross-Experiment Patterns

Outcome-led copy has won once; form length has not moved bookings.

## Baseline Anchors

/pricing 2.0% booked-call rate; /demo 2.0%.

## Discovered Mechanisms

Outcome specificity drives booking on evaluation pages.

## Coverage Gaps

No test has touched the resources pages or the post-booking flow.
