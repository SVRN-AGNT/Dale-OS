---
name: model-sanity
description: Adversarially validate financial models and forecasts before trusting their outputs. Use for DCFs, three-statement models, portfolio scenarios, probability trees, TAM/share models, unit economics, capital allocation models, or spreadsheets where formulas can be internally consistent but economically impossible.
---

# Model Sanity

## Rule

**A plausible model is not automatically a valid model.**

## Workflow

1. State the model's key claim and what must be true for it to hold.
2. Check units, signs, periods, scale and compounding boundaries before interpreting results. A series' name does not say what quantity it holds. Before reading a direction, say whether the claim is about a level, a rate, or a change in a rate, say which one the series holds, and derive the claim's quantity from the series first. A value's size may raise a doubt about its scale but never settles it: take the scale from what its source states, and when it states none, treat the scale as ambiguous.
3. Test accounting identities and probability constraints mechanically where possible.
4. Run monotonicity/sensitivity checks: changing an input in the expected direction should not produce a perverse result without an explanation.
5. Check scenario ordering, impossible shares/ratios, double counting, terminal-value dominance, and hidden circularity.
6. Recalculate at least one important output independently from the model's presentation path.
7. Label assumption risk separately from arithmetic correctness.

## Deterministic companion

When structured JSON is available, prefer `scripts/model_sanity.py` for the mechanical check. Treat its output as a constraint on reasoning, not as permission to invent missing classifications. Run it from the skill directory with JSON on stdin.
Read `references/DETERMINISTIC_INPUT.md` when you need the input contract.

## Falsify it

Try to break the model from identities, units, bounds, directionality, and independent recomputation. A plausible output does not pass if one hard invariant fails.

## Stop conditions

- Units or periods are ambiguous.
- A core identity fails.
- The model depends on an assumption that is impossible or internally contradictory.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

MODEL VERDICT · MECHANICAL CHECKS · ECONOMIC CHECKS · SENSITIVITIES · FAILED ASSUMPTIONS · INDEPENDENT RECALC · LIMITATIONS.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
