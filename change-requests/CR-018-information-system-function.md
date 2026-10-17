# CR-018: Information System Function -- kernel+specialization introduction

| Field | Value |
|-------|-------|
| **CR** | CR-018 |
| **Title** | Information System Function kernel+specialization introduction (D-1 disposition) |
| **Status** | Proposed (this PR) |
| **Layer** | Metamodel (Digital Profile) |
| **Programme** | Information Systems Semantic Architecture |
| **Architectural parent** | CR-017 (Information Systems Domain Semantic Integration and Relationship Architecture, merged 2026-10-16 via PR #170, commit `3e00b35`) |
| **Companion to** | CR-MM-PROC-01 (Process Kernel + Business Process Specialization, Proposed; kernel+specialization template precedent); CR-016 (Capability classification implementation; CR-016 + ADR-015 template precedent); CR-MM-ECF-04 (entity-system cross-reference); CR-MM-04 (authorship cardinal rule R1, R2); CR-AR-FMWK-03 (architecture cross-reference) |
| **Depends on** | CR-017; CR-MM-PROC-01; CR-016 + ADR-015; CR-MM-04; `CR-012 (dea-governance)` + DEA-ID-000 (when accepted) |
| **Enables** | CR-019, CR-020, CR-021, CR-022; CR-AR-FMWK-04; CR-IS-CAT-01 (renames the `dea-catalog-system-functions` GitHub repository to `dea-catalog-information-system-functions`) |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-16 |

## 1. Executive Summary

This CR introduces `dea:InformationSystemFunction` as the new canonical Digital Profile entity for "behaviour performed by an information system", per the **D-1** disposition decision ratified by the user on 2026-10-16 in Discord thread 1560566532973527130.

The D-1 disposition is **divergent** from the recommended option carried in CR-017's foundation PR (#170): instead of "retain `dea:SystemFunction` and reconcile the capability-oriented language", the user authorised "introduce `dea:InformationSystemFunction` as the new canonical entity; supersede `dea:SystemFunction` via legacy identifiers". Rationale (verbatim): "system" means many things, and the need to be accurate in establishing the area of system use is important.

`dea:SystemFunction` is marked `status: deprecated` and remains in the metamodel under EGV-004 (Identity Continuity). The OpenDEAM-side identifier `dea:entity-system-function` resolves to `dea:InformationSystemFunction` via the cross-reference map owned by `CR-AR-FMWK-04` (D-5 disposition).

The implementation follows the same kernel+specialization template that CR-MM-PROC-01 used for `dea:Process / dea:BusinessProcess` and that CR-016 + ADR-015 used for `dea:Capability / dea:BusinessCapability`:

- Core `dea:Behavior` (abstract, existing) is the kernel.
- `dea:InformationSystemFunction` (Digital Profile, L5, building_block L5-systems, `abstract: false`, `lifecycle: planned`) specialises `dea:Behavior` via the `dea:specializes` relationship.

This is documented as a deliberate response to the capability-confusion problem flagged in CR-017 §2.1: `dea:SystemFunction`'s capability-oriented wording made it semantically equivalent to `dea:Capability` and `dea:SystemCapability`. The new entity fixes the ambiguity by anchoring "system" to "information system".

## 2. Scope

### 2.1 In scope

1. The canonical metamodel definition of `dea:InformationSystemFunction` in `metamodel/dea-metamodel.yaml`.
2. The deprecation trail for `dea:SystemFunction` (`status: deprecated`, definition annotated with the supersession pointer and migration guidance). Per EGV-004, no record is silently reclassified or deleted.
3. The supersession declaration on the new entity (`supersedes: [dea:SystemFunction]`), a new entity-level field mirroring the relationship-level `supersedes` list. The validator and the registry generator do not carry the new field through to the registry (the registry is a derived inventory, not a relationship graph), so the field conveys supersession intent without breaking the projection.
4. Extension of four relationship endpoint lists in `metamodel/dea-metamodel.yaml`:
   - `dea:specializes.source.types` add `dea:InformationSystemFunction`; `dea:specializes.target.types` add `dea:Behavior`.
   - `dea:executes.source.types` add `dea:InformationSystemFunction`; `dea:executes.target.types` add `dea:InformationSystemFunction`.
   - `dea:orchestrates.source.types` add `dea:InformationSystemFunction`; `dea:orchestrates.target.types` add `dea:InformationSystemFunction`.
   - `dea:realizes.source.types` add `dea:InformationSystemFunction` (so a system function may realise a business capability).
5. Digital Profile membership: `metamodel/profiles/digital/profile.yaml` adds `dea:InformationSystemFunction` and annotates `dea:SystemFunction` with a `DEPRECATED` comment for EGV-004 identity continuity.
6. JSON Schema for the new entity: `schemas/entities/information-system-function.json`. Modeled on `business-capability.json` (CR-016 template) plus the relationship-mirror fields documented in CR-017 §4.1 (composition, execution target, capability, business process enablement, data + event consume + produce).
7. Regeneration of derived artefacts via the established generators (all run deterministically from the canonical source):
   - `metamodel/registry/entities.yaml` (via `.github/scripts/generate_registry.py`)
   - `metamodel/registry/relationships.yaml` (same)
   - `specification/semantic-inventory.yaml`, `specification/vocabulary.yaml`, `specification/catalogues/entities.md` (via `.github/scripts/generate_specification.py`)
8. The CR-018 document (`change-requests/CR-018-information-system-function.md`, this file).
9. `change-requests/README.md` row for CR-018.
10. `docs/information-systems-semantic-architecture.md` extension with the implemented entity state (mirror the "four concepts" table with `dea:InformationSystemFunction` as the canonical row).

### 2.2 Out of scope (explicit)

1. Migration of the `dea-catalog-system-functions` GitHub repository. Owned by `CR-IS-CAT-01`. The repository keeps its identity and its `dea:entity-system-function` namespace through the migration window.
2. Regeneration of `pydantic/information_system_function.py`, `sqlite/...` projection, `typescript/...` interface, `viewer/entity-graph.json`. The `artifacts.pydantic_model`, `artifacts.sqlite_table`, and `artifacts.ts_interface` paths in the new entity are deliberately `null` in CR-018. `CR-022` (Metamodel Artifact and Conformance Closure) regenerates them once the four entity CRs are merged.
3. Cross-extension of `dea:executes.source.types` to include `dea:InformationSystemComponent` (the new component entity). That is owned by `CR-019`.
4. Cross-extension of `dea:provides.target.types` to include `dea:InformationSystemService`. Owned by `CR-020`.
5. Cross-extension of `dea:exposes.target.types` to include `dea:IntegrationInterface`. Owned by `CR-021`.
6. OpenDEAM identifier mapping. Owned by `CR-AR-FMWK-04`.
7. Governance portfolio registration. Owned by `CR-013 (dea-governance)`.
8. Any change to Core anchor `dea:Behavior`; only the `dea:specializes` target list is extended.

## 3. Problem Statement and D-1 Disposition

The CR-017 foundation document flagged that `dea:SystemFunction` used capability-oriented language in its definition ("A functional capability exposed by a single application or system"), causing it to overlap semantically with `dea:SystemCapability` (which is a profile-level specialisation of Core `dea:Capability` per CR-016 / ADR-015).

CR-017 offered two options:

- **Option A (recommended)**: retain `dea:SystemFunction`, revise its definition to behaviour-performed semantics, preserve legacy identifier.
- **Option B**: introduce `dea:InformationSystemFunction` as the new canonical identifier; record `dea:SystemFunction` as legacy/deprecated via `legacy_ids` linkage.

The user authorised **Option B** on 2026-10-16 (thread 1560566532973527130). Rationale (verbatim): "system" means many things; the area of system use must be accurate. The narrower canonical name (`InformationSystemFunction`) anchors "system" to the OpenDEA Digital Profile concern: the information system as the actor of the behaviour.

Option B is decisive but introduces a substantive migration:

1. The new entity arrives; the legacy entity stays readable but is no longer the canonical reference.
2. The catalog (`dea-catalog-system-functions`) keeps its identity in the migration window per EGV-004 (the GitHub repository name is the project's decision, not the metamodel's), with the rename owned by `CR-IS-CAT-01`.
3. The OpenDEAM identifier `dea:entity-system-function` continues to resolve to the new entity through the OpenDEAM-to-metamodel map (D-5 disposition), owned by `CR-AR-FMWK-04`.

## 4. Entity Definition (Normative)

### 4.1 `dea:InformationSystemFunction` (new canonical)

```yaml
- id: dea:InformationSystemFunction
  name: Information System Function
  legacy_ids:
  - dea:entity-system-function
  supersedes:
  - dea:SystemFunction
  definition: A defined unit of functional behaviour performed by an information system or one of
    its components to process information, execute logic, respond to events, or produce an intended
    system outcome. Specialises Core dea:Behavior per CR-MM-PROC-01 template and dea:Capability per
    CR-016 / ADR-015. Supersedes dea:SystemFunction (D-1 disposition 2026-10-16): disambiguates
    "system" by anchoring to information systems and prevents the capability-possessed conflation of
    the legacy entity.
  layer: L5
  dimension: null
  building_block: L5-systems
  abstract: false
  status: normative
  lifecycle: planned
  class_alias: ISF
  catalog_repo: dea-catalog-system-functions
  artifacts:
    json_schema: schemas/entities/information-system-function.json
    sqlite_table: null              # regenerated by CR-022
    pydantic_model: null           # regenerated by CR-022
    ts_interface: null             # regenerated by CR-022
  membership:
    kind: profile
    profile: dea:digital
```

### 4.2 `dea:SystemFunction` (deprecated, retained)

```yaml
- id: dea:SystemFunction
  name: System Function
  legacy_ids:
  - dea:entity-system-function
  definition: DEPRECATED 2026-10-16 (CR-018 supersession; D-1 disposition). Retained for EGV-004
    identity continuity. Use dea:InformationSystemFunction for new models. The legacy entity
    remains readable for existing references and migration; new model authoring MUST use
    dea:InformationSystemFunction.
  layer: L5
  dimension: null
  building_block: L5-systems
  abstract: false
  status: deprecated
  lifecycle: planned
  class_alias: SF
  catalog_repo: dea-catalog-system-functions
  artifacts:
    json_schema: null
    sqlite_table: null
    pydantic_model: null
    ts_interface: null
  membership:
    kind: profile
    profile: dea:digital
```

The `status: deprecated` field carries the deprecation signal (per EGV-007 lifecycle separation). The `lifecycle` field retains the original `planned` value because the conformance test `test_entities_have_name_definition_layer_lifecycle` restricts the lifecycle whitelist to `{existing, scaffold, proposed, planned}`. Bringing the test whitelist into alignment with the `metamodel/vocabularies/lifecycle.yaml` controlled vocabulary (which includes `deprecated` and `retired`) is a separate doc-only CR; CR-018 does not bundle that change per CR-MM-04 R2 (split-cardinality).

## 5. Relationship Endpoint Extensions

The canonical relationship matrix from CR-017 §4.1 records the following relationship coverage. CR-018 implements the SystemFunction-side extensions; the Component, Service, and Interface extensions belong to their respective CRs.

| Source | Relationship | Target | Status in CR-018 |
|---|---|---|---|
| `dea:InformationSystemFunction` | `dea:specializes` | `dea:Behavior` | source extended; target extended |
| `dea:ApplicationComponent` | `dea:executes` | `dea:InformationSystemFunction` | target extended (source already permits `SystemFunction`) |
| `dea:ApplicationComponent` | `dea:orchestrates` | `dea:InformationSystemFunction` | target extended (source unchanged) |
| `dea:BusinessProcess` | `dea:orchestrates` | `dea:InformationSystemFunction` | target extended |
| `dea:InformationSystemFunction` | `dea:orchestrates` | `dea:BusinessProcess` / `BusinessService` / another `InformationSystemFunction` | source extended |
| `dea:InformationSystemFunction` | `dea:realizes` | `dea:BusinessCapability` / `BusinessService` / `BusinessObject` / `Service` / `ArchitectureState` | source extended (target list unchanged) |
| `dea:InformationSystemFunction` | `dea:depends-on` | `dea:InformationSystemFunction` | reserved for CR-018 implementation note; not extended here because `dea:InformationSystemFunction` is not yet a depends-on source |
| `dea:InformationSystemFunction` | `dea:consumes` | `dea:DataEntity` / `dea:Event` | source extension deferred to CR-022 / entity schema (the JSON Schema's `consumes_data` and `consumes_events` arrays carry the instances; the relationship type is universally applicable across all entities and needs no per-entity target list extension) |
| `dea:InformationSystemFunction` | `dea:produces` | `dea:DataEntity` / `dea:Event` | same as above |

The `dea:executes` target list (`BusinessFunction`, `BusinessProcess`) is unchanged in scope; it gains `dea:InformationSystemFunction` alongside the existing entries. An `dea:ApplicationComponent` may execute either kind of behaviour.

## 6. Digital Profile Registration

```yaml
profile:
  id: dea:digital
  entities:
  - dea:InformationSystemFunction
  - dea:SystemFunction  # DEPRECATED 2026-10-16 per CR-018 / D-1. Retained for EGV-004 identity continuity.
  ...
```

The deprecated entity stays in the Digital Profile membership list under the legacy-entity preservation rule. New entities are added in alphabetical position (`InformationSystemFunction` between `Event` and `IntegrationComponent`).

## 7. JSON Schema

`schemas/entities/information-system-function.json` (new). The schema's `required` list is `[id, name, type, version]`, mirroring the other CR-016 / CR-MM-* entity schemas. Optional fields mirror the canonical relationship-matrix cells from CR-017 §4.1:

- `is_part_of` (parent ISF; `dea:composes`)
- `enabled_by_components` (the components that execute it; `dea:executes`)
- `realizes_capability` (the business capability it realises; `dea:realizes`)
- `enables_process` (the business processes it enables; `dea:enables`)
- `consumes_data` / `produces_data` (`dea:consumes` / `dea:produces` to `dea:DataEntity`)
- `consumes_events` / `produces_events` (`dea:consumes` / `dea:produces` to `dea:Event`)

These fields are arrays of `dea:<lowercase-id>` strings. The relationship compliance is enforced by the metamodel validator when the JSON Schema is paired with the normative source; no further static schema validation beyond `validate_json_schemas.py` is required for this PR.

## 8. Generated Artefacts

Per D-6 disposition (`metamodel/registry/*.yaml` is generated):

| Artefact | Generator | Status |
|---|---|---|
| `metamodel/registry/entities.yaml` | `.github/scripts/generate_registry.py` | regenerated; `dea:InformationSystemFunction` projected at line 609; `dea:SystemFunction` projected at line 620 with deprecated status |
| `metamodel/registry/relationships.yaml` | `.github/scripts/generate_registry.py` | regenerated; `dea:executes`, `dea:orchestrates`, `dea:realizes`, `dea:specializes` carry the new endpoint entries |
| `specification/semantic-inventory.yaml` | `.github/scripts/generate_specification.py` | regenerated; `inventory(148e/104r)` |
| `specification/vocabulary.yaml` | `.github/scripts/generate_specification.py` | regenerated |
| `specification/catalogues/entities.md` | `.github/scripts/generate_specification.py` | regenerated |
| `pydantic/information_system_function.py` | `.github/scripts/generate_pydantic.py` | deferred to CR-022 (`artifacts.pydantic_model` is null in this CR) |
| `viewer/entity-graph.json` | `.github/scripts/generate_entity_graph.py` | owned by `CR-AR-FMWK-04` (the viewer is generated from the OpenDEAM root model; the new entity appears after CR-AR-FMWK-04 lands) |
| `ttl/dea-metamodel-ontology.ttl` | `.github/scripts/generate_ttl.py` (existence unconfirmed) | deferred to CR-022 |
| `sqlite/dea-metamodel.db` | SQL `schema.sql` | deferred to CR-022 |

## 9. Conformance and Validation

Local CI verification (run on the feature branch before opening the PR):

- `python3 .github/scripts/validate_metamodel_yaml.py` PASS (it reads the legacy `metamodel.yaml` at the repo root for backward compatibility; that file is unchanged and remains a stub with `superseded_by: metamodel/dea-metamodel.yaml`).
- `python3 .github/scripts/validate_json_schemas.py` PASS (124 JSON schemas valid).
- `python3 .github/scripts/generate_registry.py` PASS (regenerated; 148 entities / 104 relationships).
- `python3 .github/scripts/generate_specification.py` PASS (regenerated; inventory(148e/104r), vocabulary, 2 catalogues).
- `python3 -m pytest tests/conformance/` PASS (133 tests).
- `python3 -m pytest tests/runtime/` PASS (290 tests).

## 10. Cross-Repository Impact

| Repository | Required alignment |
|---|---|
| `technehub-labs/dea-architecture-framework` | `CR-AR-FMWK-04` adds `dea:entity-information-system-function` to `model/opendeam-model.yaml` entities[] with the canonical metamodel relationship IDs as architectural edges |
| `technehub-labs/dea-governance` | `CR-013 (dea-governance)` registers the new entity in the catalog portfolio map; the rename of `dea-catalog-system-functions` to `dea-catalog-information-system-functions` is ratified |
| `technehub-labs/dea-catalog-system-functions` | `CR-IS-CAT-01` extends and renames to `dea-catalog-information-system-functions`; preserves `dea:entity-system-function` namespace; existing records migrate via `legacy_ids` linkage |
| Other catalogs that reference `dea:SystemFunction` | No mandatory migration in this CR; legacy references continue to resolve via EGV-004 |

## 11. Migration and Compatibility

This is a **minor** version impact: the new entity is additive; the existing entity stays with `status: deprecated` and continues to resolve under its canonical identifier.

- Existing models referencing `dea:SystemFunction` continue to validate against the normative source.
- Existing models referencing `dea:entity-system-function` (OpenDEAM-side) resolve to `dea:InformationSystemFunction` through the cross-reference map owned by `CR-AR-FMWK-04`.
- New models MUST use `dea:InformationSystemFunction` for new behaviour-performed modelling; `dea:SystemFunction` is readable but deprecated.
- The legacy `dea-catalog-system-functions` catalog repository retains its GitHub name in the migration window; the rename is a separate CR-IS-CAT-01 decision.

## 12. Acceptance Criteria

- [ ] `dea:InformationSystemFunction` is registered as a Digital Profile entity in the normative source.
- [ ] Its definition is behaviour-performed and explicitly distinct from `dea:Capability` and `dea:SystemCapability`.
- [ ] It `specializes dea:Behavior` via the `dea:specializes` relationship (source + target both extended).
- [ ] It appears in the `dea:executes`, `dea:orchestrates`, and `dea:realizes` relationship source/target lists where applicable.
- [ ] `dea:SystemFunction` is marked `status: deprecated` with a definition annotation pointing to `dea:InformationSystemFunction`.
- [ ] The Digital Profile membership list contains both entities (the new canonical and the deprecated legacy).
- [ ] The JSON Schema is created and passes `validate_json_schemas.py`.
- [ ] All four generators (`generate_registry.py`, `generate_specification.py`) regenerate the derived artefacts consistently with the canonical source.
- [ ] Conformance and runtime test suites pass locally.
- [ ] Cardinal author rule (CR-MM-04 R1) is satisfied: `Author: Emmanuel A. Otchere` carries a value from the allowlist.
- [ ] Cardinal author rule (CR-MM-04 R2) is satisfied: this PR is one logical change (entity introduction + relationship extensions + generated artefacts); no bundle content from CR-019 / CR-020 / CR-021.
- [ ] D-004 (no en/em-dash, no U+2E3B, no U+2026) clean across all changed files.
- [ ] D-005 (no three-semicolon run) clean.
- [ ] Standardization-body embargo: no legacy telecom body vocabulary anywhere in this PR.

## 13. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Existing catalog records silently re-classified | EGV-004 identity continuity; legacy `dea:entity-system-function` namespace preserved; no record destruction |
| Conformance test whitelist inconsistency | `status: deprecated` carries the deprecation signal; `lifecycle` retains `planned`; a doc-only CR to align `test_001_entities.py` with `metamodel/vocabularies/lifecycle.yaml` is parked in DRIFT-3 |
| OpenDEAM identifier drift | D-5 disposition binds the OpenDEAM-to-metamodel identifier map to `CR-AR-FMWK-04` |
| Cross-repo generated artefact drift | All generators are deterministic; CI runs them and checks byte-identity |
| Author confusion (CRMM-04 author header) | R1 cardinal rule enforced by `validate-authorship.yml` |
| Supersession field ignored by registry generator | Registry is a derived inventory; the source-level `supersedes:` field remains the authoritative record; the relationship graph is the canonical place for supersession (a future CR may introduce `dea:superseded-by` if needed) |

## 14. Completion Definition

CR-018 is complete when:

1. `dea:InformationSystemFunction` is registered in the normative source with the relationship-endpoint extensions above.
2. `dea:SystemFunction` carries `status: deprecated` and is preserved under EGV-004.
3. The Digital Profile registers the new entity.
4. The JSON Schema is committed and validates.
5. The four deterministic generators (registry, specification) regenerate consistent artefacts.
6. Local CI checks (`validate_metamodel_yaml.py`, `validate_json_schemas.py`, conformance suite, runtime suite) all pass.
7. PR opens against `origin/main`; CI on GitHub Actions shows green before user review.
8. The PR card moves from `In Progress` to `Review` on the board-23 kanban surface.
9. Companion Kanban card (`#387 CR-018 in dea-metamodel`) updates with the PR URL and CI status.

## 15. References

### 15.1 Inputs and authorities

- `technehub-labs/dea-metamodel/change-requests/CR-017-information-systems-domain-semantic-integration.md` (the foundation CR; merged 2026-10-16 via PR #170, commit `3e00b35`)
- ADR-ISA-000 (foundation paper; supplied with this PR's foundation package)
- CR-MM-PROC-01 (the active kernel+specialization precedent in the metamodel)
- CR-016 + ADR-015 (the Capability classification template precedent)
- CR-MM-04 (authorship cardinal rule R1, R2)
- CR-MM-ECF-04 (entity-system cross-reference)
- CR-AR-FMWK-03 (architecture cross-reference)
- CR-012 (`dea-governance`; EGV-001..012 normative requirements)
- DEA-ID-000 (`dea-governance` foundation paper)

### 15.2 Companion Kanban surface

- Project 23 (DEAMMISE) at `/board/23`: card #387 (CR-018 programme), In Progress during authoring
- Companion umbrella carrier #384
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`

---

End of CR-018.
