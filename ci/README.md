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
    permissions: { contents: read, issues: write, pull-requests: write, checks: write }
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
mistaken goes to the owner). A PR that edits an `AGENTS.md`, or a path in
`instruction_paths` (added to AGENTS.md, never replacing it),
gets `HOLD`, because Codex reads those as its review instructions from the PR.
Codex's review cannot raise `OWNER GATE`, and it cannot apply a
`contract_path` or `control_issue` contract: with either set, the PM gives no
ruling. Put the contract in the `## Review guidelines` section of AGENTS.md,
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
    permissions: { contents: read, issues: write, pull-requests: write, checks: write }
    uses: SVRN-AGNT/Dale-OS/.github/workflows/ci-pm-review.yml@<sha>
    with:
      ref: <sha>
      comment_id: ${{ github.event.comment.id || inputs.comment_id }}
      held_paths: '^\.github/workflows/'
      provider: chatgpt
      expected_pr: ${{ inputs.pr }}
```

Give the repository's AGENTS.md a `## Review guidelines` section that tells
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

## What stays per repository

- the tests and the build;
- which checks are required and who may merge;
- whether a nightly or trunk workflow exists at all.

The layer reports. It never merges, deploys or approves anything; the PM
rules on a head, and a person or the repository's own merge rules act on it.
