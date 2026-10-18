# CR-MET-000 -- Metric Capability Establishment and Existing Work Reconciliation

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | None (this is the foundation CR) |
| Blocks | CR-MET-001, ADR-MET-001..004, and by extension the full 12-CR programme |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control); dea-architecture-framework (positioning and allocation); dea-catalog-metrics (reusable definitions) |
| Kanban | T-MET umbrella card #429; this CR is card #430 |

## 1. Objective

Establish Metric as a first-class, foundational, reusable semantic capability within OpenDEAM. The capability must describe what an enterprise measures, how it measures it, what results it obtains, how those results are interpreted, and how they inform enterprise decisions.

Before any new entity is introduced, this CR performs a structured reconciliation of every existing Metric, Measurement, Observation, Indicator, Measure, Unit, Target, AggregationRule, Outcome, and AssessmentResult declaration, every relevant ADR, and every existing schema, registry, and CI convention. The reconciliation output is the input to the rest of the programme.

The reconciliation prevents the new programme from inadvertently creating a second, incompatible measurement architecture.

## 2. Architectural posture (per the user-supplied CR-MET-000 strategic document)

Five architectural principles are binding on the entire programme.

1. **Metric is foundational.** Metric is a reusable, first-class metamodel entity. It is not an attribute of anything else.
2. **Measurement is distinct.** A Metric defines what and how to measure. A Measurement represents the execution or application of that definition. The two are not the same concept and the metamodel must not collapse them.
3. **Results are distinct.** An Observation captures the resulting value and its context. Observations are not Metric attributes.
4. **Interpretation is distinct.** An Assessment interprets Observations against Targets, Thresholds, criteria, and expectations. Interpretation logic lives in the assessment layer, not on Metric.
5. **Measurement is cross-domain.** Metrics can be associated with virtually any relevant OpenDEAM entity. Metric must not be allocated to a single profile, layer, or domain.

These principles drive every disposition decision in Section 4.

## 3. Reconciliation scope (every artifact audited)

The reconciliation covers the following classes of artifact. Every artifact receives an explicit disposition; the absence of a disposition is a programme failure.

### 3.1 Canonical metamodel source (`metamodel/dea-metamodel.yaml`)

| Entity / artifact | Line | Citation | Disposition |
|---|---|---|---|
| `dea:PerformanceMetric` | 1519 | ADR-0002 D1; profile `dea:assessment`; dimension `measurement-dimension`; class_alias MTR; catalog_repo `dea-catalog-metrics`; lifecycle `existing` | **EXTEND** -- promote membership from profile to core (per Principle 1: foundational). Additive enrichment of attributes per CR-MET-001. Do NOT deprecate; the existing entity is the foundation. |
| `dea:Outcome` | 1671 | CR-4 §14; metric/baseline/target/evidence attributes in the existing semantic | **RETAIN** -- the Outcome entity already references metric, baseline, target, unit, confidence, timeframe, evidence (CR-10J inheritance). Preserve every existing reference. |
| `dea:Indicator` | 1835 | CR-5 §8; profile `dea:assessment`; "the observable signal used to evaluate a criterion" | **EXTEND** -- Indicator sits under Metric semantically; CR-MET-001 may add a `kind` discriminator or repurpose Indicator as the assessment-side observation of a Metric. The disposition: keep Indicator as the assessment-profile observable signal; do not collapse it into Metric. |
| `dea:Observation` | 1855 | CR-5 §27; profile `dea:assessment`; "a raw measured or observed fact collected as input to assessment" | **REFACTOR** -- the user-supplied CR-MET-003 redefines Observation as the *result of a Measurement*. The two definitions overlap but are not identical. The disposition (per user clarification 2026-10-18): the new `dea:MeasurementObservation` is a distinct first-class entity (a sibling of `dea:Observation`); the existing assessment-side `dea:Observation` stays in `dea:assessment` profile (CR-5 §27 input concept). The two are differentiated by name and profile; no re-membership, no supersession. |
| `dea:Measure` | 1875 | CR-5 §9; profile `dea:assessment`; "a quantifiable observation of an indicator" | **CONSOLIDATE** -- the new Measurement entity (CR-MET-003) absorbs the Measure semantics. Mark `dea:Measure` deprecated; route new records through Measurement. Migration manifest: see Section 6. |
| `dea:Score` | 1895 | CR-5 §11; profile `dea:assessment`; "a numerical or ordinal evaluation derived from measures against a declared scale" | **RETAIN** -- Score belongs in the assessment-profile sub-tree; the new Metric does not subsume it. CR-MET-002 may add it as a metric `measurement_type` value. |
| `dea:Scale` | 1915 | (not in scope here; CR-5 §12); "the scale over which a maturity model's levels are defined" | **RETAIN** -- Scale is a maturity-model concept. CR-MET-005 introduces `MeasurementScale` as a new entity; the two are distinct (maturity scales are not measurement scales). The disposition: name-collision guard; MeasurementScale uses the `dea:MeasurementScale` id; Scale retains the dea:Scale id. |
| `dea:Unit` | 1935 | CR-5 §9/Phase 2; profile `dea:assessment`; "a standard quantity in which a measure is expressed" | **EXTEND** -- per user clarification 2026-10-18, `dea:Unit` is a justifiable abstract root; CR-MET-005 introduces `dea:MeasurementUnit` as a SPECIALIZATION of `dea:Unit` (using `dea:specializes`); `dea:Unit` is the abstract root, no rename, no deprecation, no EGV-004 continuity issue. Kernel+specialization template per CR-016 / ADR-015. |
| `dea:AssessmentTarget` | 2017 | CR-5 §21; profile `dea:assessment`; "a desired future value or maturity level" | **REFACTOR** -- the user-supplied CR-MET-006 investigates Baseline/Target/Threshold as first-class entities. The existing AssessmentTarget is profile-scoped; the new Target is foundational. The disposition: keep `dea:AssessmentTarget` in the assessment profile for maturity-level targets; introduce `dea:PerformanceTarget` (or `dea:Target`) as a foundational entity that AssessmentTarget may specialize. Disposition decided in CR-MET-000 Section 5 (decision point Q2). |
| `dea:AssessmentGap` | 2037 | CR-5 §30; profile `dea:assessment`; "the derived difference between a current result and a target" | **RETAIN** -- Gap is derived from Result and Target; remains assessment-profile. CR-MET-006 may reference it from the new interpretation layer but does not duplicate. |
| `dea:AggregationRule` | 2135 | CR-5 §25; profile `dea:assessment`; "how lower-level results combine into higher-level results" | **EXTEND** -- per user clarification 2026-10-18, `dea:AggregationRule` is a justifiable abstract root; CR-MET-005 introduces `dea:MeasurementAggregation` as a SPECIALIZATION of `dea:AggregationRule` (using `dea:specializes`); `dea:AggregationRule` is the abstract root, no rename. Kernel+specialization template per CR-016 / ADR-015. Future CRs may add `dea:AssessmentAggregation` as a parallel specialization for the assessment context. |
| `dea:ScoringRule` | 2155 | CR-5 §11/§25; profile `dea:assessment` | **RETAIN** -- ScoringRule stays assessment-profile; not a Metric concept. |
| `dea:assesses` | 5028 | source: Assessment, AssessmentFramework, AssessmentDimension, AssessmentResult; target: Entity, AssessmentSubject | **RETAIN** -- unchanged. |
| `dea:assessed-by` | 4584 | source: AIMLModel, BusinessCapability, BusinessProcess, SolutionComponent, TechnologyRadarEntry; target: Experiment, PerformanceMetric | **EXTEND** -- CR-MET-007 extends the source list to include all entities that may carry measurement-driven assessment. |
| `dea:measured-by` | 4612 | source: AIMLModel, ApplicationComponent, BusinessCapability, BusinessProcess, BusinessService, Outcome, StrategicObjective; target: PerformanceMetric | **EXTEND** -- CR-MET-007 extends the source list. Per user reminder 2026-10-18, do NOT add `dea:Activity` (not canonical); use `dea:BusinessProcess` (line 592; L3) decomposition via the existing catalog-internal Activity/Task hierarchy. |
| `dea:measures` | (inverse of measured-by) | not separately registered; the `dea:measured-by` inverse declaration covers it | **RETAIN** -- unchanged. |

### 3.2 Earlier CR-10J Scenario metrics work (`change-requests/CR-010.md` §11)

| Concept (CR-10J) | Disposition |
|---|---|
| `Metric` (reusable semantic object) | **RETAIN** -- CR-MET-001 formalizes this as `dea:PerformanceMetric` (or superseding name) with the six attributes CR-10J enumerated: definition, unit, calculation, source, baseline, target. |
| Metric attributes: `definition`, `unit`, `calculation`, `source`, `baseline`, `target` | **EXTEND** -- per the user-supplied CR-MET-001, Metric gets additional attributes (subject_concept, measurement_type, directionality, applicability, owner, steward, lifecycle_status, version, classification). The CR-10J attributes become the required baseline; the new attributes are additive. |
| `Baseline` and `Target` as Metric attributes | **REFACTOR** -- the user-supplied CR-MET-006 investigates making these independent first-class entities. The CR-MET-000 disposition: Baseline/Target move out of the Metric entity and into new first-class entities with `Metric` -> `has-baseline` and `Metric` -> `has-target` relationships. This preserves CR-10J semantics (the Outcome's metric reference still resolves to a target) while removing the "static attribute on Metric" anti-pattern. |

### 3.3 Existing ADRs (`docs/adrs/` and `change-requests/CR-001..CR-012`)

| ADR / CR | Disposition |
|---|---|
| ADR-0002 D1 (PerformanceMetric in orthogonal_allocators.measurement-dimension; no layer) | **RETAIN** -- binding. The Metric entity is cross-cutting; it does not live on a layer. |
| CR-005 (Assessment & Measurement) | **RETAIN** -- CR-MET-000 is the metamodel extension CR for the measurement sub-tree; it does not amend CR-005's assessment semantics. CR-AM-02..CR-AM-11 (Assessment Metamodel v1) already covers the assessment-profile side. |
| CR-010 §11 (CR-10J Scenario metrics) | **RETAIN** -- the Metric concept is preserved and extended. |
| CR-012 (Enterprise Intelligence & Advanced Agentic Runtime) | **RETAIN** -- CR-MET-012 (decision intelligence integration) extends CR-012's signal-promotion and governed-agentic-action layer. |
| DEA-ID-000 / CR-012 (identity and governance) | **RETAIN** -- every new Metric / Measurement / Observation record conforms to the General Entity System governance standard. EGV-004 identity continuity is enforced for any renamed or superseded entity. |
| CR-016 / ADR-015 (kernel+specialization template) | **RETAIN** -- new Metric / Measurement / Observation entities follow the same template (e.g. abstract kind with profile-level specializations). |
| CR-022 (Metamodel Artifact and Conformance Closure) | **RETAIN** -- the closure-CR pattern from the IS Semantic Architecture programme applies to this programme too; a closure CR is added at the end of CR-MET-012 to populate `artifacts.*` paths, regenerate hand-maintained artefacts, and author the four closure documents. |

### 3.4 Existing registry, schema, and CI conventions

| Asset | Disposition |
|---|---|
| `metamodel/registry/entities.yaml` (GENERATED, per D-6 in CR-018) | **RETAIN** -- regenerated after each canonical-source change. Hand-edits are forbidden. |
| `metamodel/registry/relationships.yaml` (GENERATED) | **RETAIN** -- regenerated after each canonical-source change. |
| `specification/catalogues/*` (GENERATED) | **RETAIN** -- regenerated after each canonical-source change. |
| `specification/{semantic-inventory,vocabulary}.yaml` (GENERATED) | **RETAIN** -- regenerated after each canonical-source change. |
| `schemas/entities/metric.json` | **EXTEND** -- the existing schema is preserved; CR-MET-001 adds the new attributes. Backward compatibility: every existing record continues to validate. |
| `schemas/entities/indicator.json`, `observation.json`, `measure.json`, `unit.json`, `assessment-target.json`, `aggregation-rule.json` | **EXTEND** or **DEPRECATE** per the per-entity disposition above. New schemas may be required (`schemas/entities/measurement-unit.json`, `schemas/entities/measurement-scale.json`, etc.). |
| `tests/conformance/` (133 tests) | **EXTEND** -- the conformance suite grows with each new entity. Test-001 (lifecycle whitelist), test-003 (no inline relationship-state), test-008 (CATEGORIES controlled vocabulary) are the affected tests. |
| `tests/runtime/` (290 tests) | **EXTEND** -- new tests per new schema. |
| `sqlite/schema.sql` (hand-maintained CHECK constraints) | **EXTEND** -- the `entities.type` and `relationships.relationship_type` CHECK lists are extended in the closure CR. |
| `typescript/src/interfaces.ts` (hand-maintained) | **EXTEND** -- new interface per new entity. |
| `ttl/dea-metamodel-ontology.ttl` (hand-maintained) | **EXTEND** -- new `owl:Class` per new entity; new `owl:ObjectProperty` per new relationship. |
| `validate-authorship.yml` (CI gate per CR-MM-04 R1) | **RETAIN** -- every commit in the new programme passes the authorship cardinal rule. |

### 3.5 Existing catalog references (the dea-catalog-* repos)

| Repo | Disposition |
|---|---|
| `dea-catalog-metrics` | **EXTEND** -- CR-MET-009 establishes the catalog; current scaffold is preserved (LICENSE, NOTICE, README.md, metamodel-pointer.yaml). The metamodel-pointer's `metamodel.entity_id: dea:entity-metric` legacy form is migrated to `dea:PerformanceMetric` (or superseding canonical id) with `legacy_ids: [dea:entity-metric, Metric]`. |
| Other `dea-catalog-*` repos | **RETAIN** -- unaffected by this programme directly. CR-MET-007 may add a `measures` relationship target to records in those catalogs; the cascade is per-CR scope. |

## 4. Disposition summary (the table the user requires)

This is the explicit disposition table the user-supplied CR-MET-000 requires. Every discovery receives exactly one disposition.

| Discovery | Disposition | Owner CR | Rationale |
|---|---|---|---|
| `dea:PerformanceMetric` | EXTEND | CR-MET-001 | Re-membership to core; attribute enrichment. |
| `dea:Outcome` | RETAIN | (n/a; preserved) | Metric/baseline/target/evidence attributes preserved as-is. |
| `dea:Indicator` | EXTEND | CR-MET-002 | Add classification discriminator; retain assessment-profile meaning. |
| `dea:Observation` | REFACTOR | CR-MET-003 | Broaden definition to subsume assessment-profile + new measurement-result semantics; re-membership from profile to core. |
| `dea:Measure` | CONSOLIDATE | CR-MET-003 | Superseded by Measurement; deprecate with EGV-004 continuity. |
| `dea:Score` | RETAIN | (n/a) | Assessment-profile; not a Metric concept. |
| `dea:Scale` | RETAIN | (n/a) | Maturity-model scale; distinct from new MeasurementScale. |
| `dea:Unit` | EXTEND | CR-MET-005 | `dea:MeasurementUnit` is a SPECIALIZATION of `dea:Unit` (kernel+specialization template per CR-016 / ADR-015). `dea:Unit` is the abstract root, no rename, no deprecation. |
| `dea:AssessmentTarget` | REFACTOR | CR-MET-006 | Keep for maturity-level targets; introduce foundational `dea:PerformanceTarget` (or `dea:Target`). |
| `dea:AssessmentGap` | RETAIN | (n/a) | Assessment-profile; derived. |
| `dea:AggregationRule` | EXTEND | CR-MET-005 | `dea:MeasurementAggregation` is a SPECIALIZATION of `dea:AggregationRule` (kernel+specialization template). `dea:AggregationRule` is the abstract root, no rename. Future CRs may add `dea:AssessmentAggregation` as a parallel specialization. |
| `dea:ScoringRule` | RETAIN | (n/a) | Assessment-profile. |
| `dea:assesses` | RETAIN | (n/a) | Unchanged. |
| `dea:assessed-by` | EXTEND | CR-MET-007 | Source list extended. |
| `dea:measured-by` | EXTEND | CR-MET-007 | Source list extended; do NOT add `dea:Activity` (user reminder). |
| `dea:measures` | RETAIN | (n/a) | Inverse of `dea:measured-by`; unchanged. |
| CR-10J `Metric` (definition, unit, calculation, source, baseline, target) | EXTEND | CR-MET-001 | The CR-10J six-attribute baseline is the required floor; CR-MET-001 adds further required attributes. |
| CR-10J `Baseline`, `Target` (as Metric attributes) | REFACTOR | CR-MET-006 | First-class entities; remove as Metric attributes. |
| ADR-0002 D1 (measurement-dimension) | RETAIN | (n/a) | Binding. |
| CR-005 (Assessment & Measurement) | RETAIN | (n/a) | Assessment profile preserved. |
| CR-010 §11 (CR-10J Scenario metrics) | RETAIN | (n/a) | Metric concept preserved and extended. |
| CR-012 (Enterprise Intelligence) | RETAIN | CR-MET-012 | CR-MET-012 extends it. |
| DEA-ID-000 / CR-012 (identity / governance) | RETAIN | (all CRs) | Cardinal rule applied per CR. |
| CR-016 / ADR-015 (kernel+specialization) | RETAIN | (all CRs) | New entities follow the template. |
| CR-022 (closure pattern) | RETAIN | CR-MET-013 (closure CR, to be added) | Closure CR at the end of the programme. |
| `metamodel/registry/*` (generated) | RETAIN | (all CRs) | Regenerate on every canonical-source change. |
| `schemas/entities/*.json` | EXTEND | (per CR) | New schemas; backward compatibility. |
| `tests/conformance/`, `tests/runtime/` | EXTEND | (per CR) | New tests per new entity. |
| `sqlite/schema.sql`, `typescript/src/interfaces.ts`, `ttl/dea-metamodel-ontology.ttl` | EXTEND | closure CR | Hand-maintained; closure CR owns the population. |
| `validate-authorship.yml` | RETAIN | (all CRs) | Cardinal rule. |
| `dea-catalog-metrics` | EXTEND | CR-MET-009 | Catalog-establishment CR. |
| Other `dea-catalog-*` repos | RETAIN | (n/a) | Direct cascade deferred to CR-MET-007. |

**No discoveries result in DEPRECATE without EGV-004 identity continuity, and no discoveries result in INTRODUCE without the audit trail above.**

## 5. Decision points for the user (the structural-change dialogue)

The reconciliation surfaces 22 questions whose answers bind the rest of the programme. Per the structural-change protocol, each is named with options; the user confirms in batch.

Q1..Q5 are the per-entity questions from the round-1 reconciliation. Q6..Q22 are the structural / architectural / scope questions surfaced by the comprehensive user-supplied CRs (CR-MET-000, CR-MET-006..012). The disposition table (Section 4) carries the per-entity recommendations; the questions below cover the structural and architectural decisions that the per-entity dispositions depend on.

### 5.1 Q1 -- `dea:Observation` vs new measurement-side Observation (REFRAMED per user clarification 2026-10-18)

The original Q1 proposed re-membership of the existing `dea:Observation` from `dea:assessment` to `dea:core`. The user insight (verbatim 2026-10-18): "Assessment score may be a measure, but not all assessments are Metrics. So am not clear why you want to membership from dea:assessment."

The reframing: the existing `dea:Observation` (CR-5 §27; "a raw measured or observed fact collected as input to assessment") is the assessment-side *input* concept. The new CR-MET-003 Observation ("an identifiable record of an observed value associated with a Metric and its measurement context") is the measurement-side *output* concept. They are different entities on the assessment-vs-measurement axis. Re-membership of the existing entity to `dea:core` is conceptually wrong because the assessment-side input is not a Metric concept.

Reframed Q1: Should the new CR-MET-003 Observation be a new first-class entity distinct from the existing `dea:Observation` (CR-5 §27)?

- **(a) Two distinct first-class entities: `dea:MeasurementObservation` (new; output of Measurement) and `dea:Observation` (existing; input to Assessment)**. Recommended. The two entities are siblings under the assessment-vs-measurement axis; no re-membership of the existing entity. Mirrors the kernel+specialization pattern of Q3(d) and Q4(d). The name `dea:MeasurementObservation` keeps the `dea:Observation` id for the assessment-side; the measurement-side gets its own id without collision.
- **(b) Refactor the existing `dea:Observation` to subsume both use cases; re-membership from `dea:assessment` to `dea:core`**. NOT recommended per user insight. Conflates the assessment-side input with the measurement-side output; loses the semantic distinction the user surfaced.
- **(c) Reuse the existing `dea:Observation` for both; add a `direction` field (input to assessment vs output of measurement)**. Loses semantic clarity; one entity serving two distinct concepts.

Status (2026-10-18): pending user confirmation of reframed Q1(a).

### 5.2 Q2 -- `dea:AssessmentTarget` disposition (carried from round 1; refined against CR-MET-006)

- **(a) Keep `dea:AssessmentTarget` for maturity-level targets; introduce foundational `dea:Target` (or `dea:PerformanceTarget`) as a new entity that AssessmentTarget may specialize**. Recommended; preserves assessment semantics.
- **(b) Rename `dea:AssessmentTarget` to `dea:Target` and broaden the definition**. Costs EGV-004 continuity.
- **(c) Keep `dea:AssessmentTarget` only; CR-MET-006 does not introduce a new Target entity**. The user's CR-MET-006 explicitly says Baseline/Target/Threshold should be independently contextualizable; if (c), the foundational Target lives on the Outcome side, not on a new entity.

### 5.3 Q3 -- `dea:MeasurementUnit` as a specialization of `dea:Unit` (REFRAMED per user clarification 2026-10-18)

The original Q3 proposed renaming `dea:Unit` to `dea:MeasurementUnit`. The user insight (verbatim 2026-10-18): "I suspect that rather creating a specialization for 'MeasurementUnit' will be appropriate."

The reframing: `dea:Unit` (CR-5 §9/Phase 2) is a justifiable abstract root entity. The kernel+specialization template (CR-016 / ADR-015) is the right pattern -- introduce `dea:MeasurementUnit` as a specialization, not a rename.

- **(a) Rename `dea:Unit` to `dea:MeasurementUnit`; preserve `dea:Unit` as a `legacy_id`**. NOT recommended per user clarification.
- **(b) Introduce `dea:MeasurementUnit` as a new entity with `supersedes: [dea:Unit]`; deprecate `dea:Unit`**. NOT recommended per user clarification; the user rejected the rename/supercede/deprecate path.
- **(c) Keep `dea:Unit`; CR-MET-005 extends its definition**. NOT recommended; does not address the measurement/assessment split.
- **(d) Introduce `dea:MeasurementUnit` as a SPECIALIZATION of `dea:Unit` (using `dea:specializes`); keep `dea:Unit` as the abstract root; no deprecation of `dea:Unit`**. Recommended per user clarification 2026-10-18. The kernel+specialization template per CR-016 / ADR-015: `dea:Unit` is the abstract root (existing; `profile: dea:assessment`); `dea:MeasurementUnit` is the new specialization for the measurement context. The `dea:specializes` relationship source = `dea:MeasurementUnit`, target = `dea:Unit`. The `class_alias` follows the kernel+specialization convention (e.g. `MUN`). No rename, no deprecation, no EGV-004 continuity issue.

Status (2026-10-18): user clarification accepted; option (d) confirmed.

### 5.4 Q4 -- `dea:MeasurementAggregation` as a specialization of `dea:AggregationRule` (REFRAMED per user clarification 2026-10-18)

The original Q4 proposed renaming `dea:AggregationRule` to `dea:AssessmentAggregation` and introducing a foundational `dea:MeasurementAggregation`. The user concern (verbatim 2026-10-18): "Why is AggregationRule to be renamed. It's a justifiable entity which can be specialized. Am not seeing the correlation between AggregationRule and MeasurementAggregation that warrant a rename."

The reframing: `dea:AggregationRule` (CR-5 §25) is a justifiable abstract root entity. The kernel+specialization template is the right pattern -- introduce `dea:MeasurementAggregation` as a specialization, not a rename.

- **(a) Rename to `dea:AssessmentAggregation`; introduce foundational `dea:MeasurementAggregation`**. NOT recommended per user clarification.
- **(b) Single entity `dea:AggregationRule` with profile-level specializations**. NOT recommended; conflicts with the foundational measurement-aggregation operators (SUM, MEAN, etc.) which are not profile-specific.
- **(c) Keep `dea:AggregationRule`; CR-MET-005 references it from new records without rename**. NOT recommended; loses the foundational/assessment separation.
- **(d) Introduce `dea:MeasurementAggregation` as a SPECIALIZATION of `dea:AggregationRule` (using `dea:specializes`); keep `dea:AggregationRule` as the abstract root; no rename**. Recommended per user clarification 2026-10-18. Mirrors Q3(d). The kernel+specialization template per CR-016 / ADR-015: `dea:AggregationRule` is the abstract root (existing; `profile: dea:assessment`); `dea:MeasurementAggregation` is the new specialization for the measurement context. The `dea:specializes` relationship source = `dea:MeasurementAggregation`, target = `dea:AggregationRule`. The `class_alias` follows the convention (e.g. `MAG`). Future CRs may add `dea:AssessmentAggregation` as a parallel specialization for the assessment context; the abstract root is the integration point.

Status (2026-10-18): user clarification accepted; option (d) confirmed.

### 5.5 Q5 -- Baseline/Target/Threshold as first-class entities (refined by CR-MET-006 §3 and the Q5d option)

- **(a) All three are first-class entities** with `dea:Metric`-related relationships.
- **(b) Baseline and Target are first-class; Threshold is a property of a Target** (Threshold becomes a `boundaries[]` field on Target).
- **(c) All three are structured properties of a `dea:MetricContext` aggregate**. NOT recommended (re-introduces the static-attribute anti-pattern).
- **(d) Baseline, Target, Threshold are first-class; Benchmark is referenceable; Expected Value is a property of Target; Variance is computed; Performance Interpretation is a derived view; Assessment Criterion reuses the assessment layer**. Recommended; matches the user-supplied "should not automatically become separate entity types" caveat interpreted as "do not introduce one entity per term in this table" rather than "do not introduce the foundational three".

### 5.6 Q6 -- KPI / KRI / KCI as Designation entity (new from CR-MET-008 §4)

- **(a) `dea:IndicatorDesignation` is a new first-class entity with the 12 attributes of CR-MET-008 §5**. Metric references designations via `dea:has-designation`. Recommended; matches the user-supplied "governed designations by default" decision.
- **(b) A `management_significance` field on Metric with a multi-value enum**. Simple, but loses the per-designation attribute set.
- **(c) KPI / KRI / KCI as specializations of Metric (subclasses)**. NOT recommended; contradicts the user-supplied decision and creates duplicate definitions.

### 5.7 Q7 -- Variance representation (new from CR-MET-006 §7)

- **(a) Variance is a derived view computed from an Observation and a reference (Baseline or Target); no entity**. Recommended; matches "should normally be calculated ... not stored as an intrinsic Metric attribute".
- **(b) Variance is a first-class entity (`dea:Variance`) carrying the reference, observed value, relative variance, and interpretation**. Useful when the same variance is reused.
- **(c) Variance is a property of a `PerformanceInterpretation` aggregate**.

### 5.8 Q8 -- Relationship vocabulary extensions for CR-MET-006 (new from CR-MET-006 §8)

- **(a) All ten user-named relationships are new**. Reuse minimal; precision maximal.
- **(b) Reuse where the existing vocabulary fits (e.g. `dea:assesses` for Assessment Criterion -- evaluates -- Subject); introduce new only for concepts the existing vocabulary does not cover**. Recommended; matches the audit-then-specifies pattern in the dea-metamodel skill. The audit table in CR-MET-006 §8 is the gating artefact.
- **(c) A single new relationship `dea:contextualizes` subsuming references / applies-to / specifies-desired-result-for / constrains / compares-against**. Loses precision; NOT recommended.

### 5.9 Q9 -- Cardinality model for "Metric is applicable to all processes but measures one specific process" (new from CR-MET-007 §5)

- **(a) Two distinct relationships: `dea:applies-to` (design-time intent) and `dea:measures` (runtime fact)**. Recommended; matches the user-supplied distinction.
- **(b) A single `dea:measures` relationship with `intended_applicability` on Metric**. Loses the design-time-vs-runtime semantic.
- **(c) A single `dea:measures` for both; the Measurement instance records the subject**. Closest to the existing model; recommended if minimal vocabulary expansion is preferred.

### 5.10 Q10 -- Maturity / DMM integration (new from CR-MET-007 §6)

- **(a) Metric is measurement-side; DMM is assessment-side; the two interact via the existing `dea:assessed-by` / `dea:assesses`**. Recommended; the existing vocabulary already provides the bridge.
- **(b) A new `dea:supports-maturity` relationship**. Vocabulary bloat; NOT recommended.
- **(c) Extend `dea:assessed-by` source list with maturity-side entities**. Out of scope.

### 5.11 Q11 -- `dea:measured-by` source list extension (new from CR-MET-007 §5)

- **(a) Extend with ValueStream, OrganizationalUnit, DataEntity, Product, Service, InformationSystem, Risk, Control, Policy, TransformationInitiative**. Recommended; covers the 11 enterprise domains named in CR-MET-007 §4 except those already in the existing list.
- **(b) Extend only the 4 most-used (ValueStream, OrganizationalUnit, DataEntity, Risk)**. Conservative; defers the rest.
- **(c) Defer all extensions to a follow-on CR**. NOT recommended; the cross-domain coverage is foundational.

### 5.12 Q12 -- Initial catalog composition (new from CR-MET-009 §6)

- **(a) Start with the 12 reference Metrics named in CR-MET-009 §6, one per domain**. Recommended; demonstrates cross-domain coverage.
- **(b) Start with the 5-KPI pilot from the round-2 proposal (MTTR, EBIT, ROI, EBITDA, one from issue #1) and add the remaining 7 in a second tranche**. Faster first slice; coverage is MECE-3 per type but not yet per domain.
- **(c) Start with the 3 already-named in the example structure (Customer Retention Rate, Mean Time to Recovery, Data Completeness) and grow**. Minimal viable catalog.

### 5.13 Q13 -- Reputability tier model (new from CR-MET-009)

- **(a) 5-value enum: industry_standard | framework_derived | sectoral_standard | internal_custom | emerging**. Recommended; matches the round-2 dual-anchor proposal.
- **(b) 3-value enum: industry_recognised | framework_derived | internal_custom**. Simpler; loses the sectoral-vs-emerging distinction.
- **(c) Free-text `reputability_notes` field**. Loses validation.

### 5.14 Q14 -- Dual-anchor requirement strength (new from CR-MET-009)

- **(a) Both anchors required for ADMIT-CANONICAL; informational-only on `lifecycle_status: proposed` records**. Recommended.
- **(b) Both anchors required for all records**. Forces the catalog to defer every record.
- **(c) Either anchor required; the other informational**. Loses the "industry-recognised AND applicable" semantic.

### 5.15 Q15 -- Lifecycle vocabulary extension (new from CR-MET-010 §5)

- **(a) Extend the existing `metamodel/vocabularies/lifecycle.yaml` with `under_review, approved, published, active, under_revision, suspended`**. Recommended.
- **(b) Map the user-supplied 7 states onto the existing 6-value vocabulary; treat `Under Review, Approved, Published, Active` as fine-grained `governance_status` values**. Avoids vocabulary extension; loses direct mapping.
- **(c) A new `metric_lifecycle` vocabulary distinct from the metamodel-level `lifecycle`**. Domain-specific; preserves the metamodel-level vocabulary.

### 5.16 Q16 -- Governance object split (new from CR-MET-010 §3)

- **(a) Four governance objects (Definition, Measurement, Observation, Indicator) each with their own lifecycle and approval**. Recommended; matches the user-supplied CR §3.
- **(b) Two governance objects (Definition and Execution); Observation is derived; Indicator is a Designation**. Reduces surface; loses Observation-specific governance.
- **(c) One governance object covering all four concerns**. Loses per-concern accountability.

### 5.17 Q17 -- Temporal dimension representation (new from CR-MET-011 §3)

- **(a) Each of the 7 dimensions is a separate field on Observation / Measurement**. Recommended.
- **(b) The 7 dimensions are encoded as a structured nested `temporal: { ... }` object on Observation**. Same content, namespace cleanliness; recommended over (a).
- **(c) Each dimension is a referenced entity**. Entity proliferation; NOT recommended.

Recommended overall: (b) on Observation (one nested `temporal` object); (c) only for `ReportingPeriod` (a genuinely reusable entity) and `EffectiveTime` (spans a definition, not a single record).

### 5.18 Q18 -- Provenance representation (new from CR-MET-011 §5)

- **(a) A `dea:Provenance` entity with 11 attributes referenced by Observation via `dea:has-provenance`**. Recommended; matches the W3C PROV-inspired approach.
- **(b) A nested `provenance: {...}` object on Observation**. Same content; namespace cleanliness.
- **(c) Each provenance element is a referenced entity**. Entity proliferation; NOT recommended.

### 5.19 Q19 -- Correction / supersession relationship (new from CR-MET-011 §7)

- **(a) Two relationships: `dea:corrects` (between an original Observation and its corrected successor) and `dea:supersedes` (between an original Observation and a later authoritative Observation)**. Recommended; matches the user-supplied distinction between Corrected and Superseded states.
- **(b) A single `dea:supersedes` relationship covering both**. Loses the semantic distinction.
- **(c) Corrections are encoded as a `correction_of` field on Observation**. Inline state; loses reusability.

### 5.20 Q20 -- Information type representation (new from CR-MET-012 §7)

- **(a) 6 separate entities: `dea:Observation` (already in scope), `dea:Estimate`, `dea:Forecast`, `dea:SimulationResult`, `dea:Recommendation`, `dea:Decision`**. Each has its own lifecycle and provenance.
- **(b) A single `dea:AnalyticalResult` entity with a `result_type` enum (observation | estimate | forecast | simulation_result | recommendation | decision)**. Recommended; reduces entity proliferation; preserves the user-supplied distinction via the type discriminator.
- **(c) Reuse the existing `dea:Observation` for all 6 types with a `kind` field**. Loses independent lifecycle.

### 5.21 Q21 -- Aggregation rules (new from CR-MET-012 §5)

- **(a) Reuse the CR-MET-005 aggregation operators and the new `dea:MeasurementAggregation` entity**. Aggregation compatibility rules are inherited from CR-MET-005. Recommended.
- **(b) Introduce a new `dea:AnalyticsAggregation` entity**. Loses the binding with CR-MET-005.
- **(c) Compute aggregations on demand without a model entity**. No reusable model.

### 5.22 Q22 -- Correlation vs causation (new from CR-MET-012 §6)

- **(a) A `dea:Correlation` entity that records the observed correlation without implying causation**.
- **(b) A `dea:CausalHypothesis` entity that records an analytical hypothesis with explicit confidence and uncertainty**.
- **(c) Both `dea:Correlation` and `dea:CausalHypothesis` are first-class entities; the distinction is preserved**. Recommended; matches the user-supplied CR §6.

## 6. Migration plan (per the cardinal rules)

Per the dea-metamodel skill's CR-022 closure pattern, every renamed or superseded entity carries a migration entry in `metamodel/migration/entity-normalization.yaml`. The migration manifest is authored in this CR and is the binding artefact for the new programme's downstream CRs.

| Disposition | Migration entry required | Closure CR obligation |
|---|---|---|
| EXTEND | No migration (additive). | Closure CR adds the new attributes to the generated artefacts. |
| RETAIN | No migration. | (n/a) |
| REFACTOR | Yes; `legacy_ids` block updated; re-membership block added. | Closure CR regenerates registries. |
| CONSOLIDATE | Yes; `legacy_ids` block updated; `supersedes` block added. | Closure CR extends `sqlite/schema.sql` CHECK constraints. |
| DEPRECATE | Yes; `status: deprecated`; `legacy_ids` retained. | Closure CR writes deprecation migration. |
| INTRODUCE | Yes; new entity entry. | Closure CR populates `artifacts.*` paths. |

## 7. Definition of Done (CR-MET-000)

- Disposition table (Section 4) approved by the user.
- Five decision points (Section 5) confirmed by the user.
- Migration entries (Section 6) authored for every REFACTOR / CONSOLIDATE / DEPRECATE disposition.
- This CR document lands in `change-requests/CR-MET-000.md` on the `technehub-labs/dea-metamodel` repo, on a `feature/CR-MET-000-reconciliation` branch, with a single PR.
- `change-requests/README.md` is updated to include CR-MET-000 in the active programme table.
- Kanban card #430 (Backlog) moves to In Progress when the PR is opened, Review when CI passes, Done on user squash-merge.
- CR-MET-001 authoring may begin only after CR-MET-000 is merged.

## 8. Out of scope (NOT-list)

- This CR does NOT add entities, attributes, relationships, or vocabulary entries. It is a reconciliation deliverable; the canonical-source changes happen in CR-MET-001..005 (and the rest of the programme).
- This CR does NOT change the `dea:measurement-dimension` allocation (ADR-0002 D1 stays binding).
- This CR does NOT introduce `dea:Activity` (per the user reminder 2026-10-18).
- This CR does NOT regenerate the registry; the regeneration is triggered by the first canonical-source change in CR-MET-001.

## 9. Cross-references

- User-supplied strategic CR-MET-000: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-000.md`.
- User-supplied implementation CR-MET-001..005: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-001-005.md`.
- Kanban surface: T-MET umbrella #429; CR-MET-000 = #430; CR-MET-001 = #431; ADR-MET-001 = #443 (first ADR after CR-MET-001). Full mapping in the umbrella description.
- Existing entity audit anchors: `metamodel/dea-metamodel.yaml` (line numbers in Section 3.1).
- Prior recon (now superseded by this CR): kanban card #418 (Done), `~/.hermes/profiles/coder/cache/scratch/CR-METRIC-01-proposal-metric-catalog-method.md` (838 lines, archived).
