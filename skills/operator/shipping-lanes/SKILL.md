---
name: shipping-lanes
description: Design, run, or adopt a pipeline in which agent-written changes are reviewed and merged without a person in the routine loop, with review and landing matched to each change's risk. Use when setting up or changing how PRs get reviewed and merged by agents; when every change waits on one person, or none gets reviewed; when a reviewer is only reached if the author asks for it; when docs and permission changes take the same path; or when bringing a new repository onto the shared shipping system. Do not use to decide whether one specific merge is authorised (use merge-authority), to judge a finished-looking result (use false-competence-check), or to prove a single guard is reached (use reachability-proof).
---

# Shipping Lanes

## Rule

**Risk picks the lane. The lane decides who judges and who lands. People keep only the steps that are theirs.**

A pipeline goes wrong in one of two directions. Either everything waits on one person, so the person becomes the bottleneck and starts approving without reading. Or everything takes the same light path, so a permissions change lands on the same single review as a typo fix. Lanes fix both by spending scrutiny where a mistake is expensive and nowhere else.

## Workflow

1. **Derive the lane from the change.** Classify by the paths the change touches, including both sides of every rename. Use a fixed vocabulary: docs, ordinary, truth (money, sync, evidence, imports, identity), and held (workflows, access, billing, migrations, merge and release tooling, and authority sources such as instruction files and the skills that set gates). Docs excludes authority sources. Never read the lane from the author. If the list of changed files cannot be read, the change is held. Make the lane visible where people look: a label and title prefix on high-stakes changes, and a fixed marker line at the end of every message that mentions one.
2. **Give every lane an independent judge.** The reviewer runs in a fresh context and loads its prompt and workflow from the base branch, so the change cannot edit its own judge. It reads the change without running it, and posts a verdict on the exact head commit. "Could not review" counts as not reviewed.
3. **Make the judge earn trust.** Correctness and stated requirements only. Each blocking finding quotes the line it is about. Re-review converges on an unchanged diff. A new reviewer reports without blocking until it clears a written bar for volume, precision, recall on planted defects, and stability. It loses blocking power automatically when it falls below that bar.
4. **Add a second vendor where mistakes are costly.** On truth and held lanes, a model from a different vendor must clear the change before it merges, so approval is never one model agreeing with itself. Ask it only once the first reviewer and CI are green on the head, so its limited budget is not spent on a change that is still moving. On the truth lane, give it a fixed timeout so a quiet reviewer cannot stall the line, and record when the timeout was used. Held changes get no timeout. A blocking ruling stops the merge, a push revokes every ruling, and the first reviewer's approval never replaces the second. Count each ruling as a round, and treat repeated rounds as a sign the change needs splitting. Ordinary work does not need it; demanding it everywhere makes the second opinion a rubber stamp.
5. **Never let the reviewed party summon the review.** A review that runs only when the author asks for it is optional. Trigger it mechanically, and check that it actually ran before the change counts as reviewed.
6. **Name one lander.** Only one automatic merger, such as a controller workflow or a merge queue, and nothing merges around it. Eligibility is mechanical: ready, required checks green on the exact tree, mergeable, dependencies in, no hold, and the lane's reviews present.
7. **Land held changes only on a second-vendor clearance for the exact head.** If no approver exists that the automation cannot impersonate, either a person lands a held change after that clearance, or the lander releases it only on that clearance, re-read from that reviewer's own comments and the head's checks just before the merge call, so a finding posted after the clearance still blocks. Never on a timeout. Say plainly that this is weaker than an independent person: anyone with write access could still forge evidence, and the gate's threat model must name that.
8. **Keep people on the irreversible and the authority-granting steps:** production releases, creating identities and secrets, reading live user data, and giving a reviewer blocking power. Take people off routine merges.
9. **Put limits in access, not prompts.** An agent that pushes gets its own identity with limits the platform enforces. Until then, it does not push.
10. **Measure the pipeline, not the mood.** Track time from ready to merged, CI runs and runner minutes per merge, escaped defects, and reviewer recall on replayed past defects. Roll back any change that speeds things up but lets more defects escape.

## Anti-patterns

- The same single review for a docs typo and a change to who may merge.
- A second reviewer that runs only when the author posts a request, so on a busy day nobody does.
- A process document that says a reviewer's clearance is required when nothing checks for it.
- An auto-fixer that pushes under a person's account, limited only by "never merge" in its prompt.
- Calling a held change "approved" because a bot account approved it.
- A reviewer promoted to blocking after a run of approvals, with no measured precision or recall.

## Relationship

`merge-authority` decides whether one specific merge is really authorised; this skill designs the lanes that decide who gives that authority. `risk-kernel` makes autonomy safe by construction; this skill applies it to the review and merge path. `completion-contract` keeps the worker from grading its own work. `reachability-proof` checks that each gate actually runs. The full operating model, adoption guide and templates are in `shipping/` at the repository root.

## Falsify it

Open a docs-only change and a change to merge tooling, and see whether they get the same reviewers and lander. Rename a file out of a held path, and see which lane applies. Edit the reviewer's prompt inside a PR, and see which prompt reviews that PR. Skip the second-vendor request on a truth change, and see whether anything notices. Push after an approval, and see whether the approval still counts. Any of these going unnoticed means the lanes are decoration.

## Stop conditions

- A held change has no approver the automation cannot impersonate, no person has been asked, and no gate re-derives a second-vendor verdict at merge time.
- The step would release to production, grant access, or read live user data.
- Giving the reviewer blocking power is proposed without measured precision and recall.

## Output

LANE (and the paths that set it) · MARKER (high stakes or ordinary) · JUDGES REQUIRED · JUDGES THAT RAN (on which head) · LANDER · HUMAN STEPS REMAINING · MEASURES (measured or expected).
