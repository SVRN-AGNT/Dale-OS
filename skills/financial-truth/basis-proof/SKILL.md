---
name: basis-proof
description: Prove cost basis and realized gain from replayable acquisition lots instead of treating missing basis as zero. Use for sells, disposals, FIFO/LIFO/specific-lot analysis, tax-lot verification, oversold positions, or realized P&L where the system must show which lots support the result.
---

# Basis Proof

## Rule

**No basis, no profit.**

## Workflow

1. Order economic events by the canonical economic date, not arbitrary import time.
2. Replay acquisitions and disposals under the lot method the account actually applied. If that method is unknown, do not assume one; stop when the choice would change the result, and pass `method` to the script explicitly rather than relying on its default.
3. For each disposal, show shares requested, shares supported, source lots, proven basis, and any unsupported remainder.
4. If shares sold exceed replayable shares, classify the disposal as unverified/oversold. Partial basis does not make the entire gain verified.
5. Never coerce missing basis to zero in realized-gain arithmetic.
6. Preserve holding-period provenance separately from basis if the dates needed for term are incomplete.

## Deterministic companion

When structured JSON is available, prefer `scripts/basis_proof.py` for the mechanical check. Treat its output as a constraint on reasoning, not as permission to invent missing classifications. Run it from the skill directory with JSON on stdin.
Read `references/DETERMINISTIC_INPUT.md` when you need the input contract.

## Falsify it

Try to replay the disposal against real acquisition lots. If sold quantity exceeds provable lots or basis is missing, realized gain is not proven.

## Stop conditions

- The lot method is unknown and would materially change the result.
- A disposal has unsupported quantity.
- Required acquisition dates or basis values are unknown.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

DISPOSAL · LOTS CONSUMED · SUPPORTED SHARES · PROVEN BASIS · REALIZED RESULT or WITHHELD · UNRESOLVED REMAINDER.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
