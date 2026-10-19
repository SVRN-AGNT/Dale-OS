# Evals

Dale OS keeps unlike evidence separate.

## Deterministic fixtures

`evals/fixtures/*.json` exercise the read-only financial tools with synthetic adversarial inputs.

```bash
python scripts/run_evals.py
```

These are ground-truth checks for arithmetic and hard invariants.

## Tool invariants and seeded bugs

`evals/invariants/test_tool_invariants.py` states the financial invariants from the domain (FIFO conservation and date order, transfer neutrality, missing is never zero, before/after symmetry) and checks them on seeded generated events. `evals/invariants/mutation_check.py` seeds one plausible bug at a time into a copy of `tools/` and fails if any bug leaves the invariants green, so the suite cannot quietly become decorative.

```bash
python evals/invariants/test_tool_invariants.py
python evals/invariants/mutation_check.py
```

## Activation evals

`evals/activation/corpus.jsonl` tests skill discovery/routing. Every canonical skill has one positive activation case and one confuser where that same skill should stay out of the way.

Capture runtime results using `schemas/model-eval-result.schema.json`, then score them with:

```bash
python scripts/score_activation.py results.jsonl
```

Routing metrics and answer-quality metrics are not interchangeable.

## Behavioral evals

`evals/behavioral/flagship.jsonl` tests behavior after the intended skill is active: refusing false certainty, carrying human authority, auditing blast radius, preserving financial truth, and stopping at protected boundaries.

```bash
python scripts/score_behavioral.py results.jsonl
```

The built-in scorer is only a **lexical smoke test**. It cannot prove semantic correctness. High-stakes claims need independent semantic review in addition to the reproducible lexical gate.

The Eve adapter includes framework-native runnable examples under `adapters/eve/evals/`.

## Full protocol

See `docs/MODEL_EVAL_PROTOCOL.md` for the cross-runtime evidence contract, required run metadata, and falsification rules.

Never collapse deterministic correctness, routing, lexical behavior, semantic judgment, tool correctness, and runtime compatibility into one blended score.
