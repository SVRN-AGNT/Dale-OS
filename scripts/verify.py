#!/usr/bin/env python3
"""Run the canonical Dale OS verification surface from one command."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PYTHON_STEPS = [
    ("build deterministic skill companions", [sys.executable, "scripts/build_companions.py"]),
    ("build Eve skill adapter", [sys.executable, "adapters/eve/scripts/build_skills.py"]),
    ("build manifest", [sys.executable, "scripts/build_manifest.py"]),
    ("build library catalog", [sys.executable, "scripts/build_catalog.py"]),
    ("build plugin eval cases", [sys.executable, "scripts/build_plugin_evals.py"]),
    ("validate repository", [sys.executable, "scripts/validate_repo.py"]),
    ("validate model eval contracts", [sys.executable, "scripts/validate_eval_contracts.py"]),
    (
        "validate receipt transitions",
        [
            sys.executable,
            "scripts/check_receipt_transition.py",
            "--fixtures",
            "evals/receipts/transition-cases.json",
        ],
    ),
    ("validate agent discovery", [sys.executable, "scripts/validate_discovery.py"]),
    ("validate repository hygiene", [sys.executable, "scripts/validate_hygiene.py"]),
    ("smoke agent control surface", [sys.executable, "scripts/smoke_agent_surface.py"]),
    ("scan public release surface", [sys.executable, "scripts/privacy_scan.py"]),
    ("test shared CI hygiene checker", [sys.executable, "ci/test_ci_hygiene.py"]),
    ("test shared PM review", [sys.executable, "ci/test_pm_review.py"]),
    ("test shared agent review", ["node", "--test", "ci/agent_review/review.test.mjs"]),
    ("check own workflows against the CI floor", [sys.executable, "ci/ci_hygiene.py", ".", "--strict"]),
    ("validate release gate ledger", [sys.executable, "scripts/release_gate.py", "--validate-only"]),
]


def run(label: str, command: list[str], cwd: Path = ROOT) -> None:
    print(f"\n==> {label}")
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-eve",
        action="store_true",
        help="also install the frozen Eve dependency graph and compile the TypeScript adapter",
    )
    args = parser.parse_args()

    for label, command in PYTHON_STEPS:
        run(label, command)

    if args.with_eve:
        eve = ROOT / "adapters" / "eve"
        run("install frozen Eve dependency graph", ["npm", "ci", "--ignore-scripts"], cwd=eve)
        run("compile Eve adapter", ["npm", "run", "build"], cwd=eve)

    print("\nVERIFY PASS")


if __name__ == "__main__":
    main()
