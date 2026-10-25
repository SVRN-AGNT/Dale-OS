# Harness Map

**One page on the whole harness, for a reader who already knows harness engineering.**

A typical Claude Code harness guide has seven layers: project instructions, skills, MCP sources, permission rules
and hooks, an evidence reviewer, effort settings, and a completion goal with a progress file. Those layers help a
single long run finish and leave evidence behind. Dale OS starts from a different question: how a fleet of agent
sessions can work on a financial codebase for months without anyone being able to claim a false state, whether that
is a wrong number reported as reconciled, a PR reported as merged, or a guard reported as running.

The short answer is that authority and evidence are meant to be enforced outside the model. The model writes, reads
and judges. Which commit a verdict covers, and when the lane may merge, are settled by CI and git. Where a rule still
rests on instructions or on a writer's good faith, Known limits says so.

The reference implementation is a private financial dashboard repository. Everything portable is in this repository.

## The seven usual layers, and what each becomes here

| Usual layer | Usual form | Here | Where |
|---|---|---|---|
| Project facts | One focused `CLAUDE.md` | A short constitution that wins on conflict, with a detail document under the same section numbers. Rules there say *when* a playbook must be read ("before editing a file in `selectors/`"), so depth loads by trigger, not at session start. On 14 October 2026 the reference repo cut its instructions from 411 to 225 lines and kept every moved line word for word. | [`shipping/README.md`](../shipping/README.md) status section |
| Saved procedures | One skill per repeated task | Skills are named after **failure classes**, not tasks: `systemic-bug-instinct`, `truth-boundary`, `reachability-proof`, `false-competence-check`. A resolver maps a symptom to the shortest skill route, and compositions say which skills to stack and which to leave out. | [`machine/failure-classes.json`](../machine/failure-classes.json), [`machine/compositions.json`](../machine/compositions.json), `python scripts/dale.py resolve <symptom>` |
| Source access | MCP connectors | Connectors exist, but every fetched page, PR comment and CI log is treated as data, never as instructions. Blocked services are denied in settings, not in prose. | [`ci/README.md`](../ci/README.md) (agent-review caller) |
| Action rules | `permissions` and a `PreToolUse` hook | Limits live in **access**, not in prompts: protected primitives are locked by foundation tests whose consumer allowlist *is* the lock, held paths are derived from the changed files (both sides of a rename), and an agent that pushes needs its own identity with platform-enforced limits. A rule that exists only as an instruction is listed as a gap. | [`risk-kernel`](../skills/operator/risk-kernel/SKILL.md), [`protected-boundary`](../skills/operator/protected-boundary/SKILL.md) |
| Evidence reviewer | A read-only subagent the main agent invokes | Two independent judges the author cannot edit. **Agent Review** runs on every ready PR by an allowlisted author without being asked, so the author cannot skip it: a fresh Claude in CI, prompt loaded from the base branch, the PR read as git objects and never checked out, a typed verdict posted as a check on the exact head SHA, and every blocking finding must carry a quote of the line it cites (a required field; the shared reviewer does not check the quote against the head). **The PM**: on authority work, a second model from a different vendor (Codex) rules `CLEAR`, `CORRECT` or `HOLD` on a `HANDOFF:` naming the head. The author posts that HANDOFF. Held scope can't merge through the lane without one, but outside held scope skipping it is caught only by convention (see Known limits). | [`ci/README.md`](../ci/README.md), [`shipping/templates/`](../shipping/templates/) |
| Reasoning effort | Set per session or subagent | Routed in three layers: the role (routing, coding, review, writing), the capability tier it needs (economical, balanced, frontier), and the concrete model, which is the only perishable part and lives in one dated file per deployment. Escalation to the frontier tier is recorded with its reason. A model is promoted on measured behavior, not on its release notes. | [`machine/model-cost-policy.json`](../machine/model-cost-policy.json) (routing), [`docs/MODEL_EVAL_PROTOCOL.md`](MODEL_EVAL_PROTOCOL.md) (promotion evidence) |
| Completion goal | `/goal` plus `progress.md` | A run never certifies its own completion. Outcomes come from a fixed set (finished, ready for review, needs a person, blocked, stuck, failed, cancelled), and anything outside the set counts as failure. Claims follow state tiers: implemented, pushed, PR open, merged, deployed. Only a state that can be proved gets claimed. | [`completion-contract`](../skills/operator/completion-contract/SKILL.md), [`verify-before-cite`](../skills/operator/verify-before-cite/SKILL.md) |

## What the usual seven layers have no place for

**1. Risk picks the lane, and the lane picks the judges.** A change's lane (docs, ordinary, truth, held) is
derived from the paths it touches and is never self-declared. Ordinary work needs green CI and a passing Agent
Review. No lander checks the review on ordinary PRs, here or in the reference repo, where the Builder waits for it by
rule. Truth work (money, sync, evidence, imports, identity) also goes to the second vendor: it lands on a `CLEAR`,
or after 2 hours with no ruling. Held work (workflows, access, billing, migrations, merge and release tooling,
authority sources) lands only on a `CLEAR` for the current head, never on the timeout. Here the held paths are one
regex, passed by hand to each of the reviewer, PM and merge-lane callers; this repository holds `.github/workflows/`
and `ci/`. The reference repo derives risk from the changed paths with a script instead. See
[`shipping-lanes`](../skills/operator/shipping-lanes/SKILL.md).

**2. One lander, and it re-derives the verdict.** No session merges around the lander. In the reference repository a single Controller
workflow is the only merger. Here, `merge-lane.yml` considers only PRs that carry a HANDOFF, and lands one only when the
gate allows it; a PR without a HANDOFF is left to the repository's own merge rule. For every PR with a HANDOFF, the merge gate
([`ci/merge_gate.py`](../ci/merge_gate.py)) re-reads Codex's own comments and the head's checks at election and again
just before the merge call, so a finding posted after a `CLEAR` still blocks. A push revokes every verdict.
Production promotion is frozen at one commit and needs the owner's written authorisation for that cut; a session
performs the merge only after the full suite is green on it.

**3. Truth states are part of the type system.** Unknown, stale, unavailable, inferred, estimated and observed stay
distinguishable everywhere downstream. Missing evidence is never zero, and analytics degrade or withhold when the
records under them are unresolved. Deterministic code does the arithmetic, replay and reconciliation. The financial
skills ([`skills/financial-truth/`](../skills/financial-truth/)) each own one such check: basis, cash, transfers,
corporate actions, tax character, close-the-books.

**4. The harness has an incident memory, and the memory is gated.** Every real failure becomes a mechanism, not a
story: an append-only mistake log in the reference repo, sanitized cases here ([`cases/`](../cases/)), and an
append-only decision ledger for owner rulings, so a decision made once is never re-asked in a new session
([`latest-authority`](../skills/operator/latest-authority/SKILL.md)). A lesson enters durable memory only through
[`memory-promotion`](../skills/operator/memory-promotion/SKILL.md), so memory gets cleaner rather than just longer.

**5. Guards have to be shown reachable.** A test or alarm that nothing runs is the most common false comfort, so a fix
counts only when it is right, reached, and visible when it fails
([`reachability-proof`](../skills/operator/reachability-proof/SKILL.md); case:
[a guard nothing runs](../cases/a-guard-nothing-runs.md)). A red scheduled run opens an issue that closes itself.

**6. Stopping counts as success.** Crossing a protected boundary, missing evidence or contradicting a standing ruling
ends in a precise stop that names the blocker and what would clear it. The constitution lists hard halts, and a weak
plan is not allowed to become code.

**7. The fleet has a shape.** Builder sessions never merge held scope, never merge around the lander, and never
promote without the owner's word for that cut. A coordinator session talks to the owner and
starts one thread per piece of work. A separate research lane hands findings to the build lane as labelled issues, not
as pasted text. Each session opens with an execution charter (objective, risk class, scope in and out, stop conditions,
verification, writeback), and its context budget scales with the risk class
([`execution-charter`](../skills/operator/execution-charter/SKILL.md); multi-agent work:
[`swarm`](../skills/operator/swarm/SKILL.md), [`AGENTIC_ENGINEERING.md`](AGENTIC_ENGINEERING.md)).

**8. The rules are attacked, not just asserted.** Behavioral, activation and composition evals, a planted-defect bar a
reviewer must clear before it may block ([ADOPT step 11](../shipping/ADOPT.md#step-11--the-reviewer-earns-blocking-power)),
and a standing invitation to break the claims ([`evals/`](../evals/), [`CHALLENGE.md`](../CHALLENGE.md),
[`PROOF.md`](../PROOF.md)).

**9. Tests are feedback; clearance comes from outside.** In the reference repo the portfolio truth engine is a named
component whose manifest lists its exact import closure, and a boundary test fails on any drift, so "the engine" means
the same files everywhere it is copied. A promotion is refused unless an
external Truth Kit, using independent verifiers and planted bugs, has cleared that exact engine digest. A green
in-repo suite never turns that check green, and a new money rule needs independently written test books before any
clearance can name it. Financial extraction follows the same split: a model may read a document's layout, but code
reads every number from the cells, and failed reconciliation checks block the save. The public financial skills carry
the rule ([`financial-evidence-grade`](../skills/financial-truth/financial-evidence-grade/SKILL.md)); the kit itself
is private.

## Known limits

These are open, and a reviewer should look at them first.

- **Some rules are still convention.** The `HANDOFF:` trigger and the Codex round budget (a full review after round 3,
  the owner's word from round 6) can't be refused by CI. The author posts the trigger.
- **No human approver the automation cannot impersonate.** The trusted-reviewer list is empty by design, so held scope
  relies on the cross-vendor gate rather than on a person's approval.
- **Agent identity.** The reference repo merged a GitHub App identity for agents on 14 October 2026. Whether every
  pushing agent in every repository uses it is not confirmed here; where it doesn't, limits on pushing agents come
  partly from instructions.
- **Adopters' held paths are narrower than the doctrine.** The lane table holds access, billing, migrations and
  authority sources, but each repository's regex decides. Some adopters hold only `.github/workflows/`, and this
  repository holds `.github/workflows/` and `ci/` but not `CLAUDE.md` or its skills; a PR that edits `AGENTS.md` gets a PM `HOLD`
  instead, which the gate also refuses.
- **Adopters run older layer code.** Callers pin the shared workflows to a commit, and some adopting repositories pin
  commits from before the latest changes here. What this repository documents is ahead of what some of them run.
- **The reviewer gates before it has earned it.** Rule 5 says a reviewer reports without blocking until it clears a
  measured bar, but the merge gate already requires a passing Agent Review on HANDOFF and held PRs, and no record shows
  the bar was cleared. The second vendor's CLEAR is the check that holds the line meanwhile.
- **Some merged trees were never tested.** Evidence counts only for the exact tree it judged. The shared merge lane
  refuses a PR that GitHub reports as behind its base, but GitHub reports that only where branch protection requires
  branches to be up to date; without that setting a behind PR can merge, a wider form of the same gap. The reference
  repo's Controller makes one exception by owner ruling (16 October 2026): a held PR behind the base still merges on
  its reviewed head when the base changed none of its files. That saves a refresh and a second-vendor round each time
  the base moves, but non-overlapping paths can still interact (dependencies, generated files, behavior). A merge
  queue that tests the prospective merge would close both.
- **A repository writer can forge evidence.** The merge gate defends against the PR itself and against timing, but
  anyone with write access (the owner, the Claude app, agent sessions) could run a modified workflow on another
  branch and post a passing check. Closing this needs review checks posted by a dedicated GitHub App whose key only
  the default branch can use. The full threat model is in the merge-lane section of [`ci/README.md`](../ci/README.md).

## For a reviewer comparing this with their own harness

If you build harnesses yourself, these are the questions where an outside view helps most:

1. **What here is enforced only by instruction?** Name any rule an agent could break with nothing failing in CI,
   git or access control.
2. **Where would you collapse layers?** Two judges, lanes, a merge gate and a constitution with a detail document all
   cost tokens, CI minutes and latency. Which parts don't pay for themselves on a one-person project?
3. **Is the cross-vendor reviewer independent?** Both reviewers read the same diff and the same PR description, so
   their errors may be correlated. What would you measure to tell?
4. **How do you handle long-run state?** This system relies on threads, issues, an append-only ledger and gated
   memory instead of a `progress.md`. Does yours recover better after compaction or a dead runner?
5. **What is missing?** For example: cost accounting per accepted change, rollback drills, or a failure class you have
   seen that the [resolver](../machine/failure-classes.json) doesn't route.

## Pointing an agent at this repository

Give your agent the repository and ask it to start at [`AGENTS.md`](../AGENTS.md). That file sets the read order and
the routing table, and it warns against loading the whole tree. To try one piece instead of the whole system:

- install a plugin: `/plugin install dale-os-operator --marketplace SVRN-AGNT/Dale-OS`;
- route a symptom: `python scripts/dale.py resolve symptom-patch --json`;
- adopt the review-and-merge pipeline step by step: [`shipping/ADOPT.md`](../shipping/ADOPT.md).
