#!/usr/bin/env python3
"""Check a repository's GitHub Actions workflows against the shared CI floor.

Zero-dependency on purpose: it reads only the structural keys it needs, by
indentation, instead of parsing YAML in full. The rules are the ones that cost
runner time or hide a failure when they are missing:

  timeout        every job that runs on a runner sets timeout-minutes
  permissions    every workflow declares top-level permissions
  concurrency    a workflow triggered by pull_request cancels superseded runs
  double-run     a workflow on pull_request does not also run on push to every branch
  shared-ref     every use of the shared layer pins the same ref

Usage:
  python ci/ci_hygiene.py [REPO_ROOT] [--strict] [--json]

Without --strict it reports and exits 0, so a repository can adopt the layer
before it is clean. With --strict any finding exits 1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SHARED_LAYER = re.compile(r"uses:\s*['\"]?([\w.-]+/Dale-OS)/\.github/workflows/[\w.-]+@([\w./-]+)")


def indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def meaningful(lines: list[str]) -> list[tuple[int, str]]:
    out = []
    for n, raw in enumerate(lines, 1):
        stripped = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if stripped.strip():
            out.append((n, stripped))
    return out


def block(rows: list[tuple[int, str]], start: int) -> list[tuple[int, str]]:
    """Rows nested under rows[start], by indentation."""
    base = indent(rows[start][1])
    out = []
    for row in rows[start + 1:]:
        if indent(row[1]) <= base:
            break
        out.append(row)
    return out


def top_level(rows: list[tuple[int, str]]) -> dict[str, int]:
    keys = {}
    for i, (_, line) in enumerate(rows):
        if indent(line) == 0 and ":" in line:
            key = line.split(":", 1)[0].strip().strip("'\"")
            keys[key] = i
    return keys


def triggers(rows, keys) -> dict[str, list[str]]:
    """Map each trigger to the lines under it. Handles `on: x`, `on: [a, b]` and the block form."""
    i = keys.get("on", keys.get("true"))  # YAML 1.1 reads a bare `on` as true; accept both spellings
    if i is None:
        return {}
    inline = rows[i][1].split(":", 1)[1].strip()
    if inline:
        names = [s.strip() for s in inline.strip("[]").split(",") if s.strip()]
        return {name: [] for name in names}
    out: dict[str, list[str]] = {}
    sub = block(rows, i)
    if not sub:
        return out
    level = indent(sub[0][1])
    current = None
    for _, line in sub:
        if indent(line) == level:
            text = line.strip().lstrip("- ").strip()
            current = text.split(":", 1)[0].strip()
            out[current] = []
        elif current:
            out[current].append(line.strip())
    return out


def check_workflow(path: Path, rel: str) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = meaningful(lines)
    keys = top_level(rows)
    findings = []

    def add(rule: str, line: int, message: str) -> None:
        findings.append({"file": rel, "line": line, "rule": rule, "message": message})

    is_reusable_only = set(triggers(rows, keys)) == {"workflow_call"}
    on = triggers(rows, keys)

    if "permissions" not in keys:
        add("permissions", 1, "no top-level permissions; the token gets the repository default")

    if "jobs" in keys:
        jobs = block(rows, keys["jobs"])
        if jobs:
            level = indent(jobs[0][1])
            for j, (n, line) in enumerate(jobs):
                if indent(line) != level or not line.strip().endswith(":"):
                    continue
                name = line.strip()[:-1]
                body = []
                for m, inner in jobs[j + 1:]:
                    if indent(inner) <= level:
                        break
                    body.append(inner.strip())
                runs = any(b.startswith("runs-on:") for b in body)
                if runs and not any(b.startswith("timeout-minutes:") for b in body):
                    add("timeout", n, f"job `{name}` has no timeout-minutes; a hung run bills up to six hours")

    if "pull_request" in on and not is_reusable_only:
        has_concurrency = "concurrency" in keys or any(
            l.strip().startswith("concurrency:") for _, l in rows
        )
        text = "\n".join(l for _, l in rows)
        if not has_concurrency or "cancel-in-progress" not in text:
            add("concurrency", 1, "pull_request workflow without cancel-in-progress; every push to a PR runs to the end")

    if "pull_request" in on and "push" in on:
        push_body = on["push"]
        if not any(b.startswith(("branches", "tags")) for b in push_body):
            add("double-run", rows[keys.get("on", keys.get("true", 0))][0],
                "runs on pull_request and on push to every branch, so each PR commit is tested twice")

    return findings


def check_repo(root: Path) -> list[dict]:
    findings = []
    wf_dir = root / ".github" / "workflows"
    refs: dict[str, list[tuple[str, int]]] = {}
    for path in sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))):
        rel = str(path.relative_to(root))
        findings += check_workflow(path, rel)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = SHARED_LAYER.search(line)
            if m and not m.group(1).endswith("/./"):
                refs.setdefault(m.group(2), []).append((rel, n))
    if len(refs) > 1:
        for ref, places in sorted(refs.items()):
            for rel, n in places:
                findings.append({
                    "file": rel, "line": n, "rule": "shared-ref",
                    "message": f"shared layer pinned at {ref}; this repository uses {len(refs)} different refs",
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    findings = check_repo(Path(args.root).resolve())
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']}: [{f['rule']}] {f['message']}")
        print(f"CI HYGIENE: {len(findings)} finding(s)" + ("" if findings else " - clean"))
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
