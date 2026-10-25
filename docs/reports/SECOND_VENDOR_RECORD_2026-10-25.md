# The second-vendor record, 16 to 25 October 2026

What the two reviewers actually did, measured across the owner's five repositories (the private reference
repository, this one, and three others) from the first PM ruling that read a Codex review (16 October, 17:37 UTC)
to a cutoff of 25 October, 14:34 UTC.

The record is [`pm-record-2026-10-25.json`](pm-record-2026-10-25.json). It keeps no titles, bodies or commit shas.
[`scripts/pm_record.py`](../../scripts/pm_record.py) built it read-only through `gh api`, and recomputes every number
below:

```bash
python scripts/pm_record.py summary docs/reports/pm-record-2026-10-25.json
```

## Definitions

- **Ruling:** a `PM REVIEW —` comment by `github-actions[bot]` that says Codex completed its review of the head.
  All others are left out, among them those the PM made on an API key before 16 October and 14 made before Codex
  had finished.
- **Agent Review passed first:** a successful `Agent Review` check run on the ruled head had completed before the
  ruling was posted. It is read from all the head's check runs, re-runs included, not from the HANDOFF's own claim,
  and unlike the merge gate it does not check which workflow posted the run.
- **Finding:** an item listed under the ruling's Blocking heading, with Codex's priority (P0 to P3). A finding that
  Codex repeats on a later head counts again.
- **Round:** the round the ruling states. The PM began stating it on 19 October; it counts that PR's earlier
  rulings too, including any made before Codex finished, and so does a PR's highest round here.

## What it shows

| Measure | Value |
|---|---|
| PRs with at least one ruling | 103, of which 97 merged by the cutoff |
| Rulings | 307: 210 `CORRECT`, 97 `CLEAR` |
| Rulings on a head Agent Review had already passed | 302 of 307 |
| Codex findings on those heads | 280: 134 P1, 143 P2, 3 P3, no P0 |
| PRs with a Codex finding after Agent Review passed | 63 of 103 |
| PRs where that included a P1 | 44 of 103 |
| PRs whose first counted ruling was `CLEAR` | 41 of 103 |
| `CORRECT` rulings caused only by a failed check, with no Codex finding | 8 |
| PRs past round 5 (of 63 with stated rounds) | 13; the most was 10 rounds; the median 2 |
| Codex "usage limits" messages | 55, on 32 PRs |
| PRs opened in the window with "revert" in the title | 0 |

P1 findings by round, counting only rulings that state one (from 19 October), which shows how slowly a long review
converges:

| Round | 1 | 2 | 3 | 4 | 5 | 6 and later |
|---|---|---|---|---|---|---|
| Rulings | 50 | 43 | 24 | 21 | 18 | 24 |
| P1 findings | 25 | 24 | 11 | 8 | 10 | 7 |

## How to read it

- **The two reviewers' findings disagree.** On 44 PRs Codex rated something P1 on a head Claude's reviewer had
  already passed. Until the findings are audited, that shows disagreement, not that one reviewer caught defects the
  other missed: a P1 may be a false positive. Nor does it show independence: both read the same diff, and nothing
  here counts the defects both missed.
- **Findings are counted, not audited.** Nobody has checked each finding for validity. A finding the author thinks is
  wrong has to be answered on its thread and waived by the owner, and this record does not count waivers. A precision
  audit of a random sample is the next measurement to make.
- **The round budget is convention.** It was set on 19 October. Thirteen PRs went past round 5 in the window, and
  the record has no machine-readable trace of the owner's word for each round past 5.
- **Long reviews keep drawing P1s.** Rounds 6 and later still drew 7. The owner's rule of 25 October, one purpose
  per PR and a sweep by class before every HANDOFF, aims at this.
- **The quota can be seen, but the PM doesn't read it.** Codex often answers a spent quota with a "usage limits"
  comment (55 in the window). The PM does not parse that comment. On 25 October, on this repository's PR #55, Codex
  posted no such message: its status read "Running" until the window reset.
- **No revert PR was opened in the window.** Nightly failures traced back to a merged PR, the rest of the
  escaped-defect measure in
  [ADOPT step 10](../../shipping/ADOPT.md#step-10--measure-four-numbers-on-every-change-to-the-pipeline), are not
  measured yet.
