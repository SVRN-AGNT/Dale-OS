# Authority Migration

Use when work changes **what decides** a value, state, action, or claim: consolidating, splitting, renaming, or retiring an enum, tier, role, flag, credential route, permission, or pricing/policy field. Load it during harness design, because axis separation changes how lanes are cut. The attack on the resulting synthesis is `adversarial-synthesis.md`.

Topology: **Consolidate -> Classify -> Separate axes -> Sequence by hazard -> Attack -> Falsify** (`workflow-patterns.md`, pattern 9).

## Separate the axes

Do not collapse these into one question:

- value correctness — is the current value right?
- authority — what source is allowed to decide it?
- persistence — where is it stored?
- derivation — what can compute from it?
- presentation — what does the user see?
- compatibility — what legacy routes remain reachable?
- migration — how old state becomes new state.

A migration can preserve the value while changing authority, or preserve authority while changing storage. Treat those as different hazards.

### Overloaded values hide independent decision axes

A single plan or tier vocabulary often answers several independent questions at once:

```text
Can this person enter?                       (admission)
What ordinary product policy do they get?    (policy)
Do they have operator / admin capability?    (authority)
Are they in a cohort or programme?           (cohort)
Which credential route applies?              (routing)
What operational budget or safety cap?       (economics)
```

For every overloaded field, ask: **what independent axes hide inside this one value? Which axis does it hold real authority over? Which are merely correlated today?** Correlation is what makes the overload invisible: a cohort value that happens to select a credential route looks like a credential authority until one account has the cohort and not the route.

**Core heuristic: separate the authority axes first, then collapse the vocabulary.** Deleting the conflating value before its axes are separated produces twin failures: an authority silently lost (operator access disappears) and an authority silently widened (a credential route fails open).

## Build the authority map

For each governed fact, list:

- canonical source;
- canonical writer;
- canonical reader/selector;
- fallbacks and their exact conditions;
- migration-only routes;
- diagnostic-only routes;
- compatibility routes;
- consumers that re-derive the fact independently.

A route with no explicit role is a competing authority until proven otherwise.

## Classify references

A raw grep inventory is misleading: it makes a label, a database column, and a security predicate look like the same "consumer". Classify every hit, and state **which slice owns each category**; that is what stops scope explosion. Dispositions are what the synthesis *recommends*; the slice that acts on one still needs its own authorization.

| Class | Means | Recommended disposition |
|---|---|---|
| **BEHAVIORAL** (canonical dependency) | decides product, security, economics, or output | the migration's real work |
| **TRANSPORT** | carries the value but decides nothing | may keep the value; loses nothing |
| **COMPATIBILITY / MIGRATION** | exists to accept, translate, or reject old state | keep until its exit condition is met |
| **PERSISTED / HISTORICAL** | stored for audit, history, or backward compatibility | usually keep; rewriting history is a separate, owner-gated decision |
| **DISPLAY / OBSERVABILITY / DOCS** | labels, admin UI, logs, analytics, documentation-only mentions | later slice; never a reason to keep an authority |
| **TEST / DEV INFRASTRUCTURE** | simulators, fixtures, capture bypasses | often deleted *with* the restriction (`adversarial-synthesis.md`) |
| **DEAD / STALE** | no production reachability | delete, but prove unreachable: dormant is not dead |
| **PROTECTED CONSUMER** | inside a locked or protected surface | fix **upstream**; never edit it to satisfy a workflow |

Do not delete every old name blindly. Some old references exist precisely to migrate or reject old state safely.

Two failure modes this prevents: using a *display* reference to justify retaining an obsolete authority, and proposing edits inside a protected surface when the fix belongs to the authority it consumes.

## Value retention is not authority retention

Two questions, and the second is never inferred from the first:

> Does this value still exist? · Does anything still **trust** it?

A good intermediate architecture often says: *the string remains for compatibility and history, but changing it changes no product behavior.* That is a legitimate, testable end state, and the safest transitional shape available, because a retained value can serve as the signal that distinguishes "pre-migration record" from "ordinary record" (`adversarial-synthesis.md`, malformed transitional shape).

So the synthesis states, per value, exactly one of:

- **retained / decides nothing**
- **retained / still decides X**
- **removed**

A value in the second state that everyone believes is in the first is the defect this section exists to surface.

## Hazard-driven sequence

A phase order is not an ordering. Every phase boundary carries its causal justification:

> **X must precede Y, because otherwise Z fails open / fails closed.**

"Phase 1, Phase 2, Phase 3" with no hazard attached is a list, and it is rejected. For each transition, state why it is now safe, which authority was lifted first, and which dangerous dependency is gone.

Default order:

1. map current authorities and consumers;
2. establish the new canonical authority;
3. move or adapt writers;
4. move readers/selectors;
5. migrate persisted state if needed;
6. constrain fallbacks;
7. remove duplicate authority;
8. verify degraded/absence behavior;
9. verify no hidden re-derivation remains;
10. retire compatibility only after its exit condition is satisfied.

Worked example, collapsing an overloaded plan value:

```text
operator authority off the value     else collapsing it removes operator access
credential routing off the value     else the route fails open to the default credential
admission off the value              else entry silently depends on a value being deleted
runtime policy collapse              now the only axis the value still owns
persistence + admin surfaces         safe once nothing behavioral reads the old value
public surfaces                      readouts follow enforcement, never lead it
vocabulary cleanup                   last: the value decides nothing by this point
```

Read it as a rule rather than a template: **every step removes an authority from the value before the step that removes the value.** Ordering derived any other way (alphabetical, by file count, by ease) is how a consolidation fails open in the middle.

## Falsification matrix

Written before implementation, so each slice knows what it must make red. For each invariant, name **one mutation expected to fail a test**. That is what separates a test that *describes* the architecture from one that *protects* it.

| Invariant | Mutation that must turn it red |
|---|---|
| the old discriminator no longer grants authority | restore the old predicate |
| the new authority is load-bearing | remove the canonical writer |
| it is the *only* writer | mount a second consumer that merely reads, and assert the shared model is never cleared |
| a refusal is final | restore the environment-default fallback |
| both conditions are required | change the `AND` to an `OR` |
| absence fails closed | make the missing policy take the old default |
| the client does not decide | restore the client-side duplicate predicate |
| the compatibility value decides nothing | change the string while holding the canonical fact fixed |

Also try to prove, before completion:

- two canonical writers can still race;
- an old reader can bypass the new authority;
- absent migrated state becomes a fabricated default;
- rollback would destroy data;
- a compatibility route can live forever without an explicit exit condition;
- tests pin spelling but not semantic authority.

**Prove both directions.** A migration is not proven because valid users still work; prove that forged legacy input no longer confers authority.

| | Invariance | Converse / anti-bypass |
|---|---|---|
| operator | legacy privileged value -> ordinary policy: operator behavior unchanged | ordinary policy **without** operator capability: operator behavior NOT granted |
| credential | legacy managed value -> ordinary policy, same assignment: same credential | assignment inactive: must NOT fall through to the default credential |

Reconnaissance need not execute these; the synthesis must name them, and the implementation slice owns running them. An invariant with no mutation beside it is one nobody has agreed how to protect.

## Deliverable

For an authority migration, the synthesis carries, in order:

1. the **axes**;
2. every reference **classified** with its owning slice;
3. per value: **retained / decides nothing**, **retained / still decides X**, or **removed**;
4. the **hazard-ordered** sequence with a causal sentence per boundary;
5. the **falsification matrix** with invariance and converse rows;
6. the CI reachability of each gate that protects an invariant (`adversarial-synthesis.md`).
