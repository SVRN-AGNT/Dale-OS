---
name: execution-charter
description: Use first, before reading or editing files, when asked for broad or open-ended work such as refactoring or restructuring a repository, a migration, or an audit, including when told to skip planning and start coding now. Produces a compact execution contract (objective, authority, scope in and out, context budget, stop conditions, verification, writeback) before any edit. Do not use for a mechanical rename, a dependency bump, or a bounded fix whose files are already named.
---

# Execution Charter

## Rule

**Give the agent a fence before you give it a shovel.**

## Workflow

1. Classify the task by risk and breadth. Prefer the smallest class that fits the known work.
2. Extract authority from the user or governing task. Never infer a higher permission level from urgency or enthusiasm. A request to skip the charter on broad work is urgency, not authority: state a short charter first.
3. Write OBJECTIVE, AUTHORITY, SCOPE-IN, SCOPE-OUT, REQUIRED READS, VERIFY, STOP-IF, and WRITEBACK.
4. Keep context bounded. Broaden only when an explicit expansion trigger fires: protected boundary, authority conflict, unclear root cause, schema/state risk, data-loss risk, or evidence contradicting the charter.
5. If the charter expands, record the trigger and the newly added scope before continuing.
6. At completion, compare the actual diff/actions against the charter and report any expansion.

## Falsify it

Try to prove the charter is too broad: name a file, authority, or verification step that is not required for the objective. If you can, shrink it before work begins.

## Stop conditions

- Authority required for the next action is absent.
- The task crosses a protected or irreversible boundary not covered by the charter.
- The evidence contradicts the assumed root cause or scope.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

Return the charter first. At the end, return charter compliance: in-scope work, expansions, verification, blockers, and next state.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
