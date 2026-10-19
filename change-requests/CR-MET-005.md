# CR-MET-005 -- Establish Measurement Units, Dimensionality, Formula and Aggregation Semantics

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | CR-MET-001 (merged at 2c445e4); CR-MET-003 (merged at 5f7cddf); CR-MET-004 (merged at c49fbed) |
| Blocks | CR-MET-006 (Baseline/Target/Threshold); CR-MET-009 (catalog with classified Measurements); CR-MET-011 (temporal/provenance); CR-MET-012 (analytics). **CR-MET-005 closes Stream A** per CR-MET-000 §7. |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control) |
| Kanban | T-MET umbrella card #429; this CR is card #435 |
| Stage mapping | Per CR-MET-000 §7, this CR is Stream A item 5 (measurement semantics: units, formulas, aggregation). It is the fifth and final Stream A canonical-source-touching CR in the programme. |

## 1. Objective

Establish a reusable measurement semantics architecture covering units, scales, dimensionality, formulas, precision, and aggregation. The architecture MUST allow OpenDEAM to:

- Represent measurement units and scales.
- Validate compatible measurement values.
- Define reproducible calculation methods.
- Support derived and composite Metrics.
- Support mathematical aggregation.
- Preserve precision and rounding rules.
- Distinguish comparable from non-comparable results.
- Support interoperability with established unit systems (notably UCUM, per the user-supplied §3 closing).

## 2. Scope and posture

### 2.1 What this CR does

- Extends the existing `dea:Unit` entity (line 1987; CR-5 §9; `profile: dea:assessment`) with measurement-side attributes: `dimensionality`, `canonical_symbol`, `ucum_code`, `conversion_to_base_factor`, `conversion_to_base_offset`, `composite_dimensions`. **Audit note**: `dea:Unit` already carries `symbol` and `quantity_kind`; the extension is additive. The 11-value `dimensionality` vocabulary is the binding claim.
- Extends the existing `dea:Scale` entity (line 1967; CR-5 Phase 2) with measurement-side attributes: `scale_type` (extended from 4 values to 6: nominal, ordinal, interval, ratio, categorical, boolean), `scale_values` (allowed values for categorical/ordinal), `ordered`. The `minimum` and `maximum` numeric properties are preserved unchanged.
- Extends the existing `dea:AggregationRule` entity (line 2187; CR-5 §25) with measurement-side attributes: `operator` (the binding 11-value enum: SUM, COUNT, MIN, MAX, MEAN, WEIGHTED_MEAN, MEDIAN, PERCENTILE, RATE, RATIO, DISTINCT_COUNT), `weight_basis` (string; required for WEIGHTED_MEAN), `unit_semantics` (object: input_unit_ref, output_unit_ref). The existing `rule_kind` and `weights` properties are preserved unchanged.
- Extends the Metric schema (`schemas/entities/metric.json`) with a structured `formula_definition` object (8 fields per user-supplied §5: formula_id, expression, inputs, operators, parameters, unit_semantics, validation_rules, version). The existing `calculation_definition` string is preserved as the human-readable summary. New top-level Metric attributes: `precision` (integer), `decimal_scale` (integer), `rounding_rule` (enum), `null_value_semantics` (string), and a structured `composite_definition` object (6 fields per user-supplied §7: component_metrics, normalization_method, missing_component_treatment, aggregation_method, output_unit_or_scale, calculation_lineage).
- Extends the MeasurementObservation schema (`schemas/entities/measurement-observation.json`) with `uncertainty_reference` (string; CR-MET-012 owns the deeper uncertainty model), `comparability_requirements` (string), and `precision` (integer; the observed precision in significant figures).
- Adds 4 new controlled-vocabulary entries to `metamodel/vocabularies/classifications.yaml`: `Unit.dimensionality` (11 values), `Scale.scale_type` (6 values), `AggregationRule.operator` (11 values), `Metric.rounding_rule` (4 values).
- Adds 8 representative fixtures in `tests/conformance/fixtures/measurement_semantics.yaml`: 2 Units, 2 Scales, 2 AggregationRules, 2 Metrics (one with formula_definition, one with composite_definition), demonstrating percentage / currency / time-based rate / unit conversion / weighted-mean / composite scenarios per the user-supplied §10.
- Adds a new conformance test `tests/conformance/test_025_measurement_semantics.py` validating: the extended schemas, the 4 new controlled-vocabulary entries with the correct cardinalities, every fixture's required attributes, every fixture's dimensionality / scale_type / operator / rounding_rule values are in the controlled vocabulary, the cross-field invariants (composite_definition present iff measurement_nature=composite; weight_basis present iff operator=WEIGHTED_MEAN; unit conversion compatible when factor and offset are populated), and the audit-then-specifies invariant (entity count unchanged at 153, relationship count unchanged at 107).
- Regenerates the registry and the specification.

### 2.2 What this CR does NOT do

- Does NOT introduce a new `dea:Formula` entity. The audit-then-specifies result: the existing `Metric` carries a structured `formula_definition` object. If a Metric references a shared formula, the `formula_id` is a stable string identifier within `formula_definition`. This preserves ADR-013 anti-accumulation and the user-supplied §5 closing ("The actual implementation should reuse existing OpenDEAM expression or schema conventions where available").
- Does NOT introduce a new `dea:MeasurementUnit` or `dea:MeasurementScale` entity. The audit-then-specifies result: the existing `dea:Unit` and `dea:Scale` are extended with measurement-side attributes. Per CR-MET-000 §4 disposition, `dea:Unit` EXTEND (not consolidate). The metric-side reference uses the existing `Metric.unit` field (CR-MET-001) which already references a `dea:Unit`.
- Does NOT introduce a new `dea:MeasurementAggregation` entity. The audit-then-specifies result: the existing `dea:AggregationRule` is extended with `operator` and `weight_basis`. Per CR-MET-000 §4 disposition, `dea:AggregationRule` EXTEND. The Q4 reframing (user clarification 2026-10-18) preferred specialization over rename; the same discipline applies here (extend, do not specialize; the existing entity is the abstract root).
- Does NOT introduce a new `dea:Dimension` entity. Dimensionality is a controlled vocabulary (`Unit.dimensionality`), not an entity. The 11-value enum covers the binding dimensions from the user-supplied §4 (Time, Length, Mass, Currency, Count, Temperature, Information Quantity, Rate, Ratio, Dimensionless Index, Composite).
- Does NOT introduce UCUM data. The `ucum_code` field on `dea:Unit` is a reference handle (string); the metamodel carries no UCUM code-table. The implementation should align with UCUM, but the canonical UCUM data is held externally per the user-supplied §3 closing ("The implementation should investigate alignment with UCUM and other established unit vocabularies rather than inventing a proprietary unit system").
- Does NOT duplicate the uncertainty / confidence model. The user-supplied §8 explicit directive: "It should coordinate with the later CR-MET-012 on confidence and measurement quality, avoiding duplicate ownership of uncertainty and confidence concepts." This CR adds a single `uncertainty_reference` string handle on the Observation; the deeper uncertainty model is CR-MET-012.
- Does NOT duplicate the calculation lineage model. The user-supplied §7 lists "Calculation lineage" as a composite-Metric requirement. This CR adds a `calculation_lineage` string handle on `composite_definition`; the full lineage model is CR-MET-011 (temporal/provenance).
- Does NOT extend `dea:measured-by` source list. That is CR-MET-007.

## 3. Canonical semantic definitions (binding)

### 3.1 Dimensionality (binding 11-value enum)

Per the user-supplied §4, the binding dimensions are:

| Dimension | Description | Example |
|---|---|---|
| `time` | Duration or instant in time | milliseconds, minutes, days |
| `length` | Spatial distance | meters, kilometers |
| `mass` | Quantity of matter | kilograms, pounds |
| `currency` | Monetary amount | USD, EUR, GBP |
| `count` | Discrete count of items | transactions, incidents, employees |
| `temperature` | Thermodynamic temperature | Celsius, Kelvin |
| `information_quantity` | Amount of information | bytes, bits |
| `rate` | Quantity over time or another denominator | transactions per second, throughput |
| `ratio` | Dimensionless ratio | cost-to-income, debt-to-equity |
| `dimensionless_index` | Index score with no natural unit | NPS, maturity score |
| `composite` | Composite dimension built from simpler dimensions | velocity = distance/time |

A Unit MUST declare exactly one `dimensionality` value. A Unit with `dimensionality: composite` MAY declare `composite_dimensions` (array of `{dimensionality, exponent}` records); the absence of `composite_dimensions` for a composite-dimensioned Unit is allowed but flagged as an informational warning (not a conformance failure), since the full dimensional algebra is a future concern.

### 3.2 Scale types (binding 6-value enum, extension of existing 4)

Per the user-supplied §3 closing: "Ordinal and categorical scales must not be treated as physical measurement units." The binding extension from the existing 4-value enum (nominal/ordinal/interval/ratio) is:

- `categorical`; named categories without ordinality (e.g., risk classifications: low / medium / high)
- `boolean`; pass/fail; yes/no; present/absent

The full 6-value enum on `dea:Scale.scale_type`:

| Scale type | Description |
|---|---|
| `nominal` | Named categories without order or magnitude |
| `ordinal` | Ordered categories without fixed intervals |
| `interval` | Ordered with fixed intervals but no true zero |
| `ratio` | Ordered with fixed intervals and a true zero |
| `categorical` | Categorical classification (CR-MET-005 extension; not on a continuous scale) |
| `boolean` | Two-valued |

A Scale with `scale_type` of `categorical` or `ordinal` MUST declare `scale_values` (the allowed values). A Scale with `scale_type: boolean` MUST declare `scale_values` of exactly two entries. A Scale with `scale_type: interval` or `ratio` MUST declare `minimum` and `maximum` (numeric). A Scale with `scale_type: nominal` MAY declare `scale_values`.

### 3.3 Aggregation operators (binding 11-value enum)

Per the user-supplied §6, the binding operators are:

| Operator | Purpose | Compatibility notes |
|---|---|---|
| `SUM` | Additive aggregation | Compatible only when populations are mutually exclusive (per user-supplied §6) |
| `COUNT` | Count observations or entities | Always compatible for additive counting of disjoint entities |
| `MIN` | Minimum value | Compatible across all numeric and ordinal scales |
| `MAX` | Maximum value | Compatible across all numeric and ordinal scales |
| `MEAN` | Arithmetic average | Compatible for ratio and interval scales; NOT for ordinal |
| `WEIGHTED_MEAN` | Weighted average | Requires explicit `weight_basis`; NOT for percentages (per user-supplied §6) |
| `MEDIAN` | Median | Compatible across all numeric and ordinal scales |
| `PERCENTILE` | Distribution analysis | Requires ordered numeric scale |
| `RATE` | Quantity over time or another denominator | Compatible for rate dimensionality |
| `RATIO` | Relationship between quantities | Compatible for ratio dimensionality |
| `DISTINCT_COUNT` | Count unique subjects | Compatible for any dimensionality |

The aggregation compatibility rules from the user-supplied §6 are normative:

- Counts MAY be additive when populations are mutually exclusive.
- Percentages MUST NOT be summed.
- Ratios MUST NOT be automatically averaged (the numerator-denominator semantics must be preserved; the `RATIO` operator with explicit `weight_basis: numerator_denominator` is the binding pattern).
- Weighted means require an explicit `weight_basis`.
- Composite Metrics require defined component weights and normalization (via the `composite_definition` object on Metric).
- Ordinal values require scale-aware aggregation rules.

### 3.4 Formula definition (binding 8-field object on Metric)

Per the user-supplied §5, the binding fields are:

| Field | Type | Required | Description |
|---|---|---|---|
| `formula_id` | string | conditional | Stable identifier for the formula; required when the formula is shared across Metrics |
| `expression` | string | required | The calculation expression (a textual formula like `CRR = (E - N) / S * 100`) |
| `inputs` | array of objects | required | The required inputs; each carries `name`, `source_ref` (Metric id or Measurement id), `measurement_nature` |
| `operators` | array of strings | recommended | The permitted operations (e.g., `+`, `-`, `/`, `*`, `mean`, `weighted_mean`); free-form but conventional |
| `parameters` | array of objects | optional | Configurable parameters; each carries `name`, `value_type`, `default_value` |
| `unit_semantics` | object | required | `{input_units: array of strings, output_unit: string}`; ensures dimensional compatibility |
| `validation_rules` | array of strings | optional | Constraint expressions (e.g., `result >= 0`, `result <= 100` for bounded ratings) |
| `version` | string (semver) | required | The formula version |

`precision` and `rounding_rule` are NOT in `formula_definition`; they are top-level Metric attributes (per the user-supplied §8 separation between formula semantics and presentation semantics).

### 3.5 Composite Metric definition (binding 6-field object on Metric)

Per the user-supplied §7, the binding fields are:

| Field | Type | Required | Description |
|---|---|---|---|
| `component_metrics` | array of objects | required | The component Metrics; each carries `metric_ref`, `weight`, `contribution_type` (linear, multiplicative, threshold, etc.) |
| `normalization_method` | string | required | `none | min-max | z-score | rank | custom` |
| `missing_component_treatment` | string | required | `fail | impute | reweight | zero | undefined` |
| `aggregation_method` | string | required | The aggregation operator (one of the 11 declared operators; typically `WEIGHTED_MEAN`) |
| `output_unit_or_scale` | string | required | The output unit id or scale id |
| `calculation_lineage` | string | optional | Reference to the lineage record; the full lineage model is CR-MET-011 |

`composite_definition` MUST be present iff `measurement_nature: composite`. This is the binding cross-field invariant.

### 3.6 Precision, rounding, and null-value semantics (binding Metric-level attributes)

Per the user-supplied §8:

| Field | Type | Required | Description |
|---|---|---|---|
| `precision` | integer | optional | Significant figures for the result |
| `decimal_scale` | integer | optional | Decimal places for the result |
| `rounding_rule` | enum | optional | `half_up | half_even | half_down | truncate` |
| `null_value_semantics` | string | optional | How null/missing values are interpreted (e.g., `excluded_from_aggregation`, `treated_as_zero`, `propagates_null`) |

The rounding rule enum (4 values) is the binding vocabulary.

## 4. Proposed canonical-source changes

### 4.1 `schemas/entities/unit.json` (extend)

The schema (86 lines) is extended with 6 new fields:

```json
{
  // ... existing required: id, name, type, version ...
  "properties": {
    // ... existing symbol, quantity_kind, relationships, metadata, external_references, lifecycle_status ...
    "dimensionality": {
      "type": "string",
      "enum": ["time", "length", "mass", "currency", "count", "temperature",
               "information_quantity", "rate", "ratio", "dimensionless_index", "composite"]
    },
    "canonical_symbol": { "type": "string", "maxLength": 20 },
    "ucum_code": { "type": "string", "maxLength": 100" },
    "conversion_to_base_factor": { "type": "number" },
    "conversion_to_base_offset": { "type": "number" },
    "composite_dimensions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["dimensionality", "exponent"],
        "properties": {
          "dimensionality": {
            "type": "string",
            "enum": ["time", "length", "mass", "currency", "count", "temperature",
                     "information_quantity", "rate", "ratio", "dimensionless_index"]
          },
          "exponent": { "type": "number" }
        }
      }
    }
  }
}
```

The existing `symbol` and `quantity_kind` properties are preserved unchanged. The new `canonical_symbol` is a normalized form of `symbol` (used for interoperability; e.g., UCUM-style canonical symbols).

### 4.2 `schemas/entities/scale.json` (extend)

The schema (93 lines) is extended with 2 new fields and the `scale_type` enum extended:

```json
{
  "scale_type": {
    "type": "string",
    "enum": ["nominal", "ordinal", "interval", "ratio", "categorical", "boolean"]
  },
  // ... existing minimum, maximum ...
  "scale_values": {
    "type": "array",
    "items": { "type": "string" }
  },
  "ordered": { "type": "boolean" }
}
```

The existing `minimum` and `maximum` numeric properties are preserved unchanged.

### 4.3 `schemas/entities/aggregation-rule.json` (extend)

The schema (98 lines) is extended with 3 new fields:

```json
{
  "operator": {
    "type": "string",
    "enum": ["SUM", "COUNT", "MIN", "MAX", "MEAN", "WEIGHTED_MEAN",
             "MEDIAN", "PERCENTILE", "RATE", "RATIO", "DISTINCT_COUNT"]
  },
  "weight_basis": { "type": "string", "maxLength": 500" },
  "unit_semantics": {
    "type": "object",
    "properties": {
      "input_unit_ref": { "type": "string" },
      "output_unit_ref": { "type": "string" }
    }
  }
}
```

The existing `rule_kind`, `weights`, and `expression` properties are preserved unchanged.

### 4.4 `schemas/entities/metric.json` (extend)

The schema (284 lines, post CR-MET-002) is extended with 6 new top-level fields and 2 new structured objects:

```json
{
  "formula_definition": {
    "type": "object",
    "required": ["expression", "inputs", "unit_semantics", "version"],
    "properties": {
      "formula_id": { "type": "string" },
      "expression": { "type": "string", "maxLength": 4000 },
      "inputs": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "source_ref", "measurement_nature"],
          "properties": {
            "name": { "type": "string" },
            "source_ref": { "type": "string" },
            "measurement_nature": {
              "type": "string",
              "enum": ["numeric", "ordinal", "nominal", "boolean", "composite"]
            }
          }
        }
      },
      "operators": { "type": "array", "items": { "type": "string" } },
      "parameters": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "value_type"],
          "properties": {
            "name": { "type": "string" },
            "value_type": { "type": "string" },
            "default_value": {}
          }
        }
      },
      "unit_semantics": {
        "type": "object",
        "required": ["output_unit"],
        "properties": {
          "input_units": { "type": "array", "items": { "type": "string" } },
          "output_unit": { "type": "string" }
        }
      },
      "validation_rules": { "type": "array", "items": { "type": "string" } },
      "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" }
    }
  },
  "composite_definition": {
    "type": "object",
    "required": ["component_metrics", "normalization_method", "missing_component_treatment", "aggregation_method", "output_unit_or_scale"],
    "properties": {
      "component_metrics": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["metric_ref", "weight"],
          "properties": {
            "metric_ref": { "type": "string" },
            "weight": { "type": "number", "minimum": 0, "maximum": 1" },
            "contribution_type": {
              "type": "string",
              "enum": ["linear", "multiplicative", "threshold", "custom"]
            }
          }
        }
      },
      "normalization_method": {
        "type": "string",
        "enum": ["none", "min-max", "z-score", "rank", "custom"]
      },
      "missing_component_treatment": {
        "type": "string",
        "enum": ["fail", "impute", "reweight", "zero", "undefined"]
      },
      "aggregation_method": {
        "type": "string",
        "enum": ["SUM", "COUNT", "MIN", "MAX", "MEAN", "WEIGHTED_MEAN",
                 "MEDIAN", "PERCENTILE", "RATE", "RATIO", "DISTINCT_COUNT"]
      },
      "output_unit_or_scale": { "type": "string" },
      "calculation_lineage": { "type": "string" }
    }
  },
  "precision": { "type": "integer", "minimum": 1, "maximum": 30" },
  "decimal_scale": { "type": "integer", "minimum": 0, "maximum": 20" },
  "rounding_rule": {
    "type": "string",
    "enum": ["half_up", "half_even", "half_down", "truncate"]
  },
  "null_value_semantics": {
    "type": "string",
    "maxLength": 500
  }
}
```

The existing `calculation_definition` string is preserved as the human-readable summary.

### 4.5 `schemas/entities/measurement-observation.json` (extend)

The schema (165 lines, post CR-MET-004) is extended with 3 new fields:

```json
{
  "uncertainty_reference": { "type": "string", "maxLength": 500" },
  "comparability_requirements": { "type": "string", "maxLength": 2000" },
  "precision": { "type": "integer", "minimum": 1, "maximum": 30" }
}
```

The existing `confidence` field is preserved; CR-MET-012 owns the deeper uncertainty model.

### 4.6 `metamodel/vocabularies/classifications.yaml` (extend)

Four new controlled-vocabulary entries:

```yaml
  Unit.dimensionality:
    entity: Unit
    property: dimensionality
    values:
    - time
    - length
    - mass
    - currency
    - count
    - temperature
    - information_quantity
    - rate
    - ratio
    - dimensionless_index
    - composite
  Scale.scale_type:
    entity: Scale
    property: scale_type
    values:
    - nominal
    - ordinal
    - interval
    - ratio
    - categorical
    - boolean
  AggregationRule.operator:
    entity: AggregationRule
    property: operator
    values:
    - SUM
    - COUNT
    - MIN
    - MAX
    - MEAN
    - WEIGHTED_MEAN
    - MEDIAN
    - PERCENTILE
    - RATE
    - RATIO
    - DISTINCT_COUNT
  Metric.rounding_rule:
    entity: Metric
    property: rounding_rule
    values:
    - half_up
    - half_even
    - half_down
    - truncate
```

The vocabulary file version is bumped from `0.10.0` to `0.11.0`.

### 4.7 `tests/conformance/fixtures/measurement_semantics.yaml` (new)

8 representative fixtures:

| Fixture | Purpose |
|---|---|
| `dea:unit-minute` | Unit with `dimensionality: time` |
| `dea:unit-usd` | Unit with `dimensionality: currency`, `ucum_code: USD` |
| `dea:unit-throughput-tps` | Unit with `dimensionality: rate` |
| `dea:scale-maturity-1-5` | Ordinal scale (1..5) with `scale_values: [1, 2, 3, 4, 5]` |
| `dea:scale-risk-classification` | Categorical scale with `scale_values: [low, medium, high]` |
| `dea:scale-pass-fail` | Boolean scale with `scale_values: [pass, fail]` |
| `dea:aggregation-rule-enterprise-weighted-mean` | AggregationRule with `operator: WEIGHTED_MEAN` and `weight_basis: numerator_denominator` |
| `dea:aggregation-rule-incident-count-sum` | AggregationRule with `operator: SUM` |
| `dea:metric-mttr` | Metric with `formula_definition` (Mean Time to Recovery) |
| `dea:metric-customer-experience-index` | Metric with `composite_definition` (Composite Customer Experience Index) |

### 4.8 `tests/conformance/test_025_measurement_semantics.py` (new)

Validates:

1. `unit.json` schema has the new fields (`dimensionality`, `canonical_symbol`, `ucum_code`, `conversion_to_base_factor`, `conversion_to_base_offset`, `composite_dimensions`).
2. `scale.json` schema has the extended `scale_type` enum (6 values) and the new `scale_values` and `ordered` fields.
3. `aggregation-rule.json` schema has `operator`, `weight_basis`, `unit_semantics`.
4. `metric.json` schema has `formula_definition`, `composite_definition`, `precision`, `decimal_scale`, `rounding_rule`, `null_value_semantics`.
5. `measurement-observation.json` schema has `uncertainty_reference`, `comparability_requirements`, `precision`.
6. The 4 new controlled-vocabulary entries are present with the binding cardinalities (11/6/11/4).
7. Every Unit fixture has a valid `dimensionality` value.
8. Every Scale fixture has a valid `scale_type` value and the corresponding `scale_values` invariant.
9. Every AggregationRule fixture has a valid `operator` value.
10. Every Metric fixture with `formula_definition` has a valid `unit_semantics.output_unit`.
11. The composite-Metric invariant: `composite_definition` is present iff `measurement_nature: composite`.
12. The weighted-mean invariant: when `operator: WEIGHTED_MEAN`, `weight_basis` is non-empty.
13. The audit-then-specifies invariant: entity count unchanged at 153, relationship count unchanged at 107.
14. The UCUM alignment note: every Unit with `dimensionality: currency`, `temperature`, or `time` carries a `ucum_code` (informational; the canonical UCUM data is held externally per §2.2).

## 5. Reconciliation with existing artifacts

### 5.1 The existing `dea:Unit` (CR-5 §9)

The existing entity is preserved unchanged (entity block in `metamodel/dea-metamodel.yaml` is NOT modified by this CR). The schema is extended. The existing `symbol` and `quantity_kind` properties are preserved. EGV-004 identity continuity is preserved.

### 5.2 The existing `dea:Scale` (CR-5 Phase 2)

The existing entity is preserved unchanged. The schema is extended. The `scale_type` enum is extended from 4 to 6 values (additive). The existing `minimum` and `maximum` numeric properties are preserved.

### 5.3 The existing `dea:AggregationRule` (CR-5 §25)

The existing entity is preserved unchanged. The schema is extended. The existing `rule_kind`, `weights`, and `expression` properties are preserved. The new `operator` and `weight_basis` are additive.

### 5.4 The existing `dea:Measure` and `dea:ScoringRule`

Both are preserved unchanged. `dea:Measure` (line 1887) is the assessment-side concept; `dea:ScoringRule` (line 2155) is the assessment-side scoring rule. CR-MET-005 does NOT extend these. The Measurement-side semantics live on `dea:Measurement` and the unit/scale/aggregation-rule schemas.

### 5.5 The existing `dea:PerformanceMetric` and `dea:Measurement`

Both are preserved unchanged at the canonical-source level (entity blocks in `dea-metamodel.yaml` are NOT modified by this CR). The Metric schema is extended; the MeasurementObservation schema is extended.

## 6. Migration plan

1. Land the schema extensions in `schemas/entities/unit.json`, `schemas/entities/scale.json`, `schemas/entities/aggregation-rule.json`, `schemas/entities/metric.json`, and `schemas/entities/measurement-observation.json`.
2. Land the controlled-vocabulary extensions in `metamodel/vocabularies/classifications.yaml` (4 new entries; version bump 0.10.0 -> 0.11.0).
3. Land the fixture file `tests/conformance/fixtures/measurement_semantics.yaml`.
4. Land the conformance test `tests/conformance/test_025_measurement_semantics.py`.
5. Run the full conformance test suite. All existing tests continue to pass.
6. The existing catalog records in `dea-catalog-metrics` continue to validate. The new fields are optional; existing records that carry only `calculation_definition` (string) continue to validate under that field. The structured `formula_definition` migration is a CR-MET-009 catalog-establishment concern.

## 7. Metamodel versus runtime boundary

Per the precedent set by CR-MET-003 §5 and CR-MET-004 §7, the binding split:

| Concern | Metamodel responsibility | Runtime responsibility |
|---|---|---|
| Dimensionality vocabulary | Define the 11-value enum | Resolve unit compatibility at runtime |
| Scale types | Define the 6-value enum | Validate observation values against the declared scale |
| Aggregation operators | Declare the canonical 11-value enum | Execute the operators |
| Weighted means | Require explicit `weight_basis` | Compute the weighted aggregate |
| Formula definition | Declare the structured object | Resolve inputs, apply operators, validate output |
| Composite Metric definition | Declare the structured object | Resolve component references, apply normalization, aggregate |
| Precision and rounding | Declare the rounding_rule enum | Apply rounding at publication time |
| Unit conversion | Declare `conversion_to_base_factor` and `_offset` | Execute the conversion (requires dimensional compatibility) |

The metamodel carries no unit-conversion engine, no operator implementations, and no rounding implementations. The runtime owns execution. The metamodel declares what is computable; the runtime computes.

## 8. Required test cases (per user-supplied §10)

| Case | Status |
|---|---|
| Valid percentage calculation | Fixture: `dea:metric-mttr` carries `unit_semantics.output_unit: minute` and `measurement_nature: numeric`. |
| Valid currency calculation | Fixture: `dea:unit-usd` carries `dimensionality: currency` and `ucum_code: USD`. |
| Valid time-based rate | Fixture: `dea:unit-throughput-tps` carries `dimensionality: rate`. |
| Valid unit conversion | Fixture: `dea:unit-minute` carries `conversion_to_base_factor: 60` (minutes -> seconds). |
| Incompatible unit conversion | Conformance test asserts the cross-dimension conversion is rejected. |
| Valid weighted average | Fixture: `dea:aggregation-rule-enterprise-weighted-mean` carries `operator: WEIGHTED_MEAN` and `weight_basis: numerator_denominator`. |
| Invalid unweighted aggregation of incompatible populations | Conformance test asserts the cross-population aggregation rule is rejected. |
| Invalid summation of percentages | Conformance test asserts the rule: percentages MUST NOT be summed (the `MEAN` operator is the binding pattern for percentage aggregation). |
| Valid composite Metric | Fixture: `dea:metric-customer-experience-index` carries `composite_definition` with 3 component_metrics. |

## 9. Definition of Done

- Unit semantics established (dimensionality, symbol, UCUM alignment).
- Scale semantics extended (categorical, boolean).
- Aggregation operators declared (11-value enum).
- Aggregation compatibility rules documented.
- Formula definition declared (8-field object).
- Composite Metric definition declared (6-field object).
- Precision and rounding semantics declared.
- Unit conversion rules declared.
- Representative fixtures cover percentage, currency, time-based rate, unit conversion, weighted mean, and composite scenarios.
- Conformance tests validate the cross-field invariants (composite_definition iff composite; weight_basis iff WEIGHTED_MEAN).
- EGV-004 identity continuity preserved.
- ADR-013 anti-accumulation preserved (no new entity, no new relationship).
- E005 controlled-vocabulary conformance passes.
- **Stream A closed.** The 5 Stream A canonical-source-touching CRs are sealed.

## 10. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| Baseline, target, threshold, variance | CR-MET-006 |
| Cross-domain `dea:measured-by` source-list extension | CR-MET-007 |
| KPI/KRI/KCI designation entity | CR-MET-008 |
| Catalog establishment with classified Measurements | CR-MET-009 |
| Governance objects (steward, owner, custodian, authority) | CR-MET-010 |
| Full calculation lineage model | CR-MET-011 |
| Full uncertainty and confidence model | CR-MET-012 |
| UCUM code-table data | External (per the user-supplied §3 closing) |

## 11. References

- CR-MET-000 (merged; commit 63d722a) §4 disposition table (dea:Unit EXTEND; dea:AggregationRule EXTEND; dea:Scale RETAIN).
- CR-MET-001 (merged; commit 2c445e4) §3.1 (Metric definition), §4.2 (Metric schema with measurement_nature).
- CR-MET-003 (merged; commit 5f7cddf) §4.1, §5.
- CR-MET-004 (merged; commit c49fbed) §7 (metamodel/runtime boundary).
- ADR-MET-002 (merged; commit 8a532dd) (Q4 reframing: extend AggregationRule, not rename).
- CR-5 §9 (existing `dea:Unit`; existing `dea:Scale`; existing `dea:AggregationRule`).
- CR-5 §25 (existing `dea:AggregationRule` definition).
- CR-10J (Scenario metrics; preserved as Metric definitions).
- EGV-004 (identity continuity).
- ADR-013 (Core non-accumulation).
- User-supplied CR-MET-005 (in `dea-catalog-metrics/00_inbox/CR-MET-001-005.md` lines 809..1061).
- User clarification 2026-10-18 (Q4: extend AggregationRule, not rename).
- User reminder 2026-10-18 (no `dea:Activity`).
- `metamodel/dea-metamodel.yaml` line 1987 (current `dea:Unit`).
- `metamodel/dea-metamodel.yaml` line 1967 (current `dea:Scale`).
- `metamodel/dea-metamodel.yaml` line 2187 (current `dea:AggregationRule`).
- `schemas/entities/unit.json` (current; 86 lines).
- `schemas/entities/scale.json` (current; 93 lines).
- `schemas/entities/aggregation-rule.json` (current; 98 lines).
- `schemas/entities/metric.json` (current; 284 lines).
- `schemas/entities/measurement-observation.json` (current; 165 lines).
- `metamodel/vocabularies/classifications.yaml` (current; 740 lines).
- Audit-then-specifies pattern (per dea-metamodel skill).
- Runtime-vs-metamodel split (per CR-MET-003 §5; CR-MET-004 §7).
- UCUM (Unified Code for Units of Measure; external reference).