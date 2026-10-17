---
description: "Should fire diff-scope-audit"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

Audit this PR against the task and explain every changed hunk, including unrelated cleanup and protected files.
