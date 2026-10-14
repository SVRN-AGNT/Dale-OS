---
name: loop-closure
description: Close, retire, and count open loops so agent work finishes instead of accumulating. Use at session start or end, for "loose ends", "full audit", "what's unfinished", backlog or queue hygiene, open PRs and branches piling up, follow-on work spawning from blocked items, capped work tiers filling up, or when an agent fleet opens more work than it finishes. Do not use to plan net-new features or to rank a fresh backlog from scratch.
---

# Loop Closure

## Rule

**Capture is not the problem. Retirement is. Report net loops: closed minus opened.**

A loop is any named, unfinished work: a queue item, an open PR, a pushed branch with no PR, a deferred finding, a pending sign-off. It has four states: **captured → tracked → closed → retired**. Agents are excellent at the first and weak at the last three, so queues grow monotonically until the file that bounds attention becomes too expensive to read.

## Workflow

1. **Close on sight, first.** Before opening new work, check whether anything already open now satisfies its own exit condition. Close it in the same session that made it true.
2. **Retire what you closed.** A checked box that stays in the queue is a second copy of the history occupying the tier that bounds attention. Remove it, keeping one line (title, reference, date) in a recently-closed list.
3. **Enforce caps by displacement, not addition.** A capped tier is a ranked list. A new item enters by displacing one and naming what it displaced, or it goes to the backlog. Never "item 6" in a list of five.
4. **Name blocked-closure gates; stop their children stacking.** When an item cannot close because a gate (review, promotion, a human look) is pending, say so in one line and do not file its follow-on polish as new loops. If the gate belongs to a person, escalate it instead of multiplying it.
5. **Run both audit passes.** A "full audit" is two passes, and the second is the one that gets skipped:
   - **Runtime health:** what is failing or drifting now (red checks, open PRs, branch state)?
   - **Completion tail:** what shipped but is not finished (deferrals, pending verification, open judgment calls, unfinished work written only in prose)?
   Report them separately. Nothing goes red when the completion tail is ignored.
6. **Treat stale loops as decaying.** Improving the architecture around an open PR is a cost to that PR, not a neutral event. Count open work before opening a new lane; anything far behind its base gets a decision this session: rebase, close, or escalate.
7. **Report the net.** State loops closed, retired, and opened. A negative net is a real result and must be visible, not buried in a deferral list.

## Design note

Closure duties must be cheap enough to run. An affordable duty that runs beats an accurate one that doesn't: an append-only one-line log of what opened and closed this session is better than a full reconciliation nobody performs.

## Falsify it

Count before and after. If the session's audit produced more open items than it closed, it did not close anything. If a capped tier holds completed items, its cap has silently shrunk. If an item's only open reason is a gate nobody was told about, it is not tracked, it is lost.

## Stop conditions

- Closing an item requires a decision only its owner can make.
- The authoritative state of an item (merged, deployed, abandoned) cannot be verified live.

Do not close from memory. Mark it unverified and name who must decide.

## Output

NET LOOPS (closed · retired · opened) · RUNTIME HEALTH · COMPLETION TAIL · DISPLACEMENTS · BLOCKED GATES (owner) · STALE LOOPS AND DECISION.
