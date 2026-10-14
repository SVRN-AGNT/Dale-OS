# The Reviewer Nobody Called

## Failure
A repository had a second, independent reviewer from a different vendor. It reviewed a change only when the author's session posted a request comment on the PR. The process document said this reviewer's clearance was required before a change was marked ready. On a busy day, several sessions opened and merged changes, some of them to merge tooling. None posted the request, so the reviewer saw none of the changes. Nothing failed and nothing warned. The merger never checked for the clearance, so the "required" review was optional in practice.

The same audit found a sibling: a check described as blocking that the merger waited for but could not be stopped by.

## Root mechanism
A gate triggered by the party it judges, plus a requirement stated in prose that no mechanism enforced. Silence looked the same as a clean review.

## Rule paid for
The reviewed party must not be the one who summons the review. Trigger review mechanically on every change in the lane, check that the verdict exists for the current head before the change counts as reviewed, and make anything called blocking actually able to block.

## Skills
`shipping-lanes` · `reachability-proof` · `merge-authority`
