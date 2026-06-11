# Changelog

## [2.4.0] - 2026-06-11

### Added
- Element-interaction and measurement-integrity capture by default: --scope-page-contains/--scope-host flags applied as a dimensionFilter to every report; event-liveness in Step 3 (dead bindings plus zero-crossings); Step 5b reworked to drop the silent skip, always enumerate autotrack linkText/linkUrl and the scoped page set, and add element events to trends; friction pass over event names and linkText; element-instrumentation and a new Measurement Integrity section promoted to REQUIRED; performance-profile schema_version 2.3. [audit-skills-interaction-measurement-capture]
