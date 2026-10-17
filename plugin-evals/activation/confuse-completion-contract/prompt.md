---
description: "Should not fire completion-contract"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

The agent says the null-check fix is done. Prove the new guard is actually reached in CI and fails when it should.
