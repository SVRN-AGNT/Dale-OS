# Verification and Adjudication

**Scope.** This file verifies **findings**: one claim, one evidence surface, one refutation objective. Attacking the **synthesized architecture** is a different job with a different failure mode (assumptions every lane shared; consequences where two lanes meet), and it lives in `adversarial-synthesis.md`. At MEDIUM/HIGH depth both run.

## Independent verification contract

A verifier is a fresh agent. For each material finding, give it:

- **the claim in one sentence**, as a falsifiable proposition ("`selectHistory` is the only writer of `history`", not "history architecture is duplicated");
- **the exact evidence surface**: the files, commands, fixtures, or data it may inspect; enough to test, not the discoverer's whole context;
- **the falsification objective**: what result would refute the claim, and the instruction to pursue it;
- **the acceptance/rejection criteria**.

Do not give the verifier the discoverer's persuasive narrative, ranking, confidence score, or desired outcome unless that context is itself evidence. Prefer fresh wording of the claim over the discoverer's wording.

Ask for a typed verdict: `refuted | survived | survived-with-correction | inconclusive`, plus the evidence and, where corrected, the corrected claim and severity. Default to `refuted` under uncertainty.

When a finding can fail in more than one way, use *distinct lenses* (correctness, security, performance, does-it-reproduce, does-it-matter-to-the-objective) rather than N identical refuters. Diversity catches what redundancy cannot.

Stakes decide coverage: a finding that will drive a decision, a code change, or a human-facing claim gets an independent falsifier; a mechanical enumeration may be checked by a deterministic script or a spot-check, and is labelled accordingly.

## Two-lens verifier

For high- and critical-severity findings, use two independent verifiers with different lenses:

1. **Mechanism lens**: does the code path exist and behave as claimed? Reproduce it, trace it, or show it cannot happen.
2. **Production-conditions lens**: under the configuration, data, and traffic that actually exist, can a real user reach it, and what is the real consequence?

A finding can be mechanically true and practically unreachable, or reachable but far less severe than claimed. In one large executable-first audit run this way, the dominant verdict was not refutation but *survived with correction*, usually with a severity downgrade: **discoverers overstated, verifiers deflated.** Treat that as the expected direction. The synthesis uses the verifier's corrected claim and the more conservative severity; it never restores the discoverer's original framing.

## Good falsification prompts

- Find a sibling consumer that disproves the claimed blast radius.
- Reproduce the behavior from the canonical source instead of the reported surface.
- Show that the proposed authority is not actually authoritative.
- Find a state transition that bypasses the claimed guard.
- Find any other writer; find a live consumer of the "dead" path.
- Revert the proposed fix and prove whether the regression test really turns red.
- Prove the alleged race cannot occur under the real scheduler.
- Show the state the harness built cannot be produced by any real flow.

## Evidence hierarchy

Prefer, in order when applicable:

1. deterministic reproduction or invariant;
2. live runtime or exact state inspection;
3. source trace to canonical authority;
4. independent primary-source evidence;
5. consistent secondary evidence;
6. reasoned inference, labeled as inference.

A higher count of weaker evidence does not automatically outweigh stronger contradictory evidence.

## Evidence standards

| Standard | Counts as proof when |
|---|---|
| Code location | `file:line` a reader can open, plus the consumer/producer trace it implies |
| Runtime reproduction | the behavior observed on a running system, with the steps |
| Test | fails with the defect and passes without it (a test that passes either way proves nothing); for an architectural invariant, name the mutation that must turn it red and confirm CI actually runs the gate |
| Benchmark / measurement | a number with its method; before and after for a fix |
| Source citation | a dated source, quoted, with the contradiction hunt done |
| Contract / schema | the declared contract and the point where behavior meets or violates it |
| Screenshot | the surface as rendered, at every form factor that matters |
| Database evidence | a query and its result, scoped and dated |
| Diff | the exact change, read cold |
| Deterministic calculation | inputs and arithmetic, reproducible by code |

Below the standard, the item is a **lead**: reported, labelled, never acted on as fact. Dormant is not dead: absence of a caller in one search is not evidence of no caller.

## Evidence levels and reachability

For audits whose findings will be acted on, **every material finding carries exactly one evidence level, and none is promoted by repetition**:

| Level | Meaning |
|---|---|
| LIVE-PROVEN | observed against live runtime or state |
| EXECUTION-PROVEN | reproduced locally through the real executable path |
| SOURCE-PROVEN | inevitable from executable code or config, without undocumented runtime assumptions |
| CONFIG-PROVEN | configuration says so; runtime realisation not observed |
| INFERRED | strong evidence with at least one unproven boundary, which is named |
| LEAD | worth investigating; not a finding |
| REFUTED | attacked and disproved |

A finding that depends on something the run could not observe (a deployed setting, a provider policy, a production endpoint) is capped at INFERRED or CONFIG-PROVEN and names the boundary.

Separately, classify how easily a real user reaches each claimed violation:

| Reachability | Meaning |
|---|---|
| NORMAL-USE | ordinary flows reach it |
| COMMON | common conditions reach it: multi-tab, multi-device, provider outage, opt-in settings |
| RARE | reachable, but only under unusual conditions |
| SYNTHETIC-ONLY | the harness built a state no real flow produces; **remove it from the violation list** |
| UNSETTLED | reachability could not be determined; say what would settle it |

Keep two categories apart: **concerning code** (a mechanism that looks wrong) and **proven architecture violation** (the system provably enters a state its own contracts forbid; the contract is quoted with `file:line` and a real path into the state is shown).

## Disagreement protocol

Majority vote is never the authority.

1. Reduce the disagreement to one proposition both sides would recognise as the crux; it is usually narrower than it looks.
2. List what each side claims and its evidence.
3. Name evidence that would discriminate between them. If none exists, say so.
4. Gather it with a targeted lane if proportionate and available.
5. Adjudicate on the discriminating evidence, on the stronger reasoning tier if the judgment is hard.
6. If the proposition remains underdetermined, preserve it: "unresolved: A vs. B; resolving evidence would be X".

Never average incompatible claims into a false middle. Five agents agreeing after reading the same misleading comment is one datum, not five; ask what the agreement is *based on* before counting it.

## Synthesis contract

The synthesizer receives all lane outputs, verifier verdicts, and the Harness Design. A final synthesis should:

- deduplicate by mechanism, keeping every provenance;
- reconcile terminology to the repository's own names;
- mark each statement **fact** (meets the evidence standard), **inference**, or **unknown**, with evidence pointers on every fact;
- list accepted findings, with their evidence level where levels are in use;
- list rejected findings and rejection evidence, so they are not rediscovered next run;
- list unresolved propositions and what would resolve them;
- name systemic mechanisms connecting multiple findings;
- state authority/state consequences;
- rank by relevance and risk to the objective, not by how many lanes reported it or how strongly;
- produce the deliverable named in the Harness Design;
- name the smallest next action allowed by current authority.

Analysis-only requests produce analysis; implementation requests are complete only after implementation and verification. A synthesis that reads as a list of everything every agent said has failed this contract.

## Retrospective checklist

After a meaningful run:

- Which lanes produced information no other lane produced?
- Which lanes duplicated effort, and would a different partition have avoided it?
- Which findings did verification reject, and would a better evidence standard have caught them earlier?
- Where did extra investigation change the answer? Where did it not?
- Which lanes were over-provisioned (strong tier on mechanical work; many agents converging on one obvious answer) or under-provisioned (hard judgment on a cheap tier; one lane where competing hypotheses were warranted)?
- Approximate compute distribution across lanes, where the runtime reports it.
- Would another topology have been cheaper for the same confidence?

Outcome: a few lines in the final report. Never an automatic edit to the skill or an automatic save of the generated workflow. If a harness proves reusable across repeated runs, report it as a *candidate* template and let the human owner decide.
