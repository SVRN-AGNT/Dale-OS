---
name: operator-ui-audit
description: Audit dense operational or financial UI before restyling or patching it. Use first when a dashboard, screen, or screenshot shows a wrong or confusing value, a hierarchy problem, or inconsistent modes, to decide whether source data, state, or presentation is responsible; or when asked to make an interface clearer while preserving workflows and data truth. Do not use once the cause is known to be a code defect behind the screen (use systemic-bug-instinct).
---

# Operator Ui Audit

## Rule

**A wrong value in the UI is usually a data problem wearing a costume.**

## Workflow

1. Separate correctness, information architecture, interaction, hierarchy, and styling findings.
2. For every wrong or inconsistent value, trace the data authority before proposing visual changes.
3. Check the screen in the context of its workflow: entry point, decision it supports, next action, and failure states.
4. Identify the top three changes by leverage, not the longest list of cosmetic issues.
5. Prefer shared primitives and existing design rules over bespoke decoration.
6. Preserve dense information when density is useful; improve hierarchy before removing data.

## Falsify it

Try to prove the problem is actually visual. Trace the displayed value and state to their authority first; if the underlying truth is wrong, do not call it a styling problem.

## Stop conditions

- The audit cannot determine whether a wrong value is a display issue or upstream data issue.
- A redesign would remove or weaken a required operational workflow.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

VERDICT · DATA TRUTH · WORKFLOW · HIERARCHY · TOP 3 CHANGES · DO-NOT-CHANGE · VERIFICATION.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
