# ADR-MET-004: Measurement subject and context via the existing `dea:measured-by` source extension

- Status: Proposed
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-007 (Metric-to-Enterprise Entity Relationships)
- Supersedes: nothing
- Referenced by: CR-MET-007, CR-MET-001, ADR-MET-009

## Context

The Metric capability requires Metric to be a cross-cutting semantic
concept usable throughout the OpenDEAM semantic architecture. A
Metric may be associated with strategic objectives, business
capabilities, business functions, business processes (including
activities and tasks), value streams, organizational units, products
and services, information systems, data entities, risks, controls,
assessment constructs, and other enterprise entities (per
user-supplied CR-MET-007 §4: 11 enterprise domains).

The existing `dea:measured-by` relationship (line 4612 of
`metamodel/dea-metamodel.yaml`) declares the source endpoint as:
`dea:AIMLModel`, `dea:ApplicationComponent`, `dea:BusinessCapability`,
`dea:BusinessProcess`, `dea:BusinessService`, `dea:Outcome`,
`dea:StrategicObjective`. This covers 7 of the 11 enterprise domains.

Four options were considered:

- A: extend the existing `dea:measured-by` source endpoint with the
  additional entities named in user-supplied CR-MET-007 §4
  (ValueStream, OrganizationalUnit, DataEntity, Product, Service,
  InformationSystem, Risk, Control, Policy, TransformationInitiative).
- B: introduce a new `dea:applies-to` relationship (per CR-MET-007 §5
  / Q9a) for design-time applicability, and keep `dea:measured-by`
  for runtime measurement facts.
- C: introduce a new `dea:contextualizes` relationship that subsumes
  the source-list extension.
- D: introduce new Metric-specific relationships for each of the 11
  enterprise domains.

Position A reuses the existing relationship and the existing
`dea:measured-by` semantics ("the source's performance, health, or
maturity is quantified by the target metric"). Position B adds a
second relationship for design-time intent; this is the recommended
option per CR-MET-007 §5 / Q9a. Position C collapses two orthogonal
relationships into one and loses precision. Position D introduces
11 new Metric-specific relationships, violating ADR-013 anti-
accumulation.

The user reminder 2026-10-18 establishes: do NOT introduce
`dea:Activity` as a new entity. Use the existing `dea:BusinessProcess`
(line 592; L3) decomposition via the catalog-internal Activity/Task
hierarchy. Therefore `dea:Activity` MUST NOT be added to any
relationship source list.

## Decision

1. The `dea:measured-by` source endpoint SHALL be extended by
   CR-MET-007 to include the additional entities named in
   user-supplied CR-MET-007 §4 that are not already in the list:
   `dea:ValueStream`, `dea:OrganizationalUnit`, `dea:DataEntity`,
   `dea:Product`, `dea:Service`, `dea:InformationSystem`,
   `dea:Risk`, `dea:Control`, `dea:Policy`,
   `dea:TransformationInitiative`. The 7 entities already in the list
   are preserved.
2. A new relationship `dea:applies-to` SHALL be introduced by
   CR-MET-007 with bounded source and target. The source is
   `dea:PerformanceMetric`; the target is the same set of enterprise
   entities as `dea:measured-by`. The cardinality: source 0..*,
   target 0..*. The inverse is `dea:has-applicable-metric`.
   Semantics: "the source Metric declares its intended applicability
   across many subjects (design-time intent)."
3. The existing `dea:measures` (inverse of `dea:measured-by`) SHALL
   be preserved. It carries the runtime measurement fact: "this
   subject was measured by this Metric."
4. The `dea:applies-to` and `dea:measures` distinction is the
   design-time-vs-runtime separation per CR-MET-007 §5 / Q9a. A
   Metric may declare applicability to all business processes
   (`dea:applies-to` cardinality 0..*) while only one specific
   process is measured in a given Measurement
   (`dea:measures` cardinality 0..*).
5. `dea:Activity` SHALL NOT be added to the `dea:measured-by` source
   list (per user reminder 2026-10-18; not canonical; activity-level
   measurement is sub-measurement of `dea:BusinessProcess` via the
   existing catalog-internal Activity/Task hierarchy).
6. The maturity / DMM integration is via the existing
   `dea:assessed-by` / `dea:assesses` relationship vocabulary
   (sources include Assessment, AssessmentFramework,
   AssessmentDimension, AssessmentResult; targets include Entity,
   AssessmentSubject). No new `dea:supports-maturity` relationship
   SHALL be introduced. The Metric supplies evidence to the
   Assessment; the Assessment produces a Maturity Level.
7. The audit-then-specifies pattern (per the dea-metamodel skill)
   SHALL be applied to the new `dea:applies-to` relationship. The CR
   body MUST contain an audit table covering the existing
   relationship vocabulary; the audit justifies the new
   relationship.
8. The `inverse` declaration on `dea:applies-to` SHALL be
   `dea:has-applicable-metric`; this is the implied inverse, not a
   separately registered relationship.
9. The cardinality of `dea:applies-to` and `dea:measured-by` SHALL
   be the same (source 0..*, target 0..*) to allow one Metric to
   measure multiple subjects and multiple Metrics to measure one
   subject.
10. The audit table for `dea:applies-to` MUST be present in the
    CR-MET-007 doc body as the gating artefact; reviewers verify the
    audit was complete before approving the new relationship.

## Consequences

- Positive: the existing `dea:measured-by` semantics are preserved
  and extended to 17 source entity types.
- Positive: the design-time-vs-runtime distinction
  (`dea:applies-to` vs `dea:measures`) is enforced at the
  relationship level.
- Positive: the user reminder 2026-10-18 is honored; no
  `dea:Activity` entity is introduced.
- Positive: the maturity / DMM integration reuses the existing
  vocabulary; no new Metric-specific relationships.
- Positive: the audit-then-specifies pattern is enforced.
- Negative: the `dea:measured-by` source list grows from 7 to 17
  entity types; the registry regenerates.
- Negative: a new relationship `dea:applies-to` is introduced with
  its own audit table; generated artefacts must regenerate.
- Forecloses: collapsed `dea:contextualizes` (Position C);
  11 Metric-specific relationships (Position D); adding
  `dea:Activity` to any source list (Position A variant).

## References

- CR-MET-007 (Metric-to-Enterprise Entity Relationships).
- CR-MET-000 §4 disposition table (dea:measured-by EXTEND).
- metamodel/dea-metamodel.yaml line 4612 (current dea:measured-by).
- metamodel/dea-metamodel.yaml line 5028 (dea:assesses).
- metamodel/dea-metamodel.yaml line 4584 (dea:assessed-by).
- metamodel/dea-metamodel.yaml line 592 (dea:BusinessProcess; L3).
- User reminder 2026-10-18 (no dea:Activity).
- User-supplied CR-MET-007 §4 (11 enterprise domains).
- Audit-then-specifies pattern (per dea-metamodel skill).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).
- ADR-MET-009 (Metric relationship architecture).
