# CR-MET-010 -- Establish Metric Governance, Semantic Quality, Lifecycle and Conformance Framework

| Field | Value |
|---|---|
| Status | Accepted (landed via PR #186) |
| Target repository | `technehub-labs/dea-governance`, `technehub-labs/dea-metamodel`, `technehub-labs/dea-catalog-metrics` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Phase | 5 (Catalog and governance) |
| Depends on | CR-MET-001 through CR-MET-009 |
| Kanban | T-MET umbrella #429; this CR is card #440 |
| Programme stream | Stream B (Enterprise interpretation and governance) |

## 1. Background and problem statement

The value of an enterprise Metric depends on the trustworthiness of its definition and the reliability of its measurement.

Without governance, organizations risk duplicate Metrics with conflicting meanings, inconsistent calculation methods, unapproved target changes, unreliable source information, untraceable observations, incomparable measurements, misleading enterprise performance reporting, and Metrics that continue to be used after their definitions become obsolete.

OpenDEAM requires a formal governance framework covering the complete Metric lifecycle. The key architectural decision (per the user-supplied CR-MET-010 §10): "Metric governance is part of the wider DEA governance architecture. It must not establish an independent governance regime that conflicts with canonical OpenDEAM governance."

## 2. Objective

Establish governance mechanisms for Metric definitions, measurement quality, observation integrity, semantic conformance, and controlled change.

## 3. Governance architecture (per the user-supplied CR §3)

Four governance objects are distinguished.

| Governance concern | Scope |
|---|---|
| Definition governance | Metric identity, semantics, classification, and formula |
| Measurement governance | Execution methods, collection, and validation |
| Observation governance | Result integrity, provenance, and quality |
| Indicator governance | KPI, KRI, KCI designation and management usage |

Governance must be assigned at the appropriate level rather than treating all four as one approval process.

## 4. Governance roles (per the user-supplied CR §4)

| Role | Responsibility |
|---|---|
| Metric Owner | Accountable for the Metric's business meaning and continued relevance |
| Metric Steward | Maintains definition quality and semantic consistency |
| Measurement Owner | Accountable for measurement execution |
| Data Owner | Accountable for authoritative source data |
| Data Steward | Supports data quality and lineage |
| Indicator Owner | Accountable for KPI / KRI / KCI usage |
| Governance Authority | Establishes policies and resolves governance exceptions |
| Metamodel Authority | Controls canonical semantic definitions |

One individual may fulfill multiple roles where appropriate, but accountability must remain explicit. The roles align with the existing OpenDEAM governance roles (CR-012, DEA-ID-000).

## 5. Metric lifecycle (per the user-supplied CR §5)

The user-supplied CR-MET-010 §5 names 7 lifecycle states: Proposed, Under Review, Approved, Published, Active, Under Revision / Suspended / Deprecated, Retired.

**Delivered (Q15a-prime).** The lifecycle is encoded as a declared specialization in `metamodel/vocabularies/lifecycle.yaml` (version 0.9.0):

```text
proposed
   |
   v
under_review
   |
   v
approved
   |
   v
published
   |
   v
active
   |
   +------> under_revision  (prior version remains authoritative)
   |
   +------> suspended       (reinstatable without a new identity)
   |
   +------> deprecated      TERMINAL (historical Observations retain context)
                |
                v
             retired          TERMINAL
```

`proposed`, `deprecated`, and `retired` are base vocabulary values; the 5 refinement values are declared by the `metric-governance` specialization. A Metric that is deprecated MUST NOT be silently deleted, particularly when historical Observations reference it; `test_l3_deprecated_metric_is_retained_not_deleted` enforces this.

## 6. Metric quality framework (per the user-supplied CR §6)

10 quality dimensions are defined.

| Quality dimension | Evaluation |
|---|---|
| Semantic clarity | Is the definition unambiguous? |
| Completeness | Are all required attributes present? |
| Consistency | Does it conform to existing definitions? |
| Validity | Does the calculation produce meaningful results? |
| Accuracy | Does the measurement reflect the intended subject? |
| Timeliness | Is the information sufficiently current? |
| Reliability | Can the measurement be reproduced? |
| Comparability | Are values comparable across contexts? |
| Traceability | Can sources and calculations be reconstructed? |
| Governance | Are ownership and approval established? |

The quality of a Metric definition must be distinguished from the quality of an individual Observation. A perfectly defined Metric can produce poor-quality observations; an individual observation may be accurate even when the Metric definition has governance weaknesses.

## 7. Conformance architecture (per the user-supplied CR §7)

Three conformance levels are defined.

Level 1 -- Structural conformance: valid schema, required attributes, valid identity, valid references, valid data types.

Level 2 -- Semantic conformance: unambiguous definition, valid classification, appropriate unit or scale, valid formula semantics, appropriate subject concept, valid relationships.

Level 3 -- Governance conformance: owner and steward, approval status, lifecycle compliance, source documentation, evidence requirements, versioning, change traceability.

## 8. Governance change management (per the user-supplied CR §8)

A semantic-change assessment process determines whether to revise the existing definition, create a new version, create a new Metric identity, deprecate an existing Metric, or establish a replacement relationship.

Not every change requires a new Metric identity. However, a change that alters the fundamental semantic meaning of a Metric must not be represented as a simple cosmetic version update.

## 9. Decision points

### Q15 (new from CR-MET-010 §5). Lifecycle vocabulary extension

- **(a) Extend the existing `metamodel/vocabularies/lifecycle.yaml` with `under_review, approved, published, active, under_revision, suspended`**. Preserves the user-supplied 7-state lifecycle; adds 6 enum values to the existing vocabulary.
- **(b) Map the user-supplied 7 states onto the existing 6-value vocabulary; treat `Under Review, Approved, Published, Active` as fine-grained `lifecycle_status` enum values on a new `governance_status` field, separate from `lifecycle`**. Avoids vocabulary extension; loses direct mapping.
- **(c) Adopt the user-supplied 7 states as a new `metric_lifecycle` vocabulary on the Metric entity, distinct from the existing metamodel-level `lifecycle` field**. Domain-specific lifecycle for Metric; preserves the metamodel-level vocabulary.

**DISPOSITION (binding): Q15a-prime.** The metamodel's lifecycle vocabulary remains the binding model; the user-supplied 7-state lifecycle is declared as an explicit *specialization* over the base vocabulary rather than a widening of it.

Rationale: widening `metamodel/vocabularies/lifecycle.yaml` from 5 to 10 values forces the `test_cr3r_lifecycle_vocabulary` equality invariant to propagate all 5 new values into all 134 entity schemas. That would force every entity in the metamodel to admit five governance states for which it has no governance process, an anti-accumulation violation under ADR-013. The declared-specialization form preserves the single-source-of-truth property while scoping the refinement states to exactly the four Metric-governed entities.

Binding implementation:

- `metamodel/vocabularies/lifecycle.yaml` base `values` remains the 5 metamodel-level states (`proposed`, `planned`, `active`, `deprecated`, `retired`).
- A `specializations.metric-governance` block declares the 5 refinement values (`under_review`, `approved`, `published`, `under_revision`, `suspended`) with an explicit `applies_to` list: `Metric`, `Measurement`, `MeasurementObservation`, `IndicatorDesignation`.
- The specialization also declares the canonical chain `proposed -> under_review -> approved -> published -> active`, the `active` branches (`under_revision`, `suspended`, `deprecated`), and the terminal set (`deprecated`, `retired`).
- `test_cr3r_lifecycle_vocabulary` is relaxed from equality to subset containment, and strengthened with two new negative assertions: a specialized schema MUST NOT admit lifecycle values outside its specialization scope, and a non-specialized schema MUST NOT admit refinement values at all. The invariant is now stronger than before, not weaker.
- The 4 Metric-governed schemas adopt the 10-value enum; the other 130 schemas keep the 5-value base enum.

### Q16 (new from CR-MET-010 §3). Governance object split

- **(a) Four governance objects (Definition, Measurement, Observation, Indicator) each with their own lifecycle and approval**. Recommended; matches the user-supplied CR §3.
- **(b) Two governance objects: Definition and Execution; Observation is a derived state of Execution; Indicator is a Designation on Definition**. Reduces governance surface; loses the Observation-specific governance (correction / supersession / quality).
- **(c) One governance object covering all four concerns**. Loses the per-concern accountability.

Recommended: (a). The four governance objects are independent in lifecycle and approval; the Indicator governance reuses the Designation lifecycle from CR-MET-008.

## 10. Reconciliation with existing governance constructs

| Existing construct | Disposition |
|---|---|
| `dea-governance` repo (DEA-ID-000, CR-012, CR-MM-04) | RETAIN -- Metric governance integrates with the existing governance authority. No parallel governance regime. |
| `metamodel/vocabularies/lifecycle.yaml` | DECLARE SPECIALIZATION (per Q15a-prime; base vocabulary not widened). Version 0.8.0 -> 0.9.0. |
| `metamodel/vocabularies/classifications.yaml` | EXTEND with 7 governance vocabularies (MetricGovernance.governance_object 4, MetricGovernance.governance_role 8, MetricQuality.quality_dimension 10, MetricQuality.quality_verdict 4, MetricConformance.conformance_level 3, MetricConformance.conformance_verdict 3, MetricChange.semantic_change_disposition 5, MetricChange.change_severity 4). Version 0.13.0 -> 0.14.0. |
| `schemas/entities/metric.json` | EXTEND with `governance` (8 roles + approval), `quality_dimensions` (10 dimensions), `conformance` (3 levels); `lifecycle_status` enum 5 -> 10 values. |
| `schemas/entities/measurement.json`, `measurement-observation.json`, `indicator-designation.json` | EXTEND `lifecycle_status` enum 5 -> 10 values (metric-governance specialization scope). |
| `tests/conformance/test_009_entity_rules.py` | STRENGTHEN `test_cr3r_lifecycle_vocabulary` from equality to subset containment plus two negative assertions. |
| `metamodel/registry/entities.yaml` (GENERATED) | REGENERATE after the lifecycle vocabulary extension. |
| Conformance test suite (`tests/conformance/`, 133 tests) | EXTEND with 3 new test classes: `test_metric_definition_conformance.py` (Level 1), `test_metric_semantic_conformance.py` (Level 2), `test_metric_governance_conformance.py` (Level 3). |

## 11. Definition of Done

- [x] The 4 governance objects (Section 3) are encoded as `MetricGovernance.governance_object` (4 values) and asserted by `test_l2_governance_object_values_known`.
- [x] The 8 governance roles (Section 4) are encoded as `MetricGovernance.governance_role` (8 values), carried on `Metric.governance`, and asserted by `test_l2_governance_role_names_known` plus `test_l3_governance_roles_are_accountable_explicitly`.
- [x] The 7-state lifecycle (Section 5) is declared as the `metric-governance` specialization in `metamodel/vocabularies/lifecycle.yaml` (Q15a-prime). Terminal states `deprecated` + `retired` enforced.
- [x] The 10 quality dimensions (Section 6) are encoded as the `quality_dimensions[]` field on Metric with governed verdicts; assertion in `test_l2_quality_dimension_values_known`. **Disposition: inline field, not a `dea:MetricQualityAssessment` entity.** Rationale: the dimensions describe a property of the Metric definition itself, not an independently identified and lifecycle-managed object; a separate entity would fragment identity per ADR-013. Definition quality remains distinct from Observation quality, which is carried on `dea:MeasurementObservation`.
- [x] The 3 conformance levels (Section 7) are implemented as 3 conformance test classes: `test_029_metric_definition_conformance.py` (Level 1, 10 tests), `test_030_metric_semantic_conformance.py` (Level 2, 10 tests), `test_031_metric_governance_conformance.py` (Level 3, 14 tests).
- [x] The semantic-change assessment process (Section 8) is encoded as `MetricChange.semantic_change_disposition` (5 values) + `MetricChange.change_severity` (4 values) with 5 exercised change records in the fixture; the binding rule that a `semantic_breaking` change MUST require a new identity is asserted by `test_l3_semantic_breaking_change_requires_new_identity`.
- [x] CI/CD governance checks per the user-supplied CR §9 (12 automated checks) are mapped to the 34 conformance tests across the 3 levels, each producing an actionable finding list.
- [x] D-004 / D-005 / embargo / author-denylist scans pass on all new files.

## 12. NOT-list

- This CR does NOT establish a parallel governance regime. The existing `dea-governance` authority is the source of truth; Metric governance integrates with it.
- This CR does NOT silently delete deprecated Metrics. Historical Observations preserve their original semantic context.
- This CR does NOT auto-approve semantically significant changes merely because schema validation passes.

## 13. Cross-references

- User-supplied CR-MET-010: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-006-012.md` (lines 1042-1306).
- CR-MET-000 reconciliation: `/home/hermes/dea-work/dea-metamodel/change-requests/CR-MET-000.md` §4.
- Existing governance: `technehub-labs/dea-governance` (DEA-ID-000, CR-012, CR-MM-04).
- Kanban: T-MET umbrella #429; this CR is card #440; ADR-MET-014 is card #456.
- Stream: Stream B (Enterprise interpretation and governance).
