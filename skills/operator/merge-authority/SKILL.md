---
name: merge-authority
description: Decide whether an automated merge, promotion, or approval is actually authorised. Use when an agent or bot will merge, auto-merge, promote, or release; when a passing check is being treated as final approval; when an approval or green result is reused after the branch or its base moved; when a change's risk is self-declared; or when an approval comes from an account the automation controls. Do not use to judge what a diff contains (use diff-scope-audit), to check whether something already merged (use verify-before-cite), or to judge a finished-looking result (use false-competence-check).
---

# Merge Authority

## Rule

**Evidence authorises only the exact tree it judged. Permission cannot come from the party asking for it.**

An automated merge is safe when nothing the requester controls can grant the permission. The usual failure is quiet: a check result from an older tree, a risk level the author typed, a sign-off from an account the bot can drive.

## Workflow

1. **Tie evidence to the tree that will land.** A check or review describes one specific combination of change and base. A new commit on the branch invalidates it. So does movement of the base, because the combined result has never been tested. Re-test on the current base, or use a merge queue that tests the exact result before landing it.
2. **Classify risk from the change itself.** Decide sensitivity from what the change touches, such as authentication and permissions, the checks that enforce them, data schema, release tooling, or anything that moves money. Ignore any risk level the author asserts: the author most likely to underrate a change is also the one least likely to label it. When a file is moved, renamed, or deleted, judge both its old and new location, because moving something out of a sensitive area is itself a sensitive change.
3. **Apply the rule as it stood before the change.** The policy that decides whether review is needed is read from the target branch. Otherwise a change could relax the policy that governs it.
4. **Require an independent approver for sensitive changes.** An approval counts only if it comes from someone the automation cannot impersonate. If no such approver exists, sensitive changes stop and a person lands them. Name this honestly as a stop, not as a pending approval nobody can give. A narrower substitute is a clearance from a reviewer of a different vendor, re-derived from that reviewer's own record at the moment of merge. Use it only with a written threat model that says who could still forge the evidence.
5. **Treat unknowns as risky.** If the list of changed files or the policy cannot be read, the change has not been assessed, and it does not merge.
6. **Know who lands changes.** Whether that is one controller, a merge queue, or a single maintainer, name it, and keep workers from merging around it.

## Anti-patterns

- A passing build accepted as approval for changes no test can judge, such as permission logic.
- An approval carried over after new commits or a moved base.
- A bot's sign-off satisfying a gate meant for a human.

## Relationship

`protected-boundary` decides when an agent must stop and ask. `risk-kernel` builds autonomy limits into the system itself; this skill applies the same idea to the merge step. `diff-scope-audit` judges the diff and the words used to report it. `verify-before-cite` checks the state afterwards.

## Falsify it

Add a commit after the last passing run and see whether the merge is still allowed. Advance the base without touching the branch and ask the same question. Label a permissions change "low risk" and see whether the decision changes. Edit the review policy inside the change and see which version is applied. Any success means the authority can be forged.

## Stop conditions

- A sensitive change has no approver the automation cannot impersonate, and no second-vendor clearance re-derived at merge time under a written threat model.
- The tree that would land differs from the tree that was tested.
- Landing the change would also release to production, and that step belongs to a person.

## Output

TREE TESTED (head + base) · TREE THAT WILL LAND · DERIVED RISK (which paths) · POLICY SOURCE · APPROVER INDEPENDENCE · DECISION (merge / stop / person).
