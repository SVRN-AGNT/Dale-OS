# Audit Graph

A reusable multi-phase topology for one broad question: **does the system the repository actually executes match the system its architecture claims?** It is a composition of the patterns in `workflow-patterns.md`, sized for a large, analyze-only audit. It is not a default; most audits need far less (`harness-design.md`).

Use it when the answer must survive hostile reading, the claimed architecture has many authorities and seams, and documentation may be stale, aspirational, or wrong.

## Ground rules

- **Analyze-only.** No production code, config, migration, test, or doctrine changes. Nothing is fixed, committed, or filed as a side effect of the audit.
- **Pin the specimen to one commit.** Record the exact commit ID investigated, and build every sandbox from that commit (for example with `git archive <commit>`), not from a moving branch. Record how the deployed system relates to the specimen, and say plainly when that relation is unproven.
- **Executable-first.** Code, config, migrations, workflows, and read-only catalog metadata are evidence. Documentation is read last (Phase D).
- **Declare the observation boundary up front**: what the audit may read live (metadata only, synthetic subjects only, no live user rows) and what it cannot observe (blocked endpoints, deployment settings, provider policies). Findings that depend on the unobservable are capped at INFERRED or CONFIG-PROVEN and name the boundary.
- **Evidence levels and reachability classes** from `verification-and-adjudication.md` apply to every material finding: exactly one level each, never promoted by repetition.
- **Disclose process breaches.** If any agent exceeded the declared boundary (read beyond metadata, disturbed the local environment, touched shared state), the report says so in full: what happened, what was and was not written, what was repaired, and which findings rest on evidence obtained outside the boundary. A conservative bias introduced by a breach (for example, verifiers unable to run tests for a window) is disclosed too.

## Phase A — independent domain lanes

One lane per domain (identity, access, persistence, ingestion, accounting, control plane, and so on, as the system actually divides). Each lane reconstructs its domain **from executable code without reading documentation**, so the docs cannot pre-shape what it sees. Include a lane for apparently dead or "ghost" surfaces.

Each lane returns a register with a fixed shape:

| Section | Contents |
|---|---|
| Summary | what actually runs, in plain words; the strongest pieces as well as the defects |
| Constitution | domain, canonical authority, writers, readers, fallbacks, persistence, freshness, authorization boundary, audit trail, tests (and whether CI runs them), confidence |
| Flow notes | the real request/data flows, step by step, as executed |
| Findings | each with severity, kind, confidence, `file:line` evidence, and later the verifier verdicts and corrected claim |
| Strong controls | mechanisms that hold and should not be disturbed by a fix |
| Authority map | who decides each governed fact, including re-derivers and mirrors |
| Negative space | what the lane looked for and did not find, and what it could not check |

Finding taxonomy:

| Kind | Shape |
|---|---|
| `false_safety` | a guard, test, or readout that appears to protect but does not |
| `silent_collapse` | distinct states collapsed into one answer without signal |
| `impossible_state` | the system can enter a state its own contracts say cannot exist |
| `contradiction` | two parts of the executing system disagree about the same fact |
| `duplicate_authority` | more than one thing decides the same fact |
| `ghost_architecture` | structure that exists but decides or protects nothing |
| `security_boundary` | an authorization, trust, or exposure boundary that does not hold |

**Phase A verification.** Every non-low finding goes to a fresh-context verifier that receives only the claim, its evidence surface, and a falsification objective. High and critical findings get **two lenses** (mechanism/reproduction and production conditions). The report uses the verifier's corrected claim and the more conservative severity.

## Phase B — seam tracers

Subsystems that are each correct can still be wrong together. Seam tracers take a pair (or chain) of independently verified subsystems and **build executable harnesses that force them to meet**: real modules, imported in a sandbox copy, driven through the seam. Each harness records CONTROL (expected behavior), MUTATION (the condition under test), RESTORE (back to control), and the outputs, so the result is reproducible without the tracer's narrative.

## Phase C0 — impossible-state hunters and gap fillers

- **Impossible-state hunters** enumerate the code's own "cannot happen" claims (invariant comments, exhaustive switches, type-level guarantees, constraint names, assertion messages) and try to drive the real modules into each forbidden state. A violation counts only when the contract is quoted with `file:line` and a real path into the state is shown.
- **Gap fillers** cover surfaces no lane owned. Ask explicitly: what did the partition leave unowned?

Every Phase B/C0 finding carries an evidence level and a category, and goes through the same verifier discipline as Phase A.

## Phase C — three attacks on the provisional synthesis

Synthesize Phases A–C0 into a **provisional** synthesis, then attack it from three fresh contexts:

1. **Trust attack**: who can cause what? Authorization, identity, credential, and exposure claims in the synthesis, attacked as an adversary would.
2. **State attack**: shared mutable state, writers, caches, persistence, transitional shapes, and the fail-open/fail-closed tables (`adversarial-synthesis.md`).
3. **Reality check**: classify every claimed violation by whether a real user in the deployed configuration can reach it (NORMAL-USE / COMMON / RARE / SYNTHETIC-ONLY / UNSETTLED), and **remove SYNTHETIC-ONLY** items from the violation list.

The revised synthesis attributes every change to the attack that forced it.

## Phase D — documentation reconciliation, last

Only now read the documentation: architecture docs, decision records, project instructions, public claims. Reconcile four systems:

| System | Source |
|---|---|
| Intended | decision records, constitutions, design docs |
| Documented | current docs, READMEs, public claims |
| Tested | what the tests actually assert, and whether CI runs them |
| Executable | what Phases A–C proved |

Each disagreement is a finding about the docs or about the code, stated in that direction. If the specimen branch moved during the audit, reconcile the delta separately and never fold it into executable truth.

## Deliverable

- verdict on the audit question, with its evidence level;
- proven architecture violations, kept apart from concerning code, each with reachability;
- the strong controls a remediation must not disturb;
- intended vs. documented vs. tested vs. executable reconciliation;
- the observation boundary and every finding it caps;
- process disclosures;
- the specimen commit and the delta reconciled.

## Scale and cost

This topology can run to a hundred or more subagents. Under autonomous invocation, present the Harness Design and wait for the human owner before launching (`harness-design.md`, extraordinary runs). Prune aggressively: a domain with no non-low findings needs no seam tracer of its own, and the graph may end smaller than designed.

## Handling the output

A report built this way describes exploitable weaknesses in detail. Keep it in a private location, and redact it before anything it lives beside is made public.
