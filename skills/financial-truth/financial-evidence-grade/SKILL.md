---
name: financial-evidence-grade
description: Grade financial evidence by provenance and constrain what each grade is allowed to drive. Use when financial data comes from statements, filings, user input, deterministic derivation, vendor estimates, LLM research, reconstructed history, or missing sources. Do not use when the values are not financial (use truth-boundary).
---

# Financial Evidence Grade

## Rule

**An estimate is not an authority.**

## Workflow

1. Attach a provenance grade to each consequential input: OBSERVED, AUTHORITATIVE, USER_ATTESTED, DERIVED, ESTIMATED, RECONSTRUCTED, or UNKNOWN.
2. Record source id/date where available. Keep freshness separate from provenance.
3. Define allowed uses for the grade. Example: an estimate may inform research but may not silently alter tax basis.
4. Propagate the weakest material dependency into downstream readiness or caveats. A combined value is DERIVED, and no use is allowed for it that a material input's grade forbids: an ESTIMATED, RECONSTRUCTED or UNKNOWN material input keeps that grade's limits on the combined value. Its freshness is that of its oldest material input, never the newest. If any material input is unavailable, the combined value is partial or withheld, never complete. When the material inputs' as-of dates differ, the value has no single as-of date: label it mixed-date, show the oldest date and which input it belongs to, and keep every input's date available. Present it as true on one date only when every material input is aligned to that date.
5. Never upgrade ESTIMATED to AUTHORITATIVE because deterministic math was applied afterward.
6. When a higher-grade source arrives, replace or supersede the lower-grade claim with an audit trail rather than erasing history.
7. Do not fill an unknown with a value that other evidence makes impossible, such as a different amount, date, or quantity for the same item. Report both values and their grades instead.

## Falsify it

Try to identify the weakest evidence supporting each downstream use. If an estimate, reconstruction, or model inference is being used as accounting authority, fail the use even if the number looks plausible.

## Stop conditions

- A consequential write depends only on estimated/inferred evidence.
- Source provenance is missing for a value presented as authoritative.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

VALUE/CLAIM · GRADE · SOURCE/FRESHNESS · ALLOWED USES · DOWNSTREAM EFFECT · SUPERSESSION STATUS.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
