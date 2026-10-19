#!/usr/bin/env python3
"""Prove the tool invariants are not decorative: each seeded bug must turn the suite red.

Each mutant is one plausible bug in `tools/`, written as an exact text replacement.
The checker copies `tools/` to a temporary directory, applies one mutant, and runs
`test_tool_invariants.py` against the copy. A mutant that survives (the suite still
passes) means an invariant is missing, and this script fails. A mutant whose text
no longer matches the source also fails, so the list cannot rot silently when a
tool is edited.

No dependency on mutmut or similar: the mutants are hand-written from the
financial failure classes the tools exist to catch, which is the point.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUITE = HERE / "test_tool_invariants.py"

# (tool file, exact source text, replacement, the bug it stands for)
MUTANTS = [
    ("basis_proof.py", "lots[key][0]", "lots[key][-1]", "LIFO instead of FIFO"),
    ("basis_proof.py", "verified=needed==0", "verified=True", "an oversold sell reported as verified"),
    ("basis_proof.py", "events.sort(key=lambda x:(x[0],x[1]))", "pass", "events consumed in input order, not date order"),
    ("basis_proof.py", "key=(e[\"ticker\"],e[\"account_id\"])", "key=e[\"ticker\"]", "lots shared across accounts"),
    ("basis_proof.py", "cost=take*lot[\"unit_cost\"]", "cost=e[\"shares\"]*lot[\"unit_cost\"]", "basis charged on the whole sell per lot"),
    ("basis_proof.py", "\"realized_gain\":money(proceeds-basis) if verified else None",
     "\"realized_gain\":money(proceeds-basis)", "a realized gain published for an oversold sell"),
    ("common.py", "if value is None or isinstance(value, bool):", "if value is None:\n        return Decimal('0')\n    if isinstance(value, bool):",
     "a missing number becomes zero"),
    ("money_trail.py", "if classification in EXTERNAL:", "if classification in EXTERNAL | INTERNAL:", "internal transfers counted as external flow"),
    ("money_trail.py", "if abs(a[3]+b[3]) > tol:", "if abs(a[3]-b[3]) > tol:", "transfer legs compared without sign"),
    ("money_trail.py", "if a[1] == b[1]: reasons.append(\"same_account\")", "pass", "a transfer within one account accepted"),
    ("money_trail.py", "if a[2] != b[2]: reasons.append(\"currency_mismatch\")", "pass", "a cross-currency transfer accepted"),
    ("money_trail.py", "if len(legs)!=2: reasons.append(\"pair_must_have_exactly_two_legs\")", "if not legs: pass",
     "an orphan transfer leg accepted"),
    ("money_trail.py", "if classification not in KNOWN:\n            unresolved.append(rid)", "if False:\n            unresolved.append(rid)",
     "an unknown classification treated as known"),
    ("money_trail.py", "or duplicates:", "or False:", "a re-imported movement allowed to PASS"),
    ("ledger_delta.py", "ds=dec(a['shares'])-dec(b['shares'])", "ds=dec(b['shares'])-dec(a['shares'])", "share delta sign inverted"),
    ("ledger_delta.py", "d=ac.get(key,0)-bc.get(key,0)", "d=ac.get(key,0)", "cash delta reported as the after balance"),
    ("ledger_delta.py", "'trades_removed':sorted(bt-at)", "'trades_removed':[]", "removed trades hidden"),
    ("ledger_delta.py", "dec(r.get('shares'),", "dec(r.get('shares',0),", "a missing share count becomes zero"),
    ("ledger_delta.py", "if key in out:", "if False:", "a duplicate position row replaces the first"),
    ("ledger_delta.py", "'cost_basis':None if r.get('cost_basis') is None else dec(", "'cost_basis':dec(0 if r.get('cost_basis') is None else ",
     "a missing cost basis becomes zero"),
]


def run_suite(tools_dir: Path) -> int:
    env = {**os.environ, "TOOLS_DIR": str(tools_dir), "INVARIANT_CASES": os.environ.get("INVARIANT_CASES", "200")}
    return subprocess.run([sys.executable, "-I", str(SUITE)], env=env, capture_output=True, text=True).returncode


def main() -> None:
    problems = []
    if run_suite(ROOT / "tools") != 0:
        raise SystemExit("MUTATION CHECK FAILED: the invariant suite is red on the unmutated tools")
    for tool, old, new, bug in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "tools"
            shutil.copytree(ROOT / "tools", dst, ignore=shutil.ignore_patterns("__pycache__"))
            src = (dst / tool).read_text()
            if src.count(old) != 1:
                problems.append(f"stale mutant ({tool}): {bug}: source text not found exactly once")
                continue
            (dst / tool).write_text(src.replace(old, new))
            if run_suite(dst) == 0:
                problems.append(f"survived ({tool}): {bug}")
    if problems:
        print("MUTATION CHECK FAILED")
        for p in problems:
            print("-", p)
        raise SystemExit(1)
    print(f"MUTATION CHECK PASS: {len(MUTANTS)}/{len(MUTANTS)} seeded bugs caught")


if __name__ == "__main__":
    main()
