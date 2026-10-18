#!/usr/bin/env python3
"""Write a pass-count record from one `claude plugin eval` aggregate-result.json.

An activation run writes plugin-evals/last-run.json. A behavioral run (--behavioral, both
arms) writes plugin-evals/last-behavioral-run.json, or the path given by --out, with per-case
counts for each arm and for whether the expected skill fired.

The raw results (prompts, traces, costs) stay local and gitignored. This keeps a small,
reviewable record: the tool version, the date, and pass counts per case.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("aggregate", type=Path, help="aggregate-result.json from claude plugin eval")
    ap.add_argument("--behavioral", action="store_true", help="summarize a two-arm behavioral run")
    ap.add_argument("--out", type=Path, help="behavioral record path (default plugin-evals/last-behavioral-run.json)")
    args = ap.parse_args()
    data = json.loads(args.aggregate.read_text(encoding="utf-8"))
    if args.behavioral:
        return behavioral(data, args.out or ROOT / "plugin-evals" / "last-behavioral-run.json")
    cases, totals = {}, {"activate": [0, 0], "confuse": [0, 0]}
    for case in data["cases"]:
        runs = case["arms"]["with"]
        passed = sum(1 for r in runs if r["passed"])
        errored = sum(1 for r in runs if r.get("error"))
        cases[case["name"]] = {"passed": passed, "runs": len(runs), "errored": errored}
        kind = case["name"].split("-", 1)[0]
        if kind in totals:
            totals[kind][0] += passed
            totals[kind][1] += len(runs)
    out = {
        "schema": "dale-os/plugin-eval-run/v1",
        "claude_code": data.get("claudeVersion"),
        "started_at": data.get("startedAt"),
        "model": "the eval's default child model",
        "families_loaded": ["operator", "financial-truth"],
        "routes_fired": f"{totals['activate'][0]}/{totals['activate'][1]}",
        "confusers_silent": f"{totals['confuse'][0]}/{totals['confuse'][1]}",
        "cases": dict(sorted(cases.items())),
    }
    (ROOT / "plugin-evals" / "last-run.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(out["routes_fired"], "routes fired;", out["confusers_silent"], "confusers silent")


def behavioral(data, path):
    cases, totals = {}, {"with": [0, 0], "without": [0, 0], "fired": [0, 0]}
    for case in data["cases"]:
        arms = case["arms"]
        if "without" not in arms:
            raise SystemExit(f"{case['name']}: no baseline arm; run with --ablation with-without")
        row = {}
        for arm in ("with", "without"):
            runs = arms[arm]
            row[arm] = sum(1 for r in runs if r.get("passed"))
            totals[arm][0] += row[arm]
            totals[arm][1] += len(runs)
        fired = sum(1 for r in arms["with"] if any(g["name"] == "skill" and g["passed"] for g in r.get("graders", [])))
        totals["fired"][0] += fired
        totals["fired"][1] += len(arms["with"])
        row.update(fired=fired, runs=len(arms["with"]))
        cases[case["name"]] = row
    out = {
        "schema": "dale-os/plugin-eval-behavioral-run/v1",
        "claude_code": data.get("claudeVersion"),
        "started_at": data.get("startedAt"),
        "model": "the eval's default child model",
        "judge": "the eval's default judge model, 3 votes per run",
        "families_loaded": ["operator", "financial-truth"],
        "with_plugins_passed": "{}/{}".format(*totals["with"]),
        "without_plugins_passed": "{}/{}".format(*totals["without"]),
        "expected_skill_fired": "{}/{}".format(*totals["fired"]),
        "cases": dict(sorted(cases.items())),
    }
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(out["with_plugins_passed"], "with;", out["without_plugins_passed"], "without;",
          out["expected_skill_fired"], "fired")


if __name__ == "__main__":
    main()
