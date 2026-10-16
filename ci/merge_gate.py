#!/usr/bin/env python3
"""The merge gate: may automation merge this PR's exact head on both reviewers' evidence, with no person typing?

Driven by `.github/workflows/ci-merge-lane.yml` (repositories with no merge
controller of their own) and by ACFDashboard's Integration Controller. Zero
dependencies. It never posts a review; it reads the evidence the two reviewers
already left on the head and answers allow / block / wait, failing closed.

Why it exists. Held-scope PRs (workflows, merge tooling, authority sources,
money, schema, access) merged only when the owner typed "merge NNNN" in a chat,
because the merge rode his admin bypass from a Claude session. The owner ruled
on 2026-10-16: "i should NEVER really need to type for you to merge things ...
this needs to be handled via our autonomous flow". So a held PR merges here,
from an Actions job, when both reviewers cleared the exact head:

  1. Agent Review (Claude, from the default branch's agent-review.yml)
     passed on the head; and
  2. the second-vendor PM (Codex on the ChatGPT plan) ruled CLEAR on the head,
     AND that CLEAR still stands when re-derived from Codex's own comments and
     the head's checks at this moment.

Point 2 re-derives the ruling with the PM's own functions (`pm_review.py`), so
the gate and the PM can never disagree about what a Codex finding means. That
also closes the late-finding hole: Codex may post an inline finding after the
CLEAR, which wakes no workflow, and a merge that only read the old CLEAR would
let it through. The PM's `PM REVIEW — CLEAR` comment and `PM Review` check are
not trusted alone: any workflow on a PR branch can post as github-actions.
Codex's comments can only come from Codex's GitHub app.

Held scope never merges on the PM's 2-hour timeout: §4a of the operating manual
keeps "a timeout alone is not enough" for held scope. Non-held PRs that carry a
HANDOFF are blocked by a CORRECT or HOLD, wait for a ruling up to 2 hours, and
need the same passing Agent Review.

  check   one PR (`--pr N [--head SHA] [--held]`): print the verdict as JSON
  scan    every open PR into the base: print {pr: verdict} as JSON
  lane    scan, then merge each PR whose HANDOFF'd head the gate allows
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_review as pm  # noqa: E402  the PM's own reading of Codex's evidence

AGENT_REVIEW = "Agent Review"
# Codex's summary, its review and its inline findings arrive as separate events. A merge reads the evidence twice,
# this many seconds apart, and merges only if the second read still allows the same head.
SETTLE_SECONDS = 90
MERGEABLE_POLLS, MERGEABLE_WAIT = 6, 5
# The only workflow whose Agent Review check counts, and only as defined on the default branch.
AGENT_REVIEW_PATH = ".github/workflows/agent-review.yml"
HOLD_LABELS = ("integration-hold", "do-not-merge", "owner-hold")
PM_TIMEOUT = dt.timedelta(hours=2)


# ---------------------------------------------------------------- pure logic

def handoffs_for(pr_comments, pr_number: int, head: str, allowed) -> list[dict]:
    """HANDOFFs through the claude app, by an allowlisted author, naming this exact head."""
    return [c for c in pr_comments
            if pm.classify(c, pr_number, True, allowed)["review"] and pm.named_head(c.get("body"), head)]


def newest(runs, name: str):
    """The newest run of a check by the github-actions app: started_at, then the monotonic id."""
    best = None
    for r in runs:
        if r.get("name") != name or (r.get("app") or {}).get("slug") != "github-actions":
            continue
        key = (r.get("started_at") or "", r.get("id") or 0)
        if best is None or key > best[0]:
            best = (key, r)
    return best[1] if best else None


def verdict(*, pr: dict, head: str, held: bool, pr_comments, review_comments, check_runs, paths,
            allowed, instruction_paths: str = "", now: dt.datetime | None = None, failed=None,
            identify=None) -> dict:
    """allow: automation may merge this head now. block: a reviewer or a check said no. wait: evidence is not in yet.
    `reasons` says why in words a person can act on. Fails closed: anything unreadable is not an allow.
    `failed` is the PM's list of failed checks on the head; without it every failed run on the head counts.
    `identify` is the PM's check_identity for this repository; an Agent Review counts only when it proves
    the check came from the default branch's agent-review.yml. Without it, no Agent Review counts."""
    now = now or dt.datetime.now(dt.timezone.utc)
    head = str(head or "").lower()
    out = {"pr": pr.get("number"), "head": head, "held": bool(held), "handoff": False,
           "allow": False, "block": False, "pm": None, "reasons": []}

    def done(state: str, why: str) -> dict:
        out["allow"], out["block"] = state == "allow", state == "block"
        out["state"] = state
        out["reasons"].append(why)
        return out

    if pr.get("state") != "open":
        return done("block", "not open")
    if str((pr.get("head") or {}).get("sha") or "").lower() != head:
        return done("block", f"the head moved past {head[:8]}")
    if pr.get("draft"):
        return done("wait", "draft")
    labels = {(lbl.get("name") or "").lower() for lbl in pr.get("labels") or []}
    hold = next((h for h in HOLD_LABELS if h in labels), None)
    if hold:
        return done("block", f"hold label: {hold}")

    handoffs = handoffs_for(pr_comments, pr.get("number"), head, allowed)
    out["handoff"] = bool(handoffs)
    ruled = pm.latest_ruling(pr_comments, head)
    out["pm"] = ruled[1] if ruled else None
    if not handoffs:
        # No second-vendor review was asked for on this head. Held scope cannot merge without one;
        # a non-held PR is outside this gate (its own merge rule applies).
        return done("block" if held else "allow", f"no HANDOFF names {head[:8]}" +
                    ("; held scope needs the PM's CLEAR on its exact head" if held else ""))

    # The PM's own derivation, exactly as its dispatch re-check runs it.
    live = pm.codex_ruling(pm.codex_review_for(pr_comments, head), pm.codex_findings(review_comments, head), head,
                           pm.reviewer_instruction_edits(paths, instruction_paths),
                           pm.failed_checks(check_runs) if failed is None else failed,
                           pm.codex_clean_receipt(pr_comments, head))
    live_v = live.get("verdict")
    if live_v in ("CORRECT", "HOLD"):
        return done("block", f"PM {live_v} on {head[:8]} from Codex's evidence now ({live.get('title')})")
    if out["pm"] in ("CORRECT", "HOLD", "OWNER_GATE"):
        return done("block", f"the PM's standing ruling on {head[:8]} is {out['pm']}")

    if live_v != "CLEAR" or out["pm"] != "CLEAR":
        if held:
            return done("wait", f"waiting on the PM's CLEAR for {head[:8]} (held scope never merges on a timeout)")
        stamps = [t for t in (_ts(c.get("created_at")) for c in handoffs) if t]
        first = min(stamps) if stamps else None
        if first and now - first >= PM_TIMEOUT:
            out["reasons"].append(f"no PM ruling 2 hours after the HANDOFF for {head[:8]}: the review timeout applies")
        else:
            return done("wait", f"waiting on the PM's ruling for {head[:8]} (2-hour timeout from the HANDOFF)")

    # The first reviewer too, and nothing on the head still running, held or not (Codex P1 on #41: a non-held
    # HANDOFF must not merge on the PM alone while Agent Review is missing or running).
    ar = newest(check_runs, AGENT_REVIEW)
    if not ar or ar.get("status") != "completed":
        return done("wait", f"waiting on Agent Review of {head[:8]}")
    ident = identify(ar) if identify else None
    if not ident or ident[1] != AGENT_REVIEW_PATH or ident[2] != "default":
        return done("block", f"the newest Agent Review on {head[:8]} is not proven to come from the default branch's "
                             f"{AGENT_REVIEW_PATH}")
    if ar.get("conclusion") != "success":
        return done("block", f"Agent Review on {head[:8]} is {ar.get('conclusion')}: {(ar.get('output') or {}).get('title') or ''}".rstrip(": "))
    # The PM's own check is left out: its ruling is re-derived above, and its "waiting" check is never completed
    # (the ruling posts a new one), so it would read as running forever (Codex P1 on #41).
    running = sorted({r.get("name") or "?" for r in check_runs
                      if r.get("status") != "completed" and r.get("name") != pm.PM_CHECK})
    if running:
        return done("wait", f"checks still running on {head[:8]}: {', '.join(running)}")
    return done("allow", f"Agent Review passed and the PM's {out['pm'] or 'timeout'} on {head[:8]} still stands")


def _ts(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------- GitHub reads

def _paths(n: int) -> list[str]:
    out = []
    for f in pm._paginate(f"/pulls/{n}/files"):
        out.append(f["filename"])
        if f.get("previous_filename"):
            out.append(f["previous_filename"])
    return out


def _identify(pr: dict):
    """The PM's check_identity for this PR's repository, with one cache for the run records it reads."""
    default_branch = ((pr.get("base") or {}).get("repo") or {}).get("default_branch") or ""
    cache: dict = {}

    def fetch(path):
        if path not in cache:
            cache[path] = pm._api("GET", path)
        return cache[path]

    return lambda r: pm.check_identity(r, default_branch, fetch)


def evaluate(n: int, head: str | None, held_rx: str, held_flag: bool | None, allowed, instruction_paths: str) -> dict:
    pr = pm._api("GET", f"/pulls/{n}")
    head = (head or pr["head"]["sha"]).lower()
    paths = _paths(n)
    held = held_flag if held_flag is not None else bool(pm.held_scope(paths, held_rx))
    return verdict(pr=pr, head=head, held=held, pr_comments=pm._paginate(f"/issues/{n}/comments"),
                   review_comments=pm._paginate(f"/pulls/{n}/comments"),
                   check_runs=pm._paginate(f"/commits/{head}/check-runs?filter=all"),
                   paths=paths, allowed=allowed, instruction_paths=instruction_paths,
                   failed=pm.head_failed_checks(pr, head), identify=_identify(pr)) | {"title": pr.get("title"),
                                                                                      "mergeable": pr.get("mergeable")}


def _open_prs(base: str) -> list[dict]:
    return [p for p in pm._paginate(f"/pulls?state=open&base={base}") if not p.get("draft")]


# ---------------------------------------------------------------- commands

def main(argv=None) -> int:
    env = os.environ
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("check", "scan", "lane"))
    ap.add_argument("--pr", type=int)
    ap.add_argument("--head")
    ap.add_argument("--held", choices=("true", "false"))
    ap.add_argument("--settle", action="store_true", help="on an allow, read again SETTLE_SECONDS later (before a merge)")
    ap.add_argument("--base", default=env.get("BASE_REF", ""))
    a = ap.parse_args(argv)
    allowed = [s.strip() for s in env.get("ALLOWED_AUTHORS", "Tataku").split(",") if s.strip()]
    held_rx, instr = env.get("HELD_PATHS", ""), env.get("INSTRUCTION_PATHS", "")
    held_flag = None if a.held is None else a.held == "true"

    if a.command == "check":
        v = evaluate(a.pr, a.head, held_rx, held_flag, allowed, instr)
        if a.settle and v["allow"]:
            v = settled(a.pr, v, lambda: evaluate(a.pr, v["head"], held_rx, held_flag, allowed, instr))
        print(json.dumps(v))
        if env.get("GITHUB_OUTPUT"):
            pm._outputs(allow=str(v["allow"]).lower(), state=v["state"], reason="; ".join(v["reasons"]))
        return 0

    base = a.base or pm._api("GET", "")["default_branch"]
    if a.command == "scan":
        out = {}
        for p in _open_prs(base):
            try:
                out[str(p["number"])] = evaluate(p["number"], None, held_rx, held_flag, allowed, instr)
            except (urllib.error.URLError, KeyError, ValueError) as e:
                out[str(p["number"])] = {"pr": p["number"], "allow": False, "block": True, "state": "block",
                                         "reasons": [f"gate could not read the PR ({e})"]}
        print(json.dumps(out))
        return 0

    return lane(base, held_rx, allowed, instr)


def lane(base: str, held_rx: str, allowed, instr: str) -> int:
    """Merge every PR into `base` whose HANDOFF'd head the gate allows, lowest number first. A PR with no
    HANDOFF is left to its own repository rule: this lane exists for the reviewed-by-both path only."""
    env = os.environ
    if (env.get("MERGE_LANE") or "on").lower() == "off":
        print("::notice::Merge lane is switched off (repository variable MERGE_LANE=off).")
        return 0
    merge_token = env.get("MERGE_TOKEN") or env["GITHUB_TOKEN"]
    lines, merged = [], 0
    for p in sorted(_open_prs(base), key=lambda x: x["number"]):
        n = p["number"]
        try:
            v = evaluate(n, None, held_rx, None, allowed, instr)
        except (urllib.error.URLError, KeyError, ValueError) as e:
            lines.append(f"#{n}: gate could not read the PR ({e})")
            continue
        if not v["handoff"]:
            continue
        lines.append(f"#{n} {v['head'][:8]} {'held' if v['held'] else 'ordinary'}: {v['state'].upper()} — {'; '.join(v['reasons'])}")
        if not v["allow"]:
            continue
        if v.get("mergeable") is False:
            lines.append(f"#{n}: not merged, GitHub reports it not mergeable")
            continue
        v2 = settled(n, v, lambda: evaluate(n, v["head"], held_rx, None, allowed, instr))
        if not v2["allow"]:
            lines.append(f"#{n}: not merged, the second read {SETTLE_SECONDS}s later says {v2['state'].upper()} — "
                         f"{'; '.join(v2['reasons'])}")
            continue
        # null means GitHub has not finished computing it yet: poll, as its REST docs say (Codex P1 on #41).
        mergeable = mergeable_now(n, v2.get("mergeable"))
        if mergeable is not True:
            lines.append(f"#{n}: not merged, GitHub reports mergeable={mergeable}")
            continue
        msg = (f"Merged by the merge lane (Dale-OS ci/merge_gate.py) on both reviewers' evidence for {v['head']}:\n"
               f"{'; '.join(v['reasons'])}.\nNo person typed this merge (owner ruling 2026-10-16).")
        try:
            _merge(n, v["head"], f"{p['title']} (#{n})", msg, merge_token)
            merged += 1
            lines.append(f"MERGED #{n}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            lines.append(f"#{n}: merge refused ({e.code}: {detail})" + (
                " A PR that changes .github/workflows needs a MERGE_TOKEN with the Workflows permission."
                if "workflow" in detail.lower() else ""))
    report = "\n".join(lines) or "No open PR into the base carries a HANDOFF for its head."
    print(report)
    if env.get("GITHUB_STEP_SUMMARY"):
        with open(env["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(f"## Merge lane: {merged} merged\n\n```text\n{report}\n```\n")
    return 0


def mergeable_now(n: int, mergeable, read=None):
    """GitHub's mergeable for PR n, polled while it is still null (computed asynchronously), MERGEABLE_POLLS times."""
    read = read or (lambda: pm._api("GET", f"/pulls/{n}").get("mergeable"))
    for _ in range(MERGEABLE_POLLS):
        if mergeable is not None:
            break
        time.sleep(MERGEABLE_WAIT)
        try:
            mergeable = read()
        except (urllib.error.URLError, KeyError, ValueError):
            mergeable = None
    return mergeable


def settled(n: int, first: dict, read) -> dict:
    """The gate's answer SETTLE_SECONDS after a first allow, for the same head; anything else is not an allow."""
    time.sleep(SETTLE_SECONDS)
    try:
        again = read()
    except (urllib.error.URLError, KeyError, ValueError) as e:
        return {"allow": False, "state": "block", "reasons": [f"gate could not re-read #{n} ({e})"]}
    if again.get("head") != first.get("head"):
        return dict(again, allow=False, state="block", reasons=[f"the head moved past {first['head'][:8]}"])
    return again


def _merge(n: int, head: str, title: str, message: str, token: str) -> None:
    saved = os.environ["GITHUB_TOKEN"]
    os.environ["GITHUB_TOKEN"] = token
    try:
        # `sha` makes GitHub refuse the merge if anyone pushed after the gate read the head.
        pm._api("PUT", f"/pulls/{n}/merge", {"merge_method": "squash", "sha": head,
                                             "commit_title": title, "commit_message": message})
    finally:
        os.environ["GITHUB_TOKEN"] = saved


if __name__ == "__main__":
    raise SystemExit(main())
