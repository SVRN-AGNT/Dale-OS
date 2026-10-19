---
name: ledger-repair
description: Design and review safe repairs to financial ledgers. Use when deleting, correcting, reclassifying, reversing, or rebuilding trades, cash events, lots, positions, flows, or accounting records and the operator needs an economic dry run, shared preflight, atomic commit plan, rollback, and audit receipt.
---

# Ledger Repair

## Rule

**Preview the economics before changing the books.**

## Workflow

1. Build a read-only preview from the same canonical logic the commit path would use.
2. Show before→after effects for records, shares, cash, basis, realized P&L, external flows, and any derived snapshots.
3. Run invariant checks on the projected state. A repair that creates a new inconsistency is blocked even if it removes the original bad row.
4. Require the commit path to use the same preflight definitions as the preview path.
5. For future write-capable implementations: commit atomically or roll back; write the audit receipt only after success; reconcile after commit.
6. Never broaden a repair from the named economic episode without exposing the additional rows separately in preview.
7. When a writer stops producing a kind of record, show the records it already wrote separately in preview, and propose reversing or superseding the ones the new rule rejects, never deleting them.

## Deterministic companion

When structured JSON is available, prefer `scripts/ledger_delta.py` for the mechanical check. Treat its output as a constraint on reasoning, not as permission to invent missing classifications. Run it from the skill directory with JSON on stdin.
Read `references/DETERMINISTIC_INPUT.md` when you need the input contract.

## Falsify it

Try to show that preview and commit produce the same economic delta from the same inputs. If they use different rules, the repair is not safe enough to execute.

## Stop conditions

- Preview and commit use different eligibility rules.
- Projected state creates unsupported shares, unexplained cash, or another blocked invariant.
- Human authority for the consequential write is missing.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

PROPOSED REPAIR · BEFORE/AFTER ECONOMICS · INVARIANTS · VERDICT · AUTHORITY REQUIRED · AUDIT RECEIPT SHAPE.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
