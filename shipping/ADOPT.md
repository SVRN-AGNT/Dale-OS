# Adopt the Shipping System in a repository

The steps below go in order, and each one is useful on its own. Stop at the level the repository needs: a docs repository may only ever need levels 1 and 2. Each step is one small PR that keeps the repository's existing tests, build and merge rules.

An agent can run this guide with the [`shipping-lanes`](../skills/operator/shipping-lanes/SKILL.md) skill. Steps marked **owner** grant access or touch production, so a person does them.

## Level 0 · Decide three things first

1. **The integration branch.** This is where the Controller merges, for example `main` or `preview`.
2. **What production is,** and the single step that releases to it. That step stays a person's.
3. **Who lands changes today.** Write it down even if the answer is "the owner, by hand". Step 6 replaces it, and nothing else may merge around it.

## Level 1 · Make CI truthful and cheap

### Step 1 · Adopt the shared CI floor

Add two jobs that call the reusable workflows in this repository, pinned to one commit SHA ([`ci/README.md`](../ci/README.md)):

```yaml
permissions:
  contents: read

jobs:
  # ...your existing jobs, e.g. `test`...

  hygiene:
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-hygiene.yml@<sha>
    with:
      ref: <sha>          # the same sha, so the checker matches the workflow

  alert:
    needs: [test]
    if: ${{ always() && (github.event_name == 'schedule' || github.ref_name == github.event.repository.default_branch) }}
    permissions:
      issues: write
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-red-alert.yml@<sha>
    with:
      result: ${{ needs.test.result }}
```

Run `python ci/ci_hygiene.py <repo-root>` from a Dale-OS checkout first. The check is report-only until you pass `strict: true`, so turn strict on once it reports no findings.

**Done when:** the hygiene job is green in strict mode, and a deliberately red trunk run opens one `ci-red` issue that closes on the next green run.

### Step 2 · Every check labelled blocking can block

List the checks your docs or PR template call required or blocking, then compare that list with what branch protection or your merge script actually reads. Wherever they differ, either make the check required or stop calling it blocking.

**Done when:** a deliberately failing run of each blocking check stops a merge. The reference repo found one that could not; see [`reachability-proof`](../skills/operator/reachability-proof/SKILL.md).

### Step 3 · Agent-sized test output

In agent sessions, stay silent while tests are green, print failures first, and put the standard summary line last. CI keeps its full output. A `PreToolUse` hook or an environment flag in the test script both work. In the reference repo the slowest tier dropped from 2,531 lines to 9 ([playbook F6](PLAYBOOK.md#f6)).

## Level 2 · Independent review

### Step 4 · Write the lane map

Copy [`templates/lanes.example.json`](templates/lanes.example.json) and list the paths for L2 (truth) and L3 (held). Put the reviewer's rubric, prompt and scripts, and the lane map itself, in L3, because they judge every later PR. Have a script derive the lane from the changed paths, checking both sides of every rename. Never read a risk level from the PR body.

Make the lane visible: L2 and L3 PRs get a `high-stakes` label and a `[HIGH STAKES]` title prefix, and every agent message that mentions a PR ends with `🔴 HIGH STAKES · #NNNN · <action>` or `🟢 Ordinary · #NNNN`.

**Done when:** a test feeds the script a docs-only change, an ordinary change, a money change, a workflow change, a change to the reviewer rubric or the lane map, and a rename out of a held path, and each gets the right lane.

### Step 5 · Add the Agent Reviewer, report-only

**Owner:** add a model credential as a repository secret first.

Build the reviewer as a workflow that has all of these properties. The reference implementation is `.github/workflows/agent-review.yml` plus `scripts/agent-review/` in the private reference repository.

- It runs on `pull_request_target` and checks out **only the base branch**, with credentials not persisted. The PR is fetched as git objects and read with read-only tools; nothing from it is checked out, installed or run.
- The workflow, prompt and rubric come from the base branch, and their paths are L3, so a PR cannot edit its own judge.
- The verdict is a check run on the exact head SHA. Anything short of clean, including "could not review", reads as not reviewed.
- It uses the rubric in [`templates/REVIEW.md`](templates/REVIEW.md): correctness only, each blocking finding quotes its line at head, nits never block, and an unchanged diff reuses its verdict (`git patch-id --verbatim`).
- It is capped with a spend budget, a process timeout, `timeout-minutes` and a `concurrency` group that cancels in progress. It has no `contents: write` permission and no merge verb.
- It is told to attack the change. An approval that lists no attempted attacks counts as not reviewed.

**Done when:** the reviewer has posted verdicts on real PRs, and a contract test fails if the merger starts reading the verdict before the owner decides it may.

### Step 6 · Second-vendor review on authority lanes

On every L2 and L3 PR, the Builder posts a `HANDOFF:` comment after the Agent Review verdict, and marks the PR ready only after a `CLEAR` on its current head, or 2 hours with no ruling (recorded as "PM timeout"), using [`templates/HANDOFF.md`](templates/HANDOFF.md). The second reviewer is a model from a different vendor, so approval is never one model agreeing with itself. Make the handoff part of the lane checklist, and have something check that the reply exists before the PR is treated as reviewed. A handoff the author may skip is a reviewer nobody calls ([case](../cases/the-reviewer-nobody-called.md)).

A `CORRECT` or `HOLD` blocks ready, a push restarts the clock, and an Agent Review approval never replaces a CLEAR. The timeout keeps a quiet reviewer from stalling the line. Ordinary L0 and L1 work needs only green CI and a passing Agent Review. The reference repo first required the second vendor on every PR. On 14 October the owner dropped that as overly cautious; its written rules are still being updated to match.

## Level 3 · Autonomous landing

### Step 7 · One lander

Pick exactly one automatic merger: a Controller workflow, or a GitHub merge queue if your plan offers one. Never run both. Eligibility is mechanical: not a draft, marked ready, required checks green on the exact head, mergeable, dependencies merged, no hold, and the lane's reviews present. Sessions never merge, enable auto-merge or update branches around it. For a small repository, "the owner merges by hand" is a valid lander; write it down.

**Done when:** a red, conflicting, held or draft PR cannot be merged by the lander, and cannot block a different eligible PR.

### Step 8 · Held scope stops honestly

The lander refuses L3. If no approver exists that the automation cannot impersonate, a person lands L3 changes. The trusted-reviewer list stays empty until a separate identity exists. When the owner delegates merges in writing, the merge commit quotes the delegation and says the merge is unattested.

A hand merge of an L3 PR waits for the second opinion. This covers a push after the PR was marked ready, or a reviewer that has gone quiet, which is why the 2-hour timeout exists alongside the ready-time CLEAR. The current head needs green CI, a passing Agent Review, and a HANDOFF answered `CLEAR` for that head, or 2 hours with no ruling. A `CORRECT` or `HOLD` blocks the merge, and a push needs a new HANDOFF and restarts the clock. Only the owner naming that specific PR waives the wait; blanket approval does not. The merge commit says which path it took.

**Done when:** an L3 PR with a fresh push and no new HANDOFF cannot be hand-merged under the written rule, and each hand-merge commit names its path (CLEAR, timeout, or the owner's per-PR waiver).

### Step 9 · Agents get their own identity before any auto-fix

**Owner:** create a GitHub App for the agents, and a ruleset its token cannot bypass.

Until then, no routine pushes fixes, because it would push under the owner's account and "never merge" would only be an instruction ([playbook F4](PLAYBOOK.md#f4)). Any Actions job that pushes uses an app token, because commits made with the default `GITHUB_TOKEN` do not trigger CI ([F10](PLAYBOOK.md#f10)).

## Level 4 · Measure, then promote

### Step 10 · Measure four numbers on every change to the pipeline

1. The median time from ready to merged, and CI runs per merged PR.
2. Runner minutes per merged PR.
3. Escaped defects: nightly reds traced to a merged PR, and reverts.
4. Reviewer recall on canaries: replay reverted past fixes and check whether the reviewer flags them.

A change that shortens the wait but raises escaped defects is rolled back.

### Step 11 · The reviewer earns blocking power

The owner decides, using the written bar: at least 30 PRs over at least 2 weeks (at least 5 of them held), at least 80% precision on blocking findings, at least 4 of 5 canaries caught, at least 9 of 10 re-runs agreeing, "could not review" on at most 5% of runs, median cost at most $1 and p95 at most $5, median wall time at most 5 minutes, and at most 1 escape. Blocking power is only a veto; an approval never releases held scope. If precision over the latest 20 findings drops below 70%, or 2 canaries are missed, the reviewer returns to report-only automatically.

### Step 12 · Releases

Freeze each promotion at one commit on its own branch, generate its receipt from git, and keep the approval with a person. A post-deploy check that reads production needs the owner's account, secret and written protocol (**owner**).

## Where each repository stands

As of 14 October 2026:

| Repository | Level reached | Next step |
|---|---|---|
| ACFDashboard (private, reference) | 3, with Level 4 partly done: Controller, held scope, report-only reviewer, second vendor on authority and held PRs with a 2-hour timeout (decided; written rule update pending) | Agents' App identity (owner); reviewer measurement script and canaries; shared-layer adoption (held scope) |
| Dale-OS (public) | 1: the layer lives here and passes strict | Lane map; agent review |
| wallet-alpha-lab (private) | Step 1 open in [#149](https://github.com/SVRN-AGNT/wallet-alpha-lab/pull/149), green | Merge (it redeploys the same site code) |
| ACF-Docs (public) | Step 1 open in [#214](https://github.com/SVRN-AGNT/ACF-Docs/pull/214), green | Merge (it redeploys the same site code) |
| chaz-automation (private) | 0: no workflows; vault docs self-merge under a written decision | Step 1 if it gains CI |

The wallet-alpha-lab link resolves only for people with access to that private repository.
