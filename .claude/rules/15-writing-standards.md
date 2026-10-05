---
version: "1.1.0"
updated: 2026-10-05
---
# Writing Standards

This rule sets the standard for all prose the agent writes or edits: where it applies, the readability floor, house style, output structure and the self-audit before prose ships.

## Scope

- You MUST apply this standard to all prose you write: chat replies, commit messages, change documents, rules, skills, READMEs and knowledge base artifacts. It is always on. No step invokes it and no request switches it on.
- Code, configs, data, quoted text and text clearly taken from an external source are outside this standard. Leave them as written. A skill's frontmatter `description` is a trigger-matching surface and is exempt.
- Apply it to existing prose as well, whoever wrote it. When you edit or review a passage, bring it up to standard.

## Readability Floor

The floor applies to every reply and every file, short ones included, whether or not anyone asked for plain language.

- **Short sentences.** Prefer short, direct sentences and phrases. Rewrite any sentence past about 30 words.
- **Plain language.** Use clear, simple words. Cut wordy, dense or flowery phrasing.
- **Less nesting and hedging.** Flatten stacked clauses and qualifiers. Assert directly.
- **One aside per sentence.** Cut nested parentheticals and em-dash asides.
- **Navigable structure.** Prefer bullets and tables over long prose, and never ship a wall of text. A sub-procedure, output format or concept that other text cites gets its own heading.
- **Lean lists.** Drop words that repeat across list items, such as a shared subject or verb.
- **Point first.** State the conclusion, then support it.
- **Explain, don't justify.** document-management's `Rationale Minimization` holds the test.
- **Code spans for section names.** Keep bold for emphasis and lead labels, never for named identifiers.

Readability is not dumbing-down. Keep load-bearing terms, numbers, names and caveats, and phrasing that technical, legal or compliance text requires.

## House Style

- **Title Case headings.** Every heading, H1 and `title` field. Articles, coordinating conjunctions and short prepositions stay lowercase unless first, as in `Ready to Fix`. Code spans keep their own case.
- **Bold lead labels.** Open a labelled bullet with `**Label.** Detail.` Labels are not headings, so they stay in sentence case. Nested lists take italic sub-labels.
- **Implied subjects.** In first-person writing, drop the subject when the actor is obvious. A directive lead-in keeps its subject: "You" before the RFC 2119 verb.

## Output Structure

- **Files.** A file or other long-form page gets the `document` shape.
- **Messages.** A chat reply or other short post, such as a comment or a Slack message, gets the `message` shape: paragraphs of two or three sentences at most, with a bias toward lists.

## Self-Audit

- **Re-read before shipping.** Ask what still reads as AI-generated. Sweep, highest yield first: clichés and AI vocabulary, flat rhythm, em-dash overuse, uniform density, hidden actors, repeated phrasing.
- **No manufactured edits.** Leave text alone when nothing is worth changing.
- **One home.** This is the only copy of the sweep list. Other documents point here.

## Transform Engine

- **Engine skill.** `human-content-transform` holds the AI-tell catalog, fix strategies, audience dial and transform procedure. Load it for an external audience or a deeper scrub.
