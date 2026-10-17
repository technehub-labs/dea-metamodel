# CR-019: Information System Component -- abstract kind + component hierarchy reconciliation

| Field | Value |
|-------|-------|
| **CR** | CR-019 |
| **Title** | Information System Component abstract kind + component hierarchy reconciliation (D-2 disposition) |
| **Status** | Proposed (this PR) |
| **Layer** | Metamodel (Digital Profile) |
| **Programme** | Information Systems Semantic Architecture |
| **Architectural parent** | CR-017 (Information Systems Domain Semantic Integration and Relationship Architecture, merged 2026-10-16 via PR #170, commit `3e00b35`); CR-018 (Information System Function, merged 2026-10-16 via PR #171, commit `0f16441`) |
| **Companion to** | CR-MM-PROC-01 (kernel+specialization template); CR-016 (kernel+specialization template, ADR-015); CR-MM-04 (authorship cardinal rule R1, R2); CR-MM-ECF-04 (entity-system cross-reference); CR-AR-FMWK-03 (architecture cross-reference); ADR-0002 D3 (SolutionComponent abstract parent) |
| **Depends on** | CR-017; CR-018; CR-016 + ADR-015; CR-MM-04; `CR-012 (dea-governance)` + DEA-ID-000 (when accepted); CR-MM-ECF-04 |
| **Enables** | CR-020 (introduces `dea:InformationSystemService`); CR-021 (introduces `dea:IntegrationInterface`); CR-022 (closes artifact regeneration + conformance); CR-AR-FMWK-04; CR-IS-CAT-02 (renames `dea-catalog-application-components` to `dea-catalog-information-system-components`) |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-16 |

## 1. Executive Summary

This CR introduces `dea:InformationSystemComponent` as the new canonical Digital Profile abstract kind for "architectural constituent of an information system", per the **D-2** disposition decision ratified by the user on 2026-10-16 in Discord thread 1560566532973527130.

The D-2 disposition has two coupled outcomes:

1. The new abstract kind `dea:InformationSystemComponent` (L5, building_block L5-systems, profile dea:digital, `abstract: true`, `lifecycle: planned`) is introduced as the kind that the concrete `dea:ApplicationComponent` and `dea:IntegrationComponent` now specialise.
2. The legacy `dea:SolutionComponent` is reconciled: the registry entry's `abstract: false` declaration is corrected to `abstract: true`. The definition is updated to acknowledge the new abstract child kind `dea:InformationSystemComponent`. The `component_type` discriminator is retained on the concrete ApplicationComponent and IntegrationComponent entries for EGV-004 identity continuity and for catalog search/filter use cases that predate the abstract ISC introduction.

A separate decision: `dea:InfrastructureComponent` (DRIFT-4) remains a direct specialisation of `dea:SolutionComponent`, not a sub-kind of `dea:InformationSystemComponent`. Rationale: the IaC-managed resource class is broader than the information-system concern; a future L0 cloud-infrastructure resource may specialise InfrastructureComponent without itself being an information system. The infrastructure hosting role is captured via `dea:hosts` and `dea:depends-on` (existing relationships).

The implementation follows the same kernel+specialization template used by CR-MM-PROC-01 (`dea:Process / dea:BusinessProcess`), CR-016 (`dea:Capability / dea:BusinessCapability`), and CR-018 (`dea:Behavior / dea:InformationSystemFunction`).

## 2. Scope

### 2.1 In scope

1. The canonical metamodel definition of `dea:InformationSystemComponent` in `metamodel/dea-metamodel.yaml`.
2. The `dea:SolutionComponent.abstract` reconciliation: `false` -> `true`. Definition updated to acknowledge the new abstract child kind.
3. `dea:ApplicationComponent` and `dea:IntegrationComponent` definitions updated to specialise `dea:InformationSystemComponent` (with the `component_type` discriminator retained on the concrete entries for EGV-004 identity continuity).
4. `dea:InfrastructureComponent` placement decision recorded (DRIFT-4): direct child of `dea:SolutionComponent`; not under `dea:InformationSystemComponent`.
5. Five relationship endpoint extensions in `metamodel/dea-metamodel.yaml`:
   - `dea:specializes.source.types` add `dea:InformationSystemComponent`, `dea:ApplicationComponent`, `dea:IntegrationComponent`.
   - `dea:realizes.source.types` add `dea:InformationSystemComponent`.
   - `dea:depends-on.source.types` and `target.types` add `dea:InformationSystemComponent`.
   - `dea:composes.source.types` and `target.types` add `dea:InformationSystemComponent`.
   - `dea:executes.source.types` add `dea:InformationSystemComponent` (an ISC can execute an ISF).
   - `dea:provides.source.types` add `dea:InformationSystemComponent` (reserved for CR-020 service provision extension; the target list is widened in CR-020 to include `dea:InformationSystemService`).
   - `dea:exposes.source.types` add `dea:InformationSystemComponent` (reserved for CR-021 interface exposure extension; the target list is widened in CR-021 to include `dea:IntegrationInterface`).
6. Digital Profile membership: `metamodel/profiles/digital/profile.yaml` adds `dea:InformationSystemComponent` and annotates `dea:IntegrationComponent` with a comment about the new specialisation path.
7. JSON Schema for the new entity: `schemas/entities/information-system-component.json` (new). The schema intentionally does NOT carry inline relationship-state properties (`executes`, `depends_on`, `provides`, `exposes`) because the canonical relationship vocabulary is the source of truth for those edges; CR-3 forbids entity records from duplicating relationship state. The pattern is `application-component.json` and `integration-component.json` (no inline relationship state).
8. Regeneration of derived artefacts via the established generators.
9. The CR-019 document (this file).
10. `change-requests/README.md` row for CR-019.
11. `docs/information-systems-semantic-architecture.md` extension with the implemented entity state.

### 2.2 Out of scope

1. Migration of the `dea-catalog-application-components` GitHub repository. Owned by `CR-IS-CAT-02` after CR-022 closure. The repository keeps its identity and its `dea:entity-application-component` namespace through the migration window.
2. `artifacts.pydantic_model`, `artifacts.sqlite_table`, `artifacts.ts_interface` paths for the new entity. `null` in this CR. `CR-022` (Metamodel Artifact and Conformance Closure) regenerates them.
3. Cross-extension of `dea:provides.target.types` to include `dea:InformationSystemService` (CR-020). Reserved; the source side is updated here.
4. Cross-extension of `dea:exposes.target.types` to include `dea:IntegrationInterface` (CR-021). Reserved; the source side is updated here.
5. OpenDEAM identifier mapping. Owned by `CR-AR-FMWK-04`.
6. Governance portfolio registration. Owned by `CR-013 (dea-governance)`.
7. Any change to the Core anchor `dea:SolutionComponent` beyond the `abstract` boolean reconciliation and definition update; the legacy catalogue `dea-catalog-digital-business-service-factory` and the legacy L3 layer attribution stay untouched (CR-019 does not change the legacy catalog's identity).

## 3. Problem Statement and D-2 Disposition

The CR-017 foundation document flagged that `dea:SolutionComponent`'s definition describes an "abstract parent of ApplicationComponent, InfrastructureComponent, IntegrationComponent" but its registry entry declared `abstract: false`. This is a registered inconsistency that blocks any sub-specialisation that treats `dea:SolutionComponent` as abstract.

CR-017 offered D-2 as one of the six design decisions: "set `dea:SolutionComponent.abstract: true`; remediation owned by CR-019".

The user ratified D-2 on 2026-10-16. Implementation in CR-019 follows the disposition: reconcile the abstract boolean, introduce the new abstract kind `dea:InformationSystemComponent` for the Information Systems sub-tree, leave the broader component hierarchy (`dea:ApplicationComponent`, `dea:IntegrationComponent`, `dea:InfrastructureComponent`) re-anchored to the corrected abstract `dea:SolutionComponent` and, where appropriate, the new `dea:InformationSystemComponent`.

The `component_type` discriminator (which was the only mechanism previously used to distinguish APC / IFC / IGC under the "discriminated union" interpretation) is retained on the concrete entries for EGV-004 identity continuity. New model authoring may specialise `dea:InformationSystemComponent` directly without supplying a `component_type` value; the discriminator becomes a catalog-internal search/filter field rather than the primary type-hierarchy mechanism.

## 4. Entity Definitions (Normative)

### 4.1 `dea:InformationSystemComponent` (new abstract kind)

```yaml
- id: dea:InformationSystemComponent
  name: Information System Component
  legacy_ids:
  - dea:entity-information-system-component
  definition: An identifiable architectural constituent of an information system that encapsulates a
    defined responsibility, structure or execution boundary and participates in the composition or
    operation of that information system. Abstract (D-2 disposition 2026-10-16; CR-019).
  layer: L5
  dimension: null
  building_block: L5-systems
  abstract: true
  status: normative
  lifecycle: planned
  class_alias: ISC
  catalog_repo: dea-catalog-application-components
  artifacts:
    json_schema: schemas/entities/information-system-component.json
    sqlite_table: null              # regenerated by CR-022
    pydantic_model: null           # regenerated by CR-022
    ts_interface: null             # regenerated by CR-022
  membership:
    kind: profile
    profile: dea:digital
```

### 4.2 `dea:SolutionComponent` (abstract reconciliation)

```yaml
- id: dea:SolutionComponent
  name: Solution Component
  legacy_ids:
  - dea:entity-solution-component
  - SolutionComponent
  definition: Abstract parent of ApplicationComponent, InfrastructureComponent, IntegrationComponent, and
    the new InformationSystemComponent (introduced in CR-019; the abstract kind that ApplicationComponent and
    IntegrationComponent specialise). Concrete subclasses are allocated to L5. (ADR-0002 D3; abstract status
    reconciled in CR-019; D-2 disposition 2026-10-16.)
  layer: L3
  dimension: null
  building_block: L3-service-offerings
  abstract: true   # was: false. Reconciled per D-2 disposition 2026-10-16.
  status: normative
  lifecycle: existing
  class_alias: SC
  catalog_repo: dea-catalog-digital-business-service-factory
  artifacts:
    json_schema: schemas/entities/solution-component.json
    sqlite_table: solution_components
    pydantic_model: pydantic/solution_component.py
    ts_interface: typescript/src/interfaces.ts
  membership:
    kind: profile
    profile: dea:digital
```

### 4.3 `dea:ApplicationComponent` (now specialises ISC)

```yaml
- id: dea:ApplicationComponent
  name: Application Component
  legacy_ids:
  - dea:entity-application-component
  - ApplicationComponent
  definition: A deployable unit of an application system. Specialises dea:InformationSystemComponent (CR-019;
    the abstract Digital Profile kind introduced for the Information Systems programme; D-2 disposition).
    Component_type discriminator remains 'application' for catalog instances; EGV-004 identity continuity.
  layer: L5
  ...
```

### 4.4 `dea:IntegrationComponent` (now specialises ISC)

Same pattern: definition updated to record the ISC specialisation, `component_type` discriminator retained, legacy_ids preserved, EGV-004 identity continuity.

### 4.5 `dea:InfrastructureComponent` (placement decision: stays under SolutionComponent)

```yaml
- id: dea:InfrastructureComponent
  name: Infrastructure Component
  legacy_ids:
  - dea:entity-infrastructure-component
  - InfrastructureComponent
  definition: An IaC-managed resource that hosts solution components. Specialises dea:SolutionComponent with
    component_type='infrastructure'. Per CR-019 placement decision (DRIFT-4): InfrastructureComponent remains a
    direct specialisation of dea:SolutionComponent rather than a sub-kind of dea:InformationSystemComponent.
    Rationale: the IaC-managed resource class is broader than the information-system concern; a future L0
    cloud-infrastructure resource may specialise InfrastructureComponent without itself being an information
    system.
  layer: L5
  ...
  membership:
    kind: profile
    profile: dea:technology
```

The infrastructure hosting role is captured via the existing `dea:hosts` relationship and via `dea:depends-on` (an ApplicationComponent or InformationSystemComponent depends on an InfrastructureComponent to host it).

## 5. Relationship Endpoint Extensions

| Source | Relationship | Target | Status in CR-019 |
|---|---|---|---|
| `dea:InformationSystemComponent` | `dea:specializes` | `dea:SolutionComponent` | source added; the parent relationship exists; CR-019 makes ISC eligible to be a specializes source/target |
| `dea:ApplicationComponent` | `dea:specializes` | `dea:InformationSystemComponent` | source added; new specialisation path; legacy `SubClass of SolutionComponent` wording preserved in the legacy_id's link note |
| `dea:IntegrationComponent` | `dea:specializes` | `dea:InformationSystemComponent` | source added; new specialisation path |
| `dea:ApplicationComponent` | `dea:executes` | `dea:InformationSystemFunction` | already permitted (CR-018 added ISF to target) |
| `dea:InformationSystemComponent` | `dea:executes` | `dea:InformationSystemFunction` | source added; new target eligibility |
| `dea:InformationSystemComponent` | `dea:composes` | `dea:InformationSystemComponent` | source and target added; composition across ISCs is now first-class |
| `dea:InformationSystemComponent` | `dea:depends-on` | `dea:InformationSystemComponent` | source and target added; dependency across ISCs is now first-class |
| `dea:ApplicationComponent` | `dea:depends-on` | `dea:InformationSystemComponent` | target added; an APC may depend on a hosting ISC |
| `dea:InformationSystemComponent` | `dea:provides` | (deferred to CR-020) | source added; target extension to `dea:InformationSystemService` is owned by CR-020 |
| `dea:InformationSystemComponent` | `dea:exposes` | (deferred to CR-021) | source added; target extension to `dea:IntegrationInterface` is owned by CR-021 |

## 6. Digital Profile Registration

```yaml
profile:
  id: dea:digital
  entities:
  - dea:InformationSystemComponent    # CR-019; abstract kind
  - dea:ApplicationComponent         # concrete specialisation of ISC
  - dea:IntegrationComponent         # concrete specialisation of ISC
  - dea:InformationSystemFunction
  - dea:SolutionComponent            # abstract parent (D-2 reconciled)
  - dea:SystemFunction               # DEPRECATED (CR-018)
  ...
```

## 7. JSON Schema

`schemas/entities/information-system-component.json` (new). The schema's `required` list is `[id, name, type, version]`, mirroring the other entity schemas. The schema intentionally does NOT include inline relationship-state properties (`executes`, `depends_on`, `provides`, `exposes`); the canonical relationship vocabulary is the source of truth for those edges (per CR-3). The pattern matches `application-component.json` and `integration-component.json`.

## 8. Generated Artefacts

Per D-6 disposition:

| Artefact | Generator | Status |
|---|---|---|
| `metamodel/registry/entities.yaml` | `.github/scripts/generate_registry.py` | regenerated; `dea:InformationSystemComponent` projected at line 554 (with `abstract: true`) |
| `metamodel/registry/relationships.yaml` | `.github/scripts/generate_registry.py` | regenerated; endpoint extensions applied |
| `specification/semantic-inventory.yaml` | `.github/scripts/generate_specification.py` | regenerated; `inventory(149e/104r)` |
| `specification/vocabulary.yaml` | `.github/scripts/generate_specification.py` | regenerated |
| `specification/catalogues/entities.md` | `.github/scripts/generate_specification.py` | regenerated |
| `pydantic/information_system_component.py` | `.github/scripts/generate_pydantic.py` | deferred to CR-022 (`artifacts.pydantic_model` is null) |
| `viewer/entity-graph.json` | `.github/scripts/generate_entity_graph.py` | owned by `CR-AR-FMWK-04` |
| `ttl/dea-metamodel-ontology.ttl` | TTL generator (existence unconfirmed) | deferred to CR-022 |
| `sqlite/dea-metamodel.db` | SQL `schema.sql` | deferred to CR-022 |

## 9. Conformance and Validation

Local CI verification:

- `python3 .github/scripts/validate_metamodel_yaml.py` PASS (legacy stub).
- `python3 .github/scripts/validate_json_schemas.py` PASS (125 JSON schemas valid).
- `python3 .github/scripts/generate_registry.py` PASS (regenerated; 149 entities / 104 relationships).
- `python3 .github/scripts/generate_specification.py` PASS (regenerated; `inventory(149e/104r)`, vocabulary, 2 catalogues).
- `python3 -m pytest tests/conformance/` PASS (133 tests).
- `python3 -m pytest tests/runtime/` PASS (290 tests).

## 10. Cross-Repository Impact

| Repository | Required alignment |
|---|---|
| `technehub-labs/dea-architecture-framework` | `CR-AR-FMWK-04` adds `dea:entity-information-system-component` to `model/opendeam-model.yaml` entities[] with the canonical metamodel relationship IDs as architectural edges |
| `technehub-labs/dea-governance` | `CR-013 (dea-governance)` registers the new entity in the catalog portfolio map; the rename of `dea-catalog-application-components` to `dea-catalog-information-system-components` is ratified |
| `technehub-labs/dea-catalog-application-components` | `CR-IS-CAT-02` extends and renames to `dea-catalog-information-system-components`; preserves the `dea:entity-application-component` namespace; existing records migrate via `legacy_ids` linkage |
| Other catalogs that reference `dea:ApplicationComponent` or `dea:IntegrationComponent` | No mandatory migration in this CR; legacy references continue to resolve via EGV-004 |

## 11. Migration and Compatibility

This is a **minor** version impact: the abstract reconciliation is backward-compatible (any concrete entry under `dea:SolutionComponent` retains its identity); the new abstract kind is additive.

- Existing models referencing `dea:SolutionComponent` continue to validate against the normative source (the `abstract: true` boolean is a documentation refinement, not a structural change; per EGV-004 the entity identity is preserved).
- Existing models referencing `dea:ApplicationComponent` or `dea:IntegrationComponent` continue to resolve under the same canonical identifier. The definition update notes the new specialisation path but does not invalidate the concrete entries.
- New models MAY specialise `dea:InformationSystemComponent` directly without supplying a `component_type` value; the discriminator becomes a catalog-internal search/filter field rather than the primary type-hierarchy mechanism.

## 12. DRIFT-4: Infrastructure Component Placement Decision

Recorded as a separate drift card on board 23 (kanban project 23, DEAMMISE):

- Question: does `dea:InfrastructureComponent` specialise `dea:InformationSystemComponent` or remain a direct child of `dea:SolutionComponent`?
- Decision (CR-019 §4.5): direct child of `dea:SolutionComponent`.
- Rationale: the IaC-managed resource class is broader than the information-system concern; a future L0 cloud-infrastructure resource may specialise InfrastructureComponent without itself being an information system. The infrastructure hosting role is captured via the existing `dea:hosts` relationship and via `dea:depends-on`.
- This decision is documented in the InfrastructureComponent definition's body (canonical source) and in this CR; a future `dea-catalog-infrastructure-components` would be a natural follow-on if the L0 cloud-infrastructure resource class gains its own profile.

## 13. Acceptance Criteria

- [ ] `dea:InformationSystemComponent` is registered as a Digital Profile abstract kind in the normative source.
- [ ] `dea:SolutionComponent.abstract` is `true` (reconciled per D-2).
- [ ] `dea:ApplicationComponent` and `dea:IntegrationComponent` definitions note the new specialisation path under `dea:InformationSystemComponent`.
- [ ] `dea:InfrastructureComponent` placement decision is recorded (DRIFT-4) and the definition body explains the rationale.
- [ ] Five relationship endpoint extensions are applied.
- [ ] Digital Profile membership registers the new abstract kind.
- [ ] JSON Schema is created and passes `validate_json_schemas.py`; it intentionally does NOT include inline relationship-state properties per CR-3.
- [ ] All four generators regenerate consistent artefacts.
- [ ] Local CI conformance and runtime test suites pass.
- [ ] Cardinal author rule (CR-MM-04 R1) is satisfied: `Author: Emmanuel A. Otchere`.
- [ ] Cardinal author rule (CR-MM-04 R2) is satisfied: this PR is one logical change (abstract kind + component hierarchy + 5 relationship extensions + generated artefacts + docs); no bundle content from CR-020 / CR-021.
- [ ] D-004 / D-005 / Standardization-body embargo clean.

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Existing catalog records lose the `component_type` discriminator | EGV-004 identity continuity; discriminator is preserved on the concrete APC / IFC entries as a non-canonical annotation; new ISC records may omit it |
| `dea:SolutionComponent.abstract` flip breaks existing catalog instances | EGV-004 identity continuity; the registry entry is updated but no record is reclassified; the legacy `dea-catalog-digital-business-service-factory` keeps its identity |
| Infrastructure Component re-anchoring causes downstream consumer breakage | DRIFT-4 records the explicit decision; InfrastructureComponent is NOT moved; existing `dea:entity-infrastructure-component` references continue to resolve after regeneration |
| Author confusion (CR-MM-04 author header) | R1 cardinal rule enforced by `validate-authorship.yml` |
| Cross-cite drift with `dea:InformationSystemFunction` (CR-018) | D-1 disposition's ISF and D-2 disposition's ISC are paired; cross-references documented in this CR and in CR-020 / CR-021 |

## 15. Completion Definition

CR-019 is complete when:

1. `dea:InformationSystemComponent` is registered in the normative source with the abstract kind properties.
2. `dea:SolutionComponent.abstract` is reconciled to `true` with definition update.
3. The three concrete component entities' definitions note the new specialisation path; the `component_type` discriminator is preserved on the concrete entries.
4. The five relationship endpoint extensions are applied.
5. Digital Profile registers the new abstract kind.
6. The JSON Schema is committed and validates; CR-3 conformance is preserved (no inline relationship-state properties).
7. The four deterministic generators regenerate consistent artefacts.
8. Local CI checks (`validate_metamodel_yaml.py`, `validate_json_schemas.py`, conformance suite, runtime suite) all pass.
9. PR opens against `origin/main`; CI on GitHub Actions shows green before user review.
10. The PR card moves from `In Progress` to `Review` on the board-23 kanban surface.
11. Companion Kanban card (`#388 CR-019 in dea-metamodel`) updates with the PR URL and CI status.

## 16. References

### 16.1 Inputs and authorities

- `technehub-labs/dea-metamodel/change-requests/CR-017-information-systems-domain-semantic-integration.md` (foundation CR; merged 2026-10-16 via PR #170, commit `3e00b35`)
- `technehub-labs/dea-metamodel/change-requests/CR-018-information-system-function.md` (kernel+specialization precedent; merged 2026-10-16 via PR #171, commit `0f16441`)
- ADR-ISA-000 (foundation paper)
- CR-MM-PROC-01 (kernel+specialization template; Process / BusinessProcess)
- CR-016 + ADR-015 (kernel+specialization template; Capability / BusinessCapability)
- CR-MM-04 (authorship cardinal rule R1, R2)
- CR-MM-ECF-04 (entity-system cross-reference)
- CR-AR-FMWK-03 (architecture cross-reference)
- ADR-0002 D3 (SolutionComponent abstract parent precedent)
- CR-012 (`dea-governance`; EGV-001..012 normative requirements)
- DEA-ID-000 (`dea-governance` foundation paper)

### 16.2 Companion Kanban surface

- Project 23 (DEAMMISE) at `/board/23`: card #388 (CR-019 programme), In Progress during authoring
- Companion umbrella carrier #384
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`

---

End of CR-019.
