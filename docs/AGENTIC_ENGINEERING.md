# Advanced Agentic Engineering

Dale OS treats agentic software engineering as a **systems problem**, not a prompting problem.

Individual agents matter, but reliability comes from the harness around them: how work is decomposed, how authority moves, how evidence is carried, how agents hand off, how completion is proved, and how the system recovers when a session or runner dies.

This document captures the advanced operating patterns that emerged from building and running real multi-agent development workflows around ACF Dashboard. The examples are concrete, but the contracts are portable.

> **Retired mechanisms.** The worker/PM loop (AUTORUN) and the durable agent mailbox described in §4 to §6 and §9 were retired in the reference system on 16 October 2026. Their lessons stand; the mechanisms do not.
>
> **Why they were retired.** The system came to run code review on subscriptions instead: Agent Review on every ready PR, and the second-vendor PM answering `HANDOFF:` comments, both with spend caps. With that in place, the pull request itself became the conversation ledger. Handoffs, rulings and findings live in PR comments and checks, pinned to an exact head and readable by any later agent, so a separate transport for agent-to-agent handoff had nothing left to carry. By early October the mailbox was ruled legacy transport. Its dashboard panel read a committed snapshot rather than the live remote. And although the design was declared dormant, every session still loaded its hooks, so agents kept rediscovering it and treating it as live: a second, stale set of instructions competing with the real control plane. The retirement removed the hooks, workflows and scripts in one change and left the history in git.
> Today's control plane is a `HANDOFF:` comment, a second-vendor PM, and the merge lane ([`ci/README.md`](../ci/README.md#the-merge-lane-caller)). The "PM" in §4 is that retired loop's reviewer, not the second-vendor PM.

The executable portable form is the canonical [`swarm` skill](../skills/operator/swarm/SKILL.md). This document explains the architecture around that skill; it is not a second source of truth for the skill contract.

## 1. Harness crafting — design before spawn

Do not begin a hard task by choosing an agent count.

Begin by designing the smallest reasoning system that can answer the question with the required confidence.

A harness design should name:

- **objective** — the exact question or outcome
- **deliverable** — what artifact constitutes completion
- **task topology** — audit, debugging, research, implementation, migration, architecture, adversarial review, reconciliation, or mixed
- **search space** — independent dimensions that can be investigated in parallel
- **dependency graph** — what must be sequential and why
- **uncertainty** — which propositions are unresolved and what evidence would reduce that uncertainty
- **failure modes** — how the workflow could come back confidently wrong
- **evidence standard** — what counts as proof for this task
- **write topology** — who may mutate what, and where writes must remain isolated
- **verification** — how findings will be independently falsified
- **resource plan** — agent count, concurrency, reasoning tier, recursion depth, retry strategy, and adversarial budget
- **stop conditions** — the observable state at which more work stops adding value

The correct harness may use many agents, a few agents, or **zero subagents**. Agent count is never the objective.

### Staged allocation

Do not freeze the whole compute graph up front.

Start broad enough to expose the main uncertainty, inspect the evidence, then:

- expand where uncertainty or expected information value remains high;
- deepen where evidence conflicts;
- prune lanes whose questions are already answered;
- kill dependent branches when a verifier falsifies their premise;
- stop when evidence converges.

The work graph should be allowed to grow **and shrink**.

This is the difference between orchestrating agents and merely parallelizing prompts.

## 2. Graph engineering — engineer relationships, not just components

Agentic systems become hard when authority, state, and evidence cross boundaries. Model those relationships explicitly.

Three graphs matter most.

### Task graph

Nodes are investigations, transformations, reviews, or writes. Edges mean one node depends on another node's output.

Use the graph to distinguish true parallelism from fake parallelism. If two lanes read the same evidence and answer the same question, they are not independent lanes.

### Authority graph

For any consequential fact or decision, ask:

> What is allowed to decide this?

Every governed fact should have one canonical authority. Alternate routes must be explicitly classified as something like:

- fallback;
- migration-only;
- diagnostic-only;
- compatibility-only.

A second unlabeled route is not redundancy. It is competing authority.

This pattern proved useful in ACF Dashboard's financial data architecture, where a machine-readable registry was used to pin one canonical route for governed accounting facts and force alternatives to declare why they existed.

### State-authority graph

Shared mutable state needs a second map:

- who can read;
- who can write;
- who can derive;
- who can overwrite;
- what happens when two actors race;
- what downstream claims become invalid when an upstream state changes.

This is where many "agent bugs" are actually systems bugs.

A correct agent can still produce a bad outcome if the state topology permits stale writeback, duplicate authority, or an implicit overwrite.

## 3. Adaptive multi-agent reasoning

Discovery is not verification.

For consequential work, use at least two different reasoning roles:

1. **investigation** — find candidate mechanisms or conclusions;
2. **falsification** — try to make those findings fail.

A verifier should receive the claim, the evidence surface, and a falsification objective. It should not receive the discoverer's persuasive narrative as its starting point.

At higher risk, add a second adversarial layer that attacks the **synthesis itself**.

Per-finding review can miss:

- an assumption every lane shared;
- a consequence that appears only where two findings interact;
- a missing authority boundary;
- a fail-open path;
- a default value that silently upgrades uncertainty into certainty.

The first synthesis is therefore provisional until the cross-lane architecture has survived attack.

Majority vote is not authority. Evidence is.

## 4. Agentic loops — engineer continuation as a protocol

A useful agentic loop is not "keep asking the model until it says done."

Treat continuation as a state machine with explicit actors and legal transitions.

A production loop should define:

- which actor owns each state;
- which actor may produce the next transition;
- exact state identity, preferably including the source commit/SHA;
- idempotency keys so retries are harmless;
- compare-and-swap or equivalent concurrency protection;
- bounded retry budgets;
- no-progress and oscillation detection;
- explicit side states such as OWNER_GATE or STALLED;
- a restart path that reads durable state rather than chat history;
- a completion state that cannot be self-certified by the implementation worker.

### Two-actor completion

One pattern ACF Dashboard used until 16 October 2026 separated the coding worker from the PM/reviewer.

The worker can implement, test, and submit evidence. It has **no path to COMPLETE**.

Completion can only be entered from PM review after the reviewer independently checks live repository state, remaining acceptance criteria, verification evidence, integration state, and required writeback.

That prevents a model's own "done" narrative from becoming the completion authority.

## 5. Event-driven handoffs

A durable state machine is not enough. Its scheduler must make the next state reachable.

A real failure exposed this distinction: a workflow design used GitHub's `workflow_run` chaining for an alternating worker/reviewer loop. The state machine itself was valid, but the transport could not support an unbounded chain because GitHub limits `workflow_run` chaining depth.

The fix was architectural, not prompt-level:

- make the handoff an explicit event;
- address the specific run;
- wake the *other* actor only;
- emit the event only after the durable transition lands;
- retain a scheduled recovery scan as a safety net, not as the normal scheduler.

The resulting transport was deterministically exercised through 12 alternations before live use.

The lesson is general:

> A state machine can be correct while its scheduler makes later states unreachable.

Test both.

## 6. Evidence plane and control plane must stay separate

Do not let evidence packets become instructions.

A durable mailbox/handoff should distinguish:

### Evidence

Facts, findings, artifacts, provenance, unknowns, verification output.

Evidence is **data**.

### Control

Authorization, routing, requested action, legal next state.

Control is **authority**.

One should not be able to masquerade as the other.

A practical mailbox protocol therefore uses:

- an exact producer/state identity;
- a validated manifest;
- immutable evidence payloads;
- an independent consumer;
- a receipt proving what durable result was promoted;
- a consumed state;
- garbage collection only after receipt validation.

This prevents a persuasive artifact from quietly elevating itself into an instruction.

## 7. Write topology — parallel reasoning does not imply parallel authority

Parallel writers are dangerous when they touch the same semantic authority.

For implementation work:

- survey before writing when the mechanism is uncertain;
- isolate parallel writers by file set **and** by authority;
- do not let two workers mutate the same registry, schema, canonical constant, or state owner unless the integration design explicitly accounts for it;
- route all writes back through one integration authority;
- keep merge, promotion, deploy, destructive mutation, credential changes, and other owner-gated actions outside the swarm's authority unless explicitly granted.

The swarm may produce the work. It does not automatically inherit the right to ship it.

## 8. Observability, recovery, and the death of conversational memory

An agentic system should survive the death of the agent session.

Durable recovery state should be enough to answer:

- what objective is active;
- what state the run is in;
- which actor owns the next action;
- what exact source state the decision was computed from;
- what acceptance criteria remain;
- what evidence has been verified;
- what retries or no-progress cycles have occurred;
- whether an owner gate is blocking continuation.

If recovery requires reconstructing the truth from a chat transcript, the workflow is not durable yet.

Diagnostics should also distinguish **silence** from **failure**. A scanner that exits successfully while operating from the wrong repository root is not healthy simply because it returned exit code 0.

## 9. Field failures that paid for these rules

These patterns were not written as theory first. They were extracted from failures.

### Wrong mailbox selected

A bootstrap scanner returned the first READY mailbox alphabetically. A valid target mailbox existed but was never consumed.

**Rule paid for:** selection must be run-addressed or otherwise unambiguous; evidence handoff needs exact identity.

### Valid transition, lost wake

A transition committed successfully, but the process expected a GitHub token in its environment that had never been explicitly bound into the step.

The durable state was correct. The next actor never woke.

**Rule paid for:** test the transport from durable write through wake-up, not merely the transition function.

### Correct state machine, unreachable later states

The loop initially relied on `workflow_run` chaining, which could not sustain the required alternating depth.

**Rule paid for:** scheduler reachability is an independent correctness property.

### Stale snapshot overwrote newer economic state

A monitoring cycle read a snapshot, awaited an external dependency, then wrote the old snapshot back after newer trade/cash changes had landed.

A focused harness reproduced the race.

**Rule paid for:** map state authority and write ownership; monitoring code should not casually own economic state.

### Competing canonical routes

Financial subsystems accumulated multiple paths capable of answering the same governed fact.

**Rule paid for:** build an authority graph and require one canonical route; make every alternative declare its limited role.

## 10. Compact operating contract

For hard agentic work:

1. **Design the harness before spawning agents.**
2. **Map the task, authority, and state graphs.**
3. **Allocate compute on information value, not agent count.**
4. **Separate discovery from falsification.**
5. **Make high-risk synthesis survive a cross-lane attack.**
6. **Treat continuation as a durable state machine.**
7. **Make completion externally adjudicated when the worker has a conflict of interest.**
8. **Separate evidence from control.**
9. **Use exact identity, idempotency, and concurrency guards.**
10. **Test transport reachability, recovery, and failure states — not only happy-path logic.**
11. **Give parallel writers disjoint semantic authority.**
12. **Stop when the evidence converges or authority runs out.**

## Source examples

The portable rules above were generalized from real systems in ACF Dashboard. The source repository is private, so the snapshots below (ACFDashboard @ `8b956f5`) are cited for provenance and are not publicly readable. The mailbox and AUTORUN documents are retired:

- [Adaptive SWARM meta-orchestrator and harness compiler](https://github.com/SVRN-AGNT/ACFDashboard/blob/8b956f58050e58d8a8631f08c50789be2f45df4a/.claude/skills/swarm/SKILL.md)
- [Harness design contract](https://github.com/SVRN-AGNT/ACFDashboard/blob/8b956f58050e58d8a8631f08c50789be2f45df4a/.claude/skills/swarm/references/harness-design.md)
- [Durable agent mailbox protocol](https://github.com/SVRN-AGNT/ACFDashboard/blob/8b956f58050e58d8a8631f08c50789be2f45df4a/docs/AGENT_MAILBOX_PROTOCOL.md)
- [Event-driven autonomous worker / PM loop](https://github.com/SVRN-AGNT/ACFDashboard/blob/8b956f58050e58d8a8631f08c50789be2f45df4a/docs/AUTORUN_ORCHESTRATOR_PROTOCOL.md)
- [Graph engineering architecture audit](https://github.com/SVRN-AGNT/ACFDashboard/blob/8b956f58050e58d8a8631f08c50789be2f45df4a/docs/audits/GRAPH_ENGINEERING_ARCHITECTURE_AUDIT_v1.md)

These are examples, not runtime requirements. Dale OS should preserve the contracts even when the host, model family, CI system, or orchestration primitives change.
