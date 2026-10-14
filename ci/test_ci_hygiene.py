#!/usr/bin/env python3
"""Fixture test for ci/ci_hygiene.py: every rule fires on the bad repo and none on the good one."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ci_hygiene import check_repo  # noqa: E402

HERE = Path(__file__).resolve().parent
bad = {f["rule"] for f in check_repo(HERE / "fixtures" / "bad")}
good = check_repo(HERE / "fixtures" / "good")
expected = {"timeout", "permissions", "concurrency", "double-run", "shared-ref"}
errors = []
if bad != expected:
    errors.append(f"bad fixture: expected rules {sorted(expected)}, got {sorted(bad)}")
if good:
    errors.append(f"good fixture: expected no findings, got {good}")
strict = subprocess.run([sys.executable, str(HERE / "ci_hygiene.py"), str(HERE / "fixtures" / "bad"), "--strict"],
                        capture_output=True, text=True)
if strict.returncode != 1:
    errors.append(f"--strict on the bad fixture exited {strict.returncode}, expected 1")
if errors:
    print("CI HYGIENE TEST FAILED")
    for e in errors:
        print("-", e)
    raise SystemExit(1)
print(f"CI HYGIENE TEST PASS: {len(expected)} rules fire on the bad fixture, none on the good one")
