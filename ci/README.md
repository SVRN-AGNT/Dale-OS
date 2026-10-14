# Shared CI layer

A small floor that every repository can stand on, so CI behaves the same way
everywhere without each repository copying the same YAML. It is deliberately
thin: each repository keeps its own tests, build and merge rules. The layer
only owns the parts that should never differ between repositories.

| Piece | What it does | How a repository adopts it |
|---|---|---|
| [`ci-red-alert.yml`](../.github/workflows/ci-red-alert.yml) | Keeps one issue open while a scheduled or trunk run is red; closes it when green | Add an `alert` job that `needs:` the watched job |
| [`ci-hygiene.yml`](../.github/workflows/ci-hygiene.yml) + [`ci_hygiene.py`](ci_hygiene.py) | Checks the repository's workflows against the floor below | Add a `hygiene` job; report-only until `strict: true` |
| [`ci-pm-review.yml`](../.github/workflows/ci-pm-review.yml) + [`pm_review.py`](pm_review.py) | Answers every Claude `HANDOFF:` comment with a second-vendor (OpenAI Codex) PM review: a `PM REVIEW —` comment and a `PM Review` check on the exact head | Add the caller below and an `OPENAI_API_KEY` repository secret |

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
jobs:
  pm:
    if: github.event_name == 'workflow_dispatch' || startsWith(github.event.comment.body, 'HANDOFF:')
    permissions: { contents: read, issues: write, pull-requests: write, checks: write }
    uses: Tataku/Dale-OS/.github/workflows/ci-pm-review.yml@<sha>
    with:
      ref: <sha>
      comment_id: ${{ github.event.comment.id || inputs.comment_id }}
      # optional: control_issue, contract_path, held_paths, allowed_authors, model, effort
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

To answer a HANDOFF posted before the caller existed, run the workflow by hand
with that comment's id.

## What stays per repository

- the tests and the build;
- which checks are required and who may merge;
- whether a nightly or trunk workflow exists at all.

The layer reports. It never merges, deploys or approves anything; the PM
rules on a head, and a person or the repository's own merge rules act on it.
