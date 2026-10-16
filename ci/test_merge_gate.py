#!/usr/bin/env python3
"""Tests for ci/merge_gate.py: automation merges a held head only on both reviewers' standing evidence."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import merge_gate as mg  # noqa: E402

HEAD = "6e6bd1c08401208248e4e6a4f51039d1fb2b28f4"
OTHER = "2db9421555b41e753a558161b751bd8d4c3668d0"
NOW = dt.datetime(2026, 10, 16, 12, 0, tzinfo=dt.timezone.utc)
errors: list[str] = []


def check(name: str, ok: bool) -> None:
    if not ok:
        errors.append(name)


def handoff(head=HEAD, at="2026-10-16T11:00:00Z", **over):
    c = {"id": 1, "body": f"HANDOFF: {head}\n@codex review", "created_at": at,
         "user": {"login": "Tataku"}, "performed_via_github_app": {"slug": "claude"}}
    c.update(over)
    return c


def summary(head=HEAD, any_findings=False):
    st = {"code_review": {"commit_sha": head, "has_any_findings": any_findings, "status": "completed"}}
    return {"id": 2, "user": {"login": "chatgpt-codex-connector[bot]", "type": "Bot"},
            "body": f"<!-- codex-review-state:v1 {json.dumps(st)} -->"}


def ruling(verdict="CLEAR", head=HEAD, login="github-actions[bot]"):
    return {"id": 3, "user": {"login": login},
            "body": f"PM REVIEW — {verdict}\n\n**PR:** #12 · **Exact reviewed head:** `{head}` · **Base:** `x`"}


def finding(head=HEAD):
    return {"user": {"login": "chatgpt-codex-connector[bot]", "type": "Bot"}, "original_commit_id": head, "path": "a",
            "line": 1, "html_url": "u", "body": "**![P2 Badge](x)  Late finding**\n\n<!-- codex-code-review-finding:v1 -->"}


def run(name, conclusion="success", status="completed", started="2026-10-16T10:00:00Z", rid=1, app="github-actions"):
    return {"id": rid, "name": name, "status": status, "conclusion": conclusion if status == "completed" else None,
            "started_at": started, "app": {"slug": app}, "output": {"title": "t"}}


PR = {"number": 12, "state": "open", "draft": False, "head": {"sha": HEAD}, "labels": []}
GREEN = [run("Agent Review"), run("ci", rid=2)]
CLEAR_COMMENTS = [handoff(), summary(), ruling()]


def proven(r):
    """Stands in for pm.check_identity: run id 1..9 proves the default branch's agent-review.yml."""
    if r.get("id") == 66:
        return (r["name"], ".github/workflows/forged.yml", "run:66")
    if r.get("id") == 77:
        return (r["name"], mg.AGENT_REVIEW_PATH, "run:77")
    return (r["name"], mg.AGENT_REVIEW_PATH, "default") if 1 <= r.get("id", 0) <= 9 else None


def v(held=True, comments=CLEAR_COMMENTS, review=(), checks=GREEN, pr=PR, paths=("a.py",), now=NOW, identify=proven,
      failed=None):
    return mg.verdict(pr=pr, head=HEAD, held=held, pr_comments=list(comments), review_comments=list(review),
                      check_runs=list(checks), paths=list(paths), allowed=["Tataku"], now=now, identify=identify,
                      failed=failed)


# the happy path the owner asked for: no person types
check("held head with Agent Review pass and a standing CLEAR merges", v()["allow"])

# the late-finding hole Codex found on ACF #5674
r = v(review=[finding()])
check("a Codex finding posted after the CLEAR blocks the merge", r["block"] and not r["allow"] and "CORRECT" in r["reasons"][0])
check("a finding on an older head does not block this one", v(review=[finding(OTHER)])["allow"])
r = v(checks=GREEN + [run("ci", "failure", rid=3)])
check("any failed check on the head blocks, as the PM reads it", r["block"])

# the CLEAR must be real and current
check("no HANDOFF: held scope is blocked", v(comments=[summary(), ruling()])["block"])
check("a HANDOFF for another head does not count", v(comments=[handoff(OTHER), summary(), ruling()])["block"])
check("a HANDOFF typed on the web (not the claude app) does not count",
      v(comments=[handoff(performed_via_github_app=None), summary(), ruling()])["block"])
check("a forged CLEAR from another login does not count",
      not v(comments=[handoff(), summary(), ruling(login="Tataku")])["allow"])
check("a CLEAR comment with no Codex review behind it does not merge", not v(comments=[handoff(), ruling()])["allow"])
check("a person's copy of Codex's summary does not count",
      not v(comments=[handoff(), dict(summary(), user={"login": "Tataku", "type": "User"}), ruling()])["allow"])
check("a standing CORRECT blocks", v(comments=[handoff(), summary(), ruling("CORRECT")])["block"])
check("a later CORRECT replaces an earlier CLEAR", v(comments=[handoff(), summary(), ruling(), ruling("CORRECT")])["block"])
check("a PR that edits AGENTS.md is held by the PM", v(paths=("AGENTS.md",))["block"])

# held scope never merges on the timeout
r = v(comments=[handoff(at="2026-10-16T08:00:00Z")])
check("held scope waits for a CLEAR even 4 hours after the HANDOFF", r["state"] == "wait" and not r["allow"])
check("non-held scope waits inside 2 hours", v(held=False, comments=[handoff()])["state"] == "wait")
check("non-held scope may merge on the 2-hour timeout",
      v(held=False, comments=[handoff(at="2026-10-16T09:59:00Z")])["allow"])
check("non-held scope with a HANDOFF still needs Agent Review (Codex P1 on #41)",
      not v(held=False, checks=[run("ci", rid=2)])["allow"])
check("non-held scope with a HANDOFF waits while Agent Review runs",
      v(held=False, checks=[run("Agent Review", status="in_progress"), run("ci", rid=2)])["state"] == "wait")
check("non-held scope with a HANDOFF is blocked by a failed Agent Review",
      v(held=False, checks=[run("Agent Review", "failure"), run("ci", rid=2)])["block"])
check("non-held scope with a CORRECT is blocked whatever the clock",
      v(held=False, comments=[handoff(at="2026-10-16T01:00:00Z"), summary(), ruling("CORRECT")])["block"])
check("non-held scope with no HANDOFF is left to its own rule", v(held=False, comments=[])["allow"])

# the first reviewer
check("held scope needs Agent Review", v(checks=[run("ci")])["state"] == "wait")
check("Agent Review still running: wait", v(checks=[run("Agent Review", status="in_progress"), run("ci", rid=2)])["state"] == "wait")
check("Agent Review changes requested blocks", v(checks=[run("Agent Review", "failure"), run("ci", rid=2)])["block"])
check("a newer Agent Review from another app does not stand in",
      v(checks=[run("Agent Review", status="in_progress"), run("Agent Review", started="2026-10-16T11:00:00Z", rid=9, app="x")])["state"] == "wait")
check("a check still running on a held head: wait", v(checks=GREEN + [run("build", status="queued", rid=4)])["state"] == "wait")
check("the PM's own never-completed waiting check does not hold the merge forever (Codex P1 on #41)",
      v(checks=GREEN + [run("PM Review", status="in_progress", rid=5)])["allow"])

# only the trusted reviewer workflow's check counts (Codex P1 on #41)
late = "2026-10-16T11:00:00Z"
check("a newer Agent Review success from another workflow does not count",
      v(checks=[run("Agent Review", "failure"), run("Agent Review", started=late, rid=66), run("ci", rid=2)],
        failed=[])["block"])
check("a newer Agent Review from a PR-branch copy of agent-review.yml does not count",
      v(checks=[run("Agent Review", "failure"), run("Agent Review", started=late, rid=77), run("ci", rid=2)],
        failed=[])["block"])
check("an Agent Review with no provable run does not count",
      v(checks=[run("Agent Review", started=late, rid=50), run("ci", rid=2)])["block"])
check("without an identity check, no Agent Review counts", v(identify=None)["block"])

# the PM's own failed-check list (identity-aware since #40) is what the gate obeys
check("the PM's failed-check list decides, when given",
      mg.verdict(pr=PR, head=HEAD, held=True, pr_comments=CLEAR_COMMENTS, review_comments=[],
                                             check_runs=GREEN + [run("ci", "cancelled", rid=3)], paths=["a.py"],
                                             allowed=["Tataku"], now=NOW, failed=[], identify=proven)["allow"])
check("without the list, any failed run on the head blocks", v(checks=GREEN + [run("ci", "cancelled", rid=3)])["block"])

# the PR itself
check("a draft is not merged", v(pr=dict(PR, draft=True))["state"] == "wait")
check("a hold label stops it", v(pr=dict(PR, labels=[{"name": "owner-hold"}]))["block"])
check("a moved head is not merged", v(pr=dict(PR, head={"sha": OTHER}))["block"])
check("a closed PR is not merged", v(pr=dict(PR, state="closed"))["block"])

# a merge reads the evidence twice, SETTLE_SECONDS apart (Codex P1 on #41: late inline findings)
naps = []
mg.time.sleep = lambda s: naps.append(s)
ALLOW = {"allow": True, "state": "allow", "head": HEAD, "reasons": ["ok"]}
check("the second read waits SETTLE_SECONDS", mg.settled(12, ALLOW, lambda: ALLOW)["allow"] and naps == [mg.SETTLE_SECONDS])
check("a finding that lands between the reads stops the merge",
      not mg.settled(12, ALLOW, lambda: {"allow": False, "state": "block", "head": HEAD, "reasons": ["CORRECT"]})["allow"])
check("a head that moved between the reads stops the merge", not mg.settled(12, ALLOW, lambda: dict(ALLOW, head=OTHER))["allow"])


def unreadable():
    raise ValueError("boom")


check("an unreadable second read stops the merge", not mg.settled(12, ALLOW, unreadable)["allow"])
merged = []
mg._open_prs = lambda base: [{"number": 12, "title": "t"}]
mg._merge = lambda *a: merged.append(a)
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True),
              {"allow": False, "state": "block", "head": HEAD, "reasons": ["late CORRECT"], "handoff": True}])
mg.evaluate = lambda *a, **k: next(reads)
os.environ.setdefault("GITHUB_TOKEN", "t")
os.environ.pop("GITHUB_STEP_SUMMARY", None)
mg.lane("main", "", ["Tataku"], "")
check("the lane does not merge when the second read blocks", merged == [])

# workflow shape
wf = (HERE.parent / ".github" / "workflows" / "ci-merge-lane.yml").read_text()
code = re.sub(r"(?m)^\s*#.*$", "", wf)
check("the lane never checks out or runs the PR", "refs/pull" not in code and "github.event.pull_request.head" not in code)
check("the lane's merge token is optional and passed only to the lane step",
      code.count("merge_token") >= 2 and "MERGE_TOKEN: ${{ secrets.merge_token }}" in code)
check("the job has a timeout", code.count("runs-on:") == 1 and "timeout-minutes:" in code)
check("one lane run at a time per repository, never cancelled mid-merge",
      "cancel-in-progress: false" in code)
caller = (HERE.parent / ".github" / "workflows" / "merge-lane.yml").read_text()
check("a dispatch runs only the default branch's caller (it holds INTEGRATION_TOKEN)",
      "if: github.event_name != 'workflow_dispatch' || github.ref_name == github.event.repository.default_branch"
      in caller)

if errors:
    print("FAIL:\n  " + "\n  ".join(errors))
    raise SystemExit(1)
print("merge gate: all checks pass")
