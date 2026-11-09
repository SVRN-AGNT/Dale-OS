# Knowledge Vault

**A reference design for agent memory that gets cleaner over time instead of longer: the git-backed vault several
Dale OS skills came from.**

Most agent memory is a scrapbook. Notes pile up, an answered question is asked again in the next session, a raw
paste is later read as fact, and a note that said a PR was open is still quoted a week after it merged. The vault
below is the owner's private working memory across several repositories. It runs on plain Markdown in a git
repository, read and written by Claude Code sessions. This page publishes its structure and rules, not its contents.

## The one idea: keep four things apart

| Layer | What it holds | What it may never do |
|---|---|---|
| **Raw context** | Whatever arrived: notes, pastes, exports, screenshots | Be edited, or be cited as verified |
| **Verified evidence** | Claims that were checked, with what checked them | Hold a claim marked done before its check |
| **Durable memory** | Lessons that change what an agent does next time, and owner decisions | Grow without passing a gate |
| **Authorized action** | What a session may actually do now | Be inferred from memory alone |

Most of the failures above are one layer read as another: raw text read as evidence, an old note read as current
state, a lesson stored without proof read as a rule. The folders exist to keep those reads apart.

## Layout

| Folder | Holds | Rule |
|---|---|---|
| `raw/` | Captured sources, as they arrived | **Immutable.** Never rewritten, reformatted or deleted. A correction is a new file linked to the old one. Metadata goes in a sibling ingestion note, never inside the source |
| `wiki/` | Pages that synthesise sources: projects, repositories, operations, research | A page is meant to cite its sources and carry a `Contradictions & Open Tensions` section; the direct writer's pages are exempt (below) |
| `decisions/` | Numbered owner decisions, `NNNN-<slug>.md` | **Append-only.** See below |
| `evidence-ledger/` | One Claim / Evidence / Verified table per long task | A row reads `Not yet` until checked, and is never reported as done |
| `memory/` | Lessons, corrections, confirmed patterns, rejected ideas, standing owner rules, playbooks | Enters only through the promotion gate |
| `indexes/` | Registries: decisions, open loops, workstreams, repositories, memory | Updated in the same change as the page they list. Finished rows move to an archive so the live index reads whole |
| `templates/` | Skeletons for each page type | A new page starts from one |
| `commands/` | Written procedures for repeated work: ingest, query, decision, reconcile, handoff, writeback, weekly review | A session follows the procedure instead of improvising it |

## Decisions are append-only

- A decision is never edited after acceptance and never deleted. To change course, a new decision names the old one
  in `supersedes`, and the old one's `status` flips to `superseded` with a `superseded_by` link. That flip is the
  only edit a closed record ever receives.
- `status` is exactly one of `proposed`, `accepted` or `superseded`. A superseded record is history: anything reading
  for current doctrine skips it and follows the link.
- **Only the owner ratifies.** A session may build a structure and propose it; the decision that adopts it is written
  only after the owner confirms. In the vault's own history, a commit that built a new taxonomy was explicitly left
  unratified until a later decision record adopted it.
- A decision records its context, the decision, alternatives considered and consequences, with the owner's words
  quoted where possible.

The portable rule is [`latest-authority`](../skills/operator/latest-authority/SKILL.md): an answered decision is
carried forward and not re-asked unless new conflicting evidence appears.

## Memory passes a gate

A note enters `memory/` only if it is durable, verified, changes future behaviour, is not already documented, is
specific enough to act on, and corrects or confirms a pattern that matters. Otherwise it stays in `raw/`, the work
queue or a report. Existing notes are updated rather than duplicated, and a note proven wrong is superseded or
deleted. Memory is the one layer meant to shrink. The portable form is
[`memory-promotion`](../skills/operator/memory-promotion/SKILL.md).

## Contradictions are kept

When two sources or two owner statements disagree, both are recorded and attributed, and the current working stance
is stated, or the tension is marked unresolved. The losing side is never silently overwritten. If a decision
resolves it, the page links the decision and keeps the tension as history.

## The vault is never live state

Vault memory goes stale. Before a session says a PR is open, a merge is pending or a task is the next best action,
it checks the live source and cites it, or it labels the claim as vault state as of a date. A fact has one home: the
model version pin, for example, is written in exactly one page, and everything else links to it. The portable form
is [`verify-before-cite`](../skills/operator/verify-before-cite/SKILL.md).

## Modes and rituals

Each non-trivial session states its mode, and the mode limits what it may do:

| Mode | Allowed | Not allowed |
|---|---|---|
| **Assess** | Read, diagnose, recommend | Modify files, open PRs, update memory |
| **Plan** | Name files, phases, checks and risks | Modify files without the owner's word |
| **Execute** | Make the authorised change | Skip the evidence ledger or the unverified-claims section |
| **Memorize** | Add, merge or supersede memory; write the session report | Feature work |

Assess is the default when the owner is thinking aloud or asks for an opinion. A session starts by loading, in
order, the owner's current instruction, the repository state, the work-queue item, the relevant decisions and
memory, the live git state and known risks and prior failures, then states its goal and what must be verified before it can claim success. It closes with the outcome, the
evidence, what stayed unverified, and any memory it proposes. The execution charter
([`execution-charter`](../skills/operator/execution-charter/SKILL.md)) and the completion contract
([`completion-contract`](../skills/operator/completion-contract/SKILL.md)) are the portable halves of those rituals.

## Writers

More than one agent writes to the vault. Claude sessions land changes through pull requests that Agent Review checks;
vault documents are not held scope and self-merge under a written owner decision, while code in the same
repository goes through the held lane. A separate assistant writes its own pages directly to the default branch,
most days, outside any pull request. When the vault's structural lint was a merge gate, that writer's pages turned
every pull request red, and sessions spent work repairing pages they had not written. The owner then ruled the lint
advisory and exempted that writer's pages from the page contract, preferring fewer gates. The lesson we draw, an
inference rather than the ruling's stated reason: a gate has to sit on the path every writer takes, or it punishes
the wrong one.

## Known limits

- **Built for one owner.** Ratification, contradictions and the standing rules assume a single authority. A team
  would need a rule for whose answer wins.
- **Git is the only access control.** Anyone who can write to the repository can write to every layer. The append-only
  and immutability rules are instructions, not enforced checks.
- **Structure drifts.** With the lint advisory, pages from the direct writer can miss sections, and nothing fails
  when they do.
- **Modes are discipline, not enforcement.** No hook stops a write during Assess; the limits depend on the agent
  following them.
- **Unmeasured.** No record counts how often an answered decision was re-asked, or a stale state cited, before and
  after the vault. The design rests on observed failures, not on a measured reduction.
