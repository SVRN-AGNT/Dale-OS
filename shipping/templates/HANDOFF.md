# HANDOFF comment for the second-vendor reviewer

Post this as a PR comment on every L2 (truth) or L3 (held) PR, after the Agent Review verdict is in, and mark the PR ready only after a `CLEAR` on its current head, or after 2 hours with no ruling (record it as "PM timeout"). An Agent Review approval never stands in for a CLEAR. The second reviewer is a model from a different vendor. Its reply is evidence for a person or the lander; it never merges anything.

The reply is automatic where the repository runs the shared PM caller ([`ci/README.md`](../../ci/README.md#the-pm-caller)). The comment must be posted through the `claude` app, start with `HANDOFF:` at byte zero, and name the current head as a full 40-character sha, or the PM skips it. Where the caller uses `provider: chatgpt` (Codex's own review on the ChatGPT plan, no API key), the comment must also carry `@codex review` on a line of its own: that line is what asks Codex, and the PM rules when Codex finishes the head.

With `provider: chatgpt` the PM reads only Codex's review of the diff, not the HANDOFF's text, so two lines are enough:

```text
HANDOFF: <full 40-character head sha>
@codex review
```

Before merging on a `provider: chatgpt` CLEAR, or calling its HANDOFF timed out, re-run the PM workflow by dispatch for that HANDOFF and its PR and wait for the run. A Codex finding posted inline after the CLEAR wakes nothing, and that run turns it into CORRECT. Only a run that concluded `success` and whose "Resolve the HANDOFF and its PR" step logged a notice naming the head counts: `the CLEAR on <head> still stands` before merging, or `Waiting on Codex's review of <head>` (or `Waiting on Codex's receipt for <head>`) before the timeout. Any other outcome does not count; fix the cause and dispatch again.

The longer form below is for `provider: api`, whose reviewer reads the claims and checks them.

```text
HANDOFF: second-vendor review requested

PR: #<number>   Head: <full sha>   Base: <branch> @ <sha>
Lane: <L2 truth | L3 held>, derived from: <the paths that set the lane>

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

The reviewer answers with one of three rulings: `CLEAR`, `CORRECT` (blocking findings), or `HOLD`. A held PR may be hand-merged only after `CLEAR` on its current head, or after 2 hours with no ruling. `CORRECT` or `HOLD` blocks ready and the merge. Only the owner naming that specific PR waives the wait.
