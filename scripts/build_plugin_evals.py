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
FLAGSHIP = ROOT / "evals" / "behavioral" / "flagship.jsonl"
CRITERIA = ROOT / "plugin-evals" / "behavioral-criteria.json"
BEHAVIORAL = ROOT / "plugin-evals" / "behavioral"
PLUGINS = '["../../../skills/operator", "../../../skills/financial-truth"]'


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
            f"plugins: {PLUGINS}\n"
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
    build_behavioral(fam)


def build_behavioral(fam):
    """One two-arm case per flagship row: the same prompt with and without the plugins, judged on criteria."""
    criteria = json.loads(CRITERIA.read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in FLAGSHIP.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = [r["id"] for r in rows]
    if set(ids) != set(criteria):
        raise SystemExit(f"{CRITERIA.relative_to(ROOT)}: criteria must cover exactly the flagship ids; differs on {sorted(set(ids) ^ set(criteria))}")
    if BEHAVIORAL.exists():
        shutil.rmtree(BEHAVIORAL)
    for row in rows:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", row["id"]) or row["skill"] not in fam:
            raise SystemExit(f"{FLAGSHIP.relative_to(ROOT)}: bad id or unknown skill in {row['id']!r}")
        case = BEHAVIORAL / row["id"]
        (case / "graders").mkdir(parents=True)
        (case / "prompt.md").write_text(
            "---\n"
            f"description: {yaml_str('Does ' + row['skill'] + ' change the answer?')}\n"
            "tags: [behavioral]\n"
            f"plugins: {PLUGINS}\n"
            "max_turns: 6\n"
            "allowed_tools: [Skill]\n"
            "---\n\n"
            f"{row['prompt']}\n",
            encoding="utf-8",
        )
        (case / "graders" / "judge.md").write_text(
            f"---\ntype: llm\n---\n\n{criteria[row['id']]}\n", encoding="utf-8"
        )
        # In a two-arm run this is reported as a plugin-fired indicator, not scored.
        (case / "graders" / "skill.md").write_text(
            "---\n"
            "type: tool_used\n"
            "tool: Skill\n"
            f"input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?{row['skill']}\"'\n"
            "---\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
