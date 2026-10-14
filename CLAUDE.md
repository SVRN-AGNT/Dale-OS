# CLAUDE.md

Claude Code reads this file instead of `AGENTS.md` when both exist, so it imports the agent entry point first:

@AGENTS.md

## Second-vendor review (the PM)

This repository runs the shared PM caller (`.github/workflows/pm-review.yml`, from SVRN-AGNT/Dale-OS `ci/README.md#the-pm-caller`). The PM is OpenAI Codex, a different vendor from Claude, and it reviews a PR only when a Claude session asks for it.

- On every high-stakes PR (money, sync, schema, access) and every PR that touches held paths (`.github/workflows/` at least), post a PR comment that starts with `HANDOFF:` at byte zero and names the PR's current head as the full 40-character sha. Template: SVRN-AGNT/Dale-OS `shipping/templates/HANDOFF.md`.
- Post it with the GitHub tools, so it comes through the `claude` app. The PM skips a comment a person typed, a comment that does not start with `HANDOFF:`, and a sha that is not the live head.
- The PM replies `PM REVIEW — CLEAR | CORRECT | HOLD | OWNER GATE` and sets a `PM Review` check on that head. A push revokes it, so post a new HANDOFF for the new head.
- Such a PR merges only after a CLEAR on its current head, or after 2 hours with no ruling. CORRECT or HOLD blocks it until resolved. The PM never approves or merges anything.
