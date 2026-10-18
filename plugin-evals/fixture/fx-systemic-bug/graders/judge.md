---
type: llm
---

PASS if the response traces the wrong month to the shared monthLabel helper in src/shared/dates.js, and names the statement view as another consumer of it, before treating a change to src/invoice/view.js alone as the fix. FAIL if it treats a change to src/invoice/view.js alone as complete, or does not mention that the statement view is affected.
