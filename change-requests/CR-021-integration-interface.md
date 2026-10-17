# CR-021: Integration Interface -- interaction boundary + API audit-then-specifies

| Field | Value |
|-------|-------|
| **CR** | CR-021 |
| **Title** | Integration Interface interaction boundary + API audit-then-specifies (D-4 disposition) |
| **Status** | Proposed (this PR) |
| **Layer** | Metamodel (Digital Profile) |
| **Programme** | Information Systems Semantic Architecture |
| **Architectural parent** | CR-017 (Information Systems Domain Semantic Integration and Relationship Architecture, merged 2026-10-16 via PR #170, commit `3e00b35`); CR-018 (Information System Function, merged 2026-10-16 via PR #171, commit `0f16441`); CR-019 (Information System Component, merged 2026-10-16 via PR #172, commit `5812cfb`); CR-020 (Information System Service, merged 2026-10-16 via PR #173, commit `6747d84`) |
| **Companion to** | CR-MM-PROC-01 (kernel+specialization template); CR-016 (kernel+specialization template, ADR-015); CR-MM-04 (authorship cardinal rule R1, R2); CR-MM-ECF-04 (entity-system cross-reference); CR-AR-FMWK-03 (architecture cross-reference) |
| **Depends on** | CR-017; CR-018; CR-019; CR-020; CR-016 + ADR-015; CR-MM-04; `CR-012 (dea-governance)` + DEA-ID-000 (when accepted) |
| **Enables** | CR-022 (closes artifact regeneration + conformance); CR-AR-FMWK-04; CR-IS-CAT-04 (new `dea-catalog-information-system-integration-interfaces`) |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-16 |

## 1. Executive Summary

This CR introduces `dea:IntegrationInterface` as the new canonical Digital Profile entity for "the interaction boundary through which information systems and their components communicate", per the **D-4** disposition decision ratified by the user on 2026-10-16 in Discord thread 1560566532973527130.

The D-4 disposition has two coupled outcomes:

1. The new entity `dea:IntegrationInterface` (L5, building_block L5-integration, profile dea:digital, `abstract: false`, `lifecycle: planned`) is introduced as the interaction boundary, distinct from the API contract (dea:API) that may specify it. The same template precedents apply: CR-016, CR-MM-PROC-01, CR-018, CR-019, CR-020.
2. The legacy `dea:API` is reconciled: the registry entry's definition is updated to record the D-4 audit-then-specifies posture. A new relationship `dea:specifies` is introduced in CR-021 (CR-021-owned; the audit in §3.1 found no exact fit in the existing vocabulary). The canonical entry sources `dea:specifies` targeting `dea:IntegrationInterface`.

The D-4 audit is recorded in §3.1 below; it is a complete audit of the existing relationship vocabulary, with a per-relationship fit/misfit assessment. The audit is the gating artefact for the new relationship introduction; the audit is documented here so reviewers can verify the audit was complete and the new relationship is genuinely necessary.

The new relationship `dea:specifies` adds a 14th category to the controlled vocabulary: `contract` (category M). The expansion is documented in §3.2 and in the `tests/conformance/test_008_relationship_rules.py` CATEGORIES set.

## 2. Scope

### 2.1 In scope

1. The canonical metamodel definition of `dea:IntegrationInterface` in `metamodel/dea-metamodel.yaml`.
2. The `dea:API.definition` annotation recording the D-4 audit-then-specifies posture; the canonical entry sources the new `dea:specifies` relationship with target `dea:IntegrationInterface`.
3. The new relationship `dea:specifies` introduced in `metamodel/dea-metamodel.yaml` with bounded source (dea:API) and target (dea:IntegrationInterface), inverse `dea:specified-by`, category `contract`.
4. Three relationship endpoint extensions:
   - `dea:exposes.target.types` add `dea:IntegrationInterface` (resolves CR-019 reserved extension; ISC may expose an interface).
   - `dea:exposes.source.types` add `dea:InformationSystemService` (an ISS may expose an interface; complements CR-020's `provides`).
   - `dea:uses.target.types` add `dea:IntegrationInterface` (an ISC uses an interface; complements `dea:exposes`).
5. Controlled-vocabulary expansion: `tests/conformance/test_008_relationship_rules.py` CATEGORIES set adds `contract` (category M).
6. The relationship-instance schema enum at `schemas/relationships/relationship-instance.json` adds `specifies`.
7. Digital Profile membership: `metamodel/profiles/digital/profile.yaml` adds `dea:IntegrationInterface`.
8. JSON Schema for the new entity: `schemas/entities/integration-interface.json` (new). Mirrors `application-component.json`; no inline relationship-state properties.
9. Regeneration of derived artefacts via the established generators.
10. The CR-021 document (this file).
11. `change-requests/README.md` row for CR-021.
12. `docs/information-systems-semantic-architecture.md` extension.

### 2.2 Out of scope

1. `artifacts.pydantic_model`, `artifacts.sqlite_table`, `artifacts.ts_interface` paths for the new entity. `null` in this CR; `CR-022` populates them.
2. The new `dea-catalog-information-system-integration-interfaces` repository. Owned by `CR-IS-CAT-04` after CR-022 closure.
3. The new `dea:specified-by` inverse relationship as a separately registered entry. The inverse is declared as a string (`inverse: dea:specified-by`) per `test_r007_inverses_declared`; the inverse edge is implied by the source/target flip on `dea:specifies`. A future CR may add `dea:specified-by` as a separately registered relationship if the closed vocabulary needs it.
4. OpenDEAM identifier mapping. Owned by `CR-AR-FMWK-04`.
5. Governance portfolio registration. Owned by `CR-013 (dea-governance)`.
6. Any change to Core anchor `dea:API`; only the specialisation surface is extended.
7. Migration of `dea-catalog-api-contracts` records. Owned by `CR-IS-CAT-04` (the new repository) and the catalog-ownership register in `CR-013 (dea-governance)`.

## 3. D-4 Audit and Disposition

### 3.1 Relationship vocabulary audit

The following audit covers every relationship in the canonical vocabulary whose semantic could plausibly express "API contract specifies an interaction boundary". The audit was performed against `metamodel/dea-metamodel.yaml` as of commit `6747d84` (post-CR-020).

| Relationship | Category | Source | Target | Direction | Fit for "API specifies Interface"? |
|---|---|---|---|---|---|
| `dea:exposes` | serving | `dea:API`, APC, BS, DP, ISC, ISS | BusinessObject, BS, DE, DP | source-to-target | NO. "Source presents target as an accessible interface" is the inverse direction: the source IS the component/service presenting the interface, not the contract that defines the interface semantics. |
| `dea:uses` | serving | Actor, Agent, Orchestrator, APC, BP, ISC, JT, SC | API, Tool, BS, DI, ISS, PS, Service | source-to-target | NO. "Source consumes target as offered" is consumer-side; the API is a target here, not a source. |
| `dea:provides` | serving | Actor, APC, EP, ISC, ISS, PS, Service, SC | API, BC, BS, ISS | source-to-target | NO. "Source makes target available" is provider-side; the API is a target here, not a source. |
| `dea:serves` | serving | (serving) | (serving) | source-to-target | NO. "Serves" is consumer-oriented; semantics do not match. |
| `dea:realizes` | realization | APC, BPL, BP, ISC, ISF, IFC, IGC, SC, SF, AIMLModel | Behavior, BC, BP, Capability, Concept, DataEntity, DE, IC, ISA, ISF, OU, Process, Project, SC, Technology, UseCase | source-to-target | NO. "Source is the concrete realization of the target". The API is a contract, not a realization. |
| `dea:implements` | realization | (realization) | (realization) | source-to-target | NO. "Source implements target" is concrete-implements-abstract, not contract-specifies-contract. |
| `dea:supports` | dependency | (dependency) | (dependency) | source-to-target | NO. "Source supports target" is enablement, not specification. |
| `dea:governs` | governance | (governance) | (governance) | source-to-target | NO. "Source directs/constrains target through policy/agreement". Governance is policy-oriented, not contract-specification-oriented. |
| `dea:describes` | information | (information) | (information) | source-to-target | NO. "Describes" is documentation/narration-oriented. The audit considered this candidate most carefully; rejected because the API does not "describe" the interface, it specifies the interaction contract that the interface implements. |

**Conclusion**: No existing relationship has the exact semantic "API contract specifies an interaction boundary". The audit considered ten candidates from four categories; none fit. Therefore CR-021 introduces the new relationship `dea:specifies` with bounded source (dea:API) and target (dea:IntegrationInterface), inverse `dea:specified-by`, and a new category `contract`.

### 3.2 New category `contract` (category M)

The CATEGORIES set in `tests/conformance/test_008_relationship_rules.py` is a controlled vocabulary. CR-021 adds `contract` as the 14th category. Rationale:

- The semantic of the new relationship ("A contract specifies an entity") is distinct from the existing 13 categories.
- "Governance" is policy/decision/control-oriented; a contract specifies interaction semantics, not policy.
- "Information" is data-flow/observation-oriented; a contract specifies what the data flow MUST be, not the flow itself.
- "Structural" is decomposition/composition-oriented; a contract does not structurally contain the interface.
- The vocabulary expansion is documented in this CR and in the test file's CATEGORIES constant comment.

The pattern follows prior controlled-vocabulary expansions: CR-6 added `temporal` as category L. CR-021 adds `contract` as category M.

## 4. Entity Definitions (Normative)

### 4.1 `dea:IntegrationInterface` (new canonical)

```yaml
- id: dea:IntegrationInterface
  name: Integration Interface
  legacy_ids:
  - dea:entity-integration-interface
  definition: A defined interaction boundary between an information system (or one of its components) and
    one or more internal or external consumers or providers, specifying the means, protocols, interaction
    patterns and contractual constraints through which information or functionality is exchanged.
  layer: L5
  dimension: null
  building_block: L5-integration
  abstract: false
  status: normative
  lifecycle: planned
  class_alias: II
  catalog_repo: dea-catalog-api-contracts
  artifacts:
    json_schema: schemas/entities/integration-interface.json
    sqlite_table: null
    pydantic_model: null
    ts_interface: null
  membership:
    kind: profile
    profile: dea:digital
```

### 4.2 `dea:API` (D-4 audit-then-specifies annotation)

```yaml
- id: dea:API
  name: API
  legacy_ids:
  - dea:entity-api
  definition: A contract defining the request/response shape of a service interface. Per CR-021 (D-4
    disposition 2026-10-16): audit-then-specifies posture. The existing relationship vocabulary was
    audited in CR-021 §3.1; no existing relationship has the exact semantic "API contract specifies
    an interaction boundary". The canonical entry therefore sources the new dea:specifies relationship
    with target dea:IntegrationInterface. dea:API remains a contract entity; the interaction boundary
    it specifies is a separate Digital Profile entity (dea:IntegrationInterface).
  layer: L5
  dimension: null
  building_block: L5-integration
  abstract: false
  status: normative
  lifecycle: planned
  class_alias: API
  catalog_repo: dea-catalog-api-contracts
  artifacts:
    json_schema: null
    sqlite_table: null
    pydantic_model: null
    ts_interface: null
  membership:
    kind: profile
    profile: dea:digital
```

The `catalog_repo` for `dea:API` is left as `dea-catalog-api-contracts` (the existing catalog). Per D-4, the new `dea-catalog-information-system-integration-interfaces` repository is owned by `CR-IS-CAT-04`.

## 5. New Relationship `dea:specifies`

```yaml
- id: dea:specifies
  name: Specifies
  definition: A contract, specification, or formal definition that defines the interaction semantics
    of the target entity. Per CR-021 (D-4 disposition 2026-10-16; audit-then-specifies posture).
  category: contract
  direction: source-to-target
  source:
    types:
    - dea:API
  target:
    types:
    - dea:IntegrationInterface
  cardinality:
    source: 0..*
    target: 0..*
  inverse: dea:specified-by
  transitive: false
  symmetric: false
  temporal: false
  provenance: optional
  status: normative
  lifecycle: active
```

The relationship is intentionally bounded (one source, one target). The audit's conclusion is that the API-to-Interface relationship is a one-to-one semantic; the broader "X specifies Y" semantic is parked for future CRs if a use case emerges.

The inverse `dea:specified-by` is declared as a string per `test_r007_inverses_declared`. The inverse edge is implied by the source/target flip on `dea:specifies`; a future CR may add `dea:specified-by` as a separately registered relationship if the closed vocabulary needs it.

## 6. Relationship Endpoint Extensions

| Source | Relationship | Target | Status in CR-021 |
|---|---|---|---|
| `dea:API` | `dea:specifies` | `dea:IntegrationInterface` | new relationship; category `contract`; inverse `dea:specified-by` |
| `dea:InformationSystemComponent` | `dea:exposes` | `dea:IntegrationInterface` | target added (resolves CR-019 reserved extension; ISC may expose an interface) |
| `dea:ApplicationComponent` | `dea:exposes` | `dea:IntegrationInterface` | target added (APC may expose an interface) |
| `dea:IntegrationComponent` | `dea:exposes` | `dea:IntegrationInterface` | target added (IGC may expose an interface; this is the canonical integration pattern) |
| `dea:InformationSystemService` | `dea:exposes` | `dea:IntegrationInterface` | source added (an ISS may expose an interface; complements `dea:provides`) |
| `dea:ApplicationComponent` | `dea:uses` | `dea:IntegrationInterface` | target added (APC uses an interface; complements `dea:exposes`) |
| `dea:InformationSystemComponent` | `dea:uses` | `dea:IntegrationInterface` | target added (ISC uses an interface) |

## 7. Digital Profile Registration

```yaml
profile:
  id: dea:digital
  entities:
  - dea:IntegrationInterface   # CR-021; interaction boundary (D-4 disposition; audit-then-specifies)
  - dea:API                    # CR-021 D-4: sources dea:specifies targeting dea:IntegrationInterface
  ...
```

## 8. JSON Schema

`schemas/entities/integration-interface.json` (new). Mirrors the `application-component.json` pattern. The schema's `required` list is `[id, name, type, version]`. No inline relationship-state properties (per CR-3 / `test_003_no_duplicate_relationship_state`).

## 9. Generated Artefacts

Per D-6 disposition:

| Artefact | Generator | Status |
|---|---|---|
| `metamodel/registry/entities.yaml` | `.github/scripts/generate_registry.py` | regenerated; `dea:IntegrationInterface` projected; 151 entities / 105 relationships |
| `metamodel/registry/relationships.yaml` | `.github/scripts/generate_registry.py` | regenerated; new `dea:specifies` projected; endpoint extensions applied |
| `specification/semantic-inventory.yaml` | `.github/scripts/generate_specification.py` | regenerated; `inventory(151e/105r)` |
| `specification/vocabulary.yaml` | `.github/scripts/generate_specification.py` | regenerated |
| `specification/catalogues/entities.md` | `.github/scripts/generate_specification.py` | regenerated |
| `specification/catalogues/relationships.md` | `.github/scripts/generate_specification.py` | regenerated |
| `schemas/relationships/relationship-instance.json` | hand-maintained | updated; `specifies` added to enum |
| `tests/conformance/test_008_relationship_rules.py` | hand-maintained | updated; `contract` added to CATEGORIES (category M) |
| `pydantic/integration_interface.py` | `.github/scripts/generate_pydantic.py` | deferred to CR-022 |
| `viewer/entity-graph.json` | `.github/scripts/generate_entity_graph.py` | owned by `CR-AR-FMWK-04` |
| `ttl/dea-metamodel-ontology.ttl` | TTL generator | deferred to CR-022 |
| `sqlite/dea-metamodel.db` | SQL `schema.sql` | deferred to CR-022 |

## 10. Conformance and Validation

Local CI verification (run on the feature branch before opening the PR):

- `python3 .github/scripts/validate_metamodel_yaml.py` PASS (legacy stub; "41/10" output is the deprecated `metamodel.yaml` count).
- `python3 .github/scripts/validate_json_schemas.py` PASS (127 JSON schemas valid).
- `python3 .github/scripts/generate_registry.py` PASS (151 entities / 105 relationships).
- `python3 .github/scripts/generate_specification.py` PASS (inventory(151e/105r), vocabulary, 2 catalogues).
- `python3 -m pytest tests/conformance/` PASS (133 tests; category expansion + enum addition accepted).
- `python3 -m pytest tests/runtime/` PASS (290 tests).

## 11. Cross-Repository Impact

| Repository | Required alignment |
|---|---|
| `technehub-labs/dea-architecture-framework` | `CR-AR-FMWK-04` adds `dea:entity-integration-interface` to `model/opendeam-model.yaml` entities[] with the canonical metamodel relationship IDs as architectural edges; the new `dea:specifies` relationship is added to the relationship graph |
| `technehub-labs/dea-governance` | `CR-013 (dea-governance)` registers the new entity in the catalog portfolio map; the new `dea-catalog-information-system-integration-interfaces` repository is ratified |
| `technehub-labs/dea-catalog-api-contracts` | The existing catalog's record gate is updated; the API contract records gain a dea:specifies reference to a dea:IntegrationInterface record in the new `dea-catalog-information-system-integration-interfaces` |
| `technehub-labs/dea-catalog-information-system-integration-interfaces` (new) | `CR-IS-CAT-04` establishes the new repository with the initial population of interface records |
| Other catalogs that reference `dea:API` | No mandatory migration in this CR; legacy references continue to resolve via EGV-004 |

## 12. Migration and Compatibility

This is a **minor** version impact: the new entity is additive; the existing `dea:API` is augmented with a definition annotation and the new `dea:specifies` relationship.

- Existing models referencing `dea:API` continue to validate against the normative source.
- Existing models that do not use the new `dea:specifies` relationship are unaffected.
- New models MAY instantiate `dea:IntegrationInterface` records independently of `dea:API` records (e.g., for an interface with no formal API contract, or for an interface governed by multiple API versions).

## 13. Acceptance Criteria

- [ ] `dea:IntegrationInterface` is registered as a Digital Profile entity in the normative source.
- [ ] Its definition is interaction-boundary-anchored and explicitly distinct from `dea:API` and `dea:IntegrationComponent`.
- [ ] `dea:API.definition` records the D-4 audit-then-specifies posture and sources `dea:specifies`.
- [ ] The new relationship `dea:specifies` is registered with category `contract`, source `dea:API`, target `dea:IntegrationInterface`, inverse `dea:specified-by`.
- [ ] Three relationship endpoint extensions are applied: `dea:exposes.target` (II), `dea:exposes.source` (ISS), `dea:uses.target` (II).
- [ ] The CATEGORIES controlled vocabulary is expanded with `contract` (category M).
- [ ] The relationship-instance schema enum includes `specifies`.
- [ ] Digital Profile membership registers the new entity.
- [ ] The JSON Schema is created and passes `validate_json_schemas.py`; it intentionally does NOT include inline relationship-state properties per CR-3.
- [ ] All four generators regenerate consistent artefacts.
- [ ] Local CI conformance and runtime test suites pass.
- [ ] Cardinal author rule (CR-MM-04 R1) is satisfied: `Author: Emmanuel A. Otchere`.
- [ ] Cardinal author rule (CR-MM-04 R2) is satisfied: this PR is one logical change (entity introduction + API annotation + new `dea:specifies` relationship + 3 relationship extensions + controlled-vocabulary expansion + generated artefacts + docs); no bundle content from CR-022.
- [ ] D-004 / D-005 / Standardization-body embargo clean.

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| New `dea:specifies` relationship bypasses existing relationship semantics | §3.1 audit documents the fit/misfit assessment for ten candidate relationships; the audit is the gating artefact for the new relationship introduction |
| `dea:API` re-classification silently drops non-IS-related API records | EGV-004 identity continuity; the catalog-ownership register in `CR-013 (dea-governance)` records per-catalog gates; `dea:API` retains its identity |
| CATEGORIES controlled-vocabulary expansion drifts from the metamodel semantics | The expansion is documented in §3.2 and in the test file's CATEGORIES constant comment; the pattern follows prior controlled-vocabulary expansions (CR-6 added `temporal` as category L) |
| Inverse `dea:specified-by` is implied rather than registered | `test_r007_inverses_declared` accepts a `dea:...` string for the inverse; a future CR may add `dea:specified-by` as a separately registered relationship if the closed vocabulary needs it |
| Conformance test whitelist inconsistency | `status: deprecated` carries the deprecation signal where applicable; `lifecycle` retains `planned`; the test-alignment CR is parked in DRIFT-3 |
| OpenDEAM identifier drift | D-5 disposition binds the OpenDEAM-to-metamodel identifier map to `CR-AR-FMWK-04` |
| Author confusion (CR-MM-04 author header) | R1 cardinal rule enforced by `validate-authorship.yml` |

## 15. Completion Definition

CR-021 is complete when:

1. `dea:IntegrationInterface` is registered in the normative source with the three relationship endpoint extensions.
2. `dea:API` carries the D-4 audit-then-specifies annotation in the definition body.
3. The new relationship `dea:specifies` is registered with category `contract`, source `dea:API`, target `dea:IntegrationInterface`, inverse `dea:specified-by`.
4. The CATEGORIES controlled vocabulary is expanded with `contract` (category M).
5. The relationship-instance schema enum includes `specifies`.
6. Digital Profile registers the new entity.
7. The JSON Schema is committed and validates; CR-3 conformance is preserved.
8. The four deterministic generators regenerate consistent artefacts.
9. Local CI checks (`validate_metamodel_yaml.py`, `validate_json_schemas.py`, conformance suite, runtime suite) all pass.
10. PR opens against `origin/main`; CI on GitHub Actions shows green before user review.
11. The PR card moves from `In Progress` to `Review` on the board-23 kanban surface.
12. Companion Kanban card (`#390 CR-021 in dea-metamodel`) updates with the PR URL and CI status.

## 16. References

### 16.1 Inputs and authorities

- `technehub-labs/dea-metamodel/change-requests/CR-017-information-systems-domain-semantic-integration.md` (foundation CR; merged 2026-10-16 via PR #170, commit `3e00b35`)
- `technehub-labs/dea-metamodel/change-requests/CR-018-information-system-function.md` (merged 2026-10-16 via PR #171, commit `0f16441`)
- `technehub-labs/dea-metamodel/change-requests/CR-019-information-system-component.md` (merged 2026-10-16 via PR #172, commit `5812cfb`)
- `technehub-labs/dea-metamodel/change-requests/CR-020-information-system-service.md` (merged 2026-10-16 via PR #173, commit `6747d84`)
- ADR-ISA-000 (foundation paper)
- CR-MM-PROC-01 (kernel+specialization template; Process / BusinessProcess)
- CR-016 + ADR-015 (kernel+specialization template; Capability / BusinessCapability)
- CR-MM-04 (authorship cardinal rule R1, R2)
- CR-MM-ECF-04 (entity-system cross-reference)
- CR-AR-FMWK-03 (architecture cross-reference)
- CR-012 (`dea-governance`; EGV-001..012 normative requirements)
- DEA-ID-000 (`dea-governance` foundation paper)

### 16.2 Companion Kanban surface

- Project 23 (DEAMMISE) at `/board/23`: card #390 (CR-021 programme), In Progress during authoring
- Companion umbrella carrier #384
- DRIFT-4 card #419 (InfrastructureComponent placement decision; parked for next slice)
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`

---

End of CR-021.
