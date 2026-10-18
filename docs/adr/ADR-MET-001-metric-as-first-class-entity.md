# ADR-MET-001: Metric as a first-class, foundational OpenDEAM entity

- Status: Proposed
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012 (OpenDEAM Metric capability)
- Source CR: CR-MET-000 (reconciliation); CR-MET-001 (canonical entity)
- Supersedes: nothing
- Referenced by: CR-MET-001 (binding), ADR-MET-002, ADR-MET-003, ADR-MET-004

## Context

The OpenDEAM metamodel declares `dea:PerformanceMetric` (canonical; line
1519 of `metamodel/dea-metamodel.yaml`; ADR-0002 D1; profile
`dea:assessment`; dimension `measurement-dimension`; class_alias MTR;
catalog_repo `dea-catalog-metrics`). The entity is currently scoped to
the `dea:assessment` profile under the `measurement-dimension` orthogonal
allocator.

The Metric capability programme (CR-MET-000..012; 13 CRs in three
streams: semantic/measurement foundation, enterprise interpretation/
governance, historical intelligence/decision support) requires Metric
to be a foundational entity usable across all five OpenDEAM profiles
(core, business, digital, technology, assessment) and across the
measurement-dimension orthogonal allocator.

Four positions were considered:

- A: keep `dea:PerformanceMetric` in `profile: dea:assessment`; add
  profile-level references from business, digital, and technology
  profiles.
- B: introduce a new abstract Core root `dea:Metric` and re-membership
  `dea:PerformanceMetric` to that root.
- C: promote `dea:PerformanceMetric` from `profile: dea:assessment` to
  `profile: dea:core` (or `kind: core`) as a first-class foundational
  entity.
- D: deprecate `dea:PerformanceMetric`; introduce a new
  `dea:MeasurementMetric` as the foundational entity.

Position A leaves the entity profile-scoped to assessment, which forces
every other profile to either re-refer or duplicate. Position B
introduces a parallel root and violates the ADR-013 anti-accumulation
rule (the Core does not gain a new root merely for symmetry). Position
D creates EGV-004 identity continuity overhead and discards the
existing entity unnecessarily. Position C re-memberships the existing
entity to a foundational scope without breaking identity continuity and
without adding a parallel root.

The reconciliation CR (CR-MET-000 §4) records this disposition as
EXTEND for `dea:PerformanceMetric`: re-membership to core, additive
attribute enrichment, no deprecation. The five architectural
principles in the user-supplied CR-MET-000 §2 (Metric is foundational;
Measurement is distinct; Results are distinct; Interpretation is
distinct; Measurement is cross-domain) are binding on this ADR.

## Decision

1. `dea:PerformanceMetric` SHALL be re-membershiped from
   `profile: dea:assessment` to a foundational scope. The implementation
   may either set `membership.kind: core` (if the canonical source
   supports it) or set `membership.kind: profile` with `membership.profile: null`
   and `dimension: measurement-dimension`; the latter is the current
   mechanism in the canonical source for orthogonal-allocator entities.
2. The definition SHALL be updated to reflect foundational scope:
   Metric is a reusable, first-class OpenDEAM semantic specification
   that describes a measurable property, characteristic, condition,
   quantity, rate, ratio, index, or other observable aspect of a
   subject, including the semantic rules necessary to determine and
   interpret its value.
3. The `class_alias` SHALL remain MTR (no change; preserves identity
   continuity for catalog records).
4. The `catalog_repo` SHALL remain `dea-catalog-metrics` (no change).
5. The `legacy_ids` SHALL be extended to include the CR-10J Scenario
   metrics identifier if not already present.
6. The dimension SHALL remain `measurement-dimension` (per ADR-0002 D1).
7. The `building_block` SHALL remain `null` (per ADR-0002 D1; no layer
   allocation for orthogonal-allocator entities).
8. The profile memberships of other profiles (business, digital,
   technology) SHALL reference `dea:PerformanceMetric` via the
   `profile.membership: [dea:PerformanceMetric]` mechanism if and when
   those profiles need Metric visibility.
9. The EGV-004 identity continuity rule SHALL be preserved: any record
   that previously referenced `dea:PerformanceMetric` in the
   `dea:assessment` profile continues to validate.
10. No parallel `dea:Metric` root SHALL be introduced. No new
    `dea:MeasurementMetric` entity SHALL be introduced. No deprecation
    of `dea:PerformanceMetric` SHALL occur.

## Consequences

- Positive: Metric is a foundational entity usable across all profiles
  and across the measurement-dimension orthogonal allocator, without
  breaking identity continuity or introducing a parallel root.
- Positive: ADR-013 anti-accumulation rule is preserved (no new Core
  root).
- Positive: the existing catalog_repo and class_alias are preserved;
  catalog records continue to validate without migration.
- Positive: the user-supplied CR-MET-000 §2 architectural principles
  (foundational, cross-domain) are enforced at the membership level.
- Negative: `membership.kind` changes from `profile: dea:assessment`
  to either `core` or `profile: null`. Generated artefacts (JSON
  schemas, Pydantic models, TypeScript interfaces, registry entries)
  must regenerate.
- Forecloses: parallel-root approaches (Position B); deprecation-and-
  replace approaches (Position D); profile-only approaches (Position
  A).

## References

- CR-MET-000 §4 disposition table (dea:PerformanceMetric EXTEND).
- CR-MET-001 (canonical entity specification).
- ADR-0002 D1 (orthogonal allocator binding).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).
- CR-016 (kernel+specialization implementation precedent).
- EGV-004 (identity continuity).
- metamodel/dea-metamodel.yaml line 1519 (current declaration).
