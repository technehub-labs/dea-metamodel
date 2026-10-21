# ADR-MET-012: Ten quality dimensions are an inline Metric attribute, not a QualityAssessment entity

- Status: Accepted (landed with CR-MET-010)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-010 (Metric Governance, Quality, Lifecycle and Conformance)
- Supersedes: nothing
- Referenced by: CR-MET-010, ADR-MET-014

## Context

User-supplied CR-MET-010 §6 defines ten quality dimensions (semantic clarity, completeness, consistency, validity, accuracy, timeliness, reliability, comparability, traceability, governance) and states a critical distinction: the quality of a Metric *definition* must be distinguished from the quality of an individual Observation. "A perfectly defined Metric can produce poor-quality observations."

The pre-authored CR-MET-010 left the representation open: encode the dimensions as a `quality_dimensions[]` field on Metric, or introduce a referenced `dea:MetricQualityAssessment` entity, with the sub-decision explicitly deferred to the closure CR.

## Decision

1. **The inline `quality_dimensions[]` field is adopted.** No `dea:MetricQualityAssessment` entity is introduced.
2. `dea:MetricQuality.quality_dimension` is the 10-value controlled set: `semantic_clarity`, `completeness`, `consistency`, `validity`, `accuracy`, `timeliness`, `reliability`, `comparability`, `traceability`, `governance`.
3. Each dimension carries a `verdict` from a 4-value controlled set: `not_assessed`, `adequate`, `needs_improvement`, `inadequate`, plus optional `rationale`, `assessed_by_ref`, and `assessed_at`.
4. **Rationale for the inline form.** The ten dimensions describe a property of the Metric definition itself, not an independently identified object with its own lifecycle. A quality assessment is not referenced by anything, is not scheduled, and has no state transitions. Giving it an identity would create an entity whose only content is a date and a verdict, and would fragment the definition it describes (ADR-013).
5. **Definition quality and Observation quality remain strictly separate.** The ten dimensions describe the definition. Observation-level quality is carried on `dea:MeasurementObservation` via its own fields: `observation_quality`, `verification_state` (`unverified`, `ai_estimated`, `independently_verified`, `human_verified`), `precision`, and `confidence`. No dimension value on Metric may be read as a statement about any particular Observation.
6. **Definition quality is not inherited by Observations.** A Metric with `semantic_clarity: adequate` may still yield an inaccurate Observation. This is asserted by conformance, not merely stated here.
7. A `needs_improvement` or `inadequate` verdict MUST carry a `rationale`. An unexplained negative verdict is not actionable.
8. The `governance` dimension is the one that ties the quality framework back to ADR-MET-014: it asks whether ownership and approval are established, which is a Level 3 conformance question in its own right.

## Consequences

- Positive: zero new entities. The quality framework lands entirely on `dea:Metric`.
- Positive: the definition/Observation distinction is structural. The dimensions are on a different entity from the observation-quality fields, so a conformance test can assert they never cross.
- Positive: a verdict is visible on the Metric itself, which is where a catalog reader will look.
- Negative: quality assessments are not independently addressable. One cannot query "which Metrics were assessed by a given steward" without scanning every record, and a re-assessment overwrites rather than accumulates. If quality assessments need their own audit trail, this decision must be revisited under ADR-015.
- Negative: 10 optional dimension entries on every Metric is a substantial authoring burden for a catalogue that may not want to assert quality at all. The pragmatic answer is to leave dimensions `not_assessed`; the risk is a Metric that claims quality it never established.
- Forecloses: `dea:MetricQualityAssessment`. Reopening this requires demonstrating that a quality assessment needs identity independent of the Metric.
- Forecloses: treating a Metric's quality verdict as a statement about its Observations.

## References

- CR-MET-010 (Metric Governance, Quality, Lifecycle and Conformance).
- User-supplied CR-MET-010 §6 (ten dimensions; definition versus Observation quality).
- `schemas/entities/metric.json` (`quality_dimensions`).
- `metamodel/vocabularies/classifications.yaml`: `MetricQuality.quality_dimension`, `MetricQuality.quality_verdict`.
- `schemas/entities/measurement-observation.json` (`observation_quality`, `verification_state`, `confidence`).
- ADR-MET-014 (Metric Governance and Lifecycle).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).