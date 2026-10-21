# ADR-MET-006: Formula semantics bind to the Metric, not to the runtime

- Status: Accepted (landed with CR-MET-005)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-005 (Measurement Semantics)
- Supersedes: nothing
- Referenced by: CR-MET-005, ADR-MET-011, ADR-MET-013

## Context

A Metric is only useful if the value it produces can be recomputed by someone who did not write the original definition. That requires the calculation to be part of the semantic definition rather than an implementation detail of whichever runtime happened to execute it.

The pre-authored CR-MET-000 Q4 offered three dispositions for calculation semantics:

- A: a `dea:Formula` entity.
- B: the formula is an attribute of `dea:Metric`, expressed as a structured `formula_definition`.
- C: formulas are runtime-owned; the metamodel records only that a calculation occurred.

Position C fails the historical-reconstruction requirement stated by CR-MET-011: if the formula lives only in the runtime, a Metric definition version cannot determine the value it once produced.

## Decision

1. The formula SHALL be an attribute of `dea:Metric`, carried as `formula_definition` with 8 properties: `formula_id`, `expression`, `inputs`, `operators`, `parameters`, `unit_semantics`, `validation_rules`, `version`.
2. `formula_definition.version` is REQUIRED. A formula without a version is not reproducible, because the definition may have changed since the value was produced.
3. `formula_definition.inputs` entries MUST carry `name` and `source_ref`. An input without a source reference is not a definition; it is an assumption.
4. `unit_semantics` MUST declare `output_unit` and SHOULD declare `input_units`. This is what binds the formula to ADR-MET-005: a formula that declares no output unit cannot be checked for dimensional consistency.
5. `validation_rules` carries the executable predicates that determine whether a produced value is admissible (for example `result >= 0`, `result <= 100`, `S > 0`).
6. `dea:Metric.composite_definition` carries the structure for a metric composed of sub-metrics. See ADR-MET-013.
7. A `dea:Measurement` records which `formula_id` and which `formula_definition.version` it executed; the `dea:Provenance` record (CR-MET-011) carries the same pin at 1:1 with the resulting Observation. The Metric holds the definition; the Provenance holds the attestation of what was actually used.
8. `dea:Metric.calculation_definition` is retained as the human-readable summary of `formula_definition`. The machine-readable form is binding; the summary is not. They may drift, and when they do the machine-readable form governs.

## Consequences

- Positive: a Metric definition version fully determines the value it produces, which is what makes CR-MET-011 historical reconstruction possible without recalculating every historical result.
- Positive: `validation_rules` makes "is this value admissible" a property of the definition rather than a per-runtime decision.
- Positive: no `dea:Formula` entity, so no new identity to manage and no new relationship vocabulary.
- Negative: the formula is stored as a structured blob rather than a queryable entity. Cross-Metric formula reuse cannot be discovered by the registry; it can only be detected by comparing `formula_id`.
- Negative: `expression` is carried as a string. Nothing in the metamodel validates that the expression parses or that it matches the declared `operators` and `inputs`. Expression well-formedness is a runtime responsibility.
- Forecloses: `dea:Formula` as a first-class entity. Should formula reuse across Metrics become a first-order concern, a `dea:specializes` relationship from a formula-bearing construct may be introduced under ADR-015, but not a parallel formula registry.
- Forecloses: runtime-owned formulas (Position C). This forecloses the CR-MET-011 provenance pin, which is the programme's central historical-traceability guarantee.

## References

- CR-MET-005 (Measurement Semantics).
- CR-MET-000 §4 (Q4a disposition: formula as a Metric attribute).
- `schemas/entities/metric.json` (`formula_definition`, `composite_definition`, `calculation_definition`).
- `schemas/entities/provenance.json` (`formula_version_ref`).
- ADR-MET-005 (Units and Dimensionality).
- ADR-MET-011 (Temporal Measurement Architecture).
- ADR-MET-013 (Composite Metrics and Aggregation).
- ADR-013 (Core non-accumulation).