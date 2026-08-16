# Changelog

All notable changes to the OpenDEA Metamodel are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
`docs/versioning.md`.

## [0.8.0] — 2026-08-16 — CR-003: Entity & Relationship Normalization

### Removed (CR-3A — breaking for schemas, reversible via migration matrix)
- **70 relationship-state properties removed from 25 entity schemas** — the 37
  CR-2F-deprecated properties plus 32 ID-reference arrays (`processes`, `metrics`,
  `owned_*`, `parties`, `mitigates`, `technology_stack`, …) and `Capability.maturity_level`.
  Every removal has a disposition (target relationship or explicit re-assertion
  requirement) in `metamodel/migration/entity-normalization.yaml`.
- SQLite projection: `owner` columns (6), `parent_ou` (+index), `parent_concept`,
  `capabilities.maturity_level` dropped.

### Added
- `lifecycle_status` on every entity schema, driven by the new centralized vocabulary
  `metamodel/vocabularies/lifecycle.yaml` (CR-3R).
- `external_references {system, identifier}` on every entity schema + SQLite
  `entity_external_references` table (CR-3P) — external IDs never replace OpenDEA identity.
- `metamodel/vocabularies/classifications.yaml` — 55 controlled classification
  vocabularies, CI-synced against schema enums (E005).
- Entity conformance rules E001–E010 as automated tests (suite now 48 tests).
- `metamodel/migration/entity-normalization.yaml` (CR-3U/3V): 54 entity actions,
  58 property dispositions, migration metadata 0.7.0 → 0.8.0 (reversible).

### Changed
- `Technology.lifecycle_status` renamed to `adoption_status` (adoption posture is a
  classification, not the universal entity lifecycle).
- Relationship endpoints extended (normative, MINOR): supports+Actor source,
  realizes+BusinessObject, represents+EcosystemActor, composes+Actor,
  owns+BusinessProcess, informs+Entity targets.

### Deferred
- Abstract entity categories (CR-3L) → CR-4 consolidation.
- Agent as specialized entity (CR-3D) → CR-7.
- Assessment/maturity model (CR-3B target) → CR-5.

## [0.7.0] — 2026-08-16 — CR-002: Authoritative Relationship Semantics

### Added
- **Canonical relationship ontology**: 49 normative relationships (48 stored + 1 virtual
  inverse view) with full §3 structure — category (A–K taxonomy), canonical direction,
  typed source/target endpoints, cardinality at both ends, inverse declarations,
  transitive/symmetric flags, temporality, provenance requirement, lifecycle
  (`proposed | active | deprecated | retired`).
- **Relationship crosswalk** `metamodel/migration/relationship-crosswalk.yaml` — all 59
  viewer labels + 10 legacy instance-enum values explicitly dispositioned; nothing
  silently reinterpreted.
- **Instance metadata** (§6/§21/§22): `relationship-instance.json` v2 supports
  `effective_from/to`, `status`, `confidence`, `asserted_by`, `rationale`, `evidence`,
  structured `provenance` incl. `agent_id` + `verification_status` for AI-asserted
  relationships, and `mapping.kind` for narrowed `maps-to`.
- **Viewer graph-side migration** (2I): every edge carries canonical `rel_ids`;
  `relationship_definitions` embedded for viewer definition display; generator
  hard-fails on unmapped labels (R012).
- **Conformance rules R001–R012** as automated tests (suite now 37 tests).

### Changed
- `maps-to` narrowed to crosswalk/classification/traceability/equivalence semantics (§9).
- Overloaded relationships decomposed (§17): `governance`→governs/mandates/controls/owns/
  responsible-for; `implements` disambiguated from `realizes`/`operationalizes`/`supports`;
  `influences`→`informs`; split labels (`produces / consumes`, `publishes / subscribes`)
  decomposed.
- SQLite `relationships` table rebuilt from the registry: 48-type CHECK constraint,
  metadata columns; pre-0.7.0 columns retained but deprecated.
- TTL ObjectProperties regenerated from the canonical registry (48).
- Legacy viewer rel_types (7) demoted to rendering styles; categories are the semantics.

### Deprecated
- 35 duplicated relationship-state properties across 20 entity schemas (CR-2F) —
  physical removal in CR-003.
- Instance types `influenced-by`, `decomposes` (superseded — see crosswalk);
  instance fields `weight`, `bidirectional`.

## [0.6.0] — 2026-08-16 — CR-001: Canonical Metamodel

### Added
- **Normative metamodel source** `metamodel/dea-metamodel.yaml` — the single
  authoritative semantic definition (CR-1.1).
- **Metamodel manifest** `metamodel/manifest.yaml` (CR-1.2).
- **Entity and relationship registries** under `metamodel/registry/` with stable
  semantic IDs for all 54 entities and 17 relationships (CR-1.4, CR-1.5).
- **Governance docs**: `docs/architecture.md`, `docs/semantics.md`,
  `docs/versioning.md` (CR-1.7, CR-1.12).
- **Change-control mechanism** `change-requests/` with CR-001 as the first record
  (CR-1.8).
- **Conformance suite** `tests/conformance/` (tests 001–006, CR-1.9).
- CI enforcement of version consistency, referential integrity, duplicate IDs, and
  generated-artifact freshness (CR-1.11).

### Changed
- Unified version baseline: all artifacts converge on **0.6.0** (previously
  metamodel.yaml 0.3.0, VERSION 0.4.0, entity-graph 0.5.0, sqlite 0.1.0-alpha).
- README restructured: explicit Normative / Derived / Informative separation.
- `metamodel.yaml` (legacy root index) deprecated in favour of the normative source;
  retained for consumer compatibility until the catalog migration phase.

### Governance
- Semantic expansion freeze in effect until CR-003 closes (CR-1.6).
- Component versions separated: metamodel / JSON Schema / SQLite projection / viewer
  (CR-1.3).

## [0.5.0] — 2026-08-15
- ADR-0005: entity_role / completeness_contract; Resource abstract same-layer root.
  Synced from OpenDEAM root model v0.5.0 (53 entities, 2 dimension entities, 70 edges).

## [0.4.0] — 2026-08
- ADR-0004 renames: Principle→Tenet, Standard→Guardrail, Reference Model→Blueprint.

## [0.3.0] — 2026-08
- Root-model pin v0.3.0; entity-graph generation from OpenDEAM root.

## [0.1.0-alpha] — 2026-08
- Initial scaffold: schemas, SQLite projection, TTL ontology, viewer graph.
