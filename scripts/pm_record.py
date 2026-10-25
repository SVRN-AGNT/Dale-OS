#!/usr/bin/env python3
"""The second-vendor record: every PM ruling that read a Codex review, and what Claude's reviewer had said first.

  collect --org ORG --repo R [--repo R ...] --since ISO --until ISO --out FILE   read-only, through `gh api`
  summary FILE                                                       the numbers docs/HARNESS_MAP.md quotes

`collect` keeps no titles, bodies or commit shas, so a snapshot of a private repository can be published. Only
comments, PR openings and merges inside the window count, so a later collection of the same window gives the same
record unless a comment, title or check run has been edited or deleted since.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime

RULING = re.compile(r"^PM REVIEW — (CLEAR|CORRECT|HOLD|OWNER_GATE)")
CODEX = "Codex (OpenAI, on the ChatGPT plan) completed a code review of"  # a ruling made before Codex finished says
# "had not finished" instead, and is left out: it read no completed second-vendor review
ROUND = re.compile(r"\*\*Codex round (\d+) on this PR\.\*\*")
FINDINGS = re.compile(r"Codex code review of this exact head: (\d+) finding")
PRIORITY = re.compile(r"^- \*\*(P[0-3])\*\*", re.M)
HEAD = re.compile(r"Exact reviewed head:\*\* `([0-9a-f]{40})`")
FAILED = re.compile(r"### Failed checks\n((?:- .*\n?)+)")
CONSUMED = re.compile(r"(?m)^PM-HANDOFF-CONSUMED: (\d+)$")
UNFINISHED = "Codex (OpenAI, on the ChatGPT plan) had not finished its review of"
USAGE_LIMIT = "reached your Codex usage limits"
PM_BOT, CODEX_BOT = "github-actions[bot]", "chatgpt-codex-connector[bot]"


def gh(path: str):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def pages(path: str):
    page = 1
    while True:
        batch = gh(f"{path}&per_page=100&page={page}")
        yield from batch
        if len(batch) < 100:
            return
        page += 1


def when(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def posted_at(org: str, repo: str, comment_id: str) -> str | None:
    """When a comment was posted, or None if it is gone."""
    try:
        return gh(f"repos/{org}/{repo}/issues/comments/{comment_id}")["created_at"]
    except subprocess.CalledProcessError:
        return None


def reviewed_before(org: str, repo: str, head: str, at: str) -> bool:
    """Whether a passing Agent Review on this head had completed by `at`. `filter=all` keeps the runs a re-run
    replaced, which the default (latest only) hides."""
    page = 1
    while True:
        runs = gh(f"repos/{org}/{repo}/commits/{head}/check-runs?check_name=Agent%20Review&filter=all"
                  f"&per_page=100&page={page}")["check_runs"]
        if any(r.get("conclusion") == "success" and r.get("completed_at") and when(r["completed_at"]) <= when(at)
               for r in runs):
            return True
        if len(runs) < 100:
            return False
        page += 1


def collect(org: str, repos: list[str], since: str, until: str) -> tuple[list[dict], list[dict]]:
    """One row per PR with a ruling or a usage-limit message in the window, and the PRs opened in the window whose
    title names a revert (kept as numbers only). A PR's state is kept only as whether it merged by `until`: a merge
    never changes afterwards, while a close can be undone by a reopen."""
    start, end = when(since), when(until)
    rows, reverts = [], []
    for repo in repos:
        # Every PR, oldest-created last: creation order never changes, so a PR updated mid-collection cannot jump
        # past the page being read and be skipped, as it can under `sort=updated`. A PR opened mid-collection
        # pushes the rest down a page, so one may be listed twice.
        seen = set()
        for pr in pages(f"repos/{org}/{repo}/pulls?state=all&sort=created&direction=desc"):
            if when(pr["updated_at"]) < start or pr["number"] in seen:
                continue
            seen.add(pr["number"])
            if start <= when(pr["created_at"]) <= end and "revert" in (pr.get("title") or "").lower():
                reverts.append({"repo": repo, "pr": pr["number"]})
            rulings, limits, unfinished, handoffs = [], 0, [], []
            for c in pages(f"repos/{org}/{repo}/issues/{pr['number']}/comments?since={since}"):
                body, login = c.get("body") or "", c["user"]["login"]
                if not start <= when(c["created_at"]) <= end:
                    continue
                if login == CODEX_BOT and USAGE_LIMIT in body:
                    limits += 1
                if login == PM_BOT and RULING.match(body) and UNFINISHED in body:
                    rnd = ROUND.search(body)
                    unfinished.append(int(rnd.group(1)) if rnd else None)  # its round, which the PM still counts
                if login != PM_BOT or not RULING.match(body) or CODEX not in body:
                    continue
                rnd, found, head, failed = ROUND.search(body), FINDINGS.search(body), HEAD.search(body), FAILED.search(body)
                # The convention is to ask Codex only after Agent Review passes, so the pass is timed against the
                # HANDOFF the ruling answered, not the ruling, which can come after a pass that landed mid-review.
                consumed = CONSUMED.search(body)
                asked = posted_at(org, repo, consumed.group(1)) if consumed else None
                # A re-run that finds blocking evidence posts a second ruling for the same HANDOFF, which replaces
                # the first; the PM counts both as one round. Kept as the HANDOFF's place on the PR, not its id.
                if consumed and consumed.group(1) not in handoffs:
                    handoffs.append(consumed.group(1))
                rulings.append({
                    "at": c["created_at"],
                    "verdict": RULING.match(body).group(1),
                    "round": int(rnd.group(1)) if rnd else None,
                    "findings": int(found.group(1)) if found else 0,
                    "priorities": PRIORITY.findall(body),
                    "failed_checks": len(failed.group(1).strip().splitlines()) if failed else 0,
                    "handoff": handoffs.index(consumed.group(1)) + 1 if consumed else None,
                    "handoff_found": asked is not None,
                    "agent_review_passed_first": bool(head and asked) and reviewed_before(org, repo, head.group(1), asked),
                })
            if rulings or limits or unfinished:
                merged_at = pr.get("merged_at")
                rows.append({"repo": repo, "pr": pr["number"], "merged": bool(merged_at) and when(merged_at) <= end,
                             "rulings": rulings, "usage_limit_messages": limits,
                             "rounds_of_rulings_before_codex_finished": unfinished})
    return rows, reverts


def summary(record: dict) -> dict:
    limits = {"usage_limit_messages": sum(row["usage_limit_messages"] for row in record["rows"]),
              "prs_with_usage_limit_messages": sum(bool(row["usage_limit_messages"]) for row in record["rows"]),
              "revert_prs": len(record["reverts"]),
              "rulings_before_codex_finished": sum(len(row["rounds_of_rulings_before_codex_finished"])
                                                   for row in record["rows"])}
    rows = [row for row in record["rows"] if row["rulings"]]
    rulings = [r for row in rows for r in row["rulings"]]
    if not rulings:
        return {"prs": 0, "rulings": 0, **limits}
    passed = [r for r in rulings if r["agent_review_passed_first"]]
    on_passed = [row for row in rows if any(r["agent_review_passed_first"] and r["findings"] for r in row["rulings"])]
    p1_on_passed = [row for row in rows
                    if any(r["agent_review_passed_first"] and "P1" in r["priorities"] for r in row["rulings"])]
    def first_answer(row):
        """The ruling that stood for the PR's first HANDOFF: its last ruling, since a later one replaces it."""
        answered = [r for r in row["rulings"] if r["handoff"]]
        if not answered:
            return min(row["rulings"], key=lambda r: when(r["at"]))
        first = min(r["handoff"] for r in answered)
        return max((r for r in answered if r["handoff"] == first), key=lambda r: when(r["at"]))

    first = [first_answer(row) for row in rows]
    rounds = [max([r["round"] or 0 for r in row["rulings"]]
                  + [n or 0 for n in row["rounds_of_rulings_before_codex_finished"]]) for row in rows]
    counted = [n for n in rounds if n]
    by_round = collections.defaultdict(lambda: {"rulings": 0, "P1": 0, "P2": 0})
    for r in rulings:
        if r["round"]:
            b = by_round["6+" if r["round"] >= 6 else str(r["round"])]
            b["rulings"] += 1
            b["P1"] += r["priorities"].count("P1")
            b["P2"] += r["priorities"].count("P2")
    return {
        "window": [min((r["at"] for r in rulings), key=when), max((r["at"] for r in rulings), key=when)],
        "prs": len(rows), "rulings": len(rulings),
        "merged": sum(row["merged"] for row in rows),
        "verdicts": dict(collections.Counter(r["verdict"] for r in rulings)),
        "first_ruling_clear": sum(r["verdict"] == "CLEAR" for r in first),
        "correct_from_failed_checks_only": sum(r["verdict"] == "CORRECT" and not r["findings"] for r in rulings),
        "rulings_without_their_handoff": sum(not r["handoff_found"] for r in rulings),
        "rulings_replacing_one_for_the_same_handoff": sum(
            sum(1 for r in row["rulings"] if r["handoff"]) - len({r["handoff"] for r in row["rulings"] if r["handoff"]})
            for row in rows),
        "rulings_after_agent_review_passed": len(passed),
        "findings_after_agent_review_passed": sum(r["findings"] for r in passed),
        "priorities_after_agent_review_passed": dict(collections.Counter(p for r in passed for p in r["priorities"])),
        "prs_with_a_finding_after_agent_review_passed": len(on_passed),
        "prs_with_a_p1_after_agent_review_passed": len(p1_on_passed),
        "prs_with_counted_rounds": len(counted),
        "max_round_distribution": dict(sorted(collections.Counter(counted).items())),
        "prs_past_round_5": sum(n >= 6 for n in counted),
        "median_max_round": statistics.median(counted) if counted else None,
        "by_round": dict(sorted(by_round.items())),
        **limits,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--org", required=True)
    c.add_argument("--repo", action="append", required=True)
    c.add_argument("--since", required=True)
    c.add_argument("--until", required=True)
    c.add_argument("--out", required=True)
    s = sub.add_parser("summary")
    s.add_argument("file")
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        rows, reverts = collect(a.org, a.repo, a.since, a.until)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump({"org": a.org, "repos": a.repo, "since": a.since, "until": a.until, "rows": rows,
                       "reverts": reverts}, f, indent=1)
            f.write("\n")
        return 0
    with open(a.file, encoding="utf-8") as f:
        print(json.dumps(summary(json.load(f)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
