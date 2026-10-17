---
name: memory-promotion
description: Gate what an agent saves to durable memory and keep that memory small, current, and correct. Use when asked to remember, save, or record what was learned; when a session or long autonomous run is wrapping up; when an agent is about to store a lesson, rule, preference, or pattern; when memory files contradict each other or the repo; or when a memory store keeps growing. Do not use for project documentation, decision records, or task tracking.
---

# Memory Promotion

## Rule

**The inbox can be messy. Memory cannot be. Remember less, better.**

Durable memory steers every future session, so a wrong or noisy note is a bug that repeats. Keep four things apart: raw context, verified evidence, durable memory, and authorized action. Most of what an agent notices belongs in the first two.

## Workflow

1. **Route before you save.** A task belongs in the tracker. A choice belongs in the decision record. An outcome belongs in a report. Raw observations stay in the inbox. Only lessons that change future behaviour are candidates for memory.
2. **Pass the six-check promotion gate.** Promote only if all six hold:
   1. **Durable:** useful beyond this one task.
   2. **Verified:** backed by evidence from the work or an explicit rule from the person.
   3. **Behaviour-changing:** it changes what the agent does next time.
   4. **Not already documented:** not obvious from the repo, the docs, or a decision record.
   5. **Specific:** actionable, not a platitude.
   6. **Corrects or confirms:** it fixes a mistake the agent made, or confirms an approach or a standing rule from the person that should keep being followed.
3. **Update before you add.** Search for an existing note that covers it and extend that one. One fact, one home.
4. **Write the why with the rule.** A rule without its reason gets misapplied at the edges. Record what happened, the rule, why it matters, and when it applies.
5. **Mark stated intent as stated.** A person's description of how something should work is not proof that it does. Save it with its source and a verify-before-asserting flag.
6. **Garbage-collect on every memory pass.** Delete or supersede anything this session proved wrong. Merge duplicates. A memory store that only grows is not being curated.
7. **Promote at the end, not mid-thought.** Memory passes happen after meaningful work, when the evidence is in, not every time something seems interesting.

## Anti-patterns

- Saving what the code, history, or docs already record.
- Saving secrets, credentials, or private data into memory at all.
- Treating a memory note as authority over a newer instruction or the live system.
- "Remember more" as a goal.

## Relationship

`latest-authority` carries a person's decisions forward. `memory-promotion` decides which lessons earn a permanent place. `verify-before-cite` treats memory as a lead to check, never as proof.

## Falsify it

Take the last five notes added and run each through the gate. Count how many fail a check. Then search the store for two notes that disagree, or one that the current code contradicts. Either finding means the gate or the collection is not running.

## Stop conditions

- The note would contain a credential or private data.
- The lesson contradicts a standing rule from the person: surface the conflict instead of saving over it.

## Output

CANDIDATE · ROUTE (memory or elsewhere) · GATE RESULT (six checks) · UPDATED OR NEW · SUPERSEDED OR DELETED · NET NOTES.
