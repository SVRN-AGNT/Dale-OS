---
name: close-the-books
description: Gate downstream financial analytics on the readiness of their required books. Use before publishing performance, attribution, tax, realized P&L, portfolio diagnostics, or model outputs when positions, cash, flows, lots, basis, corporate actions, or valuations may be incomplete, and when one unresolved domain prompts a request to block or allow every analytic at once.
---

# Close The Books

## Rule

**Do not analyze a book you have not actually closed.**

## Workflow

1. List the analytical output being requested and its required upstream domains.
2. Collect readiness states for positions, cash, trades, transfers, lots, basis, income/tax character, flows, corporate actions, and valuations as applicable.
3. Build a dependency map from each unresolved domain to the outputs it can contaminate.
4. Allow unaffected analytics to continue. Do not block an allocation view just because tax character is unresolved if tax character cannot affect allocation.
5. Withhold or degrade only the outputs whose required books are not ready. A request to switch every analytic off over-blocks: name which outputs could stay available and why, then follow the owner's decision.
6. Produce a close receipt that names what is safe, what is blocked, and the minimum evidence needed to reopen it.

## Deterministic companion

When structured JSON is available, prefer `scripts/close_books.py` for the mechanical check. Treat its output as a constraint on reasoning, not as permission to invent missing classifications. Run it from the skill directory with JSON on stdin.
Read `references/DETERMINISTIC_INPUT.md` when you need the input contract.

## Falsify it

Try to identify which analytics actually depend on each unresolved book. Block only contaminated outputs; if a clean analytic does not depend on the broken domain, it may still proceed.

## Stop conditions

- A requested output has a blocking unresolved dependency.
- The dependency map is unknown, so contamination cannot be bounded.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

BOOK CLOSE · DOMAIN STATES · SAFE ANALYTICS · WITHHELD ANALYTICS · BLOCKING DEPENDENCIES · MINIMUM NEXT EVIDENCE.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
