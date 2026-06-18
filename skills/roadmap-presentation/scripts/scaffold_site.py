#!/usr/bin/env python3
"""Deterministic scaffolding for the roadmap-presentation site.

Emits every byte of chrome for a hub-and-spoke roadmap presentation site:
the shared FunnelEnvy CSS design system (IBM Plex Sans for prose, IBM Plex Mono
for the data layer), the shared JS behaviors, the hub and spoke HTML page shells, and the prev/next pager chain wired across spokes. The
agent fills the labeled content slots after this script runs.

The emission is the drift mitigation: given the same manifest, every render is
byte-identical in chrome, so a hand-edited render can never silently fall
behind its source. The script contains no client content and no judgment logic
(no curation, no copywriting): it is pure scaffolding.

CLI:
    scaffold_site.py <manifest.json> [--out <dir>]

Manifest schema (JSON):
    {
      "title": "Experiment Roadmap",          # site title (generic, no client)
      "out_dir": "/abs/path/to/site",          # output dir (or pass --out)
      "experiments": [
        {"number": 1, "title": "Experiment title", "mockup_present": false},
        ...
      ]
    }

The agent resolves source mockup directories by each experiment's stable Key
field (slugify(title) fallback for keyless roadmaps) separately; this script
keys assets only by zero-padded experiment number, so the deployed site never
depends on slug stability.
"""
import argparse
import html
import json
import os
import sys

CONTENT_SLOT = "<!-- CONTENT-SLOT -->"

# Filenames the script emits. Stable; the agent fills the *.html content slots.
STYLES_FILENAME = "styles.css"
SCRIPT_FILENAME = "site.js"
HUB_FILENAME = "index.html"


def spoke_filename(number):
    """Spoke page filename for a 1-based experiment number, zero-padded to 2."""
    return "experiment-%02d.html" % int(number)


def asset_dir_for(number):
    """In-site asset path for an experiment's mockups (number-keyed, stable)."""
    return "assets/mockups/experiment-%02d" % int(number)


# --------------------------------------------------------------------------
# Design system (CSS). FunnelEnvy "reconciliation ledger" language: IBM Plex Sans
# for prose + IBM Plex Mono for the data layer (codes, scores, dates, percentages),
# a disciplined disposition palette (blue = active, amber = gated, green = measured
# win only, gray/slate = reframed/held/superseded), run-order spine, browser-chrome
# mockup frames, lightbox, sticky scroll-spy nav. Generic, reusable, no client content.
# --------------------------------------------------------------------------
STYLES_CSS = """/* ============================================================
   FunnelEnvy strategy deliverable - "Reconciliation Ledger" template
   Type:  IBM Plex Sans (argument) + IBM Plex Mono (all data/codes)
   Color: brand blue spine + disciplined disposition states
   Theme: light. Class vocabulary preserved for hub + spoke pages.
   ============================================================ */

:root {
  /* --- Brand spine --- */
  --blue: #3B82F6;          /* WebSys / primary / links */
  --blue-700: #1d64d8;
  --blue-50: #eff5ff;
  --purple: #8B5CF6;        /* LeadSys (available for routing/form sections) */
  --pink: #EC4899;          /* DataSys (available for measurement sections) */
  --red: #DC2626;

  /* --- Ink + neutrals (cool, never warm-cream) --- */
  --dark: #1a1d1f;          /* primary text */
  --med: #4b5563;           /* secondary */
  --light: #6b7280;         /* tertiary / meta */
  --faint: #9ca3af;         /* faint */
  --bg-white: #ffffff;
  --bg-light: #f3f4f6;
  --bg-section: #fafafa;
  --line: #e8e8e5;          /* hairline */
  --line-2: #d9d9d4;        /* stronger hairline */

  /* --- Disposition states (semantic, restrained) ---
     Blue carries "active". Gray carries "absorbed/closed".
     Amber = the one caution hue (gated). Green = measured win ONLY. */
  --st-active: #2570eb;     --st-active-bg: #eff5ff;     --st-active-bd: #c7ddfd;
  --st-gated:  #b45309;     --st-gated-bg:  #fff8e7;     --st-gated-bd:  #f0d8b0;
  --st-reframed: #475569;   --st-reframed-bg: #f1f3f5;   --st-reframed-bd: #d7dde3;
  --st-closed:  #6b7280;    --st-closed-bg:  #f4f4f3;    --st-closed-bd:  #e2e2dd;
  --win: #15803d;           --win-bg: #f0fdf4;           --win-bd: #bbe7c8;

  /* --- Legacy tier names (kept so spoke pages keep rendering) --- */
  --qw: #15803d;            /* Active Experiments tier */
  --sb: #1d4ed8;            /* Reframed Initiatives tier */
  --ex: #b45309;            /* Decide / excluded */

  /* --- Callout surfaces --- */
  --callout-yellow-bg: #fff8e7;  --callout-yellow-border: #e0a93f;
  --callout-blue-bg: #eff5ff;    --callout-blue-border: var(--blue);
  --callout-red-bg: #fef2f2;     --callout-red-border: var(--red);
  --callout-green-bg: #f0fdf4;   --callout-green-border: #34d399;

  /* --- Elevation + radius --- */
  --card-shadow: none;
  --card-shadow-hover: 0 3px 14px rgba(20,24,28,0.07);
  --r-sm: 6px; --r-md: 8px; --r-lg: 12px;

  /* --- Fonts --- */
  --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
  font-family: var(--font-sans);
  color: var(--dark);
  background: var(--bg-white);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.container { max-width: 960px; margin: 0 auto; padding: 0 2rem; }
section { padding: 52px 0; }
section + section { border-top: 1px solid var(--line); }

/* === Monospace data layer (the signature) ===
   Every code, score, %, count, date, and version is mono. Prose stays sans. */
.mono { font-family: var(--font-mono); font-feature-settings: "tnum" 1; letter-spacing: -0.01em; }
.ids  { color: var(--st-active); font-size: 0.92em; }
.ids a { color: inherit; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.12s; }
.ids a:hover { border-bottom-color: currentColor; }

/* === Navigation === */
nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(255,255,255,0.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line);
  padding: 0 2rem;
  transition: box-shadow 0.2s;
}
nav.scrolled { box-shadow: 0 1px 0 var(--line), 0 6px 18px rgba(20,24,28,0.05); }
nav .nav-inner {
  max-width: 1240px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  min-height: 54px; gap: 12px; flex-wrap: wrap; padding: 6px 0;
}
nav .brand {
  font-weight: 600; font-size: 14px; letter-spacing: -0.01em;
  white-space: nowrap; color: var(--dark); text-decoration: none;
}
nav .brand .sep { color: var(--line-2); font-weight: 400; margin: 0 7px; }
nav .brand .client { color: var(--med); font-weight: 500; }
nav .nav-links { display: flex; gap: 4px; flex-wrap: wrap; }
nav .nav-links a {
  font-size: 12px; font-weight: 500; color: var(--light);
  text-decoration: none; padding: 6px 10px; border-radius: var(--r-sm);
  transition: all 0.15s;
}
nav .nav-links a:hover { background: var(--bg-light); color: var(--dark); }
nav .nav-links a.active { background: var(--dark); color: #fff; }
nav .pager { display: flex; gap: 6px; }
nav .pager a {
  font-size: 12px; text-decoration: none; color: var(--med);
  border: 1px solid var(--line-2); border-radius: var(--r-sm); padding: 5px 11px;
  transition: all 0.15s; white-space: nowrap;
}
nav .pager a:hover { background: var(--bg-light); color: var(--dark); }
nav .pager a.disabled { opacity: 0.35; pointer-events: none; }

/* === Hero === */
.hero { padding: 116px 0 52px; background: var(--bg-white); }
.hero .provenance {
  font-size: 12px; color: var(--faint); letter-spacing: 0.01em; margin-bottom: 22px;
}
.hero .provenance .sep { color: var(--line-2); }
.hero h1 {
  font-size: 37px; font-weight: 700; line-height: 1.16;
  letter-spacing: -0.025em; margin-bottom: 16px; max-width: 19ch;
}
.hero h1 .lo { color: var(--faint); font-weight: 700; }
.hero .subtitle {
  font-size: 17px; color: var(--med); line-height: 1.55;
  max-width: 680px; margin-bottom: 28px;
}

/* Spoke page hero (lighter) */
.exp-hero { padding: 108px 0 12px; }
.exp-hero .top-line { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.exp-hero h1 { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.22; }
.exp-hero h1 .n { font-family: var(--font-mono); color: var(--faint); margin-right: 6px; }
.hypothesis { font-size: 16px; line-height: 1.55; max-width: 740px; margin-top: 12px; }
.ice-inline {
  display: inline-flex; align-items: baseline; gap: 12px; flex-wrap: wrap;
  font-family: var(--font-mono); font-size: 12.5px; color: var(--faint); margin-top: 14px;
}
.ice-inline .total { font-weight: 600; color: var(--med); font-size: 13.5px; }

/* === Reconciliation proportion bar (hero signature) === */
.recon-bar {
  display: flex; height: 14px; border-radius: 7px; overflow: hidden;
  margin: 4px 0 16px; background: var(--bg-light);
}
.recon-bar .seg { height: 100%; }
.recon-bar .seg.active { background: var(--blue); }
.recon-bar .seg.gated  { background: #e0a93f; }
.recon-bar .seg.folded { background: #b4b2a9; }
.recon-legend { display: flex; gap: 26px; flex-wrap: wrap; }
.recon-legend .lg {
  display: flex; align-items: baseline; gap: 7px;
  font-size: 13.5px; color: var(--med); line-height: 1.4;
}
.recon-legend .lg .sw { width: 9px; height: 9px; border-radius: 2px; flex-shrink: 0; align-self: center; }
.recon-legend .lg .sw.active { background: var(--blue); }
.recon-legend .lg .sw.gated  { background: #e0a93f; }
.recon-legend .lg .sw.folded { background: #b4b2a9; }
.recon-legend .lg b { font-family: var(--font-mono); font-weight: 600; color: var(--dark); font-size: 14px; }

/* === Hero run-order spine (roadmap-first summary) === */
.hero-seq { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 4px 0 12px; }
.hero-seq .hs-stage { font-size: 11px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--light); }
.hero-seq .hs-stage:not(:first-child) { margin-left: 6px; }
.hero-seq .hs-chip {
  font-family: var(--font-mono); font-size: 13px; font-weight: 500; text-decoration: none;
  color: var(--st-active); background: var(--st-active-bg); border: 1px solid var(--st-active-bd);
  padding: 5px 11px; border-radius: var(--r-md); white-space: nowrap; transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.hero-seq .hs-chip:hover { background: var(--blue); color: #fff; border-color: var(--blue); }
.hero-seq .hs-chip.lead { background: var(--blue); color: #fff; border-color: var(--blue); }
.hero-seq .hs-chip.lead:hover { box-shadow: var(--card-shadow-hover); }
.hero-seq .hs-arrow { color: var(--faint); font-size: 14px; }
.hero-seq-note { font-size: 13px; color: var(--light); margin: 0; }
.hero-seq-note a { color: var(--st-active); }

/* === Typography === */
h2 {
  font-size: 25px; font-weight: 700; letter-spacing: -0.02em;
  margin-bottom: 8px; line-height: 1.25;
}
h3 {
  font-size: 17px; font-weight: 600; letter-spacing: -0.01em;
  margin-bottom: 6px; margin-top: 30px; line-height: 1.3;
}
p { margin-bottom: 14px; font-size: 15px; }
.section-lead { font-size: 15.5px; color: var(--med); margin-bottom: 24px; max-width: 760px; }
.small { font-size: 13px; color: var(--med); }
.muted { color: var(--light); }
ul, ol { margin: 8px 0 14px 20px; font-size: 15px; }
li { margin-bottom: 6px; }
li::marker { color: var(--faint); }
a { color: var(--blue); text-underline-offset: 2px; }

/* === Callouts === */
.callout {
  padding: 15px 20px; border-radius: 0 var(--r-md) var(--r-md) 0; margin: 20px 0;
  border-left: 3px solid; font-size: 14px; line-height: 1.55; background: var(--bg-section);
}
.callout-yellow { background: var(--callout-yellow-bg); border-color: var(--callout-yellow-border); }
.callout-blue { background: var(--callout-blue-bg); border-color: var(--callout-blue-border); }
.callout-red { background: var(--callout-red-bg); border-color: var(--callout-red-border); }
.callout-green { background: var(--callout-green-bg); border-color: var(--callout-green-border); }
.callout .label {
  font-family: var(--font-mono);
  font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase; margin-bottom: 5px; display: block;
}
.callout-blue .label { color: var(--blue-700); }
.callout-yellow .label { color: #b45309; }
.callout-red .label { color: var(--red); }
.callout-green .label { color: var(--win); }

/* === Disposition badges (the loud element) === */
.disp, .warn, .tier {
  font-family: var(--font-mono);
  font-size: 11px; font-weight: 600; letter-spacing: 0.02em;
  padding: 4px 11px; border-radius: var(--r-sm); white-space: nowrap;
  display: inline-block; border: 1px solid transparent;
}
.disp.run     { background: var(--st-active-bg);   color: var(--st-active);   border-color: var(--st-active-bd); }
.disp.gated   { background: var(--st-gated-bg);    color: var(--st-gated);    border-color: var(--st-gated-bd); }
.disp.reframed{ background: var(--st-reframed-bg); color: var(--st-reframed); border-color: var(--st-reframed-bd); }
.disp.held    { background: var(--st-closed-bg);   color: var(--st-closed);   border-color: var(--st-closed-bd); }
.warn         { background: var(--st-closed-bg);   color: var(--st-closed);   border-color: var(--st-closed-bd); }
.tier.qw { background: var(--win-bg);        color: var(--qw); border-color: var(--win-bd); }
.tier.sb { background: var(--st-active-bg);  color: var(--sb); border-color: var(--st-active-bd); }
.tier.ex { background: var(--st-gated-bg);   color: var(--ex); border-color: var(--st-gated-bd); }

.run-order {
  display: inline-flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: var(--r-sm); background: var(--dark); color: #fff;
  font-family: var(--font-mono); font-size: 12px; font-weight: 600; margin-right: 9px; flex-shrink: 0;
}

/* === Verdict block (spoke) === */
.verdict {
  border: 1px solid var(--line); border-left: 3px solid var(--blue); background: var(--bg-section);
  border-radius: 0 var(--r-md) var(--r-md) 0; padding: 14px 18px; margin: 18px 0; font-size: 14px; line-height: 1.55;
}
.verdict .v-label {
  font-family: var(--font-mono); font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase; display: block; margin-bottom: 4px; color: var(--blue-700);
}
.verdict.confirm { border-left-color: var(--qw); }
.verdict.confirm .v-label { color: var(--qw); }
.verdict.gated { border-left-color: var(--st-gated); background: var(--callout-yellow-bg); }
.verdict.gated .v-label { color: var(--st-gated); }
.verdict.shelved { border-left-color: var(--st-closed); }
.verdict.shelved .v-label { color: var(--med); }
.ice-was { font-family: var(--font-mono); color: var(--faint); font-weight: 400; text-decoration: line-through; }

/* === Live-program pills === */
.live-pill {
  font-family: var(--font-mono);
  font-size: 10.5px; font-weight: 500; padding: 2px 8px; border-radius: var(--r-sm);
  background: var(--st-reframed-bg); color: var(--st-reframed); border: 1px solid var(--st-reframed-bd);
  white-space: nowrap;
}
.live-pill.running { background: var(--win-bg); color: var(--win); border-color: var(--win-bd); }
.live-pill.qa { background: var(--st-gated-bg); color: var(--st-gated); border-color: var(--st-gated-bd); }
.live-pill.design { background: var(--st-active-bg); color: var(--st-active); border-color: var(--st-active-bd); }

/* === Reconciliation ledger (the core artifact) === */
.recon-table { width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; }
.recon-table thead th {
  text-align: left; padding: 8px 14px; background: transparent;
  font-family: var(--font-mono); font-weight: 600; font-size: 11px; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--light); border-bottom: 1px solid var(--line-2);
}
.recon-table td { padding: 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
.recon-table tr:last-child td { border-bottom: none; }
.recon-table tbody tr { transition: background 0.12s; }
.recon-table tbody tr:hover td { background: var(--bg-section); }
.recon-table td strong { color: var(--dark); font-weight: 600; }
.recon-table td .recon-verdict {
  display: block; font-size: 13.5px; color: var(--med); margin-top: 5px; line-height: 1.55;
}
.recon-table td:first-child strong { font-family: var(--font-mono); }
.recon-table td .small { font-family: inherit; }

/* === Measured results (green is reserved for these) === */
.prelim { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 18px 0; }
.prelim-card {
  border: 1px solid var(--win-bd); background: var(--win-bg);
  border-radius: var(--r-lg); padding: 18px;
}
.prelim-card.caveat { border-color: var(--st-gated-bd); background: var(--callout-yellow-bg); }
.prelim-card .pl-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.prelim-card .pl-name { font-family: var(--font-mono); font-size: 12.5px; font-weight: 600; color: var(--dark); }
.prelim-card .pl-big { font-family: var(--font-mono); font-size: 30px; font-weight: 600; letter-spacing: -0.02em; color: var(--win); }
.prelim-card.caveat .pl-big { color: var(--st-gated); }
.prelim-card .pl-detail { font-size: 12.5px; color: var(--med); line-height: 1.55; }
.prelim-card .pl-flag { font-family: var(--font-mono); font-size: 11px; font-weight: 500; color: var(--st-gated); display: block; margin-top: 8px; }
@media (max-width: 720px) { .prelim { grid-template-columns: 1fr; } }

/* Status line on spokes */
.live-status {
  border: 1px solid var(--st-active-bd); background: var(--st-active-bg); border-radius: var(--r-md);
  padding: 12px 16px; margin: 14px 0; font-size: 13.5px; line-height: 1.55;
}
.live-status .ls-label {
  font-family: var(--font-mono); font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--st-active); display: block; margin-bottom: 4px;
}
.live-status.warn-edge { border-color: var(--st-gated-bd); background: var(--st-gated-bg); }
.live-status.warn-edge .ls-label { color: var(--st-gated); }

/* ES backlog emphasis */
.es-net, .es-dedup { font-family: var(--font-mono); font-size: 10.5px; font-weight: 600; letter-spacing: 0.02em; text-transform: uppercase; }
.es-net { color: var(--qw); }
.es-dedup { color: var(--med); }

/* Page chips */
.page-chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 0; }
.chip {
  font-size: 11.5px; background: var(--bg-light); border: 1px solid var(--line);
  padding: 3px 10px; border-radius: var(--r-sm); color: var(--med);
}

/* === Tier groups + portfolio cards (hub) === */
.tier-group { margin: 34px 0 6px; }
.tier-group .tg-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 14px; }
.tier-group .tg-head h3 {
  font-size: 13px; font-weight: 600; margin: 0;
  font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.04em;
  display: flex; align-items: center; gap: 8px;
}
.tier-group .tg-head h3::before {
  content: ""; width: 9px; height: 9px; border-radius: 2px; background: currentColor; display: inline-block;
}
.tier-group .tg-head .tg-sub { font-size: 12.5px; color: var(--light); }
.idx-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.idx-card {
  display: block; text-decoration: none; color: inherit;
  border: 1px solid var(--line); border-radius: var(--r-lg); padding: 18px 20px;
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s;
  position: relative; background: var(--bg-white);
}
.idx-card:hover { box-shadow: var(--card-shadow-hover); border-color: var(--line-2); transform: translateY(-1px); }
/* disposition shown as a left rail */
.idx-card::before {
  content: ""; position: absolute; left: 0; top: 14px; bottom: 14px; width: 3px; border-radius: 3px; background: var(--line-2);
}
.idx-card.qw-edge::before   { background: var(--blue); }
.idx-card.sb-edge::before   { background: var(--st-reframed); }
.idx-card.ex-edge::before   { background: var(--st-gated); }
.idx-card.hold-edge::before { background: var(--st-closed); }
.idx-card.dim { opacity: 0.82; }
.idx-card .ic-title { font-size: 15.5px; font-weight: 600; margin-bottom: 3px; padding-right: 22px; display: flex; align-items: center; flex-wrap: wrap; }
.idx-card .ic-title .n { font-family: var(--font-mono); color: var(--faint); margin-right: 6px; }
.idx-card .ic-page { font-size: 11.5px; color: var(--light); margin-bottom: 9px; }
.idx-card .ic-hyp { font-size: 13px; color: var(--med); margin-bottom: 14px; line-height: 1.55; }
.idx-card .ic-foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.idx-card .ic-ice { font-family: var(--font-mono); font-size: 11.5px; color: var(--med); font-weight: 500; }
.idx-card .ic-ice b { font-size: 14px; color: var(--dark); font-weight: 600; }
.idx-card .ic-ice .bd { font-weight: 400; color: var(--faint); }
.idx-card .ic-arrow { position: absolute; top: 18px; right: 16px; color: var(--faint); font-size: 14px; transition: transform 0.15s; }
.idx-card:hover .ic-arrow { transform: translateX(3px); color: var(--blue); }
.idx-card .ic-mock-status { font-family: var(--font-mono); font-size: 9.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.idx-card .ic-mock-status.ready { color: var(--qw); }
.idx-card .ic-mock-status.pending { color: var(--faint); }

/* === Generic tables === */
table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
th {
  text-align: left; padding: 9px 14px; background: transparent;
  font-family: var(--font-mono); font-weight: 600; font-size: 11px; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--light); border-bottom: 1px solid var(--line-2);
}
td { padding: 11px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
td:first-child { font-family: var(--font-mono); font-weight: 500; color: var(--dark); }
tr:hover td { background: var(--bg-section); }

/* === Browser-chrome mockups (spoke) === */
.mock-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 20px 0; }
.mock-compare.mobile { grid-template-columns: 1fr 1fr; max-width: 640px; }
.mock-col .mc-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.mc-tag {
  font-family: var(--font-mono); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
  padding: 3px 9px; border-radius: var(--r-sm);
}
.mc-tag.control { background: var(--bg-light); color: var(--light); }
.mc-tag.variant { background: var(--st-active-bg); color: var(--st-active); }
.mock-col .mc-sub { font-size: 11px; color: var(--light); }
.mock-chrome { border: 1px solid var(--line); border-radius: var(--r-lg); overflow: hidden; background: #fff; }
.mock-chrome:hover { box-shadow: var(--card-shadow-hover); }
.mock-chrome .bar { background: var(--bg-light); padding: 7px 12px; display: flex; gap: 6px; align-items: center; border-bottom: 1px solid var(--line); }
.mock-chrome .dot { width: 10px; height: 10px; border-radius: 50%; }
.mock-chrome .dot.r { background: #ff5f57; }
.mock-chrome .dot.y { background: #ffbd2e; }
.mock-chrome .dot.g { background: #28c940; }
.mock-chrome .url {
  flex: 1; background: #fff; border: 1px solid var(--line); border-radius: 4px;
  font-family: var(--font-mono); font-size: 10px; color: var(--light); padding: 3px 9px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mock-chrome img { width: 100%; display: block; cursor: zoom-in; }
.mock-pending {
  min-height: 190px; display: flex; flex-direction: column; gap: 4px;
  align-items: center; justify-content: center; text-align: center;
  background: repeating-linear-gradient(45deg, #fafafa, #fafafa 12px, #f4f4f4 12px, #f4f4f4 24px);
  color: var(--faint); font-size: 12px; padding: 16px;
}
.mock-pending b { font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--light); }
.annot { font-size: 12px; color: var(--med); background: var(--bg-light); border: 1px solid var(--line); border-radius: var(--r-sm); padding: 9px 13px; margin-top: 8px; line-height: 1.5; }
.annot b { color: var(--blue); }

/* === Variation tabs (spoke) === */
.var-tabs { display: flex; gap: 6px; margin: 18px 0 0; flex-wrap: wrap; }
.var-tab {
  font-family: var(--font-mono); font-size: 12px; font-weight: 500; padding: 7px 15px; border-radius: var(--r-sm) var(--r-sm) 0 0;
  border: 1px solid var(--line); border-bottom: none; background: var(--bg-light); color: var(--med); cursor: pointer;
}
.var-tab.active { background: #fff; color: var(--dark); border-color: var(--blue); position: relative; z-index: 2; }
.var-panel { border: 1px solid var(--blue); border-radius: 0 var(--r-md) var(--r-md) var(--r-md); padding: 16px 18px; font-size: 14px; margin-top: -1px; background: #fff; }
.var-panel .rec { font-family: var(--font-mono); font-size: 10px; font-weight: 600; color: var(--qw); text-transform: uppercase; letter-spacing: 0.04em; }
.var-panel.hidden { display: none; }

/* === Win/loss panels (spoke) === */
.winloss { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 14px 0; }
.wl { border-radius: var(--r-lg); padding: 16px 18px; font-size: 13.5px; line-height: 1.55; }
.wl.win { background: var(--win-bg); border: 1px solid var(--win-bd); }
.wl.loss { background: var(--callout-yellow-bg); border: 1px solid var(--st-gated-bd); }
.wl .lbl { font-family: var(--font-mono); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; display: block; margin-bottom: 5px; }
.wl.win .lbl { color: var(--win); }
.wl.loss .lbl { color: var(--st-gated); }

/* Self-critique (spoke) */
.crit { border-left: 3px solid var(--line-2); padding: 11px 16px; margin: 12px 0; background: var(--bg-section); border-radius: 0 var(--r-md) var(--r-md) 0; font-size: 13.5px; line-height: 1.55; }
.crit .ch { font-weight: 600; }
.crit .re { color: var(--med); display: block; margin-top: 5px; }

/* Folds (spoke) */
details.fold { border: 1px solid var(--line); border-radius: var(--r-md); margin: 12px 0; background: #fff; }
details.fold summary { padding: 11px 16px; font-size: 13px; font-weight: 600; cursor: pointer; list-style: none; color: var(--med); user-select: none; }
details.fold summary::before { content: "\\25B8  "; color: var(--faint); }
details.fold[open] summary::before { content: "\\25BE  "; }
details.fold .fold-body { padding: 0 16px 14px; font-size: 13.5px; }

/* === Run-order sequence (a real sequence, so numbering earns its place) === */
.seq { display: flex; gap: 0; align-items: stretch; margin: 24px 0; flex-wrap: wrap; }
.wave { flex: 1; min-width: 170px; border: 1px solid var(--line); background: var(--bg-section); padding: 18px 14px; text-align: center; }
.wave:first-child { border-radius: var(--r-lg) 0 0 var(--r-lg); }
.wave:last-child { border-radius: 0 var(--r-lg) var(--r-lg) 0; }
.wave .w-label { font-family: var(--font-mono); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--light); margin-bottom: 12px; }
.wave .w-items { display: flex; gap: 7px; justify-content: center; flex-wrap: wrap; }
.w-pill {
  font-family: var(--font-mono); font-size: 13px; font-weight: 600; width: 32px; height: 32px; border-radius: var(--r-md);
  display: inline-flex; align-items: center; justify-content: center; color: #fff; text-decoration: none; transition: transform 0.1s;
}
.w-pill:hover { transform: translateY(-2px); }
.w-pill.qw { background: var(--blue); } .w-pill.sb { background: var(--st-reframed); } .w-pill.ex { background: var(--st-gated); }
.seq-arrow { width: 28px; display: flex; align-items: center; justify-content: center; color: var(--faint); font-size: 16px; flex-shrink: 0; }
.wave .w-note { font-size: 11px; color: var(--light); margin-top: 11px; line-height: 1.5; }

/* Propagation cards */
.prop-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin: 18px 0; }
.prop-card { border: 1px dashed var(--line-2); border-radius: var(--r-lg); padding: 15px 16px; background: var(--bg-section); font-size: 12.5px; line-height: 1.55; }
.prop-card .pc-if { font-family: var(--font-mono); font-size: 10.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--blue); display: block; margin-bottom: 5px; }

/* === Exclusions === */
.excl-list { margin: 14px 0; }
.excl-list details { border-bottom: 1px solid var(--line); }
.excl-list summary { padding: 13px 4px; font-size: 14.5px; cursor: pointer; list-style: none; user-select: none; }
.excl-list summary::before { content: "\\25B8"; color: var(--faint); font-size: 11px; margin-right: 9px; }
.excl-list details[open] summary::before { content: "\\25BE"; }
.excl-list summary b { font-weight: 600; }
.excl-list summary .why { color: var(--light); font-size: 13px; }
.excl-list .excl-body { padding: 0 4px 16px 24px; font-size: 13.5px; color: var(--med); line-height: 1.6; }
.excl-list details.hl { background: var(--callout-yellow-bg); border-radius: var(--r-md); border-bottom: none; margin-bottom: 6px; }
.excl-list details.hl summary { padding: 13px 14px; }
.excl-list details.hl .excl-body { padding: 0 14px 14px 34px; }

/* === Decisions & Asks === */
.prereq-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin: 18px 0; }
.prereq-col { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 20px; background: var(--bg-white); }
.prereq-col h4 { font-family: var(--font-mono); font-size: 12px; font-weight: 600; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.03em; display: flex; align-items: center; gap: 8px; }
.prereq-col h4::before { content: ""; width: 9px; height: 9px; border-radius: 2px; background: currentColor; }
.prereq-col ul { list-style: none; margin: 0; }
.prereq-col li { font-size: 12.5px; margin-bottom: 12px; padding-left: 22px; position: relative; color: var(--med); line-height: 1.5; }
.prereq-col li::before { content: "\\2610"; position: absolute; left: 0; color: var(--faint); }
.prereq-col li .blocks { font-family: var(--font-mono); display: block; font-size: 10.5px; color: var(--blue); margin-top: 3px; letter-spacing: -0.01em; }

/* Before-launch checklist (spoke) */
.launch-list { list-style: none; margin: 12px 0; }
.launch-list li { font-size: 14px; margin-bottom: 8px; padding-left: 24px; position: relative; }
.launch-list li::before { content: "\\2610"; position: absolute; left: 0; color: var(--faint); }

/* Footer pager (spoke) */
.foot-pager { display: flex; justify-content: space-between; gap: 12px; padding: 28px 0 64px; }
.foot-pager a { font-size: 13.5px; text-decoration: none; color: var(--med); border: 1px solid var(--line); border-radius: var(--r-lg); padding: 12px 18px; transition: all 0.15s; max-width: 46%; }
.foot-pager a:hover { border-color: var(--blue); color: var(--dark); box-shadow: var(--card-shadow-hover); }
.foot-pager a .dir { font-family: var(--font-mono); font-size: 10px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--faint); display: block; }
.foot-pager .spacer { flex: 1; }

/* Lightbox */
.lightbox-overlay { display: none; position: fixed; inset: 0; z-index: 1000; background: rgba(20,24,28,0.9); align-items: center; justify-content: center; padding: 24px; cursor: zoom-out; }
.lightbox-overlay.open { display: flex; }
.lightbox-overlay img { max-width: 100%; max-height: calc(100vh - 80px); border-radius: var(--r-sm); box-shadow: 0 8px 40px rgba(0,0,0,0.4); cursor: default; }
.lb-caption { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.7); color: #fff; font-size: 14px; font-weight: 500; padding: 8px 20px; border-radius: var(--r-md); white-space: nowrap; pointer-events: none; }
.lb-close { position: fixed; top: 16px; right: 20px; background: rgba(255,255,255,0.15); border: none; color: #fff; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 26px; display: flex; align-items: center; justify-content: center; }
.lb-close:hover { background: rgba(255,255,255,0.25); }

/* === Footer === */
.site-foot { border-top: 1px solid var(--line); padding: 24px 0 60px; font-size: 12px; color: var(--light); }
.site-foot .container { font-family: var(--font-mono); letter-spacing: -0.01em; line-height: 1.6; }

/* Orphan control */
p, h1, h2, h3, li, .hypothesis, .subtitle, .ic-hyp, .wl, .crit, .annot { text-wrap: pretty; }

/* === Responsive === */
@media (max-width: 720px) {
  .idx-grid, .mock-compare, .winloss, .prereq-grid, .prop-grid { grid-template-columns: 1fr; }
  .hero { padding: 100px 0 40px; }
  .hero h1 { font-size: 28px; }
  .exp-hero h1 { font-size: 23px; }
  .recon-legend { gap: 14px; }
  nav .nav-links { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  * { scroll-behavior: auto; transition: none !important; }
}
"""


# --------------------------------------------------------------------------
# Shared JS behaviors: nav scroll state + scroll-spy, lightbox, variation tabs.
# --------------------------------------------------------------------------
SITE_JS = """// Shared behavior: nav scroll state + scroll-spy, lightbox, variation tabs.

(function () {
  var nav = document.querySelector('nav');
  if (nav) {
    window.addEventListener('scroll', function () {
      nav.classList.toggle('scrolled', window.scrollY > 10);
    });
  }

  // Scroll-spy (hub only -- pages with .nav-links anchors)
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('nav .nav-links a[href^="#"]');
  if (navLinks.length) {
    window.addEventListener('scroll', function () {
      var current = '';
      sections.forEach(function (s) {
        if (window.scrollY >= s.offsetTop - 110) current = s.id;
      });
      navLinks.forEach(function (a) {
        a.classList.toggle('active', a.getAttribute('href') === '#' + current);
      });
    });
  }

  // Lightbox for mockup images (no-op until images exist)
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.mock-chrome img'));
  if (imgs.length) {
    var overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = '<button class="lb-close">&times;</button><img alt=""><div class="lb-caption"></div>';
    document.body.appendChild(overlay);
    var lbImg = overlay.querySelector('img');
    var lbCap = overlay.querySelector('.lb-caption');
    function close() { overlay.classList.remove('open'); document.body.style.overflow = ''; }
    imgs.forEach(function (img) {
      img.addEventListener('click', function () {
        lbImg.src = img.src;
        lbCap.textContent = img.alt;
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
      });
    });
    overlay.querySelector('.lb-close').addEventListener('click', close);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('open')) close();
    });
  }

  // Variation tabs (spoke pages with multiple variations)
  var tabs = document.querySelectorAll('.var-tab');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var target = tab.getAttribute('data-panel');
      document.querySelectorAll('.var-tab').forEach(function (t) { t.classList.remove('active'); });
      document.querySelectorAll('.var-panel').forEach(function (p) {
        p.classList.toggle('hidden', p.id !== target);
      });
      tab.classList.add('active');
      var panel = document.getElementById(target);
      var annot = document.querySelector('[data-variant-annot]');
      if (panel && annot && panel.getAttribute('data-annot')) {
        annot.innerHTML = panel.getAttribute('data-annot');
      }
    });
  });
})();
"""


def _esc(text):
    """HTML-escape a string for safe insertion into emitted markup."""
    return html.escape(str(text), quote=True)


def build_hub_shell(title):
    """Return the hub (index.html) shell with a labeled content slot."""
    safe_title = _esc(title)
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | FunnelEnvy</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{styles}">
</head>
<body>

<nav>
  <div class="nav-inner">
    <a class="brand" href="{hub}">FunnelEnvy<span class="sep">/</span><span class="client">Experiment Roadmap</span></a>
    <div class="nav-links">
      <!-- NAV-LINKS-SLOT: agent fills section anchors -->
    </div>
  </div>
</nav>

{slot}

<script src="{script}"></script>
</body>
</html>
""".format(
        title=safe_title,
        styles=STYLES_FILENAME,
        hub=HUB_FILENAME,
        script=SCRIPT_FILENAME,
        slot=CONTENT_SLOT,
    )


def build_spoke_shell(exp, prev_exp, next_exp, title):
    """Return a spoke shell with breadcrumb, top pager, content slot, and foot pager.

    prev_exp / next_exp are experiment dicts or None. The pager chain is wired
    here so navigation is correct without any agent authoring.
    """
    safe_site_title = _esc(title)
    num = int(exp["number"])

    # Top-nav pager (breadcrumb + prev/next).
    if prev_exp is None:
        prev_link = '<a href="{hub}" class="disabled">&larr; Prev</a>'.format(hub=HUB_FILENAME)
    else:
        prev_link = '<a href="{f}">&larr; Prev: #{n}</a>'.format(
            f=spoke_filename(prev_exp["number"]), n=int(prev_exp["number"])
        )
    if next_exp is None:
        next_link = '<a href="{hub}" class="disabled">Next &rarr;</a>'.format(hub=HUB_FILENAME)
    else:
        next_link = '<a href="{f}">Next: #{n} &rarr;</a>'.format(
            f=spoke_filename(next_exp["number"]), n=int(next_exp["number"])
        )

    # Foot pager (Up to hub + Next).
    if next_exp is None:
        foot_next = '<div class="spacer"></div>'
    else:
        foot_next = (
            '<a href="{f}" style="text-align:right;"><span class="dir">Next</span>#{n}</a>'.format(
                f=spoke_filename(next_exp["number"]), n=int(next_exp["number"])
            )
        )

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>#{num} | {site} | FunnelEnvy</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{styles}">
</head>
<body>

<nav>
  <div class="nav-inner">
    <a class="brand" href="{hub}">&larr; Roadmap<span class="sep">/</span><span class="client">Experiment #{num}</span></a>
    <div class="pager">
      {prev_link}
      {next_link}
    </div>
  </div>
</nav>

<div class="container">

{slot}

<div class="foot-pager">
  <a href="{hub}"><span class="dir">Up</span>Roadmap overview</a>
  {foot_next}
</div>

</div>
<script src="{script}"></script>
</body>
</html>
""".format(
        num=num,
        site=safe_site_title,
        styles=STYLES_FILENAME,
        hub=HUB_FILENAME,
        prev_link=prev_link,
        next_link=next_link,
        foot_next=foot_next,
        slot=CONTENT_SLOT,
        script=SCRIPT_FILENAME,
    )


def _normalize_experiments(experiments):
    """Validate and order the experiment list. Returns a new sorted list."""
    norm = []
    for exp in experiments:
        if "number" not in exp or "title" not in exp:
            raise ValueError("each experiment requires 'number' and 'title': %r" % (exp,))
        norm.append(
            {
                "number": int(exp["number"]),
                "title": str(exp["title"]),
                "mockup_present": bool(exp.get("mockup_present", False)),
            }
        )
    norm.sort(key=lambda e: e["number"])
    return norm


def scaffold(manifest):
    """Build the in-memory file map for a manifest. Pure: returns {relpath: content}.

    Deterministic: identical manifest input yields a byte-identical file map.
    No timestamps, no dict-order dependence (experiments are sorted by number).
    """
    title = str(manifest.get("title", "Experiment Roadmap"))
    experiments = _normalize_experiments(manifest.get("experiments", []))

    files = {}
    files[STYLES_FILENAME] = STYLES_CSS
    files[SCRIPT_FILENAME] = SITE_JS
    files[HUB_FILENAME] = build_hub_shell(title)

    for idx, exp in enumerate(experiments):
        prev_exp = experiments[idx - 1] if idx > 0 else None
        next_exp = experiments[idx + 1] if idx < len(experiments) - 1 else None
        files[spoke_filename(exp["number"])] = build_spoke_shell(exp, prev_exp, next_exp, title)

    return files


def write_site(manifest, out_dir):
    """Write the scaffolded file map to out_dir. Returns the list of written paths."""
    files = scaffold(manifest)
    os.makedirs(out_dir, exist_ok=True)
    # Pre-create the number-keyed mockup asset dirs so the agent has a target.
    for exp in _normalize_experiments(manifest.get("experiments", [])):
        os.makedirs(os.path.join(out_dir, asset_dir_for(exp["number"])), exist_ok=True)
    written = []
    for relpath in sorted(files):
        abspath = os.path.join(out_dir, relpath)
        with open(abspath, "w", encoding="utf-8") as fh:
            fh.write(files[relpath])
        written.append(abspath)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scaffold a roadmap presentation site.")
    parser.add_argument("manifest", help="Path to the JSON manifest.")
    parser.add_argument("--out", default=None, help="Output directory (overrides manifest out_dir).")
    args = parser.parse_args(argv)

    with open(args.manifest, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    out_dir = args.out or manifest.get("out_dir")
    if not out_dir:
        parser.error("no output directory: pass --out or set 'out_dir' in the manifest")

    written = write_site(manifest, out_dir)
    print(json.dumps({"out_dir": out_dir, "files": [os.path.relpath(p, out_dir) for p in written]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
