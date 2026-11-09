# Harness Retest

**How to tell which parts of an agent harness a newer model no longer needs, and how to remove them without losing
a guard.**

Every piece of scaffolding wrapped around an agent costs tokens, wall time and attention on every run. Some of it
exists because the model was not good enough at something. When the model improves, that piece can stop doing
anything, and nobody notices, because a piece that never fires also never fails. Anthropic's engineering team puts
it this way: "every component in a harness encodes an assumption about what the model can't do on its own", and a
model upgrade is the moment to strip pieces that are no longer load-bearing
([Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)).

The opposite mistake is worse. A team that removes scaffolding because the release notes sound better can remove a
guard that still catches defects, or a limit on who may do what. This page separates the two and gives a procedure
that removes only what a measurement shows is idle.

## Two kinds of piece

| Kind | What it is | Retest after a model change? |
|---|---|---|
| **Compensation** | Exists because the model was not reliable enough: an extra review pass, a forced verify step, a rule restating something obvious, a routing table, a hard split of work into small steps | **Yes.** It is a bet on a weakness, and the bet can expire |
| **Boundary** | Exists because of who may do what: held paths, owner gates, the merge lane's token, secrets, the agents' own identity, fail-closed verdicts | **Never.** A better model does not change who is authorised. Limits belong in access and actions, not in a model's instructions |
| **Preference or owner limit** | Exists because a person chose it: a reply format, a spend cap | **No.** It is not a bet on the model, and only that person changes it |

A piece can be both. The independent reviewer compensates for self-grading and also gates held scope. Only the
compensation half is ever a candidate: its cost settings can move, its existence as a gate cannot.

## This repository's pieces

The inventory below covers the harness this repository publishes ([`HARNESS_MAP.md`](HARNESS_MAP.md)). An adopter
should keep its own table, because its pieces and their costs differ.

| Piece | Kind | Bets that the model... | How to test removal |
|---|---|---|---|
| Agent Review on every ready PR by an allowlisted author ([`ci/README.md`](../ci/README.md)) | Compensation and boundary | ...misses its own defects when it grades its own work | Keep the gate. Its timeout may be retested against measured run times; its usage cap is an owner limit (below) |
| The required quote beside every blocking finding | Compensation | ...reports findings that are not in the diff | Replay the reviewer with and without the field on a set of known-bad and known-good diffs; drop it only if false blocks stay at zero |
| The second vendor on truth and held work | Compensation and boundary | ...shares blind spots with a reviewer of the same vendor | Keep the gate. The record shows the two vendors disagree, not which was right ([report](reports/SECOND_VENDOR_RECORD_2026-10-25.md)), so there is no evidence yet for removal |
| Skill descriptions that name the pressure moment ("use when told to skip this") | Compensation | ...won't load the rule when the prompt pushes against it | The behavioral ablation below |
| The routing table in [`AGENTS.md`](../AGENTS.md) and the resolver | Compensation | ...won't pick the right skill from descriptions alone | The activation run already measures routing without the table, since `AGENTS.md` is not in its context ([`PROOF.md`](../PROOF.md)). The missing arm is a run with the table loaded, on vaguer prompts than the corpus uses; shrink the table to a pointer if that arm adds nothing |
| The execution charter before non-trivial work | Compensation | ...over-reads context and widens scope | Compare tokens, wall time and scope violations on replayed tasks with and without it |
| Held paths, the merge gate, fail-closed verdicts | Boundary | Not a bet on the model | Never retested by this procedure |
| The Codex round budget and Agent Review's usage cap | Owner limit (a spend cap the owner set) | Not a bet on the model | Changed only by the owner. A retest may report what a cap costs in blocked work, but never moves it |

## When to retest

1. **The model pin changes.** When the deployment's dated tier-to-model mapping (kept in one place per deployment, by
   the rules in [`model-cost-policy.json`](../machine/model-cost-policy.json) under `routing`) moves any tier, run the procedure on every compensation row that tier serves.
2. **A quarter passes with no pin change.** Run it on the two most expensive rows only.
3. **A piece fails visibly.** It blocked good work, or let a defect through: run it on that row.

## Procedure for one row

1. **Name the assumption** in one sentence ("the model reports findings that are not in the diff").
2. **Pick the evidence set.** Prefer 20 to 50 real past tasks or diffs drawn from real failures
   ([Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
   Fix the grading criteria before the first run and do not change them after seeing results.
3. **Run with and without the piece** on the current model. Record pass rate, false positives, tokens and wall
   time.
4. **Decide.** Remove the piece only if the run without it is no worse on correctness. Cost alone never justifies
   removing something that catches defects. A difference inside run-to-run noise is not evidence either way.
5. **Ship the removal as its own PR**, citing the numbers from step 3, under the repository's normal lane. A
   removal that touches a boundary is out of scope for this procedure.
6. **Record the result** in the inventory: date, numbers, and the PR, including a decision to keep.

## Worked example: the skills themselves

The behavioral ablation in [`PROOF.md`](../PROOF.md#measured-behavior-with-and-without-the-plugins) is the closest
existing instance of this design, applied to the whole skill library rather than to one row. It departs from the
procedure in two ways: its evidence set is one author-written pressure prompt per skill, not real past tasks, and the
skills were tuned between passes on those same prompts (the held-out prompts were written after seeing failures, so
they are not blind). It compares all plugins against none; no run compares the pressure clauses with and without.
Each skill's flagship prompt pushes the agent to break
the skill's rule, and the same prompt runs with both plugin families loaded and with none, three runs per arm,
graded by a judge model against criteria fixed in advance.

- Overall, the skills earn their place on the measured model: 78 of 93 runs passed with the plugins against 53 of 93
  without (pass 3, [`last-behavioral-run.json`](../plugin-evals/last-behavioral-run.json)), and 18 of 21 against 7 of
  21 on held-out prompts.
- The first pass found a different problem than idle scaffolding: sixteen skills never fired under pressure. The fix
  was to the piece, not its removal. Seven descriptions gained a clause naming the pressure as a moment of use, and
  on those seven cases the plugin arm went from 0 of 21 to 13 of 21. That is a before-and-after of a text change, not
  an ablation of the clauses.
- Seven skills still never fired on their pressure prompt in pass 3, and on most of those the baseline already
  passes. That makes them candidates under step 4, not removals: one prompt per skill and three runs per arm is
  inside the noise the same record reports (single cases moved by up to two runs between passes). The next step is a
  larger evidence set for those seven, not deletion.

## What this page does not show

- **No piece has been removed by this procedure yet.** The worked example kept and repaired pieces. The procedure's
  removal path is unexercised.
- **The inventory kept for the reference repository is not yet measured.** It was written on 14 October 2026, and the model pin
  refresh that day fired trigger 1 for every compensation row. As of its last update it records no with-and-without
  run. Its first two candidates are the reviewer's verify step and a rule that stops work when the strongest coding tier,
  with extended thinking, is unavailable.
- **One model, small samples.** Every number above comes from one model at three runs per arm. A result on one model
  says nothing about another.
- **A judge model grades the runs.** Its votes stand as cast; some read as strict on review
  ([`PROOF.md`](../PROOF.md)).
