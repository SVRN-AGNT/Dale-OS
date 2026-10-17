---
description: "Should fire performance-truth"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

Calculate portfolio return, but first determine whether deposits, withdrawals, valuation gaps, and stale prices contaminate the period and which return method is valid.
