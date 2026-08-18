# ADR-005: Provenance model

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

CR-9B establishes that the runtime carries five distinct kinds of knowledge
(model, runtime state, assertion, evidence, derived knowledge) and that
they MUST NOT be conflated. CR-10 §D (the truth model) makes the same point
at the scenario level: observed, asserted, inferred, and approved knowledge
are different epistemic states, with different confidence, different
sources, and different downstream authority. CR-9BC further requires that
derived knowledge be reachable back to its sources through an explicit
chain `Conclusion → Inference → Assertions → Evidence → Sources`. The
risk being mitigated is the silent overwrite: a derived or inferred claim
replacing an asserted one, or an approved claim eroding an observed one,
without any audit trail back to what was known, when, and by whom.

## Decision

- The runtime **MUST** represent four epistemic states for any claim:
  **observed** (sensor / system capture), **asserted** (human or system
  claim), **inferred** (derived by a rule), and **approved** (human
  endorsement of an assertion). The four states **MUST NEVER** be conflated
  into a single boolean.
- Each piece of derived knowledge **MUST** carry a provenance chain
  `Conclusion → Inference → Assertions → Evidence → Sources` (CR-9BC).
  Every link in the chain **MUST** be resolvable as a graph edge, not
  hidden in metadata.
- Transitions between states **MUST** be explicit state transitions, never
  silent overwrites (see ADR-008). Supersession **MUST** create a new
  assertion plus a `supersedes` link, not a destructive edit.
- Every assertion **MUST** record `asserted_by`, `asserted_at`,
  `confidence` where applicable, and `status`
  (Proposed → Verified → Approved / Rejected / Superseded / Disputed,
  CR-9O).
- A consumer that needs to know "is this authoritative right now?"
  **MUST** be able to derive the answer from the state, the
  supersession chain, and the approval status — not from a cached flag.

## Consequences

- Positive: every claim in the graph is auditable back to its sources,
  with the rule that produced it and the evidence it relied on.
- Positive: competing assertions coexist; the closed loop can reason
  about disagreement instead of papering over it.
- Negative: more nodes, more edges, more state to maintain; the graph is
  heavier than a naive entity–relationship model would be.
- Forecloses: a single "truth" flag per entity; overwriting one assertion
  with another; inference results stored as if they were observations.

## References

- CR-9B — five kinds of knowledge
- CR-9BC — provenance chain
- CR-9O — assertion status
- CR-10 §D — truth model
- docs/runtime-architecture.md §3