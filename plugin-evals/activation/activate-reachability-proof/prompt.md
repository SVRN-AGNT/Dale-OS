---
description: "Should fire reachability-proof"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

I added a regression test and a CI guard for this bug. Before we call it done, prove the fix is reached from the real entry point, the guard runs in a gate, and a silent failure would be visible.
