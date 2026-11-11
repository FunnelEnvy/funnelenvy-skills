# Acme Fixture: Planted Opportunities

The opportunities planted in this synthetic scope, for the recall count in the fixture measurement. One row per planted passage. Source paths are relative to this directory. Classes P1 to P8 are the eight benchmark classes; P9 to P12 cover one tactical lens each.

| ID | Class | Source file | Planted passage |
|---|---|---|---|
| P1 | Lifecycle and nurture | `context/audience-messaging.md` | Prospects who download a report and do not book a call hear nothing further from Acme; there is no nurture sequence after a download. |
| P2 | Post-booking conversion (kept rate) | `context/performance-profile.md` | Of booked scoping calls, only 54% are kept; the rest no-show, and no reminder is sent between booking and the call. |
| P3 | Sales handoff and routing | `context/performance-profile.md` | Demo requests routed to the shared sales inbox wait 2.5 business days on median before first contact. |
| P4 | Lead classification | `context/performance-profile.md` | The contact form mixes support requests and sales inquiries into one contact_form_submit event, so sales and support submits cannot be told apart. |
| P5 | Partner and referral channel | `context/company-identity.md` | Referrals from the three implementation partners close at twice the rate of web leads, yet no partner has a referral page or a tracked referral link. |
| P6 | Segments from closed-won revenue | `context/company-identity.md` | Closed-won revenue last year came 58% from mid-market logistics firms, a segment none of the research personas describes. |
| P7 | Per-asset tuning on download pages | `context/performance-profile.md` | /resources/benchmark-report converts downloads at 9% while the other three asset pages convert at about 1%. |
| P8 | Pricing and engagement-model transparency | `context/audience-messaging.md` | "We can't tell what an engagement costs" is the most common objection sales hears on first calls. |
| P9 | Surface lens | `context/positioning-scorecard.md` | Clarity: the pricing page hero names the method, not the outcome a buyer gets. |
| P10 | Persona-and-journey lens | `context/audience-messaging.md` | Operations Directors land on /solutions from search and leave without visiting /pricing; the solutions page never routes them to the scoping call. |
| P11 | History lens | `deliverables/experiments/acme-101-pricing-hero-claim/insight.md` | I believe the outcome claim will lift booked calls on /solutions |
| P12 | Competitive-and-proof lens | `context/competitive-landscape.md` | No competitor publishes named customer outcome data; a named outcome on the evaluation pages would be unclaimed ground. |

## Expected Sizing

At the posture (90% two-sided, 80% power, 20% relative MDE, 26-week A/B window, 100 conversions per variant):

| Page | Sessions/mo | Rate | Read model |
|---|---|---|---|
| /pricing | 6,000 | 2.0% | A/B, about 21.6 weeks |
| /solutions | 3,000 | 2.0% | Directional, achievable effect about 25.8% |
| /demo | 1,000 | 2.0% | Pre/post, about 61 conversions per variant over the window |

## Expected Readiness Signal

`context/engagement-constraints.md` withholds sign-off on showing price ranges, so a P8 row should land as needing a client decision.
