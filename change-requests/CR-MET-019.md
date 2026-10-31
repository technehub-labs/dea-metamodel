# CR-MET-019: Information Model Entity (IM) + dea:structures Relationship

| Field | Value |
|---|---|
| **CR** | CR-MET-019 |
| **Title** | Information Model entity (IM) + dea:structures relationship — the conceptual/logical blueprint of the information family |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-01 |
| **Depends on** | CR-AR-FMWK-15 (dea-architecture-framework PR #34: root-model allocation, v0.9.0, tag cut); dea-governance CR-017 (register v8: the catalog_repo is registered ahead of this PR so reconciler R1 never flags it) |
| **Enables** | dea-catalog-information-models CR-IM-CAT-01 (kit; pins root ref v0.9.0) / CR-IM-CAT-02 (population plan) |
| **Trigger** | Owner directive: extend the metamodel with an "information model" entity distinct from InformationClass (the sensitivity/regulatory band) and InformationAsset (the consumable form). Design decisions ratified by the owner: conceptual/logical-blueprint definition; new `dea:structures` relationship; evidence-only ramp-up. |

## 1. Executive summary

Introduces `dea:InformationModel` (alias `IM`, L4-information-knowledge, profile `dea:data`, lifecycle `planned`, `catalog_repo: dea-catalog-information-models`) — *a formal model that specifies the structure, semantics, and constraints of information for a domain: the conceptual or logical blueprint from which Data Entities are shaped and Information Assets take form.* Adds the `dea:structures` relationship (InformationModel → DataEntity, InformationAsset; inverse `dea:structured-by`) — model-level structuring, which the vocabulary does not currently serve (`specifies` is deliberately bounded to API→IntegrationInterface per CR-021; `curates` is instance-level content maintenance). Extends `dea:represents.source` and `dea:informs.target`, the `dea:Information` anchor enumeration (all four copies), the `dea:data` profile, and ships every artifact in this PR (the artifact-drift ratchet forbids the CR-020/CR-022 two-CR null window).

## 2. Changes

1. `metamodel/dea-metamodel.yaml`: entity block; `dea:structures` relationship; `dea:represents.source` += InformationModel; `dea:informs.target` += InformationModel; `dea:Information` definition enumeration += InformationModel.
2. `metamodel/profiles/data/profile.yaml`: entity added; scope sentence extended ("models").
3. `metamodel/core/core-entities.yaml` + `ttl/dea-metamodel-ontology.ttl`: anchor enumeration extended; TTL gains `owl:Class dea:InformationModel` and `owl:ObjectProperty dea:structures` (single-word id per TTL camelization convention); `specification/*` regenerated (fourth copy rides the generator).
4. `schemas/entities/information-model.json` (new; `metamodel_version` 1.0.0 per the manifest — test_004 requires fleet consistency); `metamodel/vocabularies/classifications.yaml`: `InformationModel.model_form` enum registered (E005).
5. `schemas/relationships/relationship-instance.json`: `structures` added to the 119-type closed enum (R005).
6. `sqlite/schema.sql`: `information_models` table + `InformationModel` in the entities type CHECK.
7. `typescript/src/interfaces.ts`: `InformationModel` interface, AnyEntity union, ENTITY_TYPES (the insertion correctly targets the `] as const;` closer — the earlier DRIFT-5 RelationshipType union is untouched).
8. `pydantic/information_model.py` regenerated; `metamodel/registry/*` + `specification/*` regenerated; **VERSION unchanged at 1.0.0** (manifest governs; test_004 pins fleet consistency — a canonical bump would churn 139 schemas and is deferred to the next closure CR).

## 3. Decisions

| # | Decision |
|---|---|
| D1 | Definition: conceptual/logical blueprint (owner-ratified); formal artifacts (schemas, ontologies) are the model's *forms*, not its boundary |
| D2 | Structuring role served by a new `dea:structures` relationship, not a widening of `specifies` (owner-ratified; preserves the CR-021 API→II boundary) |
| D3 | Alias `IM` (unassigned in both the root model's 99-alias set and the metamodel registry) |
| D4 | Profile `dea:data`; building block L4-information-knowledge (alongside InformationAsset/KnowledgeAsset) |
| D5 | Lifecycle `planned` at allocation; promotion to `existing` by a boundary CR once the catalog carries its foundation (CR-MET-016 precedent) |

## 4. Verification

1. `pytest tests/conformance/` — 369 passed, 10 skipped.
2. `validate_artifacts.py --report` — TOTAL FINDINGS: 0 (ratchet intact).
3. Registry regenerated at manifest version: 164 entities, 121 relationships (test_007 sync).
4. `tsc --noEmit` clean.
5. Root model v0.9.0 (tag) carries the allocation; governance register v8 carries the repo (reconciler Findings: 0).

## 5. NOT-list

1. No changes to `dea:specifies` (the CR-021 boundary stands).
2. No TTL generator work (DRIFT-6 stands; hand-maintained entries follow the file's camelization convention).
3. No DRIFT-5 RelationshipType-union repair (pre-existing; named follow-up).
4. No catalog-side content (CR-IM-CAT series owns the repo).
5. The pre-existing sqlite entities-type CHECK omission of the older information-family types (InformationAsset, DataEntity, etc.) is named here as a follow-up — this CR adds only its own type per the CR-022 pattern.
