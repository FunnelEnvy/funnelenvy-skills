---
schema: performance-profile
schema_version: "2.1"
generated_by: aa-audit
last_updated: 2026-11-11
last_updated_by: aa-audit
confidence: 4
company: "Acme"
report_suite: "acme-prod"
date_range: "2026-05-01 to 2026-10-31"
days: 184

total_sessions: 84000
total_users: 61000
device_mobile_pct: 31

top_pages:
  - path: "/pricing"
    sessions: 36000
    bounce_rate: 48.0
    pages_per_session: 2.2
    avg_engagement_sec: 71
    failure_mode: "message_mismatch"
  - path: "/solutions"
    sessions: 18000
    bounce_rate: 62.0
    pages_per_session: 1.4
    avg_engagement_sec: 54
    failure_mode: "dead_end"
  - path: "/demo"
    sessions: 6000
    bounce_rate: 35.0
    pages_per_session: 1.8
    avg_engagement_sec: 88
    failure_mode: null
  - path: "/resources/benchmark-report"
    sessions: 4200
    bounce_rate: 41.0
    pages_per_session: 1.6
    avg_engagement_sec: 66
    failure_mode: null
  - path: "/resources/peak-season-guide"
    sessions: 3900
    bounce_rate: 70.0
    pages_per_session: 1.2
    avg_engagement_sec: 31
    failure_mode: "low_engagement"

conversion_events:
  - name: "scoping_call_booked"
    count: 1260
    classification: conversion
  - name: "contact_form_submit"
    count: 410
    classification: conversion
  - name: "report_download"
    count: 690
    classification: micro_conversion
primary_conversion_event: "scoping_call_booked"
primary_conversion_rate: 1.5

top_channels:
  - channel: "Organic Search"
    sessions: 39000
    bounce_rate: 51.0
  - channel: "Paid Search"
    sessions: 21000
    bounce_rate: 58.0
  - channel: "Direct"
    sessions: 14000
    bounce_rate: 40.0

source_page_mismatches: []

new_vs_returning:
  new_sessions_pct: 71
  new_conversion_rate: 0.9
  returning_conversion_rate: 2.9
  returning_to_new_ratio: 3.2
  signal: "normal_b2b"

page_groups:
  - group: "Resources"
    url_pattern: "/resources/*"
    monthly_sessions: 2600
    conversion_rate: 0.4
    bounce_rate: 58.0
    page_count: 4

top_opportunities:
  - page: "/pricing"
    issue: "Scoping-call rate below the site's evaluation-page benchmark"
    formula_type: "conversion_lift"
    current_metric: 2.0
    target_metric: 2.4
    monthly_sessions: 6000
    estimated_monthly_impact: "medium"
    action_category: "messaging"
    sizing_note: "Estimated using standard CRO conservatism factors (0.4x), not property-specific data"

traffic_adequacy: "adequate"
sampling_applied: false

scope_applied: false
scope_method: "none"
scope_note: null

element_instrumentation_state: "partial"
tracked_elements:
  - name: "Book a scoping call"
    count: 3100
    status: live
missing_element_classes: ["download form submit by asset"]
instrumentation_ask: "Tag report downloads with the asset name."

event_liveness:
  - event: "scoping_call_booked"
    count: 1260
    status: live
  - event: "contact_form_submit"
    count: 410
    status: live
measurement_integrity_flags: []
friction_interactions: []

element_interactions_available: true

l0_available: false
l0_confidence: null
---
# Acme: Performance Profile

Synthetic fixture for a fictional company. All figures are invented. The window is 2026-05-01 to 2026-10-31.

## Property Overview

Report suite acme-prod, whole suite, no scope applied. Six months of data.

## Page Performance

### Top Pages

| Page | Sessions/mo | Primary conversion rate (scoping call booked) |
|---|---|---|
| /pricing | 6,000 | 2.0% |
| /solutions | 3,000 | 2.0% |
| /demo | 1,000 | 2.0% |

The /pricing hero names the method rather than the outcome, and its bounce rate is 48%.

### High-Bounce Pages

/solutions at 62% and /resources/peak-season-guide at 70%.

### Page Group Performance

The four asset download pages average 0.4% conversion, but /resources/benchmark-report converts downloads at 9% while the other three asset pages convert at about 1%.

### Underperforming Pages

/solutions: a dead end with no route to the scoping call.

## Conversion Events

### Event Inventory

scoping_call_booked, contact_form_submit, report_download.

### Per-page Funnels

Of booked scoping calls, only 54% are kept; the rest no-show, and no reminder is sent between booking and the call.

### Missing Tracking Gaps

The contact form mixes support requests and sales inquiries into one contact_form_submit event, so sales and support submits cannot be told apart.

Demo requests routed to the shared sales inbox wait 2.5 business days on median before first contact.

## Channel Performance

### By Channel

Organic Search leads; Paid Search bounces highest.

### Top Sources

google, bing, direct.

## Device & User Segment Performance

Mobile is 31% of sessions with a 0.6 point lower conversion rate. Returning visitors convert at 3.2 times the new-visitor rate.

## Landing Page Performance

/pricing and /solutions are the top entry pages.

## Opportunity Sizing

/pricing: medium monthly impact from a conversion lift on 6,000 sessions a month.

## Element-Level Interactions

State: partial. Report downloads are not tagged by asset name. Ask: tag report downloads with the asset name.

## Measurement Integrity

No dead bindings and no zero-crossings over the window.

## Key Metrics Summary

- **Strengths:** steady organic traffic
- **Weaknesses:** /solutions dead end, kept-call rate
- **Experiment opportunities:** /pricing outcome hero, asset page tuning
- **Data gaps:** download events lack the asset name
