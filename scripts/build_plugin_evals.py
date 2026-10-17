#!/usr/bin/env python3
"""Render evals/activation/corpus.jsonl into `claude plugin eval` cases under plugin-evals/.

One case per corpus row. A positive row checks that its skill fires and that no other Dale OS
skill does; a confuser row checks that the forbidden skill does not fire and that the run
ended in an answer. Each case loads both skill families, as the install lines in INSTALL.md do, so a
skill has to win against all 31. Regenerate after editing the corpus. verify.py rebuilds the cases, CI fails if the tracked copy differs, and validate_repo.py fails if a generated case is not committed.
"""
from __future__ import annotations
import json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evals" / "activation" / "corpus.jsonl"
OUT = ROOT / "plugin-evals" / "activation"


def families():
    return {p.parent.name: p.parent.parent.name for p in ROOT.glob("skills/*/*/SKILL.md")}


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def main():
    fam = families()
    rows = []
    for n, line in enumerate(CORPUS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        skill = row.get("expected_skill") or row.get("forbidden_skill")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(row.get("id", ""))):
            raise SystemExit(f"{CORPUS.relative_to(ROOT)}:{n}: id must be lowercase words joined by hyphens")
        if skill not in fam:
            raise SystemExit(f"{CORPUS.relative_to(ROOT)}:{n}: unknown skill {skill!r}")
        rows.append(row)
    if OUT.exists():
        shutil.rmtree(OUT)
    for row in rows:
        skill = row.get("expected_skill") or row["forbidden_skill"]
        positive = "expected_skill" in row
        case = OUT / row["id"]
        (case / "graders").mkdir(parents=True)
        (case / "prompt.md").write_text(
            "---\n"
            f"description: {yaml_str(('Should fire ' if positive else 'Should not fire ') + skill)}\n"
            "tags: [activation]\n"
            'plugins: ["../../../skills/operator", "../../../skills/financial-truth"]\n'
            "max_turns: 4\n"
            "allowed_tools: [Skill]\n"
            "---\n\n"
            f"{row['prompt']}\n",
            encoding="utf-8",
        )
        bounds = "min: 1\n" if positive else "min: 0\nmax: 0\narm: both\n"
        (case / "graders" / "skill.md").write_text(
            "---\n"
            "type: tool_used\n"
            "tool: Skill\n"
            f"input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?{skill}\"'\n"
            f"{bounds}"
            "---\n",
            encoding="utf-8",
        )
        if positive:
            others = "|".join(sorted(s for s in fam if s != skill))
            (case / "graders" / "no-other-skill.md").write_text(
                "---\n"
                "type: tool_used\n"
                "tool: Skill\n"
                f"input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?(?:{others})\"'\n"
                "min: 0\n"
                "max: 0\n"
                "---\n",
                encoding="utf-8",
            )
        else:
            # A run that died before answering has not shown the skill stays silent.
            (case / "graders" / "answered.md").write_text(
                "---\n"
                "type: regex\n"
                "pattern: '\\S'\n"
                "---\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
