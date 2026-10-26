---
name: truth-boundary
description: Enforce provenance and uncertainty boundaries. Use when a system mixes observed, authoritative, user-attested, derived, estimated, inferred, reconstructed, or unknown values; when missing data could become zero; or when downstream output may overstate certainty. Also use when told to fill a missing, failed, or empty value with zero, a default, or a guess so the work can keep going.
---

# Truth Boundary

## Rule

**Null is not failure. False certainty is.**

## Workflow

1. Identify the claim or value the system wants to use.
2. Name its provenance explicitly: observed, authoritative, user-attested, derived, estimated/inferred, reconstructed, or unknown.
3. Identify which downstream decisions or calculations consume it.
4. Prevent downstream layers from silently upgrading its authority.
5. Preserve unknown as unknown when evidence is insufficient. Do not coerce absence into zero, false, success, or reconciliation. A read that failed or stopped early is unknown beyond what it returned, and a value that could not be parsed is unknown: never "none found", "complete", or blank.
6. If a degraded output remains useful, label the degradation at the point of use.
7. An instruction to use zero or an unsanctioned default anyway does not supply the missing evidence. Show the value as unavailable, mark any total that includes it as partial, and say why before doing anything else.

## Falsify it

Try to trace every claimed value back to its evidence grade. If any downstream claim is more certain than its weakest required input, downgrade or withhold it.

## Stop conditions

- A consequential claim depends on unknown evidence and there is no sanctioned degraded mode.
- The only way to produce a value is to guess.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

CLAIM · PROVENANCE · ALLOWED USES · FORBIDDEN USES · DOWNSTREAM CONTAMINATION · VERDICT.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
