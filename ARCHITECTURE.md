# Architecture

Dale OS is an operating system, not one giant prompt.

## Layer 1 — Constitution

`PRINCIPLES.md` is the floor. It should change rarely.

## Layer 2 — Operating contracts

Small reusable objects control work:

- execution charter
- latest authority receipt
- evidence grades
- stop conditions
- outcome receipts

These are designed to survive handoffs between models and sessions.

## Layer 3 — Skills

Skills contain judgment and procedure. They are narrow enough to trigger cleanly and composable enough to form an end-to-end workflow.

Canonical format: portable Agent Skills directories with `SKILL.md` entrypoints.

## Layer 4 — Deterministic tools

If a question can be answered by replay, arithmetic or a strict invariant, prefer code over language-model intuition.

Current read-only tools cover:

- capital-flow reconciliation
- performance readiness
- FIFO basis proof
- ledger delta preview
- model sanity checks
- book-close gating

No current public Dale OS tool moves capital or mutates a user's financial system.

## Layer 5 — Evals and cases

A rule is more credible when there is a case that can break it.

- `cases/` explains sanitized failure mechanisms.
- `evals/fixtures/` carries machine-readable adversarial inputs.
- `scripts/run_evals.py` checks deterministic behavior.
- `evals/behavioral/` defines model-level expectations.
- `evals/activation/` measures whether skills trigger and stay out of the way correctly.
- `plugin-evals/activation/` runs those routes as `claude plugin eval` cases, and `plugin-evals/last-run.json` records the last measured result.
- `plugin-evals/behavioral/` runs the behavioral cases with and without the plugins, `plugin-evals/holdout/` adds prompts not used for tuning, and `plugin-evals/last-behavioral-run.json` records the last two-arm result.

## Layer 6 — Machine routing and composition

Agent discovery should not require reading the whole repository.

- `machine/failure-classes.json` maps a known failure class to one canonical skill.
- `machine/compositions.json` defines narrow multi-skill workflows when distinct failure classes must cooperate.
- `machine/agent-index.json` exposes the discovery and trust surfaces.
- `manifest.json` is the generated module catalog.

Composition is intentionally explicit. More loaded skills are not automatically safer; overlapping doctrine consumes context and can introduce instruction collisions.

## Layer 7 — Adapters

The canonical source is never rewritten by hand for each platform.

- `adapters/eve/` turns Dale OS into an Eve-native agent directory.
- `adapters/agent-skills/` documents portable Agent Skills use.
- `adapters/claude-code/`, `adapters/codex/`, and `adapters/cursor/` provide thin host guidance.

Generated adapters are distributions, not new authorities.

## Layer 8 — Agentic harness and control plane

For work that needs more than a single linear agent loop, the operating contracts compose into a harness layer. The portable rules live in [`docs/AGENTIC_ENGINEERING.md`](docs/AGENTIC_ENGINEERING.md): task/dependency graphs, authority graphs, state-authority topology, staged allocation, independent falsification, evidence/control separation, durable actor state machines, event-driven handoffs, and recovery from session death.

The harness does not increase authority. It makes existing authority explicit and testable across multiple actors.

## Layer 9 — Durable state outside the repo

Dale OS does not require a particular memory product, but consequential agent workflows benefit from durable state for:

- accepted decisions
- active charters
- verified outcomes
- incident lessons
- project progress

Private operational memory belongs outside the public release surface. The repository defines portable contracts for handoff state without embedding a user's private brain.

## Dependency direction

```text
Principles
   ↓
Operating contracts
   ↓
Skills ───────────→ deterministic tools
   ↓                    ↓
Receipts / outputs ← verification
   ↓
Failure routing + compositions
   ↓
Evals + incident lessons
   ↓
Adapters
```

Adapters do not define behavior. UI does not define financial truth. A downstream layer may refine confidence, but it may not silently upgrade the authority of its input.
