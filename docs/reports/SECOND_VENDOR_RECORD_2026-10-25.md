# The second-vendor record, 16 to 25 October 2026

What the two reviewers actually did, measured across the owner's five repositories (the private reference
repository, this one, and three others) from the first PM ruling that read a Codex review (16 October, 17:37 UTC)
to 25 October, 14:33 UTC.

The record is [`pm-record-2026-10-25.json`](pm-record-2026-10-25.json). It keeps no titles, bodies or commit shas.
[`scripts/pm_record.py`](../../scripts/pm_record.py) built it read-only through `gh api`, and recomputes every number
below:

```bash
python scripts/pm_record.py summary docs/reports/pm-record-2026-10-25.json
```

## Definitions

- **Ruling:** a `PM REVIEW —` comment by `github-actions[bot]` that names Codex's review. Rulings that don't, such as
  those the PM made on an API key before 16 October, are left out.
- **Agent Review passed first:** a successful `Agent Review` check run on the ruled head had completed before the
  ruling was posted. It is read from the head's check runs, not from the HANDOFF's own claim, and unlike the merge
  gate it does not check which workflow posted the run.
- **Finding:** an item listed under the ruling's Blocking heading, with Codex's priority (P0 to P3). A finding that
  Codex repeats on a later head counts again.
- **Round:** the round the ruling states. The PM began stating it on 19 October; it counts that PR's earlier
  rulings too.

## What it shows

| Measure | Value |
|---|---|
| PRs with at least one ruling | 104 (97 merged, 6 open, 1 closed) |
| Rulings | 321: 224 `CORRECT`, 97 `CLEAR` |
| Rulings on a head Agent Review had already passed | 305 of 321 |
| Codex findings on those heads | 281: 134 P1, 144 P2, 3 P3, no P0 |
| PRs where Codex found something after Agent Review passed | 64 of 104 |
| PRs where that included a P1 | 44 of 104 |
| PRs cleared on their first ruling | 35 of 104 |
| `CORRECT` rulings caused only by a failed check, with no Codex finding | 21 |
| PRs past round 5 (of 64 with stated rounds) | 13; the most was 10 rounds; the median 2 |
| Codex "usage limits" messages | 50, on 27 PRs |

P1 findings by round, counting only rulings that state one (from 19 October), which shows how slowly a long review
converges:

| Round | 1 | 2 | 3 | 4 | 5 | 6 and later |
|---|---|---|---|---|---|---|
| Rulings | 59 | 43 | 24 | 22 | 18 | 24 |
| P1 findings | 25 | 24 | 11 | 8 | 10 | 7 |

## How to read it

- **The second vendor is not a rubber stamp.** On 44 PRs Codex rated something P1 on a head Claude's reviewer had
  already passed. That is evidence the two reviewers' errors differ. It is not proof that they are independent:
  both read the same diff, and nothing here counts the defects both missed.
- **Findings are counted, not audited.** Nobody has checked each finding for validity. A finding the author thinks is
  wrong has to be answered on its thread and waived by the owner, and this record does not count waivers. A precision
  audit of a random sample is the next measurement to make.
- **The round budget is convention.** It was set on 19 October. Thirteen PRs went past round 5 in the window, and
  the record has no machine-readable trace of the owner's word for each round past 5.
- **Long reviews keep finding P1s.** Rounds 6 and later still produced 7. The owner's rule of 25 October, one
  purpose per PR and a sweep by class before every HANDOFF, aims at this.
- **The quota can be seen, but the PM doesn't read it.** Codex often answers a spent quota with a "usage limits"
  comment (50 in the window). The PM does not parse that comment. On 25 October Codex posted no such message: its
  status read "Running" until the window reset.
- **No revert PR was opened in the window** (no PR title in the five repositories contains "Revert"). Nightly
  failures traced back to a merged PR, the rest of the escaped-defect measure in
  [ADOPT step 10](../../shipping/ADOPT.md#step-10--measure-four-numbers-on-every-change-to-the-pipeline), are not
  measured yet.
