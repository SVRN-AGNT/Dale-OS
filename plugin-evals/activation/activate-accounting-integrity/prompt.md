---
description: "Should fire accounting-integrity"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

All ledger rows pass schema validation, but shares, cash, basis, dates, and realized P&L may contradict each other. Test whether the records can all be true at once.
