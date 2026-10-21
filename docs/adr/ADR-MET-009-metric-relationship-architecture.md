# ADR-MET-009: Metric relationships extend the existing vocabulary; the design-time and runtime faces are separate relationships

- Status: Accepted (landed with CR-MET-003 and CR-MET-007)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-003 (Measurement and Observation Relationships); CR-MET-007 (Metric-to-Enterprise Entity Relationships)
- Supersedes: ADR-MET-004 §2 decision item 2 (naming; see Drift note)
- Referenced by: CR-MET-003, CR-MET-007, ADR-MET-004

## Context

CR-MET-001 introduced `dea:Measurement` and `dea:MeasurementObservation` but specified no relationships. Two distinct kinds of relationship are needed:

- Design-time intent: *this Metric is declared applicable to these subjects*. A catalog entry states which processes, capabilities, or controls a Metric is intended to cover, whether or not anything has been measured yet.
- Runtime fact: *this subject was measured by this Metric*. A Measurement records that an actual collection happened for a specific subject.

Conflating these would mean a catalog entry cannot declare applicability without also asserting a measurement occurred.

The pre-authored CR-MET-003 offered: extend `dea:produces`; add `dea:applies-metric` and `dea:measures-subject`. The pre-authored CR-MET-007 offered: extend `dea:measured-by` source from 7 to 16 types, add `dea:applies-subject`, or introduce a `dea:contextualizes`.

## Decision

1. **`dea:produces` is EXTENDED, not duplicated.** It gains `dea:Measurement` as a source and `dea:MeasurementObservation` as a target, carrying "the Measurement executed produces the Observation that was recorded."
2. **`dea:applies-metric` is introduced** (CR-MET-003): source `dea:PerformanceMetric`, target `dea:Measurement`, cardinality 1:1. It carries the design-time intent: this Metric definition is the one this Measurement applies.
3. **`dea:measures-subject` is introduced** (CR-MET-003): source `dea:Measurement`, target the measured subject, cardinality 1:1. It carries the runtime fact.
4. **`dea:measured-by` source is EXTENDED from 7 to 16 types** (CR-MET-007): `dea:AssessmentDimension`, `dea:Control`, `dea:DataEntity`, `dea:MaturityModel`, `dea:OrganizationalUnit`, `dea:Policy`, `dea:Risk`, `dea:Service`, `dea:ValueStream`, plus `dea:ApplicationComponent`. This covers the 10 cross-domain integration categories named in user-supplied CR-MET-007 §3.
5. **`dea:measures-subject` target is EXTENDED to the same 16 types** (CR-MET-007), mirroring `dea:measured-by` so the design-time and runtime faces stay in step. An asymmetry between the two lists would let a Metric declare applicability to a subject it could never be measured against.
6. **`dea:applies-subject` is introduced** (CR-MET-007): source `dea:PerformanceMetric` cardinality 0..*, target the same 16 enterprise types cardinality 0..*. It is the design-time applicability declaration; `dea:measured-by` is the runtime measurement fact.
7. `dea:applies-subject` and `dea:measures-subject` are the Q9a split: design-time intent and runtime fact are distinct relations and neither implies the other.
8. **`dea:Activity` is NOT introduced and MUST NOT be added to any relationship source list** (user instruction 2026-10-18). `dea:BusinessProcess` is the decomposition path; activity-level measurement is sub-measurement reached through the catalog-internal Activity/Task hierarchy.

## Drift note

ADR-MET-004 as originally written names the design-time relationship `dea:applies-to`. The implementation ships `dea:applies-subject`, because pre-existing `applies_to` properties in `maturity-rule.json` and `policy-rule.json` collided with the bare name and violated E003. This ADR records the shipped name. ADR-MET-004 decision item 2 and decision item 8 should be read with the substitution `dea:applies-to` -> `dea:applies-subject`.

## Consequences

- Positive: a catalog entry can declare intended applicability without asserting a measurement occurred, and a Measurement can record a runtime fact without polluting the catalog declaration.
- Positive: `dea:measured-by` growing from 7 to 16 source types is one extension of an existing relationship rather than 9 new ones.
- Positive: mirroring the 16-type list across `dea:measured-by` and `dea:measures-subject` makes the intent/fact pair checkable by a single conformance assertion.
- Negative: three new relationships (`dea:applies-metric`, `dea:measures-subject`, `dea:applies-subject`) is a real vocabulary cost.
- Negative: the 16-type lists must be kept in step across two relationships. A conformance test asserts they match, but the burden of remembering that remains with authors.
- Forecloses: `dea:contextualizes` (the collapsed option). Collapsing design-time and runtime into one relation was rejected because it destroys the distinction.
- Forecloses: Metric-specific relationships per enterprise domain (9 new relationships for the same 9 domains).
- Forecloses: `dea:Activity` as an entity or as a relationship endpoint.

## References

- CR-MET-003 (Measurement and Observation Relationships).
- CR-MET-007 (Metric-to-Enterprise Entity Relationships; 10 cross-domain categories).
- ADR-MET-004 (Measurement subject and context).
- `metamodel/dea-metamodel.yaml`: `dea:produces`, `dea:measured-by`, `dea:applies-metric`, `dea:measures-subject`, `dea:applies-subject`.
- User instruction 2026-10-18 (no `dea:Activity`).
- `metamodel/dea-metamodel.yaml` line 592 (`dea:BusinessProcess`, L3).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).