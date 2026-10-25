# Roadmap

This file tracks only unfinished or future work. Completed release evidence belongs in `PROOF.md` and `release/gates.json`.

## Current development line — 0.2.0-dev

The current tree builds on the frozen public v0.1.0 release and adds eleven skills (including SWARM), the advanced agentic-engineering layer, two Claude Code plugins, the shared CI layer and the Shipping System.

Near-term work should be earned by evidence rather than feature count:

- run the full clean-runner validation surface against the 0.2.0-dev tree after material changes;
- gather field evidence from real SWARM use and promote only failure classes that repeat;
- extend provider-backed model evidence to SWARM when a stable evaluation contract is worth freezing;
- keep developer onboarding, routing, and source-of-truth boundaries simple enough that a new contributor can verify the repo without private context.

## Future candidates

Only promote work that is paid for by a demonstrated failure, user need, or measurable portability gap.

- expand sanitized incident cases when new failure classes are observed;
- add property/fuzz tests where deterministic financial invariants benefit from them;
- deepen corporate-action and cross-account transfer fixtures when evidence warrants it;
- expand adapter coverage only for hosts with meaningful demand;
- add long-horizon handoff reliability tests when a portable runtime contract exists.

## Release rule

A future release earns new evidence. It does not inherit unqualified confidence from v0.1.0.

Use `release/gates.json`, `PROOF.md`, and `docs/PUBLIC_RELEASE_READINESS.md` to distinguish frozen historical evidence from claims about the current tree.
