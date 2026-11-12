---
experiment_id: ACME-101
---
# ACME-101: Experiment Insight

Synthetic fixture for a fictional company.

```yaml
experiment_id: ACME-101
design_type: ab_test
result_classification: "Type 1: Clear Winner"
blockers:
  - description: "Confirm the outcome hero is still live on /pricing before any follow-on."
    owner: "joint"
next_experiments:
  - type: rollout
    hypothesis: >-
      I believe the outcome claim will lift booked calls on /solutions
      because the mechanism does not depend on the page.
    surfaces: ["/solutions"]
    priority: recommended_lead
    if_true: "The outcome claim is a sitewide lever."
    if_false: "The pricing win was page-specific."
  - type: new_hypothesis
    hypothesis: "I believe a named customer outcome beside the pricing CTA will lift booked calls."
    surfaces: ["/pricing"]
    priority: high
    if_true: "Proof near the CTA matters as much as the claim."
    if_false: "The claim alone carried the win."
  - type: iteration
    hypothesis: "I believe a sharper outcome number in the hero will extend the win."
    surfaces: ["/pricing"]
    priority: medium
  - type: follow_up
    hypothesis: "A footer variant of the claim."
    surfaces: ["/"]
    priority: low
```
