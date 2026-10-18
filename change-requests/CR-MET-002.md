# CR-MET-002 -- Establish Metric Classification and Taxonomy

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | CR-MET-001 (merged at commit 2c445e4 on main); ADR-MET-003 (merged at 8a532dd on main) |
| Blocks | CR-MET-008 (KPI/KRI/KCI designation); CR-MET-009 (catalog establishment with classified Metrics); CR-MET-002 is itself a Stream A item 2 in the programme |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (controlled vocabulary governance) |
| Kanban | T-MET umbrella card #429; this CR is card #432 |
| Stage mapping | Per CR-MET-000 §7, this CR is Stream A item 2 (semantic foundation, classification + taxonomy). It is the second canonical-source-touching CR in the programme after CR-MET-001. |

## 1. Objective

Establish a canonical, extensible Metric classification framework supporting discovery, semantic grouping, governance, analytics, and interoperability. The framework MUST be multidimensional (six orthogonal axes), MUST reuse the existing OpenDEAM classification metamodel rather than create a Metric-specific classification mechanism, and MUST preserve the binding principle that classification does not alter the fundamental identity of a Metric (changing a subject classification does not change the Metric id).

The six classification dimensions are:

1. Measurement subject (what the Metric measures)
2. Measurement purpose (why the Metric is used)
3. Measurement orientation (leading / lagging / diagnostic / concurrent)
4. Measurement nature (quantitative / qualitative / categorical / ordinal / binary / composite)
5. Measurement scope (enterprise / business domain / unit / process / etc.)
6. Management significance (KPI / KRI / KCI / SLI / general; bound by CR-MET-008)

## 2. Scope and posture

### 2.1 What this CR does

- Extends the existing controlled-vocabulary registry `metamodel/vocabularies/classifications.yaml` with 6 new Metric classification schemes (one per axis).
- Extends `schemas/entities/metric.json` with 5 new optional classification fields (subject, purpose, orientation, scope, management_significance). The 6th axis (nature) was added in CR-MET-001 as `measurement_nature` (required); the binding text is preserved unchanged.
- Extends `schemas/entities/indicator.json` with an optional `kind` discriminator that mirrors the `measurement_orientation` axis. This is per ADR-MET-003 decision 6 (the MAY for the Indicator `kind` discriminator); CR-MET-002 owns the implementation.
- Adds 6 representative classified Metric definitions as fixtures in `tests/conformance/fixtures/classified_metrics.yaml` (the 6 from the user-supplied spec §7).
- Adds a new conformance test `tests/conformance/test_022_metric_classification.py` validating: every Metric fixture has the required `subject_classification` (at least one) and `measurement_nature` (already required by CR-MET-001); the orientation, scope, and management-significance classifications are valid controlled-vocabulary values; the Indicator `kind` discriminator, when present, is a valid value.
- Regenerates the controlled-vocabulary artefacts and the registry.

### 2.2 What this CR does NOT do

- Does NOT introduce Metric-specific classification entities. The existing classification metamodel (controlled vocabularies in `metamodel/vocabularies/classifications.yaml`; binding on entity schemas per E005) is reused.
- Does NOT alter the fundamental identity of a Metric. Classification assignments are field-level references, not identity-defining attributes.
- Does NOT introduce a new parallel `dea:Classification` entity. The existing `dea:Information` line 1107 ("A classification of information by sensitivity and regulatory regime (PII, PHI, PCI)") is preserved; that is a separate, narrower classification concept for information-sensitivity regimes and is not generalizable.
- Does NOT introduce the `dea:IndicatorDesignation` entity (CR-MET-008 owns that). The `management_significance` field on Metric is a controlled-vocabulary value (KPI | KRI | KCI | SLI | general) referenced from the existing `dea:IndicatorDesignation` taxonomy.
- Does NOT extend the `dea:measured-by` source list (CR-MET-007 owns that).
- Does NOT add governance objects (CR-MET-010).

## 3. Classification architecture (six dimensions, binding)

### 3.1 Reuse of the existing classification metamodel

The existing OpenDEAM classification metamodel is the controlled-vocabulary registry at `metamodel/vocabularies/classifications.yaml`. The mechanism is: a classification scheme is identified by an `entity.property` key; the property is a field on a schema; the values are the controlled enumeration. Conformance test E005 (in `tests/conformance/test_009_entity_rules.py`) enforces that any property with an `enum` in an entity schema MUST have a matching entry in the controlled-vocabulary registry. The registry is therefore the single source of truth for the allowed values.

This CR extends the registry with 6 new Metric classification schemes. No new mechanism is introduced.

### 3.2 Axis 1: Measurement subject (extends, not parallelizes)

The subject axis identifies WHAT the Metric measures. The binding values, per the user-supplied CR-MET-002 §3.A, are:

- `dea:subject-financial` (revenue, margin, cost)
- `dea:subject-customer` (satisfaction, retention, acquisition)
- `dea:subject-organizational` (engagement, workforce stability)
- `dea:subject-operational` (throughput, efficiency, cycle time)
- `dea:subject-technology` (availability, latency, reliability)
- `dea:subject-data` (accuracy, completeness, consistency)
- `dea:subject-risk` (exposure, loss frequency)
- `dea:subject-capability` (capability performance and maturity)
- `dea:subject-strategic` (strategic objective attainment)
- `dea:subject-sustainability` (environmental and social performance)

A Metric MAY have multiple subject classifications. The field on the Metric schema is `subject_classification`; type is `array of string`; the values are the IDs above. The vocabulary entry is `Metric.subject_classification`.

The `dea:subject-*` IDs are referenceable. The full binding for these is a CR-MET-009 catalog establishment item (the canonical subject concept registry) per the user-supplied CR-MET-002 §3.A directive that the classification must be extensible and not force every Metric into one subject category.

### 3.3 Axis 2: Measurement purpose

The purpose axis identifies WHY the Metric is used. The binding values are:

- `performance_measurement`
- `risk_monitoring`
- `compliance_monitoring`
- `quality_measurement`
- `efficiency_measurement`
- `effectiveness_measurement`
- `maturity_measurement`
- `outcome_measurement`
- `diagnostic_measurement`
- `predictive_measurement`

A Metric MAY have multiple purpose classifications. The field on the Metric schema is `purpose_classification`; type is `array of string`. The vocabulary entry is `Metric.purpose_classification`.

### 3.4 Axis 3: Measurement orientation (also Indicator.kind)

The orientation axis identifies the temporal stance of the Metric. The binding values, per the user-supplied CR-MET-002 §3.C, are:

- `leading` (provides an indication of potential future conditions)
- `lagging` (records an outcome that has already occurred)
- `diagnostic` (helps explain a condition or performance result)
- `concurrent` (describes a condition occurring during the measurement period)

A Metric MAY have multiple orientation classifications only where the definitions genuinely support them. The field on the Metric schema is `orientation_classification`; type is `array of string`. The vocabulary entry is `Metric.orientation_classification`.

Per ADR-MET-003 decision 6, the existing `dea:Indicator` MAY be extended with a `kind` discriminator that mirrors the orientation axis. CR-MET-002 implements this: `dea:Indicator.kind` is added as an optional field with the same four-value enum. This binds the orientation axis to the Indicator entity while keeping the Metric-side classification as a separate field. A Metric with `orientation_classification: [leading]` MAY reference a `dea:Indicator` whose `kind: leading`.

### 3.5 Axis 4: Measurement nature (CR-MET-001 binding; preserved)

The nature axis identifies the data nature of the produced value. CR-MET-001 already declares this as the required `measurement_nature` field with the binding five-value enum (`numeric | ordinal | nominal | boolean | composite`); the controlled-vocabulary entry is `Metric.measurement_nature`. CR-MET-002 does NOT modify this; the binding is preserved.

The user-supplied CR-MET-002 §3.D uses a six-value taxonomy (`quantitative | qualitative | categorical | ordinal | binary | composite`). The reconciliation: CR-MET-001 collapsed the user-supplied six into the binding five by treating `quantitative` as `numeric`, `qualitative` as `nominal`, and `categorical` as `nominal` (with `binary` retained as a separate value). The reconciliation rationale is recorded in CR-MET-001 §4.2 item 2. This CR preserves the CR-MET-001 binding.

### 3.6 Axis 5: Measurement scope

The scope axis identifies the organizational or architectural scope of the measurement. The binding values, per the user-supplied CR-MET-002 §3.E, are:

- `enterprise`
- `business_domain`
- `business_unit`
- `organizational_unit`
- `value_stream`
- `capability`
- `process`
- `product_or_service`
- `system_or_component`
- `individual_subject`

A Metric MAY have multiple scope classifications. The field on the Metric schema is `scope_classification`; type is `array of string`. The vocabulary entry is `Metric.scope_classification`.

Note: `process` here refers to `dea:BusinessProcess` (line 592; L3) and its decomposition. There is no `dea:Activity` entity (per user reminder 2026-10-18). The activity-level scope is sub-scope of `process`.

### 3.7 Axis 6: Management significance (KPI / KRI / KCI / SLI)

The management-significance axis identifies how the Metric is designated for management reporting. The binding values, per the user-supplied CR-MET-002 §3.F, are:

- `general_metric` (not a managed designation; a plain Metric)
- `kpi` (Key Performance Indicator)
- `kri` (Key Risk Indicator)
- `kci` (Key Control Indicator)
- `sli` (Service-Level Indicator)
- `other_governed_designation` (reserved for future CR-registered designations)

A Metric MAY have multiple management-significance designations. The field on the Metric schema is `management_significance`; type is `array of string`. The vocabulary entry is `Metric.management_significance`.

Per the user-supplied CR-MET-002 §3.F directive and the binding ADR-MET-003 decision 7, these are designations or governed classifications, not automatic entity specializations. The binding declaration of KPI / KRI / KCI / SLI as a first-class entity (`dea:IndicatorDesignation`) is owned by CR-MET-008; this CR only declares the controlled-vocabulary values on the Metric.

## 4. Proposed canonical-source changes

### 4.1 `metamodel/vocabularies/classifications.yaml` (extend)

The existing file (630 lines; version 0.8.0) is extended with 6 new Metric classification schemes immediately after the existing `Metric.legacy_metric_type` block (around line 277) and before `Metric.frequency`. The new entries are:

```yaml
  Metric.subject_classification:
    entity: Metric
    property: subject_classification
    values:
    - dea:subject-financial
    - dea:subject-customer
    - dea:subject-organizational
    - dea:subject-operational
    - dea:subject-technology
    - dea:subject-data
    - dea:subject-risk
    - dea:subject-capability
    - dea:subject-strategic
    - dea:subject-sustainability
  Metric.purpose_classification:
    entity: Metric
    property: purpose_classification
    values:
    - performance_measurement
    - risk_monitoring
    - compliance_monitoring
    - quality_measurement
    - efficiency_measurement
    - effectiveness_measurement
    - maturity_measurement
    - outcome_measurement
    - diagnostic_measurement
    - predictive_measurement
  Metric.orientation_classification:
    entity: Metric
    property: orientation_classification
    values:
    - leading
    - lagging
    - diagnostic
    - concurrent
  Indicator.kind:
    entity: Indicator
    property: kind
    values:
    - leading
    - lagging
    - diagnostic
    - concurrent
  Metric.scope_classification:
    entity: Metric
    property: scope_classification
    values:
    - enterprise
    - business_domain
    - business_unit
    - organizational_unit
    - value_stream
    - capability
    - process
    - product_or_service
    - system_or_component
    - individual_subject
  Metric.management_significance:
    entity: Metric
    property: management_significance
    values:
    - general_metric
    - kpi
    - kri
    - kci
    - sli
    - other_governed_designation
```

The file `version: 0.8.0` is bumped to `0.9.0` per the existing version-management convention. (The version is the vocabulary version, not the metamodel version.)

### 4.2 `schemas/entities/metric.json` (extend)

The existing schema (199 lines, post CR-MET-001) is extended with 5 new optional classification fields immediately after the `measurement_nature` field (around line 65) and before `directionality`:

```json
"subject_classification": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": [
      "dea:subject-financial",
      "dea:subject-customer",
      "dea:subject-organizational",
      "dea:subject-operational",
      "dea:subject-technology",
      "dea:subject-data",
      "dea:subject-risk",
      "dea:subject-capability",
      "dea:subject-strategic",
      "dea:subject-sustainability"
    ]
  },
  "description": "Measurement subject axis. CR-MET-002 binding. A Metric MAY have multiple subject classifications."
},
"purpose_classification": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": [
      "performance_measurement",
      "risk_monitoring",
      "compliance_monitoring",
      "quality_measurement",
      "efficiency_measurement",
      "effectiveness_measurement",
      "maturity_measurement",
      "outcome_measurement",
      "diagnostic_measurement",
      "predictive_measurement"
    ]
  },
  "description": "Measurement purpose axis. CR-MET-002 binding. A Metric MAY have multiple purpose classifications."
},
"orientation_classification": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": ["leading", "lagging", "diagnostic", "concurrent"]
  },
  "description": "Measurement orientation axis. CR-MET-002 binding. Mirrors Indicator.kind."
},
"scope_classification": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": [
      "enterprise",
      "business_domain",
      "business_unit",
      "organizational_unit",
      "value_stream",
      "capability",
      "process",
      "product_or_service",
      "system_or_component",
      "individual_subject"
    ]
  },
  "description": "Measurement scope axis. CR-MET-002 binding. A Metric MAY have multiple scope classifications."
},
"management_significance": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": [
      "general_metric",
      "kpi",
      "kri",
      "kci",
      "sli",
      "other_governed_designation"
    ]
  },
  "description": "Management significance axis (KPI/KRI/KCI/SLI/general). CR-MET-002 binding. Designations, not specializations. Full IndicatorDesignation entity in CR-MET-008."
}
```

The previously required fields are preserved: `id`, `name`, `type`, `version`, `subject_concept`, `measurement_nature`. The new classification fields are optional. The deprecation-marker field `legacy_metric_type` is preserved (per CR-MET-001 §4.2).

### 4.3 `schemas/entities/indicator.json` (extend with `kind`)

The existing `indicator.json` schema is extended with a `kind` discriminator:

```json
"kind": {
  "type": "string",
  "enum": ["leading", "lagging", "diagnostic", "concurrent"],
  "description": "Indicator kind discriminator (CR-MET-002). Mirrors Metric.orientation_classification."
}
```

This implements ADR-MET-003 decision 6 (the MAY for the Indicator `kind` discriminator); CR-MET-002 owns the implementation.

### 4.4 `tests/conformance/fixtures/classified_metrics.yaml` (new)

Six representative classified Metric fixtures, per the user-supplied CR-MET-002 §7. The fixtures file is `tests/conformance/fixtures/classified_metrics.yaml` and contains:

| Metric id | subject | purpose | orientation | nature | scope | management |
|---|---|---|---|---|---|---|
| `dea:metric-customer-retention-rate` | customer | performance_measurement | lagging | numeric | enterprise | kpi |
| `dea:metric-employee-engagement-score` | organizational | diagnostic_measurement | concurrent | ordinal | organizational_unit | general_metric |
| `dea:metric-mean-time-to-recovery` | technology, operational | quality_measurement | lagging | numeric | system_or_component | kri |
| `dea:metric-data-completeness` | data | quality_measurement | concurrent | numeric | data | kci |
| `dea:metric-strategic-objective-attainment` | strategic | outcome_measurement | lagging | ordinal | enterprise | kpi |
| `dea:metric-operational-capacity-utilization` | operational | efficiency_measurement | concurrent | numeric | process | general_metric |

Each fixture carries the binding required fields (id, name, type, version, subject_concept, measurement_nature) plus the classification fields.

The fixture file is consumed by the conformance test `test_022_metric_classification.py`.

### 4.5 `tests/conformance/test_022_metric_classification.py` (new)

The new conformance test file validates:

1. Every fixture in `classified_metrics.yaml` has a non-empty `subject_classification` (at least one value).
2. Every fixture's `measurement_nature` is in the controlled vocabulary (CR-MET-001 binding).
3. Every fixture's `subject_classification` values are in the controlled vocabulary.
4. Every fixture's `purpose_classification` values are in the controlled vocabulary (if present).
5. Every fixture's `orientation_classification` values are in the controlled vocabulary (if present).
6. Every fixture's `scope_classification` values are in the controlled vocabulary (if present).
7. Every fixture's `management_significance` values are in the controlled vocabulary (if present).
8. The Indicator schema has a `kind` property with the binding four-value enum.
9. The Indicator `kind` enum is the same as the Metric `orientation_classification` enum (cross-check).

The test follows the existing `tests/conformance/test_009_entity_rules.py` style (CR-3 §24; E001-E010).

### 4.6 `metamodel/registry/entities.yaml` and `specification/` regenerated

The entity registry is regenerated from the canonical source. The Indicator entity declaration is unchanged (no new attribute on the entity; the `kind` is a schema-level field). The classification scheme additions to `classifications.yaml` trigger a vocabulary regeneration in `specification/vocabulary.yaml`.

## 5. Reconciliation with existing artifacts

### 5.1 Existing classification metamodel

The existing `dea:Information` (line 1107) and the existing `metamodel/vocabularies/classifications.yaml` mechanism are preserved. No change to existing classifications.

### 5.2 CR-10J Scenario metrics

Existing CR-10J Scenario metric records continue to validate. The new classification fields are optional; existing records that carry only the MECE `legacy_metric_type` continue to validate under the legacy field. The classification migration is a CR-MET-009 catalog-establishment concern, not a CR-MET-002 concern.

### 5.3 CR-5 §8 Indicator

The existing `dea:Indicator` (CR-5 §8) is preserved. The new `kind` discriminator is an optional field. The Indicator definition (line 1847) is unchanged. The `kind` value is independent of the Indicator identity (changing the kind does not change the Indicator id).

### 5.4 The pre-CR-MET-001 `metric_type` MECE enum

The pre-CR-MET-001 `metric_type` MECE enum is preserved as `legacy_metric_type` on the Metric schema (per CR-MET-001 §4.2). The CR-MET-002 classification axes are the binding replacement; the legacy enum is preserved for one release cycle.

## 6. Migration plan

1. Land the controlled-vocabulary extensions in `metamodel/vocabularies/classifications.yaml` (6 new Metric classification schemes; 1 new Indicator kind scheme).
2. Land the schema extensions in `schemas/entities/metric.json` (5 new optional fields).
3. Land the Indicator `kind` discriminator in `schemas/entities/indicator.json`.
4. Land the fixture file `tests/conformance/fixtures/classified_metrics.yaml` (6 representative Metrics).
5. Land the conformance test `tests/conformance/test_022_metric_classification.py`.
6. Regenerate the registry, vocabulary, and specification.
7. Run the full conformance test suite. All existing tests continue to pass (EGV-004).
8. Existing catalog records validate unchanged.

## 7. Required test cases (per user-supplied CR-MET-002 §7 and §8)

| Case | Status |
|---|---|
| Customer Retention Rate (customer, performance, lagging, numeric, enterprise, kpi) | Fixture; conformance test validates. |
| Employee Engagement Score (organizational, diagnostic, concurrent, ordinal, organizational_unit, general_metric) | Fixture; conformance test validates. |
| Mean Time to Recovery (technology, operational, quality, lagging, numeric, system_or_component, kri) | Fixture; conformance test validates. |
| Data Completeness (data, quality, concurrent, numeric, data, kci) | Fixture; conformance test validates. |
| Strategic Objective Attainment (strategic, outcome, lagging, ordinal, enterprise, kpi) | Fixture; conformance test validates. |
| Operational Capacity Utilization (operational, efficiency, concurrent, numeric, process, general_metric) | Fixture; conformance test validates. |
| Metric with multiple subject classifications | Conformance test validates; reused pattern in fixture for Mean Time to Recovery (subjects: technology + operational). |
| Metric with multiple purpose classifications | Conformance test validates; the user-supplied spec §5 says MAY. |
| Metric with multiple management designations | Conformance test validates; user-supplied spec §5 says MAY. |
| Deprecated classification, historically traceable | Deferred to CR-MET-009 (catalog establishment); the controlled vocabulary preserves every value. |
| Classification change does not alter Metric identity | Conformance test validates by re-fetching the fixture by id and confirming presence. |

## 8. Definition of Done

- Existing classification architecture reviewed.
- Canonical Metric taxonomy established.
- Classification schemes and concepts documented.
- Multiple classification assignments supported.
- Management designations defined.
- Extension and deprecation rules established (deferred to CR-MET-009 for catalog-side).
- Classification validation implemented.
- Representative examples validated.
- No competing Metric-specific classification architecture introduced.
- EGV-004 identity continuity preserved.
- ADR-013 anti-accumulation preserved.
- E005 conformance (controlled vocabulary) passes.

## 9. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| Full `dea:IndicatorDesignation` entity (KPI / KRI / KCI / SLI first-class) | CR-MET-008 |
| Catalog establishment (`dea-catalog-metrics` with classified Metrics) | CR-MET-009 |
| Governance objects for classification ownership | CR-MET-010 |
| Cross-domain classification examples | CR-MET-007 |
| Classification versioned governance | CR-MET-010 |
| Deprecated-classification lifecycle (proposed -> active -> deprecated) | CR-MET-009 |

## 10. References

- CR-MET-000 (merged; commit 63d722a) §2 architectural posture, §4 disposition table, §7 stage mapping.
- CR-MET-001 (merged; commit 2c445e4) §3 canonical semantic definition, §4.2 schema changes (subject_concept + measurement_nature).
- ADR-MET-003 (merged; commit 8a532dd) decisions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
- CR-5 §8 (existing `dea:Indicator` definition).
- CR-10J (Scenario metrics).
- EGV-004 (identity continuity).
- ADR-013 (Core non-accumulation).
- Existing OpenDEAM classification metamodel (controlled vocabularies in `metamodel/vocabularies/classifications.yaml`; E005 enforcement).
- User-supplied CR-MET-002 (in `dea-catalog-metrics/00_inbox/CR-MET-001-005.md` lines 232..419).
- User-supplied CR-MET-002 §3.A subject axis (10 values).
- User-supplied CR-MET-002 §3.B purpose axis (10 values).
- User-supplied CR-MET-002 §3.C orientation axis (4 values).
- User-supplied CR-MET-002 §3.D nature axis (6 values; reconciled to CR-MET-001's 5-value binding).
- User-supplied CR-MET-002 §3.E scope axis (10 values).
- User-supplied CR-MET-002 §3.F management significance axis (5 values plus `general_metric`).
- User-supplied CR-MET-002 §7 representative Metrics (6 fixtures).
- `metamodel/vocabularies/classifications.yaml` (existing controlled vocabulary; CR-3B/N, E005).
- `metamodel/dea-metamodel.yaml` line 1107 (existing `dea:Information` classification reference).
- `metamodel/dea-metamodel.yaml` line 1498 (existing `dea:Term` / classification node).
- `metamodel/dea-metamodel.yaml` line 1847 (existing `dea:Indicator`).
- `metamodel/dea-metamodel.yaml` line 592 (existing `dea:BusinessProcess`; L3; for scope = process).
- `tests/conformance/test_009_entity_rules.py` (E005 precedent).
- `tests/conformance/test_021_metric_canonical_entity.py` (CR-MET-001 precedent).
