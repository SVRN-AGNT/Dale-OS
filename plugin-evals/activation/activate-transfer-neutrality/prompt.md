---
description: "Should fire transfer-neutrality"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

Reconcile account-to-account movements so paired internal transfers net to zero external portfolio flow, and leave unpaired legs unresolved.
