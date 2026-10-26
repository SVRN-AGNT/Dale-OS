#!/usr/bin/env python3
"""Tests for ci/openweight_review.py: the open-weight PM reads only the checkout, and anything short of one JSON
ruling is "no ruling", never a CLEAR."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import openweight_review as ow  # noqa: E402
import pm_review as pm  # noqa: E402

errors: list[str] = []


def check(name: str, ok: bool) -> None:
    if not ok:
        errors.append(name)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


# A caller checkout: base has a.py; the PR head changes it; prepare's files sit in .pm-review/.
tmp = Path(tempfile.mkdtemp())
outside = tmp / "secret.txt"
outside.write_text("TOKEN=abc")
root = tmp / "caller"
root.mkdir()
git(root, "init", "-q", "-b", "main")
git(root, "config", "user.email", "t@example.com")
git(root, "config", "user.name", "t")
(root / "a.py").write_text("def total(xs):\n    return sum(xs)\n")
git(root, "add", ".")
git(root, "commit", "-q", "-m", "base")
BASE = git(root, "rev-parse", "HEAD")
(root / "a.py").write_text("def total(xs):\n    return sum(xs) + 1\n")
git(root, "commit", "-q", "-am", "head")
HEAD = git(root, "rev-parse", "HEAD")
git(root, "checkout", "-q", BASE)
(root / ".pm-review").mkdir()
(root / ".pm-review" / "pr.diff").write_text("-    return sum(xs)\n+    return sum(xs) + 1\n")
(root / "link").symlink_to(outside)

t = ow.Tools(root, HEAD, BASE)
check("reads a file with line numbers", t.call("read_file", {"path": "a.py"}).startswith("1\tdef total"))
check("reads prepare's files", "+ 1" in t.call("read_file", {"path": ".pm-review/pr.diff"}))
check("a path outside the checkout is refused", t.call("read_file", {"path": "../secret.txt"}).startswith("error:"))
check("an absolute path stays inside the checkout", t.call("read_file", {"path": str(outside)}).startswith("error:"))
check("a symlink out of the checkout is refused", t.call("read_file", {"path": "link"}).startswith("error:"))
check(".git is not readable", t.call("read_file", {"path": ".git/config"}).startswith("error:"))
check("list_dir hides .git", ".git" not in t.call("list_dir", {"path": "."}))
check("git_show reads the PR head", "sum(xs) + 1" in t.call("git_show", {"path": "a.py"}))
check("git_show reads the merge base", "+ 1" not in t.call("git_show", {"path": "a.py", "rev": "base"}))
check("git_show takes no other revision", t.call("git_show", {"path": "a.py", "rev": "HEAD~1"}).startswith("error:"))
check("git_show refuses an option for a path", t.call("git_show", {"path": "--output=x"}).startswith("error:"))
check("git_grep searches the head", "a.py:2:" in t.call("git_grep", {"pattern": r"sum\(xs\) \+ 1"}))
check("git_grep treats a dash pattern as a pattern", not t.call("git_grep", {"pattern": "--open-files-in-pager=sh"}).startswith("error:")
      and not (root / "x").exists())
check("search finds base-tree lines", "a.py:2:" in t.call("search", {"pattern": "sum", "path": "."}))
check("an unknown tool is an error, not a crash", t.call("rm", {}).startswith("error:"))
check("bad arguments are an error, not a crash", t.call("read_file", {"nope": 1}).startswith("error:"))
big = root / "big.txt"
big.write_text("x" * (ow.TOOL_CHARS + 50))
check("long output is cut and says so", "cut at" in t.call("read_file", {"path": "big.txt"}))

GOOD = {"verdict": "CLEAR", "summary": "Adds one.", "verified": ["a.py:2 adds 1 to the total"], "blocking": [],
        "required_actions": [], "owner_question": ""}
SCHEMA = pm.PM_SCHEMA


def scripted(*replies):
    """A fake endpoint: each reply is a message dict, or an exception to raise. Records what it was sent."""
    sent, queue = [], list(replies)

    def post(base_url, key, body):
        sent.append(body)
        r = queue.pop(0)
        if isinstance(r, Exception):
            raise r
        return {"choices": [{"message": r}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
    return post, sent


def call(name, args, cid="c1"):
    return {"role": "assistant", "content": "", "tool_calls": [
        {"id": cid, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]}


def http(code):
    return urllib.error.HTTPError("u", code, "x", {}, None)


def client(post, models=("m1", "m2")):
    return ow.Client("https://example.invalid/v1", "KEY", list(models), post=post, sleep=lambda s: None)


post, sent = scripted(call("read_file", {"path": ".pm-review/pr.diff"}), {"role": "assistant", "content": json.dumps(GOOD)})
c = client(post)
final = ow.review(c, t, "prompt", SCHEMA)
check("a tool round then a JSON answer is the final message", json.loads(final) == GOOD)
check("the tool result went back to the model", any(m.get("role") == "tool" and "+ 1" in m["content"] for m in sent[1]["messages"]))
check("the PM's interpret reads it as a CLEAR", pm.interpret(final, HEAD)["verdict"] == "CLEAR")
check("the key never enters the conversation", "KEY" not in json.dumps(sent))
check("usage is counted", c.usage == {"prompt_tokens": 20, "completion_tokens": 10})

post, _ = scripted({"role": "assistant", "content": "```json\n" + json.dumps(GOOD) + "\n```"})
check("one json fence is tolerated", json.loads(ow.review(client(post), t, "p", SCHEMA)) == GOOD)

post, sent = scripted({"role": "assistant", "content": "Looks fine to me!"}, {"role": "assistant", "content": json.dumps(GOOD)})
check("prose instead of a ruling: the ruling is demanded with the schema", json.loads(ow.review(client(post), t, "p", SCHEMA)) == GOOD
      and sent[1]["response_format"]["type"] == "json_schema")

post, sent = scripted({"role": "assistant", "content": "ok"}, http(400), {"role": "assistant", "content": json.dumps(GOOD)})
check("a host without json_schema is asked for json_object", json.loads(ow.review(client(post), t, "p", SCHEMA)) == GOOD
      and sent[2]["response_format"] == {"type": "json_object"})

post, _ = scripted({"role": "assistant", "content": "ok"}, {"role": "assistant", "content": "still prose"},
                   {"role": "assistant", "content": "[1]"}, {"role": "assistant", "content": "no"})
check("no ruling in shape is an empty final message (no ruling, never a CLEAR)", ow.review(client(post), t, "p", SCHEMA) == "")
check("an empty final message is not a CLEAR to the PM", pm.interpret("", HEAD)["ruled"] is False)

post, sent = scripted(http(503), http(503), http(503), {"role": "assistant", "content": json.dumps(GOOD)})
c = client(post)
check("a model that keeps failing hands over to the next", json.loads(ow.review(c, t, "p", SCHEMA)) == GOOD
      and [b["model"] for b in sent] == ["m1", "m1", "m1", "m2"] and c.used == "m2")

post, sent = scripted(http(404), {"role": "assistant", "content": json.dumps(GOOD)})
c = client(post)
ow.review(c, t, "p", SCHEMA)
check("a model the host does not serve is skipped at once", [b["model"] for b in sent] == ["m1", "m2"])

post, sent = scripted(call("list_dir", {"path": "."}), http(503), http(503), http(503))
c = client(post)
try:
    ow.review(c, t, "p", SCHEMA)
    check("a review never switches model mid-way", False)
except ow.Budget:
    check("a review never switches model mid-way", all(b["model"] == "m1" for b in sent))

post, _ = scripted(*[http(500)] * 6)
try:
    ow.review(client(post), t, "p", SCHEMA)
    check("every model failing raises Budget", False)
except ow.Budget as e:
    check("the failure names no key", "KEY" not in str(e))

post, sent = scripted(*[call("list_dir", {"path": "."}, f"c{i}") for i in range(3)], {"role": "assistant", "content": json.dumps(GOOD)})
check("at the turn cap the ruling is demanded", json.loads(ow.review(client(post), t, "p", SCHEMA, max_turns=3)) == GOOD
      and "response_format" in sent[-1] and "tools" not in sent[-1])

post, sent = scripted(call("read_file", {"path": "big.txt"}), {"role": "assistant", "content": json.dumps(GOOD)})
check("past the context budget the ruling is demanded", json.loads(ow.review(client(post), t, "p", SCHEMA, max_chars=100)) == GOOD
      and "tools" not in sent[-1])

post, _ = scripted({"role": "assistant", "content": "", "tool_calls": [
    {"id": "x", "type": "function", "function": {"name": "read_file", "arguments": "not json"}}]},
    {"role": "assistant", "content": json.dumps(GOOD)})
check("malformed tool arguments are reported to the model, not a crash", json.loads(ow.review(client(post), t, "p", SCHEMA)) == GOOD)

check("only_json refuses an array", ow.only_json("[1,2]") == "")
check("only_json refuses trailing prose", ow.only_json(json.dumps(GOOD) + " thanks") == "")

if errors:
    print("OPENWEIGHT REVIEW TEST FAILED")
    for e in errors:
        print("-", e)
    raise SystemExit(1)
print("OPENWEIGHT REVIEW TEST PASS")
