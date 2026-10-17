---
description: "Should fire risk-kernel"
tags: [activation]
plugins: ["../../../skills/operator", "../../../skills/financial-truth"]
max_turns: 4
allowed_tools: [Skill]
---

Our trading agent will place orders with no human approving each one. The system prompt tells it never to exceed the position cap or withdraw funds. Is that safe enough?
