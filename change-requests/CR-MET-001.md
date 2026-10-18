# CR-MET-001 -- Establish Metric as a First-Class OpenDEAM Metamodel Entity

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | CR-MET-000 reconciliation (merged at commit 63d722a on main); ADR-MET-001 (merged at 8a532dd on main); ADR-MET-002 (merged at 8a532dd on main) |
| Blocks | CR-MET-002 (classification); CR-MET-003 (Measurement and Observation entities); CR-MET-007 (cross-domain relationships); CR-MET-008 (IndicatorDesignation); CR-MET-009 (catalog); CR-MET-010 (governance); CR-MET-011 (temporal/provenance); CR-MET-012 (analytics) |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control); dea-catalog-metrics (reusable definitions) |
| Kanban | T-MET umbrella card #429; this CR is card #431 |
| Stage mapping | Per CR-MET-000 §7, this CR is Stream A item 1 (semantic foundation, canonical entity). It is the FIRST canonical-source-touching CR in the programme after CR-MET-000 reconciliation. |

## 1. Objective

Establish Metric as a first-class, independently identifiable, reusable semantic entity in the OpenDEAM metamodel. The entity MUST describe what is intended to be measured, the measurement's semantic meaning, how the metric is determined, its measurement unit or scale, its source or method, and its association with enterprise entities. The entity MUST support reusable definitions across multiple contexts, versioning, and governance. The entity MUST remain independent of any specific performance-management framework.

The Metric definition is the binding point for the rest of the programme: CR-MET-002 (classification), CR-MET-003 (Measurement and Observation entities), CR-MET-007 (cross-domain relationships), CR-MET-008 (IndicatorDesignation), and CR-MET-009 (catalog establishment) all reference this CR's entity specification.

## 2. Scope and posture

### 2.1 What this CR does

- Promotes the existing `dea:PerformanceMetric` declaration to a foundational scope per ADR-MET-001.
- Replaces the MECE-only `metric_type` (kpi | health | maturity | performance | adoption | compliance | risk) with the binding six-dimensional classification axes (subject, purpose, orientation, nature, scope, management significance) per ADR-MET-003 and CR-MET-002.
- Adds `dea:Measurement` and `dea:MeasurementObservation` as new first-class entities per ADR-MET-002 (siblings of the existing assessment-side `dea:Observation`; no re-membership, no supersession).
- Extends the JSON schema `schemas/entities/metric.json` to express the binding attribute set.
- Extends the JSON schema registry to declare the new entity schemas `schemas/entities/measurement.json` and `schemas/entities/measurement-observation.json` (placeholders; the full CR-MET-003 attributes land in the next CR).
- Extends the conformance tests to validate the new schema, the new attributes, and the orthogonal-dimension allocation.
- Updates the entity registry regeneration to include the new entity declarations.

### 2.2 What this CR does NOT do

- Does NOT introduce a new `dea:Metric` root. The existing `dea:PerformanceMetric` is re-membershiped, not paralleled.
- Does NOT deprecate any existing entity. EGV-004 identity continuity is preserved.
- Does NOT introduce a new `dea:Activity`. The existing `dea:BusinessProcess` decomposition is the activity-level path (per user reminder 2026-10-18).
- Does NOT touch the IndicatorDesignation entity. That is CR-MET-008.
- Does NOT extend `dea:measured-by` source list. That is CR-MET-007.
- Does NOT add governance objects. That is CR-MET-010.
- Does NOT add temporal/provenance/analytics. That is CR-MET-011 and CR-MET-012.

## 3. Canonical semantic definition (binding text)

### 3.1 `dea:PerformanceMetric` (extended; re-membershiped to foundational scope)

> A Metric is a formally defined, reusable semantic specification that describes a measurable property, characteristic, condition, quantity, rate, ratio, index, or other observable aspect of a subject, including the semantic rules necessary to determine and interpret its value.
>
> A Metric defines what is to be measured and the rules governing its determination. It does not, by itself, represent a measurement execution or an observed result. This distinction is normative.
>
> A Metric is foundational: it is not allocated to a single profile. It is reified across the `measurement-dimension` orthogonal allocator (per ADR-0002 D1) and may be referenced from any profile (assessment, business, digital, technology, governance) where measurement is in scope.
>
> A Metric MUST have a stable identity independent of its name. A Metric MUST have an unambiguous definition. A Metric MUST identify the subject concept it measures. A Metric MUST declare an appropriate measurement nature (numeric, ordinal, nominal, boolean, or composite). Numeric Metrics MUST define or reference a compatible unit or scale. Formula-based Metrics MUST have an explicit calculation definition. Qualitative Metrics MUST NOT be forced into numeric measurement semantics. A Metric MUST NOT contain individual observation values. A Metric MUST NOT contain operational measurement history.

### 3.2 `dea:Measurement` (new first-class entity)

> A Measurement is the execution or application of a Metric to a particular subject, within a defined context, using an identified measurement method and applicable configuration.
>
> A Measurement reifies the act of measuring: it carries the `applies-metric` reference to the Metric definition version applied, the `measures-subject` reference to the entity that was measured, the temporal context, the responsible party, and any configuration parameters necessary to reproduce the result. A Measurement MAY produce zero or more Observations (zero when the measurement failed, was cancelled, or was otherwise incomplete).
>
> A Measurement is distinct from a Metric. A Measurement is also distinct from a MeasurementObservation: the Measurement is the act; the MeasurementObservation is the recorded result.

### 3.3 `dea:MeasurementObservation` (new first-class entity)

> A MeasurementObservation is the recorded result of a Measurement. It captures the resulting value, the unit, the temporal context of the value (when the value was obtained), the confidence (if applicable), and the provenance reference.
>
> A MeasurementObservation is a sibling of the existing assessment-side `dea:Observation` (CR-5 §27; line 1855). The two are distinct concepts on the assessment-vs-measurement axis and MUST NOT be merged, re-membershiped, or supersed-ed. The existing `dea:Observation` remains in `profile: dea:assessment` unchanged and continues to be the assessment-side INPUT concept.
>
> A MeasurementObservation is a sibling, not a specialization, of `dea:Observation`; the `dea:Observation` id is preserved for the assessment-side concept per the user clarification 2026-10-18.

### 3.4 Existing `dea:Observation` (unchanged)

> A raw measured or observed fact collected as input to assessment (CR-5 §27).

This declaration is NOT modified by this CR.

## 4. Proposed canonical-source changes

### 4.1 `metamodel/dea-metamodel.yaml` changes

The `dea:PerformanceMetric` block (line 1519) is modified in three respects:

1. The `definition` field is updated to the binding text in §3.1.
2. The `membership` block is changed from `kind: profile / profile: dea:assessment` to `kind: core / profile: null` per ADR-MET-001 decision 1.
3. The `legacy_ids` field is extended with the CR-10J Scenario metrics identifier if not already present.

The `dea:Measurement` block is added in the entity registry in the existing abstract-entity ordering (after `dea:BusinessProcess`; before `dea:Information`).

The `dea:MeasurementObservation` block is added in the entity registry in the existing concrete-entity ordering (after `dea:Observation`; before `dea:Measure`).

The `dea:Observation` block is NOT modified.

#### 4.1.1 `dea:PerformanceMetric` (re-membershiped, extended)

```yaml
- id: dea:PerformanceMetric
  name: Performance Metric
  legacy_ids:
  - dea:entity-metric
  - Metric
  - CR-10J:scenario-metric
  definition: |
    A formally defined, reusable semantic specification that describes a measurable
    property, characteristic, condition, quantity, rate, ratio, index, or other
    observable aspect of a subject, including the semantic rules necessary to
    determine and interpret its value. A Metric defines what is to be measured
    and the rules governing its determination. It does not, by itself, represent
    a measurement execution or an observed result. A Metric is foundational:
    it is reified across the measurement-dimension orthogonal allocator
    (per ADR-0002 D1) and may be referenced from any OpenDEAM profile where
    measurement is in scope. A Metric MUST have a stable identity independent
    of its name; MUST have an unambiguous definition; MUST identify its subject
    concept; MUST declare an appropriate measurement nature; MUST define or
    reference a compatible unit or scale (numeric metrics); MUST have an
    explicit calculation definition (formula-based metrics); MUST NOT force
    qualitative metrics into numeric measurement semantics; MUST NOT contain
    individual observation values; and MUST NOT contain operational measurement
    history. (CR-MET-001, binding CR-MET-000 reconciliation and ADR-MET-001.)
  layer: null
  dimension: measurement-dimension
  building_block: null
  abstract: false
  status: normative
  lifecycle: existing
  class_alias: MTR
  catalog_repo: dea-catalog-metrics
  artifacts:
    json_schema: schemas/entities/metric.json
    sqlite_table: metrics
    pydantic_model: pydantic/metric.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: core
    profile: null
```

Diff summary (for review):
- `legacy_ids` appended: `- CR-10J:scenario-metric`.
- `definition` field updated to the binding text in §3.1.
- `membership.kind: profile / profile: dea:assessment` replaced with `membership.kind: core / profile: null`.
- All other fields preserved: `id`, `name`, `layer`, `dimension`, `building_block`, `abstract`, `status`, `lifecycle`, `class_alias`, `catalog_repo`, `artifacts`.

#### 4.1.2 `dea:Measurement` (new first-class entity)

```yaml
- id: dea:Measurement
  name: Measurement
  legacy_ids: []
  definition: |
    The execution or application of a Metric to a particular subject, within
    a defined context, using an identified measurement method and applicable
    configuration. A Measurement carries the applies-metric reference to the
    Metric definition version applied, the measures-subject reference to the
    entity that was measured, the temporal context, the responsible party, and
    any configuration parameters necessary to reproduce the result. A
    Measurement MAY produce zero or more MeasurementObservations. (CR-MET-001
    binding ADR-MET-002; full attribute set in CR-MET-003.)
  layer: null
  dimension: measurement-dimension
  building_block: null
  abstract: false
  status: normative
  lifecycle: new
  class_alias: MMT
  catalog_repo: null
  artifacts:
    json_schema: schemas/entities/measurement.json
    sqlite_table: measurements
    pydantic_model: pydantic/measurement.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: core
    profile: null
```

#### 4.1.3 `dea:MeasurementObservation` (new first-class entity)

```yaml
- id: dea:MeasurementObservation
  name: Measurement Observation
  legacy_ids: []
  definition: |
    The recorded result of a Measurement. Captures the resulting value, the
    unit, the temporal context of the value (when the value was obtained), the
    confidence (if applicable), and the provenance reference. A
    MeasurementObservation is a sibling of the existing assessment-side
    dea:Observation (CR-5 27). The two are distinct concepts on the
    assessment-vs-measurement axis and MUST NOT be merged, re-membershiped,
    or supersed-ed. (CR-MET-001 binding ADR-MET-002; user clarification
    2026-10-18; full attribute set in CR-MET-003.)
  layer: null
  dimension: measurement-dimension
  building_block: null
  abstract: false
  status: normative
  lifecycle: new
  class_alias: MOBS
  catalog_repo: null
  artifacts:
    json_schema: schemas/entities/measurement-observation.json
    sqlite_table: measurement_observations
    pydantic_model: pydantic/measurement_observation.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: core
    profile: null
```

#### 4.1.4 `dea:Observation` (unchanged)

The existing `dea:Observation` block is NOT modified. The block (line 1855) remains as-is, in `profile: dea:assessment`, with its CR-5 §27 definition.

### 4.2 `schemas/entities/metric.json` changes

The existing `metric.json` schema (166 lines; current `metric_type` enum `kpi | health | maturity | performance | adoption | compliance | risk`) is extended as follows:

1. The top-level `description` is updated to reference CR-MET-001 and ADR-MET-001 binding.
2. The `metric_type` enum is REPLACED with a six-axis classification block: `subject_classification`, `purpose_classification`, `orientation_classification`, `scope_classification`, `management_significance_designation` (per CR-MET-002 / CR-MET-008), and `measurement_nature` (per CR-MET-001). The MECE-only enum is preserved as a deprecated informational field `legacy_metric_type` for one release cycle to allow existing catalog records to migrate.
3. New required attribute: `subject_concept` (a string; the type of phenomenon or property measured; the binding replacement for the implicit subject field that the old MECE enum buried).
4. New required attribute: `measurement_nature` (an enum: `numeric | ordinal | nominal | boolean | composite`; normative per CR-MET-001 §3.1).
5. New optional attribute: `directionality` (an enum: `higher_is_better | lower_is_better | target_is_better | nominal`; per CR-MET-001 §4 of the user-supplied spec).
6. New optional attribute: `measurement_method` (already present; preserved with an updated `maxLength` of 2000 to match the user-supplied spec's `measurement_method` requirement).
7. New optional attribute: `calculation_definition` (a string with `maxLength` 2000; carries the formula or computational definition; normative for formula-based metrics).
8. The `owner` and `steward` governance fields are NOT added in this CR. They are owned by CR-MET-010 (governance objects). The existing test E003 (no undeclared relationship-state in entity schemas) bans `owner` as a top-level field, so adding it here would fail the conformance suite. The CR-MET-001 doc's §4 of the user-supplied spec lists owner and steward as Governance-controlled; the binding implementation lands in CR-MET-010.

The `legacy_metric_type` field (preserved for one release cycle) is `metric_type` with the existing MECE enum plus the value `metric_type_deprecated_marker` (a sentinel that downstream validators treat as a warning, not a hard error). After the deprecation window closes, the `metric_type` field is removed in a subsequent CR (CR-MET-013 closure CR is the natural home).

The required attributes after this CR: `id`, `name`, `type`, `version`, `subject_concept`, `measurement_nature`. The previously required `metric_type` and `unit` are downgraded to optional: `metric_type` becomes `legacy_metric_type` (informational, deprecated); `unit` becomes optional and is governed by CR-MET-005 (units, formulas, aggregation).

This is the minimum extension to land the binding attribute set per the user-supplied CR-MET-001 §4. The full classification axis values (six dimensions of values) are added in CR-MET-002 (the next CR in the stream).

### 4.3 `schemas/entities/measurement.json` (new)

A new placeholder schema. The schema contains the minimum required attributes for `dea:Measurement`: `id`, `name`, `type`, `version`, `applies_metric` (reference to a `dea:PerformanceMetric`), `measures_subject` (reference to any eligible enterprise entity per the same source list as `dea:measured-by`), `temporal` (placeholder object; full spec in CR-MET-004), `responsible_party` (placeholder string; full spec in CR-MET-010), and `configuration` (placeholder object; full spec in CR-MET-003). The `applies_metric` and `measures_subject` are the binding relationships per ADR-MET-002 decisions 6 and 7.

The full attribute set (governance, temporal, provenance, analytics) lands in CR-MET-003, CR-MET-004, and CR-MET-011 as the corresponding CRs are merged.

### 4.4 `schemas/entities/measurement-observation.json` (new)

A new placeholder schema. The schema contains the minimum required attributes for `dea:MeasurementObservation`: `id`, `name`, `type`, `version`, `produces` (implicit; the MeasurementObservation is the result of a Measurement; the relationship is `dea:produced-by` from the observation to the measurement; cardinality 1:0..1), `value` (typed as `number | string | boolean | object` to support the four measurement natures), `unit` (optional string; cross-reference to the unit registry per CR-MET-005), `temporal` (placeholder object; full spec in CR-MET-011), and `confidence` (optional number 0..1).

The full attribute set lands in CR-MET-003 and CR-MET-011.

### 4.5 Conformance test changes

A new test file `tests/conformance/test_021_metric_canonical_entity.py` is added. The test validates:

1. `dea:PerformanceMetric` is present with `membership.kind: core / profile: null` (re-membership).
2. `dea:PerformanceMetric.legacy_ids` includes `CR-10J:scenario-metric`.
3. `dea:PerformanceMetric.definition` matches the binding text in §3.1 (a contains check; the binding text is the canonical string).
4. `dea:PerformanceMetric.dimension: measurement-dimension` (orthogonal allocator).
5. `dea:Measurement` is present with `membership.kind: core / profile: null`.
6. `dea:MeasurementObservation` is present with `membership.kind: core / profile: null`.
7. `dea:Observation` is unchanged (its `membership.kind: profile / profile: dea:assessment` is preserved).
8. `schemas/entities/metric.json` declares `subject_concept` as required.
9. `schemas/entities/metric.json` declares `measurement_nature` as required.
10. `schemas/entities/measurement.json` exists with `applies_metric` and `measures_subject` references.
11. `schemas/entities/measurement-observation.json` exists with `value` and `produces` references.
12. No entity in the registry has `metric_type: <value>` where `<value>` is in the old MECE enum (`kpi | health | maturity | performance | adoption | compliance | risk`) AS THE NORMATIVE type. The `metric_type` field is preserved as `legacy_metric_type` with a deprecation marker, but the normative type is now `subject_concept + measurement_nature`.

The test follows the existing `tests/conformance/test_009_entity_rules.py` style (CR-3 §24; E001-E010).

## 5. Reconciliation with existing artifacts

### 5.1 CR-10J Scenario metrics

The CR-10J Scenario metrics identifier is added to `dea:PerformanceMetric.legacy_ids` as `CR-10J:scenario-metric`. The CR-10J Scenario metrics' definition, unit, calculation, source, baseline, target fields are preserved through the schema's existing `definition`, `unit`, `measurement_method`, `calculation_definition`, `measurement_source`, `baseline_value`, `target_value` attributes. No CR-10J record is lost.

### 5.2 CR-10 Outcome references

The CR-10 Outcome concept's metric-related references (baseline, expected outcome, target, unit, confidence, timeframe, evidence) are preserved per CR-MET-000 §4 disposition (`dea:Outcome` RETAIN). The `Metric` is now referenceable from `dea:Outcome` via the existing `dea:assesses` / `dea:assessed-by` vocabulary. No Outcome record is lost.

### 5.3 Existing catalog records

Existing catalog records in `dea-catalog-metrics` referencing `dea:PerformanceMetric` (e.g. `dea:metric-api-adoption-rate` shown in the schema's `examples` array) continue to validate. The `legacy_metric_type` field preserves the MECE enum values, so existing records that carry `metric_type: kpi | health | maturity | performance | adoption | compliance | risk` continue to validate under the legacy field. They are not required to migrate to the new six-axis classification in this CR; that migration is part of CR-MET-002 (next) and the pilot tranche (CR-MET-009).

### 5.4 Existing relationships

The `dea:measured-by` relationship (line 4612) is preserved unchanged. Its source-list extension is owned by CR-MET-007 (per ADR-MET-004). No relationship is added in this CR; the `applies_metric` and `measures_subject` references in the new schemas are field-level references, not new registry relationships, until CR-MET-003 (which adds `dea:produces`, `dea:applies-metric`, `dea:measures-subject` per ADR-MET-002 decisions 5, 6, 7).

## 6. Migration plan

1. Land the canonical-source changes in `metamodel/dea-metamodel.yaml` (3 blocks: dea:PerformanceMetric, dea:Measurement, dea:MeasurementObservation).
2. Land the schema changes in `schemas/entities/metric.json` (extend), `schemas/entities/measurement.json` (new), `schemas/entities/measurement-observation.json` (new).
3. Land the conformance test in `tests/conformance/test_021_metric_canonical_entity.py`.
4. Regenerate the entity registry from the canonical source.
5. Run the full conformance test suite. All existing tests continue to pass (EGV-004).
6. Existing catalog records validate unchanged.
7. The `metric_type` deprecation window begins: the field is preserved as `legacy_metric_type` for one release cycle. After the window, the field is removed in a subsequent CR.

## 7. Required test cases (per user-supplied CR-MET-001 §8)

| Case | Status |
|---|---|
| Valid quantitative Metric | Reused via existing conformance test; new test validates `measurement_nature: numeric` + `unit` reference. |
| Valid percentage Metric | Reused; new test validates `measurement_nature: numeric` + `unit: %`. |
| Valid qualitative Metric | New test; validates `measurement_nature: nominal` + no `unit` required. |
| Valid ordinal Metric | New test; validates `measurement_nature: ordinal` + optional unit. |
| Metric without a calculation definition | New test; validates the metric is rejected if `measurement_nature: numeric` and `calculation_definition` is missing. |
| Metric with an invalid measurement nature | New test; validates the `measurement_nature` enum. |
| Metric without a subject concept | New test; validates `subject_concept` is required. |
| Duplicate identifier | Reused via E001 (existing test). |
| Same name with different semantic definitions | Reused via E002 (existing test). |
| Metric linked to multiple enterprise entities | Reused via existing relationship test; full source list extension is CR-MET-007. |
| Metric referencing a deprecated unit | Reused via existing unit test; full unit deprecation is CR-MET-005. |
| Metric containing an observation value | New test; validates the metric is rejected if it contains a `value` field (the binding text in §3.1 prohibits this). |

## 8. Definition of Done

- Canonical Metric semantics approved.
- Existing CR-10J work reconciled.
- `dea:PerformanceMetric` re-membershiped to foundational scope per ADR-MET-001.
- `dea:Measurement` and `dea:MeasurementObservation` introduced per ADR-MET-002.
- Existing `dea:Observation` unchanged.
- New schemas `measurement.json` and `measurement-observation.json` exist.
- Existing `metric.json` schema extended with the binding attribute set.
- Identity and metadata conform to existing conventions.
- Measurement types and applicable constraints established.
- Conformance test `tests/conformance/test_021_metric_canonical_entity.py` passes.
- All existing tests continue to pass.
- Documentation generated or updated.
- No duplicate or conflicting Metric definition introduced.
- Existing Outcome references remain valid or have an approved migration.
- EGV-004 identity continuity preserved.
- ADR-013 anti-accumulation preserved.
- Registry generation updated.

## 9. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| Six-dimensional classification values (scheme, concept) | CR-MET-002 |
| `dea:Measurement` full attribute set (lifecycle, configuration, governance) | CR-MET-003 |
| `dea:MeasurementObservation` full attribute set (provenance, confidence, temporal) | CR-MET-003 |
| `dea:produces`, `dea:applies-metric`, `dea:measures-subject` registry relationships | CR-MET-003 |
| Measurement lifecycle and execution | CR-MET-004 |
| Units, formulas, aggregation | CR-MET-005 |
| Baseline, target, threshold, variance, performance interpretation | CR-MET-006 |
| Cross-domain `dea:measured-by` source-list extension | CR-MET-007 |
| KPI / KRI / KCI designation (`dea:IndicatorDesignation`) | CR-MET-008 |
| Metric catalog establishment (`dea-catalog-metrics`) | CR-MET-009 |
| Governance objects (steward, owner, custodian, authority) | CR-MET-010 |
| Temporal dimensions, provenance, history | CR-MET-011 |
| Analytics, decision intelligence | CR-MET-012 |
| `metric_type` field removal (after deprecation window) | CR-MET-013 closure |

## 10. References

- CR-MET-000 (merged; commit 63d722a) §2 architectural posture, §4 disposition table, §5 22-question dialogue, §6 migration plan, §7 stage mapping.
- ADR-MET-001 (merged; commit 8a532dd) decision 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
- ADR-MET-002 (merged; commit 8a532dd) decisions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
- ADR-MET-003 (merged; commit 8a532dd) decision 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
- ADR-MET-004 (merged; commit 8a532dd) decisions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
- CR-5 §27 (existing `dea:Observation` definition).
- CR-10J (Scenario metrics).
- CR-10 (Outcome concept with metric-related references).
- ADR-0002 D1 (orthogonal allocator binding).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).
- CR-016 (kernel+specialization implementation precedent).
- EGV-004 (identity continuity).
- User-supplied CR-MET-001 (in `dea-catalog-metrics/00_inbox/CR-MET-001-005.md` lines 51..230).
- User clarification 2026-10-18 (verbatim: "Assessment score may be a measure, but not all assessments are Metrics. So am not clear why you want to membership from dea:assessment.").
- User reminder 2026-10-18 (no `dea:Activity`).
- `metamodel/dea-metamodel.yaml` line 1519 (current `dea:PerformanceMetric`).
- `metamodel/dea-metamodel.yaml` line 1855 (current `dea:Observation`).
- `schemas/entities/metric.json` (current; 166 lines).
- `schemas/entities/entity.json` (abstract root).
- `tests/conformance/test_009_entity_rules.py` (precedent for test_021).
