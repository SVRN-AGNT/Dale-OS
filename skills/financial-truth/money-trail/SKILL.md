---
name: money-trail
description: Trace financial capital flows without inventing economic meaning. Use for deposits, withdrawals, transfers, cash adjustments, settlements, income, fees, taxes, portfolio funding, or unexplained balance changes when every dollar needs a source, destination, classification, and audit trail. Also use when told to classify a movement from its sign or amount alone.
---

# Money Trail

## Rule

**Every dollar gets a passport.**

## Workflow

1. Normalize each movement by date, account, amount, currency, source record, and stable id.
2. Separate arithmetic fact from economic classification. A positive sign does not prove "deposit," and a negative one does not prove "withdrawal." An instruction to classify by sign does not change that: say which record would settle it and leave the movement unclassified until it is checked.
3. Use explicit metadata and authoritative records first. Produce candidate matches only when evidence is incomplete.
4. A row that cancels, reverses, or returns another movement is matched to the movement it undoes and classified as its reversal, never as a new flow. Both rows stay in account reconciliation, where they net out. If the original cannot be found, mark the reversal unpaired.
5. For transfers, require both sides or mark the movement unpaired. Portfolio-level external flow for a proven internal transfer is zero.
6. Reconcile totals by account and portfolio. Surface unmatched or duplicate movements rather than absorbing them.
7. Produce a money-trail receipt showing source, destination, classification, evidence grade, and downstream effects.

## Deterministic companion

When structured JSON is available, prefer `scripts/money_trail.py` for the mechanical check. Treat its output as a constraint on reasoning, not as permission to invent missing classifications. Run it from the skill directory with JSON on stdin.
Read `references/DETERMINISTIC_INPUT.md` when you need the input contract.

## Falsify it

Try to pair and explain every movement without using sign alone as meaning. Any unmatched movement that could change external-flow treatment keeps the ledger unresolved.

## Stop conditions

- Economic classification is ambiguous and would change performance, tax, or cash truth.
- The same movement appears to be counted in two financial domains.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

MOVEMENT LEDGER · PAIRED/UNPAIRED · EXTERNAL FLOW EFFECT · CASH EFFECT · P&L EFFECT · UNRESOLVED ITEMS.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
