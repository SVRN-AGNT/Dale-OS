# PR header

Put this block at the top of a PR body. The lane is filled in from the lane script's output, never chosen by the author. The lander reads the state, and people read the rest.

```text
STATE: DRAFT | READY | REPAIR | HOLD | DEPENDENCY
BASE_SHA: <sha the branch was cut from or last updated to>
DEPENDS_ON: <PR numbers, or none>
LANE: <L0 | L1 | L2 | L3> (derived by <script>, from <paths>)
REVIEW: Agent Review <verdict> on <sha>; second vendor <CLEAR | CORRECT | HOLD | not required>
```

Then use the usual sections: what changed, why, how it was verified, and what is still unknown.
