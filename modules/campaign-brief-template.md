# Campaign Brief Template

> **Module type:** Schema reference + template structure
> **Used by:** landing-page-generator/phases/brief.md (Phase 1 output format)
> **Scope:** Defines the structure and fields for a completed campaign brief. Everything in this template changes per campaign. Everything in modules/conversion-playbook.md stays constant.

---

## Frontmatter Schema

```yaml
---
schema: campaign-brief
schema_version: "1.0"
client: <company-name>
campaign: <campaign-slug>
service_line: <service description>
target_persona: <title and qualifier, e.g., "CFO (PE-Backed Mid-Market)">
target_keywords:
  - <keyword-1>
  - <keyword-2>
  - <keyword-3>
offer_type: <demo|consultation|content|quote>
form_strategy:
  fields: <int>
  type: <lightbox|embedded|multi-step>
  enrichment_tool: <true|false>
post_submit: <calendar|asset|thankyou>
proof_points_count: <int>
gaps:
  - <description of any unresolved IMPORTANT gaps>
depth: <standard|deep>
generated_by: "landing-page-generator/brief"
last_updated: <ISO-8601>
---
```

---

## Brief Body Structure

### Campaign Context

**Client**: [Client name, from company-identity.md]

**Service line / offer**: [From campaign seed]

**Target keywords**:
- [keyword 1]
- [keyword 2]
- [keyword 3]

**Ad copy** (paste the actual ad text if available):
```
[Ad headline, description lines, sitelink text.
If not yet written, describe the ad theme in 1-2 sentences.]
```

**Why this service line first**: [1-2 sentences. Include data if available from performance-profile.md: current CVR, bounce rate, traffic volume.]

---

### Audience

**Primary buyer persona**: [Title and qualifier]

**Buyer's situation when they search**: [Trigger event. What just happened or is about to happen?]

**What they're measured on**: [2-3 metrics their boss evaluates them against]

**Emotional state**: [e.g., "Urgent. Controller just resigned, close in 3 weeks." or "Researching. Evaluating options for next quarter."]

---

### Page Pillars (3 max)

**Pillar 1: [Name]**
- Pain: [What the buyer is experiencing]
- Fix: [How this client solves it]
- Proof: [Supporting proof point, or [GAP] if none]

**Pillar 2: [Name]**
- Pain: [What the buyer is experiencing]
- Fix: [How this client solves it]
- Proof: [Supporting proof point, or [GAP] if none]

**Pillar 3: [Name]**
- Pain: [What the buyer is experiencing]
- Fix: [How this client solves it]
- Proof: [Supporting proof point, or [GAP] if none]

---

### Headline Strategy

| Option | Approach | Headline |
|--------|----------|----------|
| A (recommended) | Pain-forward | [Lead with buyer's problem] |
| B | Keyword-forward | [Lead with primary search term] |
| C | Proof-forward | [Lead with strongest metric] |

**CTA button text**: [Exact text, e.g., "Schedule a 15-Minute Strategy Call"]

**Supporting micro-copy below CTA**: [e.g., "No commitment. No long contracts. Just a conversation with a senior advisor."]

---

### Proof Points

#### Metrics

| Metric | What It Proves | Page Placement |
|--------|---------------|----------------|
| [e.g., NPS 93] | [e.g., Client satisfaction] | [e.g., Hero + stats section] |

#### Case Studies

| Client | Outcome (with numbers) | Named/Anonymous | Page Placement |
|--------|----------------------|-----------------|----------------|
| [e.g., Atlas Technical] | [e.g., 4-week SEC filing from three-way merger] | [Named] | [Stats section] |

#### Testimonials

| Quote or Summary | Person | Title | Company | Page Placement |
|-----------------|--------|-------|---------|----------------|
| [Exact quote] | [Name] | [Title] | [Company] | [Proof section] |

#### Client Logos (max 5)

1. [Company]
2. [Company]
3. [Company]
4. [Company]
5. [Company]

---

### Objection Handling

| Buyer Question | Answer | Supporting Proof |
|---------------|--------|-----------------|
| [Framed as buyer would ask it] | [Proof-backed response] | [Metric or case study] |

---

### Client-Specific Overrides

**Form field overrides**: [e.g., "Client uses ZoomInfo. 2-field lightbox: first name + work email."]

**Post-submit flow**: [e.g., "Redirect to Calendly embed. Prospect books own slot."]

**Regulatory / compliance**: [e.g., "Required disclaimer: 'Acme Corp is not a CPA firm.' Banned terms: see Language Guidance below."]

**Language Guidance**:

| Use This | Not This |
|----------|----------|
| [approved term] | [banned term] |

---

### Context Sources Used

> For internal tracking only. Tells the Copy Agent which context files were available during brief building.

| Context File | Available | Confidence | Notes |
|-------------|-----------|------------|-------|
| company-identity.md | yes/no | 1-5 | |
| audience-messaging.md | yes/no | 1-5 | |
| competitive-landscape.md | yes/no | 1-5 | |
| positioning-scorecard.md | yes/no | 1-5 | |
| performance-profile.md | yes/no | 1-5 | |
| Rendered deliverables | yes/no | n/a | [which ones] |

---

*Campaign Brief Template v1.0 | FunnelEnvy | March 2026*
