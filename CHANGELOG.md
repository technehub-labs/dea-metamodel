# Changelog

All notable changes to the OpenDEA Metamodel are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
`docs/versioning.md`.

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
