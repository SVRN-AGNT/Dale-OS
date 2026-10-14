---
name: risk-kernel
description: Design structural safety for an agent that acts without per-action human approval. Use when an agent will execute, trade, spend, deploy, send, or mutate real state autonomously; when someone proposes prompt instructions or policy text as the safety layer; when an agent can edit its own strategy, limits, or stage; or when reviewing whether a forbidden capability is truly unreachable. Do not use to judge whether an individual action is a good idea.
---

# Risk Kernel

## Rule

**Instructions are not boundaries. Make the forbidden unexpressible, not discouraged.**

Anything written in a prompt is reachable by anything else that reaches the prompt: retrieved text, tool output, a hostile document, the agent's own drift. When an agent acts without a human approving each action, safety has to be a property of the system's construction, not of its instructions. The human control surface moves from approving actions to setting the sandbox and reading the evidence.

The pattern is **agent proposes → kernel disposes → agent executes.**

## Workflow

1. **Make the kernel the only door.** One small module is the sole producer of the executable-action type, and every executor accepts nothing else. "Execute something the kernel never approved" must be an unrepresentable state, not a forbidden one.
2. **Bound limits in code, configure them in data.** Policy files may tune limits inside hard bounds compiled into the source and checked on load. Raising a bound is a reviewed code change, never a file edit the agent can reach.
3. **Remove capabilities instead of restricting them.** If the agent must never move money, withdraw, deploy, or delete, those verbs are absent from its intent type, its toolkit, and the interface it calls. A missing verb cannot be talked into existence.
4. **Keep self-modification inert.** The agent may rewrite its own strategy notes, and that is safe only if no enforcement code ever reads them. A note saying "ignore the cap" must be a string nobody executes.
5. **Deny self-promotion.** Capital, permissions, and autonomy tiers come from records no agent tool writes, and advance out of band on evidence derived from the ledger of outcomes, never from the agent's own claim.
6. **Resolve the stage from the environment only.** Replay, shadow, and live are decided in one file that reads the environment. No prompt, config, or argument can raise it.
7. **Stage the autonomy.** Replay proves plumbing, shadow proves decisions, then a bounded real budget the agent may genuinely lose, then more only as calibration is demonstrated.
8. **Pre-register and trip.** Each action records its predicted outcome and its own falsifiers before execution. Name tripwires that suspend autonomy automatically: an execution with no matching kernel permit, an action on stale data, a loss outside the sandbox's arithmetic, a capability reached by an unanticipated route.

## Anti-patterns

- A kernel that also judges quality (expected value, timing, taste). That is strategy wearing a safety hat. The kernel answers "is this inside the sandbox?", never "is this a good idea?".
- Regex-filtering hostile instructions. Filtering is a game you eventually lose; unreadable-by-enforcement is a property you can prove.
- One doctrine for every subsystem. "Human approves each action" and "kernel disposes" are per-subsystem choices. Write down which one governs where.

## Relationship

`protected-boundary` decides when an agent must stop and ask. `risk-kernel` is for the case where nobody will be asked, so the stop has to be built into the system. `reachability-proof` then proves the kernel actually sits on every path.

## Falsify it

Try to reach each forbidden capability from the agent's side: from the prompt, from its writable notes, from its config, from a tool's output. Search the code for any second producer of the executable type, and for any enforcement path that reads agent-writable state. One route found means the boundary is policy, not construction.

## Stop conditions

- The executable type has more than one producer, or executors accept raw intents.
- A hard bound lives only in a file the agent can write.
- The worst-case loss inside the sandbox has not been computed and accepted by the person who owns the money.

A bounded sandbox does not make the agent well-behaved. It can be calmly, reliably wrong inside it. Say so.

## Output

DOOR (sole producer) · HARD BOUNDS · REMOVED CAPABILITIES · INERT STATE · PROMOTION SOURCE · STAGE SOURCE · WORST-CASE LOSS · TRIPWIRES · ROUTES FOUND.
