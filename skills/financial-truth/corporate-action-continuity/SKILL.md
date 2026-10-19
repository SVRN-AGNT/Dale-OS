---
name: corporate-action-continuity
description: Preserve economic continuity through splits, reverse splits, symbol changes, and other supported structural corporate actions. Use when an asset identity or share count changes but basis, lots, holding period, cash, or realized P&L may need to remain continuous. Also use when told to treat a renamed, converted, or merged holding as a new purchase with fresh basis.
---

# Corporate Action Continuity

## Rule

**The identity changed. The economics may not have.**

## Workflow

1. Classify the action as structural or economically realizational before changing any ledger behavior. An instruction to reset basis does not make the action realizational; say what evidence would show a taxable disposal.
2. For supported splits/reverse splits, transform quantities by the ratio while preserving total basis and holding-period dates.
3. For supported symbol changes, resolve the ticker chain without rewriting historical trades or creating duplicate active positions.
4. Identify each instrument by a stable identifier, with its stated type as a check, never by its symbol alone or by the kind of account that holds it: one symbol can name different instruments. Keep the account in the position key, so the same instrument held in two accounts stays two positions.
5. Keep cash and realized P&L neutral unless the action explicitly includes cash/boot or a taxable realization.
6. Defer unsupported mergers, spin-offs, boot, cash-in-lieu, and complex reorganizations rather than approximating them.
7. Run continuity checks before and after: ownership, total basis, lots, holding period, cash, realized P&L.

## Falsify it

Try to prove the action is economically structural rather than a disposal or new purchase. If cash, basis, holding period, or realized P&L should change, the continuity rule may not apply.

## Stop conditions

- The action includes unsupported taxable components.
- Multiple live destination identities make the chain ambiguous.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

ACTION · STRUCTURAL/REALIZATIONAL · QUANTITY EFFECT · BASIS · HOLDING PERIOD · CASH/P&L · CONTINUITY VERDICT.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
