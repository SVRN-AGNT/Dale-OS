# Changelog

## 0.2.0-dev — development

- Added behavioral ablation: `plugin-evals/behavioral/` runs one flagship case per skill with and without the plugins, graded by a judge model against `plugin-evals/behavioral-criteria.json`, and `plugin-evals/holdout/` adds seven held-out pressure prompts. The first pass found that sixteen skills never fired when the prompt told the agent to break their rule. Seven skill descriptions now name that instruction as a moment of use, and six workflows say an instruction does not supply missing evidence. Plugin arm 62 → 75 of 93 runs passed, baseline 53 → 56; held out 14 of 21 with the plugins, 3 of 21 without (records in `plugin-evals/first-behavioral-run.json`, `last-behavioral-run.json` and `last-holdout-run.json`). Twelve skills still never fire on their pressure prompt. After the behavioral pass, `financial-evidence-grade` began deferring non-financial values to `truth-boundary`; `validate_repo.py` now checks the holdout cases. Method and limits are in `PROOF.md`.
- Added `plugin-evals/activation/`: the activation corpus rendered as 62 `claude plugin eval` cases by `scripts/build_plugin_evals.py`, which `verify.py` runs. Positive cases also fail if a different Dale OS skill fires. Confusers fail if the run ends without an answer. Each skill family gained a `.claude-plugin/plugin.json`, so `claude --plugin-dir skills/operator` and the eval harness can load it; `validate_repo.py` keeps those manifests in step with the marketplace. Measured with all 31 skills loaded: 93 of 93 route runs fired the right skill alone, and 93 of 93 confuser runs stayed silent (`plugin-evals/last-run.json`). Before that run, three skills (`systemic-bug-instinct`, `operator-ui-audit`, `memory-promotion`) never fired on their own routes; their descriptions were rewritten. Method and limits are in `PROOF.md`.
- `validate_repo.py` now rejects SKILL.md front matter that strict YAML parsers refuse. Claude Code's loader is lenient, but `npx skills` and the Eve adapter are not, and a colon in a description had silently dropped a skill from them.
- The repository is now a Claude Code plugin marketplace (`.claude-plugin/marketplace.json`, marketplace `dale-os`) with two plugins, `dale-os-operator` (19 skills) and `dale-os-financial-truth` (12 skills). Verified with `claude plugin validate` and a local install that loaded all 31 skills. README and INSTALL carry the install lines.
- Added `ci-pm-review.yml` and `ci/pm_review.py` to the shared CI layer: every Claude `HANDOFF:` comment gets a second-vendor PM review from OpenAI Codex (read-only, sudo dropped), posted as a `PM REVIEW —` comment and a `PM Review` check on the exact head. "No ruling" is never a CLEAR. This replaces pasting HANDOFFs into ChatGPT by hand: ChatGPT event tasks fire on supported pull request activity, not comments. Dale-OS calls it on its own PRs.
- Added a shared CI layer under `ci/`: a reusable red-alert workflow that keeps
  one issue open while a scheduled or trunk run is red, and a zero-dependency
  workflow checker (`ci/ci_hygiene.py`) for timeouts, permissions, PR
  concurrency, duplicate push and pull_request runs, and a single pinned ref.
  `validate.yml` now runs on push to `main` only, which the checker flagged:
  every PR commit had been tested twice.
- Added `swarm`, an adaptive multi-agent harness skill with design-before-spawn, staged allocation, independent falsification, adversarial synthesis, authority-migration, and write-topology contracts.
- Expanded the canonical catalog from 20 to 21 skills while preserving the frozen v0.1.0 20-skill release evidence as historical proof.
- Added `reachability-proof`: correctness has three legs (right, reached, visible); a guard no gate runs is documentation, and an assertion satisfied by the null case is not a test.
- Added `loop-closure`: loops move captured → tracked → closed → retired; caps hold by displacement; a full audit is two passes; report net loops.
- Added `false-competence-check`: thirteen counterfeits of good work, each paired with the single check that tells them apart.
- Deepened `swarm` references with portable material from field use: authority choke-point audit, value-versus-authority retention, evidence-level ladder, two-lens verification, and an audit-graph topology.
- Expanded the canonical catalog to 24 skills. Frozen v0.1.0 evidence is unchanged.
- Added `risk-kernel`: autonomous agents are made safe by construction (one door, compiled bounds, removed capabilities, inert self-modification, out-of-band promotion), not by instructions.
- Added `verify-before-cite`: work state is live-verified against its authority before it is reported, every record of it is reconciled, and the canonical copy is the one corrected.
- Added `memory-promotion`: a six-check gate for durable agent memory, update-before-add, and garbage collection.
- Added the library catalog (`machine/library.json`, `docs/LIBRARY.md`): every skill shelved under one domain and lane, rendered into `docs/SKILL_CATALOG.md` by `scripts/build_catalog.py`, with a validator that enforces positional call numbers, real paths, one shelf per skill, and byte-for-byte generated docs. Skill paths are unchanged.
- Expanded the canonical catalog to 27 skills.
- Added `completion-contract`: a finish line agreed in advance where a missing answer counts as no, a judge separate from the worker (script, separate reviewer, or person), a fixed outcome set, sticky retry exhaustion, and no-progress detection.
- Added `merge-authority`: evidence bound to the exact tree that will land (head and base), risk classified from the change rather than the author, policy read from the target branch, and an approver the automation cannot impersonate.
- Added role → tier → dated model mapping rules to `machine/model-cost-policy.json` (policy, not a skill, per its promotion rule).
- Expanded the canonical catalog to 29 skills.
- Added `seam-audit`: the boundary where two representations of one concept meet is a first-class bug surface (definition, shape, projection, preview versus commit, clocks, lifecycle, evidence grade, unknown).
- `systemic-bug-instinct` now warns that reconciling arithmetic is not proof, and to search for a capability before declaring it missing.
- `accounting-integrity` now covers aggregates over withheld values and fallback chains.
- Added cases `a-total-that-dropped-an-account` and `the-capability-nobody-fed`.
- Expanded the canonical catalog to 30 skills.
- Added the Shipping System under `shipping/`: the operating model for agent review and merge by risk lane (roles, L0–L3 lanes, rules, what stays human), a stage-by-stage before and after with measured versus expected labels, the sourced Anthropic playbook with rollout status, a twelve-step adoption guide, and templates (reviewer rubric, HANDOFF comment, lane map, PR header).
- Added `shipping-lanes`: risk picks the lane, the lane picks the judge and the lander, and the reviewed party never summons its own review. Shelved at A2.4.
- Added case `the-reviewer-nobody-called`.
- Corrected `shipping/` and `shipping-lanes`: the second-vendor review clears every PR before ready (the reference repo's standing rule), not only authority work. The held hand-merge rule is merged in the reference repo.
- Added the high-stakes marker to `shipping/` and `shipping-lanes`: L2/L3 PRs get a `high-stakes` label, a `[HIGH STAKES]` title prefix, and a closing `🔴 HIGH STAKES · #NNNN · <action>` line in every message about them; ordinary PRs get `🟢 Ordinary · #NNNN`.
- Recorded the owner's decision: ordinary PRs need green CI and a passing Agent Review; truth and held PRs also need a second-vendor CLEAR before ready, or 2 hours with no ruling ("PM timeout"). A blocking ruling stops ready, a push restarts the clock, and Agent Review never replaces a CLEAR.
- Expanded the canonical catalog to 31 skills.

## 0.1.0 — public release

- Public repository launch authorized and completed.
- Preserved the frozen four-model baseline at 78/80 semantic passes (97.5%) with 0 critical invariant violations.
- Clarified `systemic-bug-instinct` and `performance-truth` from the two genuine baseline deviations, then verified both fixes with targeted provider-backed probes.
- Added a durable cross-model verification report and machine-readable evidence receipt.
- Added external field-derived regression cases for over-withholding, selective dependency blocking, mixed corporate-action treatment, and lossy receipt handoffs.
- Added a lightweight deterministic receipt-transition guard for evidence-free status upgrades, dropped unknowns, claim injection, and evidence-grade changes.
- Kept the 20-skill catalog, narrow composition model, and read-only financial-tool boundary unchanged.

## 0.1.0-rc.1 — public release candidate

- Established Dale OS as an agentic operating system rather than a prompt collection.
- Added 8 Operator OS skills and 12 Financial Truth skills with explicit falsifiers.
- Added six deterministic read-only finance tools and adversarial fixtures.
- Added generated standalone finance companions and generated Eve skills from canonical source.
- Added failure-first routing, narrow composition contracts, low-context control surfaces, and machine-readable receipts.
- Added activation, behavioral, and composition eval corpora with separate scoring contracts.
- Added Agent Skills, Eve, Claude Code, Codex, and Cursor integration guidance.
- Added Apache-2.0 licensing, privacy/release gates, and clean-runner verification.
- Frozen Eve dependency graph verified with `npm ci` on Node 24.
- GitHub CLI Agent Skills dry-run validation and 20/20 local install verification passed.
