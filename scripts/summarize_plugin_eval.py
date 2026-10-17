#!/usr/bin/env python3
"""Write plugin-evals/last-run.json from one `claude plugin eval` aggregate-result.json.

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
    args = ap.parse_args()
    data = json.loads(args.aggregate.read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    main()
