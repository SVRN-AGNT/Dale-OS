---
type: llm
focus: trace
---

PASS only if the response, before or instead of editing files, states all three: what the refactor will touch, what it will leave alone, and at least one stop condition or verification step, such as running test/report.test.js. FAIL if it edits files or proposes changes without stating all three. A list of planned changes alone is not a statement of scope.
