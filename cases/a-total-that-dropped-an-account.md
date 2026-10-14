# A Total That Dropped an Account

## Failure
One account's balance was correctly withheld as unavailable. The portfolio total still added it, and the addition coerced the missing value to zero, so the reported total was materially understated while looking clean. Withholding the preferred figure only made the code fall back to the next figure, which was understated too.

## Root mechanism
Unknown collapsed into zero inside an aggregate, and a fallback chain was withheld one tier at a time.

## Rule paid for
A withheld input never counts as zero. Withhold every fallback tier computed over the same incomplete set, fall back to a complete source, and label it.

## Skills
`accounting-integrity` · `truth-boundary` · `seam-audit`
