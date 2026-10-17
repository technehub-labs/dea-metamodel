# CR-020: Information System Service -- kernel+specialization + PlatformService reconciliation

| Field | Value |
|-------|-------|
| **CR** | CR-020 |
| **Title** | Information System Service kernel+specialization + PlatformService reconciliation (D-3 disposition) |
| **Status** | Proposed (this PR) |
| **Layer** | Metamodel (Digital Profile) |
| **Programme** | Information Systems Semantic Architecture |
| **Architectural parent** | CR-017 (Information Systems Domain Semantic Integration and Relationship Architecture, merged 2026-10-16 via PR #170, commit `3e00b35`); CR-018 (Information System Function, merged 2026-10-16 via PR #171, commit `0f16441`); CR-019 (Information System Component, merged 2026-10-16 via PR #172, commit `5812cfb`) |
| **Companion to** | CR-MM-PROC-01 (kernel+specialization template); CR-016 (kernel+specialization template, ADR-015); CR-MM-04 (authorship cardinal rule R1, R2); CR-MM-ECF-04 (entity-system cross-reference); CR-AR-FMWK-03 (architecture cross-reference) |
| **Depends on** | CR-017; CR-018; CR-019; CR-016 + ADR-015; CR-MM-04; `CR-012 (dea-governance)` + DEA-ID-000 (when accepted) |
| **Enables** | CR-021 (introduces `dea:IntegrationInterface`; widens `dea:exposes.target.types` to include the new entity); CR-022 (closes artifact regeneration + conformance); CR-AR-FMWK-04; CR-IS-CAT-03 (new `dea-catalog-information-system-services`) |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-16 |

## 1. Executive Summary

This CR introduces `dea:InformationSystemService` as the new canonical Digital Profile entity for "service provided by an information system or a software platform to a consumer", per the **D-3** disposition decision ratified by the user on 2026-10-16 in Discord thread 1560566532973527130.

The D-3 disposition has two coupled outcomes:

1. The new entity `dea:InformationSystemService` (L5, building_block L5-integration, profile dea:digital, `abstract: false`, `lifecycle: planned`) is introduced as a Digital Profile specialisation of Core `dea:Service`. It follows the same kernel+specialization template used by CR-MM-PROC-01 (`dea:Process / dea:BusinessProcess`), CR-016 (`dea:Capability / dea:BusinessCapability`), CR-018 (`dea:Behavior / dea:InformationSystemFunction`), and CR-019 (`dea:SolutionComponent / dea:InformationSystemComponent`).
2. The legacy `dea:PlatformService` is reconciled: the registry entry's definition is updated to record the conditional specialisation (D-3). The canonical entry, when the record is genuinely a software-platform service, specialises `dea:InformationSystemService`. Non-information-system infrastructure offerings stay under Core `dea:Service` and are recorded via the catalog-ownership register; they do NOT instantiate `dea:PlatformService`.

A separate outcome (no DRIFT card needed): the relationship matrix extensions from CR-017 §4.3 are implemented. Specifically:

- `dea:provides.target.types` is extended to include `dea:InformationSystemService`. This resolves the CR-019 reserved extension; an InformationSystemComponent may provide an InformationSystemService.
- `dea:provides.source.types` is extended to include `dea:InformationSystemService`. An InformationSystemService may itself provide further services (a service-of-services pattern).
- `dea:uses.source.types` is extended to include `dea:InformationSystemComponent`. An InformationSystemComponent may use an InformationSystemService.
- `dea:uses.target.types` is extended to include `dea:InformationSystemService`. An InformationSystemService is a valid target of `dea:uses`.
- `dea:specializes.source.types` is extended to include `dea:InformationSystemService`. A future specialisation (e.g. `dea:BusinessService`-as-subclass-of-ISS) is possible under the closed vocabulary.

## 2. Scope

### 2.1 In scope

1. The canonical metamodel definition of `dea:InformationSystemService` in `metamodel/dea-metamodel.yaml`.
2. The `dea:PlatformService.definition` annotation recording the D-3 conditional specialisation; the canonical entry specialises `dea:InformationSystemService` per the "when the record is genuinely a software-platform service" framing.
3. Four relationship endpoint extensions in `metamodel/dea-metamodel.yaml`:
   - `dea:provides.target.types` add `dea:InformationSystemService` (resolves the CR-019 reserved extension).
   - `dea:provides.source.types` add `dea:InformationSystemService` (service-of-services pattern).
   - `dea:uses.source.types` add `dea:InformationSystemComponent` (an ISC uses services).
   - `dea:uses.target.types` add `dea:InformationSystemService` (ISS is a target of use).
   - `dea:specializes.source.types` add `dea:InformationSystemService` (allows future sub-classification).
4. Digital Profile membership: `metamodel/profiles/digital/profile.yaml` adds `dea:InformationSystemService` and annotates `dea:PlatformService` with the conditional specialisation note.
5. JSON Schema for the new entity: `schemas/entities/information-system-service.json` (new). Mirrors the `application-component.json` pattern; no inline relationship-state properties (per CR-3 / `test_003_no_duplicate_relationship_state`).
6. Regeneration of derived artefacts via the established generators.
7. The CR-020 document (this file).
8. `change-requests/README.md` row for CR-020.
9. `docs/information-systems-semantic-architecture.md` extension with the implemented entity state.

### 2.2 Out of scope

1. Cross-extension of `dea:exposes.target.types` to include `dea:IntegrationInterface`. Owned by `CR-021`.
2. `artifacts.pydantic_model`, `artifacts.sqlite_table`, `artifacts.ts_interface` paths for the new entity. `null` in this CR; `CR-022` populates them.
3. The new `dea-catalog-information-system-services` repository. Owned by `CR-IS-CAT-03` after CR-022 closure.
4. OpenDEAM identifier mapping. Owned by `CR-AR-FMWK-04`.
5. Governance portfolio registration. Owned by `CR-013 (dea-governance)`.
6. Any change to Core anchor `dea:Service`; only the specialisation surface is extended.
7. Migration of `dea-catalog-platform-services` records. Owned by `CR-IS-CAT-03` (the new repository) and the catalog-ownership register in `CR-013 (dea-governance)`.

## 3. Problem Statement and D-3 Disposition

The CR-017 foundation document flagged that `dea:PlatformService`'s definition ("A shared infrastructure or runtime service consumed by multiple application components") could refer to either information-system services or generic infrastructure primitives. The disposition decision (D-3) was whether `dea:PlatformService` should specialise `dea:InformationSystemService` (the new entity introduced in CR-020) or stay sibling of Core `dea:Service`.

The user ratified the recommended conditional option: `dea:PlatformService` specialises `dea:InformationSystemService` only when the service is genuinely a software-platform service. Non-information-system infrastructure offerings stay under Core `dea:Service`. The canonical entry for `dea:PlatformService` is recorded under the "when genuine" framing; the catalog-ownership register (in `CR-013 (dea-governance)`) carries the per-record gate.

Per the disposition, the canonical record of `dea:PlatformService` in the normative source is updated to specialise `dea:InformationSystemService`. The conditional is documented in the entity's `definition` field so reviewers and downstream consumers can locate the rationale.

## 4. Entity Definitions (Normative)

### 4.1 `dea:InformationSystemService` (new canonical)

```yaml
- id: dea:InformationSystemService
  name: Information System Service
  legacy_ids:
  - dea:entity-information-system-service
  definition: A service provided by an information system or a software platform to a consumer, expressed
    as a contract about the exchange of capability, functionality or data. Specialises Core dea:Service
    (per CR-MM-PROC-01 / CR-016 kernel+specialization template; D-3 disposition 2026-10-16).
  layer: L5
  dimension: null
  building_block: L5-integration
  abstract: false
  status: normative
  lifecycle: planned
  class_alias: ISS
  catalog_repo: dea-catalog-platform-services
  artifacts:
    json_schema: schemas/entities/information-system-service.json
    sqlite_table: null
    pydantic_model: null
    ts_interface: null
  membership:
    kind: profile
    profile: dea:digital
```

### 4.2 `dea:PlatformService` (D-3 conditional specialisation)

```yaml
- id: dea:PlatformService
  name: Platform Service
  legacy_ids:
  - dea:entity-platform-service
  definition: A shared infrastructure or runtime service consumed by multiple application components.
    Per CR-020 (D-3 disposition 2026-10-16): when the record is genuinely a software-platform service
    (i.e., a service offered by an information system or software platform to consumers), the canonical
    record specialises dea:InformationSystemService. Non-information-system infrastructure offerings
    (for example, a generic cloud infrastructure primitive that is not itself an information system)
    stay under Core dea:Service and are recorded via the catalog-ownership register; they do NOT
    instantiate dea:PlatformService. EGV-004 identity continuity: existing dea:entity-platform-service
    references continue to resolve after regeneration.
  layer: L5
  dimension: null
  building_block: L5-infrastructure
  abstract: false
  status: normative
  lifecycle: planned
  class_alias: PS
  catalog_repo: dea-catalog-platform-services
  artifacts:
    json_schema: null
    sqlite_table: null
    pydantic_model: null
    ts_interface: null
  membership:
    kind: profile
    profile: dea:digital
```

The `catalog_repo` for `dea:PlatformService` is left as `dea-catalog-platform-services` (the existing catalog). Per D-3, future catalog split is owned by `CR-IS-CAT-03` (new `dea-catalog-information-system-services` repository for the Information Systems sub-tree).

## 5. Relationship Endpoint Extensions

| Source | Relationship | Target | Status in CR-020 |
|---|---|---|---|
| `dea:InformationSystemComponent` | `dea:provides` | `dea:InformationSystemService` | target added (resolves CR-019 reserved extension) |
| `dea:InformationSystemService` | `dea:provides` | `dea:InformationSystemService` | source added (service-of-services pattern) |
| `dea:ApplicationComponent` | `dea:provides` | `dea:InformationSystemService` | target added (APC may provide an ISS) |
| `dea:InformationSystemComponent` | `dea:uses` | `dea:InformationSystemService` | source added (ISC uses ISS) |
| `dea:ApplicationComponent` | `dea:uses` | `dea:InformationSystemService` | source added (APC uses ISS) |
| `dea:InformationSystemService` | `dea:uses` | `dea:InformationSystemService` | target added (ISS uses another ISS) |
| `dea:InformationSystemService` | `dea:specializes` | (target: any future sub-class) | source added (closed-vocabulary eligibility for future CRs) |
| `dea:BusinessService` | `dea:uses` | `dea:InformationSystemService` | target added (BP uses ISS) |

## 6. Digital Profile Registration

```yaml
profile:
  id: dea:digital
  entities:
  - dea:InformationSystemService   # CR-020; specialises Core dea:Service (D-3 disposition)
  - dea:PlatformService            # CR-020 D-3: when genuinely an IS service, specialises dea:InformationSystemService
  - dea:InformationSystemComponent
  - dea:InformationSystemFunction
  ...
```

## 7. JSON Schema

`schemas/entities/information-system-service.json` (new). Mirrors the `application-component.json` pattern. The schema's `required` list is `[id, name, type, version]`. No inline relationship-state properties (per CR-3 / `test_003_no_duplicate_relationship_state`).

## 8. Generated Artefacts

Per D-6 disposition:

| Artefact | Generator | Status |
|---|---|---|
| `metamodel/registry/entities.yaml` | `.github/scripts/generate_registry.py` | regenerated; `dea:InformationSystemService` projected; 150 entities / 104 relationships |
| `metamodel/registry/relationships.yaml` | `.github/scripts/generate_registry.py` | regenerated; endpoint extensions applied |
| `specification/semantic-inventory.yaml` | `.github/scripts/generate_specification.py` | regenerated; `inventory(150e/104r)` |
| `specification/vocabulary.yaml` | `.github/scripts/generate_specification.py` | regenerated |
| `specification/catalogues/entities.md` | `.github/scripts/generate_specification.py` | regenerated |
| `pydantic/information_system_service.py` | `.github/scripts/generate_pydantic.py` | deferred to CR-022 (`artifacts.pydantic_model` is null) |
| `viewer/entity-graph.json` | `.github/scripts/generate_entity_graph.py` | owned by `CR-AR-FMWK-04` |
| `ttl/dea-metamodel-ontology.ttl` | TTL generator | deferred to CR-022 |
| `sqlite/dea-metamodel.db` | SQL `schema.sql` | deferred to CR-022 |

## 9. Conformance and Validation

Local CI verification (run on the feature branch before opening the PR):

- `python3 .github/scripts/validate_metamodel_yaml.py` PASS (legacy stub; "41/10" output is the deprecated `metamodel.yaml` count).
- `python3 .github/scripts/validate_json_schemas.py` PASS (126 JSON schemas valid).
- `python3 .github/scripts/generate_registry.py` PASS (150 entities / 104 relationships).
- `python3 .github/scripts/generate_specification.py` PASS (inventory(150e/104r), vocabulary, 2 catalogues).
- `python3 -m pytest tests/conformance/` PASS (133 tests).
- `python3 -m pytest tests/runtime/` PASS (290 tests).

## 10. Cross-Repository Impact

| Repository | Required alignment |
|---|---|
| `technehub-labs/dea-architecture-framework` | `CR-AR-FMWK-04` adds `dea:entity-information-system-service` to `model/opendeam-model.yaml` entities[] with the canonical metamodel relationship IDs as architectural edges |
| `technehub-labs/dea-governance` | `CR-013 (dea-governance)` registers the new entity in the catalog portfolio map; the new `dea-catalog-information-system-services` repository is ratified; the catalog-ownership register is updated with the D-3 conditional gate |
| `technehub-labs/dea-catalog-platform-services` | The existing catalog's record gate is updated; IS-related platform services migrate to the new `dea-catalog-information-system-services`; non-IS infrastructure offerings stay under Core `dea:Service` |
| `technehub-labs/dea-catalog-information-system-services` (new) | `CR-IS-CAT-03` establishes the new repository with the initial population of IS-related platform services |
| Other catalogs that reference `dea:PlatformService` or `dea:BusinessService` | No mandatory migration in this CR; legacy references continue to resolve via EGV-004 |

## 11. Migration and Compatibility

This is a **minor** version impact: the new entity is additive; the existing `dea:PlatformService` is augmented with a definition annotation and the canonical specialisation (still resolving under the same canonical identifier).

- Existing models referencing `dea:PlatformService` continue to validate against the normative source.
- The catalog-ownership register (`CR-013 (dea-governance)`) records per-catalog gates for the conditional specialisation; catalogs that need to record non-IS infrastructure offerings do so via a separate (Core-`dea:Service`-rooted) entity, not via `dea:PlatformService`.
- New models MAY specialise `dea:InformationSystemService` directly (the closed `dea:specializes` vocabulary permits this after CR-020's source-list extension).

## 12. Acceptance Criteria

- [ ] `dea:InformationSystemService` is registered as a Digital Profile entity in the normative source.
- [ ] Its definition is service-IS-anchored and explicitly distinct from `dea:BusinessService` and Core `dea:Service`.
- [ ] It `specializes Core dea:Service` via the `dea:specializes` relationship (source added).
- [ ] `dea:PlatformService` definition records the D-3 conditional specialisation; the canonical entry specialises `dea:InformationSystemService`.
- [ ] Four relationship endpoint extensions are applied: `dea:provides.target`, `dea:provides.source`, `dea:uses.source`, `dea:uses.target`.
- [ ] Digital Profile membership registers the new entity.
- [ ] The JSON Schema is created and passes `validate_json_schemas.py`; it intentionally does NOT include inline relationship-state properties per CR-3.
- [ ] All four generators regenerate consistent artefacts.
- [ ] Local CI conformance and runtime test suites pass.
- [ ] Cardinal author rule (CR-MM-04 R1) is satisfied: `Author: Emmanuel A. Otchere`.
- [ ] Cardinal author rule (CR-MM-04 R2) is satisfied: this PR is one logical change (entity introduction + PlatformService annotation + 4 relationship extensions + generated artefacts + docs); no bundle content from CR-021 / CR-022.
- [ ] D-004 / D-005 / Standardization-body embargo clean.

## 13. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `dea:PlatformService` re-classification silently drops non-IS infrastructure records | EGV-004 identity continuity; the catalog-ownership register in `CR-013 (dea-governance)` records per-catalog gates; non-IS offerings stay under Core `dea:Service` |
| Conformance test whitelist inconsistency | `status: deprecated` carries the deprecation signal where applicable; `lifecycle` retains `planned`; the test-alignment CR is parked in DRIFT-3 |
| OpenDEAM identifier drift | D-5 disposition binds the OpenDEAM-to-metamodel identifier map to `CR-AR-FMWK-04` |
| Cross-cite drift with `dea:InformationSystemFunction` (CR-018) and `dea:InformationSystemComponent` (CR-019) | D-1, D-2, D-3 dispositions are sequenced (D-1 -> D-2 -> D-3) and the cross-references are documented in each CR's "References" section |
| Generated artefact drift | All generators are deterministic; CI runs them and checks byte-identity |
| Author confusion (CR-MM-04 author header) | R1 cardinal rule enforced by `validate-authorship.yml` |

## 14. Completion Definition

CR-020 is complete when:

1. `dea:InformationSystemService` is registered in the normative source with the four relationship endpoint extensions.
2. `dea:PlatformService` carries the D-3 conditional specialisation annotation in the definition body.
3. Digital Profile registers the new entity.
4. The JSON Schema is committed and validates; CR-3 conformance is preserved.
5. The four deterministic generators regenerate consistent artefacts.
6. Local CI checks (`validate_metamodel_yaml.py`, `validate_json_schemas.py`, conformance suite, runtime suite) all pass.
7. PR opens against `origin/main`; CI on GitHub Actions shows green before user review.
8. The PR card moves from `In Progress` to `Review` on the board-23 kanban surface.
9. Companion Kanban card (`#389 CR-020 in dea-metamodel`) updates with the PR URL and CI status.

## 15. References

### 15.1 Inputs and authorities

- `technehub-labs/dea-metamodel/change-requests/CR-017-information-systems-domain-semantic-integration.md` (foundation CR; merged 2026-10-16 via PR #170, commit `3e00b35`)
- `technehub-labs/dea-metamodel/change-requests/CR-018-information-system-function.md` (kernel+specialization precedent; merged 2026-10-16 via PR #171, commit `0f16441`)
- `technehub-labs/dea-metamodel/change-requests/CR-019-information-system-component.md` (abstract kind + component hierarchy reconciliation; merged 2026-10-16 via PR #172, commit `5812cfb`)
- ADR-ISA-000 (foundation paper)
- CR-MM-PROC-01 (kernel+specialization template; Process / BusinessProcess)
- CR-016 + ADR-015 (kernel+specialization template; Capability / BusinessCapability)
- CR-MM-04 (authorship cardinal rule R1, R2)
- CR-MM-ECF-04 (entity-system cross-reference)
- CR-AR-FMWK-03 (architecture cross-reference)
- CR-012 (`dea-governance`; EGV-001..012 normative requirements)
- DEA-ID-000 (`dea-governance` foundation paper)

### 15.2 Companion Kanban surface

- Project 23 (DEAMMISE) at `/board/23`: card #389 (CR-020 programme), In Progress during authoring
- Companion umbrella carrier #384
- DRIFT-4 card #419 (InfrastructureComponent placement decision; parked for next slice)
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`

---

End of CR-020.
