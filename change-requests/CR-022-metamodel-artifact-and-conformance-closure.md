# CR-022: Metamodel Artifact and Conformance Closure

| Field | Value |
|-------|-------|
| **CR** | CR-022 |
| **Title** | Metamodel Artifact and Conformance Closure (final metamodel-side CR of Path Y) |
| **Status** | Proposed (this PR) |
| **Layer** | Metamodel (Digital Profile) |
| **Programme** | Information Systems Semantic Architecture |
| **Architectural parent** | CR-017 (foundation, merged 2026-10-16 via PR #170); CR-018 (ISF, merged via PR #171); CR-019 (ISC, merged via PR #172); CR-020 (ISS, merged via PR #173); CR-021 (II, merged via PR #174) |
| **Companion to** | CR-MM-PROC-01; CR-016; CR-MM-04; CR-MM-ECF-04; CR-AR-FMWK-03; CR-012 (dea-governance) + DEA-ID-000 |
| **Depends on** | CR-017; CR-018; CR-019; CR-020; CR-021; CR-MM-04 |
| **Enables** | CR-AR-FMWK-04; CR-IS-CAT-01..04; `CR-013 (dea-governance)` portfolio adoption |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-16 |

## 1. Executive Summary

This CR is the metamodel artifact and conformance closure for the Information Systems Semantic Architecture programme (CR-017..CR-021). It is the final metamodel-side CR of Path Y.

The closure scope has seven concrete artefacts:

1. **Canonical source `artifacts.*` paths populated** for the four new entities (ISF, ISC, ISS, II): `pydantic_model`, `sqlite_table`, `ts_interface`. The paths were left `null` in CR-018..CR-021 per the implementing-CR convention; CR-022 populates them.
2. **Pydantic generator run**; the four new modules are now present: `pydantic/information_system_function.py`, `pydantic/information_system_component.py`, `pydantic/information_system_service.py`, `pydantic/integration_interface.py`. Total: 123 pydantic modules + `pydantic/entity.py` (the shared base).
3. **SQLite CHECK constraint extended** to include the four new entity types in the `entities.type` CHECK and the new `specifies` relationship type in the `relationships.relationship_type` CHECK. SQLite schema parses cleanly (99 tables).
4. **TypeScript `interfaces.ts` extended**: four new `BaseEntity`-extending interfaces (InformationSystemFunction, InformationSystemComponent, InformationSystemService, IntegrationInterface); the four new entity types added to the `AnyEntity` union and the `ENTITY_TYPES` array. `tsc --noEmit` PASS.
5. **TTL ontology `dea-metamodel-ontology.ttl` extended**: four new `owl:Class` declarations for the Information Systems sub-tree; the new `dea:specifies` relationship declared as `owl:ObjectProperty` with category `contract` (category M).
6. **D-004 cleanup pass** on the touched files: 99 pre-existing em-dash / en-dash / horizontal-ellipsis / three-dot-pause characters in `ttl/dea-metamodel-ontology.ttl` (71), `sqlite/schema.sql` (5), `typescript/src/interfaces.ts` (23). FILE-not-DIFF posture: clean whole files, not just the diff.
7. **Four closure documents** under `docs/is-semantic-architecture/`:
   - `migration-id-map.yaml` (EGV-004 identity continuity map)
   - `conformance-test-catalogue.yaml` (9 positive + 10 negative conformance tests)
   - `closed-vocabulary-profile.yaml` (introduced and reconciled entities, new relationship, new category, type aliases, deprecation signals)
   - `opendeam-identifier-map.yaml` (stub for CR-AR-FMWK-04)

## 2. Scope

### 2.1 In scope

1. `artifacts.pydantic_model` populated for ISF, ISC, ISS, II.
2. `artifacts.sqlite_table` populated for ISF, ISC, ISS, II.
3. `artifacts.ts_interface` populated for ISF, ISC, ISS, II (all point to `typescript/src/interfaces.ts`).
4. `.github/scripts/generate_pydantic.py` run; the four new pydantic modules land.
5. `sqlite/schema.sql` CHECK constraint extended to include the four new entity types and the new `specifies` relationship type.
6. `typescript/src/interfaces.ts` extended: four new interfaces, `AnyEntity` union extended, `ENTITY_TYPES` array extended.
7. `ttl/dea-metamodel-ontology.ttl` extended: four new `owl:Class` declarations and the new `dea:specifies` `owl:ObjectProperty` declaration.
8. D-004 cleanup of the touched files (FILE-not-DIFF posture).
9. The four closure documents under `docs/is-semantic-architecture/`.
10. The CR-022 document (this file).
11. `change-requests/README.md` row for CR-022.
12. `docs/information-systems-semantic-architecture.md` update.

### 2.2 Out of scope

1. The new catalog repositories (`dea-catalog-information-system-functions`, `dea-catalog-information-system-components`, `dea-catalog-information-system-services`, `dea-catalog-information-system-integration-interfaces`). Owned by `CR-IS-CAT-01..04` after this CR lands.
2. The OpenDEAM architectural model extension. Owned by `CR-AR-FMWK-04`.
3. The governance portfolio registration. Owned by `CR-013 (dea-governance)`.
4. The TypeScript relationship-type union expansion (DRIFT-5). The existing `RelationshipType` union in `typescript/src/interfaces.ts` is locked at 10 entries (CamelCase). The canonical metamodel source uses kebab-case. Reconciling the two is a separate refactoring CR; documented in DRIFT-5.
5. The TTL generator (script that produces `ttl/dea-metamodel-ontology.ttl`). The file is hand-maintained. The new entities and the new relationship were added manually in this CR; a TTL generator is a future-CR concern.

## 3. Artifacts Closure

### 3.1 Canonical source `artifacts.*` paths

The canonical metamodel source for the four new entities now carries explicit `artifacts.*` paths.

| Entity | json_schema | sqlite_table | pydantic_model | ts_interface |
|---|---|---|---|---|
| `dea:InformationSystemFunction` | `schemas/entities/information-system-function.json` | `information_system_functions` | `pydantic/information_system_function.py` | `typescript/src/interfaces.ts` |
| `dea:InformationSystemComponent` | `schemas/entities/information-system-component.json` | `information_system_components` | `pydantic/information_system_component.py` | `typescript/src/interfaces.ts` |
| `dea:InformationSystemService` | `schemas/entities/information-system-service.json` | `information_system_services` | `pydantic/information_system_service.py` | `typescript/src/interfaces.ts` |
| `dea:IntegrationInterface` | `schemas/entities/integration-interface.json` | `integration_interfaces` | `pydantic/integration_interface.py` | `typescript/src/interfaces.ts` |

The `ts_interface` path is shared (all four entities go into the single `typescript/src/interfaces.ts` file). The convention follows the existing entities (e.g., `dea:ApplicationComponent` and `dea:IntegrationComponent` both point to `typescript/src/interfaces.ts`).

### 3.2 Pydantic generator output

The Pydantic generator (`.github/scripts/generate_pydantic.py`) reads the JSON Schema files and the canonical source, and emits a Pydantic module per entity. CR-022 produces four new modules; the total is now 123 Pydantic modules + `pydantic/entity.py` (the shared base).

The Pydantic modules mirror the JSON Schema definitions, including the `type: const: 'InformationSystemFunction'` etc. discriminator. No inline relationship-state properties (per CR-3 / `test_003_no_duplicate_relationship_state`).

### 3.3 SQLite schema extension

The `entities.type` CHECK constraint is extended from a closed list of 13 entity types to a closed list of 17. The new types:

- `'InformationSystemFunction'`
- `'InformationSystemComponent'`
- `'InformationSystemService'`
- `'IntegrationInterface'`

The `relationships.relationship_type` CHECK constraint is extended with `'specifies'`. The new relationship was introduced in CR-021 (D-4 audit-then-specifies posture). The full CHECK constraint parses cleanly; 99 tables in the resulting schema.

### 3.4 TypeScript interface extension

The `typescript/src/interfaces.ts` file is extended with four new `BaseEntity`-extending interfaces. Each interface carries the `type: '...'` discriminator plus a small set of optional fields. The fields are intentionally minimal; the canonical source's relationship vocabulary is the source of truth for relationship edges, and CR-3 forbids inline relationship-state in entity records.

The `AnyEntity` union is extended with the four new types. The `ENTITY_TYPES` array is extended with the four new entries.

`tsc --noEmit` PASS.

### 3.5 TTL ontology extension

The `ttl/dea-metamodel-ontology.ttl` file is extended with four new `owl:Class` declarations and one new `owl:ObjectProperty` declaration. The new entity declarations follow the existing pattern: `rdfs:subClassOf dea:Entity`, `rdfs:label`, `skos:definition`. The new `dea:specifies` declaration follows the existing relationship pattern: `dea:category`, `dea:inverseOf`.

`validate_ttl.py` SKIP (rdflib not installed in the local environment; the file is a hand-maintained Turtle and the CI pipeline has rdflib for validation).

## 4. DRIFT-5: TypeScript RelationshipType Union

The existing `typescript/src/interfaces.ts` `RelationshipType` union is locked at 10 entries (CamelCase: `mapsTo`, `realizes`, `implements`, `influencedBy`, `decomposes`, `orchestrates`, `consumes`, `provides`, `governs`, `measuredBy`). The canonical metamodel source uses kebab-case for relationship ids (`dea:executes`, `dea:specializes`, `dea:depends-on`, `dea:composes`, `dea:uses`, `dea:exposes`, `dea:specifies`, etc.). The two naming conventions are inconsistent.

DRIFT-5 records this inconsistency. The closure is a separate refactoring CR (parked for the next metamodel governance cycle). CR-022 does not expand the `RelationshipType` union because:

- Expanding the union requires a TypeScript refactoring (kebab-case vs CamelCase, deprecated entries, etc.)
- The relationship-type vocabulary in the canonical source is larger than the TypeScript union; a one-shot expansion risks introducing inconsistency
- The TypeScript interface file is hand-maintained; the existing pattern is incremental

The `RELATIONSHIP_TYPES` array in `typescript/src/interfaces.ts` is similarly locked; a comment in the new entity types (added in this CR) explains the future alignment.

## 5. Migration ID Map

The migration ID map is at `docs/is-semantic-architecture/migration-id-map.yaml`. It records the legacy_id to canonical_id mapping for all entities reconciled in the IS Semantic Architecture programme:

- `dea:entity-system-function` → `dea:InformationSystemFunction` (CR-018 D-1)
- `dea:SystemFunction` → `dea:InformationSystemFunction` (CR-018 D-1; EGV-004)
- `dea:entity-solution-component` → `dea:SolutionComponent` (CR-019 D-2)
- `dea:entity-application-component` → `dea:ApplicationComponent` (CR-019 D-2)
- `dea:entity-integration-component` → `dea:IntegrationComponent` (CR-019 D-2)
- `dea:entity-infrastructure-component` → `dea:InfrastructureComponent` (CR-019 D-2; DRIFT-4 placement)
- `dea:entity-platform-service` → `dea:PlatformService` (CR-020 D-3; conditional specialisation)
- `dea:entity-api` → `dea:API` (CR-021 D-4; audit-then-specifies)

The map is consumed by `CR-AR-FMWK-04` (OpenDEAM extension) and the catalog CRs (`CR-IS-CAT-01..04`).

## 6. Conformance Test Catalogue

The conformance test catalogue is at `docs/is-semantic-architecture/conformance-test-catalogue.yaml`. It contains 9 positive and 10 negative conformance tests covering:

- Specialization paths (ISF specializes Behavior; APC/IGC specialize ISC; ISS specializes Service; II has no specializes; PS specializes ISS conditionally)
- Composition (ISC composes ISC; ISF composes ISF; ISC depends-on ISC)
- Execution (ISC executes ISF; APC executes ISF)
- Provision (ISC provides ISS; ISC provides ISS; ISS provides ISS)
- Realization (BusinessService realized through ISS)
- Exposure (IGC exposes II; APC exposes II; ISC exposes II; ISS exposes II)
- Use (ISC uses II; APC uses II; BusinessProcess uses ISS)
- Specification (API specifies II)
- Exchange (II exchanges Event; II exchanges DataEntity)

The negative tests cover invalid specializations, invalid relationship endpoints, invalid category assignments, duplicate semantic identities, and abstract-entity instantiations. The catalogue is consumed by `tests/conformance/` and the catalog CI workflows.

## 7. Closed-Vocabulary Profile

The closed-vocabulary profile is at `docs/is-semantic-architecture/closed-vocabulary-profile.yaml`. It records the closed vocabulary of:

- **Entities introduced**: ISF, ISC, ISS, II (with their class_aliases, profiles, layers, building_blocks, abstract flags, specializations, legacy_ids, artifacts).
- **Entities reconciled**: SystemFunction, SolutionComponent, ApplicationComponent, IntegrationComponent, InfrastructureComponent, PlatformService, API.
- **Relationship introduced**: `dea:specifies` (CR-021; category `contract`; source `dea:API`; target `dea:IntegrationInterface`; inverse `dea:specified-by`).
- **Relationships extended**: 18 endpoint extensions across CR-018..CR-021.
- **Category introduced**: `contract` (category M; new controlled-vocabulary entry).
- **Vocabulary constraints**: kebab-case preferred; type constraints on entity and relationship ids; class aliases; deprecation signals.

The profile is consumed by `CR-AR-FMWK-04`, `CR-013 (dea-governance)`, and the catalog CRs.

## 8. OpenDEAM Identifier Map Stub

The OpenDEAM identifier map stub is at `docs/is-semantic-architecture/opendeam-identifier-map.yaml`. It maps each `open_deam:dea:*` legacy id to the canonical metamodel `dea:*` id, with a per-CR disposition note.

The map is a stub; the canonical version is owned by `CR-AR-FMWK-04` (OpenDEAM allocation + relationship integration). The stub documents the per-CR resolution as of the IS Semantic Architecture programme closure (2026-10-16) so that downstream CRs have a starting point.

## 9. Conformance and Validation

Local CI verification:

- `python3 .github/scripts/validate_metamodel_yaml.py` PASS (legacy stub).
- `python3 .github/scripts/validate_json_schemas.py` PASS (127 schemas).
- `python3 .github/scripts/validate_ttl.py` SKIP (rdflib not installed locally).
- `python3 .github/scripts/generate_registry.py` PASS (151 entities / 105 relationships).
- `python3 .github/scripts/generate_specification.py` PASS (inventory(151e/105r), vocabulary, 2 catalogues).
- `python3 .github/scripts/generate_pydantic.py` PASS (123 pydantic modules + entity.py).
- `cd typescript && npx tsc --noEmit` PASS.
- `python3 -m pytest tests/conformance/` PASS (133 tests).
- `python3 -m pytest tests/runtime/` PASS (290 tests).
- `python3` SQLite parse of `sqlite/schema.sql` PASS (99 tables).
- D-004 / D-005 / Standardization-body embargo: clean across all changed files.

## 10. Cross-Repository Impact

| Repository | Required alignment |
|---|---|
| `technehub-labs/dea-architecture-framework` | `CR-AR-FMWK-04` adds the four new entities, the new `dea:specifies` relationship, the new `contract` category, and the OpenDEAM-to-metamodel identifier map to `model/opendeam-model.yaml` |
| `technehub-labs/dea-governance` | `CR-013 (dea-governance)` registers the four new entities, the new relationship, the new category, the migration ID map, the conformance test catalogue, the closed-vocabulary profile, and the catalog-ownership register in the portfolio |
| `technehub-labs/dea-catalog-system-functions` → `dea-catalog-information-system-functions` | `CR-IS-CAT-01` renames and extends the existing catalog |
| `technehub-labs/dea-catalog-application-components` → `dea-catalog-information-system-components` | `CR-IS-CAT-02` renames and extends the existing catalog |
| `technehub-labs/dea-catalog-platform-services` (+ new `dea-catalog-information-system-services`) | `CR-IS-CAT-03` establishes the new catalog and migrates IS-related platform services |
| `technehub-labs/dea-catalog-api-contracts` (+ new `dea-catalog-information-system-integration-interfaces`) | `CR-IS-CAT-04` extends the existing catalog and establishes the new interface catalog |

## 11. Migration and Compatibility

This is the closure CR. There are no new entity introductions. The `artifacts.*` paths are populated; the generated artifacts are present and consistent. The D-004 cleanup pass is a documentation refinement, not a structural change.

The legacy `dea:SystemFunction` continues to resolve under its identity; EGV-004 is preserved. The new `dea:InformationSystemFunction` is the canonical entity for new models.

## 12. Acceptance Criteria

- [ ] `artifacts.pydantic_model` populated for ISF, ISC, ISS, II.
- [ ] `artifacts.sqlite_table` populated for ISF, ISC, ISS, II.
- [ ] `artifacts.ts_interface` populated for ISF, ISC, ISS, II.
- [ ] Four new Pydantic modules land: `pydantic/information_system_function.py`, `pydantic/information_system_component.py`, `pydantic/information_system_service.py`, `pydantic/integration_interface.py`.
- [ ] SQLite schema CHECK constraint includes the four new entity types and the new `specifies` relationship type.
- [ ] TypeScript `interfaces.ts` includes the four new `BaseEntity` interfaces; `AnyEntity` and `ENTITY_TYPES` are extended; `tsc --noEmit` PASS.
- [ ] TTL ontology `dea-metamodel-ontology.ttl` includes the four new `owl:Class` declarations and the new `dea:specifies` `owl:ObjectProperty` declaration.
- [ ] D-004 cleanup pass complete on touched files.
- [ ] Four closure documents present under `docs/is-semantic-architecture/`.
- [ ] Local CI conformance and runtime test suites pass.
- [ ] Cardinal author rule (CR-MM-04 R1) is satisfied: `Author: Emmanuel A. Otchere`.
- [ ] Cardinal author rule (CR-MM-04 R2) is satisfied: this PR is one logical change (artifacts closure + generator runs + schema/type/TTL extensions + D-004 cleanup + closure documents + docs); no bundle content from CR-AR-FMWK-04.
- [ ] D-004 / D-005 / Standardization-body embargo clean.

## 13. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `RelationshipType` union inconsistency (DRIFT-5) | Parked for a separate refactoring CR; CR-022 does not expand the union |
| TTL generator not yet implemented (DRIFT-6) | The new entities and the new relationship were added manually in CR-022; a TTL generator is a future-CR concern |
| Generated artifact drift | All generators are deterministic; CI runs them and checks byte-identity |
| Author confusion (CR-MM-04 author header) | R1 cardinal rule enforced by `validate-authorship.yml` |
| Cross-cite drift with downstream CRs | D-5 disposition binds the OpenDEAM-to-metamodel identifier map to CR-AR-FMWK-04; the migration ID map is the bridge |

## 14. Completion Definition

CR-022 is complete when:

1. The four `artifacts.*` paths are populated for the four new entities.
2. The four new Pydantic modules land.
3. The SQLite schema CHECK constraint is extended.
4. The TypeScript interfaces and unions are extended.
5. The TTL ontology is extended.
6. D-004 cleanup pass is complete.
7. The four closure documents are present.
8. Local CI checks pass.
9. PR opens against `origin/main`; CI on GitHub Actions shows green before user review.
10. The PR card moves from `In Progress` to `Review` on the board-23 kanban surface.

## 15. Path Y Completion

The metamodel-side slice of Path Y is complete after CR-022 lands. The remaining Path Y work is downstream:

1. `CR-AR-FMWK-04` (OpenDEAM allocation + relationship integration)  :  consumes the OpenDEAM identifier map stub and the migration ID map.
2. `CR-IS-CAT-01..04` (catalog renames + new catalogs)  :  consume the closed-vocabulary profile, the migration ID map, and the conformance test catalogue.
3. `CR-013 (dea-governance)` (portfolio adoption)  :  the closure gate; consumes the migration ID map, the conformance test catalogue, the closed-vocabulary profile, the OpenDEAM identifier map, and the catalog-ownership register.

## 16. References

### 16.1 Inputs and authorities

- `technehub-labs/dea-metamodel/change-requests/CR-017-information-systems-domain-semantic-integration.md` (foundation; merged 2026-10-16 via PR #170, commit `3e00b35`)
- `technehub-labs/dea-metamodel/change-requests/CR-018-information-system-function.md` (merged 2026-10-16 via PR #171, commit `0f16441`)
- `technehub-labs/dea-metamodel/change-requests/CR-019-information-system-component.md` (merged 2026-10-16 via PR #172, commit `5812cfb`)
- `technehub-labs/dea-metamodel/change-requests/CR-020-information-system-service.md` (merged 2026-10-16 via PR #173, commit `6747d84`)
- `technehub-labs/dea-metamodel/change-requests/CR-021-integration-interface.md` (merged 2026-10-16 via PR #174, commit `9e02ee5`)
- ADR-ISA-000 (foundation paper)
- CR-MM-PROC-01 (kernel+specialization template)
- CR-016 + ADR-015 (kernel+specialization template)
- CR-MM-04 (authorship cardinal rule R1, R2)
- CR-MM-ECF-04 (entity-system cross-reference)
- CR-AR-FMWK-03 (architecture cross-reference)
- CR-012 (`dea-governance`; EGV-001..012 normative requirements)
- DEA-ID-000 (`dea-governance` foundation paper)

### 16.2 Closure documents (this PR)

- `docs/is-semantic-architecture/migration-id-map.yaml` (9 entries)
- `docs/is-semantic-architecture/conformance-test-catalogue.yaml` (9 positive + 10 negative tests)
- `docs/is-semantic-architecture/closed-vocabulary-profile.yaml` (4 introduced + 7 reconciled entities, 1 new relationship, 1 new category)
- `docs/is-semantic-architecture/opendeam-identifier-map.yaml` (10 mappings, 5 notes for CR-AR-FMWK-04)

### 16.3 Companion Kanban surface

- Project 23 (DEAMMISE) at `/board/23`: card #391 (CR-022 programme), In Progress during authoring
- Companion umbrella carrier #384
- DRIFT-4 card #419 (InfrastructureComponent placement decision; recorded)
- DRIFT-5 (TypeScript RelationshipType union) and DRIFT-6 (TTL generator) recorded in this CR; cards pending
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`

---

End of CR-022.
