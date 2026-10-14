---
name: completion-contract
description: Decide whether an autonomous or long-running agent task is actually complete, using explicit obligations instead of the worker's word. Use when designing or running an agent loop, autorun, overnight job, or multi-iteration task; when an agent reports "done", "all set", or "finished"; when a loop keeps running without retiring anything; or when retries are exhausted. Do not use to verify one specific fix or guard (use reachability-proof) or to audit a backlog (use loop-closure).
---

# Completion Contract

## Rule

**A model saying "done" is not completion. The worker cannot certify its own run closed.**

Long autonomous runs fail in a predictable way: the worker grows confident before the work is finished, and its own summary becomes the evidence. Completion has to be adjudicated by something other than the worker, against obligations written down before the work started.

## Workflow

1. **Write the obligations first.** Before the run starts, list what "complete" requires, for example: verification actually executed · attributable failures resolved or truthfully classified · branch, PR, and head verified live · runtime proof where the task needs it · integration state reconciled · records written back · every spawned finding retired, routed, or explicitly handed to a person.
2. **Make every obligation explicit.** Each must be answered `true`. An unanswered obligation fails. An obligation can be waived only by an explicit declaration made up front, such as "no runtime proof required", never by silence.
3. **Separate the worker from the judge.** The worker produces a completion packet with evidence. A different leg (a reviewer, a checker, a person) issues the verdict. The worker has no path to the complete state at all.
4. **Use a closed verdict set.** For example: continue · final-verify · complete · needs-person · blocked · stalled · retryable-failure · cancelled. Prose rides alongside as rationale and never becomes a state. An unrecognised verdict is a failure, never a guess and never "complete".
5. **Prefer machine sources over narrative.** Where a system can answer (PR state, check results, mergeability), the judge reads the system. The worker's description of that state does not satisfy the obligation.
6. **Bound retries and latch exhaustion.** When the retry budget runs out the run goes to stalled, never complete, and a later success does not clear the latch.
7. **Detect no-progress.** Fingerprint each iteration from the objective, the outstanding obligations, and the evidence. Reordering is not progress; retiring an obligation is. A short cycle that retires nothing is oscillation, so stop it.
8. **Make side states explicit.** Needs-person, blocked, and stalled are named states that need an outside act to leave. A leg that "helpfully" resumes one has authorised itself past the gate that parked it.

## Anti-patterns

- The worker's final message used as the completion record.
- "All tests pass" when no test ran this session.
- A loop that ends because it ran out of turns, reported as finished.
- Follow-up findings dropped silently because they were outside the original task.

## Relationship

`reachability-proof` proves one guard or fix is real. `loop-closure` retires open work across a backlog. `completion-contract` decides when one run may close. `swarm` designs the workers; this decides when they are done.

## Falsify it

Delete one obligation's evidence from a completion packet and submit it. If the run still closes, the contract is narrative. Then feed the judge an unknown verdict string and confirm it fails rather than completes.

## Stop conditions

- An obligation cannot be checked by anyone other than the worker.
- The run needs an action only a person can authorise.

Report the run as not complete, name the unmet obligation, and park it in a named side state.

## Output

VERDICT · OBLIGATIONS (each true / false / waived-explicitly) · EVIDENCE SOURCE (machine or narrative) · RETRIES USED · PROGRESS FINGERPRINT · SPAWNED FINDINGS AND THEIR ROUTE.
