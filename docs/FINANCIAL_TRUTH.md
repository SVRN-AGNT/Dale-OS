# Financial Truth

The point is not to make an AI sound like an accountant. The point is to keep an AI from manufacturing clean answers from dirty money data.

## The stack

```text
Evidence
  ↓
Money Trail
  ↓
Accounting Integrity
  ↓
Basis / Cash / Transfer / Tax Character
  ↓
Performance Truth
  ↓
Model Sanity
  ↓
Close the Books
```

A downstream answer cannot become more authoritative than the evidence feeding it.

## Evidence grades

- **OBSERVED** — direct transaction, statement or measured record.
- **AUTHORITATIVE** — official filing, form or source that governs the fact.
- **USER_ATTESTED** — explicitly supplied or confirmed by the human owner.
- **DERIVED** — deterministic result from accepted inputs.
- **ESTIMATED** — model, vendor or heuristic estimate.
- **UNKNOWN** — evidence cannot currently establish the value.

The grade describes provenance. It is not a confidence percentage.

## Financial states

Prefer explicit states over ambiguous booleans:

- `PASS`
- `WARNING`
- `BLOCKED`
- `WITHHELD`
- `UNRESOLVED`
- `NOT_APPLICABLE`

## Contamination rule

If unresolved data can materially change an output, that output must either:

1. withhold,
2. degrade with an explicit caveat, or
3. narrow itself to the subset that remains valid.

Do not silently calculate through contamination.

## Mutation rule

The public financial tools are read-only by design, in v0.1.0 and in the current 0.2.0-dev tree. Any future financial mutation must satisfy all of these before execution:

1. deterministic preview,
2. same economic logic in preview and commit,
3. explicit human authorization,
4. atomicity or rollback,
5. audit receipt,
6. post-write reconciliation.

If those cannot be met, do not add the writer.
