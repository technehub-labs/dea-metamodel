# ADR-010: Scenario isolation from production state

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

Scenarios — "what if we retire application X", "what if regulation Y
applies", "what if we acquire Z" — must be evaluated against the
enterprise *without* modifying the enterprise's current state. CR-10 §3
(CR-10B) establishes the discipline: a scenario is a reference to a
baseline plus the deltas it applies; evaluation never mutates the
baseline. CR-10AG extends this to scenario lifecycle: scenarios themselves
are versioned, immutable once executed, and referenceable as
reproducible artefacts. The risk being mitigated is the worst kind of
silent corruption — a "what if" calculation that, on completion, leaves
the production graph half-replayed.

## Decision

- A scenario **MUST** reference an explicit baseline (`baseline_id`,
  `as_of` temporal point) and **MUST** carry only the deltas it applies
  on top of that baseline. The full graph state **MUST NOT** be copied
  into the scenario.
- Scenario evaluation **MUST** run against a derived view composed at
  evaluation time: `baseline ∪ deltas`. The baseline **MUST NEVER** be
  mutated by evaluation, and the deltas **MUST NOT** be persisted into
  the baseline's `GraphStore`.
- Scenarios **MUST** be immutable once executed. Their inputs
  (baseline, deltas, parameters, evaluation timestamp) **MUST** be
  recorded as part of the scenario's version record (CR-10AG); the
  version is what makes the scenario reproducible, not the live graph
  state.
- A scenario that needs to influence production state **MUST** do so by
  generating a proposed change (decision / transition / new assertion)
  that goes through the standard authorization and assertion lifecycle
  (ADR-009, ADR-005). It **MUST NOT** write directly.
- Two scenarios evaluating the same baseline + deltas + parameters
  **MUST** produce equivalent results. Any non-determinism **MUST** be
  recorded in the scenario's result, not hidden by re-running.

## Consequences

- Positive: production state is never at risk from "what if" work;
  scenarios can be re-run, audited, and compared safely.
- Positive: scenario results carry their inputs; reproducibility is a
  property of the scenario record, not of the surrounding graph.
- Negative: every scenario evaluation allocates a derived view; cost is
  paid up-front rather than amortised over accidental side effects.
- Forecloses: in-place scenario replay; scenarios that "save their
  results" by mutating current state; scenario parameters that change
  silently because the baseline changed.

## References

- CR-10 §3, CR-10B — baseline + deltas
- CR-10AG — scenario immutability and versioning
- ADR-005 — provenance model
- ADR-009 — agent authorization model