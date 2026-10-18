# CR-MET-003 -- Establish Measurement and Observation as Distinct OpenDEAM Entities

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | CR-MET-001 (merged at commit 2c445e4 on main); CR-MET-002 (merged at 84f10f4 on main); ADR-MET-002 (merged at 8a532dd on main) |
| Blocks | CR-MET-004 (Measurement lifecycle and execution); CR-MET-005 (units, formulas, aggregation); CR-MET-006 (Baseline/Target/Threshold); CR-MET-009 (catalog with classified Measurements); CR-MET-010 (governance of Measurements); CR-MET-011 (temporal / provenance / history of Observations) |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control) |
| Kanban | T-MET umbrella card #429; this CR is card #433 |
| Stage mapping | Per CR-MET-000 §7, this CR is Stream A item 3 (measurement architecture: Measurement and Observation entities). It is the third canonical-source-touching CR in the programme. |

## 1. Objective

Establish Measurement and Observation as first-class OpenDEAM entities distinct from the Metric definition. A Metric is the rule; a Measurement is the act; an Observation is the recorded result. The metamodel must reliably support historical measurement, traceability, comparisons, trend analysis, and measurement provenance. Without these distinctions, the metamodel collapses three orthogonal concepts into one and loses the auditability that enterprise measurement requires.

This CR is the binding implementation of the placeholders introduced in CR-MET-001 §3.2 and §3.3. The CR-MET-001 declaration of `dea:Measurement` and `dea:MeasurementObservation` is extended here with the full attribute set, the three binding relationships (`dea:applies-metric`, `dea:measures-subject`, and the extended `dea:produces`), the runtime-vs-metamodel responsibility split, and the conformance test.

## 2. Scope and posture

### 2.1 What this CR does

- Extends the `schemas/entities/measurement.json` placeholder with the full binding attribute set per the user-supplied CR-MET-003 §4.
- Extends the `schemas/entities/measurement-observation.json` placeholder with the full binding attribute set per the user-supplied CR-MET-003 §5.
- Extends the canonical relationship `dea:produces` (line 3822 of `metamodel/dea-metamodel.yaml`; pre-existing for ApplicationComponent/Assessment/BusinessCapability/BusinessProcess/Experiment/SystemFunction sources) with `dea:Measurement` as a new source type and `dea:MeasurementObservation` as a new target type. **Audit note**: per the audit-then-specifies pattern (per dea-metamodel skill), the existing `dea:produces` relationship is reused; the binding semantics ("the source creates or emits the target as an output") already cover the new Measurement-to-MeasurementObservation case.
- Adds a new relationship `dea:applies-metric` with source = `dea:Measurement`, target = `dea:PerformanceMetric`, cardinality 1:1 (every Measurement applies exactly one Metric definition version).
- Adds a new relationship `dea:measures-subject` with source = `dea:Measurement`, target = the same set of enterprise entities as `dea:measured-by` (line 4612; current 7 entity types: dea:AIMLModel, dea:ApplicationComponent, dea:BusinessCapability, dea:BusinessProcess, dea:BusinessService, dea:Outcome, dea:StrategicObjective). Cardinality 1:1 (every Measurement targets one subject). The source-list extension to 17 entity types per ADR-MET-004 / CR-MET-007 is NOT in this CR; CR-MET-007 owns the extension. CR-MET-003 declares `dea:measures-subject` with the current 7-type source-list; CR-MET-007 will widen it to 17.
- Adds 4 representative Measurement fixtures and 6 representative MeasurementObservation fixtures in `tests/conformance/fixtures/measurement_observations.yaml` (per the user-supplied §7 example and the binding customer-retention-rate test case).
- Adds a new conformance test `tests/conformance/test_023_measurement_observation.py` validating: every Measurement fixture has `applies_metric` and `measures_subject` references; every MeasurementObservation fixture has `produced_by` and `value`; the `dea:produces` relationship is extended with the new source/target types; `dea:applies-metric` and `dea:measures-subject` are present in the registry with the correct cardinalities; numeric observations are typed numerically; ordinal observations reference a valid ordinal scale where present; runtime-vs-metamodel responsibility split is documented in the CR.
- Regenerates the registry and specification.

### 2.2 What this CR does NOT do

- Does NOT collapse Measurement into Metric. The Metric-Definition-vs-Measurement-Execution distinction is normative (per the user-supplied CR-MET-000 §2 architectural principle 2 and CR-MET-001 §3.1).
- Does NOT collapse MeasurementObservation into the existing assessment-side `dea:Observation` (CR-5 §27; line 1855). The two are siblings on the assessment-vs-measurement axis; per the user clarification 2026-10-18, no re-membership, no supersession, no deprecation.
- Does NOT introduce a new `dea:Activity` (per user reminder 2026-10-18). The activity-level measurement is sub-measurement of `dea:BusinessProcess` (line 592; L3) via the existing catalog-internal Activity/Task hierarchy.
- Does NOT add the Measurement lifecycle states (planned, initiated, in_progress, etc.). CR-MET-004 owns the lifecycle. The CR-MET-003 schemas reference the lifecycle vocabulary but the binding implementation lands in CR-MET-004.
- Does NOT add governance objects. CR-MET-010 owns that.
- Does NOT add temporal dimensions or provenance beyond a `temporal` placeholder object. CR-MET-011 owns the binding 7 temporal dimensions.
- Does NOT add units, formulas, aggregation. CR-MET-005 owns that.
- Does NOT introduce the `dea:provenance` or `dea:evidence` entities. Those are cross-cutting concepts owned by their respective CRs; this CR uses string references on the Measurement / MeasurementObservation schemas that the future governance / provenance CRs will resolve.
- Does NOT touch the runtime architecture. The CR documents the runtime-vs-metamodel responsibility split (per the user-supplied §8 recommendation); the runtime implementation is a future concern.

## 3. Canonical semantic definitions (binding text)

### 3.1 `dea:Measurement` (extended from CR-MET-001 §3.2)

> A Measurement is an identifiable occurrence or record of applying a Metric definition to a particular subject, within a defined context, using an identified measurement method and applicable measurement configuration. A Measurement carries the `applies-metric` reference to the Metric definition version applied, the `measures-subject` reference to the entity that was measured, the temporal context, the responsible party, the source, the configuration, and any evidence supporting the measurement. A Measurement MAY produce zero or more MeasurementObservations (zero when the measurement failed, was cancelled, or was otherwise incomplete).
>
> A Measurement is distinct from a Metric (the definition) and from a MeasurementObservation (the result). The three are siblings on the definition-execution-result axis.

### 3.2 `dea:MeasurementObservation` (extended from CR-MET-001 §3.3)

> A MeasurementObservation is an identifiable record of an observed or determined value associated with a Metric and its measurement context, including the temporal, provenance, and quality information necessary to interpret that value. A MeasurementObservation is the recorded result of a Measurement. A MeasurementObservation is a sibling of the existing assessment-side `dea:Observation` (CR-5 §27; line 1855); the two are distinct concepts on the assessment-vs-measurement axis and MUST NOT be merged, re-membershiped, or supersed-ed (per the user clarification 2026-10-18).
>
> The value representation of a MeasurementObservation MUST be compatible with the parent Metric's `measurement_nature` (CR-MET-001 binding). A numeric observation MUST be typed as a number. An ordinal observation MUST reference a valid ordinal scale. A categorical observation MUST reference a controlled vocabulary where appropriate. A composite observation is an object. A boolean observation is a boolean.

## 4. Proposed canonical-source changes

### 4.1 `schemas/entities/measurement.json` (extend)

The placeholder schema (85 lines, post CR-MET-001) is extended with the full binding attribute set per the user-supplied CR-MET-003 §4:

```json
{
  // ... existing required: id, name, type, version, applies_metric, measures_subject ...
  "properties": {
    // ... existing applies_metric, measures_subject, temporal, responsible_party, configuration, relationships, metadata ...
    "measurement_method": { "type": "string", "maxLength": 2000 },
    "measurement_time": { "type": "string", "format": "date-time" },
    "reporting_period_start": { "type": "string", "format": "date" },
    "reporting_period_end": { "type": "string", "format": "date" },
    "measurement_source": { "type": "string", "maxLength": 500 },
    "measurement_status": {
      "type": "string",
      "enum": [
        "planned", "initiated", "in_progress", "pending_validation",
        "validated", "completed", "failed", "cancelled",
        "rejected", "superseded"
      ]
    },
    "configuration_reference": { "type": "string" },
    "evidence_reference": {
      "type": "array",
      "items": { "type": "string" }
    },
    "context": { "type": "object", "additionalProperties": true }
  }
}
```

Notes:

- `measurement_method` is required (per user-supplied §4).
- `measurement_time` is required (per user-supplied §4).
- `measurement_status` is required (per user-supplied §4). The enum is the 10-value canonical lifecycle from CR-MET-003 §5, which CR-MET-004 will refine.
- `reporting_period_start` and `reporting_period_end` are conditional (per user-supplied §4; conditional on Metric with a reporting period concept; full binding in CR-MET-006).
- `evidence_reference` is an array of strings (per user-supplied §4); each reference is a string handle that the future governance / evidence CRs will resolve. The `evidence` entity is a cross-cutting concept not introduced in this CR.
- `measurement_source` is the source system or originating system (per user-supplied §4).
- The `applies_metric` and `measures_subject` references (introduced as placeholders in CR-MET-001) are now required and binding.

### 4.2 `schemas/entities/measurement-observation.json` (extend)

The placeholder schema (97 lines, post CR-MET-001) is extended with the full binding attribute set per the user-supplied CR-MET-003 §5:

```json
{
  // ... existing required: id, name, type, version, produced_by, value ...
  "properties": {
    // ... existing produced_by, value, unit, temporal, confidence, relationships, metadata ...
    "observed_at": { "type": "string", "format": "date-time" },
    "valid_from": { "type": "string", "format": "date" },
    "valid_to": { "type": "string", "format": "date" },
    "reporting_period_start": { "type": "string", "format": "date" },
    "reporting_period_end": { "type": "string", "format": "date" },
    "observation_quality": { "type": "string", "maxLength": 1000 },
    "provenance_reference": { "type": "string" },
    "evidence_reference": {
      "type": "array",
      "items": { "type": "string" }
    },
    "observation_status": {
      "type": "string",
      "enum": [
        "proposed", "active", "superseded", "retired"
      ]
    }
  }
}
```

Notes:

- `produced_by` and `value` remain required (per CR-MET-001).
- `observed_at` is required (per user-supplied §5).
- `observation_status` is required (per user-supplied §5). The 4-value enum is the binding observation validity state; the relationship to Measurement status is documented.
- `valid_from` / `valid_to` are conditional (per user-supplied §5; conditional on observations that have a validity period concept).
- `value` is typed as a discriminated union compatible with the parent Metric's `measurement_nature`. The binding types per the user-supplied §5 + §8:
  - `numeric` (CR-MET-001 binding) -> number
  - `ordinal` -> number or string (depends on the ordinal scale)
  - `nominal` -> string
  - `boolean` -> boolean
  - `composite` -> object

### 4.3 `metamodel/dea-metamodel.yaml` changes

#### 4.3.1 `dea:produces` relationship (extend)

The existing `dea:produces` block (line 3822) is extended by adding `dea:Measurement` to the source list and `dea:MeasurementObservation` to the target list. The binding semantics ("The source creates or emits the target as an output") already cover the new case; the extension is additive only.

Diff:

```yaml
- id: dea:produces
  name: Produces
  definition: The source creates or emits the target as an output.
  category: flow
  direction: source-to-target
  source:
    types:
    - dea:ApplicationComponent
    - dea:Assessment
    - dea:BusinessCapability
    - dea:BusinessProcess
    - dea:Experiment
    - dea:SystemFunction
    - dea:Measurement            # CR-MET-003: added
  target:
    types:
    - dea:AssessmentResult
    - dea:BusinessObject
    - dea:DataEntity
    - dea:Event
    - dea:Evidence
    - dea:InformationAsset
    - dea:Signal
    - dea:MeasurementObservation  # CR-MET-003: added
  cardinality:
    source: 0..*
    target: 0..*
  inverse: dea:produced-by
  transitive: false
  symmetric: false
  temporal: true
  provenance: optional
  status: normative
  lifecycle: active
```

Audit note: the existing `dea:produces` semantics are NOT changed. The CR-MET-003 extension is purely additive on the source and target lists. No new relationship is introduced; the existing relationship is reused per the audit-then-specifies pattern.

#### 4.3.2 `dea:applies-metric` (new)

```yaml
- id: dea:applies-metric
  name: Applies Metric
  definition: The Measurement (source) applies the Metric definition (target) version. Cardinality 1:1; every Measurement applies exactly one Metric definition version. The reference is to the specific semantic version of the Metric (e.g. dea:metric-customer-retention-rate@1.0.0).
  category: measurement
  direction: source-to-target
  source:
    types:
    - dea:Measurement
  target:
    types:
    - dea:PerformanceMetric
  cardinality:
    source: 1
    target: 1
  inverse: dea:applied-by
  transitive: false
  symmetric: false
  temporal: false
  provenance: required
  status: normative
  lifecycle: active
```

#### 4.3.3 `dea:measures-subject` (new)

```yaml
- id: dea:measures-subject
  name: Measures Subject
  definition: The Measurement (source) targets the entity (target) that is being measured. Cardinality 1:1; every Measurement targets exactly one subject. The target list is the same as dea:measured-by's source list. CR-MET-003 declares the current 7-entity source list (matching the existing dea:measured-by source endpoint); CR-MET-007 will widen this to 17 entity types per ADR-MET-004.
  category: measurement
  direction: source-to-target
  source:
    types:
    - dea:Measurement
  target:
    types:
    - dea:AIMLModel
    - dea:ApplicationComponent
    - dea:BusinessCapability
    - dea:BusinessProcess
    - dea:BusinessService
    - dea:Outcome
    - dea:StrategicObjective
  cardinality:
    source: 1
    target: 1
  inverse: dea:measured-by
  transitive: false
  symmetric: false
  temporal: false
  provenance: required
  status: normative
  lifecycle: active
```

Note: the `inverse: dea:measured-by` declaration here is a NOTIONAL inverse. The existing `dea:measured-by` relationship is independent; this CR does NOT modify `dea:measured-by` (per ADR-MET-004, the extension of `dea:measured-by` is owned by CR-MET-007). The `inverse: dea:measured-by` declaration is a semantic claim that a Measurement's `measures-subject` reference is the inverse-pole of the subject's `measured-by` reference; this is the binding cardinality check, not a registry duplication.

#### 4.3.4 `dea:produced-by` (verify pre-existing inverse)

The inverse `dea:produced-by` is already declared in the existing `dea:produces` block (line 3847). This CR confirms that the inverse is the binding inverse for the new Measurement-to-MeasurementObservation case. No change to `dea:produced-by`.

### 4.4 `tests/conformance/fixtures/measurement_observations.yaml` (new)

4 representative Measurement fixtures and 6 representative MeasurementObservation fixtures, per the user-supplied §7 example (Customer Retention Rate Q3 2026) and the binding representative cases.

#### 4.4.1 Measurements (4 fixtures)

| id | applies_metric | measures_subject | method | time | status |
|---|---|---|---|---|---|
| `dea:measurement-2026-q3-customer-retention` | `dea:metric-customer-retention-rate@1.0.0` | `dea:customer-segment-north-america-enterprise` | calculated | 2026-10-01T00:00:00Z | completed |
| `dea:measurement-2026-q3-employee-engagement` | `dea:metric-employee-engagement-score@1.0.0` | `dea:organizational-unit-global-engineering` | manual | 2026-09-15T00:00:00Z | completed |
| `dea:measurement-2026-q3-mean-time-to-recovery` | `dea:metric-mean-time-to-recovery@1.0.0` | `dea:information-system-component-checkout-service` | automated | 2026-10-01T00:00:00Z | completed |
| `dea:measurement-2026-q3-data-completeness-failed` | `dea:metric-data-completeness@1.0.0` | `dea:data-entity-customer-profile` | automated | 2026-10-01T00:00:00Z | failed |

The 4th fixture (`...-failed`) is the canonical "MAY produce zero observations" case: a failed Measurement that produced no MeasurementObservations.

#### 4.4.2 MeasurementObservations (6 fixtures)

| id | produced_by | value | unit | observed_at | status |
|---|---|---|---|---|---|
| `dea:measurement-observation-2026-q3-customer-retention` | `dea:measurement-2026-q3-customer-retention` | 0.924 | % | 2026-10-01T00:00:00Z | active |
| `dea:measurement-observation-2026-q3-employee-engagement-1` | `dea:measurement-2026-q3-employee-engagement` | 4.2 | (ordinal scale 1-5) | 2026-09-15T00:00:00Z | active |
| `dea:measurement-observation-2026-q3-employee-engagement-2` | `dea:measurement-2026-q3-employee-engagement` | 3.8 | (ordinal scale 1-5) | 2026-09-15T00:00:00Z | active |
| `dea:measurement-observation-2026-q3-mttr` | `dea:measurement-2026-q3-mean-time-to-recovery` | 142 | minutes | 2026-10-01T00:00:00Z | active |
| `dea:measurement-observation-2026-q3-mttr-superseded` | `dea:measurement-2026-q3-mean-time-to-recovery` | 158 | minutes | 2026-09-15T00:00:00Z | superseded |
| `dea:measurement-observation-2026-q3-data-completeness` | (none; measurement failed) | 0.987 | % | 2026-10-01T00:00:00Z | active |

Note: the 6th fixture is the canonical "Measurement MAY produce zero observations" case: the failed Measurement does not produce any observation; the 6th observation is from a separate successful measurement (the data-completeness metric for the customer-profile data entity for the same period).

The fixture file is consumed by the conformance test.

### 4.5 `tests/conformance/test_023_measurement_observation.py` (new)

The new conformance test file validates:

1. Every Measurement fixture has non-empty `applies_metric`, `measures_subject`, `measurement_method`, `measurement_time`, `measurement_status`.
2. Every MeasurementObservation fixture has non-empty `produced_by`, `value`, `observed_at`, `observation_status`.
3. Numeric observations (`measurement_nature: numeric` from the parent Metric) have a numeric `value`.
4. The `dea:produces` relationship in the registry has `dea:Measurement` in the source list and `dea:MeasurementObservation` in the target list.
5. The `dea:applies-metric` relationship is present in the registry with cardinality 1:1.
6. The `dea:measures-subject` relationship is present in the registry with cardinality 1:1.
7. The failed-Measurement fixture has no corresponding `produced_by` reference in the MeasurementObservations (the "MAY produce zero observations" case).
8. The superseded observation fixture has `observation_status: superseded`.
9. EGV-004 identity continuity: every fixture has a unique `dea:` id matching the pattern.

### 4.6 `metamodel/registry/relationships.yaml` regenerated

The registry is regenerated from the canonical source. The regenerated registry contains the extended `dea:produces` block and the new `dea:applies-metric` and `dea:measures-subject` blocks.

## 5. Runtime-vs-metamodel responsibility split

Per the user-supplied CR-MET-003 §8 recommendation, the CR documents the split:

| Concern | Owner | Rationale |
|---|---|---|
| Canonical Measurement / MeasurementObservation semantics | metamodel (this CR) | Required for cross-domain referenceability and conformance. |
| Identity, lifecycle vocabulary, conformance rules | metamodel (this CR + CR-MET-004) | Required for governance. |
| Cardinality and relationship rules | metamodel (this CR + ADR-MET-002) | Required for the cross-domain graph. |
| **High-volume operational observation storage** | **future runtime architecture** | **A future measurement data repository/service owns the operational scale-out. The metamodel carries the schema; the runtime carries the data.** |
| Measurement execution engines | future runtime architecture | Per the user-supplied §1, measurements may be automated, manual, calculated, aggregated, external, assessed, simulated, AI-assisted. The metamodel does not prescribe a runtime; it declares the lifecycle and the entity semantics. |
| Real-time observation streams | future runtime architecture | The metamodel carries the `observation_status` enum; the runtime owns the stream. |
| Audit log retention | future runtime architecture | The metamodel carries the `provenance_reference` field; the runtime owns the audit log. |

This split is the binding answer to the user-supplied §8 question "should Observation be a standalone registry entity, a runtime data entity, or a hybrid metamodel construct?"; the answer is: a hybrid. The metamodel carries canonical semantics; the runtime carries operational scale. Both are required for the OpenDEAM Metric capability to work end-to-end. The future runtime architecture decisions are out of scope for this CR.

## 6. Reconciliation with existing artifacts

### 6.1 CR-10J Scenario metrics

The CR-10J Scenario metrics continue to validate as Metric definitions. The Measurement / MeasurementObservation concept is new in CR-MET-003; no CR-10J record is impacted. The future CR-10J Scenario metrics will be reusable as Metric definitions in Measurement fixtures.

### 6.2 CR-10 Outcome references

The existing `dea:Outcome` entity (line 1671) is preserved unchanged. The `dea:measures-subject` relationship is allowed to target `dea:Outcome` (per the existing `dea:measured-by` source list at line 4612 which includes `dea:Outcome`). No Outcome record is impacted.

### 6.3 The existing `dea:produces` relationship

The existing `dea:produces` relationship is extended, not replaced. The existing ApplicationComponent-to-Event / Assessment-to-AssessmentResult / BusinessProcess-to-BusinessObject uses are preserved. The new Measurement-to-MeasurementObservation case is additive. EGV-004 identity continuity is preserved.

### 6.4 The existing `dea:measured-by` relationship

The existing `dea:measured-by` relationship (line 4612) is NOT modified by this CR. The source-list extension from 7 to 17 entity types is owned by CR-MET-007 per ADR-MET-004. The `dea:measures-subject` inverse reference is a NOTIONAL claim, not a registry duplication.

## 7. Migration plan

1. Land the schema extensions in `schemas/entities/measurement.json` and `schemas/entities/measurement-observation.json`.
2. Land the canonical-source changes in `metamodel/dea-metamodel.yaml`: extend `dea:produces` (source + target), add `dea:applies-metric`, add `dea:measures-subject`.
3. Land the fixture file `tests/conformance/fixtures/measurement_observations.yaml`.
4. Land the conformance test `tests/conformance/test_023_measurement_observation.py`.
5. Regenerate `metamodel/registry/relationships.yaml` and the specification.
6. Run the full conformance test suite. All existing tests continue to pass.
7. The `dea:measures-subject` source list is 7 entity types (matching the current `dea:measured-by` source endpoint); CR-MET-007 will widen to 17.

## 8. Required test cases (per user-supplied CR-MET-003 §10)

| Case | Status |
|---|---|
| Measurement-to-Metric referential integrity | Conformance test validates `applies_metric` is a non-empty reference. |
| Subject identity and eligibility | Conformance test validates `measures_subject` is in the eligible source list. |
| Metric definition version consistency | Conformance test validates every fixture references a Metric with a specific version. |
| Observation value type compatibility | Conformance test validates numeric observations have numeric values. |
| Unit compatibility | Deferred to CR-MET-005 (units, formulas, aggregation); CR-MET-003 declares the `unit` field as a string. |
| Reporting-period consistency | Conformance test validates the `reporting_period_start` / `reporting_period_end` pair is consistent. |
| Observation uniqueness | Out of scope (runtime concern); the metamodel declares the `produced_by` reference, the runtime enforces uniqueness. |
| Provenance requirements | Conformance test validates `provenance_reference` is non-empty where present. |
| Evidence references | Conformance test validates `evidence_reference` is an array of strings. |
| Temporal validity | Conformance test validates `valid_from` <= `valid_to` where both are present. |
| Supersession and correction semantics | Conformance test validates the `observation_status: superseded` case. |
| Failed measurement produces no observations | Conformance test validates the `failed` Measurement has no corresponding `produced_by` reference. |
| Numeric observation value type | Conformance test validates numeric observations are typed numerically. |
| Ordinal observation scale reference | Deferred to CR-MET-005; the metamodel carries the value; the scale reference is CR-MET-005. |

## 9. Definition of Done

- Measurement semantics approved.
- Observation semantics approved.
- Both entities added to the normative metamodel with the full attribute set.
- Identity and lifecycle requirements established.
- Relationships and cardinalities validated.
- Multiple measurement and observation scenarios supported (4 + 6 fixtures).
- Numeric and non-numeric values supported.
- Metric version traceability established (via the `applies_metric` reference).
- Provenance and evidence references established.
- Failed and incomplete measurements supported (canonical fixture).
- Registry and CI validation updated.
- Operational storage responsibilities documented (§5).
- EGV-004 identity continuity preserved.
- ADR-013 anti-accumulation preserved.
- Runtime-vs-metamodel split documented.

## 10. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| Measurement lifecycle states (initiated, in_progress, pending_validation, etc.) | CR-MET-004 |
| Units, formulas, aggregation | CR-MET-005 |
| Baseline, target, threshold, variance, performance interpretation | CR-MET-006 |
| `dea:measured-by` source-list extension (7 -> 17) | CR-MET-007 |
| 7 temporal dimensions (reported, observation, measurement, definition, validity, baseline, target) | CR-MET-011 |
| Provenance model (entity-attached metadata) | CR-MET-011 |
| Corrects / supersedes relationship | CR-MET-011 |
| Governance objects (steward, owner, custodian, authority) | CR-MET-010 |
| AI-assisted measurement execution mode (the binding declaration) | CR-MET-004 (lifecycle) and CR-MET-012 (analytics) |
| Runtime measurement data repository/service architecture | Future (out of programme) |
| `dea:provenance` / `dea:evidence` first-class entities | Cross-cutting (out of programme) |

## 11. References

- CR-MET-000 (merged; commit 63d722a) §2 architectural posture, §4 disposition table, §5 Q1 clarification, §7 stage mapping.
- CR-MET-001 (merged; commit 2c445e4) §3.1, §3.2, §3.3, §3.4, §4.1, §4.3, §4.4.
- CR-MET-002 (merged; commit 84f10f4) §3, §4.2, §4.3.
- ADR-MET-002 (merged; commit 8a532dd) decisions 5, 6, 7, 8, 9, 10.
- ADR-MET-004 (merged; commit 8a532dd) decisions 1, 2, 3, 4, 5.
- CR-5 §27 (existing `dea:Observation` definition; line 1855).
- CR-10 (Outcome concept; line 1671).
- CR-10J (Scenario metrics; preserved as Metric definitions).
- EGV-004 (identity continuity).
- ADR-013 (Core non-accumulation).
- User-supplied CR-MET-003 (in `dea-catalog-metrics/00_inbox/CR-MET-001-005.md` lines 407..677).
- User clarification 2026-10-18 (verbatim: "Assessment score may be a measure, but not all assessments are Metrics.").
- User reminder 2026-10-18 (no `dea:Activity`).
- `metamodel/dea-metamodel.yaml` line 1519 (current `dea:PerformanceMetric`).
- `metamodel/dea-metamodel.yaml` line 1855 (current `dea:Observation`).
- `metamodel/dea-metamodel.yaml` line 3822 (current `dea:produces`).
- `metamodel/dea-metamodel.yaml` line 4612 (current `dea:measured-by`).
- `schemas/entities/measurement.json` (current placeholder; 85 lines).
- `schemas/entities/measurement-observation.json` (current placeholder; 97 lines).
- `metamodel/registry/relationships.yaml` line 285 (current `dea:produces` registry entry).
- Audit-then-specifies pattern (per dea-metamodel skill).
- Runtime-vs-metamodel responsibility split (per user-supplied §8).
