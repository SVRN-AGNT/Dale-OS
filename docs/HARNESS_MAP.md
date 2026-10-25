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

## What runs where

- **Builders** are Claude Code sessions. They open PRs and post the `HANDOFF:` that asks for the second vendor through
  the `claude` GitHub app; a HANDOFF posted any other way does not count.
- **Agent Review** is a separate headless Claude Code run on GitHub Actions, billed to the Claude subscription. It
  runs this repository's reviewer code (other repositories pin a commit of it) against the merged base, with
  file-reading tools only, and sees the PR's title and description only after its own pass over the diff.
- **The PM** is Codex's GitHub app, reviewing on the owner's ChatGPT plan when a HANDOFF asks. A Python workflow
  ([`ci/pm_review.py`](../ci/pm_review.py)) reads only comments Codex's app wrote and posts the ruling and a
  `PM Review` check on the head.
- **The merge lane** ([`ci/merge_gate.py`](../ci/merge_gate.py)) runs on GitHub Actions. Its merge token lives in an
  environment only the default branch can use, and it never checks out or runs the PR.
- **Runners** are GitHub-hosted. In private repositories, jobs with a read-only token may run on Ubicloud.

The reference app's own stack, hosting, data stores and endpoints are left out on purpose
([`PUBLIC_BOUNDARY.md`](PUBLIC_BOUNDARY.md)). Nothing above depends on them.

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

**10. Cost is a design constraint, learned the expensive way.** Each rule below answers a cost the system actually
paid, not a guess. The principle is in [`machine/model-cost-policy.json`](../machine/model-cost-policy.json): capability is a
budgeted resource, not a default setting, and no saving may trade away accounting, provenance, authority or safety.

| What it cost | What changed |
|---|---|
| GitHub bills each job rounded up to a whole minute. In the reference repo one PR run billed 10 minutes for about 7.4 real ones, a docs-only push paid it in full, and the Actions budget hit its monthly cap in August 2026 | Since 22 August a first job asks one question (did anything outside docs change?) with no checkout or install: one billed minute that can save nine. Jobs that cannot block a merge skip drafts |
| Heads that only merged in the base used 30% of PR CI minutes (973 of 3,279 billed minutes over 200 runs, 13 and 14 October) | Builders refresh the base only to fix a conflict, pick up code they need, or once before a held PR's final HANDOFF ([rule 16](../shipping/README.md)) |
| The same whole-minute bill on short, read-only jobs, at GitHub's full per-minute price | Jobs with a read-only token may run on a runner about a third of the price (`ubicloud-standard-2`). Anything holding a credential or able to write to a PR stays on GitHub, so a cheaper runner can never forge what the merge gate reads (owner, 19 October; [`ci/README.md`](../ci/README.md#runners)). Public repositories stay on GitHub, which bills them nothing |
| Codex's automatic review used about 2.5% of the owner's 5-hour ChatGPT window per push, and asking it on every PR was judged overly cautious (14 October) | Automatic review is off. The second vendor is asked once per finished change, only after CI and Agent Review are green, only on truth and held work in the reference repo (here the lane lands only PRs that carry a HANDOFF), and `@codex` appears nowhere else. Rounds are budgeted: a full review and split check after round 3, the owner's word from round 6 |
| This repository's PR #54 took six rounds, most of them on one class of mistake (one doc contradicting another) found and fixed one line at a time (25 October) | One purpose per PR, and before each HANDOFF the Builder sweeps the whole PR for every instance of each class a reviewer could flag, not only the flagged line (owner, 25 October) |
| A paid eval triggered by a PR path re-ran on every push while the trigger file stayed in the diff | The targeted paid probe runs only by manual dispatch, and the full paid eval only on dispatch or a deliberate push to its verification branch ([report](reports/CROSS_MODEL_VERIFICATION_2026-08-07.md)) |

Agent Review bills only the Claude subscription (any API key is stripped from its environment), under a daily cap, a
per-review usage cap counted in notional dollars, a job timeout and a concurrency group, so a usage limit reads as "not reviewed", never as an API bill.
The numbers that keep this honest are in [ADOPT step 10](../shipping/ADOPT.md#step-10--measure-four-numbers-on-every-change-to-the-pipeline): runner minutes per
merged PR are measured beside escaped defects, and a change that shortens the wait but raises escaped defects is
rolled back.

## What the record shows

[The second-vendor record](reports/SECOND_VENDOR_RECORD_2026-10-25.md) covers 103 PRs and 307 PM rulings in five
repositories, 16 to 25 October 2026, rebuilt from GitHub by [`scripts/pm_record.py`](../scripts/pm_record.py).

- 288 rulings answered a HANDOFF posted after Claude's Agent Review had passed the head. In those, Codex made 271
  findings, 133 of them P1, across 61 PRs. 43 PRs drew at least one P1.
- 41 PRs cleared on their first ruling. Of the 63 PRs whose rulings state a round, the median took 2 rounds and 13
  went past round 5.
- Findings are counted, not checked for validity, so they show the reviewers disagree, not that either was right.
  Nothing measures what both reviewers missed.

Which rules CI or git enforce, and which rest on convention:

| Rule | Enforced by | Evidence |
|---|---|---|
| A verdict covers one exact head; a push revokes it | Merge gate | [`ci/test_merge_gate.py`](../ci/test_merge_gate.py): "a HANDOFF for another head does not count", "a moved head is not merged" |
| Only Codex's app can supply the review; a forged or edited copy blocks | Merge gate | "a forged CLEAR from another login does not count", "a Codex comment edited by someone else blocks the merge" |
| A finding posted after the CLEAR still blocks | Merge gate, which reads twice, 90 s apart, before merging | "a Codex finding posted after the CLEAR blocks the merge", "a finding that lands between the reads stops the merge" |
| Agent Review counts only from the default branch's workflow, run for this head | Merge gate | "a newer Agent Review from a PR-branch copy of agent-review.yml does not count", "a pass claiming a run started for another PR's head blocks" |
| Held scope never merges on the timeout | Merge gate | "held scope waits for a CLEAR even 4 hours after the HANDOFF" |
| Ask the second vendor only after Agent Review passes | Convention | 288 of the record's 307 rulings answered a HANDOFF posted after Agent Review passed; 19 did not (the record leaves out 14 made before Codex finished) |
| The round budget (owner's word from round 6) | Convention; the PM states it in every ruling | 13 of 63 PRs went past round 5 |
| One purpose per PR; sweep by class before a HANDOFF | Convention | Not measured |

The merge gate's suite runs 132 named checks. It cites Codex findings on this repository's PR #41 (17 P1, 3 P2)
20 times, each beside the checks that finding produced.

## Known limits

These are open, and a reviewer should look at them first.

- **Some rules are still convention.** The `HANDOFF:` trigger and the Codex round budget (a full review after round 3,
  the owner's word from round 6) can't be refused by CI. The author posts the trigger. The table above lists them,
  with what the record shows for each.
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
  the bar was cleared. The second vendor's CLEAR is the check that holds the line meanwhile; in the record Codex
  flagged a P1 on 43 PRs after Agent Review had passed them.
- **Some merged trees were never tested.** Evidence counts only for the exact tree it judged. The shared merge lane
  refuses a PR that GitHub reports as behind its base, but GitHub reports that only where branch protection requires
  branches to be up to date; without that setting a behind PR can merge, a wider form of the same gap. The reference
  repo's Controller makes one exception by owner ruling (16 October 2026): a held PR behind the base still merges on
  its reviewed head when the base changed none of its files. That saves a refresh and a second-vendor round each time
  the base moves, but non-overlapping paths can still interact (dependencies, generated files, behavior). A merge
  queue that tests the prospective merge would close both.
- **The second vendor's quota is shared, and the PM doesn't read it.** One ChatGPT plan backs the PM in every
  repository and the owner's own Codex use. Codex often says when the window is spent, with a "usage limits" comment
  (55 in the record), but the PM does not parse it. Sometimes it says nothing: on 25 October its status read
  "Running" for about two hours until the window reset, and the PM waited. The workaround is procedural: check the
  quota before re-asking. Rounds count rulings, so a re-ask on a head that got no ruling stays the same round.
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
3. **Is the cross-vendor reviewer independent?** Both reviewers read the same diff, so their errors may be
   correlated. The record shows their findings disagree (Codex flagged a P1 on 43 PRs after Agent Review had passed them), but
   not which were right or what both missed. What would you measure to tell?
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
