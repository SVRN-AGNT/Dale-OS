---
name: latest-authority
description: Preserve the latest explicit human decision across agent, model, session, and worker handoffs. Use after a user answers a choice, grants or denies authority, sets a constraint, or resolves an ambiguity that future agents must not reopen without new conflicting evidence.
---

# Latest Authority

## Rule

**The human answered. Carry it forward.**

## Workflow

1. Capture the decision as a compact authority receipt immediately after it is made.
2. Record DECISION, AUTHORITY, SCOPE, CONSTRAINTS, and any action/merge disposition.
3. Carry the receipt into handoffs and new task contracts before re-auditing the question.
4. Do not re-ask the same decision because context was lost. A declined proposal stays declined when a later sync or import returns the same proposal within the decision's recorded scope, even under a new id or import time. A different effective date or period is a different proposal, and changed facts go to step 5.
5. If genuinely new conflicting evidence appears, surface both the receipt and the conflict. Let the human reconcile them; do not silently override either.

## Falsify it

Try to find genuinely newer conflicting evidence or a later human decision. If neither exists, the active receipt remains authoritative and the choice stays closed.

## Stop conditions

- A later instruction explicitly supersedes the receipt.
- New evidence materially changes the premise the human decided on.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

LATEST AUTHORITY RECEIPT with decision, scope, constraints, status, and reopen condition.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
