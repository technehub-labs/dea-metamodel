# ADR-MET-015: The metamodel specifies measurement semantics, not the measurement runtime

- Status: Accepted (landed with CR-MET-004 and CR-MET-005)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-004 (Measurement Lifecycle and Execution Modes)
- Supersedes: nothing
- Referenced by: CR-MET-004, CR-MET-005

## Context

The Metric programme defines a Measurement lifecycle with 10 states, 8 execution modes, and 16 legal transitions. The risk is that specifying a lifecycle implicitly specifies a scheduler: a reader may reasonably infer that the metamodel expects an engine to drive those transitions, and a runtime team may build one that the metamodel then has to accommodate.

CR-MET-004 explicitly drew a boundary in its own vocabulary file under the key `metamodel_runtime_boundary`.

## Decision

1. **The metamodel is canonical semantics only.** It specifies what states exist, which transitions are legal, what each state means, and what must be recorded when a state is entered. It specifies **no** executor, no scheduler, no queue, no retry policy, and no concurrency model.
2. `metamodel/vocabularies/measurement-lifecycle.yaml` carries the boundary statement explicitly under `metamodel_runtime_boundary`, so a reader of the vocabulary sees the boundary without needing to find the CR.
3. **10 lifecycle states.** Terminal states are strictly `cancelled` and `superseded`. `completed`, `failed`, and `rejected` are conditionally terminal with exactly one outgoing transition each, to `superseded`.
4. **8 execution modes** are named as a controlled vocabulary. A mode is a semantic classification of *how* a Measurement runs, not a scheduling instruction.
5. **16 legal transitions** are enumerated. Any transition not in the 16 is illegal, and a runtime that attempts it is in violation of the metamodel rather than exercising an extension point.
6. **The vocabulary is pure data.** No executable content, no ordering directives that imply scheduling, no timing requirements. Runtime concerns are the runtime's.
7. Where a Measurement needs operational detail (how many retries, what timeout, which queue), that detail lives in the `dea:Measurement` record and the runtime, not in the lifecycle vocabulary.

## Consequences

- Positive: a runtime team can implement the lifecycle without asking the metamodel for permission, and without the metamodel having to know the runtime's shape.
- Positive: the 16-transition enumeration means a non-conformant state machine is detectable. A runtime that permits a transition outside the set can be tested against the vocabulary.
- Positive: keeping the vocabulary as pure data means it can be consumed by a conformance validator, a documentation generator, or a UI, none of which require interpreting control flow.
- Negative: the vocabulary says nothing about how long a Measurement may sit in `running`. A runtime with a stuck Measurement is not in violation of the metamodel, which is correct but means operational monitoring is entirely a runtime responsibility.
- Negative: because there are no timing constraints, the metamodel cannot help decide whether a given execution mode is appropriate for a given SLA.
- Negative: a runtime team may build a state machine that differs from the metamodel's intent while still respecting the 16 transitions. Semantic drift within legal transitions is not detectable from the vocabulary alone.
- Forecloses: an execution engine, scheduler, or queue inside the metamodel.
- Forecloses: treating the lifecycle vocabulary as an orchestration specification.

## References

- CR-MET-004 (Measurement Lifecycle and Execution Modes).
- CR-MET-005 (Measurement Semantics; `metamodel_runtime_boundary`).
- `metamodel/vocabularies/measurement-lifecycle.yaml` (10 states, 8 execution modes, 16 transitions, terminal states, `metamodel_runtime_boundary`).
- ADR-006 (Temporal Semantics).
- ADR-007 (Runtime API Separation).
- ADR-MET-011 (Temporal Measurement Architecture).
- ADR-MET-016 (Metric Analytics and Decision Intelligence).