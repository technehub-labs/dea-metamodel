# ADR-MET-016: Analytics is a semantic layer over measurements; correlation is never causation

- Status: Accepted (landed with CR-MET-012)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-012 (Measurement Analytics, Performance Intelligence and Decision Intelligence Integration)
- Supersedes: nothing
- Referenced by: CR-MET-012, ADR-MET-010, ADR-MET-013

## Context

User-supplied CR-MET-012 §12 is explicit: "OpenDEAM's Metric capability provides the semantic measurement foundation for enterprise decision intelligence. It should not absorb the responsibilities of analytical engines, forecasting platforms, or workflow orchestration systems."

The programme must nonetheless let an enterprise distinguish what was measured from what was inferred, predicted, simulated, or recommended. §7 states these "must not be conflated or published as equivalent measurement facts."

## Decision

1. **The metamodel provides the semantic foundation only.** It specifies no analytical engine, no forecasting platform, and no orchestration system. `dea:analyses-metric` records the semantic dependency between an analytical result and the measurement it draws on, not the engine that produced it.
2. **`dea:AnalyticalResult` carries a 4-value `result_type` enum: `estimate`, `forecast`, `simulation_result`, `recommendation`.** The pre-authored CR-MET-012 proposed 6 values including `observation` and `decision`. The audit reduced this to 4:
   - `observation` is already first-class as `dea:MeasurementObservation` (CR-MET-001). Including it would create a second identity for the same concept.
   - `decision` is already first-class as `dea:Decision` (CR-4 §13), carrying `statement`, `rationale`, `authority_ref`, `confidence`, `uncertainty`, `assumptions`. Absorbing it would conflate an **authorized management choice** with a **derived analytical output**.
   The §7 non-conflation requirement is therefore enforced **structurally**: those two types cannot appear as `result_type` values at all.
3. **`dea:informs-decision` makes the distinction explicit** without duplicating identity: a Recommendation informs a Decision; it does not become one. An analytical output is a derived artifact; an authorized management choice is a governance act with an accountable authority.
4. **Six analytical capabilities** are encoded as `AnalyticalResult.analytical_capability`: `descriptive`, `diagnostic`, `predictive`, `prescriptive`, `comparative`, `scenario_simulation`.
5. **Every analytical result MUST cite `evidence_refs`, MUST carry `provenance_reference` (ADR-MET-010), and MUST declare `confidence`.** An unsupported analytical output is not admissible; an unquantified one is not reviewable.
6. **`forecast` and `simulation_result` MUST declare `uncertainty`, `model_ref`, and `horizon_ref`.** A forward-looking output with no uncertainty statement is inadmissible. `simulation_result` MUST additionally declare the `scenario_ref` it is conditioned on.
7. **`recommendation` MUST carry `value: null` and MUST record `alternative_considered`.** A recommendation proposes an action rather than asserting a quantity, and a recommendation with no recorded alternatives is not auditable.
8. **`dea:Correlation` and `dea:CausalHypothesis` are BOTH first-class** (Q22c). The distinction is enforced structurally rather than by naming:
   - `dea:Correlation` carries a REQUIRED `confusion_guard` that MUST be `false`. A correlation asserts association only.
   - `dea:CausalHypothesis` requires a `mechanism` (a hypothesis without one is an assertion) plus a `validation_state` recording how far it was tested: `asserted`, `correlation_supported`, `experiment_running`, `validated`, `refuted`.
   - `dea:correlates` is **symmetric**, because correlation has no direction. `dea:tests-hypothesis` is directed from Correlation to CausalHypothesis.
   - A hypothesis MUST record `counter_evidence` and a `falsification_test`. A hypothesis with no recorded counter-evidence is either trivially true or not honestly recorded.
   - **A hypothesis's `confidence` MAY NOT exceed the absolute coefficient of its strongest supporting correlation.** A 0.63 correlation cannot license a 0.9 causal confidence.
9. `dea:Correlation` MUST record `method` and `sample_size` so the coefficient is reproducible, and MUST carry `confounder_candidates`. Absence of confounders is not evidence of their absence.
10. **`dea:derives-from` carries the evidence chain** (source gains `AnalyticalResult`, target gains `dea:MeasurementObservation`). `dea:produces` is deliberately NOT extended: an analytical output is not a produced measurement result.

## Consequences

- Positive: the §7 non-conflation requirement is a schema-level guarantee, not a convention. An `AnalyticalResult` with `result_type: decision` cannot be authored.
- Positive: the confidence ceiling on causal hypotheses is machine-checkable, so the most common analytical failure in enterprise programmes is prevented at authoring time.
- Positive: requiring `evidence_refs` on every result means an analytical claim can be traced to the Observations that produced it, which extends CR-MET-011 provenance into the analytics layer.
- Positive: `dea:correlates` being symmetric is correct and was almost certainly to be got wrong; correlation has no direction.
- Negative: requiring `uncertainty`, `model_ref`, and `horizon_ref` on forecasts is a heavy authoring burden, and a team under deadline pressure will find a way to satisfy it without genuinely quantifying uncertainty.
- Negative: the confidence ceiling is a coarse rule. A hypothesis supported by three independent correlations could legitimately carry confidence above any single coefficient. The rule errs toward blocking a defensible claim rather than admitting an indefensible one, which is the correct direction for this trade.
- Negative: requiring counter-evidence on every hypothesis means the negative list will often be padded with weak entries to satisfy the check.
- Forecloses: a `dea:AnalyticalService` entity. The analytical service is a runtime role, and `dea:analyses-metric` records the semantic dependency without creating identity for a component that is properly a deployment concern.
- Forecloses: collapsing Correlation and CausalHypothesis into one entity. The distinction is the point.
- Forecloses: an inference engine inside the metamodel.

## References

- CR-MET-012 (Measurement Analytics, Performance Intelligence and Decision Intelligence Integration).
- User-supplied CR-MET-012 §3 (six analytical capabilities), §7 (information types that must not be conflated), §11 (five reference scenarios), §12 (no absorption of engine responsibilities).
- `schemas/entities/analytical-result.json`, `correlation.json`, `causal-hypothesis.json`.
- `metamodel/vocabularies/classifications.yaml`: `AnalyticalResult.result_type`, `.analytical_capability`, `Correlation.strength`, `CausalHypothesis.validation_state`.
- CR-MET-001 (`dea:MeasurementObservation`), CR-4 §13 (`dea:Decision`).
- ADR-MET-010 (Measurement Evidence and Provenance).
- ADR-MET-013 (Composite Metrics and Aggregation).
- ADR-008 (Inference versus Authoritative Knowledge).
- ADR-013 (Core non-accumulation).