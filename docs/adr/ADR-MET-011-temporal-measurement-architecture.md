# ADR-MET-011: Seven temporal dimensions are distinct facts; ReportingPeriod specializes TemporalInterval

- Status: Accepted (landed with CR-MET-011)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-011 (Temporal Semantics, Provenance and Historical Traceability)
- Supersedes: nothing
- Referenced by: CR-MET-011, ADR-MET-010

## Context

The user-supplied CR-MET-011 §3 states that seven temporal dimensions must be distinguished and explicitly that they "must not be collapsed into one timestamp." The dimensions are: observation time, measurement time, reporting period, valid time, transaction time, effective time, and publication time.

The CR offered three representations:

- A: seven separate fields on Observation / Measurement.
- B: one nested `temporal` object covering all seven.
- C: seven referenced entities.

## Decision

1. **Position B is adopted for Observation.** The pre-existing `temporal` placeholder on `measurement-observation.json` (which read "Full specification in CR-MET-011" with `additionalProperties: true`) is now fully specified with 9 named fields and `observed_at` + `recorded_at` required.
2. **`dea:ReportingPeriod` is introduced, and it SPECIALIZES `dea:TemporalInterval`.** This was not in the original options; it was the finding of the audit. `dea:TemporalInterval` (CR-6 §5) already carries `valid_from`, `valid_to`, `recorded_at`, `observed_at`, `planned_start`, `planned_end`, `effective_from`, `effective_to`, and its definition already states that the clocks are not interchangeable. Rather than duplicating that payload, `dea:ReportingPeriod` adds only what is genuinely new: `period_type` (7 values: `instantaneous`, `point_in_time`, `fixed_duration`, `rolling`, `cumulative`, `event_based`, `irregular`) and `period_semantics` (5 values: `calendar`, `fiscal`, `rolling`, `event_based`, `custom`). This is the kernel+specialization pattern of ADR-015.
3. **`EffectiveTime` is NOT introduced as a separate entity.** It is carried as the `effective_from` / `effective_to` pair on the Provenance record and in the Observation temporal object. Effective time describes the *governing definition*, not a separately identified object; giving it an identity would produce an entity with no lifecycle of its own.
4. **Conditional period fields are binding:**
   - `instantaneous` and `point_in_time` MUST have `period_start` and `period_end` null.
   - `fixed_duration`, `cumulative`, and `irregular` MUST have both non-null, with `period_start` preceding `period_end`.
   - `rolling` MUST declare `anchor_reference` and `window_size`.
   - `irregular` MUST declare `interval_count`.
   - `fiscal` semantics MUST declare `calendar_reference` and `fiscal_year_ref`.
   - `window_size` MUST be null on any non-rolling period.
5. **`dea:MeasurementObservation.record_state` carries the 5 record states** from user-supplied §7: `original`, `corrected`, `superseded`, `invalid`, `retracted`.
6. **`dea:corrects` is introduced; `dea:supersedes` is reused.** The audit found `dea:supersedes` was extended by CR-MET-004 to carry `dea:MeasurementObservation` on **both** endpoints, so supersession was already modelled and no new relationship was required. Only `dea:corrects` is genuinely new. The two are not interchangeable:
   - `dea:corrects` asserts the target was **wrong** (a revised restatement).
   - `dea:supersedes` asserts a **newer authoritative** value exists for the same period.
7. **The pre-existing `supersedes_observation` field is DEPRECATED.** Its description read "Reference to the prior observation this observation corrects", which is correction semantics carried in a supersession field. New records MUST use `corrects_observation_ref` for correction and the `dea:supersedes` relationship for supersession. The field is retained for one release cycle.
8. **A correction MUST NOT overwrite the original.** A corrected Observation carries a distinct value, `correction_reason`, and `corrects_observation_ref`; the original is retained with `observation_status: superseded`. An enforced by `test_section7_correction_never_overwrites_the_original`.
9. `dea:applies-period` is introduced (category `temporal`) connecting Measurement, MeasurementObservation, Baseline, PerformanceTarget, Threshold, PerformanceInterpretation, and IndicatorDesignation to the ReportingPeriod they report on.

## Consequences

- Positive: seven dimensions are separately addressable, so "when was this observed" and "when was this recorded" are answerable independently, which is what an audit needs.
- Positive: specializing `dea:TemporalInterval` means the interval clocks have one definition in the metamodel. A second interval entity would have created two answers to "what does valid_from mean".
- Positive: `dea:corrects` versus `dea:supersedes` makes the audit question "was the original wrong, or is there something newer" answerable from the graph rather than from a free-text reason.
- Positive: conditional period fields are machine-checkable. A rolling period missing its window is a conformance failure, not a reader's puzzle.
- Negative: the 9-field nested object is verbose on every Observation. For a high-frequency measurement this is real storage cost.
- Negative: `record_state` and `observation_status` are two parallel status vocabularies on the same entity. `observation_status` is CR-3R lifecycle; `record_state` is CR-MET-011 §7 record standing. They are related but not identical, and authors must reason about which they are setting.
- Negative: the deprecated `supersedes_observation` field remains for a release cycle, so during the migration both fields can be set inconsistently. Only the conformance test can catch that.
- Forecloses: seven referenced temporal entities (Position C). Five of the seven dimensions are facts about a single record, not objects with identity.
- Forecloses: `dea:EffectiveTime` as an entity.

## References

- CR-MET-011 (Temporal Semantics, Provenance and Historical Traceability).
- User-supplied CR-MET-011 §3 (7 temporal dimensions), §4 (period semantics), §7 (correction and supersession), §10 (architectural decision).
- CR-6 §5 (`dea:TemporalInterval`, multi-clock lineage).
- CR-MET-004 (`dea:supersedes` extension carrying Observation on both endpoints).
- `schemas/entities/reporting-period.json`, `schemas/entities/measurement-observation.json` (`temporal`, `record_state`).
- `metamodel/vocabularies/classifications.yaml`: `ReportingPeriod.period_type`, `.period_semantics`, `Measurement Observation.record_state`, `Provenance.temporal_dimension`.
- ADR-MET-010 (Measurement Evidence and Provenance).
- ADR-015 (kernel+specialization template).
- ADR-013 (Core non-accumulation).