# Dale OS

**An agentic operating system for high-integrity software and finance.**

[![validate](https://github.com/Tataku/Dale-OS/actions/workflows/validate.yml/badge.svg)](https://github.com/Tataku/Dale-OS/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

**Authority before autonomy. Evidence before confidence. Real fixes to real problems.**

[Install](INSTALL.md) · [Advanced agentic engineering](docs/AGENTIC_ENGINEERING.md) · [Try to break it](CHALLENGE.md) · [Read the proof](PROOF.md) · [Browse the skills](docs/SKILL_CATALOG.md)

Dale OS is a portable control plane for AI agents doing consequential software and financial work. It turns recurring failure modes into small falsifiable skills, deterministic checks, narrow compositions, machine-readable receipts, and reproducible evals.

**If you are an agent:** read [`AGENTS.md`](AGENTS.md). If you already know what is broken, start with `machine/failure-classes.json`. If the work spans multiple failure classes, use `machine/compositions.json`. Do not load the whole repo.

I did not start this as a framework. I kept running into the same expensive failure modes while building real software: agents fixing symptoms instead of mechanisms, reopening decisions I had already made, wandering outside scope, calling a PR "shipped," or producing a financially clean-looking number from dirty underlying records.

So I started turning the lessons into rules. Dale OS is the result.

The basic idea is simple:

- **Authority before autonomy.**
- **Real fixes to real problems.**
- **Null is not failure. False certainty is.**
- **Get the money right.**

This repository is the canonical source. Skills are modules inside the operating system. Deterministic tools handle math and reconciliation where reasoning alone is not good enough. Evals try to break the rules before real work does.

## Developer quickstart

If you want the fastest technical read, inspect these in order:

1. [`skills/operator/swarm/SKILL.md`](skills/operator/swarm/SKILL.md) — the adaptive multi-agent harness.
2. [`docs/AGENTIC_ENGINEERING.md`](docs/AGENTIC_ENGINEERING.md) — the graph, authority, handoff, and control-plane architecture behind it.
3. [`machine/failure-classes.json`](machine/failure-classes.json) and [`machine/compositions.json`](machine/compositions.json) — low-context routing and narrow composition.
4. [`examples/swarm-harness.md`](examples/swarm-harness.md) — a worked example of decomposing a real agent-loop failure.
5. [`CHALLENGE.md`](CHALLENGE.md) and [`PROOF.md`](PROOF.md) — how the claims are attacked instead of merely asserted.

From a checkout:

```bash
python scripts/verify.py
# add Node 24 / Eve adapter verification:
python scripts/verify.py --with-eve
```

## Two systems, one philosophy

### Operator OS

For coding agents and agentic software work:

- `execution-charter` — give the agent a fence before a shovel.
- `systemic-bug-instinct` — assume a bug may be systemic until the blast-radius audit says otherwise.
- `truth-boundary` — separate known, derived, estimated, inferred and unknown.
- `latest-authority` — carry the latest human decision forward; do not re-ask it without new conflicting evidence.
- `diff-scope-audit` — every hunk owes the charter an explanation.
- `protected-boundary` — stopping is a valid successful action.
- `intent-drift-check` — busy is not the same as aligned.
- `operator-ui-audit` — a wrong value in the UI is usually a data problem wearing a costume.
- `swarm` — design the smallest task-specific multi-agent harness; expand and prune on evidence.
- `reachability-proof` — a guard nothing reaches is not a guard; silence is not evidence of health.
- `loop-closure` — capture is not the problem, retirement is; report net loops.
- `false-competence-check` — the most expensive mistakes look like good work.

### Advanced agentic engineering

For hard software work that exceeds a single-agent loop, Dale OS also documents the harness layer: adaptive task graphs, authority graphs, state-authority topology, independent falsification, durable worker/reviewer loops, evidence/control separation, exact-SHA handoffs, recovery, and write-topology rules. See [`docs/AGENTIC_ENGINEERING.md`](docs/AGENTIC_ENGINEERING.md).

The central shift is from **prompt engineering** to **environment engineering**: shape what agents can see, what they are allowed to decide, how they prove progress, how they hand off, and what makes completion valid.

### Financial Truth

For money, ledgers, portfolio analytics and financial models:

- `money-trail` — every dollar gets a passport.
- `accounting-integrity` — well-formed data can still lie.
- `performance-truth` — funding is not performance.
- `basis-proof` — no basis, no profit.
- `ledger-repair` — preview the economics before changing the books.
- `transfer-neutrality` — money does not teleport.
- `cash-truth` — missing cash is not zero cash.
- `financial-evidence-grade` — an estimate is not an authority.
- `tax-character-proof` — observed cash and tax character are different facts.
- `corporate-action-continuity` — identity can change without changing economics.
- `model-sanity` — a plausible model is not automatically a valid model.
- `close-the-books` — do not publish analytics whose required books are not ready.

## Five-minute proof

```bash
python scripts/dale.py catalog
python scripts/dale.py resolve symptom-patch --json
python scripts/dale.py compositions --json
python scripts/dale.py challenge
python scripts/dale.py doctor
```

The repo ships a machine-readable receipt contract in [`RECEIPTS.md`](RECEIPTS.md) and `schemas/receipt.schema.json`, so agent handoffs can preserve claims, unknowns, mutations and verification instead of forwarding confidence without evidence.

## Repository map

```text
Dale-OS/
├── README.md                # human entry point
├── AGENTS.md                # machine-first entry point
├── INSTALL.md               # preview/install/update paths
├── PRINCIPLES.md            # operating floor
├── ARCHITECTURE.md          # dependency and authority model
├── skills/                  # canonical Agent Skills modules
│   ├── operator/
│   └── financial-truth/
├── tools/                   # deterministic, read-only financial checks
├── evals/                   # activation, behavior, composition, fixtures
├── cases/                   # sanitized incidents that paid for rules
├── machine/                 # routing, composition, discovery contracts
├── adapters/                # host-specific distributions/guidance
├── scripts/                 # control surface, generators, validators
├── schemas/                 # portable machine contracts
├── release/                 # machine-readable release authority
└── docs/                    # deeper operating and evaluation contracts
```

For detailed navigation, see [`llms.txt`](llms.txt) or [`AGENTS.md`](AGENTS.md).

## Source rule

**One source. Many adapters.**

The canonical skill lives in `skills/**/SKILL.md`. Platform adapters are generated from that source. Never hand-maintain a second copy of a rule just because a different agent framework wants a different filesystem shape.

## Financial safety rule

Dale OS does not let an LLM become the accounting authority just because it can write a convincing explanation.

When evidence cannot establish the answer, the correct output may be:

```text
WITHHELD
Reason: evidence insufficient
```

That is not the system failing. That is the system working.

## Status

**Current tree: 0.2.0-dev.** It adds the canonical `swarm` skill and the advanced agentic-engineering layer.

**Frozen public release evidence: v0.1.0.** That release closed clean-runner validation, privacy scanning, 20/20 skill installability, generated-source parity, four-model provider-backed evaluation, semantic review, and targeted remediation. The historical four-model baseline remains **78/80 semantic passes (97.5%) with 0 critical invariant violations**; it is not rewritten to include post-v0.1 capabilities.

SWARM has its own activation/behavioral coverage and repository validators in the current tree, but it is **not** claimed as part of the frozen v0.1.0 provider-backed matrix.

See [`PROOF.md`](PROOF.md), [`docs/reports/CROSS_MODEL_VERIFICATION_2026-08-07.md`](docs/reports/CROSS_MODEL_VERIFICATION_2026-08-07.md), and [`docs/PUBLIC_RELEASE_READINESS.md`](docs/PUBLIC_RELEASE_READINESS.md).

## Why “Dale OS”?

Dale OS is partly what happens when one messy human tries to run a small institution out of one skull. Dale is a solopreneur juggling finance, software, product, research, QA, and the organizational chaos between them while trying to build financial software with institutional-style discipline. The brain is useful; the queue is not. Dale OS externalizes the operating rules so AI can absorb more of that complexity **without amplifying the chaos**.

Designed and curated by Dale Powell from real human-agent operating experience while building ACF Dashboard and related systems. The public package is intentionally generalized: ACF-specific scoring logic, personal financial data and proprietary product internals do not belong here.
