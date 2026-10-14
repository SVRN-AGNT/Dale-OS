---
name: accounting-integrity
description: Test whether financially well-formed records are economically coherent. Use on trade ledgers, cash histories, lot records, reconciliations, portfolio imports, or financial state where schemas pass but realized P&L, shares, basis, dates, flows, or account state may still be wrong.
---

# Accounting Integrity

## Rule

**Well-formed data can still lie.**

## Workflow

1. Validate shape first, then test meaning. Do not confuse schema validity with economic validity.
2. Check cross-record invariants: acquisition before disposal, no unsupported shares, duplicate economic events, mirrored cash/flow relationships, corporate-action continuity, and canonical-vs-mirror agreement.
3. Reuse canonical definitions instead of restating what "unverified," "cash movement," or another financial concept means.
4. Check every aggregate over values that can be withheld. A withheld input is never silently zeroed or dropped from any aggregate, whether a sum, an average, or an extremum. Count withheld contributions and report the result as partial, or fall back to a complete source and label it. When a fallback chain exists, withhold every tier computed over the same incomplete set together; withholding only the first tier promotes the next understated one.
5. A field named for a quantity holds that quantity or nothing, never a substitute.
6. Rank findings by contamination: wrong clean-looking numbers before malformed records that already fail visibly.
7. For ambiguous findings, report and withhold auto-repair. A warning may require human classification rather than an inferred fix.

## Falsify it

Try to construct the same reported state from the underlying records. If shares, basis, cash, dates, or P&L cannot all be true at once, schema validity does not rescue it.

## Stop conditions

- A proposed auto-fix requires guessing economic intent.
- Two modules use different definitions of the same financial concept and no authority is established.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

INTEGRITY VERDICT · BLOCKERS · WARNINGS · CONTAMINATED OUTPUTS · CANONICAL DEFINITIONS USED · NEXT EVIDENCE.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
