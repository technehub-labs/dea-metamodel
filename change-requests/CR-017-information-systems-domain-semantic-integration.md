# CR-017: Information Systems Domain Semantic Integration and Relationship Architecture

| Field | Value |
|-------|-------|
| **CR** | CR-017 |
| **Title** | Information Systems Domain Semantic Integration and Relationship Architecture |
| **Status** | Proposed (this PR) |
| **Layer** | Metamodel (Digital Profile) |
| **Programme** | Information Systems Semantic Architecture |
| **Architectural parent** | ADR-ISA-000 (foundation paper, supplied with this PR) |
| **Companion to** | CR-016 (Capability classification; kernel+specialization template precedent); CR-MM-PROC-01 (Process Kernel + BusinessProcess specialization; kernel+specialization template precedent); CR-MM-ECF-04 (entity-system cross-reference); CR-MM-04 (authorship cardinal rule R1 + R2); CR-MM-ECF-03 (Domain 6 v2.5.0 migration); CR-AR-FMWK-03 (architecture cross-reference) |
| **Depends on** | CR-002 (Relationship Semantics); CR-003 (Entity/Relationship Normalization); CR-004 (Core DEA Ontology); CR-008 (Semantic Architecture and Conformance Specification); CR-016; ADR-002 (Core versus Profiles); ADR-013 (Core non-accumulation); ADR-015 (Capability classification by specialization); CR-MM-PROC-01; CR-MM-ECF-04; CR-MM-04; CR-AR-FMWK-03; `CR-012 (dea-governance)` and DEA-ID-000 (when accepted) |
| **Enables** | CR-018, CR-019, CR-020, CR-021, CR-022; CR-AR-FMWK-04; CR-IS-CAT-01..04; `CR-013 (dea-governance)` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-16 |

## 1. Executive Summary

This Change Request establishes the shared semantic architecture for four Information Systems concepts in the OpenDEA metamodel:

1. `dea:InformationSystemFunction` (behaviour performed by an information system)
2. `dea:InformationSystemComponent` (architectural constituent of an information system)
3. `dea:InformationSystemService` (service provided by an information system)
4. `dea:IntegrationInterface` (interaction boundary through which systems exchange information and functionality)

The CR does not itself register the four entities; that is the work of CR-018, CR-019, CR-020, and CR-021, in that order, with CR-022 closing the metamodel artifacts. CR-017 records the disposition decisions, the canonical relationship matrix, the existing-entity reconciliations, and the cross-domain link between the Information Systems subgraph and the broader Business, Data, Digital, and Technology profiles.

The CR resolves six design decisions (D-1 through D-6) recorded in this PR's thread conversation (thread 1560566532973527130). Five of the six take the recommended option from ADR-ISA-000 section 9; one diverges (D-1, see section 3.1).

The metamodel remains normative at `metamodel/dea-metamodel.yaml`. Generated artifacts (`metamodel/registry/{entities,relationships}.yaml`, `schemas/`, `pydantic/`, `typescript/`, `sqlite/`, `ttl/`, `viewer/`) are produced by the existing generator; no hand-edits.

## 2. Background and Problem Statement

### 2.1 Existing semantic surface

The current metamodel contains entities relevant to information systems:

- `dea:SystemFunction` (L5, building_block L5-systems, profile dea:digital; abstract false; lifecycle planned; catalog_repo dea-catalog-system-functions). Definition: "A functional capability exposed by a single application or system." Legacy identifier: `dea:entity-system-function`.
- `dea:SolutionComponent` (L3, building_block L3-service-offerings, profile dea:digital; abstract false; lifecycle existing; catalog_repo dea-catalog-digital-business-service-factory). Definition: "Abstract parent of ApplicationComponent, InfrastructureComponent, IntegrationComponent (discriminated union by component_type)." Legacy identifiers: `dea:entity-solution-component`, `SolutionComponent`.
- `dea:ApplicationComponent`, `dea:IntegrationComponent`, `dea:InfrastructureComponent` are concrete `SubClass`es of `dea:SolutionComponent` discriminated by `component_type`.
- `dea:PlatformService` (L5, building_block L5-infrastructure, profile dea:digital; abstract false; lifecycle planned; catalog_repo dea-catalog-platform-services). Definition: "A shared infrastructure or runtime service consumed by multiple application components."
- `dea:API` (L5, building_block L5-integration, profile dea:digital; abstract false; lifecycle planned; catalog_repo dea-catalog-api-contracts). Definition: "A contract defining the request/response shape of a service interface."
- `dea:Behavior` (Core anchor; lines 1415 plus four relationship references).
- `dea:Service` (Core anchor; abstract).
- `dea:Capability` (Core anchor; abstract, introduced by CR-016).
- `dea:BusinessCapability`, `dea:BusinessProcess`, `dea:BusinessService`, `dea:DataEntity`, `dea:Event` (Digital Profile anchors).

The current state has three identified semantic problems that CR-017 resolves by disposition:

- `dea:SystemFunction`'s definition uses capability-oriented language ("functional capability") that conflates it with `dea:Capability` and `dea:SystemCapability`. The entity exists; the meaning is ambiguous.
- `dea:SolutionComponent`'s definition describes an "abstract parent" but its registry entry declares `abstract: false`. The inconsistency blocks any sub-specialisation that treats `dea:SolutionComponent` as abstract.
- `dea:API` is the only integration-side concept; no separate interaction-boundary concept exists for non-API interactions (file transfer, streaming, event subscription).

### 2.2 Discovered dependencies (live)

Verified against `origin/main` on 2026-10-16 (see companion snapshot doc + Kanboard thread 1560566532973527130):

- **Latest merged metamodel CR**: `CR-MM-ECF-04` (Entity System Cross-Reference, PR #169). Not CR-016, which is implemented but not the latest.
- **Companion parallel chain CRs in flight**: `CR-MM-PROC-01` (Proposed; uses the same abstract-Core-kernel + concrete-specialization template CR-017 cascades for `dea:InformationSystemFunction` specialising `dea:Behavior`).
- **Authorship cardinal rule CR-MM-04 (R1, R2)** governs every CR merged since 2026-10-13. R1: every authorship field carries a value from `{Emmanuel A. Otchere, TechNeHub Labs}`. R2: any file naming a person playing a named role carries the canonical identity.
- **Governance foundation CR-012 in `dea-governance` is Proposed** (open PR #2); the EGV-001..012 normative requirements are the upstream reference frame.
- **CR-013 in `dea-metamodel` is RESERVED** for Digital Twin / Continuous Enterprise Model (per the CR-1.6 programme index). No naming collision: this CR takes the plain-chain slot CR-017 (CR-016 latest in the plain chain; CR-013 reserved).

## 3. Disposition Decisions (locked)

The following six decisions were disposed on 2026-10-16 in Discord thread 1560566532973527130. CR-017 is the foundation CR for the decisions; CR-018 through CR-022 implement the consequences.

### 3.1 Decision D-1 (DIVERGENT from doc recommendation): introduce `dea:InformationSystemFunction`

Adopted: **Option B** (introduce `dea:InformationSystemFunction` as canonical; retain `dea:SystemFunction` as legacy/superseded via `legacy_ids`).

Rationale (per user 2026-10-16): "system" means many things; the area of system use must be accurate. "System function" can refer to functions performed by an organization system, an ecosystem system, or an information system; only the last is the OpenDEA Digital Profile concern. The narrower canonical name disambiguates the metamodel.

Implications:

- `dea:InformationSystemFunction` is registered as a Digital Profile entity in CR-018, specialising Core `dea:Behavior` (the abstract anchor CR-MM-PROC-01 introduced for Process).
- `dea:SystemFunction` is marked `status: deprecated` with `supersedes` / `legacy_ids` linkage pointing to `dea:InformationSystemFunction`. No record is silently reclassified.
- OpenDEAM identifier `dea:entity-system-function` resolves to `dea:InformationSystemFunction` via the OpenDEAM-to-metamodel identifier map owned by CR-AR-FMWK-04.
- The `dea-catalog-system-functions` GitHub repository renames to `dea-catalog-information-system-functions` per CR-IS-CAT-01. Existing repository redirects/aliases are preserved under EGV-004 (Identity Continuity).
- Cross-cite convention: every cross-repo reference uses the canonical identifier (`dea:InformationSystemFunction`); the legacy identifier appears only in `legacy_ids` lists or the deprecation migration register.

### 3.2 Decision D-2 (adopted recommendation): `dea:SolutionComponent.abstract: true`

`dea:SolutionComponent` becomes abstract in the normative source. Existing and downstream catalog instances keep their concrete identity under EGV-004. The remediation is implemented in CR-019 (where the component hierarchy is rebuilt); CR-017 only records the disposition. Split-cardinality per CR-MM-04 R2: the abstract flip ships with the component hierarchy rewire, not with CR-017.

### 3.3 Decision D-3 (adopted recommendation): `dea:PlatformService` specialises `dea:InformationSystemService` (when applicable)

`dea:PlatformService` becomes a Digital Profile specialisation of `dea:InformationSystemService` only when the record is genuinely a service provided by an information system or software platform. Non-information-system infrastructure offerings stay under Core `dea:Service`. Implemented in CR-020; catalog ownership ratified by `CR-013 (dea-governance)`.

### 3.4 Decision D-4 (adopted recommendation; CR-021 owns the final audit-first decision)

The relationship from `dea:API` to `dea:IntegrationInterface` is implemented ONLY after a vocabulary audit. CR-021 audits the existing relationship vocabulary (`dea:realizes`, `dea:implements`, `dea:specifies`, `dea:governs`, `dea:describes`, etc.). If no existing relationship fits the API-to-interface semantics, CR-021 proposes `dea:API specifies dea:IntegrationInterface` as a new relationship with full source/target constraints and a documented inverse.

### 3.5 Decision D-5 (adopted recommendation): OpenDEAM identifier mapping owned by CR-AR-FMWK-04

Every OpenDEAM `dea:entity-*` identifier maps to a canonical metamodel `dea:*` identifier inside `model/opendeam-model.yaml`. The mapping is owned by CR-AR-FMWK-04 and captured in the migration-id-map (per EGV-012). CR-017 does not introduce or alter mapping entries.

### 3.6 Decision D-6 (adopted recommendation): generated-registry authority with blocking CI gate

`metamodel/registry/{entities,relationships}.yaml` is generated from `metamodel/dea-metamodel.yaml`. The relationship registry is NOT an independent source of truth. A blocking CI gate is added (or extended, where the `validate-metamodel` workflow already enforces this) to reject any hand-edit to `metamodel/registry/*.yaml` other than under the generator's own commit signature. EGV-011 applies.

## 4. Canonical Relationship Matrix

The matrix below records the intended relationship coverage between the four Information Systems concepts and the relevant existing concepts. Each cell carries either a relationship name (existing vocabulary) or the marker `audit-then-decide` (CR-021 audit required before introducing a new relationship).

### 4.1 Information System Function

| Source | Relationship | Target | Status |
|---|---|---|---|
| `dea:InformationSystemFunction` | `dea:specializes` | `dea:Behavior` | Reserved for CR-018 (Core anchor exists; `dea:specializes` vocabulary extension required) |
| `dea:InformationSystemFunction` | `dea:composes` | `dea:InformationSystemFunction` | Existing vocabulary; retain and validate |
| `dea:InformationSystemFunction` | `dea:realizes` | `dea:BusinessCapability` | Existing vocabulary (`dea:realizes` source list includes `SystemFunction`; CR-018 to validate the equivalent for `InformationSystemFunction`) |
| `dea:InformationSystemFunction` | `dea:enables` | `dea:BusinessProcess` | Existing vocabulary; retain and validate |
| `dea:InformationSystemFunction` | `dea:depends-on` | `dea:InformationSystemFunction` | Existing vocabulary; retain |
| `dea:InformationSystemFunction` | `dea:orchestrates` | `dea:InformationSystemFunction` | Existing vocabulary; retain |
| `dea:InformationSystemFunction` | `dea:flows-to` | `dea:InformationSystemFunction` | Existing vocabulary; retain and validate direction |
| `dea:InformationSystemFunction` | `dea:consumes` | `dea:DataEntity` / `dea:Event` | Existing vocabulary; retain |
| `dea:InformationSystemFunction` | `dea:produces` | `dea:DataEntity` / `dea:Event` | Existing vocabulary; retain |
| `dea:InformationSystemComponent` | `dea:executes` | `dea:InformationSystemFunction` | Existing vocabulary; **target list extension required** (`dea:executes` target list currently `BusinessFunction, BusinessProcess`; CR-019 extends) |
| `dea:InformationSystemFunction` | `dea:uses` | `dea:InformationSystemService` | Existing vocabulary; CR-020 validates the source/target placement after the service introduction |

### 4.2 Information System Component

| Source | Relationship | Target | Status |
|---|---|---|---|
| `dea:InformationSystemComponent` | `dea:specializes` | `dea:SolutionComponent` | Reserved for CR-019 (after D-2 abstract flip) |
| `dea:ApplicationComponent` | `dea:specializes` | `dea:InformationSystemComponent` | Reserved for CR-019 (sub-classification requires `dea:specializes` vocabulary extension) |
| `dea:IntegrationComponent` | `dea:specializes` | `dea:InformationSystemComponent` | Reserved for CR-019 |
| `dea:InfrastructureComponent` | `dea:specializes` | (TBD) | CR-019 evaluates: a true information-system constituent, or remain `dea:SolutionComponent` direct |
| `dea:InformationSystemComponent` | `dea:composes` | `dea:InformationSystemComponent` | Existing vocabulary; CR-019 extends endpoints |
| `dea:InformationSystemComponent` | `dea:depends-on` | `dea:InformationSystemComponent` | Existing vocabulary; CR-019 extends endpoints |
| `dea:InformationSystemComponent` | `dea:executes` | `dea:InformationSystemFunction` | Existing vocabulary; CR-019 adds target list to `dea:executes` |
| `dea:InformationSystemComponent` | `dea:provides` | `dea:InformationSystemService` | Existing vocabulary; CR-020 extends target list of `dea:provides` |
| `dea:InformationSystemComponent` | `dea:exposes` | `dea:IntegrationInterface` | Existing vocabulary (`dea:exposes` already permits `ApplicationComponent` as source); CR-021 extends to `dea:IntegrationInterface` as target |

### 4.3 Information System Service

| Source | Relationship | Target | Status |
|---|---|---|---|
| `dea:InformationSystemService` | `dea:specializes` | `dea:Service` | Reserved for CR-020 (Core anchor exists) |
| `dea:PlatformService` | `dea:specializes` | `dea:InformationSystemService` | Reserved for CR-020 (per D-3; conditional) |
| `dea:ApplicationComponent` | `dea:provides` | `dea:InformationSystemService` | Existing vocabulary; CR-020 extends target list |
| `dea:InformationSystemComponent` | `dea:provides` | `dea:InformationSystemService` | Existing vocabulary; CR-020 extends target list |
| `dea:BusinessProcess` | `dea:uses` | `dea:InformationSystemService` | Existing vocabulary; CR-020 validates / extends |
| `dea:InformationSystemService` | `dea:depends-on` | `dea:InformationSystemService` | Existing vocabulary; CR-020 validates |
| `dea:InformationSystemService` | `dea:realizes` | `dea:BusinessService` | Audit-then-decide: confirm or extend the realization vocabulary before use |
| `dea:InformationSystemService` | `dea:exposes` | `dea:IntegrationInterface` | Existing vocabulary (`dea:exposes` permits `Service` family as source); CR-021 extends target list |

### 4.4 Integration Interface

| Source | Relationship | Target | Status |
|---|---|---|---|
| `dea:IntegrationComponent` | `dea:exposes` | `dea:IntegrationInterface` | Existing vocabulary; CR-021 extends target list |
| `dea:ApplicationComponent` | `dea:exposes` | `dea:IntegrationInterface` | Existing vocabulary; CR-021 extends target list |
| `dea:InformationSystemComponent` | `dea:exposes` | `dea:IntegrationInterface` | Existing vocabulary; CR-021 extends target list |
| `dea:InformationSystemComponent` | `dea:uses` | `dea:IntegrationInterface` | Existing vocabulary; CR-021 extends target list |
| `dea:API` | `dea:specifies` | `dea:IntegrationInterface` | **Audit-then-decide** (D-4): CR-021 audits the existing vocabulary first; introduces `dea:API specifies dea:IntegrationInterface` only if no existing fit |
| `dea:IntegrationInterface` | `dea:exchanges` | `dea:DataEntity` / `dea:Event` | Existing vocabulary; CR-021 extends source list and validates |
| `dea:IntegrationInterface` | `dea:depends-on` | `dea:InformationSystemComponent` | Audit-then-decide: confirm whether dependency belongs to the interface or to the provider |

## 5. Relationship Reuse Rule (inherited from CR-002)

For every relationship in section 4, the entity CRs MUST follow the relationship reuse sequence established by CR-002:

1. Search the existing canonical relationship vocabulary.
2. Confirm the existing relationship's definition and category.
3. Confirm the existing source and target type constraints.
4. Confirm direction and inverse.
5. Confirm the relationship semantics fit the intended assertion.
6. Reuse the relationship if all conditions are satisfied.
7. Propose a new relationship only if no existing relationship is semantically suitable.
8. Update the normative metamodel source, regenerate derived registries, validate all affected existing and new endpoints.

A relationship MUST NOT be reused merely because its name appears suitable; the audit produces the rationale, not the matching label.

## 6. Out of Scope

This CR does not:

- Register `dea:InformationSystemFunction`, `dea:InformationSystemComponent`, `dea:InformationSystemService`, or `dea:IntegrationInterface`. Those entity introductions belong to CR-018 through CR-021.
- Define catalog content or migrate catalog records (CR-IS-CAT-01..04).
- Modify the OpenDEAM root model (CR-AR-FMWK-04).
- Introduce a new general governance standard (CR-012 in `dea-governance` owns that).
- Replace the organization-wide governance standard with an Information-Systems-specific one.
- Modify any Core anchor; all Information Systems work is Digital Profile or Technology Profile scoped.
- Make any change to runtime execution semantics, API gateway configuration, or message broker topology.

## 7. Architectural Decisions Required Before CR-018..021 Implementation

The following decisions are recorded in this CR and delegated to the owning entity CR per ADR-ISA-000 section 18:

| Decision ID | Decision | Owning CR |
|---|---|---|
| D-017-01 | `dea:InformationSystemFunction` identity locked as new canonical per D-1 | CR-018 |
| D-017-02 | `specializes dea:Behavior` confirmed | CR-018 |
| D-017-03 | `dea:SolutionComponent.abstract: true` | CR-019 |
| D-017-04 | Component specialisation hierarchy | CR-019 |
| D-017-05 | PlatformService specialisation (per D-3) | CR-020 |
| D-017-06 | `dea:InformationSystemService specializes dea:Service` | CR-020 |
| D-017-07 | API-to-Integration-Interface relationship semantics (audit-then-specifies per D-4) | CR-021 |
| D-017-08 | Whether a new interface-connection relationship is required | CR-021 |
| D-017-09 | Relationship endpoint changes and inverse consistency across the Information Systems subgraph | CR-018 through CR-021 |
| D-017-10 | Catalog ownership and migration mappings (per EGV-012) | CR-IS-CAT-01..04, ratified by `CR-013 (dea-governance)` |

CR-017 lands with all ten decisions delegated; the dispositions in section 3 are the agreed binding. No entity CR may override a delegated decision without an amendment CR to CR-017.

## 8. Implementation Plan and Dependencies

Implementation follows the dependency sequence in ADR-ISA-000 section 4:

1. CR-017 (this CR; foundation). Lands first.
2. CR-018 (System Function). Gated on this CR's merge.
3. CR-019 (Information System Component). Gated on this CR's merge.
4. CR-020 (Information System Service). Gated on this CR's merge.
5. CR-021 (Integration Interface). Gated on this CR's merge.
6. CR-022 (Metamodel Artifact and Conformance Closure). Gated on CR-018 through CR-021 merging.
7. CR-AR-FMWK-04 (OpenDEAM Entity Allocation and Relationship Integration). Gated on CR-022 merging.
8. CR-IS-CAT-01..04 (catalog rename / establishment / population). Gated on CR-022 + CR-AR-FMWK-04.
9. `CR-013 (dea-governance)` portfolio adoption and registration. Closure gate for the programme.

The four entity CRs may be developed in parallel after CR-017's merge, but their acceptance is coordinated so the final subgraph is consistent.

## 9. Repository Changes (scoped to this CR)

This CR's own PR is documentation-only:

- `change-requests/CR-017-information-systems-domain-semantic-integration.md` (added)
- `change-requests/README.md` (registers CR-017 and its dependencies)
- `docs/information-systems-semantic-architecture.md` (added; references ADR-ISA-000 + the four downstream entity CRs)
- `docs/glossary.md` (preliminary pointer entries for the four concepts; full definitions land with CR-018..021)

No edits to `metamodel/dea-metamodel.yaml`, `metamodel/registry/*.yaml`, schemas, Pydantic, TypeScript, SQLite, TTL, or viewer artifacts land in CR-017. Those belong with CR-018 through CR-022.

## 10. Acceptance Criteria

CR-017 is complete only when all the following are satisfied:

- [ ] The four Information Systems concepts have approved normative semantic distinctions.
- [ ] Capability, function, behaviour, component, service, interface, and contract are explicitly distinguished.
- [ ] Each concept has documented scope and exclusions.
- [ ] The six disposition decisions in section 3 are recorded in the umbrella carrier card.
- [ ] No duplicate canonical concept is introduced without an explicit identity decision.
- [ ] The canonical relationship matrix (section 4) is recorded as the normative basis for CR-018 through CR-021.
- [ ] Existing entities (`dea:SystemFunction` legacy role, `dea:SolutionComponent`, `dea:PlatformService`, `dea:API`) are explicitly reconciled.
- [ ] The Core and Profile separation is preserved (ADR-002, ADR-013).
- [ ] `metamodel/registry/*.yaml` authority rule is reaffirmed (D-6).
- [ ] Cross-references to CR-016, CR-MM-PROC-01, CR-MM-ECF-04, CR-MM-04, CR-MM-ECF-03, CR-AR-FMWK-03 are present.
- [ ] Cross-references to `CR-012 (dea-governance)` and DEA-ID-000 are present (when accepted).
- [ ] Authorship cardinal rule (CR-MM-04 R1) is satisfied: `Author: Emmanuel A. Otchere` carries a value from the allowlist.
- [ ] Authorship cardinal rule (CR-MM-04 R2) is satisfied: this PR is a single logical change.
- [ ] D-004 (no en/em-dash, no U+2E3B) clean across all changed files.
- [ ] D-005 (no three-semicolon run) clean across all changed files.
- [ ] Standardization-body embargo: no legacy telecom body vocabulary anywhere in this PR.
- [ ] CI: `validate-metamodel` workflow green; `validate-authorship` workflow green per CR-MM-04.
- [ ] Companion Kanboard umbrella carrier card on board 23 (DEAMMISE) is at column Review; companion parent-card on board 9 (github-technelabs) acknowledges the programme.

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `dea:InformationSystemFunction` and `dea:SystemFunction` end up with overlapping content | Identity drift | D-1 disposition plus the dependency hand-off to CR-018 + D-3 cascade documentation (DRIFT-3 card on board 23) |
| `dea:SolutionComponent` abstract flip breaks existing catalog instances | Regression | EGV-004 identity continuity; CR-019 owns the migration map per EGV-012 |
| Platform Service reclassification creates catalog split | Ownership drift | D-3 conditional specialisation; CR-013 (governance) owns the catalog ownership decision |
| `dea:API specifies dea:IntegrationInterface` is introduced without audit | Semantic dilution | D-4 audit-first posture; CR-021 records the audit and the rationale for any new relationship |
| `metamodel/registry/*.yaml` is hand-edited | Multiple sources of truth | D-6 generated-authority rule with blocking CI gate |
| Existing-Catalog migrations are incomplete | Lost identity continuity | EGV-012 per-record disposition register in CR-022 + CR-AR-FMWK-04 |

## 12. Completion Definition

CR-017 is complete when the Information Systems semantic architecture has been approved, the canonical relationship matrix is locked against the existing vocabulary, the six disposition decisions are recorded in the umbrella carrier, and CR-018 through CR-021 can implement the four concepts without redefining the shared architecture.

CR-017 does not claim the four entities, the catalogs, or the OpenDEAM allocations are already in place. It establishes the normative architecture that makes those subsequent changes coherent.

## 13. References

### 13.1 Author-supplied inputs (this PR's foundation package)

- ADR-ISA-000: Information Systems Semantic Architecture programme envelope (foundation paper)
- CR-017 (author-supplied draft): section structure, the reconciliation problem statement, the cross-domain link
- CR-018, CR-019, CR-020, CR-021: entity-specific CR drafts, each referencing this foundation

### 13.2 Existing canonical references in `dea-metamodel`

- `metamodel/dea-metamodel.yaml` (NORMATIVE; lines 906, 1193, 1215, 1236, 1258, 1280, 1301, 1415 carry the entities and the Core anchor this CR references)
- `metamodel/registry/{entities,relationships}.yaml` (GENERATED; not edited by hand per D-6)
- `change-requests/README.md` (CR-1.8; programme index and freeze history)
- `change-requests/CR-016.md` (Capability classification implementation; PR #152; kernel+specialization template precedent)
- `change-requests/CR-MM-PROC-01.md` (Proposed; the active kernel+specialization use case in the metamodel)
- `change-requests/CR-MM-ECF-04.md` (PR #169; latest merged; entity-system cross-reference)
- `change-requests/CR-MM-04.md` (PR #168; authorship cardinal rule R1, R2)
- `change-requests/CR-MM-ECF-{01,02,03}.md` (PR #161, #165, #167; ECF Domain Enum migrations)
- `change-requests/CR-AR-FMWK-01.md` (Process Kernel + Business Process Specialization in OpenDEAM root model; precedent for CR-AR-FMWK-04)

### 13.3 Cross-repo references

- `technehub-labs/dea-governance/change-requests/CR-012-org-wide-entity-governance.md` (Proposed; PR #2; EGV-001..012 normative requirements)
- `technehub-labs/dea-governance/docs/design/entity-system-foundation.md` (DEA-ID-000; foundation paper for the entity system)
- `technehub-labs/dea-architecture-framework/change-requests/CR-AR-FMWK-03.md` (PR #16; entity-system cross-reference in architecture framework)

### 13.4 Companion Kanban surface

- Project 23 (DEAMMISE) at `/board/23`: per-thread kanban for the Information Systems programme
- Project 9 (github-technelabs) at `/board/9`: parent-channel umbrella card
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`

---

End of CR-017.
