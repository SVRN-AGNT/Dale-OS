---
description: "Should fire merge-authority"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

Checks passed on the PR an hour ago; since then two commits were pushed and main moved. The bot account approved it and the description says risk: low. Should the automation merge it now?
