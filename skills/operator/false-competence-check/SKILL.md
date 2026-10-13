---
name: false-competence-check
description: Check finished-looking agent work against the failure modes that look like competence but are not. Use before declaring a fix done, before opening or approving a PR, when a change was fast and confident, when tests are green on the first try, after a rename, sweep, or cleanup, or when reviewing another agent's "done" claim. Do not use as a substitute for the task's own acceptance criteria.
---

# False Competence Check

## Rule

**The most expensive mistakes look like good work.**

Decisiveness, speed, cleanup, diligence, and confidence each have a counterfeit. The counterfeit passes casual review because it has the shape of the real thing.

## The counterfeits

| Looks like | Actually | Counter-procedure |
|---|---|---|
| Decisiveness | Implementing from stale premises | A prior audit is a hypothesis. Re-locate every symbol by content before building on it. |
| Speed | A shallow search-based fix | A rename searches the entire file, including templates. Claims about large files need uncapped searches and reading every hit. |
| A quick win | A visual fix that dodges the data | Identify the mechanism (paint order, clipping, scale, data truth) before choosing the fix class. A wrong number is withheld or labelled, never dressed. |
| Craftsmanship | A broad refactor disguised as cleanup | Scope out adjacent ugliness. Use anchored edits and verify with counts and a parse. A partial sweep is worse than none. |
| Diligence | Tests that bless the bug | Break the fix and watch the test fail. When a test encodes current behaviour, ask whether that behaviour is the bug. |
| Generosity | A PR with hidden unrelated diffs | Diff from the merge base. Every hunk traces to scope-in; incidental fixes get their own commit and a line in the report. |
| Confidence | False verification | Verify in the environment class where the code runs. Compare suite results against a clean tree. Count deliverables explicitly; search your own diff for placeholders. |
| Completeness | One instance fixed, pattern not hunted | Search every surface that reads the same data or renders the same pattern before declaring done. |
| Progress | Fixing the wrong link in the chain | Trace the whole pipeline first. When a feature yields nothing, check the wiring before the producer. |
| Finished | A code fix presented as data repair | Corrected code does not repair rows it already wrote. Data repair is a separate, dry-run-first, owner-gated path. |
| Defensiveness | Safety relief keyed to a label | Key relief to the degraded condition itself and test the success-with-degraded-inputs path. |
| Validation | Model-generated values passing value-blind guards | Overwrite system-owned fields at the trusted boundary. Validate claimed values against the canonical source. Print "unavailable", never a synthetic zero. |
| Consistency | Grandfathered violations reused as precedent | Ratchets only go down. New code meets the current standard even inside old files. |

## Workflow

1. Name which counterfeit your current work most resembles.
2. Run the one additional check that would falsify the resemblance.
3. Report the check and its result, not the reassurance.

## Falsify it

Ask: "Which of these does my diff most resemble, and what single check would prove it is not that?" If you cannot name the check, you have not ruled it out.

## Stop conditions

- The falsifying check requires access or authority the task does not have.
- The check fails and fixing it would broaden scope beyond the charter.

Report the resemblance and the blocked check rather than claiming done.

## Output

CLOSEST COUNTERFEIT · FALSIFYING CHECK · RESULT · RESIDUAL RISK.
