# Adversarial Synthesis

Use at MEDIUM/HIGH depth after the first synthesis exists. At MEDIUM, narrow the *reading* to the authorities in play; never narrow the probe set.

The goal is to attack assumptions that individual finding verification can miss.

## What this pass is, and what it is not

It is not more breadth. The lanes have reported and a synthesis exists; this pass exists to **attack that synthesis** before anyone writes code. Its subject is the proposed architecture and its migration path, not any individual finding. It does read code (every probe below is a targeted read), but it opens no new survey lane and re-answers no question the lanes were cut to answer.

Per-finding verification (`verification-and-adjudication.md`) checks one claim against one evidence surface. It cannot catch an assumption **every lane shared and no lane owned**, or a consequence that appears only where two lanes' conclusions meet. A consolidation can pass every per-finding check and still contain a whole class of second-order defects: breadth found the architecture, and nothing yet tried to break it.

Because the probes decide what the lanes must bring back, skim them during harness design and run the pass once the first synthesis exists.

## Brief

Run the pass on the strongest reasoning tier available, in a fresh context, briefed the way a per-finding verifier is briefed. The higher-stakes layer does not deserve the thinner brief. It receives:

1. **The synthesis as a claim under attack**, never as settled background: no lane's persuasive narrative, no confidence ranking.
2. **An evidence surface**: the authorities the architecture proposes, the *inputs* each derives its answer from, the file sets the lanes covered, and where the gate and CI configuration live. A pass given no surface answers from data nobody gathered.
3. **A read budget**, so "I could not check that" is a reportable outcome rather than a silent one.

## Cross-lane probes

Ask these of the synthesized architecture, not of the codebase in general. Each names the shape it catches, because a bare question invites a bare "checked, fine".

- **Shared unproven assumptions.** What do several lanes assume without any lane having proved it? An assumption every lane inherited from the same doc, comment, or naming convention reads as consensus and is one datum. Name it, then ask which lane would have had to prove it.
- **Surviving authority.** What would still decide something after the simplification lands? The shape: a value keeps deciding in one forgotten branch while everyone treats it as retired.
- **Fail-open on disappearance.** If this field, branch, or discriminator disappears, what becomes permissive that was restrictive? Every removed condition is a grant unless something else denies.
- **Unexpected fail-closed.** What becomes restrictive for a legitimate user who has no new-world state yet? A migration that is safe for new accounts and locks out existing ones is not safe.
- **Independent re-derivation.** Which consumer computes the old answer from raw inputs instead of asking the new authority? Grep for the *inputs*, not the authority's name: a re-deriver never mentions it.
- **Meaning drift in stored state.** What persisted state changes meaning when the old discriminator goes away? A value written under old semantics is read under new ones, and nothing errors.
- **Second writers and listeners.** What other writer, listener, store, or cache can disagree with the new authority?
- **Inert residue.** What does the target architecture leave standing but deciding nothing: fields, branches, flags, envelope keys? Dead authority is a false signal to the next reader. Sweep **companion** values too, anything that gated the same way as the value being consolidated, which a grep scoped to the consolidated vocabulary never returns. Each survivor gets a named compatibility purpose or a deletion slice.
- **Silent legacy restoration.** Which fallback quietly restores the old behavior?
- **Readout vs. enforcement.** Which label, notification, or status surface now tells a story enforcement no longer backs?
- **Tests that describe rather than protect.** Which green test is green because it never exercises the real path: a fixture that sets the answer, a mock that is the authority, a suite CI does not run?
- **Composition effects.** Which consequence appears only when two accepted findings interact? A cross-lane bug may belong to neither lane alone.

### Canonical authority

For every important value or decision, ask:

- What is allowed to decide this?
- Is there exactly one canonical route?
- Can a fallback or compatibility path silently become canonical?
- Is the value re-derived elsewhere from lower-level inputs?
- Can a downstream layer upgrade confidence or authority without evidence?

## Authority choke-point audit

For each proposed canonical authority `X`, work all ten rows. "Who calls `X`" is one of them, and the least likely to hold the defect. A row that cannot apply is **answered `n/a` with its reason**, never skipped silently; for a single-consumer authority several rows are `n/a` in one line each.

| | Row | The shape it catches |
|---|---|---|
| 1 | Producers | two functions that both mint the answer |
| 2 | Direct consumers | the easy grep; establishes nothing on its own |
| 3 | Alternate producers | a helper that builds the same object from parts |
| 4 | Bypasses | a caller that reaches past `X` to its inputs |
| 5 | **Fallbacks** | `X()` refused, and the caller supplies its own answer |
| 6 | Default / coalesce behavior | `??`, `\|\|`, `default:`, optional-chain-plus-default |
| 7 | Cached copies | a memo or module store holding a pre-migration answer |
| 8 | Persisted copies | a column or document written before the change |
| 9 | Client mirrors | the client recomputing a server decision |
| 10 | Status / readout mirrors | a label or admin screen with its own derivation |

**The canonical fail-open: a refusal undone one line later by a fallback.** A credential resolver correctly refuses, and its caller falls back to a shared default credential from the environment, so the refusal is undone by code that looks like resilience. Search for that shape directly: read every call site of the authority for what happens on the negative branch.

Two rows deserve their own greps rather than reading call sites: **fallbacks** (the authority's name adjacent to `||`, `??`, `catch`, `default`) and **re-derivation** (the authority's *input* names appearing where its name does not).

## State-authority topology

Applies wherever state is shared and mutable (a client store, a server cache, a module singleton, a context provider), not only to work that announces itself as frontend. A lane cut by authority axis does not label itself "frontend", which is how this class hides.

Map the topology before proposing a one-writer contract:

```text
WRITERS · READERS · SUBSCRIBERS · LISTENERS · CONTEXT PROVIDERS
MODULE STORES · CACHE OWNERS · REFRESH TRIGGERS · CLEAR/RESET CALLERS
DERIVATIONS · OVERWRITE PATHS · RACES · PERSISTENCE BOUNDARIES · INVALIDATION EDGES
```

Never assume *same hook = harmless reuse*. Ask:

- Does mounting this consumer instantiate another listener?
- **Does reading this also write?** A hook that owns a fetch is a writer even where the caller only wants its `loading` flag.
- Can two roots legitimately own separate writers, or is this one-writer/many-reader?
- Does an identity change **clear** shared state before the replacement arrives? A writer that resets then refetches makes every reader briefly see "no capability", which renders as a refusal.
- Can a downstream component accidentally become a producer?
- Can a correct worker still cause a wrong outcome because the topology permits stale writeback or competing ownership?

The typical shape: one hook becomes the canonical writer; an unrelated page still mounts it merely to read `loading`, creating a second writer that clears the shared read model before refetching, so the UI blinks into a refusal. **Verify transitive mounts, not direct imports**: the second writer is usually a component that renders the consumer, not one that names it. Bound the sweep to a mount trace from each consumer of the authority being moved, not a traversal of the whole tree.

## Fail-open / fail-closed, per authority move

One small table per high-risk move. Filling it is the point; a prose paragraph hides the empty cell.

| Field | Content |
|---|---|
| Current condition | what decides today |
| Proposed condition | what decides after |
| Failure if OLD state is missing | |
| Failure if NEW state is missing | |
| Fail-open possibility | who gets access they should not |
| Fail-closed possibility | who loses access they should keep |
| Safe transitional behavior | what the migration does about the malformed middle |
| Degraded-state readout | does the UI or report tell the truth about the degraded state? |

For every missing or failed dependency, also record whether absence is distinct from zero, false, or success.

**Hunt the malformed transitional shape, not the two clean states.** The happy-path old world and the happy-path new world are both consistent; defects live in the record that is neither.

```text
old:     a legacy plan value selects a managed credential route
new:     an explicit assignment record selects that route
hazard:  a legacy account that has the old value and no assignment yet
wrong:   treat it as ordinary -> hand it the shared default credential (fail-open)
safe:    read the legacy value ONLY as "this account was historically managed",
         so a missing assignment fails CLOSED until the assignment exists
```

The safe transition keeps the legacy value as a **compatibility signal with no product authority** (`authority-migration.md`, value vs. authority) purely so absence cannot be mistaken for "ordinary". That is the general move.

## Absence is not a safe default

Scope: the call sites of the authorities this change moves, not every coalesce in the files they live in. At each `||`, `??`, `default:`, `catch`, or optional-chain fallback, ask one question:

> After this change, does **missing** still mean what it meant before?

The shape: a field that was optional becomes canonical. Before, absent meant "ordinary user", so defaulting to the ordinary policy was right. After, absent means **malformed or pre-migration record**, and defaulting to the ordinary policy is fail-open. The old default did not become wrong when it was written; it became wrong when the field's meaning changed, which is why it survives review. Every migration that makes an optional field mandatory has at least one of these, and it will read as harmless.

## Transport and scheduler reachability

For loops and state machines, test both:

- legal state transitions;
- whether the runtime can actually wake the actor that owns the next state.

A valid state machine with an unreachable scheduler edge is still broken.

## Communication, readout, and CI reachability

**Communication is a downstream consumer of architecture.** When an authority's meaning changes, ask which surface now makes a promise enforcement no longer backs: emails, notifications, setup and onboarding flows, status pages, admin labels, billing and usage readouts, call-to-action copy, support and debug screens. The shape: once a credential denial stops meaning whole-product denial, an invite notification resumes sending, which is correct for admission and wrong for a user whose required dependency is disabled. Separate the axes the copy is conflating: *admitted, ready, configured, available, billable, operator, cohort member* are distinct states, and one generic "eligible / unresolved / denied" must not absorb several.

**CI reachability, recorded beside each invariant.** For every invariant the architecture depends on, the gate must actually run. Does it run on a pull request? On promotion? Only manually? Is the file named in a package script, and does a workflow call that script? Is it excluded by a tier or config? A green local test CI never executes is not a regression gate. Record reachability beside the invariant, not in a separate list.

**Verification reachability.** Does the test execute the live path or only a helper? Would it fail if the root fix were reverted? Is the environment class representative of production behavior? Are pre-existing failures separated from attributable ones?

**Census test infrastructure that compensates for the architecture.** Ask it of the simulators, flags, bypasses, mock roles, dev modes, and fixture-only paths that touch the restriction being removed, not of the whole harness: **census their callers**, then ask whether each exercises a **supported state** or defeats a restriction this change removes. The census is the evidence; "most real callers are capture harnesses forcing elevated access so a surface will render" is a finding, not an impression. Where the restriction goes, the pass **recommends** deleting the bypass rather than carrying the simulator; it writes and deletes nothing itself. Test infrastructure is never a justification for retaining dead production architecture.

## Output contract

The pass does not end in commentary. It returns:

1. **Probe ledger**: one line per probe: *probe · surface read · finding or `clean` · evidence*. A skipped probe and a clean probe must not produce identical output, and an unread surface is reported unread, never clean.
2. **Architecture-level breaks found**, with evidence.
3. **Shared assumptions that survived attack.**
4. **Revised synthesis**: the architecture after the attack, each change attributed to the probe that forced it.
5. **Hazards**: the completed choke-point table per authority, every fail-open/fail-closed table, the malformed transitional shapes, and the inert-residue inventory.
6. **Reclassifications**: references that moved category (`authority-migration.md`), because a category change moves slice ownership.
7. **Sequencing corrections**: any ordering the hazards force.
8. **Falsification plan**: the mutations that would prove each invariant real, with CI reachability beside each.
9. **Unsettled / new uncertainty**: what the pass could not resolve or newly introduced, and what evidence would resolve it.
10. **Handoff call**: whether the result is safe to hand off for already-authorized implementation, or should deepen or stop.

If the pass changed the architecture materially, re-derive the sequence and invariants from the revised version rather than patching them onto the old one.
