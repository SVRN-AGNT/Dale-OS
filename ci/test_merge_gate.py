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


CI = ".github/workflows/ci.yml"


def wfrun(conclusion="success", status="completed", path=CI, head=HEAD, created="2026-10-16T10:00:00Z", wid=500):
    return {"id": wid, "path": path, "head_sha": head, "status": status,
            "conclusion": conclusion if status == "completed" else None, "created_at": created}


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
      failed=None, required=(CI,), workflow_runs=None, foreign_edits=(), reviewed_head=lambda r: HEAD):
    return mg.verdict(pr=pr, head=HEAD, held=held, pr_comments=list(comments), review_comments=list(review),
                      check_runs=list(checks), paths=list(paths), allowed=["Tataku"], now=now, identify=identify,
                      failed=failed, required=required,
                      workflow_runs=[wfrun()] if workflow_runs is None else workflow_runs, foreign_edits=foreign_edits,
                      reviewed_head=reviewed_head)


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

# any standing ruling but CLEAR blocks, whatever its spelling (the PM writes "OWNER GATE")
check("an OWNER GATE ruling blocks a non-held PR at the timeout",
      v(held=False, comments=[handoff(at="2026-10-16T08:00:00Z"), ruling("OWNER GATE")])["block"])
# an edited HANDOFF restarts the clock (the PM only answers new comments)
check("a day-old HANDOFF edited a minute ago to name this head does not start at the timeout",
      v(held=False, comments=[handoff(at="2026-10-15T10:00:00Z", updated_at="2026-10-16T11:59:00Z")])["state"] == "wait")

# a completed Codex review with no readable ruling never reaches the timeout (it may hide an unparsed or deleted finding)
r = v(held=False, comments=[handoff(at="2026-10-16T08:00:00Z"), summary(any_findings=True)])
check("a finished Codex review with no readable ruling does not merge on the timeout", not r["allow"])
check("no review at all still merges a non-held PR on the timeout",
      v(held=False, comments=[handoff(at="2026-10-16T08:00:00Z")])["allow"])

# a Codex comment someone else edited cannot be trusted (write access can edit any comment; the author stays Codex)
check("a Codex comment edited by someone else blocks the merge",
      v(foreign_edits=["comment 2 by Tataku"])["block"])
check("it blocks a non-held PR on the timeout too",
      v(held=False, comments=[handoff(at="2026-10-16T08:00:00Z")], foreign_edits=["comment 2 by x"])["block"])
cx = {"login": mg.CODEX_LOGIN}


def node(i, author=cx, editor=None):
    return {"databaseId": i, "author": author, "editor": editor}


def conn(*nodes, more=False):
    return {"pageInfo": {"hasNextPage": more}, "nodes": list(nodes)}


check("Codex editing its own comments is fine", mg.foreign_edits_in(
    {"comments": conn(node(1, editor=cx)), "reviews": conn(dict(node(2), comments=conn(node(3, editor=cx))))}) == [])
check("an edit by anyone else to a Codex summary is caught", mg.foreign_edits_in(
    {"comments": conn(node(1, editor={"login": "Tataku"})), "reviews": conn()}) == ["comment 1 by Tataku"])
check("an edit by anyone else to a Codex review or inline finding is caught", len(mg.foreign_edits_in(
    {"comments": conn(), "reviews": conn(dict(node(2, editor={"login": "github-actions"}),
                                              comments=conn(node(3, editor={"login": "x"}))))})) == 2)
check("someone editing their own comment is not Codex's evidence", mg.foreign_edits_in(
    {"comments": conn(node(1, author={"login": "Tataku"}, editor={"login": "Tataku"})), "reviews": conn()}) == [])
try:
    mg.foreign_edits_in({"comments": conn(more=True), "reviews": conn()})
    check("an unread page of comments fails closed", False)
except ValueError:
    pass

# a dispatch runs whatever the chosen ref defines, so it counts as CI only from the default branch (Codex P1 on #41)
PR_MAIN = dict(PR, base={"repo": {"default_branch": "main"}})
check("a dispatched CI run on the PR branch is not CI", v(pr=PR_MAIN, workflow_runs=[
    dict(wfrun(), event="workflow_dispatch", head_branch="feature")])["state"] == "wait")
check("it cannot mask a failed pull_request run either", v(pr=PR_MAIN, workflow_runs=[
    wfrun("failure", wid=1), dict(wfrun(created="2026-10-16T11:00:00Z", wid=2), event="workflow_dispatch",
                                  head_branch="feature")])["block"])
check("a dispatch from the default branch counts", v(pr=PR_MAIN, workflow_runs=[
    dict(wfrun(), event="workflow_dispatch", head_branch="main")])["allow"])
check("a pull_request run counts", v(pr=PR_MAIN, workflow_runs=[dict(wfrun(), event="pull_request")])["allow"])

# an Agent Review check claiming the trusted run cannot outvote that run's own failure (Codex P1 on #41)
genuine = lambda c="success", status="completed", stamp="run:900:1": dict(  # noqa: E731
    run("Agent Review", c, status=status), external_id=stamp)
forged = dict(run("Agent Review", started="2026-10-16T10:30:00Z", rid=3), external_id="run:900:1")
check("a forged pass next to the same run's failure blocks",
      v(checks=[genuine("failure"), forged, run("ci", rid=2)], failed=[])["block"])
check("a forged pass while the same run is still going waits",
      v(checks=[genuine(status="in_progress"), forged, run("ci", rid=2)], failed=[])["state"] == "wait")
check("a genuine re-run (another run) still passes after an old failure",
      v(checks=[genuine("failure", stamp="run:899:1"), forged, run("ci", rid=2)], failed=[])["allow"])
check("so does a re-run attempt of the same run",
      v(checks=[genuine("failure", stamp="run:900:1"), dict(forged, external_id="run:900:2"), run("ci", rid=2)],
        failed=[])["allow"])

# the claimed run must have been started for this head (Codex P1 on #41)
check("a pass claiming a run started for another PR's head blocks", v(reviewed_head=lambda r: OTHER)["block"])
check("a pass whose run cannot be read blocks", v(reviewed_head=lambda r: None)["block"])
check("without a run reader no Agent Review counts", v(reviewed_head=None)["block"])
check("a run started for this head (any case) counts", v(reviewed_head=lambda r: HEAD.upper())["allow"])

# _reviewed_head on GitHub's own run records (Codex P1 on #41: "bind pull_request_target reviews through their PR
# payload"). Recorded 2026-10-17 from GET /actions/runs/{id}, trimmed to the fields read. A run's pull_requests[]
# head is the PR's head *now*, not the head the run reviewed: run 38977044284 reviewed 2c636321 and its payload
# already reads 33efaa99. Binding through it would let an older head's pass count, so head_sha stays the binding.
RECORDED = {
    "/actions/runs/38977044284": {"event": "pull_request_target", "head_sha": "2c63632102abdaaa916014039a7e743570bc115e",
                                  "pull_requests": [{"number": 41, "head": {"sha": "33efaa9925eedfead28974493ba15f5c3dff615d"}}]},
    "/actions/runs/38978021996": {"event": "pull_request_target", "head_sha": "33efaa9925eedfead28974493ba15f5c3dff615d",
                                  "pull_requests": [{"number": 41, "head": {"sha": "33efaa9925eedfead28974493ba15f5c3dff615d"}}]},
    # a dispatch records the default branch's tip and no PR
    "/actions/runs/38953200612": {"event": "workflow_dispatch", "head_sha": "3c8b2f417e66f6c65a5276a06057ada84441aea3",
                                  "pull_requests": []},
}
LIVE_HEAD = "33efaa9925eedfead28974493ba15f5c3dff615d"


def stamped(rid):
    return dict(run(mg.AGENT_REVIEW, rid=rid), external_id=f"run:{rid}:1")


mg.pm._api, saved_api = (lambda method, path, *a, **k: RECORDED.get(path.split("/attempts/")[0])), mg.pm._api
check("a pull_request_target run that reviewed an older head binds to that head, not the PR's live head",
      mg._reviewed_head(stamped(38977044284)) == "2c63632102abdaaa916014039a7e743570bc115e")
check("a pull_request_target run started for this head binds to it", mg._reviewed_head(stamped(38978021996)) == LIVE_HEAD)
check("a dispatched run is never this head's review", mg._reviewed_head(stamped(38953200612)) != LIVE_HEAD)
check("a run GitHub has no record of binds to nothing", mg._reviewed_head(stamped(1)) is None)
mg.pm._api = saved_api

check("a PR GitHub cannot list in full never merges (Codex P2 on #41)", mg.verdict(
    pr=PR, head=HEAD, held=True, pr_comments=list(CLEAR_COMMENTS), review_comments=[], check_runs=list(GREEN),
    paths=["a.py"], allowed=["Tataku"], now=NOW, identify=proven, required=(CI,), workflow_runs=[wfrun()],
    complete=False)["block"])

def receipt(head=HEAD, clean=False):
    return {"user": {"login": "chatgpt-codex-connector[bot]", "type": "Bot"},
            "body": "<!-- codex-review-receipt:v1 -->\n\n" + ("Codex Review: Didn't find any major issues." if clean else
                    "### Codex Review\n\nHere are some automated review suggestions") +
                    f"\n\n**Reviewed commit:** `{head[:10]}`"}


check("Codex's suggestions review of this head blocks even with its findings deleted (Codex P1 on #41)",
      mg.verdict(pr=PR, head=HEAD, held=True, pr_comments=list(CLEAR_COMMENTS), review_comments=[],
                 check_runs=list(GREEN), paths=["a.py"], allowed=["Tataku"], now=NOW, identify=proven,
                 required=(CI,), workflow_runs=[wfrun()], codex_reviews=[receipt()])["block"])
check("a suggestions review of an older head does not block this one", not mg.codex_suggested([receipt(OTHER)], HEAD))
check("Codex's clean receipt is not a suggestions review", not mg.codex_suggested([receipt(clean=True)], HEAD))
check("someone else's copy of the receipt does not count",
      not mg.codex_suggested([dict(receipt(), user={"login": "Tataku", "type": "User"})], HEAD))

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
r = v(checks=[run("Agent Review", "failure"), run("Agent Review", started="2026-10-16T11:00:00Z", rid=9, app="x"),
              run("ci", rid=2)], failed=[])
check("a newer Agent Review from another app does not stand in", r["block"] and "Agent Review" in r["reasons"][0])
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

# the repository's CI must have run and passed (Codex P1 on #41: a HANDOFF can clear before CI starts)
check("a required workflow that has not started: wait", v(workflow_runs=[])["state"] == "wait")
check("a required workflow that was skipped blocks", v(workflow_runs=[wfrun("skipped")])["block"])
check("a required workflow still running: wait", v(workflow_runs=[wfrun(status="in_progress")])["state"] == "wait")
check("non-held scope needs the required workflow too", v(held=False, workflow_runs=[])["state"] == "wait")
check("the newest run of the workflow decides",
      v(workflow_runs=[wfrun(), wfrun("failure", created="2026-10-16T11:00:00Z", wid=501)])["block"])
check("a run of another workflow file does not stand in", v(workflow_runs=[wfrun(path=".github/workflows/x.yml")])["state"] == "wait")
check("a run on another head does not stand in", v(workflow_runs=[wfrun(head=OTHER)])["state"] == "wait")
# Codex P1 on #41: a check named like the CI job, posted by any workflow, is not the CI
check("a forged success check named like the CI does not stand in for a failed CI run",
      v(checks=GREEN + [run("ci", rid=8)], workflow_runs=[wfrun("failure")], failed=[])["block"])
os.environ["REQUIRED_WORKFLOWS"] = ".github/workflows/ci.yml\n .github/workflows/b.yml \n"
check("REQUIRED_WORKFLOWS is one path per line",
      mg.required_workflows() == [".github/workflows/ci.yml", ".github/workflows/b.yml"])
os.environ.pop("REQUIRED_WORKFLOWS")
check("no REQUIRED_WORKFLOWS means none", mg.required_workflows() == [])

# an abandoned in-progress run, superseded by a newer completed run of the same proven check, is not running
check("an abandoned run superseded by a newer completed one does not hold the merge",
      v(checks=GREEN + [run("build", status="in_progress", started="2026-10-16T09:00:00Z", rid=4),
                        run("build", started="2026-10-16T10:30:00Z", rid=5)])["allow"])
check("a running run with no newer completed one still waits",
      v(checks=GREEN + [run("build", status="in_progress", started="2026-10-16T11:00:00Z", rid=4),
                        run("build", started="2026-10-16T10:30:00Z", rid=5)])["state"] == "wait")
check("an unprovable running run is never set aside",
      v(checks=GREEN + [run("build", status="in_progress", started="2026-10-16T09:00:00Z", rid=40),
                        run("build", started="2026-10-16T10:30:00Z", rid=41)])["state"] == "wait")

# the PM's own failed-check list (identity-aware since #40) is what the gate obeys
check("the PM's failed-check list decides, when given",
      mg.verdict(pr=PR, head=HEAD, held=True, pr_comments=CLEAR_COMMENTS, review_comments=[],
                                             check_runs=GREEN + [run("ci", "cancelled", rid=3)], paths=["a.py"],
                                             allowed=["Tataku"], now=NOW, failed=[], identify=proven,
                                             reviewed_head=lambda r: HEAD)["allow"])
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
answers = iter([{"mergeable": None}, {"mergeable": None}, {"mergeable": True, "mergeable_state": "clean"}])
check("a null mergeable is polled until GitHub computes it (Codex P1 on #41)",
      mg.mergeable_now(12, {"mergeable": None}, lambda: next(answers)) == (True, "clean"))
check("a known mergeable is not re-read",
      mg.mergeable_now(12, {"mergeable": False, "mergeable_state": "dirty"}, unreadable) == (False, "dirty"))
check("a mergeable that stays null is not a merge", mg.mergeable_now(12, {"mergeable": None}, lambda: {})[0] is None)
answers = iter([{"mergeable": True, "mergeable_state": "behind"}])
check("the state comes from the same read as the mergeable it resolves (Codex P1 on #41)",
      mg.mergeable_now(12, {"mergeable": None, "mergeable_state": "unknown"}, lambda: next(answers)) == (True, "behind"))
check("clean is merge-ready", mg.not_ready(True, "clean", HEAD, []) == "")
for state in ("blocked", "behind", "dirty", "draft", "unknown", None, "something-new"):
    check(f"{state} is never merge-ready on a bypass token (Codex P1 on #41)", mg.not_ready(True, state, HEAD, []) != "")
check("unstable with every commit status green is merge-ready",
      mg.not_ready(True, "unstable", HEAD, [{"context": "Vercel", "state": "success"}]) == "")
for st in ("failure", "error", "pending"):
    check(f"unstable with a {st} commit status is not merge-ready",
          mg.not_ready(True, "unstable", HEAD, [{"context": "Vercel", "state": st}]) != "")
combined = {}
mg.pm._api, saved_api = (lambda *a, **k: combined), mg.pm._api
combined = {"state": "pending", "total_count": 0, "statuses": []}
check("no commit statuses at all is green", mg._statuses(HEAD) == [])
combined = {"state": "failure", "total_count": 150, "statuses": [{"context": f"c{i}", "state": "success"} for i in range(100)]}
check("a red status past the first page still counts (Codex P2 on #41)", mg._statuses(HEAD) != [])
combined = {"state": "success", "total_count": 150, "statuses": []}
check("a green combined status is green", mg._statuses(HEAD) == [])
mg.pm._api = saved_api
real_statuses, mg._statuses = mg._statuses, lambda h: unreadable()
check("unstable whose statuses cannot be read is not merge-ready", mg.not_ready(True, "unstable", HEAD) != "")
mg._statuses = real_statuses
check("a null mergeable is never merge-ready", mg.not_ready(None, "clean", HEAD, []) != "")
# a PR GitHub cut off at 3000 files is held even when renames make its name list look complete (Codex P2 on #41)
names = mg._PathList(["a.py", "old.py"] * 1500)
names.records = 3000
check("truncation is judged by file records, not names", names.records < 3001 and len(set(names)) < 3001)
check("--settle refuses a settled read that is not merge-ready", mg.not_ready(True, "blocked", HEAD, []) != "")
check("a caller's MERGE_READY_STATES can name a state its own rule makes normal",
      mg.not_ready(True, "blocked", HEAD, [], ready=("clean", "blocked")) == "")
import contextlib, io  # noqa: E401,E402
saved_eval = mg.evaluate
mg.evaluate = lambda *a, **k: dict(ALLOW, mergeable=True, mergeable_state="blocked")
os.environ.pop("GITHUB_OUTPUT", None)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    mg.main(["check", "--pr", "12", "--settle"])
check("check --settle does not allow a head GitHub reports blocked (Codex P1 on #41)",
      json.loads(buf.getvalue())["allow"] is False)
mg.evaluate = lambda *a, **k: dict(ALLOW, mergeable=True, mergeable_state="clean")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    mg.main(["check", "--pr", "12", "--settle"])
check("check --settle allows a clean settled head", json.loads(buf.getvalue())["allow"] is True)
mg.evaluate = saved_eval
os.environ["MERGE_READY_STATES"] = "clean, blocked"
check("MERGE_READY_STATES is read from the environment", mg.merge_ready_states() == ("clean", "blocked"))
os.environ.pop("MERGE_READY_STATES")
check("the default merge-ready states never include blocked", "blocked" not in mg.merge_ready_states())
merged = []
mg._open_prs = lambda base: [{"number": 12, "title": "t"}]
mg._merge = lambda *a: merged.append(a)
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state="clean"),
              {"allow": False, "state": "block", "head": HEAD, "reasons": ["late CORRECT"], "handoff": True}])
mg.evaluate = lambda *a, **k: next(reads)
os.environ.setdefault("GITHUB_TOKEN", "t")
os.environ.pop("GITHUB_STEP_SUMMARY", None)
mg.lane("main", "", ["Tataku"], "")
check("the lane does not merge when the second read blocks", merged == [])
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=None), dict(ALLOW, mergeable=True, mergeable_state="clean")])
mg.pm._api = lambda *a, **k: {"mergeable": True, "mergeable_state": "clean"}
mg.lane("main", "", ["Tataku"], "")
check("the lane merges once a null mergeable resolves to true", len(merged) == 1)
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=None, mergeable_state="unknown")])
mg.pm._api = lambda *a, **k: {"mergeable": True, "mergeable_state": "behind"}
mg.lane("main", "", ["Tataku"], "")
check("a null that resolves to behind is not merged", len(merged) == 1)
# Codex P1 on #41: no mergeability poll may sit between the final evidence read and the merge call.
order = []
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=None),
              dict(ALLOW, mergeable=True, mergeable_state="clean")])
mg.evaluate = lambda *a, **k: (order.append("evidence"), next(reads))[1]
mg.pm._api = lambda *a, **k: (order.append("poll"), {"mergeable": True, "mergeable_state": "clean"})[1]
mg.lane("main", "", ["Tataku"], "")
check("the mergeability poll runs before the final evidence read, never after it",
      len(merged) == 2 and order == ["evidence", "poll", "evidence"])
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state="clean"),
              dict(ALLOW, mergeable=None, mergeable_state="unknown")])
mg.lane("main", "", ["Tataku"], "")
check("a final read whose mergeable is null waits for the next run instead of polling past the evidence",
      len(merged) == 2)
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state="clean"),
              dict(ALLOW, mergeable=True, mergeable_state="behind")])
mg.lane("main", "", ["Tataku"], "")
check("a final read that turned behind is not merged", len(merged) == 2)
mg.evaluate = lambda *a, **k: next(reads)
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state="clean"),
              dict(ALLOW, mergeable=True, mergeable_state="blocked")])
mg.lane("main", "", ["Tataku"], "")
check("a final read that turned blocked is not merged on a bypass token (Codex P1 on #41)", len(merged) == 2)
mg._statuses = lambda h: [{"context": "Vercel", "state": "failure"}]
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state="unstable")])
mg.lane("main", "", ["Tataku"], "")
check("an unstable PR with a failed commit status is not merged", len(merged) == 2)
mg._statuses = lambda h: [{"context": "Vercel", "state": "success"}]
reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state="unstable"),
              dict(ALLOW, mergeable=True, mergeable_state="unstable")])
mg.lane("main", "", ["Tataku"], "")
check("an unstable PR whose statuses are all green merges (its check runs are the gate's evidence)", len(merged) == 3)
for state in ("behind", "dirty", "blocked"):
    reads = iter([dict(ALLOW, handoff=True, held=True, mergeable=True, mergeable_state=state)])
    mg.lane("main", "", ["Tataku"], "")
    check(f"the lane never merges a {state} PR on a bypass token", len(merged) == 3)

# workflow shape
wf = (HERE.parent / ".github" / "workflows" / "ci-merge-lane.yml").read_text()
code = re.sub(r"(?m)^\s*#.*$", "", wf)
check("the lane never checks out or runs the PR", "refs/pull" not in code and "github.event.pull_request.head" not in code)
check("the lane's merge token is optional and passed only to the lane step",
      "MERGE_TOKEN: ${{ secrets.INTEGRATION_TOKEN }}" in code and code.count("secrets.INTEGRATION_TOKEN") == 1)
check("the merge token is read only in the default-branch-only environment",
      "environment: merge-lane" in code and "merge_token" not in code)
check("the job has a timeout", code.count("runs-on:") == 1 and "timeout-minutes:" in code)
check("one lane run at a time per repository, never cancelled mid-merge",
      "cancel-in-progress: false" in code)
caller = (HERE.parent / ".github" / "workflows" / "merge-lane.yml").read_text()
check("a dispatch runs only the default branch's caller (it holds INTEGRATION_TOKEN)",
      "if: github.event_name != 'workflow_dispatch' || github.ref_name == github.event.repository.default_branch"
      in caller)
check("the lane and its caller can read commit statuses (private repos 403 without it)",
      "statuses: read" in code and "statuses: read" in caller)

if errors:
    print("FAIL:\n  " + "\n  ".join(errors))
    raise SystemExit(1)
print("merge gate: all checks pass")
