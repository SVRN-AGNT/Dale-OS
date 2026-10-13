# Greater Or Equal To Itself

## Failure
A causal test built the same output twice with opposite inputs and asserted `after >= before` in both directions. Both assertions passed because the two outputs were identical: the pipeline was ignoring its input entirely. Only an afterthought assertion that "something changed" failed.

## Root mechanism
A non-strict comparison between two runs is satisfied by the null case, which is exactly the failure the test existed to catch.

## Rule paid for
A causal assertion must be unsatisfiable by the null case. Assert the difference first.

## Skills
`reachability-proof` · `false-competence-check` · `truth-boundary`
