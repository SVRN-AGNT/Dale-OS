#!/usr/bin/env python3
"""The second-vendor record: every PM ruling that read a Codex review, and what Claude's reviewer had said first.

  collect --org ORG --repo R [--repo R ...] --since ISO --out FILE   read-only, through `gh api`
  summary FILE                                                       the numbers docs/HARNESS_MAP.md quotes

`collect` keeps no titles, bodies or commit shas, so a snapshot of a private repository can be published.
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
CODEX = "Codex (OpenAI, on the ChatGPT plan)"  # every ruling that read Codex's review names it
ROUND = re.compile(r"\*\*Codex round (\d+) on this PR\.\*\*")
FINDINGS = re.compile(r"Codex code review of this exact head: (\d+) finding")
PRIORITY = re.compile(r"^- \*\*(P[0-3])\*\*", re.M)
HEAD = re.compile(r"Exact reviewed head:\*\* `([0-9a-f]{40})`")
FAILED = re.compile(r"### Failed checks\n((?:- .*\n?)+)")
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


def reviewed_before(org: str, repo: str, head: str, at: str) -> bool:
    """Whether a passing Agent Review on this head had completed before the PM ruled on it."""
    runs = gh(f"repos/{org}/{repo}/commits/{head}/check-runs?check_name=Agent%20Review&per_page=100")["check_runs"]
    return any(r.get("conclusion") == "success" and r.get("completed_at") and when(r["completed_at"]) <= when(at)
               for r in runs)


def collect(org: str, repos: list[str], since: str) -> list[dict]:
    rows = []
    for repo in repos:
        for pr in pages(f"repos/{org}/{repo}/pulls?state=all&sort=updated&direction=desc"):
            if pr["updated_at"] < since:
                break
            rulings, limits = [], 0
            for c in pages(f"repos/{org}/{repo}/issues/{pr['number']}/comments?since={since}"):
                body, login = c.get("body") or "", c["user"]["login"]
                if c["created_at"] < since:
                    continue
                if login == CODEX_BOT and USAGE_LIMIT in body:
                    limits += 1
                if login != PM_BOT or not RULING.match(body) or CODEX not in body:
                    continue
                rnd, found, head, failed = ROUND.search(body), FINDINGS.search(body), HEAD.search(body), FAILED.search(body)
                rulings.append({
                    "at": c["created_at"],
                    "verdict": RULING.match(body).group(1),
                    "round": int(rnd.group(1)) if rnd else None,
                    "findings": int(found.group(1)) if found else 0,
                    "priorities": PRIORITY.findall(body),
                    "failed_checks": len(failed.group(1).strip().splitlines()) if failed else 0,
                    "agent_review_passed_first": bool(head) and reviewed_before(org, repo, head.group(1), c["created_at"]),
                })
            if rulings:
                rows.append({"repo": repo, "pr": pr["number"], "merged": bool(pr.get("merged_at")),
                             "open": pr["state"] == "open", "rulings": rulings, "usage_limit_messages": limits})
    return rows


def summary(rows: list[dict]) -> dict:
    rulings = [r for row in rows for r in row["rulings"]]
    if not rulings:
        return {"prs": 0, "rulings": 0}
    passed = [r for r in rulings if r["agent_review_passed_first"]]
    on_passed = [row for row in rows if any(r["agent_review_passed_first"] and r["findings"] for r in row["rulings"])]
    p1_on_passed = [row for row in rows
                    if any(r["agent_review_passed_first"] and "P1" in r["priorities"] for r in row["rulings"])]
    first = [min(row["rulings"], key=lambda r: r["at"]) for row in rows]
    rounds = [max(r["round"] or 0 for r in row["rulings"]) for row in rows]
    counted = [n for n in rounds if n]
    by_round = collections.defaultdict(lambda: {"rulings": 0, "P1": 0, "P2": 0})
    for r in rulings:
        if r["round"]:
            b = by_round["6+" if r["round"] >= 6 else str(r["round"])]
            b["rulings"] += 1
            b["P1"] += r["priorities"].count("P1")
            b["P2"] += r["priorities"].count("P2")
    return {
        "window": [min(r["at"] for r in rulings), max(r["at"] for r in rulings)],
        "prs": len(rows), "rulings": len(rulings),
        "merged": sum(row["merged"] for row in rows), "open": sum(row["open"] for row in rows),
        "verdicts": dict(collections.Counter(r["verdict"] for r in rulings)),
        "first_ruling_clear": sum(r["verdict"] == "CLEAR" for r in first),
        "correct_from_failed_checks_only": sum(r["verdict"] == "CORRECT" and not r["findings"] for r in rulings),
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
        "usage_limit_messages": sum(row["usage_limit_messages"] for row in rows),
        "prs_with_usage_limit_messages": sum(bool(row["usage_limit_messages"]) for row in rows),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--org", required=True)
    c.add_argument("--repo", action="append", required=True)
    c.add_argument("--since", required=True)
    c.add_argument("--out", required=True)
    s = sub.add_parser("summary")
    s.add_argument("file")
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        rows = collect(a.org, a.repo, a.since)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump({"org": a.org, "since": a.since, "rows": rows}, f, indent=1)
            f.write("\n")
        return 0
    with open(a.file, encoding="utf-8") as f:
        print(json.dumps(summary(json.load(f)["rows"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
