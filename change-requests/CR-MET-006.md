# CR-MET-006 -- Establish Contextual Measurement Evaluation and Performance Interpretation Semantics

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Target repository | `dea-metamodel` |
| Depends on | CR-MET-001 (merged 2c445e4); CR-MET-003 (merged 5f7cddf); CR-MET-004 (merged c49fbed); CR-MET-005 (merged 9fdf356); binding ADR-MET-005 |
| Blocks | CR-MET-007 (cross-domain enterprise `dea:measured-by` widening); CR-MET-008 (KPI/KRI/KCI designation); CR-MET-009 (catalog with classified Measurements); CR-MET-010 (governance); CR-MET-012 (analytics) |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control) |
| Kanban | T-MET umbrella #429; this CR is card #436; ADR-MET-005 is card #449 |
| Stream | Stream B (Enterprise interpretation and governance); first Stream B item. |

## 1. Background and problem statement

A Metric defines what is measured and how its value is determined. It does NOT establish whether the resulting value is good, bad, acceptable, expected, or desirable.

Interpretation depends on additional information: the subject, applicable organizational context, reporting period, expected outcome, baseline against which change is evaluated, target being pursued, threshold defining acceptable or unacceptable conditions, and relevant assessment criteria.

For example, a system availability observation of 99.5% has no universally valid performance interpretation. It depends on the service, contractual commitment, criticality, and applicable evaluation period.

OpenDEAM must therefore separate measurement from evaluation. The Metric entity defines measurement; a separate contextual evaluation layer interprets measurement.

## 2. Objective

Establish reusable semantic constructs and relationships for evaluating Observations against Baselines, Targets, Thresholds, Benchmarks, and Assessment Criteria. Separate these from the Metric definition so that the same Metric can carry different Baselines and Targets in different contexts.

## 3. Binding 8-concept architecture (audited)

The user-supplied CR-MET-006 §3 names 8 concepts. Per the audit-then-specifies pattern, each concept is audited against the existing canonical source and either (a) reused as-is, (b) extended, or (c) introduced as a new entity.

| Concept | Disposition | Rationale |
|---|---|---|
| Baseline | **NEW entity: `dea:Baseline`** | No existing concept carries the 9 binding attributes (reference Metric, subject, reference value, establishment date, reporting period, scope, methodology, source, version). Reuse would force flattening into Outcome. |
| Target | **NEW entity: `dea:PerformanceTarget`** | Existing `dea:AssessmentTarget` (line 2017) is for maturity-level targets (CR-5 §21). The user-supplied binding 9 attributes (associated Metric, target value/range, direction, effective period, owner, associated objective, approval status, rationale) are value-level. Distinct semantics warrant a separate first-class entity. **Both entities coexist**: `dea:AssessmentTarget` for maturity-level targets; `dea:PerformanceTarget` for value-level targets. |
| Threshold | **NEW entity: `dea:Threshold`** | 4 directional models (higher_is_better, lower_is_better, bounded_optimum, exact_match) and 4 levels (critical, warning, acceptable, optimal) plus escalation rule reference. No existing concept carries these. |
| Benchmark | **REUSE existing `dea:BenchmarkReference`** | `dea:BenchmarkReference` (line 2347; CR-5 §28) is "a specific comparative value drawn from a benchmark population: industry level, peer median, percentile". Exact match for the user-supplied concept. **NO new entity introduced for Benchmark.** The existing `dea:benchmarked-against` relationship (line 4xxx) is EXTENDED with `dea:PerformanceMetric` in its source list (see Section 6). |
| Expected Value | **PROPERTY of `dea:PerformanceTarget`** | The `target_value` field carries the expected value; no separate entity. Per user-supplied §3 caveat ("should not automatically become separate entity types merely because they appear in this table"). |
| Variance | **DERIVED VIEW (no entity)** | Per user-supplied §7: "Variance should normally be calculated from an Observation and an explicitly selected reference, not stored as an intrinsic Metric attribute." Variance is computable from `(ObservedValue - ReferenceValue) / ReferenceValue * 100` (relative variance) with directionality sign correction per CR-MET-005 §3.3. |
| Performance Interpretation | **NEW entity: `dea:PerformanceInterpretation`** | Carries the meaning assigned to a result under defined criteria (e.g., "exceeds target by 5%", "within tolerance", "below critical threshold"). Distinct from `dea:AssessmentResult` which carries score/level; PerformanceInterpretation carries the judgment. |
| Assessment Criterion | **REUSE existing `dea:AssessmentCriterion`** | Existing entity (line 1827; CR-5 §7) "defines what is evaluated within a dimension". Reused. The existing `dea:assesses` relationship covers "Assessment Criterion -- evaluates -- Subject/Observation". |

**Net entity delta**: 153 → 157 (4 NEW). The 3 REUSE / PROPERTY / DERIVED decisions honor the user-supplied §3 caveat and the audit-then-specifies pattern. ADR-013 anti-accumulation preserved where the existing canonical source provides fit.

## 4. Baseline semantics (NEW: `dea:Baseline`)

A Baseline represents a reference condition against which change, improvement, or deterioration can be evaluated.

The Baseline entity carries the 9 binding attributes from the user-supplied §4:

| Field | Type | Required | Description |
|---|---|---|---|
| `reference_metric_ref` | string (PerformanceMetric id) | required | The Metric this Baseline is a reference for |
| `subject_ref` | string (AssessmentSubject ref) | required | The subject being referenced |
| `reference_value` | number or string | required | The reference value or observation summary |
| `establishment_date` | string (date) | required | When the Baseline was established |
| `applicable_period` | TemporalInterval ref | required | The applicable reporting period |
| `organizational_scope` | string or array | required | The organizational scope (e.g., enterprise, business_unit, capability) |
| `measurement_methodology` | string | optional | How the reference value was determined |
| `source_evidence` | string or array | optional | Source and evidence supporting the Baseline |
| `version` | string (semver) | required | Version of the Baseline; supports baseline supersession via `dea:supersedes` |
| `approval_status` | enum (Baseline.approval_status) | required | `draft | proposed | approved | retired` |

A Baseline MAY be historical, initial, strategic, operational, regulatory, or scenario-derived. The Baseline kind is declared via the controlled vocabulary `Baseline.kind`:

| Value | Description |
|---|---|
| `historical` | Historical record (e.g., last year's measurement) |
| `initial` | Initial baseline at program inception |
| `strategic` | Strategic reference (e.g., industry standard) |
| `operational` | Operational reference (e.g., SLA target baseline) |
| `regulatory` | Regulatory reference (e.g., compliance floor) |
| `scenario_derived` | Derived from a scenario model (CR-10J) |

A Baseline MUST preserve its historical validity even when a new Baseline is established. The same Metric MAY have multiple Baselines active in different reporting periods or organizational scopes.

## 5. Target semantics (NEW: `dea:PerformanceTarget`)

A PerformanceTarget represents a desired or expected measurement result at the value level. It is distinct from `dea:AssessmentTarget` (maturity-level targets).

The PerformanceTarget entity carries the 9 binding attributes from the user-supplied §5:

| Field | Type | Required | Description |
|---|---|---|---|
| `target_metric_ref` | string (PerformanceMetric id) | required | The Metric being targeted |
| `target_subject_ref` | string | required | The subject being targeted |
| `target_scope` | string or array | required | The scope (enterprise, business domain, business unit, capability, process, product_or_service, system) |
| `target_value` | number | conditional | The desired value (numeric); mutually exclusive with `target_range` |
| `target_range` | object {min, max} | conditional | The desired range; mutually exclusive with `target_value` |
| `target_direction` | enum (PerformanceTarget.direction) | required | `increase | decrease | maintain | bounded | exact_match` |
| `effective_period` | TemporalInterval ref | required | When this Target is effective |
| `owner_ref` | string (Actor ref) | required | Responsible owner |
| `associated_objective_ref` | string (StrategicObjective or Outcome ref) | optional | The Objective/Outcome this Target supports |
| `approval_status` | enum | required | `draft | proposed | approved | retired` |
| `supporting_rationale` | string | optional | Why this Target is set |

A PerformanceTarget MUST have either `target_value` or `target_range` (mutually exclusive). The same Metric MAY have different PerformanceTargets in different contexts (scope, effective_period, subject).

The 8 target levels from user-supplied §5 (enterprise, business_domain, business_unit, capability, process, product_or_service, system) align with the `Metric.scope_classification` enum (CR-MET-002).

The existing `dea:AssessmentTarget` is preserved unchanged for maturity-level targets (CR-5 §21). The two target types are siblings in the assessment profile; both are first-class; neither subsumes the other.

## 6. Threshold semantics (NEW: `dea:Threshold`)

Thresholds establish boundaries for interpretation or action.

The Threshold entity carries the binding attributes:

| Field | Type | Required | Description |
|---|---|---|---|
| `threshold_metric_ref` | string (PerformanceMetric id) | required | The Metric being constrained |
| `threshold_value` | number or object {min, max} | required | The boundary value(s) |
| `threshold_level` | enum (Threshold.level) | required | `critical | warning | acceptable | optimal` |
| `direction` | enum (Threshold.direction) | required | The directional model |
| `effective_period` | TemporalInterval ref | required | When this Threshold is effective |
| `owner_ref` | string (Actor ref) | optional | Responsible owner |
| `escalation_rule_ref` | string | optional | Reference to an escalation rule |

The 4 directional models per user-supplied §6:

| Direction | Description |
|---|---|
| `higher_is_better` | Higher values are better (e.g., customer retention) |
| `lower_is_better` | Lower values are better (e.g., incident frequency) |
| `bounded_optimum` | Bounded optimum range; neither too high nor too low is desirable |
| `exact_match` | Exact match to a target value (e.g., regulatory pass/fail) |

The 4 levels per user-supplied §6 table:

| Level | Illustrative interpretation |
|---|---|
| `critical` | Requires immediate intervention |
| `warning` | Indicates elevated concern |
| `acceptable` | Within defined tolerance |
| `optimal` | Meets or exceeds desired performance |

A single Threshold declares one (level, value, direction) tuple. A Metric MAY have multiple Thresholds (e.g., one critical, one warning); distinguished by `threshold_level`.

## 7. Variance and Performance Interpretation (NEW: `dea:PerformanceInterpretation`)

Per the binding disposition (Section 3), Variance is a derived view, not an entity. The variance calculation is:

```
AbsoluteVariance  = ObservedValue - ReferenceValue
RelativeVariance  = (ObservedValue - ReferenceValue) / ReferenceValue * 100
```

The sign and interpretation account for the Metric's directionality (per CR-MET-005 §3.3 `Metric.directionality`):

| Metric direction | Observed > Target | Observed < Target |
|---|---|---|
| `higher_is_better` | Positive variance | Negative variance |
| `lower_is_better` | Negative variance | Positive variance |
| `target_band` (target range) | Depends on band position | Depends on band position |
| `categorical` | N/A (use categorical interpretation) | N/A |

A PerformanceInterpretation carries:

| Field | Type | Required | Description |
|---|---|---|---|
| `interprets_metric_ref` | string (PerformanceMetric id) | required | The Metric being interpreted |
| `interprets_observation_ref` | string (MeasurementObservation id) | required | The Observation being interpreted |
| `interpretation_kind` | enum (PerformanceInterpretation.kind) | required | `variance_evaluation | threshold_evaluation | benchmark_evaluation | composite_judgment` |
| `interpretation_state` | enum (PerformanceInterpretation.state) | required | `exceeds_target | meets_target | within_tolerance | warning | critical | unknown` |
| `reference_used` | string | required | Which reference was used (Baseline ref, Target ref, Threshold ref, BenchmarkReference ref) |
| `absolute_variance` | number | optional | Computed absolute variance |
| `relative_variance` | number | optional | Computed relative variance (percentage) |
| `narrative` | string | optional | Human-readable interpretation |
| `evaluated_by_ref` | string (Actor ref) | optional | Who/what performed the interpretation |
| `evaluated_at` | string (datetime) | required | When the interpretation was made |

The PerformanceInterpretation entity is the auditable record of how an Observation was interpreted against a specific reference. The same Observation MAY have multiple PerformanceInterpretations (e.g., one against each Threshold level; one against the Target).

The interpretation_state enum is the 6-value binding:

| State | Meaning |
|---|---|
| `exceeds_target` | Above the target (for higher_is_better) |
| `meets_target` | At the target |
| `within_tolerance` | Within defined acceptable bounds |
| `warning` | Warning level per Threshold |
| `critical` | Critical level per Threshold |
| `unknown` | Cannot be determined (e.g., missing reference) |

## 8. Relationship architecture (audited against canonical source)

The user-supplied §8 names 10 relationships. Each is audited per the dea-metamodel skill's audit-then-specifies pattern.

| Source | Proposed | Target | Audit verdict | Final decision |
|---|---|---|---|---|
| Baseline | references | Metric | No existing fit; `dea:measured-by` is the wrong semantic direction (source is being measured, not referencing). | **NEW** `dea:references` (Baseline → PerformanceMetric) |
| Baseline | applies to | Subject | No existing fit. | **NEW** `dea:applies-subject` (Baseline → AssessmentSubject; shared with PerformanceTarget) |
| Target | specifies desired result for | Metric | `dea:targets` exists but its target type is `dea:Outcome`, not `dea:PerformanceMetric`. Different semantic. | **NEW** `dea:specifies-target` (PerformanceTarget → PerformanceMetric) |
| Target | applies to | Subject | As above | shared with Baseline `dea:applies-subject` |
| Threshold | constrains/interprets | Metric | `dea:constrains` exists (line 4xxx; source types include Constraint/Guardrail/Regulation/Requirement; target types include ApplicationComponent/BusinessProcess). Threshold constants are not in the source list; `dea:PerformanceMetric` is not in the target list. | **EXTEND** `dea:constrains` source list with `dea:Threshold`; extend target list with `dea:PerformanceMetric`. Semantic preserved: "source constrains target". |
| Benchmark | compares against | Metric | `dea:benchmarked-against` exists with direction source=thing-being-benchmarked, target=BenchmarkReference. To use Metric → BenchmarkReference direction, extend source list. | **EXTEND** `dea:benchmarked-against` source list with `dea:PerformanceMetric`. (The user's "Benchmark compares against Metric" wording is the inverse direction; we use the existing direction because it matches the data flow: a Metric is benchmarked against a BenchmarkReference.) |
| Performance Interpretation | evaluates | Observation | No existing fit. | **NEW** `dea:interprets` (PerformanceInterpretation → MeasurementObservation). Note: `dea:interprets` is intentionally distinct from `dea:assesses` which is the assessment-side "result evaluates" semantic; PerformanceInterpretation interprets a MEASUREMENT observation, not an assessment subject. |
| Assessment Criterion | evaluates | Subject/Observation | Existing `dea:assesses` (line 5028) covers Assessment-Dimension → Entity + AssessmentResult → AssessmentSubject. | **REUSE** `dea:assesses`. |
| Outcome | is evaluated using | Metric/Observation | Existing `dea:assessed-by` inverse `dea:assesses` covers Outcome → Metric. | **REUSE** existing relationship. |
| Strategic Objective | is supported by | Target | No existing fit. | **NEW** `dea:has-target` (StrategicObjective → PerformanceTarget). |

**Net relationship delta**: 107 → 112 (5 NEW + 2 EXTENDED). The 3 REUSE / EXTEND decisions honor audit-then-specifies where the existing canonical source provides fit.

## 9. Controlled vocabulary additions

| Vocabulary | Cardinality | Purpose |
|---|---|---|
| `Baseline.kind` | 6 values | historical, initial, strategic, operational, regulatory, scenario_derived |
| `Baseline.approval_status` | 4 values | draft, proposed, approved, retired |
| `PerformanceTarget.direction` | 5 values | increase, decrease, maintain, bounded, exact_match |
| `PerformanceTarget.approval_status` | 4 values | draft, proposed, approved, retired |
| `Threshold.level` | 4 values | critical, warning, acceptable, optimal |
| `Threshold.direction` | 4 values | higher_is_better, lower_is_better, bounded_optimum, exact_match |
| `PerformanceInterpretation.kind` | 4 values | variance_evaluation, threshold_evaluation, benchmark_evaluation, composite_judgment |
| `PerformanceInterpretation.state` | 6 values | exceeds_target, meets_target, within_tolerance, warning, critical, unknown |

The vocabulary file `metamodel/vocabularies/classifications.yaml` version is bumped from 0.11.0 to 0.12.0.

## 10. Canonical-source changes

### 10.1 New entity blocks in `metamodel/dea-metamodel.yaml`

4 new entity blocks inserted at the end of the `entities:` list (lines 153+ in the canonical source):

```yaml
- id: dea:Baseline
  name: Baseline
  definition: "A reference measurement or established starting condition against which change, improvement, or deterioration can be evaluated (CR-MET-006 binding). 9 binding attributes per user-supplied section 4."
  layer: null
  dimension: measurement-dimension
  abstract: false
  status: normative
  lifecycle: proposed
  artifacts:
    json_schema: schemas/entities/baseline.json
    sqlite_table: baselines
    pydantic_model: pydantic/baseline.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: profile
    profile: dea:assessment

- id: dea:PerformanceTarget
  name: Performance Target
  definition: "A value-level desired measurement result (CR-MET-006 binding). 9 binding attributes per user-supplied section 5. Sibling of dea:AssessmentTarget (maturity-level). NOT a re-membership; NOT a dea:AssessmentTarget extension. The two target types coexist."
  layer: null
  dimension: measurement-dimension
  abstract: false
  status: normative
  lifecycle: proposed
  artifacts:
    json_schema: schemas/entities/performance-target.json
    sqlite_table: performance_targets
    pydantic_model: pydantic/performance_target.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: profile
    profile: dea:assessment

- id: dea:Threshold
  name: Threshold
  definition: "A directional boundary used to classify or trigger an evaluation (CR-MET-006 binding). 4 directional models and 4 levels per user-supplied section 6."
  layer: null
  dimension: measurement-dimension
  abstract: false
  status: normative
  lifecycle: proposed
  artifacts:
    json_schema: schemas/entities/threshold.json
    sqlite_table: thresholds
    pydantic_model: pydantic/threshold.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: profile
    profile: dea:assessment

- id: dea:PerformanceInterpretation
  name: Performance Interpretation
  definition: "The meaning assigned to a result under defined criteria (CR-MET-006 binding). Carries interpretation_state (exceeds_target/meets_target/within_tolerance/warning/critical/unknown), reference_used, and computed variance. Sibling of dea:AssessmentResult (which carries score); PerformanceInterpretation carries judgment."
  layer: null
  dimension: measurement-dimension
  abstract: false
  status: normative
  lifecycle: proposed
  artifacts:
    json_schema: schemas/entities/performance-interpretation.json
    sqlite_table: performance_interpretations
    pydantic_model: pydantic/performance_interpretation.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: profile
    profile: dea:assessment
```

### 10.2 New relationships in `metamodel/dea-metamodel.yaml`

5 NEW + 2 EXTENDED relationships:

```yaml
# NEW: dea:references (Baseline -> PerformanceMetric)
- id: dea:references
  name: References
  definition: "The source references the target as a semantic anchor (CR-MET-006 binding). Specifically: Baseline references the Metric it is a Baseline FOR."
  category: structural
  direction: source-to-target
  source:
    types:
    - dea:Baseline
  target:
    types:
    - dea:PerformanceMetric
  cardinality: "1..1"
  inverse: dea:referenced-by
  symmetric: false
  temporal: true
  provenance: required

# NEW: dea:applies-to (Baseline|PerformanceTarget -> AssessmentSubject)
- id: dea:applies-to
  name: Applies To
  definition: "The source applies to / concerns the target subject (CR-MET-006 binding)."
  category: structural
  direction: source-to-target
  source:
    types:
    - dea:Baseline
    - dea:PerformanceTarget
  target:
    types:
    - dea:Entity
    - dea:AssessmentSubject
  cardinality: "1..1"
  inverse: dea:has-applied
  symmetric: false
  temporal: true
  provenance: required

# NEW: dea:specifies-target (PerformanceTarget -> PerformanceMetric)
- id: dea:specifies-target
  name: Specifies Target
  definition: "The source specifies a desired target value for the target Metric (CR-MET-006 binding)."
  category: structural
  direction: source-to-target
  source:
    types:
    - dea:PerformanceTarget
  target:
    types:
    - dea:PerformanceMetric
  cardinality: "1..1"
  inverse: dea:has-target-specification
  symmetric: false
  temporal: true
  provenance: required

# EXTEND: dea:constrains (add Threshold to source; PerformanceMetric to target)
- id: dea:constrains
  name: Constrains
  # ... existing fields ...
  source:
    types:
    - dea:CollaborationAgreement
    - dea:Constraint
    - dea:Guardrail
    - dea:Regulation
    - dea:Requirement
    - dea:Threshold      # ADDED CR-MET-006
  target:
    types:
    - dea:ApplicationComponent
    - dea:ArchitectureElement
    - dea:BusinessProcess
    - dea:BusinessService
    - dea:SolutionComponent
    - dea:PerformanceMetric  # ADDED CR-MET-006

# EXTEND: dea:benchmarked-against (add PerformanceMetric to source)
- id: dea:benchmarked-against
  name: Benchmarked Against
  # ... existing fields ...
  source:
    types:
    - dea:AssessmentResult
    - dea:BusinessCapability
    - dea:BusinessProcess
    - dea:BusinessService
    - dea:Technology
    - dea:PerformanceMetric  # ADDED CR-MET-006

# NEW: dea:interprets (PerformanceInterpretation -> MeasurementObservation)
- id: dea:interprets
  name: Interprets
  definition: "The source interprets the target Observation under defined criteria (CR-MET-006 binding). The semantic is judgment/evaluation against a reference, distinct from dea:assesses which is assessment-side scoring."
  category: assessment
  direction: source-to-target
  source:
    types:
    - dea:PerformanceInterpretation
  target:
    types:
    - dea:MeasurementObservation
    - dea:Observation
  cardinality: "0..*"
  inverse: dea:interpreted-by
  symmetric: false
  temporal: true
  provenance: required

# NEW: dea:has-target (StrategicObjective -> PerformanceTarget)
- id: dea:has-target
  name: Has Target
  definition: "The StrategicObjective is supported by the PerformanceTarget (CR-MET-006 binding)."
  category: governance
  direction: source-to-target
  source:
    types:
    - dea:StrategicObjective
  target:
    types:
    - dea:PerformanceTarget
  cardinality: "0..*"
  inverse: dea:supports-objective
  symmetric: false
  temporal: true
  provenance: required
```

### 10.3 New schema files

4 new schemas in `schemas/entities/`:

- `baseline.json` (~95 lines)
- `performance-target.json` (~115 lines)
- `threshold.json` (~95 lines)
- `performance-interpretation.json` (~110 lines)

### 10.4 Relationship-instance.json enum extension

The `schemas/relationships/relationship-instance.json` enum is extended to include the 5 new relationships (alphabetical placement):
- `applies-to` (between `applies-metric` and `approves`)
- `benchmarks` (between `benchmarked-against` and `bounded-by`)
- `interprets` (between `integrates-with` and `interacts-with`)
- `references` (between `recorded-by` and `related-to`)
- `specifies-target` (after `specializes-by`/`specializes`)
- `has-target` (after `has-status`)

(Plus the existing 2 EXTENDED relationships `constrains` and `benchmarked-against` which already have enum entries.)

### 10.5 Controlled-vocabulary additions

8 new entries in `metamodel/vocabularies/classifications.yaml` (version 0.11.0 → 0.12.0).

## 11. Migration plan

1. Land the 4 entity blocks in `metamodel/dea-metamodel.yaml` (153 → 157 entities).
2. Land the 5 NEW relationships + 2 EXTENDED relationships in `metamodel/dea-metamodel.yaml` (107 → 112 relationships).
3. Land the 4 new schema files.
4. Extend `schemas/relationships/relationship-instance.json` enum.
5. Land the 8 controlled-vocabulary entries; version bump 0.11.0 → 0.12.0.
6. Land the fixture file `tests/conformance/fixtures/performance_evaluation.yaml`.
7. Land the conformance test `tests/conformance/test_026_performance_evaluation.py`.
8. Run full test suite; regenerate registry + specification.

The 5 existing Stream A CRs continue to validate; existing catalog records continue to validate. The new entities are first-class additions; they don't supersede or modify existing entities.

## 12. Definition of Done

- All 4 new entities established (`dea:Baseline`, `dea:PerformanceTarget`, `dea:Threshold`, `dea:PerformanceInterpretation`).
- 5 NEW relationships introduced.
- 2 EXISTING relationships extended (`dea:constrains`, `dea:benchmarked-against`).
- 8 controlled-vocabulary entries added.
- 4 new schema files validated.
- Variance remains a derived view (not an entity), per user-supplied §7 closing.
- `dea:AssessmentTarget` preserved unchanged (maturity-level targets).
- `dea:Outcome` references remain compatible (CR-10 backward compatibility gate).
- EGV-004 identity continuity preserved.
- ADR-013 anti-accumulation honored where existing canonical source provides fit (3 of 8 concepts REUSE / PROPERTY / DERIVED).
- Conformance tests validate the cross-field invariants.
- **Stream B item 1 sealed.**

## 13. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| KPI/KRI/KCI designation | CR-MET-008 |
| Cross-domain `dea:measured-by` widening (10 → 17 source entities) | CR-MET-007 |
| Catalog establishment with classified Measurements | CR-MET-009 |
| Governance objects (steward, owner, custodian, authority) on Baseline/Target/Threshold | CR-MET-010 |
| Full calculation lineage model | CR-MET-011 |
| Full uncertainty and confidence model on PerformanceInterpretation | CR-MET-012 |
| Automatic variance calculation at runtime | runtime concern (metamodel declares the semantic; runtime computes) |

## 14. References

- CR-MET-000 (merged; commit 63d722a) §4 disposition table (Baseline/Target/Threshold/PerformanceInterpretation/Benchmark/Variance/Expected-Value positions).
- CR-MET-001 (merged; commit 2c445e4) §3.1 (Metric definition).
- CR-MET-003 (merged; commit 5f7cddf) §4.1 (Measurement/MeasurementObservation).
- CR-MET-005 (merged; commit 9fdf356) §3.3 (Directionality vocabulary), §3.6 (Precision/rounding).
- ADR-MET-005 (this slice; authored in PR #183 alongside this CR).
- CR-5 §21 (existing `dea:AssessmentTarget`; maturity-level targets).
- CR-5 §28 (existing `dea:BenchmarkReference`; the binding match for user-supplied Benchmark concept).
- CR-5 §30 (existing `dea:AssessmentGap`; the derived-gap precedent; reinforces Variance-as-derived-view).
- CR-10J (Scenario metrics; Scenario-derived Baseline kind).
- User-supplied CR-MET-006 §1..§10 (in `dea-catalog-metrics/00_inbox/CR-MET-006-012.md` lines 177..425).
- Audit-then-specifies pattern (per dea-metamodel skill).
- ADR-013 (Core non-accumulation).
- EGV-004 (identity continuity).