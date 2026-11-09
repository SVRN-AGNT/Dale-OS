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
6. Scope each record by the record it acts on. When a record that retracts or adjusts another lacks the field a filter selects on, such as the account, follow its reference to the original record and use that record's field, following further references until one carries it. A reference that is missing or unreadable, or that leads back to a record already visited, cannot be followed. When no reference can be followed, never apply its amount to any scope: mark every scope it could touch as partial, mark the record unpaired, and report why.
7. Take a rounding tolerance from the precision each number was printed with: half a unit in its last printed digit, counting trailing zeros (1.50 is to hundredths, 1.5 to tenths). Never hard-code a tolerance that fits only the first source a parser supported. When a source is known to strip or pad trailing zeros, use its documented precision instead. Unless the tolerance is strictly smaller than the smallest difference that matters, report the check as too weak to verify. Keep the original text beside the parsed number when a later check needs its precision.
8. Rank findings by contamination: wrong clean-looking numbers before malformed records that already fail visibly.
9. For ambiguous findings, report and withhold auto-repair. A warning may require human classification rather than an inferred fix.

## Falsify it

Try to construct the same reported state from the underlying records. If shares, basis, cash, dates, or P&L cannot all be true at once, schema validity does not rescue it.

## Stop conditions

- A proposed auto-fix requires guessing economic intent.
- Two modules use different definitions of the same financial concept and no authority is established.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

INTEGRITY VERDICT · BLOCKERS · WARNINGS · CONTAMINATED OUTPUTS · CANONICAL DEFINITIONS USED · NEXT EVIDENCE.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
