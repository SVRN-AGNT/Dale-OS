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

A piece can be both. The independent reviewer compensates for self-grading and also gates held scope. For such a
mixed piece the gate is never switched off, not even for a test. Its retest runs in shadow: the piece is replayed
offline on a fixed set of past diffs, its compensating parts (a verify step, a required field) on and
off, while the live gate stays authoritative on every real PR. Only those parts can be removed. The gate's existence
is not a candidate.

## This repository's pieces

The inventory below covers the harness this repository publishes ([`HARNESS_MAP.md`](HARNESS_MAP.md)). An adopter
should keep its own table, because its pieces and their costs differ. Only the skill library has a recorded run, and
that run departs from the procedure (see the worked example); every other compensation row reads `none` until step 6 fills it in.

| Piece | Kind | Served by | Bets that the model... | Retest | Last retest |
|---|---|---|---|---|---|
| Agent Review as a gate on every ready PR by an allowlisted author ([`ci/README.md`](../ci/README.md)) | Compensation and boundary | Reviewer model | ...misses its own defects when it grades its own work | Not a removal candidate: the piece is the gate. Its timeout is a parameter, retested by comparing measured run times with the limit | none |
| The required quote beside every blocking finding | Compensation | Reviewer model | ...reports findings that are not in the diff | Shadow: replay the reviewer offline on a fixed set of known-bad and known-good diffs with the field required and not; drop it only if false blocks stay at zero | none |
| Agent Review's "Verify before you report" step ([`review.mjs`](../ci/agent_review/review.mjs)) | Compensation | Reviewer model | ...reports plausible findings it has not checked against the code | Shadow: replay the reviewer offline on the same fixed diff set with the step in its prompt and without; drop it only if false blocks stay at zero | none |
| The second vendor on truth and held work | Compensation and boundary | Second vendor's model | ...shares blind spots with a reviewer of the same vendor | Not a removal candidate: the piece is the gate. A shadow replay of past held diffs can count findings only this vendor made, graded against what later happened to each diff (a fix or a revert), for information only. The record so far shows the vendors disagree, not which was right ([report](reports/SECOND_VENDOR_RECORD_2026-10-25.md)) | none |
| The skill library, skill by skill ([`skills/`](../skills/)) | Compensation | Session model | ...won't apply a rule it was never handed, under pressure to break it | Screen: run each skill's flagship pressure prompt with the plugins loaded and with none, as the worked example does. A skill whose without arm is no worse goes on to a step-2 evidence set before any decision; one prompt per skill never reaches step 4 | 2026-10-18, pass 3, before the final charter wording: 78 of 93 with, 53 of 93 without; all skills kept; seven named as candidates for a larger set, none yet scheduled ([`last-behavioral-run.json`](../plugin-evals/last-behavioral-run.json), [#45](https://github.com/SVRN-AGNT/Dale-OS/pull/45)) |
| Skill descriptions that name the pressure moment ("use when told to skip this") | Compensation | Session model | ...won't load the rule when the prompt pushes against it | Run the flagship and held-out pressure prompts with the clauses present and removed, plugins loaded in both arms | none |
| The routing table in [`AGENTS.md`](../AGENTS.md) | Compensation | Session model | ...won't pick the right skill from descriptions alone | Run a set of vaguer prompts than the activation corpus uses, with the table loaded and absent, skills loaded in both arms; shrink the table to a pointer if the table arm adds nothing. The activation run probably had no table, since its cases load only the plugin skills, but it used clear prompts only ([`PROOF.md`](../PROOF.md)); that is an inference, not a measured arm | none |
| The resolver (`python scripts/dale.py resolve`) | Compensation | Session model | ...won't map a symptom to the shortest skill route on its own | Route a fixed set of symptom tasks with the resolver available and absent, skills loaded in both arms; compare route correctness and tokens. The activation run never calls the resolver | none |
| The execution charter before non-trivial work | Compensation | Session model | ...over-reads context and widens scope | Compare tokens, wall time and scope violations on replayed tasks with the charter and without it, other skills loaded in both arms, on its current wording. No record yet measures that wording | none |
| Held paths, the merge gate, fail-closed verdicts | Boundary | n/a | Not a bet on the model | Never retested by this procedure | n/a |
| The Codex round budget and Agent Review's usage cap | Owner limit (a spend cap the owner set) | n/a | Not a bet on the model | Changed only by the owner. A retest may report what a cap costs in blocked work, but never moves it | n/a |

## When to retest

1. **The model pin changes.** When the deployment's dated tier-to-model mapping (kept in one place per deployment, by
   the rules in [`model-cost-policy.json`](../machine/model-cost-policy.json) under `routing`) moves any tier, run the procedure on every
   compensation row whose Served by model changed. A row served by an unchanged model keeps its last result. The
   second vendor's model is outside this repository's pin; its row is retested when that vendor announces a change.
2. **A quarter passes with no pin change.** Run it on the two rows that cost most per run, measured in tokens or
   wall time. Until those costs are measured, take the required-quote and verify-step rows, which run on every Agent Review.
3. **A piece fails visibly.** It blocked good work, or let a defect through: run it on that row.

## Procedure for one row

1. **Name the assumption** in one sentence ("the model reports findings that are not in the diff").
2. **Pick the evidence set.** Prefer 20 to 50 real past tasks or diffs drawn from real failures
   ([Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
   Fix the grading criteria before the first run and do not change them after seeing results.
3. **Run with and without the piece** on the current model. Record pass rate, false positives, tokens and wall
   time. For a mixed piece, run both arms offline in shadow and leave the live gate untouched. A parameter such as a
   timeout has no off arm: retest it by measuring against its limit.
4. **Decide.** Remove the piece only if the run without it is no worse on correctness. Cost alone never justifies
   removing something that catches defects. A difference inside run-to-run noise is not evidence either way.
5. **Ship the removal as its own PR**, citing the numbers from step 3, under the repository's normal lane. A
   removal that touches a boundary is out of scope for this procedure.
6. **Record the result** in the inventory's last column: date, numbers, and the PR, including a decision to keep.

## Worked example: the skills themselves

The behavioral ablation in [`PROOF.md`](../PROOF.md#measured-behavior-with-and-without-the-plugins) is the closest
existing instance of this design, and the recorded run of the skill-library row. It departs from the
procedure in two ways: its evidence set is one author-written pressure prompt per skill, not real past tasks, and the
skills were tuned between passes on those same prompts (the held-out prompts were written after seeing failures, so
they are not blind). It compares all plugins against none; no run compares the pressure clauses with and without.
Each skill's flagship prompt pushes the agent to break
the skill's rule, and the same prompt runs with both plugin families loaded and with none, three runs per arm,
graded by a judge model against criteria fixed in advance.

- Overall, before the final charter wording, the plugin arm passed more often on the measured model: 78 of 93 runs passed with the plugins against 53 of 93
  without (pass 3, [`last-behavioral-run.json`](../plugin-evals/last-behavioral-run.json)), and 18 of 21 against 7 of
  21 on held-out prompts.
- The first pass found a different problem than idle scaffolding: sixteen skills never fired under pressure. The fix
  was to the piece, not its removal. Seven descriptions gained a clause naming the pressure as a moment of use, and
  on those seven cases the plugin arm went from 0 of 21 to 13 of 21. Six of them also gained a workflow line in the
  same pass, so the gain is a before-and-after of two text changes, not an ablation of the clauses.
- Seven skills still never fired on their pressure prompt in pass 3, and on most of those the baseline already
  passes. That makes them candidates under step 4, not removals: one prompt per skill and three runs per arm is
  inside the noise the same record reports (single cases moved by up to two runs between passes). The next step is a
  larger evidence set for those seven, not deletion.

## What this page does not show

- **No piece has been removed by this procedure yet.** The worked example kept and repaired pieces. The procedure's
  removal path is unexercised.
- **The reference repository's own inventory is not yet measured either.** It is a separate, private table of that
  repository's pieces, written on 14 October 2026, and the model pin refresh that day fired trigger 1 for every
  compensation row in it. As of its last update it records no with-and-without run. Its first two candidates are the reviewer's verify step and a rule that stops work when the strongest coding tier,
  with extended thinking, is unavailable.
- **One model, small samples.** Every number above comes from one model at three runs per arm. A result on one model
  says nothing about another.
- **A judge model grades the runs.** Its votes stand as cast; some read as strict on review
  ([`PROOF.md`](../PROOF.md)).
