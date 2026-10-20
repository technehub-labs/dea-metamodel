# CR-MET-007 -- Establish Cross-Domain Metric Relationships and Enterprise Measurement Applicability

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Depends on | CR-MET-001 (merged 2c445e4); CR-MET-002 (merged 84f10f4); CR-MET-003 (merged 5f7cddf); CR-MET-005 (merged 9fdf356); CR-MET-006 (merged 8a8185a) |
| Blocks | CR-MET-008 (KPI/KRI/KCI designation); CR-MET-009 (catalog with classified Measurements); CR-MET-011 (temporal/provenance); CR-MET-012 (analytics) |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control) |
| Kanban | T-MET umbrella #429; this CR is card #437 |
| Stream | Stream B (Enterprise interpretation and governance); second Stream B item. |

## 1. Background and problem statement

Metric is a cross-cutting semantic concept within OpenDEAM. An enterprise does not measure metrics in isolation; it measures characteristics and performance of business capabilities, processes, value streams, organizational units, products, services, technology, data, and strategic objectives.

A Metric therefore must be associated with the enterprise entities it measures or helps evaluate. However, association alone is insufficient; OpenDEAM must distinguish the semantic nature of each relationship. A Metric may measure a capability, indicate progress towards an objective, support assessment of a process, monitor a risk, or evaluate control effectiveness. These relationships are not interchangeable.

## 2. Objective

Establish a consistent cross-domain relationship architecture allowing Metric definitions and Measurements to be reused throughout the enterprise metamodel.

## 3. Binding 10-category relationship architecture (audited)

Per the user-supplied §3, 10 relationship categories are in scope. Each is audited against the existing canonical source (audit-then-specifies).

| Category | Canonical relationship | Verdict |
|---|---|---|
| Measurement | `dea:measured-by` (subject -> PerformanceMetric) | REUSE; subject side covers Measurement |
| Performance | `dea:measured-by` | REUSE; subject side covers Performance |
| Monitoring | `dea:measured-by` | REUSE; subject side covers Monitoring |
| Outcome | `dea:measured-by` (Outcome is a subject) | REUSE; Outcome already in source list |
| Assessment | `dea:assessed-by` (subject -> PerformanceMetric) + `dea:assesses` inverse | REUSE; maturity integration via existing assessment-side relationships |
| Risk | `dea:measured-by` (Risk subject) | EXTEND; add `dea:Risk` to source list |
| Control | `dea:measured-by` (Control subject) | EXTEND; add `dea:Control` to source list |
| Quality | `dea:measured-by` (DataEntity subject) | EXTEND; add `dea:DataEntity` to source list |
| Capability | `dea:measured-by` (BusinessCapability subject) | REUSE; already in source list |
| Strategic alignment | `dea:has-target` (StrategicObjective -> PerformanceTarget) | REUSE; introduced in CR-MET-006 |

**Net relationship delta**: 0 NEW relationships. The 10 categories map to 3 existing relationships (`dea:measured-by`, `dea:assessed-by`, `dea:has-target`) with 5 EXTENSIONS to source/target lists. ADR-013 anti-accumulation honored.

## 4. Enterprise integration coverage (user-supplied §4)

The user-supplied §4 names 11 enterprise domains. Each domain has relevant entities. The audit verifies each entity's coverage.

| Enterprise domain | Relevant entities | Existing in canonical source? | Coverage via existing relationship |
|---|---|---|---|
| Strategy | Objective, Strategy, Initiative | Objective: yes; Strategy: no; Initiative: no | Objective via `dea:measured-by`; Strategy/Initiative deferred (entities do not exist yet) |
| Organization | Enterprise, Business Unit, Organizational Unit | Enterprise: yes; BusinessUnit: no; OrganizationalUnit: yes | OrganizationalUnit via `dea:measured-by` (extension); Enterprise is the root; BusinessUnit deferred |
| Business architecture | Capability, Function, Process | Capability: yes; Function: no; Process: yes | Capability and Process via `dea:measured-by` (already present); Function deferred |
| Value architecture | Value Stream, Value Stage | ValueStream: yes; ValueStage: no | ValueStream via `dea:measured-by` (extension); ValueStage deferred |
| Customer | Customer Segment, Journey, Experience | none | All deferred; entities do not exist yet |
| Product and service | Product, Service, Service Offering | Service: yes; Product: no; ServiceOffering: no | Service via `dea:measured-by` (extension); Product/ServiceOffering deferred |
| Information architecture | Data Entity, Information Object | DataEntity: yes; InformationObject: no | DataEntity via `dea:measured-by` (extension); InformationObject deferred |
| Technology architecture | System, Component, Infrastructure | ApplicationComponent: yes; InformationSystem: no; Infrastructure: no | ApplicationComponent via `dea:measured-by` (already present); InformationSystem/Infrastructure deferred |
| Governance | Risk, Control, Policy | all 3 yes | all 3 via `dea:measured-by` (extensions) |
| Transformation | Transformation Initiative, Outcome | Outcome: yes; TransformationInitiative: no | Outcome via `dea:measured-by` (already present); TransformationInitiative deferred |
| Maturity | Maturity Model, Dimension, Assessment | all 3 yes | MaturityModel and AssessmentDimension via `dea:measured-by` (extensions); Assessment via `dea:assessed-by` (already present) |

**Binding extension set** (entities present in canonical source; extension to `dea:measured-by` source list):
- `dea:ValueStream`
- `dea:OrganizationalUnit`
- `dea:DataEntity`
- `dea:Service`
- `dea:Risk`
- `dea:Control`
- `dea:Policy`
- `dea:MaturityModel`
- `dea:AssessmentDimension`

That is 9 NEW source entities for `dea:measured-by` (from 7 to 16).

## 5. Cross-domain fixture coverage (user-supplied §8)

The user-supplied §8 names 10 cross-domain integration examples. Each is validated as a fixture.

| Example | Relationship | Source | Target |
|---|---|---|---|
| Metric measuring Business Capability | `dea:measured-by` | `dea:BusinessCapability` | `dea:PerformanceMetric` |
| Metric measuring Business Process | `dea:measured-by` | `dea:BusinessProcess` | `dea:PerformanceMetric` |
| Metric measuring Value Stream | `dea:measured-by` | `dea:ValueStream` | `dea:PerformanceMetric` |
| Metric supporting Strategic Objective | `dea:has-target` (CR-MET-006) | `dea:StrategicObjective` | `dea:PerformanceTarget` |
| Metric monitoring Risk | `dea:measured-by` | `dea:Risk` | `dea:PerformanceMetric` |
| Metric evaluating Control | `dea:measured-by` | `dea:Control` | `dea:PerformanceMetric` |
| Metric supporting DMM Assessment | `dea:assessed-by` (existing) + `dea:assesses` inverse | `dea:Assessment` | `dea:PerformanceMetric` |
| Metric measuring Data Quality | `dea:measured-by` | `dea:DataEntity` | `dea:PerformanceMetric` |
| Metric measuring Technology Reliability | `dea:measured-by` | `dea:ApplicationComponent` | `dea:PerformanceMetric` |
| Metric evaluating Transformation Outcome | `dea:measured-by` | `dea:Outcome` | `dea:PerformanceMetric` |

All 10 examples are covered by the existing + extended relationships; no new relationship types are required for these examples.

## 6. Q9 disposition: design-time applicability vs runtime measurement

The user-supplied §5 requires distinguishing a Metric's intended applicability from an actual Measurement instance. The user-supplied Q9a recommends two distinct relationships.

The audit-then-specifies decision:

- `dea:applies-subject` (introduced in CR-MET-006, source list Baseline|PerformanceTarget) is EXTENDED with `dea:PerformanceMetric` as a source. The semantic: a Metric declares its design-time intended applicability to a subject (e.g., "system availability metric applies to all services").
- `dea:measures-subject` (introduced in CR-MET-003, source Measurement) is EXTENDED with 9 NEW target entities (the same 9 from Section 4). The semantic: a Measurement records which specific subject was measured (e.g., "Measurement of system availability for payment processing at 2025-Q1").

The distinction between `dea:applies-subject` (design-time intent) and `dea:measures-subject` (runtime fact) is preserved. The audit-then-specifies decision: extend the existing CR-MET-006 relationship rather than introduce a new one.

## 7. Q10 disposition: maturity / DMM integration

The user-supplied §6 requires integration with DMM and other maturity models. The audit decision:

- The existing `dea:assessed-by` (line 4584) and `dea:assesses` (line 5028) relationships bridge Metric and the maturity model. An Assessment uses a Metric via `dea:assessed-by`; the Assessment attains a Maturity Level. Metric does NOT subsume Maturity Level.
- No new relationships are introduced for the maturity integration.
- A Metric may supply quantitative evidence, qualitative evidence, or maturity scoring support; the Assessment integrates these and produces a Maturity Level.

The maturity model integration pattern is documented in the CR doc; no vocabulary changes.

## 8. Canonical-source changes

### 8.1 EXTEND `dea:measured-by` source list

Source list extended from 7 entities to 16 entities. The 9 new entries are:
- `dea:ValueStream`
- `dea:OrganizationalUnit`
- `dea:DataEntity`
- `dea:Service`
- `dea:Risk`
- `dea:Control`
- `dea:Policy`
- `dea:MaturityModel`
- `dea:AssessmentDimension`

### 8.2 EXTEND `dea:measures-subject` target list

Target list extended from 7 entities to 16 entities. The 9 new entries match the `dea:measured-by` extension:
- `dea:ValueStream`
- `dea:OrganizationalUnit`
- `dea:DataEntity`
- `dea:Service`
- `dea:Risk`
- `dea:Control`
- `dea:Policy`
- `dea:MaturityModel`
- `dea:AssessmentDimension`

### 8.3 EXTEND `dea:applies-subject` source list

Source list extended from 2 entities (Baseline, PerformanceTarget) to 3 entities, adding:
- `dea:PerformanceMetric`

The cardinality and category are unchanged. The relationship now covers Baseline, PerformanceTarget, and PerformanceMetric -> Entity|AssessmentSubject.

## 9. Deferred items

| Item | Reason | Owner CR |
|---|---|---|
| `dea:Strategy`, `dea:Initiative`, `dea:BusinessUnit`, `dea:Function`, `dea:ValueStage` | entities do not exist in canonical source yet | future CR |
| `dea:CustomerSegment`, `dea:Journey`, `dea:Experience` | entities do not exist in canonical source yet | future CR (customer-domain) |
| `dea:Product`, `dea:ServiceOffering`, `dea:InformationObject`, `dea:InformationSystem`, `dea:Infrastructure`, `dea:TransformationInitiative` | entities do not exist in canonical source yet | future CR (product/technology/transform) |
| Automatic applicability inference (e.g., a Metric with `scope_classification: process` is automatically applicable to all `dea:BusinessProcess` entities) | runtime concern; metamodel declares the semantic | runtime |

## 10. Migration plan

1. Land the 3 EXTENSIONS in `metamodel/dea-metamodel.yaml`. No new entities; no new relationships; no vocabulary version bump.
2. Land the fixture file `tests/conformance/fixtures/cross_domain_metrics.yaml` with 10 representative cross-domain examples.
3. Land the conformance test `tests/conformance/test_027_cross_domain_metrics.py`.
4. Run the full test suite. All existing tests continue to pass.
5. Regenerate registry + specification.

## 11. Definition of Done

- `dea:measured-by` source list extended from 7 to 16 entities.
- `dea:measures-subject` target list extended from 7 to 16 entities.
- `dea:applies-subject` source list extended from 2 to 3 entities (adds `dea:PerformanceMetric`).
- 10 cross-domain fixtures demonstrating the user-supplied §8 examples.
- Conformance test validates the extension invariants and the 10 examples.
- EGV-004 identity continuity preserved.
- ADR-013 anti-accumulation honored (0 NEW relationships; 0 NEW entities).
- Stream B item 2 sealed.

## 12. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| KPI/KRI/KCI designation | CR-MET-008 |
| Catalog establishment with classified Measurements | CR-MET-009 |
| Governance objects (steward, owner, custodian, authority) | CR-MET-010 |
| Full calculation lineage model | CR-MET-011 |
| Full uncertainty and confidence model | CR-MET-012 |
| Entities named in §4 that do not exist yet (Strategy, Initiative, Function, ValueStage, CustomerSegment, Journey, Experience, Product, ServiceOffering, InformationObject, InformationSystem, Infrastructure, TransformationInitiative) | future CR (per domain) |

## 13. References

- CR-MET-000 (merged; commit 63d722a) §4 disposition table; §7 programme structure.
- CR-MET-001 (merged; commit 2c445e4) §3.1 (Metric definition).
- CR-MET-003 (merged; commit 5f7cddf) §4 (introduced `dea:measures-subject`).
- CR-MET-006 (merged; commit 8a8185a) §10.2 (introduced `dea:applies-subject`).
- ADR-MET-001 (merged; commit 8a532dd) (Metric as foundational).
- CR-5 §21 (existing `dea:AssessmentTarget`).
- CR-5 §28 (existing `dea:BenchmarkReference`).
- User-supplied CR-MET-007: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-006-012.md` (lines 426..619).
- User reminder 2026-10-18 (no new `dea:Activity`; use `dea:BusinessProcess` decomposition).
- EGV-004 (identity continuity).
- ADR-013 (Core non-accumulation).
- Audit-then-specifies pattern (per dea-metamodel skill).