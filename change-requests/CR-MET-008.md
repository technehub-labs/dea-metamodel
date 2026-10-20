# CR-MET-008 -- Establish Governed Management Indicator Designations and Semantics

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | CR-MET-001 (merged 2c445e4); CR-MET-002 (merged 84f10f4); CR-MET-005 (merged 9fdf356); CR-MET-006 (merged 8a8185a); CR-MET-007 (merged c319ea5) |
| Blocks | CR-MET-009 (catalog with classified Measurements and KPI designations); CR-MET-010 (governance) |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control) |
| Kanban | T-MET umbrella #429; this CR is card #438 |
| Stream | Stream B (Enterprise interpretation and governance); third Stream B item. |

## 1. Background and problem statement

Not every Metric is a KPI, and not every KPI is a measure of financial performance. Organizations use several types of indicators for performance management, governance, operational control, and risk management.

OpenDEAM must represent these distinctions without fragmenting the Metric architecture into numerous unnecessarily specialized entities.

The user-supplied CR-MET-008 §4 makes the recommended decision explicit: "Use governed designations by default. This allows one Metric to serve different management purposes without creating duplicate definitions. Where a designation introduces materially different lifecycle, identity or governance requirements, a specialized construct may be justified through an ADR."

## 2. Objective

Establish canonical semantics for management indicators and define how they are designated, governed, and associated with Metrics.

## 3. Indicator concepts (per the user-supplied §3)

| Indicator | Definition |
|---|---|
| KPI | Key Performance Indicator; a Metric designated as particularly important for evaluating performance against an objective |
| KRI | Key Risk Indicator; a Metric designated to monitor risk exposure, risk drivers, or changes in risk conditions |
| KCI | Key Control Indicator; a Metric designated to evaluate control operation or effectiveness |
| SLI | Service-Level Indicator; a Metric used to quantify a service characteristic or performance |
| Operational Indicator | A Metric designated for operational monitoring |

Plus the measurement orientations:

| Orientation | Definition |
|---|---|
| Leading | An indicator providing evidence about potential future conditions |
| Lagging | An indicator reporting realized historical conditions |
| Neutral | Neither leading nor lagging |

Leading and Lagging are measurement orientations, not substitutes for KPI or KRI designations. They are cross-cutting attributes; the same Metric may be designated as `KPI Leading` for one purpose and `KPI Lagging` for another (e.g., Net Retention as a `KPI Lagging` for the financial reporting context, Net Retention as a `KPI Leading` for the next-quarter forecast context).

## 4. Binding architectural decision: Governed Designations (user-supplied §4 option c)

Three architectural options were considered by the user-supplied CR-MET-008 §4. The binding decision is option (c):

> KPI, KRI, KCI as governed designations applied to Metric. RECOMMENDED.
>
> This allows one Metric to serve different management purposes without creating duplicate definitions.

The audit-then-specifies result: a NEW first-class entity `dea:IndicatorDesignation` carries the 12 designation attributes from the user-supplied §5. The Metric entity (already established in CR-MET-001) references its designations via a NEW relationship `dea:has-designation` (PerformanceMetric -> IndicatorDesignation). The Metric does NOT carry designation fields directly; the designation adds management context without altering measurement identity (EGV-004 preserved).

**The Metric identity is preserved across designations.** The same `dea:metric-customer-retention-rate` may carry both a `KPI Lagging` designation (for the executive quarterly review) and a `KRI Leading` designation (for the early-warning risk monitoring); the underlying measurement definition is not fragmented.

## 5. IndicatorDesignation semantics (NEW: `dea:IndicatorDesignation`)

The IndicatorDesignation entity carries the 12 binding attributes from the user-supplied §5:

| Field | Type | Required | Description |
|---|---|---|---|
| `designation_type` | enum | required | KPI, KRI, KCI, SLI, Operational |
| `associated_metric_ref` | string (PerformanceMetric id) | required | The Metric being designated |
| `management_purpose` | string | required | Why the designation exists (e.g., "executive quarterly review") |
| `associated_objective_ref` | string (StrategicObjective or Outcome ref) | optional | The objective/Outcome this designation supports |
| `organizational_scope` | string or array | required | Scope of application (enterprise, business_domain, business_unit, capability, process, product_or_service, system) |
| `accountable_owner_ref` | string (Actor ref) | required | Responsible management authority |
| `reporting_frequency` | enum | required | real_time, hourly, daily, weekly, monthly, quarterly, semi_annual, annual |
| `target_reference` | string (PerformanceTarget ref) | optional | Applicable Target |
| `threshold_reference` | string (Threshold ref) | optional | Applicable Threshold |
| `escalation_rules` | string or array | optional | Required management response |
| `measurement_orientation` | enum | required | leading, lagging, neutral |
| `effective_period` | TemporalInterval ref | required | Validity of designation |
| `approval_status` | enum | required | draft, proposed, approved, retired |

The IndicatorDesignation is a sibling of `dea:AssessmentResult` (which carries score) and `dea:PerformanceInterpretation` (which carries judgment). The IndicatorDesignation carries the management-significance context that is not part of the underlying measurement.

### 5.1 KPI-specific constraints (user-supplied §6)

When `designation_type: KPI`, the following fields are REQUIRED:

- `associated_objective_ref` (every KPI must reference an objective; the absence requires explicit documentation)
- `accountable_owner_ref`
- `reporting_frequency`
- `measurement_orientation`
- `effective_period`
- `approval_status: approved` (a KPI in production must be governance-approved)

### 5.2 KRI-specific constraints (user-supplied §7)

When `designation_type: KRI`, the following fields are REQUIRED:

- `associated_metric_ref` (inherently)
- `management_purpose` (must reference a Risk context)
- `reporting_frequency`
- `escalation_rules` (warning/critical thresholds trigger escalation)
- `accountable_owner_ref` (risk owner)
- `effective_period`
- `approval_status`

A KRI MUST NOT be assumed to be a direct measurement of realized loss. It MAY measure an exposure, condition, or driver associated with a risk. The `management_purpose` field documents this distinction.

### 5.3 KCI-specific constraints (user-supplied §8)

When `designation_type: KCI`, the following fields are REQUIRED:

- `associated_metric_ref` (inherently)
- `associated_objective_ref` (the control objective; the user-supplied §8 "control objective")
- `accountable_owner_ref` (control owner)
- `escalation_rules` (remediation escalation)
- `reporting_frequency`
- `effective_period`
- `approval_status`

The cross-reference: the `associated_objective_ref` for a KCI points to a control objective (e.g., "prevent unauthorized access"). For a KPI, it points to a business objective (e.g., "increase customer retention"). For a KRI, it points to a risk-objective (e.g., "maintain risk exposure below appetite").

## 6. IndicatorDesignation lifecycle

The IndicatorDesignation carries its own lifecycle (`approval_status`) which is independent of the Metric's lifecycle. A Metric may be `proposed` while one of its designations is `approved` (e.g., a Metric has been approved for use but its first KPI designation is still being defined).

The lifecycle is governed by CR-MM-04 (R1) for canonical-source changes and CR-MM-04 (R2) for catalog-side governance. The user-supplied §9 binding decision: "A Metric remains a Metric regardless of its management designation."

## 7. Canonical-source changes

### 7.1 NEW entity: `dea:IndicatorDesignation`

1 entity block appended to the canonical source:

```yaml
- id: dea:IndicatorDesignation
  name: Indicator Designation
  legacy_ids: []
  definition: "A governed management designation applied to a PerformanceMetric (CR-MET-008 binding). Carries designation_type (KPI, KRI, KCI, SLI, Operational), measurement_orientation (leading, lagging, neutral), management_purpose, associated_objective, organizational_scope, accountable_owner, reporting_frequency, target_reference, threshold_reference, escalation_rules, effective_period, approval_status. The Metric identity is preserved across designations (EGV-004). One Metric may carry multiple designations (e.g. KPI Lagging and KRI Leading) for different management purposes."
  layer: null
  dimension: measurement-dimension
  building_block: null
  abstract: false
  status: normative
  lifecycle: proposed
  class_alias: null
  catalog_repo: null
  artifacts:
    json_schema: schemas/entities/indicator-designation.json
    sqlite_table: indicator_designations
    pydantic_model: pydantic/indicator_designation.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: profile
    profile: dea:assessment
```

### 7.2 NEW relationship: `dea:has-designation`

1 new relationship block appended to the canonical source:

```yaml
- id: dea:has-designation
  name: Has Designation
  definition: "The PerformanceMetric has the IndicatorDesignation as a governed management designation. CR-MET-008 binding: cardinality source 0..* (a Metric may carry any number of designations), target 1 (each designation applies to exactly one Metric). The Metric identity is preserved; the designation adds management context without altering measurement identity (EGV-004)."
  category: governance
  direction: source-to-target
  source:
    types:
      - dea:PerformanceMetric
  target:
    types:
      - dea:IndicatorDesignation
  cardinality:
    source: 0..*
    target: "1"
  inverse: dea:designates
  transitive: false
  symmetric: false
  temporal: true
  provenance: required
  status: normative
  lifecycle: proposed
```

### 7.3 NEW schema: `schemas/entities/indicator-designation.json`

The schema declares the 13 binding attributes (12 from user-supplied §5 + the `measurement_orientation` cross-cutting attribute). JSON Schema with `metamodel_version`, `external_references` (CR-3P compliant), and the controlled-vocabulary enums aligned with the new classifications.yaml entries.

### 7.4 EXTEND `schemas/relationships/relationship-instance.json` enum

Add the new `has-designation` entry (alphabetical placement between `grants` and `has-oversight`).

### 7.5 Controlled vocabulary additions

4 new entries in `metamodel/vocabularies/classifications.yaml` (version 0.12.0 -> 0.13.0):

| Vocabulary | Cardinality | Purpose |
|---|---|---|
| `IndicatorDesignation.designation_type` | 5 values | KPI, KRI, KCI, SLI, Operational |
| `IndicatorDesignation.measurement_orientation` | 3 values | leading, lagging, neutral |
| `IndicatorDesignation.reporting_frequency` | 8 values | real_time, hourly, daily, weekly, monthly, quarterly, semi_annual, annual |
| `IndicatorDesignation.approval_status` | 4 values | draft, proposed, approved, retired |

## 8. Migration plan

1. Land the 1 NEW entity block in `metamodel/dea-metamodel.yaml` (157 -> 158 entities).
2. Land the 1 NEW relationship in `metamodel/dea-metamodel.yaml` (112 -> 113 relationships).
3. Land the 1 new schema `schemas/entities/indicator-designation.json`.
4. Extend `schemas/relationships/relationship-instance.json` enum with `has-designation`.
5. Land the 4 controlled-vocabulary entries; version bump 0.12.0 -> 0.13.0.
6. Land the fixture file `tests/conformance/fixtures/indicator_designations.yaml` with 8 representative designations (1 KPI, 1 KRI, 1 KCI, 1 SLI, 1 Operational, 1 Leading-only, 1 Lagging-only, 1 KPI Leading combo).
7. Land the conformance test `tests/conformance/test_028_indicator_designations.py`.
8. Run the full test suite; regenerate registry + specification.

## 9. Definition of Done

- `dea:IndicatorDesignation` established as a new first-class entity (157 -> 158 entities).
- `dea:has-designation` relationship introduced (112 -> 113 relationships).
- The 13 binding attributes encoded on the IndicatorDesignation schema.
- KPI/KRI/KCI-specific constraints encoded as required-field constraints (enforced by test_028).
- Leading / Lagging encoded as `measurement_orientation` field, NOT a designation type.
- SLI and Operational Indicator encoded as additional `designation_type` enum values.
- 4 controlled-vocabulary entries added (version 0.12.0 -> 0.13.0).
- 8 representative fixtures validate the cross-cutting patterns.
- EGV-004 identity continuity preserved (Metric identity is preserved across designations).
- ADR-013 anti-accumulation honored where existing canonical source provides fit; the Designation is genuinely a new concept with independent lifecycle and governance.
- Conformance tests validate the cross-field invariants.
- Stream B item 3 sealed.

## 10. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| DesignationType subtype entities (KPI/KRI/KCI as separate constructs) if materially justified | future ADR per user-supplied §4 escape clause |
| Full governance objects (steward, owner, custodian, authority) on Designation | CR-MET-010 |
| Catalog establishment with classified Measurements and KPI designations | CR-MET-009 |
| Reporting-cron and escalation-rule resolution | runtime concern |

## 11. References

- CR-MET-000 (merged; commit 63d722a) §4 disposition table.
- CR-MET-001 (merged; commit 2c445e4) §3.1 (Metric definition).
- CR-MET-002 (merged; commit 84f10f4) §3 (classification with 6 axes).
- CR-MET-005 (merged; commit 9fdf356) §3.6 (precision/rounding).
- CR-MET-006 (merged; commit 8a8185a) §5 (PerformanceTarget), §6 (Threshold), §7 (PerformanceInterpretation).
- CR-MET-007 (merged; commit c319ea5) §6 (Q9a design-time applicability).
- User-supplied CR-MET-008: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-006-012.md` (lines 619..803).
- User-supplied §4 escape clause: "Where a designation introduces materially different lifecycle, identity or governance requirements, a specialized construct may be justified through an ADR."
- EGV-004 (identity continuity).
- ADR-013 (Core non-accumulation).