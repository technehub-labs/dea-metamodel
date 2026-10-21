# ADR-MET-005: Units and dimensionality bind to the existing `dea:Unit`, `dea:Scale`, and `dea:AggregationRule`

- Status: Accepted (landed with CR-MET-005)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-005 (Measurement Semantics: Units, Dimensions, Formulas and Aggregation)
- Supersedes: nothing
- Referenced by: CR-MET-005, ADR-MET-006, ADR-MET-013

## Context

CR-MET-001 through CR-MET-004 established that Metric, Measurement, and MeasurementObservation exist, that Metrics carry a six-axis classification (CR-MET-002), and that a Measurement has a governed lifecycle (CR-MET-004). None of those slices bound the *quantity semantics*: what a measured value means physically, which units it may be expressed in, whether those units are commensurable, and how several measurements combine into one.

The pre-authored CR-MET-005 offered three dispositions for units and aggregation:

- A: introduce new entities `dea:MeasurementUnit` and `dea:MeasurementAggregation`.
- B: audit the existing `dea:Unit`, `dea:Scale`, `dea:AggregationRule` and extend them in place.
- C: leave units and aggregation to the runtime and specify nothing.

## Decision

1. `dea:Unit`, `dea:Scale`, and `dea:AggregationRule` already exist and already carry the binding semantics through `quantity_kind`, `scale_type`, `minimum`, `maximum`, `scale_values`, `rule_kind`, and `weights`. Position B is adopted: **zero new entities and zero new relationships** are introduced by CR-MET-005.
2. `dea:Unit` gains the following properties, which together make unit arithmetic well-defined:
   - `dimensionality` (11 controlled values, extended from 4 by CR-MET-005): `time`, `length`, `mass`, `currency`, `count`, `temperature`, `information_quantity`, `rate`, `ratio`, `dimensionless_index`, `composite`.
   - `canonical_symbol`, `ucum_code`: the canonical spelling and the Unified Code for Units of Measure identifier, so a unit is interoperable outside OpenDEAM.
   - `conversion_to_base_factor`, `conversion_to_base_offset`: the affine conversion to the canonical base unit. Without these, two units of the same dimensionality are merely *commensurable*, not *convertible*.
   - `composite_dimensions`: for a derived quantity such as velocity or throughput, the dimensions it is composed of.
3. `dea:Scale.scale_type` is extended from 4 to 6 controlled values: `nominal`, `ordinal`, `interval`, `ratio`, `categorical`, `boolean`. `categorical` and `boolean` are separated because a boolean admits arithmetic that an ordered category does not.
4. `dea:AggregationRule` gains `operator` (11 controlled values: `SUM`, `COUNT`, `MIN`, `MAX`, `MEAN`, `WEIGHTED_MEAN`, `MEDIAN`, `PERCENTILE`, `RATE`, `RATIO`, `DISTINCT_COUNT`), `weight_basis`, and `unit_semantics`.
5. `dea:Unit` for any given dimensionality MUST declare `canonical_symbol`. A Metric that references a unit without a dimensionality is not semantically conformant.
6. Conversion between two units of the *same* dimensionality MUST use `conversion_to_base_factor` and `conversion_to_base_offset`. Conversion between units of *different* dimensionality is forbidden; it is a category error, not an approximation.
7. A `ratio` or `dimensionless_index` dimensionality MUST NOT be aggregated by `SUM`. A ratio that must be combined across units MUST use `WEIGHTED_MEAN` with an explicit `weight_basis` of `numerator_denominator`. This is the binding financial-ratio rule (see ADR-MET-013).
8. `dea:Metric` gains `precision`, `decimal_scale`, and `rounding_rule` (4 controlled values: `half_up`, `half_even`, `half_down`, `truncate`), plus `null_value_semantics`. A Metric that does not declare how nulls aggregate will silently produce a wrong total.

## Consequences

- Positive: zero new entities and zero new relationships. ADR-013 anti-accumulation is preserved at 153 entities and 107 relationships for this slice.
- Positive: unit arithmetic is now decidable. A conformance test can state that summing a ratio is invalid, rather than leaving it to a reader.
- Positive: `ucum_code` makes the unit vocabulary interoperable with the external measurement ecosystem.
- Negative: `dea:Unit` grows from 5 to 13 properties. The Unit vocabulary now requires a canonical symbol to be useful, which is a real authoring burden for a catalogue that previously only needed a label.
- Negative: forbidding cross-dimensionality conversion is a constraint. A runtime that previously converted freely now has to convert through the canonical base unit explicitly.
- Forecloses: `dea:MeasurementUnit` (Position A). A measurement-side unit variant would fragment a unit whose meaning is physical, not architectural; if a future slice needs a unit variant it MUST use `dea:specializes` (ADR-015).
- Forecloses: deferring units to the runtime (Position C). Without declared dimensionality and conversion factors, a runtime cannot aggregate correctly without out-of-band configuration, which would make results non-reproducible across runtimes.

## References

- CR-MET-005 (Measurement Semantics).
- `schemas/entities/unit.json` (CR-MET-005 extension).
- `schemas/entities/scale.json` (CR-MET-005 extension; `scale_type` 4 to 6).
- `schemas/entities/aggregation-rule.json` (CR-MET-005 extension).
- `metamodel/vocabularies/classifications.yaml`: `Unit.dimensionality`, `Scale.scale_type`, `AggregationRule.operator`, `Metric.rounding_rule`.
- ADR-MET-006 (Formula and Calculation Semantics).
- ADR-MET-013 (Composite Metrics and Aggregation).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).
- Unified Code for Units of Measure (UCUM).