---
name: completion-contract
description: Decide whether an autonomous or long-running agent run is actually finished, using obligations set in advance instead of the agent's own account. Use when designing or running an agent loop, scheduled job, or multi-step autonomous task; when a run reports "done" or "all set"; when a loop keeps iterating without finishing anything; or when retries run out. Do not use to prove one fix is reached (use reachability-proof), to clear a backlog (use loop-closure), or to judge whether one piece of work is genuine (use false-competence-check).
---

# Completion Contract

## Rule

**"Done" is a verdict, not a report. The agent that did the work does not deliver it.**

Long autonomous runs drift toward confidence before the work is finished, and the agent's own summary quietly becomes the evidence. Finishing has to be judged against a list agreed before the run started, by something other than the worker.

## Workflow

1. **Agree the finish line up front.** Before the run, write what finished means for this job. Typical items: the checks actually ran · failures caused by the work are fixed or honestly labelled · the current state of the branch or output was looked up, not remembered · proof from the running system where the job needs it · related records updated · anything new the run discovered is closed, handed on, or flagged for a person.
2. **Every item needs an explicit yes.** A missing answer counts as no. An item may be dropped only by saying so at the start ("no runtime proof needed for this job"), never by leaving it out.
3. **Keep the judge separate from the worker.** The worker hands in its evidence; something else decides. In order of strength:
   1. a deterministic check or script;
   2. a separate reviewer that sees only the evidence, not the worker's reasoning (weaker, and say so);
   3. a person.

   A single agent working alone can only reach "ready for review", never "finished".
4. **Decide from a fixed set of outcomes.** For example: keep going · ready for review · finished · needs a person · blocked · stuck · failed, can retry · cancelled. Explanations ride alongside; they are never an outcome. Anything outside the set is treated as a failure, never as finished.
5. **Read systems, not stories.** Where a system can answer (did the checks pass, is it merged, does the file exist), the judge asks the system. The worker's description does not count.
6. **Cap retries and make running out stick.** When retries are used up the run is stuck, not finished. A later lucky pass does not undo that.
7. **Notice when nothing changes.** Compare each round by what is still open and what evidence exists. Shuffling the order is not progress; closing an item is. Rounds that close nothing mean the run is stuck.
8. **Parked runs stay parked.** "Needs a person", "blocked" and "stuck" are left only by an outside act. A worker that resumes one on its own has skipped the gate.

## Anti-patterns

- The worker's last message used as the record of completion.
- "Tests pass" when none ran in this run.
- A run that stopped because it hit its turn limit, reported as finished.
- Discoveries outside the original task dropped without a word.

## Relationship

`reachability-proof` proves one fix or guard is real. `false-competence-check` tests whether a result is genuine. `loop-closure` clears a backlog. `completion-contract` decides when one run may end. `swarm` designs the workers; this decides when they are done.

## Falsify it

Remove the evidence for one item and submit the rest. If the run still ends as finished, the contract is only words. Give the judge an outcome outside the fixed set and confirm it fails instead of finishing.

## Stop conditions

- No judge other than the worker is available: end at "ready for review" or "needs a person".
- The run needs an action only a person can authorise.

## Output

OUTCOME · FINISH LINE (each item: yes / no / dropped up front) · JUDGE (script / separate reviewer / person) · EVIDENCE SOURCE (system or narrative) · RETRIES USED · PROGRESS SINCE LAST ROUND · DISCOVERIES AND WHERE THEY WENT.
