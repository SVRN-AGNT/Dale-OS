---
name: reachability-proof
description: Prove that a fix, guard, test, job, or check is reached by the path that matters, enforced by a gate that actually runs, and loud when it stops working. Use before claiming a fix, regression test, CI guard, ratchet, scheduled job, hook, or monitor is done; when a check board is empty or stale; when tests are green but the feature may be dead; or when a checker reports "0 findings". Do not use for exploratory prototypes where no correctness claim is being made.
---

# Reachability Proof

## Rule

**A guard nothing reaches is not a guard. Silence is not evidence of health.**

Correctness is three legs, not one: the code is right, the code is **reached** by the path that matters, and its failure would be **visible**. Ship any one without the other two and you have shipped an illusion.

## Workflow

Answer each question with verification, not prose.

1. **Reached — "What calls this in production?"** Trace from the real entry point (app entry, route, schedule, CI trigger, hook registration), not from the file that declares it. An import only tests reach is not reached. A job that is correct but never scheduled is not running.
2. **Enforced — "What blocks a merge that breaks it?"** Name the command that runs the guard and show that the gate invokes that command. A test in a tier CI never runs is documentation. Wiring the guard into the gate is part of writing the guard, not a follow-up.
3. **Falsifiable — "Would this fail if the feature were dead?"** A causal assertion must be unsatisfiable by the null case. `after >= before` passes when the pipeline ignores its input entirely. Assert the difference first, use a strict inequality, or assert a delta threshold. Break the fix and watch the test go red; commit the intended state before you do, so restoring it is safe.
4. **Visible — "What does absence look like?"** State how a silent no-op would present. If the answer is "identical to success", build the signal: a run ledger, a dead-man's switch, a parser-sanity assertion that fails when the checker stops finding anything.
5. **Report the legs honestly.** When verification is partial, name the missing leg instead of saying "verified".

## Anti-patterns

- asserting that a module exists instead of that it behaves (existence tests can pin dead code in place);
- adding a guard without adding it to a gate;
- reading an empty or stale check board as a passing one;
- "tests pass" when the relevant test never executed the relevant path;
- "0 findings" from a checker that could not have found anything;
- relaxing a ratchet to make a red tier green, or adding a cheaper second checker that will drift from the real one.

## Relationship

`systemic-bug-instinct` asks what else shares the mechanism: blast radius across space. This skill asks whether anything reaches the fix and whether you would know if it stopped: blast radius across execution. A complete post-fix audit covers both.

## Falsify it

Try to make the claim fail. Remove the call site and see whether anything goes red. Delete the fix and see whether the test fails. Make the checker's input empty and see whether it still passes. Confirm the CI run you are citing exists and matches the current head commit. If none of these can be done, the leg is unproven; say so.

## Stop conditions

- The only available verification would exercise a path other than the one the claim is about.
- Proving a leg requires production access or authority the task was not granted.

A stop is an output. Name the unproven leg and what would prove it.

## Output

REACHED (entry point → path) · ENFORCED (gate → command → guard) · FALSIFIABLE (null-case check, break-the-fix result) · VISIBLE (absence signal) · MISSING LEGS · REQUIRED LANGUAGE (for example: "correct and reached, but no gate enforces it").
