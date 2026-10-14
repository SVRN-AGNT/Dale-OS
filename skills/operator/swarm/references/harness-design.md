# Harness Design

The Harness Design is the contract a swarm run executes. It is short (a screen, not a document), written *before* any agent is spawned, and revised when evidence changes the picture.

## Template

```text
HARNESS DESIGN — <one-line task>
Authorization: <analyze/diagnose | implement> + explicit owner-gated actions   (inherited; never raised)
Depth: LOW | MEDIUM | HIGH   (from authority moved and blast radius, never from confidence)
Objective: <exact question/outcome>
Deliverable: <artifact that constitutes completion>
Topology: <audit | debugging | research | implementation | migration | architecture | adversarial review | classification | reconciliation | mixed>
Search space: <independent dimensions>
Dependencies: <sequential edges and why>
Uncertainty: <open propositions and evidence that would reduce them>
Failure modes: <how the harness could return a confidently wrong answer>
Evidence standard: <what counts as proof>
Write topology: <implementation only: editable sets, read-only lanes, semantic authorities, integration point>
Verification: <who falsifies what>
Resource plan: <agents, concurrency, tiers, context, recursion, retry/escalation, adversarial reserve>
Stop when: <observable completion contract>
Verdict: SOLO | FAN-OUT | SCRIPTED
```

State it before spawning. A SOLO verdict is a complete, valid output and needs only the verdict, its reason, and the depth tier; the tier still decides what the run owes. The full template is for fan-out verdicts.

## Design rules

### Separate question from artifact

The objective is the question. The deliverable is the thing that proves the question was answered. Workers are aimed at the question; synthesis produces the artifact.

Example:

- Objective: determine why a page intermittently shows stale data.
- Deliverable: one reproduced root mechanism, blast radius, falsification result, and authorized repair plan.

### Decompose by information independence

A lane should exist only if it can produce information another lane cannot cheaply produce. If two candidate lanes would read the same files and answer the same question, they are one lane.

Useful boundaries include:

- separate runtime surfaces;
- competing root-cause hypotheses;
- state/data path vs network path;
- current authority map vs migration risk;
- implementation vs independent review;
- discovery vs falsification;
- authority axes, when the task moves something that decides (`authority-migration.md`).

Do not split files alphabetically or divide a codebase into equal chunks unless those chunks represent real independent questions. If a lane cannot be named by the *information* it uniquely produces, it should not exist.

### Make dependencies typed

Anything that needs another lane's output is sequential; make the handoff a typed contract (a schema), not a narrative.

### Make uncertainty explicit

Every important uncertainty must be:

- assigned to a lane;
- reduced by deterministic evidence; or
- preserved as unresolved in the final synthesis.

Unowned uncertainty is a harness-design defect.

### Design for failure

Ask "how could this come back wrong and look right?" and name the answer before the workers start. Typical examples:

- all lanes share the same wrong premise;
- duplicated lanes masquerade as independent confirmation;
- agents agree because they read the same misleading comment;
- stale docs treated as truth; a fixture treated as production data;
- a dormant code path treated as dead;
- the writer also reviews its own work;
- a fallback silently becomes canonical;
- a worker can broaden scope;
- a scheduler cannot reach a later state;
- tests prove a helper but not the live path;
- two parallel writers mutate one authority.

Each failure mode needs a verifier lens or an evidence standard that would catch it.

### Evidence standard

Pick from: code location (`file:line`), runtime reproduction, test, benchmark, source citation, contract/schema, screenshot, database evidence, diff, deterministic calculation. A finding below the standard is a *lead*, reported as such (`verification-and-adjudication.md`).

### Verification

For each finding class, name who falsifies it and with what framing. Low-stakes mechanical results may be self-verified by deterministic checks; anything that will drive a decision or a code change gets an independent falsifier.

### Stop conditions

Written before running: for example, "every route classified with evidence, every HIGH finding independently verified or marked unresolved, deliverable produced". For discovery of unknown size: "K consecutive rounds surface nothing new", with K chosen for the task.

## Staged allocation

```text
round 0  design the smallest useful graph
round 1  broad-enough discovery
round 2  inspect signal and contradictions
round 3  deepen only unresolved/high-value regions
round 4  independent falsification
round 5  provisional synthesis
round 6  cross-lane attack if MEDIUM/HIGH
round 7  final synthesis / authorized implementation handoff
```

The graph may shrink at every round. Ending smaller than the design is success, not under-delivery.

Concrete triggers:

- **Converged and decisive** -> stop expanding; move to verification/synthesis.
- **One subsystem contradicts itself** -> deepen that subsystem with competing hypotheses.
- **Verifier rejects a finding** -> kill the lanes that depended on it.
- **A shared mechanism appears** -> re-partition around the mechanism (systemic until proven isolated), not around its symptoms.
- **K consecutive rounds return nothing new** -> discovery is dry.

### Add capacity when

- a material proposition lacks independent evidence;
- two credible explanations remain live;
- a verifier exposes an unresolved mechanism;
- a new systemic mechanism expands the true blast radius;
- a specialized domain requires a different reasoning lens;
- an implementation lane needs an independent reviewer.

### Prune capacity when

- a lane duplicates another lane's evidence and question;
- deterministic evidence settles the proposition;
- a verifier kills the lane's premise;
- new information shows a surface is outside the blast radius;
- the result cannot affect the requested decision.

## Resource planning

| Lever | Decide by |
|---|---|
| Agent count | genuinely independent lanes plus the verifiers the stakes justify; never a preset |
| Concurrency | runtime cap and file-collision risk; readers can be wide, writers narrow |
| Reasoning tier | strongest available for harness design, adjudication, architecture, systems risk, and cross-lane synthesis; cheaper capacity for enumeration, extraction, deterministic checks, and classification; never orchestrate on the smallest tier; never write a model version into a worker prompt |
| Worker context | the slice, shared truths, constraints, output contract, needed files, and the safety floor; nothing else |
| Effort budget | proportional to stakes; explicit invocation removes the *permission* question, not the *proportionality* question |
| Recursion depth | a parent subdivides only a domain that is genuinely large and independent; each extra level needs a stated reason |
| Retry / escalation | retry only on mechanical failure (tool error, empty result); a lane that returns a *wrong* answer is escalated to a verifier, a stronger tier, or a reframed brief, never rerun identically |
| Adversarial budget | at MEDIUM/HIGH, reserve capacity for the cross-lane pass before spending it all on breadth |

## Escalation to an extraordinary run

When invoked autonomously, if the design would become a mega-run (hundreds of agents, multi-million-token scale, or cost far outside the task's norm), present the Harness Design and wait for the human owner before launching. Explicit invocation removes only that compute confirmation; every stop condition and owner gate still applies, as does any opt-in rule the host imposes on scripted orchestration.

## Decomposition examples

- **Large application audit** -> routes, mobile, copy, duplicate surfaces, diagnostics, dead UI, modal load, information density, onboarding, hierarchy, accessibility. Each lane reads a different slice; overlap is resolved at the cluster/adjudicate stage, not by pre-merging lanes.
- **Difficult bug** -> competing root-cause hypotheses (one lane each, each trying to confirm its own and refute the others), runtime reproduction, state/data path, network path, lifecycle, recent regression history (`git log -S`, blame on the symptom's surface).
- **Architecture decision** -> current authority map, dependency graph, alternative designs, migration risk, contradiction search across docs vs. code, future extensibility, adversarial critique of the leading option.

## Worked designs

These illustrate that the harness changes with the task. They are not templates to reuse; each real run designs its own.

### A. "Audit the reporting-history architecture." (analyze-only, MEDIUM)

- Topology: architecture + audit.
- Search space: authority map (who writes history, who reads it), data path (source of truth -> snapshot -> derived series), consumers (pages, exports, sync jobs), contradiction hunt (docs and decision records vs. code), regression history. Five read-only survey lanes; cheaper tier where the work is enumeration, strong tier for the authority map.
- Verification: every "duplicate authority" or "dead path" claim gets a fresh falsifier ("dormant is not dead": find any live consumer). Evidence standard: `file:line` plus a consumer trace.
- Synthesis: Map -> Cluster -> Adjudicate, then a ranked architecture assessment and the cross-lane attack. The deliverable is analysis; no implementation is manufactured from findings.
- Stop: every history producer and consumer classified; every HIGH claim verified or marked unresolved.

### B. "Figure out why this page is so slow and fix the root cause." (implement, LOW-MEDIUM)

- Topology: debugging -> implementation.
- Phase 1 (read-only): reproduction lane first (measure; without a number there is no bug), then competing hypotheses: render churn, data-fetch waterfall, selector recomputation, bundle/asset load, third-party scripts. Each lane tries to confirm its hypothesis *and* refute the others. A lane whose hypothesis fails the reproduction is pruned.
- Adjudication on measured evidence (profile, timing), not vote.
- Phase 2 (only once the root cause is established): one writer on an isolated branch, minimal fix at the baseline; one independent reviewer reads the diff cold; re-measure against the reproduction. Hunt other consumers of the same mechanism and report them; do not widen the fix without authorization. Deliver through the repository's normal integration path.
- Stop: the reproduction shows the improvement, gates are green, blast-radius audit reported.

### C. "Add a 'copy invite link' button to a table row." (implement, LOW — not swarm-worthy)

- Verdict: **SOLO**. Known files, one surface (plus its responsive counterpart), an existing design system to compose from, a nearby test to extend. One agent obtains the answer cheaply; orchestration overhead would exceed the information gained.
- If invoked explicitly as a swarm, the skill still returns SOLO and says so: the request authorizes compute, it does not require spending it.

### D. "Consolidate the plan / mode / access model." (analyze-only, HIGH)

Authorization stays analyze-only: the deliverable is the analysis, the sequence, and the matrix. Implementation is a separate, separately authorized slice; "diagnose first" is not an escalation path. `authority-migration.md` is loaded during design, because it decides how the lanes are cut.

- **Lanes by axis, not by file**: admission, ordinary product policy, operator/admin authority, cohort and programme state, credential routing, runtime economics. One lane per axis, each answering "what does this value actually decide here, and what would decide it instead?" Cutting per directory would split every axis across several lanes and leave no one owning the question.
- **Classification is part of each lane's output**, not a later cleanup: every reference returned as BEHAVIORAL / TRANSPORT / COMPATIBILITY / PERSISTED / DISPLAY / TEST-INFRA / DEAD / PROTECTED. A raw reference count is not an inventory.
- **Synthesis** produces the axes, the target architecture, and a hazard-ordered sequence with a causal sentence per boundary: operator authority off the value before the value collapses, else operator access disappears; credential routing off it before that, else the route fails open to a default credential.
- **Then the attack** (`adversarial-synthesis.md`), where this shape earns its cost: the choke-point audit on each new authority, the second-writer topology for the client read model, the fail-open table for legacy-shaped accounts not yet migrated, communication surfaces that resume promising what enforcement no longer guarantees, and the CI reachability of every gate the plan leans on.
- **Falsification matrix before implementation**, invariance *and* converse per invariant: valid users still working proves nothing about whether forged legacy input still confers authority.
- Stop: axes named, every reference classified with an owning slice, sequence hazard-justified, matrix written, and the deepen / stop / proceed decision recorded.
