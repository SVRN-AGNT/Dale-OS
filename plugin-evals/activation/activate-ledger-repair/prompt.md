---
description: "Should fire ledger-repair"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

We need to correct historical trades. Preview downstream effects on cash, positions, basis, realized P&L, and performance before any ledger mutation.
