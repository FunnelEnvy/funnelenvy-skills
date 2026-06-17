#!/usr/bin/env python3
"""Deterministic scaffolding for the roadmap-presentation site.

Emits every byte of chrome for a hub-and-spoke roadmap presentation site:
the shared FunnelEnvy CSS design system, the shared JS behaviors, the hub and
spoke HTML page shells, and the prev/next pager chain wired across spokes. The
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

The agent slugifies experiment titles separately (per modules/slugify.md) to
locate source mockup directories; this script keys assets only by zero-padded
experiment number, so the deployed site never depends on slug stability.
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
# Design system (CSS). FunnelEnvy visual language: IBM Plex Sans, CSS-variable
# palette, tier/disposition badges, verdict banners, browser-chrome mockup
# frames, lightbox, sticky scroll-spy nav. Generic, reusable, no client content.
# --------------------------------------------------------------------------
STYLES_CSS = """/* Roadmap presentation: FunnelEnvy design system (IBM Plex Sans).
   Emitted by scaffold_site.py. Generic, reusable chrome: no client content. */

:root {
  --blue: #3B82F6;
  --purple: #8B5CF6;
  --red: #DC2626;
  --dark: #212628;
  --med: #595959;
  --light: #666B73;
  --faint: #8a8f96;
  --bg-white: #FFFFFF;
  --bg-light: #F5F5F5;
  --bg-section: #FAFAFA;
  --qw: #16a34a;
  --sb: #1d4ed8;
  --ex: #b45309;
  --callout-yellow-bg: #FFF8E7;
  --callout-yellow-border: #F6B26B;
  --callout-blue-bg: #EBF0FC;
  --callout-blue-border: #3C78D8;
  --callout-red-bg: #FEF2F2;
  --callout-red-border: #DC2626;
  --callout-green-bg: #F0FDF4;
  --callout-green-border: #22C55E;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --card-shadow-hover: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
  font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--dark);
  background: var(--bg-white);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.container { max-width: 920px; margin: 0 auto; padding: 0 2rem; }
section { padding: 44px 0; }
section + section { border-top: 1px solid #eee; }

/* Navigation */
nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #eee;
  padding: 0 2rem;
  transition: box-shadow 0.2s;
}
nav.scrolled { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
nav .nav-inner {
  max-width: 1240px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  min-height: 52px; gap: 12px; flex-wrap: wrap; padding: 6px 0;
}
nav .brand {
  font-weight: 700; font-size: 14px; letter-spacing: -0.01em;
  white-space: nowrap; color: var(--dark); text-decoration: none;
}
nav .brand .sep { color: #ccc; font-weight: 300; margin: 0 6px; }
nav .brand .client { color: var(--med); font-weight: 500; }
nav .nav-links { display: flex; gap: 6px; flex-wrap: wrap; }
nav .nav-links a {
  font-size: 12px; font-weight: 500; color: var(--med);
  text-decoration: none; padding: 6px 10px; border-radius: 6px;
  transition: all 0.15s;
}
nav .nav-links a:hover { background: var(--bg-light); color: var(--dark); }
nav .nav-links a.active { background: var(--blue); color: #fff; }
nav .pager { display: flex; gap: 6px; }
nav .pager a {
  font-size: 12px; text-decoration: none; color: var(--med);
  border: 1px solid #e5e5e5; border-radius: 6px; padding: 5px 11px;
  transition: all 0.15s; white-space: nowrap;
}
nav .pager a:hover { background: var(--bg-light); color: var(--dark); }
nav .pager a.disabled { opacity: 0.35; pointer-events: none; }

/* Hero */
.hero {
  padding: 104px 0 44px;
  background: linear-gradient(135deg, #f8f9ff 0%, #fff 50%, #f0fdf4 100%);
}
.hero h1 {
  font-size: 32px; font-weight: 700; line-height: 1.2;
  letter-spacing: -0.02em; margin-bottom: 8px;
}
.hero .subtitle {
  font-size: 17px; color: var(--med); line-height: 1.5;
  max-width: 720px; margin-bottom: 20px;
}
.hero .meta { font-size: 13px; color: var(--light); }
.hero .meta span + span::before { content: " / "; }

/* Spoke page hero (lighter) */
.exp-hero { padding: 96px 0 12px; }
.exp-hero .top-line { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.exp-hero h1 { font-size: 27px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.25; }
.exp-hero h1 .n { color: var(--faint); margin-right: 4px; }
.hypothesis { font-size: 16px; line-height: 1.55; max-width: 740px; margin-top: 12px; }
.ice-inline {
  display: inline-flex; align-items: baseline; gap: 12px; flex-wrap: wrap;
  font-size: 12.5px; color: var(--faint); margin-top: 14px;
}
.ice-inline .total { font-weight: 700; color: var(--med); font-size: 13.5px; }

/* Typography */
h2 {
  font-size: 23px; font-weight: 700; letter-spacing: -0.02em;
  margin-bottom: 8px; line-height: 1.3;
}
h3 {
  font-size: 17px; font-weight: 600; letter-spacing: -0.01em;
  margin-bottom: 6px; margin-top: 26px; line-height: 1.3;
}
p { margin-bottom: 14px; font-size: 15px; }
.section-lead { font-size: 15px; color: var(--med); margin-bottom: 22px; max-width: 740px; }
.small { font-size: 13px; color: var(--med); }
.muted { color: var(--light); }
ul, ol { margin: 8px 0 14px 20px; font-size: 15px; }
li { margin-bottom: 6px; }
li::marker { color: var(--light); }
a { color: var(--blue); }

/* Callouts */
.callout {
  padding: 16px 20px; border-radius: 8px; margin: 20px 0;
  border-left: 4px solid; font-size: 14px;
}
.callout-yellow { background: var(--callout-yellow-bg); border-color: var(--callout-yellow-border); }
.callout-blue { background: var(--callout-blue-bg); border-color: var(--callout-blue-border); }
.callout-red { background: var(--callout-red-bg); border-color: var(--callout-red-border); }
.callout-green { background: var(--callout-green-bg); border-color: var(--callout-green-border); }
.callout .label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.05em;
  text-transform: uppercase; margin-bottom: 6px; display: block;
}
.callout-blue .label { color: var(--callout-blue-border); }
.callout-yellow .label { color: #b45309; }
.callout-red .label { color: var(--red); }
.callout-green .label { color: #16a34a; }

/* Stat row */
.stat-row { display: flex; gap: 14px; flex-wrap: wrap; margin: 22px 0; }
.stat-item {
  flex: 1; min-width: 140px; background: #fff; padding: 16px;
  border-radius: 10px; text-align: center; border: 1px solid #eee;
  box-shadow: var(--card-shadow);
}
.stat-item .num { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; }
.stat-item .num.green { color: var(--qw); }
.stat-item .num.red { color: var(--red); }
.stat-item .num.amber { color: var(--ex); }
.stat-item .desc { font-size: 12px; color: var(--light); margin-top: 2px; line-height: 1.4; }

/* Tier badges */
.tier {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  padding: 4px 10px; border-radius: 12px; white-space: nowrap; display: inline-block;
}
.tier.qw { background: #f0fdf4; color: var(--qw); border: 1px solid #bbe7c8; }
.tier.sb { background: #eff4fe; color: var(--sb); border: 1px solid #c4d6f8; }
.tier.ex { background: #fff7eb; color: var(--ex); border: 1px solid #f0d8b0; }

/* Disposition badges */
.disp {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  padding: 4px 10px; border-radius: 12px; white-space: nowrap; display: inline-block;
}
.disp.run { background: #f0fdf4; color: var(--qw); border: 1px solid #bbe7c8; }
.disp.gated { background: var(--callout-yellow-bg); color: #b45309; border: 1px solid #f0d8b0; }
.disp.reframed { background: #eff4fe; color: var(--sb); border: 1px solid #c4d6f8; }
.disp.held { background: var(--bg-light); color: var(--med); border: 1px solid #ddd; }
.disp.superseded { background: var(--bg-light); color: var(--light); border: 1px solid #ddd; }
.disp.net-new { background: #f0fdf4; color: var(--qw); border: 1px solid #bbe7c8; }
.run-order {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%; background: var(--dark); color: #fff;
  font-size: 11px; font-weight: 700; margin-right: 8px; flex-shrink: 0;
}
.verdict {
  border: 1px solid #e5e5e5; border-left: 4px solid var(--blue); background: var(--bg-section);
  border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 18px 0; font-size: 13.5px; line-height: 1.55;
}
.verdict .v-label {
  font-size: 10.5px; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; display: block; margin-bottom: 4px; color: var(--blue);
}
.verdict.confirm { border-left-color: var(--qw); }
.verdict.confirm .v-label { color: var(--qw); }
.verdict.gated { border-left-color: #b45309; background: var(--callout-yellow-bg); }
.verdict.gated .v-label { color: #b45309; }
.verdict.shelved { border-left-color: #999; }
.verdict.shelved .v-label { color: var(--med); }
.ice-was { color: var(--faint); font-weight: 400; text-decoration: line-through; }

/* Page chips */
.page-chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 0; }
.chip {
  font-size: 11.5px; background: var(--bg-light); border: 1px solid #e8e8e8;
  padding: 3px 10px; border-radius: 11px; color: var(--med);
}

/* Tier groups + index cards (hub) */
.tier-group { margin: 26px 0 6px; }
.tier-group .tg-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
.tier-group .tg-head h3 { font-size: 16px; font-weight: 700; margin: 0; }
.tier-group .tg-head .tg-sub { font-size: 12.5px; color: var(--light); }
.idx-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.idx-card {
  display: block; text-decoration: none; color: inherit;
  border: 1px solid #e8e8e8; border-radius: 12px; padding: 18px;
  box-shadow: var(--card-shadow); transition: box-shadow 0.15s, border-color 0.15s;
  position: relative; background: #fff;
}
.idx-card:hover { box-shadow: var(--card-shadow-hover); border-color: var(--blue); }
.idx-card.qw-edge { border-top: 3px solid var(--qw); }
.idx-card.sb-edge { border-top: 3px solid var(--sb); }
.idx-card.ex-edge { border-top: 3px solid var(--ex); }
.idx-card.hold-edge { border-top: 3px solid #b3b8bf; }
.idx-card.dim { opacity: 0.88; }
.idx-card .ic-title { font-size: 15px; font-weight: 700; margin-bottom: 2px; padding-right: 20px; }
.idx-card .ic-title .n { color: var(--faint); margin-right: 5px; }
.idx-card .ic-page { font-size: 11.5px; color: var(--light); margin-bottom: 8px; }
.idx-card .ic-hyp { font-size: 13px; color: var(--med); margin-bottom: 12px; line-height: 1.5; }
.idx-card .ic-foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.idx-card .ic-ice { font-size: 11.5px; color: var(--med); font-weight: 600; }
.idx-card .ic-ice b { font-size: 14px; color: var(--dark); }
.idx-card .ic-ice .bd { font-weight: 400; color: var(--faint); }
.idx-card .ic-arrow { position: absolute; top: 16px; right: 16px; color: var(--faint); font-size: 14px; }
.idx-card .ic-mock-status {
  font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
}
.idx-card .ic-mock-status.ready { color: var(--qw); }
.idx-card .ic-mock-status.pending { color: var(--faint); }
.idx-card .ic-thumb { display: block; width: 100%; border-radius: 6px; margin-top: 10px; border: 1px solid #eee; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
th {
  text-align: left; padding: 10px 14px; background: var(--bg-light);
  font-weight: 600; font-size: 12px; letter-spacing: 0.03em;
  text-transform: uppercase; color: var(--med); border-bottom: 2px solid #e5e5e5;
}
td { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; vertical-align: top; }
tr:hover td { background: #fafafa; }

/* Browser-chrome mockup frames */
.mock-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 20px 0; }
.mock-compare.mobile { grid-template-columns: 1fr 1fr; max-width: 640px; }
.mock-col .mc-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.mc-tag {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  padding: 3px 9px; border-radius: 4px;
}
.mc-tag.control { background: #f1f5f9; color: #64748b; }
.mc-tag.variant { background: #dbeafe; color: #1d4ed8; }
.mock-col .mc-sub { font-size: 11px; color: var(--light); }
.mock-chrome {
  border: 1px solid #e5e5e5; border-radius: 10px; overflow: hidden; background: #fff;
}
.mock-chrome:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.mock-chrome .bar {
  background: #f1f1f1; padding: 7px 12px;
  display: flex; gap: 6px; align-items: center; border-bottom: 1px solid #e5e5e5;
}
.mock-chrome .dot { width: 10px; height: 10px; border-radius: 50%; }
.mock-chrome .dot.r { background: #ff5f57; }
.mock-chrome .dot.y { background: #ffbd2e; }
.mock-chrome .dot.g { background: #28c940; }
.mock-chrome .url {
  flex: 1; background: #fff; border: 1px solid #e5e5e5; border-radius: 4px;
  font-size: 10px; color: var(--light); padding: 3px 9px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mock-chrome img { width: 100%; display: block; cursor: zoom-in; }
.mock-pending {
  min-height: 190px; display: flex; flex-direction: column; gap: 4px;
  align-items: center; justify-content: center; text-align: center;
  background: repeating-linear-gradient(45deg, #fafafa, #fafafa 12px, #f4f4f4 12px, #f4f4f4 24px);
  color: var(--faint); font-size: 12px; padding: 16px;
}
.mock-pending b { font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--light); }
.annot {
  font-size: 12px; color: var(--med); background: var(--bg-light);
  border: 1px solid #eee; border-radius: 6px; padding: 9px 13px; margin-top: 8px; line-height: 1.5;
}
.annot b { color: var(--blue); }

/* Variation tabs */
.var-tabs { display: flex; gap: 6px; margin: 18px 0 0; flex-wrap: wrap; }
.var-tab {
  font-size: 12.5px; font-weight: 600; padding: 7px 15px; border-radius: 7px 7px 0 0;
  border: 1px solid #e5e5e5; border-bottom: none; background: var(--bg-light);
  color: var(--med); cursor: pointer;
}
.var-tab.active { background: #fff; color: var(--dark); border-color: var(--blue); position: relative; z-index: 2; }
.var-panel {
  border: 1px solid var(--blue); border-radius: 0 8px 8px 8px; padding: 16px 18px;
  font-size: 14px; margin-top: -1px; background: #fff;
}
.var-panel .rec {
  font-size: 10px; font-weight: 700; color: var(--qw);
  text-transform: uppercase; letter-spacing: 0.05em;
}
.var-panel.hidden { display: none; }

/* Win/loss panels */
.winloss { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 14px 0; }
.wl { border-radius: 10px; padding: 16px 18px; font-size: 13.5px; line-height: 1.55; }
.wl.win { background: var(--callout-green-bg); border: 1px solid #bbe7c8; }
.wl.loss { background: #fff7eb; border: 1px solid #f0d8b0; }
.wl .lbl {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; display: block; margin-bottom: 5px;
}
.wl.win .lbl { color: var(--qw); }
.wl.loss .lbl { color: var(--ex); }

/* Self-critique */
.crit {
  border-left: 3px solid #ddd; padding: 11px 16px; margin: 12px 0;
  background: var(--bg-section); border-radius: 0 8px 8px 0; font-size: 13.5px; line-height: 1.55;
}
.crit .ch { font-weight: 600; }
.crit .re { color: var(--med); display: block; margin-top: 5px; }

/* Folds */
details.fold { border: 1px solid #eee; border-radius: 8px; margin: 12px 0; background: #fff; }
details.fold summary {
  padding: 11px 16px; font-size: 13px; font-weight: 600; cursor: pointer;
  list-style: none; color: var(--med); user-select: none;
}
details.fold summary::before { content: "\\25B8  "; color: var(--faint); }
details.fold[open] summary::before { content: "\\25BE  "; }
details.fold .fold-body { padding: 0 16px 14px; font-size: 13.5px; }

/* Sequencing waves */
.seq { display: flex; gap: 0; align-items: stretch; margin: 22px 0; flex-wrap: wrap; }
.wave {
  flex: 1; min-width: 160px; border: 1px solid #e5e5e5; background: var(--bg-section);
  padding: 16px 12px; text-align: center;
}
.wave:first-child { border-radius: 10px 0 0 10px; }
.wave:last-child { border-radius: 0 10px 10px 0; }
.wave .w-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--light); margin-bottom: 10px;
}
.wave .w-items { display: flex; gap: 7px; justify-content: center; flex-wrap: wrap; }
.w-pill {
  font-size: 12.5px; font-weight: 700; width: 30px; height: 30px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  color: #fff; text-decoration: none; transition: transform 0.1s;
}
.w-pill:hover { transform: scale(1.12); }
.w-pill.qw { background: var(--qw); } .w-pill.sb { background: var(--sb); } .w-pill.ex { background: var(--ex); }
.seq-arrow {
  width: 26px; display: flex; align-items: center; justify-content: center;
  color: var(--faint); font-size: 16px; flex-shrink: 0;
}
.wave .w-note { font-size: 10.5px; color: var(--light); margin-top: 9px; line-height: 1.45; }

/* Exclusions */
.excl-list { margin: 14px 0; }
.excl-list details { border-bottom: 1px solid #f0f0f0; }
.excl-list summary {
  padding: 11px 4px; font-size: 14px; cursor: pointer; list-style: none; user-select: none;
}
.excl-list summary::before { content: "\\25B8  "; color: var(--faint); font-size: 12px; }
.excl-list details[open] summary::before { content: "\\25BE  "; }
.excl-list summary b { font-weight: 600; }
.excl-list summary .why { color: var(--light); font-size: 13px; }
.excl-list .excl-body { padding: 0 4px 14px 20px; font-size: 13.5px; color: var(--med); }

/* Asks columns */
.prereq-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin: 18px 0; }
.prereq-col { border: 1px solid #eee; border-radius: 12px; padding: 18px; background: #fff; box-shadow: var(--card-shadow); }
.prereq-col h4 { font-size: 13px; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
.prereq-col ul { list-style: none; margin: 0; }
.prereq-col li { font-size: 12.5px; margin-bottom: 10px; padding-left: 22px; position: relative; color: var(--med); line-height: 1.45; }
.prereq-col li::before { content: "\\2610"; position: absolute; left: 0; color: var(--faint); }
.prereq-col li .blocks { display: block; font-size: 10.5px; color: var(--blue); margin-top: 1px; }

/* Before-launch checklist (spoke) */
.launch-list { list-style: none; margin: 12px 0; }
.launch-list li { font-size: 14px; margin-bottom: 8px; padding-left: 24px; position: relative; }
.launch-list li::before { content: "\\2610"; position: absolute; left: 0; color: var(--faint); }

/* Footer pager (spoke) */
.foot-pager { display: flex; justify-content: space-between; gap: 12px; padding: 28px 0 64px; }
.foot-pager a {
  font-size: 13.5px; text-decoration: none; color: var(--med);
  border: 1px solid #e5e5e5; border-radius: 10px; padding: 12px 18px;
  transition: all 0.15s; max-width: 46%;
}
.foot-pager a:hover { border-color: var(--blue); color: var(--dark); box-shadow: var(--card-shadow); }
.foot-pager a .dir {
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--faint); display: block;
}
.foot-pager .spacer { flex: 1; }

/* Lightbox */
.lightbox-overlay {
  display: none; position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.88);
  align-items: center; justify-content: center;
  padding: 24px; cursor: zoom-out;
}
.lightbox-overlay.open { display: flex; }
.lightbox-overlay img {
  max-width: 100%; max-height: calc(100vh - 80px);
  border-radius: 6px; box-shadow: 0 8px 40px rgba(0,0,0,0.4); cursor: default;
}
.lb-caption {
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,0.7); color: #fff; font-size: 14px; font-weight: 500;
  padding: 8px 20px; border-radius: 8px; white-space: nowrap; pointer-events: none;
}
.lb-close {
  position: fixed; top: 16px; right: 20px; background: rgba(255,255,255,0.15);
  border: none; color: #fff; width: 44px; height: 44px; border-radius: 50%;
  cursor: pointer; font-size: 26px; display: flex; align-items: center; justify-content: center;
}
.lb-close:hover { background: rgba(255,255,255,0.25); }

/* Footer */
.site-foot {
  border-top: 1px solid #eee; padding: 22px 0 60px;
  font-size: 12px; color: var(--light);
}

/* Orphan control */
p, h1, h2, h3, li, .hypothesis, .subtitle, .ic-hyp, .wl, .crit, .annot { text-wrap: pretty; }

@media (max-width: 720px) {
  .idx-grid, .mock-compare, .winloss, .prereq-grid { grid-template-columns: 1fr; }
  .hero h1 { font-size: 26px; }
  .exp-hero h1 { font-size: 22px; }
  nav .nav-links { display: none; }
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
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
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
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
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
