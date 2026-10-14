# HANDOFF comment for the second-vendor reviewer

Post this as a PR comment on every PR, after the Agent Review verdict is in, and mark the PR ready only after a `CLEAR` on its current head. (Narrowing this to L2 and L3 is an owner decision; in the reference repo it is pending.) The second reviewer is a model from a different vendor. Its reply is evidence for a person or the lander; it never merges anything.

```text
HANDOFF: second-vendor review requested

PR: #<number>   Head: <full sha>   Base: <branch> @ <sha>
Lane: <L0 | L1 | L2 | L3>, derived from: <the paths that set the lane>

Objective: <one sentence on what the change must achieve>
Scope IN: <what it changes>
Scope OUT: <what it deliberately does not change>

Agent Review: <APPROVE | REQUEST_CHANGES> on <sha>; findings addressed: <list or "none">
Verification run: <commands and results, or the check names that are green on this head>
Known unknowns: <what was not verified, and why>

Please review for correctness and authority only. Quote the line for any blocking finding.
Reply CLEAR, CORRECT with blocking findings, or HOLD, for head <sha>.
```

A reply covers only the head it names. A push after the reply means asking again.

The reviewer answers with one of three rulings: `CLEAR`, `CORRECT` (blocking findings), or `HOLD`. A held PR may be hand-merged only after `CLEAR` on its current head, or after 2 hours with no ruling. `CORRECT` or `HOLD` blocks the merge. Only the owner naming that specific PR waives the wait.
