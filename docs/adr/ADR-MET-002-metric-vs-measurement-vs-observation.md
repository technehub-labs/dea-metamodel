# ADR-MET-002: Metric vs Measurement vs Observation as distinct semantic concepts

- Status: Proposed
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-000 §4 (dea:Observation REFACTOR); CR-MET-003
  (Measurement and Observation entities)
- Supersedes: nothing
- Referenced by: CR-MET-001, CR-MET-003, CR-MET-004, CR-MET-011

## Context

The OpenDEAM metamodel currently declares `dea:Observation` (line 1855;
profile `dea:assessment`; CR-5 §27: "a raw measured or observed fact
collected as input to assessment"). This is the assessment-side INPUT
concept: a fact flowing INTO an Assessment.

The Metric capability programme (CR-MET-003) introduces two new
entities:

- `dea:Measurement`: the execution or application of a Metric
  definition to a particular subject, within a defined context, using
  an identified measurement method and applicable configuration.
- `dea:MeasurementObservation`: the recorded result of a
  `dea:Measurement`. This is the measurement-side OUTPUT concept.

The user insight (verbatim 2026-10-18): "Assessment score may be a
measure, but not all assessments are Metrics. So am not clear why you
want to membership from dea:assessment."

The user clarification establishes that the existing assessment-side
`dea:Observation` and the new measurement-side `dea:MeasurementObservation`
are different entities on the assessment-vs-measurement axis. The
existing `dea:Observation` is an INPUT to an Assessment; the new
`dea:MeasurementObservation` is an OUTPUT of a Measurement. They are
siblings, not re-memberships.

Four options were considered for the relationship:

- A: re-membership the existing `dea:Observation` from `dea:assessment`
  to a foundational scope, broadening the definition to subsume both
  use cases.
- B: reuse the existing `dea:Observation` for both; add a `direction`
  field (input to assessment vs output of measurement).
- C: introduce `dea:MeasurementObservation` as a new first-class entity
  and keep the existing `dea:Observation` in `dea:assessment` profile
  unchanged.
- D: introduce `dea:MeasurementObservation` and refactor the existing
  `dea:Observation` to a measurement-side sibling with re-membership.

Position A is the original CR-MET-000 Q1(a) recommendation; the user
clarification 2026-10-18 rejected it. Position B collapses two distinct
concepts into one entity and loses semantic clarity. Position D
mixes the new entity with the old (re-membership) and re-introduces
the same problem Position A had. Position C is the cleanest
separation: the existing entity stays where it is; the new entity
lives alongside it as a sibling.

The user-supplied CR-MET-000 §2 establishes the binding principle:
"Measurement is distinct. A Metric defines what and how to measure. A
Measurement represents the execution or application of that definition."

## Decision

1. `dea:Measurement` SHALL be a new first-class entity introduced by
   CR-MET-003. It represents the execution or application of a Metric
   to a subject.
2. `dea:MeasurementObservation` SHALL be a new first-class entity
   introduced by CR-MET-003. It represents the recorded result of a
   `dea:Measurement`. The id `dea:MeasurementObservation` preserves the
   `dea:Observation` id for the existing assessment-side concept.
3. The existing `dea:Observation` (CR-5 §27) SHALL remain in
   `profile: dea:assessment` unchanged. It is the assessment-side INPUT
   concept; it is NOT a Metric concept.
4. `dea:Measurement` and `dea:MeasurementObservation` SHALL be siblings
   of `dea:Observation` along the assessment-vs-measurement axis. They
   are NOT specializations of `dea:Observation`; they are NOT a
   re-membership of `dea:Observation`.
5. A new relationship `dea:produces` SHALL be introduced (if not
   present) with source = `dea:Measurement`, target =
   `dea:MeasurementObservation`. Cardinality: 1 source to 0..*
   target (a Measurement may fail, be cancelled, or otherwise produce
   zero Observations).
6. A new relationship `dea:applies-metric` SHALL be introduced with
   source = `dea:Measurement`, target = `dea:PerformanceMetric`.
   Cardinality: 1 source to 1 target (every Measurement applies
   exactly one Metric definition version).
7. A new relationship `dea:measures-subject` SHALL be introduced with
   source = `dea:Measurement`, target = any eligible enterprise
   entity (the same source-list as `dea:measured-by`).
8. The Assessment-side existing `dea:Observation` continues to
   reference `dea:Assessment` via the existing `dea:assesses`
   / `dea:assessed-by` vocabulary; no change.
9. EGV-004 identity continuity SHALL be preserved: every existing
   `dea:Observation` record continues to validate under the assessment
   profile; no migration is required.
10. No re-membership, no supersession, no deprecation of
    `dea:Observation` SHALL occur. The new entity is purely additive.

## Consequences

- Positive: the user clarification is honored at the metamodel level;
  the existing assessment-side `dea:Observation` is preserved
  unchanged.
- Positive: three distinct concepts (Metric, Measurement, Observation)
  are clearly separated: Metric is the definition; Measurement is the
  execution; Observation is the result.
- Positive: no EGV-004 migration overhead for the ~N existing
  assessment-profile Observation records.
- Positive: the new entity is purely additive; existing tests,
  schemas, and conformance suites continue to pass.
- Negative: the metamodel gains two new entities
  (`dea:Measurement`, `dea:MeasurementObservation`) and three new
  relationships (`dea:produces`, `dea:applies-metric`,
  `dea:measures-subject`). Generated artefacts must regenerate.
- Forecloses: re-membership of `dea:Observation` (Position A);
  field-direction collapse (Position B); mixed re-membership
  (Position D).

## References

- CR-MET-000 §4 disposition table (dea:Observation REFACTOR; user
  clarification 2026-10-18).
- CR-MET-003 (Measurement and Observation entities).
- CR-MET-004 (Measurement lifecycle).
- CR-MET-011 (Temporal Measurement; Observation has a nested `temporal`
  object per Q17b).
- metamodel/dea-metamodel.yaml line 1855 (current dea:Observation).
- User-supplied CR-MET-000 §2 architectural principles.
- EGV-004 (identity continuity).
