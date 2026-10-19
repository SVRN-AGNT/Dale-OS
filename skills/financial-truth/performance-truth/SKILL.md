---
name: performance-truth
description: Gate and calculate investment performance only when the required valuation and capital-flow evidence is ready. Use for TWR, Modified Dietz, simple return, benchmark comparison, trader-skill analytics, or portfolio history when deposits, withdrawals, gaps, stale values, or untrusted records can contaminate return.
---

# Performance Truth

## Rule

**Funding is not performance.**

## Workflow

1. Check readiness before calculating: trusted valuations, sufficient endpoints, continuity, external-flow coverage, and any domain-specific blockers.
2. Identify the return method and state why it is valid for the available records.
3. If a material external flow is known but its timing is missing and the valid return method depends on that timing, the requested return is **WITHHELD**. A sensitivity range may be shown only as diagnostic context and must be labeled as not being a publishable return result.
4. Do not fall back to a flattering or approximate simple return when unresolved external flows can be mistaken for gains or when required flow timing is unavailable.
5. Rebase or narrow across material valuation discontinuities instead of drawing unbounded continuity through a gap. Use the trading calendar of the venue that prices the asset: a value missing on a closed day may carry the last close, and one missing on a trading day is a gap and is handled as above.
6. Publish the method, evidence status, exclusions, and caveats beside the number.
7. Withhold when unresolved data can materially change the performance conclusion.

## Deterministic companion

When structured JSON is available, prefer `scripts/performance_readiness.py` for the mechanical check. Treat its output as a constraint on reasoning, not as permission to invent missing classifications. Run it from the skill directory with JSON on stdin.
Read `references/DETERMINISTIC_INPUT.md` when you need the input contract.

## Falsify it

Try to explain the reported return without confusing funding with performance and without crossing an untrusted valuation gap. If a material external flow lacks timing required by the chosen method, try to prove that a single publishable return can still be supported. If you cannot, withhold the return.

## Stop conditions

- Unresolved cash movements could be external flows.
- A material external flow is known but the timing required by the valid return method is missing.
- Fewer than two trusted continuous valuations exist for the requested period.
- The selected calculation method does not match the available flow data.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

READINESS · METHOD · PERIOD · RETURN or WITHHELD · EXCLUSIONS · CONTINUITY · FLOW COVERAGE · CAVEATS.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
