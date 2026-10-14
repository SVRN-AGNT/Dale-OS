# HANDOFF comment for the second-vendor reviewer

Post this as a PR comment on every L2 (truth) or L3 (held) PR, after the Agent Review verdict is in. The second reviewer is a model from a different vendor. Its reply is evidence for a person or the lander; it never merges anything.

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
Reply CLEAR or a list of blocking findings for head <sha>.
```

A reply covers only the head it names. A push after the reply means asking again.
