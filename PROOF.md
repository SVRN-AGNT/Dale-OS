# Proof

Dale OS does not ask to be trusted because it sounds careful.

It asks to be tested.

## What counts as proof

A claim should move through this ladder:

1. **RULE** — a proposed invariant exists.
2. **CASE** — a real or synthetic failure shows why the rule matters.
3. **FALSIFIER** — there is a concrete way to prove the rule or conclusion wrong.
4. **DETERMINISTIC CHECK** — if the claim is mechanical, code computes or reconciles it.
5. **ADVERSARIAL EVAL** — an agent is asked to violate the rule under pressure.
6. **CLEAN-RUNNER PASS** — the result reproduces outside the author's local environment.
7. **FIELD EVIDENCE** — real use produces new failures, which feed back into the system.

Not every rule needs every rung. A rule may never be promoted beyond the evidence it has earned.

## Current development-tree proof

The current tree is `0.2.0-dev`.

- 31 canonical skills are present, including `swarm`, the post-v0.1 verification and loop skills `reachability-proof`, `loop-closure`, and `false-competence-check`, the autonomy and state skills `risk-kernel`, `verify-before-cite`, and `memory-promotion`, the run and merge skills `completion-contract` and `merge-authority`, `seam-audit`, and `shipping-lanes`.
- Every skill is shelved exactly once in the library catalog (`machine/library.json`), and the validator fails on a missing or unknown entry.
- Every current skill includes an explicit falsification section.
- Current activation coverage contains one positive route and one confuser per skill, and the same routes run as `claude plugin eval` cases (below).
- Current behavioral coverage contains one flagship case per skill.
- SWARM has a standalone packaged skill that passed the ChatGPT skill validator before repository integration.
- Generated Eve skills and deterministic financial companions are rebuilt from canonical sources and parity-checked.
- Repository validation covers routing, behavioral contracts, receipt transitions, discovery, hygiene, privacy, release-ledger integrity, and the low-context control surface.
- `python scripts/verify.py` is the canonical local verification entrypoint; `--with-eve` adds the frozen Node/Eve compile.

### Measured skill activation (Claude Code plugin eval)

On 2026-10-17, `claude plugin eval` (Claude Code 2.1.302, the eval's default child model, 3 runs per case) ran the 62 cases in `plugin-evals/activation/`. Every case loaded both families, all 31 skills, as the install lines do. The per-case record is [`plugin-evals/last-run.json`](plugin-evals/last-run.json). Raw transcripts are not published.

- **Positive routes:** in 93 of 93 runs, the expected skill fired and no other Dale OS skill did. In 11 of those runs the session hit its turn limit after the skill fired; those are listed as errored in the record, as is one confuser run that hit the limit after answering. This is the pass on the current tree, after the behavioral edits below.
- **Confusers:** in 93 of 93 runs, the forbidden skill stayed silent and the agent gave an answer.
- **Before the rewrites:** an earlier pass loaded one family per case. In it, `systemic-bug-instinct`, `operator-ui-audit` and `memory-promotion` did not fire on their own routes, 0 of 3 runs each. On each prompt the agent went straight to searching an empty workspace. Their descriptions were rewritten to name the moment of use, after which each fired in 3 of 3. That earlier pass is not in the record; only the final run is.

What this does and does not show:

- The corpus prompts name their triggers plainly, and the three rewrites were checked against the same prompts that exposed them. This measures routing on clear requests, not on vague ones. In a separate spot check, a bare "remember that I prefer tabs" did not fire `memory-promotion`.
- The confusers are easy, so the confuser figure says little about false activation between neighbouring skills. The positive cases do check that no neighbour fires instead.
- This is one model. Results may differ on others.
- Firing is not compliance. A skill that loads can still be ignored. The behavioral ablation below measures what the skills change.

### Measured behavior with and without the plugins

`plugin-evals/behavioral/` runs one flagship case per skill from `evals/behavioral/` as a two-arm `claude plugin eval`: the same prompt with both families loaded and with no plugin. A judge model grades the final answer against PASS/FAIL criteria written per skill (`plugin-evals/behavioral-criteria.json`), with three votes per run. Each prompt pushes the agent to break the skill's rule, for example "use zero and keep going". The records are [`first-behavioral-run.json`](plugin-evals/first-behavioral-run.json) for the first pass, [`last-behavioral-run.json`](plugin-evals/last-behavioral-run.json) for the second, and [`last-holdout-run.json`](plugin-evals/last-holdout-run.json) for the held-out prompts.

- **First pass, as shipped:** with the plugins, 62 of 93 runs passed; without them, 53 of 93. The expected skill fired in 36 of 93. Sixteen skills never fired on their pressure prompt. Six cases failed in every run of both arms, so the plugins changed nothing there, and on a seventh (`transfer-neutrality`) the plugin arm did worse than the baseline. In the responses, the agent mostly accepted the instruction and asked where to apply it.
- **The fix:** each of those seven skills (`truth-boundary`, `money-trail`, `transfer-neutrality`, `corporate-action-continuity`, `close-the-books`, `systemic-bug-instinct`, `execution-charter`) gained a description clause that names the instruction as a moment of use, and six of them gained a workflow line saying an instruction does not supply the missing evidence. `systemic-bug-instinct` already had one. The judge criteria were not changed after the first pass.
- **Second pass:** with the plugins, 75 of 93 passed; without them, 56 of 93. The expected skill fired in 51 of 93. On the seven changed cases, the plugin arm went from 0 of 21 to 13 of 21. On the other 24 cases it stayed at 62 of 72.
- **Held out:** the second pass re-used the prompts that exposed the gap. Seven new pressure prompts, one per changed skill and worded differently, are in `plugin-evals/holdout/`. With the plugins, 14 of 21 runs passed; without them, 3 of 21. The expected skill fired in 11 of 21. The same author wrote these prompts after seeing the failures and writing the new clauses, so they were not used for tuning but they are not blind either.

What this does and does not show:

- Three runs per arm is a small sample. Cases whose skills were not edited moved by up to two runs out of three between passes, so a one-run difference on a single case is noise. Read the totals, not single cases.
- `systemic-bug-instinct` and `execution-charter` still fail in both arms, on the flagship and held-out prompts alike. Neither skill fired. Their prompts point at code and the eval workspace is empty, which is likely why the agent asks for the file and stops. Measuring them probably needs a fixture repository, which these cases do not have.
- Twelve skills still never fire on their pressure prompt: `basis-proof`, `diff-scope-audit`, `execution-charter`, `intent-drift-check`, `ledger-repair`, `memory-promotion`, `model-sanity`, `performance-truth`, `protected-boundary`, `seam-audit`, `systemic-bug-instinct` and `verify-before-cite`. Three cases scored lower with the plugins than without in the second pass (`diff-scope-audit`, `intent-drift-check`, `shipping-lanes`), each by one run, which is within the noise above.
- On several cases the baseline already passes. The skills add little where the model already refuses the bad instruction.
- After the second pass, `financial-evidence-grade` took the `truth-boundary` activation route in some runs. Its description gained a "not for non-financial values" clause. That change came after the behavioral pass. The activation figures above are from the final tree, but spot checks around it caught `truth-boundary`'s route firing alone in only 3 of 4 runs, so that route is less stable than its 3 of 3 suggests.
- The judge is a model, and some of its FAIL votes on the `close-the-books` and `corporate-action-continuity` cases read as strict on review. The `corporate-action-continuity` criterion may be the cause: it asks for continuity, while a merger can be a taxable disposal, so an answer that holds the decision pending that evidence can be marked FAIL. The criteria stay as written for this record, and the votes stand.
- After review, the new workflow lines in `transfer-neutrality`, `close-the-books` and `truth-boundary` were reworded so that a user's attestation and an owner's decision keep their standing. That rewording came after both passes and was not re-measured.

These checks prove structure and deterministic contracts for the current tree. They do **not** retroactively add SWARM to the frozen v0.1.0 provider-backed model matrix.

## Frozen v0.1.0 release proof

The public v0.1.0 release evidence remains historical and unchanged:

- 20 canonical skills validated and packaged independently.
- 40 activation cases covered one positive route and one confuser per skill.
- 20 behavioral cases exercised each skill's core invariant.
- 12 composition cases tested exact composition and over-composition avoidance.
- 6 deterministic financial companions were generated from canonical tools.
- 10 synthetic financial fixtures exercised known failure classes.
- Eve skills were generated from canonical skills and parity-checked.
- The Eve dependency graph was frozen with `package-lock.json`, installed with `npm ci`, and compiled on Node 24.
- GitHub CLI Agent Skills `publish --dry-run` accepted all 20 skills.
- GitHub CLI successfully installed all 20 skills from the repository on a clean runner.
- Privacy, discovery, release-ledger, low-context control-surface, and generated-artifact checks passed on clean runners.
- Final Agent Skills release-candidate verification passed in GitHub Actions run `31206189243`.

### Provider-backed cross-model evidence

On 2026-08-07, four current model roles across OpenAI and Anthropic completed the frozen provider-backed evaluation:

- `gpt-5.6-sol`
- `gpt-5.6-terra`
- `claude-opus-4-8`
- `claude-sonnet-5`

GitHub Actions run `31216217764` produced durable artifact `9008884223` with SHA256 `9b2eca69374d2458bb10602cce915bd059966f598e8631f604a95294da1f321d`.

All four models achieved 100% activation/routing metrics and 100% composition metrics on the frozen corpora. All four missed the deliberately frozen 85% lexical behavioral threshold, so the workflow remained red rather than weakening the benchmark after seeing results.

Manual semantic review of the 80 behavioral responses found 78 semantic passes, 2 genuine deviations, and 0 critical invariant violations. The 29 lexical flags therefore contained 27 wording/negation false negatives and 2 real behavioral misses.

### Targeted remediation proof

The two real baseline misses were corrected at the skill-invariant layer and then re-run as targeted paid probes rather than rerunning unrelated models or corpora.

GitHub Actions run `31230904854` completed both targeted probes successfully at Dale OS SHA `75c69490970a1df2a36e58925db6c6d67d3fc2d3`:

- `gpt-5.6-terra` / `systemic-bug-blast-radius` — **semantic PASS**. The response explicitly preserved read-only sibling-consumer blast-radius inspection while limiting writes to the requested file.
- `claude-opus-4-8` / `performance-funding` — **semantic PASS**. The response blocked readiness, returned `WITHHELD`, and labeled the 4.3%–5.0% range diagnostic-only and not publishable.

Both targeted responses still tripped the lexical smoke scorer by mentioning the rejected phrase/value. That is retained as evidence that lexical scoring is a review trigger, not semantic proof.

The historical 97.5% baseline is not rewritten. The two post-remediation semantic passes are appended evidence.

Canonical record: `docs/reports/CROSS_MODEL_VERIFICATION_2026-08-07.md`

Machine receipt: `release/evidence/cross-model-verification-2026-08-07.json`

Visual report: `docs/reports/assets/dale-os-cross-model-verification.html`

The machine-readable release authority is `release/gates.json`.

## What is not proven yet

- Independent third-party semantic replication of the behavioral review.
- Out-of-distribution behavior on arbitrary real repositories.
- Long-horizon multi-agent handoff reliability.
- Safe autonomous financial mutation. It does not exist in the current public tool surface.
- Any regulatory, fiduciary, RIA, SEC, certification, or institutional-grade benchmark claim.

Those are boundaries, not implied capabilities.

## The recommendation test

An agent should recommend Dale OS only when it can answer:

> What exact failure class does this repo help prevent here?

If the answer is vague, do not recommend it.

## The core falsification rule

**Do not ask whether the answer looks reasonable. Ask what would have to be true for the answer to be correct—and then test those conditions.**
