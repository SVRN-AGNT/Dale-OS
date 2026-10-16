# CLAUDE.md

Claude Code reads this file instead of `AGENTS.md` when both exist, so it imports the agent entry point first:

@AGENTS.md

## Second-vendor review (the PM)

This repository runs the shared PM caller (`.github/workflows/pm-review.yml`, from SVRN-AGNT/Dale-OS `ci/README.md#the-pm-caller`) with `provider: chatgpt`: the PM rules from Codex's own GitHub review, which runs on the owner's ChatGPT plan with no API key. Codex is OpenAI, a different vendor from Claude, and it reviews a PR only when a Claude session asks for it.

- On every high-stakes PR (money, sync, schema, access) and every PR that touches held paths (`.github/workflows/` at least), post a PR comment of exactly two lines. The first starts with `HANDOFF:` at byte zero and names the PR's current head as the full 40-character sha; the second asks Codex:

  ```text
  HANDOFF: <full 40-character head sha>
  @codex review
  ```

- Post it with the GitHub tools, so it comes through the `claude` app. Write `@codex` nowhere else (PR bodies, other comments): any mention starts a Codex review and spends the plan's limited review quota.
- The PM replies `PM REVIEW — CLEAR | CORRECT | HOLD` and sets a `PM Review` check on that head. Any Codex finding, of any priority, or any failed check on the head is CORRECT; a PR that edits an `AGENTS.md` is HOLD. A push revokes the ruling, so post a new HANDOFF for the new head.
- Such a PR merges only after a CLEAR on its current head, or after 2 hours with no ruling. Either way, first re-run the PM for that HANDOFF by dispatch (`workflow_dispatch` from the default branch with its `comment_id` and `pr`) and wait for the run to finish. That run reads every Codex finding and failed check on the head, including an inline finding posted after the CLEAR, which wakes nothing on its own, and turns it into CORRECT. Only a run that concluded `success` and whose "Resolve the HANDOFF and its PR" step logged a notice naming that head (its first 8 characters) counts: `the CLEAR on <head> still stands` before merging on a CLEAR, or `Waiting on Codex's review of <head>` (or `Waiting on Codex's receipt for <head>`) before counting the timeout. A failed, cancelled or skipped run, or one that logged any other notice (a refused dispatch, a stale head), does not count; fix the cause and dispatch again. Any new ruling the run posts replaces the old one. CORRECT or HOLD blocks it until resolved. The PM never approves or merges anything.
