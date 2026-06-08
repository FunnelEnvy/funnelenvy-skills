# Procurement Pattern Library (archetype: procurement)

Version: 1.0.0
Last updated: 2026-06-08
Pattern count: 6
Categories: 4 (Headline/Messaging, Navigation/UX, Content/Resource, Page Structure/Layout)

Patterns for sign-in-walled, configure-and-quote / e-procurement stores. Loaded by the archetype resolver (SKILL.md Phase 1) when `category.primary` resolves to "procurement". Supplements the base library; does not replace it.

Each pattern follows the Pattern Schema defined in `experiment-patterns.md`. Patterns are listed in PR-NN order because their sequencing notes reference one another; the per-pattern `Category` field records each pattern's base-library category.

---

### PR-01: Authenticated Gate Value Recovery

**Category:** Headline/Messaging
**Applies when:**
- Store is sign-in-walled (no public catalog or pricing)
- The gate / sign-in / create-account page is a top entry surface by volume
- Gate copy uses generic category or capability language interchangeable with competitor gates
- Strategy-context lists capability differentiators not surfaced on the gate

**Typical test:** Replace gate headline, value pillars, and CTA together with differentiated, capability-specific messaging adapted from the store's strongest verified differentiator.

**Causal mechanism:** The gate is the only public surface and the highest-attention moment for prospective and evaluating buyers. Generic capability copy gives no evaluation handle and no reason to invest in account setup. Specific capability claims reduce evaluation ambiguity and let the buyer self-qualify.

**ICE baseline:** Impact 4 | Confidence 3 | Ease 5
**Modifiers:**
- Confidence +1 if the gate exceeds 5,000 entries/mo AND a variant-instrumented proxy (CTA click-through) is available (proxy-readable at volume; makes the hypothesis Quick-Win-eligible)
- Impact +1 if the gate absorbs >50% of store entry traffic (funnel-wide effect)
- Confidence -1 if exact current gate copy is not in context
- Ease -1 if the gate template was missed in tag migration (verify injection coverage first)

**Common mistakes:**
- Testing a differentiated headline while leaving generic value pillars (tests one line in a hostile context; a loss is uninterpretable)
- Assuming gate arrivals are all prospects when most may be credentialed users heading to the form (read on the create-account segment via CTA instrumentation)

**Sequencing notes:** Run after or alongside PR-02 on the same surface; serialize, do not run concurrently on the same page.

---

### PR-02: Gate Route Disambiguation

**Category:** Navigation/UX
**Applies when:**
- The sign-in gate bounces a large share of entries
- The store deflects wrong-audience accounts (consumer, partner, employee) only via post-login error handling
- No pre-login routing signal exists

**Typical test:** Inject a pre-login account-type router above or beside the sign-in form with destination links, each click instrumented.

**Causal mechanism:** A meaningful share of gate bounce is wrong-audience arrivals with no path forward who leave silently. Pre-login disambiguation converts silent exits into correct-store handoffs and cleans the funnel signal for every later experiment.

**ICE baseline:** Impact 4 | Confidence 3 | Ease 4
**Modifiers:**
- Confidence +1 if router interaction is variant-instrumented on a high-traffic gate (proxy-readable; Quick-Win-eligible)
- Impact +1 if the gate absorbs >50% of entry traffic (top-of-funnel plus measurement-hygiene payoff)
- Confidence +1 if the store's own error strings already encode the routes (verified routing logic)
- Ease -1 if injection on the unauthenticated surface is unverified

**Common mistakes:**
- Routing consumer-intent visitors off-store and reading the traffic reduction as a decline (guardrail on sign-in completions, not raw traffic)
- Attributing all bounce to misrouting when credentialed-user friction or SSO patterns may dominate (near-zero router interaction is itself the answer, delivered cheaply)

**Sequencing notes:** Run first on the gate surface; its result recalibrates the addressable audience for PR-01.

---

### PR-03: Procurement Model Explanation Layer

**Category:** Content/Resource
**Applies when:**
- The store uses undefined internal procurement vocabulary (e.g., a "Standards" buy-list never defined)
- The quote-vs-order distinction and role model are unexplained
- Onboarding for new or expansion buyers is bare

**Typical test:** A bundled in-context explanation layer (one-line definitions on the internal-vocabulary surfaces, a quote-vs-order explainer, a surfaced role description) shipped as one variant because they test one idea: the store explains its own model.

**Causal mechanism:** Undefined internal vocabulary imposes a comprehension cost on every visit and sustains the rep-relationship habit. Explaining the model in context reduces hesitation at the surfaces where buying-to-standard and quoting begin. Gated competitors under-explain equally, so clarity is unclaimed territory.

**ICE baseline:** Impact 4 | Confidence 3 | Ease 4
**Modifiers:**
- Confidence +1 if the opacity is verified verbatim in the store (exact undefined terms quotable)
- Confidence -1 if no buyer testimony exists to calibrate the comprehension-to-quote-volume link (structure-inferred)
- Impact +1 if the explainer surfaces sit on the highest-traffic authenticated pages
- Ease -1 if injections span three or more surfaces

**Common mistakes:**
- Cluttering terse procedural surfaces that expert buyers value (keep injections to one line; match the existing register)
- Bundling explanations across three or more surfaces that test distinct comprehension ideas (if the bundle spans 3+ surfaces and a loss cannot name a single failure mode, sequence the surfaces instead, per the hypothesis-interactions module: different sections or pages are sequenced, not bundled)

**Sequencing notes:** Independent of the public-gate tests; inherit winning message direction from PR-01 where they overlap.

---

### PR-04: Decision Data at the Commit Surface

**Category:** Page Structure/Layout
**Applies when:**
- A configure-and-quote flow exists with high abandonment
- Decision-critical facts (real price, ship estimate, component lifecycle, support state) live inside the configurator, one level below where the buyer commits
- The PDP and cart show none of them

**Typical test:** Surface a decision-facts block (ship window, lifecycle status, support summary) on PDPs for configurable models and mirror it on cart lines.

**Causal mechanism:** Committing a large order without visible ship, lifecycle, or support status is the anxiety the store's own structure creates. The buyer's question "can I see the facts before I commit?" is answered one level too deep. Surfacing decision data where the decision is framed reduces deferral and abandonment.

**ICE baseline:** Impact 4 | Confidence 3 | Ease 2
**Modifiers:**
- Confidence +1 if a behavioral-friction signal confirms the mechanism (e.g., dead clicks on non-interactive decision data inside the configurator)
- Impact +1 if the configurator funnel is the largest sized non-measurement opportunity in the performance profile
- Ease -2 if sourcing configurator-resident data onto PDP and cart requires integration work
- Confidence -1 if completion's sensitivity to earlier data exposure is untested

**Common mistakes:**
- Reading configurator abandonment as an information gap when it may be exploration behavior (a flat result reframes abandonment as research sessions; redirect to quote-flow capacity)
- Ignoring QA scope on high-risk component-display surfaces and punchout integrations

**Sequencing notes:** Heaviest build; scope integration feasibility while lighter tests run. Sequence behind any live precursor (e.g., a configurator-summary layout change) whose readout is an input to this experiment's go/no-go.

---

### PR-05: Commit-Surface Default-State Prompt

**Category:** Page Structure/Layout
**Applies when:**
- A high-margin attach (support, services, financing) defaults to "None" or off, one level below the commit surface
- No nudge surfaces anywhere in the flow

**Typical test:** A conditional one-line prompt at the commit surface when no line carries the attach, instrumented for display and click.

**Causal mechanism:** Defaults persist. A buyer who never actively chose "no support" rarely revisits the choice. Surfacing the consequence of the default at the commit surface converts a silent default into an active decision.

**ICE baseline:** Impact 2 | Confidence 3 | Ease 4
**Modifiers:**
- Impact +1 if the attach is high-margin and the client has already prioritized surfacing it elsewhere (internal alignment signal)
- Confidence -1 if no attach-rate baseline exists
- Ease +1 if the prompt is conditional copy injection with instrumentation
- Impact -1 if the commit surface is low-traffic

**Common mistakes:**
- Scoring Impact high on modest-traffic commit surfaces (the payoff is per-order economics, not funnel volume)
- Assuming attach decisions are in-store when they may live in procurement policy (a loss keeps future effort off attach nudges)

**Sequencing notes:** Independent; lower strategic learning than the comprehension and decision-data tests, so sequence after them.

---

### PR-06: Rep-Channel Self-Service Bridge

**Category:** Navigation/UX
**Applies when:**
- Rep-created offline quotes or rep-channel artifacts appear in the self-service UI as dead-ends (detail links redirect away)
- The rep-relationship habit is a dominant force keeping credentialed buyers off self-service

**Typical test:** On rep-created rows, replace the silent dead-end with an explainer plus an action ("Build a version of this yourself") bridging into the catalog or configurator, instrumented for exposure and click.

**Causal mechanism:** The rep habit persists partly because the store treats rep artifacts as dead-ends. The moment a buyer comes looking for a rep-created quote is the moment the store offers nothing. An in-store action at that moment of intent interrupts the habit loop and converts rep-led demand into a self-service trial.

**ICE baseline:** Impact 3 | Confidence 2 | Ease 4
**Modifiers:**
- Confidence +1 if the dead-end is verified in the store
- Confidence -1 if whether buyers want to rebuild a rep's quote is untested with no buyer testimony
- Impact +1 if rep-channel leakage is confirmed as the bigger self-service leak
- Ease -1 if conditional row-level logic is non-trivial

**Common mistakes:**
- Treating thin rep-quote-row traffic as a volume play (it is a habit-conversion bet: high strategic value per conversion, low volume)
- Routing all rep demand to self-service when rep territory may stay rep territory (grow self-service from new demand instead)

**Sequencing notes:** Thin traffic; sequence by strategic learning; runs before lower-learning per-order tests.
