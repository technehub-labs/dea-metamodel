# ADR-MET-007: Baseline, Target, and Threshold are first-class; Variance is a derived view

- Status: Accepted (landed with CR-MET-006)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-006 (Performance Evaluation: Baselines, Targets, Thresholds and Interpretation)
- Supersedes: nothing
- Referenced by: CR-MET-006, ADR-MET-014

## Context

A measured value alone does not answer whether performance is acceptable. That judgement needs a reference point (a Baseline), an aspiration (a Target), a breach boundary (a Threshold), and a recorded judgement (an Interpretation).

The user-supplied CR-MET-006 §3 tabulates eight concepts and closes with an explicit caveat: a concept "should not automatically become separate entity types merely because they appear in this table." The pre-authored CR honoured that caveat for Benchmark and Expected Value but proposed four new entities.

Three positions were on the table:

- A: introduce new entities for every concept in the table.
- B: introduce entities only where the concept carries binding attributes the existing entities cannot absorb, and reuse existing entities otherwise.
- C: introduce no entities; represent all evaluation context as Metric attributes.

Position A violates ADR-013 by creating identity for concepts that are attributes of a comparison. Position C loses the auditable judgement record, which CR-MET-010 later requires at its Level 3 conformance.

## Decision

1. **Four new entities** are introduced by CR-MET-006, because each carries binding attributes that the existing assessment-side entities cannot absorb without identity fragmentation:
   - `dea:Baseline` (`dea:Baseline.kind`, 6 controlled values: `historical`, `initial`, `strategic`, `operational`, `regulatory`, `scenario_derived`; plus `approval_status`, 4 values).
   - `dea:PerformanceTarget` (`dea:PerformanceTarget.direction`, 5 controlled values: `increase`, `decrease`, `maintain`, `bounded`, `exact_match`; plus `approval_status`).
   - `dea:Threshold` (`dea:Threshold.level`, 4 values: `critical`, `warning`, `acceptable`, `optimal`; plus `dea:Threshold.direction`).
   - `dea:PerformanceInterpretation` (`dea:PerformanceInterpretation.kind`, 4 values: `variance_evaluation`, `threshold_evaluation`, `benchmark_evaluation`, `composite_judgment`; plus `dea:PerformanceInterpretation.state`).
2. **Benchmark reuses the existing `dea:BenchmarkReference`.** Per the user-supplied §3 caveat, a benchmark reference does not become a new entity type merely by appearing in a table. `dea:Benchmark` and `dea:BenchmarkPopulation` also already exist in the assessment lineage and are left unchanged.
3. **Expected Value is a property of `dea:PerformanceTarget.target_value`, not an entity.** It is the value the target states, not an independently identified object.
4. **Variance is a derived view, not an entity.** Variance is computed from an Observation, a Baseline, and a Target; it has no independent lifecycle. What must be auditable is not the arithmetic but *the judgement*, and `dea:PerformanceInterpretation` carries that.
5. **`dea:AssessmentTarget` is preserved unchanged.** It is a maturity-level target from the assessment lineage (CR-5 §21). `dea:PerformanceTarget` is a sibling for value-level targets. The two are not unified: a maturity level and a measured value are different kinds of target.
6. **Five new relationships** are introduced by CR-MET-006: `dea:references`, `dea:applies-subject`, `dea:specifies-target`, `dea:interprets`, `dea:has-target`. Two existing relationships are extended: `dea:constrains` gains `dea:Threshold` as a source and `dea:PerformanceMetric` as a target; `dea:benchmarked-against` gains `dea:PerformanceMetric` as a source.
7. A `dea:PerformanceInterpretation` that evaluates against a Threshold MUST cite the Threshold it evaluated. An interpretation with no cited reference is a bare opinion and is not admissible.

## Consequences

- Positive: four new entities carry genuinely independent lifecycle. A Target can be approved, revised, or retired without any change to the Metric it targets.
- Positive: `dea:PerformanceInterpretation` gives CR-MET-010 Level 3 conformance something to check. Governance conformance asserts owner, steward, approval, and lifecycle compliance; without a recorded judgement object there is nothing to audit.
- Positive: Benchmark introduces no new identity, honouring the user-supplied caveat directly.
- Negative: Variance is not addressable as a first-class record. To audit a variance you must reconstruct it from the Observation, Baseline, and Target. This is a deliberate trade: a stored Variance would go stale the moment any input is corrected.
- Negative: five new relationships is a real vocabulary cost, and `dea:references` in particular is generic enough that its reuse value should be reviewed at the next anti-accumulation review.
- Forecloses: one entity per concept in the §3 table (Position A). Particularly forecloses `dea:Benchmark` and `dea:ExpectedValue` as new entities.
- Forecloses: collapsing `dea:PerformanceTarget` into `dea:AssessmentTarget`. The distinction is preserved deliberately.

## References

- CR-MET-006 (Performance Evaluation).
- User-supplied CR-MET-006 §3 (the eight-concept table and its closing caveat).
- User-supplied CR-MET-006 §7 (Variance as a derived view).
- `schemas/entities/baseline.json`, `performance-target.json`, `threshold.json`, `performance-interpretation.json`.
- `metamodel/vocabularies/classifications.yaml`: `Baseline.kind`, `Baseline.approval_status`, `PerformanceTarget.direction`, `PerformanceTarget.approval_status`, `Threshold.level`, `Threshold.direction`, `PerformanceInterpretation.kind`, `PerformanceInterpretation.state`.
- CR-5 §21 (`dea:AssessmentTarget`, maturity-level targets).
- ADR-014 (Metric Governance and Lifecycle).
- ADR-013 (Core non-accumulation).