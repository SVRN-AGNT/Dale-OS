# Workflow Patterns

Use these as composable shapes, not presets. Choose the pattern that matches the information structure of the task. Each entry gives when it fits, its shape, what it protects against, and how it goes wrong.

Vocabulary: "fan-out" is several agents running at once on whatever mechanism the host supports; "barrier" means the next stage needs *all* prior results together (dedup, early exit, cross-item comparison). Otherwise let items flow stage to stage independently.

## 1. Survey -> Verify -> Synthesize

Use for broad audits where many surfaces may contain the same failure class.

- Survey lanes map candidate findings, one per independent dimension.
- Verifiers independently attack material findings with claim + evidence surface + falsification objective.
- Synthesis deduplicates and connects systemic mechanisms.

Protects against plausible-but-wrong findings surviving into the deliverable. Goes wrong when verifiers receive the surveyor's narrative and nod, survey lanes overlap and double-count, or the synthesizer concatenates.

Avoid when the problem is already a single reproducible mechanism.

## 2. Map -> Cluster -> Adjudicate

Use for large inventories, policy/rule audits, architecture consolidation, or the output of pattern 1 at scale.

- Map raw instances, with provenance.
- Barrier, then cluster by underlying mechanism or authority (plain code where a key exists, an agent where judgment is needed).
- Adjudicate conflicts on evidence and choose canonical classifications.

Protects against ten symptoms of one mechanism reported as ten findings, and two lanes contradicting silently. Goes wrong when clustering by file or wording instead of root mechanism.

Do not let clustering frequency become a vote on truth.

## 3. Competing Hypotheses -> Falsification -> Convergence

Use for debugging when several root causes plausibly explain one symptom.

- Reproduction first: a measurement or failing test is the anchor.
- Give each hypothesis an owner who must produce discriminating evidence, confirming its own and refuting the others.
- Add falsifiers that try to kill the strongest surviving hypotheses against the reproduction.
- Converge only after the evidence distinguishes them, or report "unresolved between H2 and H3; resolving evidence would be X".

Protects against anchoring on the first plausible cause and fixing a symptom. Goes wrong when no reproduction exists (lanes argue about narratives) or hypotheses are not mutually exclusive and the design does not say so.

Do not assign several agents to "investigate the bug" without distinct hypotheses.

## 4. Research -> Triangulate -> Contradiction Hunt -> Synthesize

Use when evidence comes from multiple external or internal sources that may disagree or be stale (docs vs. code, vendor docs vs. behavior, prior decisions vs. current state).

- Research independent sources from different angles, each blind to the others.
- Triangulate each claim across at least two independent sources.
- A dedicated lane searches only for contradictions and date/population/scope mismatches.
- Synthesize with provenance, dated claims, and uncertainty.

Protects against one source's error propagating, and consensus that is really one upstream source quoted five times. Goes wrong when "independent" sources share an origin, or the contradiction lane is skipped because everything looked consistent.

## 5. Implement -> Independent Review -> Test -> Integrate

Use when implementation is authorized, the root cause or design is settled, and work can be safely partitioned.

- Writers own disjoint files and semantic authorities, in isolated workspaces.
- Reviewers read changes cold against the task and governing rules.
- Verification runs against the original reproduction or acceptance contract.
- One integration authority combines the work: whatever the repository's integration policy names, never the swarm itself.

Protects against concurrent edits to one file or authority, build-green/runtime-dead, and scope creep by a worker. Goes wrong when two writers own one registry or constant, tests are adjusted to pass, or "done" is claimed before verification.

Do not let the writer become the sole reviewer or integration authority.

## 6. Red Team

Use when the main risk is a shared assumption, authority leak, unsafe default, or completion overclaim; or for any proposal whose acceptance has consequences.

- Give the red team the proposed synthesis or system, not the discovery narrative.
- Use distinct lenses when the proposal can fail in more than one way: correctness, security, performance, reproducibility, does-it-address-the-objective.
- Ask for a concrete counterexample or missing edge; default to "refuted" when uncertain.
- Require evidence for each claimed break.

Goes wrong when the red team's brief is the proposal's own argument, or a refutation is overruled by majority rather than evidence.

## 7. Recursive Expansion

Use only when a broad domain contains genuinely independent subdomains, most of the space is likely fine, and the parent cannot cheaply enumerate them itself.

- Parent defines the partition and output schema; a light, wide first round.
- Inspect signal; children deepen or subdivide only their own slice where uncertainty or expected information value stays high.
- Recursion ends when subdomains become linear or deterministic, or K consecutive rounds return nothing new.

Avoid uncontrolled agent trees. Every recursive edge must have a reason and stop condition. Goes wrong when expansion is triggered by activity rather than uncertainty, or pruning never happens.

## 8. Hierarchical Decomposition

Use when one synthesis depends on several specialized domains that can each be solved independently and one parent cannot hold the whole plan.

- Domain leads design and run their own sub-harness within the parent's contract and return a typed summary.
- A top-level synthesizer compares the domain conclusions and attacks cross-domain interactions.

The hierarchy should mirror information dependencies, not organization-chart aesthetics. Goes wrong when children re-decide authorization or scope, depth grows without a reason, or child results skip the verification a flat design would give them.

## 9. Consolidate -> Classify -> Separate axes -> Sequence by hazard -> Attack -> Falsify

Use when collapsing, splitting, renaming, or retiring something that **decides**: a tier, role, flag, credential route, permission, or policy field. Always MEDIUM or HIGH depth.

- One lane per candidate *authority axis*, not per directory.
- Each lane returns references already classified by authority type.
- Synthesis names the axes and the target architecture.
- Sequence ordered by hazard, with a causal sentence per boundary, not by convenience.
- Adversarial cross-lane pass on the synthesis.
- Falsification matrix with converse cases.
- Implementation slices only if implementation was already authorized (pattern 5).

Protects against the twin failures of a premature collapse (an authority silently lost, an authority silently widened) and against scope explosion from treating display, persistence, and test references as behavioral. Goes wrong when the vocabulary is deleted before its axes are separated, a grep inventory is mistaken for a consumer map, the sequence is numbered but not causally justified, or the pass is skipped because the lanes agreed.

Detail: `authority-migration.md` and `adversarial-synthesis.md`.

## 10. Multi-phase executable-truth audit

Use for a broad question of the form "does the system that actually executes match the system its architecture claims?" Independent domain lanes reconstruct from code without reading docs, two-lens verifiers deflate the findings, seam tracers and impossible-state hunters force subsystems to meet, three attacks hit the provisional synthesis, and docs are read last to reconcile. Detail: `audit-graph.md`.

## Composition rules

1. Pick by **topology** (task shape) and **stakes**, then size by **independence**. A pattern's stage list is not a headcount.
2. Chain patterns only across a real handoff: 3 -> 5 (root cause established, then implement); 1 -> 2 (survey produced many findings); 4 -> 6 (research produced a recommendation).
3. Every discovery stage that feeds a decision passes through verification (`verification-and-adjudication.md`).
4. **At MEDIUM/HIGH depth, synthesis is not the last stage.** Whichever patterns compose the chain, the cross-lane pass (`adversarial-synthesis.md`) runs on the synthesized architecture before any implementation slice is handed off.
5. Prefer stage-to-stage flow over barriers; use a barrier only where the next stage needs the full prior set.
6. Log what was bounded (top-N, sampling, skipped modality). Silent truncation reads as coverage.
7. Novel harnesses (tournament, staged escalation, self-repair loops) are allowed when the task calls for them. Name the composed pattern in the Harness Design so the retrospective can judge it.
