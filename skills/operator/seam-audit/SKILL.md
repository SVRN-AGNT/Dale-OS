---
name: seam-audit
description: Audit the boundary where two components represent the same concept, because each side can pass its own tests while the combined system is wrong. Use when a value looks coherent but is wrong, when a projection or compatibility view stands in for a full record, when sync or merge involves deletes, when status codes or result shapes cross a boundary, or when "unknown" may become zero, false, or success as it crosses between two components. Do not use for a defect inside one component (use systemic-bug-instinct), for grading one claim's certainty (use truth-boundary), or for a financial repair's preview and commit (use ledger-repair).
---

# Seam Audit

## Rule

**Each side can be right while the system is wrong. Audit the join, not just the parts.**

Most dangerous defects produce values that look coherent. They live where two representations of one idea meet: a reader and a writer, a preview and a commit, a list view and the full record, two devices merging. Local tests pass on both sides because each side is internally consistent.

## Workflow

1. **Name the concept and every place it is represented.** List each component that holds, reads, writes, or displays it.
2. **Ask the seam questions for each pair:**
   - **Definition.** Do both sides mean the same thing by the word, such as "unverified", "deleted", "complete", "available"?
   - **Shape.** Does a result field read on one side exist under that name on the other? A success flag spelled differently reads as failure, or as success, by accident.
   - **Projection.** Does a summary or list view drop fields that carry the meaning, and does anything downstream treat it as the full record?
   - **Preview and commit.** Does the dry run check the same conditions as the real write?
   - **Clocks.** Are event time, recorded time, settlement time, and effective time being collapsed into one?
   - **Lifecycle.** Does a delete stay deleted under merge, replay, or sync from another device?
   - **Grade.** Does an evidence or confidence level mean the same thing to the retriever, the scorer, the display, and the writer?
   - **Unknown.** Is "unknown" or "not available" turned into 0, false, empty, or success anywhere along the path?
3. **Force the two sides to meet.** Drive real inputs through both components together, rather than testing each with mocks of the other. Record CONTROL (expected behavior), MUTATION (the condition under test), RESTORE (back to control), and the outputs, as in `swarm` audit-graph Phase B.
4. **Fix at the shared definition.** Route both sides through one canonical definition, shape, or clock, rather than patching the side where the symptom appeared.
5. **Pin the seam.** Add a test that exercises both sides together and fails if they diverge again.

## Anti-patterns

- Fixing the display because that is where the wrong number showed up.
- Two tests, one per side, each mocking the other.
- A second, simpler checker written for one side that drifts from the real one.

## Relationship

`systemic-bug-instinct` owns the diagnosis; `seam-audit` is the checklist for where its blast-radius search looks. `truth-boundary` grades a single claim; this checks that the grade survives the crossing. The audit-graph topology in `swarm` scales this to many seams at once.

## Falsify it

For each pair, construct one input where the two sides should disagree if the seam were broken, such as a deleted record from another device, a withheld value, or a dry run of a write that should be refused. Run it through both together. If you cannot construct such an input, you have not identified the seam yet.

## Stop conditions

- The canonical definition is contested and no authority has decided it.
- Forcing the sides together would write to real data.

## Output

CONCEPT · REPRESENTATIONS · SEAM QUESTIONS FAILED · JOINT TEST (CONTROL, MUTATION, RESTORE, outputs) · CANONICAL FIX LOCUS · PINNING TEST.
