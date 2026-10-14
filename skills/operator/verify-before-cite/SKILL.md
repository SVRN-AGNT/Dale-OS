---
name: verify-before-cite
description: Live-verify work state before reporting or relying on it, and reconcile every place that state is recorded. Use before a status report, standup, handoff, or "what's open" answer; when a tracker, queue, memory note, or prior session says something is pending, merged, shipped, or blocked; after any merge, release, or promotion; or when records in two places disagree. Do not use to judge whether a claim about data or numbers is proven.
---

# Verify Before Cite

## Rule

**Memory is a lead, not a fact. Verify the item against its authority before you cite it, and correct the record where people actually read it.**

Work state lives in the systems that change it: the code host, the deploy log, the ledger. Notes, queues, and session memory are copies, and copies go stale silently. The failure is not bad reasoning; it is reporting a confident "still waiting on your merge" for something that merged yesterday.

## Workflow

1. **Name the authority for each item.** Merged lives on the code host. Deployed lives in the deploy system. Decided lives in the decision record. A tracker row, a memory note, and a person's "I believe" are all unverified until checked.
2. **Verify each cited item live, this session.** Check the specific item, not a summary of it. Integration is not production: "on the default branch" and "deployed" are different states.
3. **Sweep every location that records it.** From truth to belief: the live systems, then trackers and queues, then notes and memory, then what people have said. The same item must read the same state everywhere.
4. **Patch the canonical copy, not a side note.** When you learn that a record is wrong, correct the copy that agents and people actually read, in the same session. A correction written only in your own notes is recorded drift. If you cannot patch it, mark the record visibly as unpatched and make clearing that mark the next action.
5. **Sweep for dark work.** List branches with commits and no open PR, drafts with no tracker entry, and interrupted sessions' leftovers. Adopt each into tracked state or retire it explicitly.
6. **Stamp freshness.** Every cited state carries when and how it was verified. Treat open-state records as stale by default once a release or promotion has happened since they were written.
7. **Run it on a cadence, and always before reporting.** A sweep on a schedule self-heals the records; the verify-before-cite step before every report is the guarantee.

## Anti-patterns

- Citing the tracker as proof the work is done.
- Comparing commit counts between long-lived branches instead of comparing content.
- Fixing the vault, the notes, or your memory and leaving the canonical queue wrong. The next agent reads the queue.
- "As of my last check" with no date.

## Relationship

`truth-boundary` grades claims about data. `verify-before-cite` keeps claims about work state current. `loop-closure` decides what to do with the open items this sweep finds.

## Falsify it

Pick three items from your report and look each one up in its authority now. If any reads differently, the report was built from memory. Then search for one branch or draft that appears in no tracker; finding one means the sweep missed a location.

## Stop conditions

- The authority for an item cannot be reached.
- Two authorities disagree, for example the code host says merged and the deploy log has no release.

Report the item as unverified and name the disagreement. Never resolve it from memory.

## Output

ITEM · AUTHORITY · LIVE STATE (verified when) · RECORDS CHECKED · RECORDS PATCHED · UNPATCHED MARKS · DARK WORK FOUND.
