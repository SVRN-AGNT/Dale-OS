# Public / Private Boundary

Dale OS is public. That does not mean everything that taught it belongs in public.

## Safe to publish

- generalized operating principles
- portable workflows
- sanitized incident mechanisms
- generic financial fixtures
- deterministic tools built on synthetic data
- eval rubrics
- adapter code

## Keep private

- personal account values or transactions
- brokerage exports
- credentials, tokens, keys or private endpoints
- ACF proprietary scoring formulas and weights
- private ACF product architecture that is not required to understand the generic rule
- internal customer or beta-user data
- anything that makes a security boundary easier to attack

## Sanitization rule

Preserve the **failure mechanism**, not identifying details.

Bad public case:

> Account X at Broker Y was wrong by $12,345.67.

Better:

> A canonical non-zero cash balance had no mirror row. The classifier treated absence as agreement and marked the account reconciled.

The second version teaches the rule without leaking the book.
