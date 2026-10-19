#!/usr/bin/env python3
"""Hand-written invariants for the read-only financial tools, checked on generated events.

Why hand-written and why mutation-checked: an agent that writes both a tool and its
property tests tends to restate the implementation, so the tests pass whatever the
code does. Each invariant here is stated from the domain (FIFO conservation, transfer
neutrality, missing is never zero), not from the code, and `mutation_check.py` proves
the suite is not decorative: every listed bug, seeded into a copy of `tools/`, must
turn at least one invariant red.

Zero dependencies: a seeded `random.Random` generates the cases, so a failure
reproduces from its seed. `TOOLS_DIR` points the suite at another copy of `tools/`.
"""
from __future__ import annotations

import copy
import importlib
import os
import random
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(os.environ.get("TOOLS_DIR") or ROOT / "tools")
sys.path.insert(0, str(TOOLS))
basis_proof = importlib.import_module("basis_proof")
money_trail = importlib.import_module("money_trail")
ledger_delta = importlib.import_module("ledger_delta")

CASES = int(os.environ.get("INVARIANT_CASES", "200"))
CENT = Decimal("0.01")
errors: list[str] = []


def check(name: str, ok: bool, seed: int | None = None) -> None:
    if not ok:
        errors.append(f"{name}" + (f" (seed {seed})" if seed is not None else ""))


def d(x) -> Decimal:
    return Decimal(str(x))


# --- generators -------------------------------------------------------------

def gen_basis_events(rng: random.Random) -> list[dict]:
    """BUY/SELL events across two tickers and two accounts, on distinct-or-shared days."""
    events = []
    for i in range(rng.randint(1, 12)):
        events.append({
            "id": f"e{i}",
            "date": f"2026-01-{rng.randint(1, 28):02d}",
            "type": rng.choice(["BUY", "BUY", "SELL"]),
            "ticker": rng.choice(["AAA", "BBB"]),
            "account_id": rng.choice(["acct1", "acct2"]),
            "shares": rng.choice([1, 2, 3, 5, 10, 0.5, 2.25]),
            "price": rng.choice([0, 1, 9.99, 10, 25.5, 100]),
        })
    return events


def gen_movements(rng: random.Random) -> list[dict]:
    """External flows and fees with unique ids and source refs (no accidental duplicates)."""
    rows = []
    for i in range(rng.randint(0, 8)):
        cls = rng.choice(["contribution", "withdrawal", "fee", "income", "trade_settlement"])
        amt = d(rng.randint(1, 50000)) / 100
        if cls in ("withdrawal", "fee"):
            amt = -amt
        rows.append({"id": f"m{i}", "account_id": rng.choice(["a", "b"]), "date": f"2026-02-{rng.randint(1, 28):02d}",
                     "amount": str(amt), "classification": cls, "source_ref": f"ref{i}"})
    return rows


def transfer_pair(rng: random.Random, tag: str) -> list[dict]:
    amt = d(rng.randint(1, 50000)) / 100
    day = f"2026-02-{rng.randint(1, 28):02d}"
    return [
        {"id": f"{tag}-out", "account_id": "a", "date": day, "amount": str(-amt), "classification": "internal_transfer",
         "pair_id": tag, "source_ref": f"{tag}-1"},
        {"id": f"{tag}-in", "account_id": "b", "date": day, "amount": str(amt), "classification": "internal_transfer",
         "pair_id": tag, "source_ref": f"{tag}-2"},
    ]


# --- basis_proof: FIFO ------------------------------------------------------

def held_and_sold(events: list[dict]) -> dict:
    """Per (ticker, account): shares bought, shares sold. The oracle, independent of the lot engine."""
    out: dict = {}
    for e in events:
        k = (e["ticker"], e["account_id"])
        b, s = out.get(k, (Decimal(0), Decimal(0)))
        out[k] = (b + d(e["shares"]), s) if e["type"] == "BUY" else (b, s + d(e["shares"]))
    return out


def basis_invariants(seed: int) -> None:
    rng = random.Random(seed)
    events = gen_basis_events(rng)
    r = basis_proof.analyze({"events": events})
    disposals = r["disposals"]
    check("basis: every sell yields one disposal", len(disposals) == sum(e["type"] == "SELL" for e in events), seed)
    for x in disposals:
        sold, sup, uns = d(x["shares_sold"]), d(x["shares_supported"]), d(x["shares_unsupported"])
        check("basis: supported + unsupported = sold", sup + uns == sold, seed)
        check("basis: proven basis is never negative", d(x["proven_basis"]) >= 0, seed)
        check("basis: consumed lots add up to the supported shares",
              sum(d(c["shares"]) for c in x["lots_consumed"]) == sup, seed)
        if uns == 0:
            check("basis: a fully supported sell is VERIFIED", x["status"] == "VERIFIED", seed)
            check("basis: realized gain = proceeds - basis",
                  x["realized_gain"] is not None and abs(d(x["realized_gain"]) - (d(x["proceeds"]) - d(x["proven_basis"]))) <= CENT, seed)
        else:
            check("basis: an oversold sell never reports a realized gain",
                  x["status"] != "VERIFIED" and x["realized_gain"] is None, seed)
    check("basis: any unverified disposal keeps the run from PASS",
          r["status"] != "PASS" or all(x["status"] == "VERIFIED" for x in disposals), seed)
    # Conservation: shares supported per position never exceed shares bought.
    totals = held_and_sold(events)
    for k, (bought, _sold) in totals.items():
        sup = sum(d(x["shares_supported"]) for x in disposals if (x["ticker"], x["account_id"]) == k)
        check("basis: no position sells more supported shares than it bought", sup <= bought, seed)
    # Positions are independent: each (ticker, account) analysed alone gives the same disposals.
    for k in totals:
        alone = basis_proof.analyze({"events": [e for e in events if (e["ticker"], e["account_id"]) == k]})["disposals"]
        together = [x for x in disposals if (x["ticker"], x["account_id"]) == k]
        check("basis: positions do not leak into each other", alone == together, seed)
    # Lots are consumed in date order, whatever order the events arrive in.
    by_date = sorted(events, key=lambda e: e["date"])  # stable: same-day order is kept
    check("basis: input order across days does not change any disposal",
          basis_proof.analyze({"events": by_date})["disposals"] == disposals, seed)
    # Splitting a buy into two halves at the same price leaves every sell's basis unchanged.
    buys = [i for i, e in enumerate(events) if e["type"] == "BUY"]
    if buys:
        i = rng.choice(buys)
        half = d(events[i]["shares"]) / 2
        split = copy.deepcopy(events)
        split[i] = {**events[i], "shares": str(half)}
        split.insert(i + 1, {**events[i], "id": events[i]["id"] + "b", "shares": str(half)})
        a = [(x["event_id"], x["proven_basis"], x["shares_supported"]) for x in disposals]
        b = [(x["event_id"], x["proven_basis"], x["shares_supported"]) for x in basis_proof.analyze({"events": split})["disposals"]]
        check("basis: splitting a lot does not change any sell's basis", a == b, seed)


def basis_fixed_cases() -> None:
    r = basis_proof.analyze({"events": [
        {"id": "b1", "date": "2026-01-01", "type": "BUY", "ticker": "X", "account_id": "a", "shares": 10, "price": 10},
        {"id": "b2", "date": "2026-01-02", "type": "BUY", "ticker": "X", "account_id": "a", "shares": 10, "price": 20},
        {"id": "s1", "date": "2026-01-03", "type": "SELL", "ticker": "X", "account_id": "a", "shares": 15, "price": 30},
    ]})
    x = r["disposals"][0]
    check("basis: FIFO consumes the oldest lot first (10@10 + 5@20 = 200)", x["proven_basis"] == 200.0)
    check("basis: FIFO realized gain is 450 - 200", x["realized_gain"] == 250.0)
    r = basis_proof.analyze({"events": [
        {"id": "s1", "date": "2026-01-01", "type": "SELL", "ticker": "X", "account_id": "a", "shares": 1, "price": 5},
        {"id": "b1", "date": "2026-01-02", "type": "BUY", "ticker": "X", "account_id": "a", "shares": 1, "price": 1},
    ]})
    check("basis: a buy dated after the sell cannot support it", r["disposals"][0]["status"] == "UNVERIFIED_OVERSOLD")
    for bad in ({"shares": None}, {"price": None}, {"date": None}):
        ev = {"id": "b", "date": "2026-01-01", "type": "BUY", "ticker": "X", "account_id": "a", "shares": 1, "price": 1, **bad}
        check(f"basis: a missing {list(bad)[0]} blocks, never becomes zero", basis_proof.analyze({"events": [ev]})["status"] == "BLOCKED")


# --- money_trail: transfer neutrality -----------------------------------------

def external_total(rows: list[dict]) -> Decimal:
    return sum((d(r["amount"]) for r in rows if r["classification"] in ("contribution", "withdrawal")), Decimal(0))


def money_invariants(seed: int) -> None:
    rng = random.Random(seed)
    rows = gen_movements(rng)
    base = money_trail.analyze({"movements": rows})
    check("money: external flow total = sum of contributions and withdrawals",
          d(base["external_flow_total"]) == external_total(rows).quantize(CENT), seed)
    check("money: clean classified flows PASS", base["status"] == "PASS", seed)
    with_pair = rows + transfer_pair(rng, "t1")
    rng.shuffle(with_pair)
    r = money_trail.analyze({"movements": with_pair})
    check("money: a balanced internal transfer never changes the external flow total",
          r["external_flow_total"] == base["external_flow_total"], seed)
    check("money: a balanced internal transfer between two accounts PASSES", r["status"] == "PASS", seed)
    # Breaking any one property of the pair must stop it passing.
    broken = copy.deepcopy(transfer_pair(rng, "t2"))
    how = rng.choice(["amount", "account", "currency", "orphan", "class"])
    if how == "amount":
        broken[1]["amount"] = str(d(broken[1]["amount"]) + Decimal("0.02"))
    elif how == "account":
        broken[1]["account_id"] = broken[0]["account_id"]
    elif how == "currency":
        broken[1]["currency"] = "EUR"
    elif how == "orphan":
        broken = broken[:1]
    else:
        broken[1]["classification"] = "contribution"
    r = money_trail.analyze({"movements": rows + broken})
    check(f"money: a transfer pair with a broken {how} does not PASS", r["status"] != "PASS", seed)
    if how != "class":
        check(f"money: an internal-transfer leg is never external flow, even with a broken {how}",
              r["external_flow_total"] == base["external_flow_total"], seed)
    # An unknown classification is never counted and never PASSES.
    unk = rows + [{"id": "u", "account_id": "a", "date": "2026-02-01", "amount": "5", "classification": "mystery", "source_ref": "u"}]
    r = money_trail.analyze({"movements": unk})
    check("money: an unknown classification never PASSES", r["status"] != "PASS" and "u" in r["unresolved_ids"], seed)
    check("money: an unknown classification adds nothing to external flows",
          r["external_flow_total"] == base["external_flow_total"], seed)
    # The same movement imported twice is a duplicate candidate.
    if rows:
        dup = {**rng.choice(rows)}
        dup["id"] = "dup"
        r = money_trail.analyze({"movements": rows + [dup]})
        check("money: a re-imported movement is flagged and does not PASS", r["duplicate_candidates"] and r["status"] != "PASS", seed)


def money_fixed_cases() -> None:
    for bad in ({"amount": None}, {"amount": ""}, {"date": "02/01/2026"}):
        row = {"id": "m", "account_id": "a", "date": "2026-02-01", "amount": "10", "classification": "contribution", **bad}
        check(f"money: an invalid {list(bad)[0]} blocks, never becomes zero", money_trail.analyze({"movements": [row]})["status"] == "BLOCKED")
    r = money_trail.analyze({"movements": [{"id": "x", "amount": "1", "date": "2026-02-01", "classification": "fee"},
                                           {"id": "x", "amount": "1", "date": "2026-02-02", "classification": "fee"}]})
    check("money: a duplicate id blocks", r["status"] == "BLOCKED")


# --- ledger_delta: preview symmetry ---------------------------------------------

def gen_snapshot(rng: random.Random) -> dict:
    keys = rng.sample([("a", "X"), ("a", "Y"), ("b", "X"), ("b", "Z")], rng.randint(0, 4))
    return {
        "positions": [{"account_id": a, "ticker": t, "shares": rng.randint(0, 50), "cost_basis": str(d(rng.randint(0, 99999)) / 100)}
                      for a, t in keys],
        "cash_by_account": {a: str(d(rng.randint(-5000, 99999)) / 100) for a in rng.sample(["a", "b"], rng.randint(0, 2))},
        "trades": [{"id": f"t{i}"} for i in rng.sample(range(6), rng.randint(0, 6))],
    }


def ledger_invariants(seed: int) -> None:
    rng = random.Random(seed)
    before, after = gen_snapshot(rng), gen_snapshot(rng)
    fwd = ledger_delta.analyze({"before": before, "after": after})
    rev = ledger_delta.analyze({"before": after, "after": before})
    same = ledger_delta.analyze({"before": before, "after": copy.deepcopy(before)})
    check("ledger: a snapshot against itself has no deltas",
          not same["position_deltas"] and not same["cash_deltas"] and not same["trades_added"] and not same["trades_removed"], seed)
    neg = lambda rows, f: sorted((x.get("key") or x.get("account_id"), -x[f]) for x in rows)
    check("ledger: reversing before/after negates share deltas",
          neg(fwd["position_deltas"], "shares_delta") == sorted((x["key"], x["shares_delta"]) for x in rev["position_deltas"]), seed)
    check("ledger: reversing before/after negates cash deltas",
          neg(fwd["cash_deltas"], "cash_delta") == sorted((x["account_id"], x["cash_delta"]) for x in rev["cash_deltas"]), seed)
    check("ledger: trades added one way are removed the other", fwd["trades_added"] == rev["trades_removed"], seed)
    # Each delta is after minus before, computed here from the raw snapshots.
    pos = lambda s: {f"{p['account_id']}::{p['ticker']}": d(p["shares"]) for p in s["positions"]}
    pb, pa = pos(before), pos(after)
    want = sorted((k, float(pa.get(k, 0) - pb.get(k, 0))) for k in set(pb) | set(pa) if pa.get(k, 0) != pb.get(k, 0))
    got = sorted((x["key"], x["shares_delta"]) for x in fwd["position_deltas"] if x["shares_delta"])
    check("ledger: each share delta is after minus before", got == want, seed)
    cb = lambda s: {f"{p['account_id']}::{p['ticker']}": d(p["cost_basis"]) for p in s["positions"]}
    cbb, cba = cb(before), cb(after)
    want_cb = {k: float((cba.get(k, Decimal(0)) - cbb.get(k, Decimal(0))).quantize(CENT)) for k in set(cbb) | set(cba)}
    check("ledger: each cost-basis delta is after minus before",
          all(x["cost_basis_delta"] == want_cb[x["key"]] for x in fwd["position_deltas"]), seed)
    # Cash deltas sum to the change in total cash.
    tot = lambda s: sum((d(v) for v in s["cash_by_account"].values()), Decimal(0))
    check("ledger: cash deltas sum to the change in total cash",
          sum((d(x["cash_delta"]) for x in fwd["cash_deltas"]), Decimal(0)) == (tot(after) - tot(before)).quantize(CENT), seed)


def ledger_fixed_cases() -> None:
    pos = {"account_id": "a", "ticker": "X", "shares": 10, "cost_basis": 100}
    no = lambda field: {"positions": [{k: v for k, v in pos.items() if k != field}]}
    r = ledger_delta.analyze({"before": {"positions": [pos]}, "after": no("shares")})
    check("ledger: a missing share count blocks, never becomes zero", r["status"] == "BLOCKED")
    r = ledger_delta.analyze({"before": {"positions": [pos]}, "after": no("cost_basis")})
    check("ledger: a missing cost basis gives an unknown delta, never a zero-based one",
          r["status"] == "UNRESOLVED" and r["position_deltas"] == [{"key": "a::X", "shares_delta": 0.0, "cost_basis_delta": None}])
    r = ledger_delta.analyze({"before": {"positions": [pos, {**pos, "shares": 5}]}, "after": {"positions": [pos]}})
    check("ledger: two rows for one position block instead of one replacing the other", r["status"] == "BLOCKED")


def main() -> None:
    for seed in range(CASES):
        basis_invariants(seed)
        money_invariants(seed)
        ledger_invariants(seed)
    basis_fixed_cases()
    money_fixed_cases()
    ledger_fixed_cases()
    if errors:
        seen = sorted(set(errors))
        print("TOOL INVARIANTS FAILED")
        for e in seen[:40]:
            print("-", e)
        raise SystemExit(1)
    print(f"TOOL INVARIANTS PASS ({CASES} seeds per property)")


if __name__ == "__main__":
    main()
