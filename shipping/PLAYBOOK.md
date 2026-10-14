# The sourced playbook

What Anthropic itself says about making agent and development workflows faster, smarter and cheaper. Every finding is traced only to anthropic.com, claude.com, code.claude.com or Anthropic's GitHub, and each one is mapped to a rule in the [Shipping System](README.md).

**How this was sourced.** Engineering posts are dated by publication. Docs pages change over time and have no publish date, so they show the date they were read: 2026-10-14. Docs quotes were copied from the full page text. Quotes from engineering posts came from an automated page reader, so spot-check any you plan to cite onward. No social-media posts are used, including posts attributed to Anthropic staff. Anything that could not be traced is listed under [Left out](#left-out).

## Findings

<a id="f1"></a>
### F1 · Give the agent a check it can run

> "Give Claude a check it can run: tests, a build, a screenshot to compare. It's the difference between a session you watch and one you walk away from." … "If you can't verify it, don't ship it."

Source: [Best practices](https://code.claude.com/docs/en/best-practices), docs. **In the system:** required checks on the exact tree, and evidence instead of assertions.

<a id="f2"></a>
### F2 · The agent doing the work should not grade it

> "Agents reliably skew positive when grading their own work." · "A reviewer prompted to find gaps will usually report some, even when the work is sound … Tell the reviewer to flag only gaps that affect correctness or the stated requirements."

Sources: [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24) and [Best practices: adversarial review step](https://code.claude.com/docs/en/best-practices#add-an-adversarial-review-step). **In the system:** an independent Agent Reviewer in a fresh context that judges correctness only.

<a id="f3"></a>
### F3 · Find in parallel, verify each candidate, then post

> "A verification step checks candidates against actual code behavior to filter out false positives." · "The check run always completes with a neutral conclusion so it never blocks merging."

Source: [Code Review](https://code.claude.com/docs/en/code-review), docs. The tool is a research preview on Team and Enterprise plans; it averages $15 to $25 and about 20 minutes per review. A repository-root `REVIEW.md` sets a verification bar, a cap on nits, and convergence on re-review. **In the system:** a blocking finding quotes its line at head; [`templates/REVIEW.md`](templates/REVIEW.md); re-review is blocking-only.

<a id="f4"></a>
### F4 · Humans stay accountable for critical code; new AI reviewers start in shadow mode

> "Draw the boundary around access and actions, not around a model's instructions." · "Agents aren't merging code to production unchecked."

Source: [How Anthropic secures its AI-native SDLC](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle) (2026-07-21). It describes risk-tiered codebases with human approval for critical ones, new AI reviewers that only comment until trusted, logged automated approvals that people sample, and agents that cannot deploy their own fixes. **In the system:** lanes, the shadow-mode reviewer with a promotion bar, the owner-only production step, and agents' own identity.

<a id="f5"></a>
### F5 · Keep standing instructions short; load the rest on demand

> "Aim to keep CLAUDE.md under 200 lines by including only essentials." · "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic."

Sources: [Best practices: CLAUDE.md](https://code.claude.com/docs/en/best-practices#write-an-effective-claude-md), [Costs: move instructions to skills](https://code.claude.com/docs/en/costs#move-instructions-from-claude-md-to-skills), and [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29). **In the system:** the 411 to 225 line cut, with detail moved to docs and skills.

<a id="f6"></a>
### F6 · Tests built for agents

> "The test harness should not print thousands of useless bytes." · "Claude can't tell time and, left alone, will happily spend hours running tests instead of making progress."

Sources: [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05) and [Costs: filter test output with a hook](https://code.claude.com/docs/en/costs#offload-processing-to-hooks-and-skills). **In the system:** terse, failure-first output in agent sessions; a fast PR tier with the whole suite nightly.

<a id="f7"></a>
### F7 · Start simple; more agents cost more

> "Multi-agent systems use about 15× more tokens than chats." · "You should consider adding complexity only when it demonstrably improves outcomes."

Sources: [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06-13) and [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (2024-12-19). **In the system:** one Builder plus a strong check by default, and parallel agents only for breadth.

<a id="f8"></a>
### F8 · Every harness piece is a bet about a model weakness

> "Every component in a harness encodes an assumption about what the model can't do on its own."

Source: [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps). **In the system:** a harness audit after each model upgrade.

<a id="f9"></a>
### F9 · Long-running work keeps state on disk and checks end to end

Source: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26): a progress file, one feature at a time, commits as checkpoints, and browser-driven end-to-end tests that caught what unit tests missed. **In the system:** per-PR notes compiled at promotion; screenshots driven through the running app.

<a id="f10"></a>
### F10 · Unattended runs need self-contained prompts and known gaps covered

- Routine prompts "must be self-contained and explicit about what to do and what success looks like", and a green run "does not mean the task in your prompt succeeded". Pick an off-the-hour start time. [Routines](https://code.claude.com/docs/en/routines)
- "GitHub does not emit a webhook when the base branch advances and creates a merge conflict." [Auto-fix pull requests](https://code.claude.com/docs/en/claude-code-on-the-web#auto-fix-pull-requests)
- Commits made with the default `GITHUB_TOKEN` do not trigger CI. Cap runs with `--max-turns`, job timeouts and concurrency groups. [GitHub Actions](https://code.claude.com/docs/en/github-actions)
- Auto mode's classifier misses 17% of real overeager actions and is "not a drop-in replacement for careful human review on high-stakes infrastructure". [Auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) (2026-03-25)

**In the system:** caps on every model job, an app token for any job that pushes, and a person on held scope.

<a id="f11"></a>
### F11 · Measure with small evals drawn from real failures

> "20-50 simple tasks drawn from real failures is a great start." Regression evals "should have a nearly 100% pass rate."

Source: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2026-01-09). **In the system:** canary replays of past defects measure the reviewer's recall, and a red nightly is news.

## Recommendations and where they stand

Status is from the rollout tracker on 14 October 2026, with PR states checked live on GitHub. PR numbers refer to the reference repository unless they name another one.

| # | Recommendation | From | Status |
|---|---|---|---|
| R1 | Run the new reviewer in shadow mode first | F4 | Done: report-only, with a written promotion and demotion bar |
| R1b | Separate grader, plus a second vendor on critical code | F2, F4 | Done: Agent Review on every PR; a second-vendor CLEAR (or 2 hours with no ruling) before ready on authority and held PRs (owner decision 2026-10-14, replacing an every-PR rule; the reference repo's written rule update is pending); a held hand merge waits for it too (merged) |
| R2 | Find, then verify each finding before it can block | F3 | Done |
| R3 | Correctness only, nits never block, re-review converges | F2, F3 | Done |
| R4 | Gate merges on the count of blocking findings | F3 | Owner decides, after shadow data meets the bar |
| R5 | A fixer routine for red PRs | F10 | Paused until R6 lands |
| R6 | Agents get their own GitHub identity, with limits on access | F4, F10 | Waiting on the owner to create the App, ruleset and variables |
| R7 | Terse test output for agents | F6 | Built (9 lines instead of 2,531), waiting to merge |
| R8 | A fast sampled PR tier plus a nightly full regression | F6, F11 | Partly done: the PR tier and nightly exist; further cuts are built |
| R9 | Caps on every model job; reusable workflows across repos | F10 | Partly done: the reviewer is capped, and the shared layer is in this repo ([#20](https://github.com/Tataku/Dale-OS/pull/20)) |
| R10 | Instructions file under about 200 lines | F5 | Done: 411 to 225 lines |
| R11 | Deterministic promotion gates | F4, F5 | In progress: tooling and the frozen cut merged, receipt built |
| R12 | Post-deploy production check | F10 | Owner decides: built switched off |
| R13 | Changelog fragments instead of one shared file | F9 | Not started (by analogy to F9; Anthropic does not describe changelogs) |
| R14 | Screenshots on UI PRs, driven through the running app | F1, F2, F9 | Done: before and after screenshots on UI PRs (merged 2026-10-14) |
| R15 | A weekly digest routine, off the hour, updating one page | F10 | Done as a Friday digest issue (merged 2026-10-14) |
| R16 | Strip the harness as models improve | F7, F8 | Adopted as a principle |
| R17 | Harness audit after each model upgrade | F8 | Done: procedure written, first run completed |

<a id="left-out"></a>
## Left out

These could not be traced to a primary source, so nothing here depends on them:

- A post attributed to an Anthropic engineer about cutting agent cost by 95%. No Anthropic-hosted source was found, and the owner says it was fake.
- "91 PRs in 24 hours" from a third-party post about a software factory. The original was not found.
- A "slot machine" description of how Anthropic teams work. It does not appear in [How Anthropic teams use Claude Code](https://claude.com/resources/articles/how-anthropic-teams-use-claude-code) (2025-07-24).
