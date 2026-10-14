---
name: merge-authority
description: Decide whether an automated merge, promotion, or approval is actually authorised, and report its state in exact language. Use when an agent or bot will merge, auto-merge, promote, or release; when CI green is being treated as final approval; when an approval, review, or green check is reused after new commits; when risk is self-declared in a PR body; or when "merged", "deployed", "shipped", and "live" are being used interchangeably. Do not use to review the content of a diff (use diff-scope-audit).
---

# Merge Authority

## Rule

**Green on H authorises H, never a descendant of H. Authority comes from identity and evidence, not from the actor's own claim.**

Automated merging is safe only when the thing that grants permission cannot be supplied by the thing asking for it. Most failures are an authority quietly granted to the wrong party: a stale green, a self-declared risk level, an approval from an account the agent can act as.

## Workflow

1. **Bind every approval to an exact head.** Checks, reviews, and promotion evidence name the commit they judged. Any new commit revokes them until that commit earns its own. A green from an older SHA is evidence about a different tree.
2. **Derive risk from what changed, never from what the author says.** Classify high-risk scope by the paths and kinds of change (access control, the gates that enforce it, schema migrations, deploy and merge machinery, money). A risk label in the PR body repeats the failure it is meant to prevent, because the author who misjudges the blast radius is the one who omits the label. Count both sides of a rename.
3. **Judge each change against the already-merged rule.** The policy that decides whether a change needs review is read from the base branch, not from the change. A PR must not be able to widen the rule that judges it.
4. **Require a second identity for held scope.** An approval counts only from an identity the automation cannot act as. If no such identity exists, held scope is a stop, and a person merges it by hand. Do not call that stop "approval required" when nobody can supply the approval.
5. **Fail closed.** If the changed files cannot be read, risk was not assessed, and that never merges like "no risk".
6. **Keep one terminal merger.** One controller orders and merges. Workers build and hand off; they do not merge, update branches, or arbitrate between competing changes.
7. **Report state in exact tiers.** Implemented · pushed · PR open · merged to the integration branch · deployed to production. Merged is not deployed, and a merge to an integration branch is not a release.

## Anti-patterns

- Treating "CI green" as sufficient authority for changes CI cannot judge, such as authorisation logic.
- Re-using a review after a force-push or a new commit.
- A bot's approval satisfying a gate labelled "owner review".
- Saying "it's live" because the PR merged.

## Relationship

`protected-boundary` decides when an agent must stop. `merge-authority` decides when an automated merge may proceed and how to describe what happened. `diff-scope-audit` judges what the diff contains; this judges who may land it.

## Falsify it

Push a commit after the last green and check whether the merge is still allowed. Add a risk label claiming "low" to a change touching access control and check whether it changes the decision. Edit the review rule inside the PR itself and check which copy the merger reads. Any of these succeeding means the authority is forgeable.

## Stop conditions

- The change touches held scope and no independent reviewer identity exists.
- The head moved after the evidence was produced.
- The merge would also deploy to production and that step needs a person.

## Output

HEAD (exact SHA) · EVIDENCE BOUND TO HEAD · DERIVED RISK (paths) · RULE SOURCE (base branch) · REVIEWER IDENTITY · DECISION (merge / stop / person) · STATE TIER REPORTED.
