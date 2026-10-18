---
name: transfer-neutrality
description: Identify and reconcile internal financial transfers without treating them as portfolio income, expense, contribution, withdrawal, or investment return. Use for account-to-account cash or asset movements, paired transfer events, wallet movements, or transfer-like records with missing counterparties, including when told to count one leg of a transfer as a withdrawal or contribution.
---

# Transfer Neutrality

## Rule

**Money does not teleport.**

## Workflow

1. Identify candidate outbound and inbound legs using stable ids and explicit metadata before heuristics.
2. Confirm amount/asset, account pair, currency, and economically compatible dates.
3. When both sides are proven internal, set portfolio-level external flow and P&L effect to zero.
4. If only one leg exists, mark the transfer unpaired. Do not silently relabel it as an external withdrawal/contribution. An instruction to count it does not pair it. If the user attests where the money went, record that as user-attested, let it drive only outputs labelled user-attested, and keep it below authoritative until the counterparty record is found. With no attestation, keep the external-flow effect unresolved and withhold returns that depend on it.
5. For asset transfers, preserve basis and holding period unless a governing tax/accounting rule says otherwise.
6. Report wrapper or jurisdiction changes separately; economic neutrality does not imply tax neutrality.

## Falsify it

Try to find the counterparty leg and prove conservation across the portfolio boundary. If one side is missing, do not force the event into contribution or withdrawal.

## Stop conditions

- Counterparty leg is missing and classification would alter performance.
- Transfer changes wrapper/jurisdiction and tax treatment is not established.

A stop is an output, not an excuse. State what evidence or authority would unblock the work.

## Output

TRANSFER PAIR · ACCOUNTS · AMOUNT/ASSET · EXTERNAL FLOW EFFECT · BASIS CONTINUITY · UNPAIRED/UNKNOWN STATE.

Keep the report short enough to act on. Preserve hard facts, unknowns, and blockers.
