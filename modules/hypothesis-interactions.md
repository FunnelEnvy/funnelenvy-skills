# Hypothesis Interaction Model

Version: 2.0.0
Last updated: 2026-11-11

This module defines how candidates on the same page interact. The interaction type decides whether elements belong on one card, or whether two rows run in a set order. It feeds the `Sequencing` method section and the write-up's `**Bundled elements:**` line. It never changes a row's score: a bundle is scored on its own.

## Interaction Types

- **Multiplicative (AND-gate):** both problems must co-occur to produce the failure. Fixing one alone yields little while the other still suppresses conversion. Bundle or sequence with a stated dependency.
- **Additive (OR-gate):** independent problems, each costing conversion on its own. Order by rank, with no dependency.

## Interaction Matrix

Default type when two categories target the same page. Categories are those in `modules/experiment-patterns.md`.

| Category A | Category B | Type | Implication |
|---|---|---|---|
| Headline/Messaging | Page Structure/Layout | Multiplicative | Bundle when both target the first screen; otherwise messaging first |
| Headline/Messaging | Form Optimization | Additive | No dependency |
| Headline/Messaging | Social Proof | Multiplicative | Messaging first (set the claim), then proof (support it) |
| Headline/Messaging | Trust/Credibility | Additive | No dependency |
| Headline/Messaging | Pricing | Additive | Multiplicative when the messaging involves price anchoring or value framing |
| Headline/Messaging | Navigation/UX Flow | Additive | Multiplicative for paid landing match (NX-04): message match and navigation reduction compound |
| Page Structure/Layout | Form Optimization | Additive | No dependency |
| Page Structure/Layout | Trust/Credibility | Multiplicative | Bundle in the same section; otherwise structure first |
| Form Optimization | Trust/Credibility | Multiplicative | Bundle form context reinforcement (FO-03) with trust work on the same form; otherwise trust first |
| Social Proof | Trust/Credibility | Additive | No dependency |
| Content/Resource | Headline/Messaging | Additive | No dependency |
| Personalization | Any | Multiplicative | Every other test on the page resolves first; personalization runs last there |
| Element Engagement | Headline/Messaging | Multiplicative when the element is a CTA | Messaging first on the same page; independent across pages |
| Element Engagement | Page Structure/Layout | Additive | Multiplicative for drop-off (EE-02) plus first-screen reset (PS-01) when the element sits above the fold |

## Empirical Interaction Effects

These pattern-level effects override the matrix when the specific pair co-occurs. Each yields an annotation on the affected rows and, where stated, a sequencing dependency.

- **EIE-01, login value x login prominence (multiplicative):** Login prominence (NX-07) lifts revenue only when the logged-in experience has value (saved payment, faster checkout, a useful dashboard). Low account value: annotate the counter-evidence and sequence an account-value improvement first. Seen: an apparel retailer gained 4.1% orders; a site whose account held only order history saw nothing.
- **EIE-02, funnel position x messaging type (polarity flip):** Urgency and guarantee messaging helps on checkout, booking and pricing pages (+4% to +14%) and hurts on homepages and browse pages (-8% to -11%). Social proof is neutral to positive on both. Tag such cards with funnel position and apply CTR-08.
- **EIE-03, ad parity x urgency x hero reduction (synergistic):** On a paid landing page, ad-creative match, an urgency element and a smaller hero can lift more together than apart. Flag as a bundling candidate when all three target the page. Caution: one data point (+45% to +65% subscriptions), and a loss will not say which element failed. Consider NX-04 alone first.
- **EIE-04, UI color x device (sign flip):** Color or state styling of interactive elements can win on mobile and lose on desktop. Pre-register a device split, or run device-targeted variants. Opposite signs are two findings, not an inconclusive test. Seen: brand orange on a desktop donation page cost 40% of donations.
- **EIE-05, carousel item count x prominence (negative compound):** More items and more prominence together reversed a prior carousel win. Do not bundle a drop-off restructure (EE-02) with a prominence change; sequence them, holding item count equal or lower.
- **EIE-06, form field count x audience trust (magnitude):** Field reduction (FO-01) matters most to new, low-trust visitors. New visitors over 60% of the form page: Impact +1. Returning over 60%: Impact -1. A form for existing customers or referred leads: Impact 3 at most. Seen: an 8-to-6 field cut gave +15.31% for new visitors and +2.42% for returning. CTR-01 can apply at the same time.
- **EIE-07, content widget x intent redistribution:** A conversion widget on a content page (CR-04) shifts behavior from reading to converting. Read on the conversion action, track content engagement as secondary, and count a conversion gain as a win even when content clicks fall.

## Same-Page Analysis

1. Look up the category pair in the matrix.
2. Apply any empirical effect for the specific pair; it takes precedence.
3. Check the exception in the Implication column.
4. Rule:
   - *Multiplicative, same section:* the elements serve one idea, so they belong on one card and one write-up. The write-up names them under `**Bundled elements:**`, with what the test will not isolate.
   - *Multiplicative, different sections:* separate rows with a stated dependency in `Sequencing`: "[A] runs before [B] because [rationale]. If [A] wins, [B]'s expected effect grows. If [A] loses, revisit [B]'s mechanism."
   - *Additive:* order by rank. Mention it only when running both at once on the page would confound the read.

**Cross-surface bundling rule.** Bundle elements that serve one idea on the same page or section. Across different surfaces, bundle only if a single failure mode can be named for a combined loss. If a combined loss would list three or more independent things that could have failed on different surfaces, sequence the experiments instead. A bundle whose loss analysis cannot name one failure mode is several experiments under one name.

## Cross-Page Rules

Rows on different pages are independent by default. Two exceptions go into `Sequencing` as soft notes:

- The same messaging strategy on two pages: the first result informs whether the strategy applies to the second.
- One row creates content another consumes (a comparison page feeding a secondary offer).
