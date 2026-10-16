# Information Systems Semantic Architecture (CR-017 foundation)

> **Status**: foundation layer. The four entity introductions land with CR-018, CR-019, CR-020, and CR-021 in `technehub-labs/dea-metamodel`.
>
> **Programme**: Information Systems Semantic Architecture.
>
> **Foundation paper**: ADR-ISA-000 (Information Systems Semantic Architecture programme envelope).
>
> **Source CR**: [CR-017](../change-requests/CR-017-information-systems-domain-semantic-integration.md).

This document is the architectural pointer for the Information Systems subgraph in the OpenDEA metamodel. It summarizes the four concepts, the canonical relationship matrix, and the cross-reference to the implementation CRs.

## 1. The four concepts

| Concept | Canonical name | Layer | Profile | Owns | Implementation status |
|---|---|---|---|---|---|
| Behaviour performed by an information system | `dea:InformationSystemFunction` | L5 | dea:digital | CR-018 | **Implemented in CR-018** (PR open); legacy `dea:SystemFunction` retains `status: deprecated` per EGV-004 |
| Architectural constituent of an information system | `dea:InformationSystemComponent` | L5 | dea:digital | CR-019 | Pending; `dea:SolutionComponent` abstract flip + Application/Integration specialisation rewire |
| Service provided by an information system | `dea:InformationSystemService` | L5 | dea:digital | CR-020 | Pending; Core `dea:Service` specialisation; `dea:PlatformService` reconciliation per D-3 |
| Interaction boundary through which systems exchange | `dea:IntegrationInterface` | L5 | dea:digital | CR-021 | Pending; API reconciliation per D-4 (audit-then-specifies) |

`dea:SystemFunction`, `dea:ApplicationComponent`, `dea:IntegrationComponent`, `dea:InfrastructureComponent`, `dea:PlatformService`, and `dea:API` are reconciled with the four concepts in CR-018 through CR-021. No duplicate identity is introduced without an explicit migration record.

## 2. The six disposition decisions (locked 2026-10-16)

D-1 through D-6 were disposed in Discord thread 1560566532973527130. The decisions are normative; downstream CRs implement them.

- **D-1** Introduce `dea:InformationSystemFunction` as the new canonical Digital Profile entity. `dea:SystemFunction` is retained as a legacy/superseded concept with `legacy_ids` linkage. Rationale: "system" means many things; the area of system use must be accurate. DIVERGENT from the recommendation in the author-supplied CR-017 doc; ratified by the user.
- **D-2** Set `dea:SolutionComponent.abstract: true`. Owned by CR-019.
- **D-3** `dea:PlatformService` specialises `dea:InformationSystemService` only when the service is genuinely a software-platform service; otherwise stay under Core `dea:Service`. Owned by CR-020 with ratification from `CR-013 (dea-governance)`.
- **D-4** Audit the existing relationship vocabulary before introducing `dea:API specifies dea:IntegrationInterface`. Owned by CR-021.
- **D-5** OpenDEAM `dea:entity-*` identifiers map to canonical metamodel `dea:*` identifiers inside `model/opendeam-model.yaml`. Owned by CR-AR-FMWK-04.
- **D-6** `metamodel/registry/{entities,relationships}.yaml` is generated from `metamodel/dea-metamodel.yaml`. A blocking CI gate keeps the registry as a derived artifact (per EGV-011).

## 3. The canonical relationship matrix

The matrix records the intended relationship coverage between the four Information Systems concepts and the relevant existing concepts. Every relationship reuse follows the seven-step audit in CR-002. New relationships are introduced only after the audit.

- Function to Function: `composes`, `depends-on`, `orchestrates`, `flows-to`.
- Function to Business: `realizes` (to `BusinessCapability`), `enables` (to `BusinessProcess`).
- Function to Data/Event: `consumes`, `produces` (`DataEntity`, `Event`).
- Component to Function: `executes` (target list extension in CR-019; `InformationSystemFunction` joins the target list).
- Component to Component: `composes`, `depends-on` (endpoint extensions in CR-019).
- Component to Service: `provides` (target list extension in CR-020).
- Component to Interface: `exposes` (source list extension in CR-021), `uses` (extension CR-021).
- Service to Core: `specializes` (`dea:Service`; introduced in CR-020).
- Service to Business: `realizes` to `BusinessService` (audit-then-decide; CR-020).
- Service to Interface: `exposes` (CR-021).
- API to Interface: `specifies` (introduced by CR-021 after vocabulary audit; per D-4).
- Interface to Information: `exchanges` (CR-021; `DataEntity`, `Event`).

The full matrix lives in CR-017 sections 4.1 through 4.4. The matrix is the normative basis for the four entity CRs.

## 4. Architectural decisions delegated to the entity CRs

Per CR-017 section 18, ten architectural decisions are delegated:

- D-017-01 through D-017-02: System Function identity and Core specialization. CR-018.
- D-017-03 through D-017-04: Solution Component abstract reconciliation and component hierarchy. CR-019.
- D-017-05 through D-017-06: Platform Service specialisation; Information System Service specialisation. CR-020.
- D-017-07 through D-017-09: API-to-Integration-Interface relationship; new interface connection relationship; relationship endpoint changes. CR-021.
- D-017-10: Catalog ownership and migration mappings. CR-IS-CAT-01 through CR-IS-CAT-04, ratified by `CR-013 (dea-governance)`.

No entity CR may override a delegated decision without an amendment CR to CR-017.

## 5. Cross-domain link

The four Information Systems concepts connect to the broader OpenDEA profiles through the registered relationships:

- Business Architecture: `dea:BusinessCapability`, `dea:BusinessProcess`, `dea:BusinessService` (via `realizes`, `enables`, `realizes`).
- Digital Architecture: `dea:ApplicationComponent`, `dea:IntegrationComponent`, `dea:PlatformService` (via `executes`, `composes`, `provides`, `uses`).
- Technology Architecture: `dea:Technology`, `dea:InfrastructureComponent` (via `specializes`, `depends-on`; subject to the component hierarchy decision in CR-019).
- Data Architecture: `dea:DataEntity`, `dea:Event`, `dea:Information`, `dea:InformationAsset` (via `consumes`, `produces`, `exchanges`).
- Core: `dea:Behavior`, `dea:Service`, `dea:Capability` (via `specializes`).

## 6. Cross-reference

| CR / ADR | Repository | Role |
|---|---|---|
| CR-017 (this CR's foundation) | `technehub-labs/dea-metamodel` | Records dispositions, matrix, and architectural decisions |
| CR-018 | `technehub-labs/dea-metamodel` | Introduces `dea:InformationSystemFunction`; reconciles `dea:SystemFunction` |
| CR-019 | `technehub-labs/dea-metamodel` | Introduces `dea:InformationSystemComponent`; reconciles component hierarchy |
| CR-020 | `technehub-labs/dea-metamodel` | Introduces `dea:InformationSystemService`; reconciles `dea:PlatformService` |
| CR-021 | `technehub-labs/dea-metamodel` | Introduces `dea:IntegrationInterface`; reconciles `dea:API` |
| CR-022 | `technehub-labs/dea-metamodel` | Metamodel artifact and conformance closure |
| CR-AR-FMWK-04 | `technehub-labs/dea-architecture-framework` | OpenDEAM allocation + relationship integration |
| CR-IS-CAT-01 | `technehub-labs/dea-catalog-system-functions` (rename to information-system-functions) | Catalog rename + content extension |
| CR-IS-CAT-02 | `technehub-labs/dea-catalog-application-components` (rename to information-system-components) | Catalog rename + content extension |
| CR-IS-CAT-03 | `technehub-labs/dea-catalog-information-system-services` (new) | Catalog establishment + initial population |
| CR-IS-CAT-04 | `technehub-labs/dea-catalog-information-system-integration-interfaces` (new) | Catalog establishment + initial population |
| `CR-013 (dea-governance)` | `technehub-labs/dea-governance` | Portfolio adoption; closure gate |
| CR-MM-PROC-01 | `technehub-labs/dea-metamodel` | Kernel+specialization template precedent |
| CR-MM-ECF-04 | `technehub-labs/dea-metamodel` | Entity-system cross-reference |
| CR-MM-04 | `technehub-labs/dea-metamodel` | Authorship cardinal rule R1, R2 |
| CR-016 | `technehub-labs/dea-metamodel` | Capability classification template precedent |
| CR-AR-FMWK-03 | `technehub-labs/dea-architecture-framework` | Architecture cross-reference precedent |
| CR-012 (`dea-governance`) | `technehub-labs/dea-governance` | EGV-001..012 governance standard |
| DEA-ID-000 | `technehub-labs/dea-governance` | Foundation paper |

## 7. Companion Kanban surface

- Sub-thread project 23 (DEAMMISE) at `/board/23`: per-thread kanban
- Parent-channel card on board 9 (github-technelabs): programme umbrella
- Per-channel skill at `~/.hermes/profiles/coder/skills/dea-is-semantic-arch-kanban-discipline/SKILL.md`
- Snapshot doc at `~/.hermes/profiles/coder/kanban/dea-metamodel-is-snapshot-2026-10-16.md`
