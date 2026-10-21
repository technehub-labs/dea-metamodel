# ADR-MET-013: Aggregation respects the CR-MET-005 rules; a plain average is not universal

- Status: Accepted (landed with CR-MET-005)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-005 (Measurement Semantics); reinforced by CR-MET-012 Q21a
- Supersedes: nothing
- Referenced by: CR-MET-005, CR-MET-012, ADR-MET-005

## Context

User-supplied CR-MET-012 §5 requires aggregation across enterprise structures (process into value stream, capability into business domain, business domain into enterprise, availability into service reliability, individual transformation outcomes into programme-level benefits), and states the binding constraint: "A simple arithmetic average must not be treated as a universal aggregation method."

This is the single most consequential rule in the measurement programme. An enterprise that averages its four business units' margins to report an enterprise margin produces a number that is arithmetically valid and analytically meaningless.

## Decision

1. **Aggregation reuses the existing `dea:AggregationRule`** (CR-MET-005). No `dea:AnalyticsAggregation` entity is introduced. The pre-authored CR-MET-000 Q4a proposed a `dea:MeasurementAggregation` specialization; the audit found `dea:AggregationRule` already carried `rule_kind`, `operator`, `weights`, and `expression`, so a second entity would have split one concept across two identities.
2. `dea:AggregationRule.operator` is the controlled 11-value set: `SUM`, `COUNT`, `MIN`, `MAX`, `MEAN`, `WEIGHTED_MEAN`, `MEDIAN`, `PERCENTILE`, `RATE`, `RATIO`, `DISTINCT_COUNT`.
3. `dea:AggregationRule.weight_basis` records what the weights represent. This is the field that makes ratio aggregation correct.
4. **The binding ratio rule:** a Metric of `ratio` or `dimensionless_index` dimensionality MUST NOT be aggregated by `SUM`. Where it must be combined across subjects, the aggregation MUST use `WEIGHTED_MEAN` with `weight_basis: numerator_denominator`.
5. **`AnalyticalResult.aggregation_rule_ref` is REQUIRED on every analytical result** (CR-MET-012 Q21a). An aggregate with no declared rule is inadmissible, which means "we just averaged it" must be written down and can then be reviewed.
6. A rollup across organizational units on a ratio-valued Metric MUST declare a weighted rule; the CR-MET-012 conformance suite asserts this directly.
7. `dea:AggregationRule.unit_semantics` records whether the operator is dimension-preserving. `SUM` over `count` is dimension-preserving; `SUM` over `ratio` is not.
8. Composite metrics carry `dea:Metric.composite_definition` (ADR-MET-006) declaring how sub-metric contributions combine. A composite Metric without a composite definition is a label, not a calculation.

## Consequences

- Positive: no new entity. One aggregation concept, one identity, one place to audit an aggregation decision.
- Positive: the ratio rule is machine-checkable. A conformance test can reject `SUM` over a ratio, which means the most common enterprise reporting error is prevented at the point of definition rather than discovered in an audit.
- Positive: `weight_basis` makes the reason for a weighting inspectable. "Weighted by revenue" and "weighted by headcount" produce different enterprise numbers, and the difference is now a recorded fact.
- Negative: the rule is a constraint on authors, and it will be resisted. A team reporting a simple average of unit-level percentages will need to compute it differently or record why the rule does not apply.
- Negative: `weight_basis` is a vocabulary value on the rule, not a validated derivation. Nothing verifies that the declared weights actually match the numerators and denominators.
- Negative: `unit_semantics` is a declaration. Whether `SUM` over a given operator is genuinely dimension-preserving is asserted by the author and trusted.
- Forecloses: `dea:MeasurementAggregation` and `dea:AnalyticsAggregation`. Both were rejected as a split of one concept.
- Forecloses: on-demand aggregation with no model entity. An unmodelled aggregation cannot be reviewed, and cannot be reproduced after the weights change.
- Forecloses: treating `MEAN` as a default.

## References

- CR-MET-005 (Measurement Semantics).
- CR-MET-012 Q21a (Aggregation rules).
- User-supplied CR-MET-012 §5 (cross-enterprise aggregation; the arithmetic-average prohibition).
- `schemas/entities/aggregation-rule.json` (`operator`, `weight_basis`, `unit_semantics`).
- `metamodel/vocabularies/classifications.yaml`: `AggregationRule.operator`, `AggregationRule.rule_kind`.
- `schemas/entities/analytical-result.json` (`aggregation_rule_ref`).
- ADR-MET-005 (Units and Dimensionality).
- ADR-MET-006 (Formula and Calculation Semantics).
- ADR-MET-016 (Metric Analytics and Decision Intelligence).
- ADR-013 (Core non-accumulation).