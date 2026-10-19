# Shared CI layer

A small floor that every repository can stand on, so CI behaves the same way
everywhere without each repository copying the same YAML. It is deliberately
thin: each repository keeps its own tests, build and merge rules. The layer
only owns the parts that should never differ between repositories.

| Piece | What it does | How a repository adopts it |
|---|---|---|
| [`ci-red-alert.yml`](../.github/workflows/ci-red-alert.yml) | Keeps one issue open while a scheduled or trunk run is red; closes it when green | Add an `alert` job that `needs:` the watched job |
| [`ci-hygiene.yml`](../.github/workflows/ci-hygiene.yml) + [`ci_hygiene.py`](ci_hygiene.py) | Checks the repository's workflows against the floor below | Add a `hygiene` job; report-only until `strict: true` |
| [`ci-pm-review.yml`](../.github/workflows/ci-pm-review.yml) + [`pm_review.py`](pm_review.py) | Answers every Claude `HANDOFF:` comment with a second-vendor (OpenAI Codex) PM review: a `PM REVIEW —` comment and a `PM Review` check on the exact head | Add the caller below, with `provider: chatgpt` (no key) or an `OPENAI_API_KEY` repository secret |
| [`ci-agent-review.yml`](../.github/workflows/ci-agent-review.yml) + [`agent_review/`](agent_review/review.mjs) | An independent Claude instance reviews every non-draft PR by an allowlisted author and posts an `Agent Review` check on the exact head, billed to the Claude subscription only | Add the caller below; the `CLAUDE_CODE_OAUTH_TOKEN` organization secret reaches every repository |
| [`ci-merge-lane.yml`](../.github/workflows/ci-merge-lane.yml) + [`merge_gate.py`](merge_gate.py) | Merges a PR whose exact head carries a HANDOFF once Agent Review passed on it and the PM's CLEAR still stands when re-derived at merge time; held scope never merges on the 2-hour timeout | Add the caller below; an `INTEGRATION_TOKEN` with the Workflows permission lets it merge PRs that change workflow files |

## The floor

`ci_hygiene.py` checks these rules. Each one exists because its absence costs
runner time or hides a failure:

- **timeout**: every job on a runner sets `timeout-minutes`. Without one, a hung
  job runs for up to six hours.
- **permissions**: every workflow declares top-level `permissions`, so the
  token never silently gets the repository default.
- **concurrency**: a workflow triggered by `pull_request` cancels superseded
  runs, so pushing twice to a PR does not test both commits to the end.
- **double-run**: a workflow on `pull_request` does not also run on `push` to
  every branch. Without a branch filter, each PR commit is tested twice.
- **shared-ref**: every use of this layer in a repository pins the same ref, so
  one repository never runs two versions of the floor at once.

Run it locally with `python ci/ci_hygiene.py <repo-root>`.

## Pinning

Callers pin a commit sha, never a branch, so a change here cannot change
another repository's CI without that repository taking the new sha in a
reviewed PR. `ci-hygiene.yml` takes the same sha as its `ref` input, so the
workflow and the checker it runs always come from the same commit.

## Runners

`ci-hygiene.yml` takes a `runner` input (default `ubuntu-latest`). Private
repositories may pass `ubicloud-standard-2`: its jobs mostly run under a
minute, and GitHub bills each one as a full minute, so a runner a third of the
price cuts that caller's bill. Public repositories keep the default, since
GitHub bills them nothing.

Only jobs whose token is read-only may leave GitHub-hosted runners (owner,
2026-10-19). A job that holds `INTEGRATION_TOKEN`, a GitHub App key, the review
OAuth token or an API key, or whose `GITHUB_TOKEN` can write to a pull request
(comments, labels, its text, checks or statuses), stays on `ubuntu-latest`: on
another provider's runner it could leak the credential or forge what the merge
gate reads. That is why `ci-merge-lane.yml`, `ci-agent-review.yml` and
`ci-pm-review.yml` have no `runner` input. A caller's own jobs follow the same
rule: builds and tests with `contents: read` may move; anything that writes to
a pull request may not.

## The PM caller

GitHub runs `issue_comment` workflows from the default branch, so the caller
only works once it is merged there. A personal account has no organization
secrets, so each repository needs its own `OPENAI_API_KEY` secret. Without it
the PM says "not configured" on the PR and any review timeout applies.

```yaml
name: pm-review
on:
  issue_comment: { types: [created] }
  workflow_dispatch: { inputs: { comment_id: { type: string, required: true } } }
permissions: { contents: read }
concurrency: { group: 'pm-review-${{ github.event.comment.id || inputs.comment_id }}', cancel-in-progress: false }
jobs:
  pm:
    if: (github.event_name == 'workflow_dispatch' && github.ref_name == github.event.repository.default_branch) || startsWith(github.event.comment.body, 'HANDOFF:')
    permissions: { contents: read, issues: write, pull-requests: write, checks: write, actions: read }
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-pm-review.yml@<sha>
    with:
      ref: <sha>
      comment_id: ${{ github.event.comment.id || inputs.comment_id }}
      held_paths: '^\.github/workflows/'   # add the repository's own held paths
      # optional: control_issue, contract_path, allowed_authors, model, effort
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

The `concurrency` group stops a redelivered comment from billing a second
review. A Claude session only reaches the PM by posting a comment through the
`claude` app that starts with `HANDOFF:` and names the PR's head as a full
40-character sha ([`shipping/templates/HANDOFF.md`](../shipping/templates/HANDOFF.md)).

### Without an API key: `provider: chatgpt`

Codex's own GitHub review runs on the owner's ChatGPT plan, so the PM can rule
from it with no `OPENAI_API_KEY`. Turn Codex's automatic review off (it would
review every push and spend the plan's 5-hour window; measured about 2.5% per
review) and let the HANDOFF ask: it carries `@codex review` on a line of its
own. The PM reads only comments written by `chatgpt-codex-connector[bot]`, an
app login GitHub reserves. No findings on the head and no failed check is
`CLEAR`; any finding, of any priority, or a failed or not-reviewed (`action_required`) check is `CORRECT`, even before Codex marks its review completed (priority
is Codex's urgency, not whether the code is wrong; a finding the author thinks
mistaken goes to the owner). A failed run stops counting only when a successful
run that started after it is provably the same check, from GitHub's own run
records (`check_identity` in `pm_review.py`): the same check name and workflow
file, defined on the default branch or as a re-run attempt of the same workflow
run (a dispatch or push counts as the default branch only when its commit is
on it). Job checks prove their run through the job link GitHub writes. `Agent
Review` only claims its run attempt, in `external_id`, and that claim must name
a real run of the same file and fall inside it; whoever could forge the claim
could already rewrite the failed check, so it adds no authority. A name or app
alone proves nothing, and a skipped or neutral run sets nothing aside. The PM
reads run records, so its caller grants `actions: read`; without it every
failure keeps counting.
A PR that edits an `AGENTS.md`, or a path in
`instruction_paths` (added to AGENTS.md, never replacing it),
gets `HOLD`, because Codex reads those as its review instructions from the PR.
Codex's review cannot raise `OWNER GATE`, and it cannot apply a
`contract_path` or `control_issue` contract: with either set, the PM gives no
ruling. Put the contract in the `## Code Review Rules` section of AGENTS.md,
which Codex applies.

```yaml
on:
  issue_comment: { types: [created, edited] }
  workflow_dispatch: { inputs: { comment_id: { type: string, required: true }, pr: { type: string, required: true } } }
permissions: { contents: read }
jobs:
  pm:
    if: >-
      (github.event_name == 'workflow_dispatch' && github.ref_name == github.event.repository.default_branch)
      || (github.event.action == 'created' && startsWith(github.event.comment.body, 'HANDOFF:'))
      || (github.event.comment.user.login == 'chatgpt-codex-connector[bot]' && (contains(github.event.comment.body, 'codex-review-state:v1') || contains(github.event.comment.body, 'codex-review-receipt:v1')))
    concurrency: { group: 'pm-review-${{ github.event.issue.number || inputs.pr }}', cancel-in-progress: false }
    permissions: { contents: read, issues: write, pull-requests: write, checks: write, actions: read }
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-pm-review.yml@<sha>
    with:
      ref: <sha>
      comment_id: ${{ github.event.comment.id || inputs.comment_id }}
      held_paths: '^\.github/workflows/'
      provider: chatgpt
      expected_pr: ${{ inputs.pr }}
```

Give the repository's AGENTS.md a `## Code Review Rules` section (the heading
Codex's docs name; keeping a `### Review guidelines` subheading inside it
matches older readers) that tells
Codex to take review instructions only from that section and to treat every
file the PR changes as content under review. Codex reads AGENTS.md from the PR,
but a PR that edits it is held, so the guidelines it applies are the base
branch's. A dispatch names both the comment and its PR, so it takes the same
per-PR lock as comment events; the PM refuses a comment on any other PR.

The HANDOFF run sets `PM Review` to in progress; Codex's summary comment
changing to completed, or its receipt for the head, runs the PM again, and it
rules for the latest HANDOFF naming that head. Codex's `has_any_findings` covers
the whole PR, so a head with no findings of its own is CLEAR only once Codex's
"no major issues" receipt names it. Whichever arrives second rules, so a review that finished
before the HANDOFF is answered at once.

A finding Codex posts inline, or a check that fails, after the last event the
PM saw wakes nothing (review events would run the PR's own copy of the
workflow, so the PM never listens to them). So with `provider: chatgpt`, a
review timeout counts only after a dispatch re-run of the HANDOFF on the head,
from the default branch, still gives no ruling; that run reads every finding
and failed check on the head. The same re-run comes before merging on a
`CLEAR`, since a finding Codex posts inline after the `CLEAR` wakes nothing.
Only a run that concluded `success` and logged the PM's notice for that head
(`the CLEAR on <head> still stands`, or `Waiting on Codex's review of <head>` /
`Waiting on Codex's receipt for <head>` before a timeout) counts; a failed,
cancelled or refused run does not.

With `provider: chatgpt` a `CLEAR` is not final for its head. A later Codex
summary or receipt, a repeat HANDOFF, or a dispatch re-reads the head, and a
finding or failed check found then posts a `CORRECT` (or `HOLD`) that replaces
the `CLEAR`. Nothing ever turns a `CORRECT` or `HOLD` into a `CLEAR` on the same
head; that takes a push and a new HANDOFF.

**The round budget (owner ruling, 2026-10-19).** Every ruling the PM posts on a
PR is a Codex round, whatever its verdict or head, and rounds spent before this
rule count. The PM counts its own earlier ruling comments on the PR, one per
`PM-HANDOFF-CONSUMED` id (a ruling that replaces a `CLEAR` on the same HANDOFF
stays in that round), and adds one line to the comment and the `PM Review`
check:

| Round | The line says |
|---|---|
| 1, 2 | `Codex round N on this PR.` |
| 3 | Before the next HANDOFF, run a full Claude review of the whole PR and check whether to split it (on a `CLEAR`: if the PR changes again). |
| 4 | Round 5 goes ahead; round 6 needs the owner's word. |
| 5 and later | Before the next HANDOFF, get the owner's word for the next round. |

CI cannot refuse a round, because `@codex review` starts Codex by itself, so
the budget holds by convention; the count makes a breach visible in the ruling
the session acts on. A run with no ruling is not a round. The count reads
comments by `github-actions[bot]`, which a workflow on a PR branch can also post
as; a forged ruling can only raise the count, which brings the stop sooner.

To answer a HANDOFF posted before the caller existed, run the workflow by hand
from the default branch with that comment's id (and, for `provider: chatgpt`, its PR
number). A dispatch from any other branch
is refused: it would run that branch's copy of the reviewer.

## The agent-review caller

The Claude reviewer runs on `pull_request_target`, so the caller, the reviewer
and its prompt always come from the merged base: a PR cannot edit its own
judge, and nothing from the PR is checked out or run. It bills only the Claude
subscription (`CLAUDE_CODE_OAUTH_TOKEN`, from `claude setup-token`); any API
key is stripped from the reviewer's environment. A subscription usage limit
gives `action_required` ("not reviewed"), never an API bill.

```yaml
name: agent-review
on:
  pull_request_target: { types: [opened, reopened, synchronize, ready_for_review] }
  workflow_dispatch: { inputs: { pr: { type: string, required: true } } }
permissions: { contents: read }
concurrency: { group: 'agent-review-${{ github.event.pull_request.number || inputs.pr }}', cancel-in-progress: true }
jobs:
  review:
    if: (github.event_name == 'workflow_dispatch' && github.ref_name == github.event.repository.default_branch) || (github.event_name == 'pull_request_target' && github.event.pull_request.draft == false)
    permissions: { contents: read, pull-requests: write, checks: write, actions: read }
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-agent-review.yml@<sha>
    with:
      ref: <sha>
      pr: ${{ github.event.pull_request.number || inputs.pr }}
      held_paths: '^\.github/workflows/'   # add the repository's own held paths
      # optional: base_ref, allowed_authors, daily_cap, model, budget_usd
    secrets:
      claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

Only same-repository PRs by an allowlisted author reach the model, so on a
public repository a stranger's PR never spends the subscription. The reviewer
has file-reading tools only (no shell, not even git: `git grep -O` runs
commands), no network tool, and never reads PR comments; any credential is
redacted from the verdict it posts.

## The merge-lane caller

Owner ruling, 2026-10-16: held PRs must merge "via our autonomous flow", with no
person typing "merge". The lane merges a PR when, on its exact head:

1. a HANDOFF names the head (posted through the `claude` app);
2. the PM's latest ruling is CLEAR **and** re-deriving it now from Codex's own
   comments and the head's checks (the PM's own functions) still gives CLEAR,
   so a Codex finding posted after the CLEAR blocks the merge;
3. the newest `Agent Review` passed (proven to come from the default branch's `agent-review.yml`), the newest run of each `required_workflows` file on the head passed (GitHub's workflow-run record, not a check by name), and no check other than the PM's own is still running, held or not.

A held PR never merges on the 2-hour timeout. A PR with no HANDOFF is left to
the repository's own rule. An `owner-hold`, `do-not-merge` or `integration-hold`
label stops it; the repository variable `MERGE_LANE=off` switches the lane off.

```yaml
name: merge-lane
on:
  workflow_run: { workflows: [pm-review, agent-review, <CI workflow name>], types: [completed] }
  workflow_dispatch:
  schedule: [{ cron: '17 */2 * * *' }]   # wakes it after a timeout passes or a hold label comes off
permissions: { contents: read }
jobs:
  lane:
    # Only the default branch's copy may run on a dispatch: it holds INTEGRATION_TOKEN.
    if: github.event_name != 'workflow_dispatch' || github.ref_name == github.event.repository.default_branch
    permissions: { contents: write, pull-requests: write, issues: read, checks: read, actions: read, statuses: read }
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-merge-lane.yml@<sha>
    with:
      ref: <sha>
      held_paths: '<the same regex the PM caller passes>'
      required_workflows: |                # the repository's CI workflow files, one per line; '' only with no CI
        .github/workflows/<ci>.yml
    secrets:
      INTEGRATION_TOKEN: ${{ secrets.INTEGRATION_TOKEN }}   # stored ONLY in the `merge-lane` environment
```

Store `INTEGRATION_TOKEN` only as a secret of a `merge-lane` environment whose deployment branches are the
default branch alone, never as a repository or organization secret: same-repository `pull_request` runs receive
every repository secret, so a PR adding a workflow could use the token to merge itself before any review.

**Threat model.** The gate decides on evidence; this is what it defends and what it trusts.

- *Defends against the PR itself:* everything on the PR head, including code its workflows run. Every
  `pull_request` workflow in these repositories gets a read-only `GITHUB_TOKEN`; a PR can only change that by
  changing `.github/workflows/`, which is held scope and needs Codex's CLEAR on that exact diff.
- *Defends against timing:* findings that land after a CLEAR, pushes between reads, mergeability changing, and
  re-runs (two reads 90s apart, the exact head on the merge call, live re-derivation of the PM ruling).
- *Trusts the default branch's workflows* (`agent-review.yml`, `pm-review.yml`, the required CI files), GitHub's own
  records (workflow runs, check-run app, comment editor), and Codex's app as the author of Codex's comments.
- *Does not defend against a repository writer deliberately forging evidence* (Dale, the Claude app, agent
  sessions): a writer can run a modified workflow on another branch whose `GITHUB_TOKEN` posts a check as
  `github-actions` on any sha. GitHub has no native way to tell workflows apart inside that app. Closing this needs a
  dedicated review GitHub App whose key lives only in an environment limited to the default branch, the review
  checks posted as that App, and the gate (plus a ruleset) requiring that App's id; that is an owner action.

Known limit, accepted because held scope also needs Codex's CLEAR on the same head: the `Agent Review` check is
proven by the run that posted it, not by who last set its conclusion, so a workflow a PR adds could restate it; that
PR changes `.github/workflows/`, is held, and Codex reviews the workflow it adds. CI is read from GitHub's
workflow-run records, which no posted check can stand in for. The
merge token may bypass branch rules, so the lane itself merges only from a merge-ready state: `clean`, `has_hooks`, or `unstable` with every commit status green. `blocked`, `behind`, `dirty`, `draft` and `unknown` are refused.
Write access can edit any comment and the author stays Codex, so a Codex comment, review or finding last edited by
anyone else blocks the PR (read through GraphQL's `editor`). A completed Codex review of the head that yields no
readable ruling never reaches the 2-hour timeout. A caller's `--held false` cannot override the gate's own held paths.
`check --settle` applies the same merge-ready test to its settled read; a caller whose own rule makes another state
normal names the full list in `MERGE_READY_STATES`. A required workflow's dispatched run counts only from the default
branch, and an Agent Review pass is sunk by any other check claiming the same run that failed or is still running.
The run an Agent Review claims must be one GitHub started for this head (its run record's `head_sha`), so a check
cannot borrow a trusted run that reviewed another PR; a dispatched review records the default branch's tip, so the
gate does not count it and the PR's own `pull_request_target` run must be re-run instead.

`workflow_run`, not `pull_request_target`: GitHub blocks the latter by default
in public repositories from 2026-11-02 (second-brain #210). GitHub refuses to
let `GITHUB_TOKEN` merge a PR that changes `.github/workflows/`, so the lane
merges with `INTEGRATION_TOKEN` (Contents, Pull requests and Workflows: read and
write) and says plainly when a merge was refused for lack of it.

## What stays per repository

- the tests and the build;
- which checks are required and who may merge;
- whether a nightly or trunk workflow exists at all.

The layer reports. It never merges, deploys or approves anything; the PM
rules on a head, and a person or the repository's own merge rules act on it.
