# ADR-008: Inference versus authoritative knowledge

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

Inference is useful — it surfaces gaps, suggests consequences, and powers
decision support — but if it silently merges with authoritative
knowledge, the graph loses its ability to distinguish *what is claimed*
from *what was derived*. CR-9CQ forbids silent inference: a derived
result **MUST** never appear in the same state as an observation or an
approved assertion. CR-9R/T requires that any inference carry provenance
(`derived_from` plus the `derivation_rule`) and be labelled with a
reasoning level (e.g. structural, rule-based, statistical, ML). CR-10 §D
makes the same point for the truth model: scenarios, simulations, and
assessments all produce *inferred* claims and must keep them separate
from *asserted* ones.

## Decision

- The runtime **MUST NEVER** silently merge an inferred result with an
  observed fact or an approved assertion (CR-9CQ). Inference produces
  claims in the `inferred` epistemic state; they remain there until a
  human or system explicitly promotes them through the assertion
  lifecycle.
- An inference operation **MUST** result in an explicit state transition
  in the graph: the derived node/edge appears with `provenance.derived_from`
  and `derivation_rule`, never by overwriting an existing assertion.
- Every inferred claim **MUST** carry a reasoning level (structural /
  rule-based / statistical / ML / other) per CR-9R/T. Downstream
  consumers **MUST** be able to filter or weight by reasoning level.
- Promotion of an inferred claim to an asserted claim **MUST** go
  through the assertion lifecycle (`Proposed → Verified → Approved`) and
  **MUST** create a new assertion; it **MUST NOT** mutate the inferred
  claim in place.
- A consumer that needs "what is true right now?" **MUST** consult the
  truth model (ADR-005) and **MUST NOT** rely on inferred results as
  authoritative unless they have been promoted.

## Consequences

- Positive: the graph never confuses "the model said so" with "we know
  this to be true" — the closed loop stays trustworthy.
- Positive: reasoning level and derivation rule let audit and compliance
  trace any inferred claim back to its inputs.
- Negative: more nodes, more state transitions; "answer a simple
  question" requires choosing an epistemic filter.
- Forecloses: rule engines that write inferred results over authoritative
  ones; ML predictions silently treated as observations; "smart"
  consumers that hide the inference boundary from users.

## References

- CR-9CQ — no silent inference
- CR-9R/T — provenance + reasoning level for derived knowledge
- CR-10 §D — truth model
- ADR-005 — provenance model