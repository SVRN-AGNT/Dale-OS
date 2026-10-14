# The Dale OS Library

## The theme

**Truth under autonomy.**

Every skill here answers one question from a different side: how do you let an agent act on consequential work without letting it manufacture truth, or certify a truth it has not earned?

In software, the truth at stake is about the work. Did it ship? Does the guard run? Did the agent stay in scope? In finance, the truth at stake is about the money. Where did it go? What did it cost? Is the return real? Finance is the domain where false certainty is most expensive, so it gets its own wing. The discipline is the same in both.

Workflow management is how the library gets used. Truth is what it is about.

## How the shelves work

The library has four domains. Each domain is split into lanes, and each lane holds a few skills. Every skill has a call number: domain letter, lane number, then position. `E2.2` is the second skill in lane 2 of the Evidence domain.

| Domain | The question it answers | Lanes |
|---|---|---|
| **A. Authority and scope** | Who decides, and what is in bounds? | A1 Mandate · A2 Boundaries · A3 Scope |
| **E. Evidence and verification** | Is it true, and how do we know? | E1 Claims · E2 Mechanisms · E3 Surfaces |
| **O. Orchestration and memory** | How do agents work together and over time? | O1 Harness · O2 Loops · O3 Memory |
| **F. Financial truth** | Is the money right? | F1 Flows and cash · F2 Books and ledgers · F3 Basis and events · F4 Evidence and outputs |

The full shelf list, with every call number, is the [Skill Catalog](SKILL_CATALOG.md). The machine-readable version is [`machine/library.json`](../machine/library.json).

## Finding a skill

- **You know the symptom.** Start at [`machine/failure-classes.json`](../machine/failure-classes.json). It maps each failure to one skill.
- **You know the question.** Pick the domain whose question matches, then the lane.
- **The work spans several failures.** Use [`machine/compositions.json`](../machine/compositions.json) for a narrow chain instead of loading a whole domain.

Do not load the whole library. A good agent reads one or two skills per task.

## The catalog, not the folder, decides the shelf

Skills live at stable paths under `skills/operator/` and `skills/financial-truth/`. Those paths are an install surface for adapters and other repos, so they do not move when the shelving changes. The catalog is where subject organization lives. Reshelving a skill is a one-line change to `machine/library.json` and never breaks a link.

## Adding a skill

A skill joins the library only when it earns a place:

1. **It names a real failure.** Something that went wrong in actual work, not a hypothetical. Add the failure class to `machine/failure-classes.json`.
2. **It has one rule.** A sentence a tired person can remember. The rest of the skill is how to apply it.
3. **It can be falsified.** Every skill has a `## Falsify it` section: the check that would prove the skill was not followed.
4. **It is tested.** One activation case, one confuser case, and one behavioral case in `evals/`.
5. **It is shelved once.** One domain, one lane, one call number in `machine/library.json`. If it seems to belong in two lanes, it is probably two skills, or it belongs to the lane whose question it answers first.
6. **It is public-safe.** No credentials, account values, private decisions, or proprietary internals. See [`PUBLIC_BOUNDARY.md`](PUBLIC_BOUNDARY.md).

`python scripts/verify.py` fails if a skill is missing from the catalog, shelved twice, given a duplicate call number, or pointed at a path that does not exist.

## What stays off the shelves

Personal and venture decisions, persona prompts, account figures, private audit findings, and proprietary product internals are not published. When a lesson came from one of those places, the library keeps the method and drops the specifics.
