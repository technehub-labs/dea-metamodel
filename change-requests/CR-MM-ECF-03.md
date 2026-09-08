# CR-MM-ECF-03: ECF Domain Enum v2.5.0 Migration (Domain 6 rename)

Status: Accepted
Layer: Metamodel
Owner: Coder (for eaojnr)
Depends on: CR-ECF-008 (governed by ADR-ECF-003); CR-MM-ECF-02 (the v2.4.0 migration carrier)
Companion to: CR-BP-23 (dea-catalog-processes); CR-BC-ECF-03 (dea-catalog-business-capabilities); CR-BO-02 (dea-catalog-business-objects); CR-OU-02 (dea-catalog-organizational-units)
Date: 2026-09-08

## What this CR is

This CR is the **v2.5.0 migration carrier** for `technehub-labs/dea-metamodel`. ECF Domain 6 is renamed from `OperationsAndEnablement` (v2.4.0) to `EnablementAndOperations` (v2.5.0), driven by the Domain/Stage Orthogonality Stress Test (ADR-ECF-003 §5): the word `Operations` in the Domain 6 name shared a lexical root with Stage 5 `Operate`, obscuring the orthogonality that the ECF requires between the Domain axis and the Stage axis. The change is a single Domain rename; the other six Domains and the cardinality of the seven-Domain × seven-Stage matrix are unchanged. No content redistribution is required (CR-ECF-008 §3.5): all content that previously belonged to `Operations & Enablement` remains in `Enablement & Operations`.

The v2.3.0 carrier (`CR-MM-ECF-01`) and the v2.4.0 carrier (`CR-MM-ECF-02`) are the historical records of the previous migrations; the new carrier (`CR-MM-ECF-03`) is the v2.5.0 update.

## Mapping

| Old form (v2.4.0) | New form (v2.5.0) |
|---|---|
| `OperationsAndEnablement` (PascalCase enum value) | `EnablementAndOperations` |
| `operations-enablement` (kebab-case enum value) | `enablement-operations` |
| `operationsEnablement` (lowerCamelCase identifier) | `enablementAndOperations` |
| `operations_enablement` (Python identifier; pydantic Literal) | `enablement_and_operations` |
| `Operations & Enablement` (display form) | `Enablement & Operations` |

## Unchanged

- Domain number (6), matrix position (row 6)
- Semantic anchor (`Execution`)
- Axiomatic grounding ("persists" + "exchanging value")
- Domain scope, lifecycle applicability, seven-Domain partition
- Seven lifecycle Stages
- Stage 5 name (`Operate`)
- ECF construction: `Domain × Stage = 49 coordinates`
- Catalog ID abbreviation `oe` (stable; not re-keyed)

## Backward compatibility

The metamodel keeps the kebab-case form `enablement-operations` as the canonical in-schema enum value (lowest blast radius; consumer catalogs already use kebab-case per CR-MM-ECF-01 §3.1). The PascalCase `EnablementAndOperations` is the canonical enum value in `dea-metaframework`. The lowerCamelCase `enablementAndOperations` is the identifier suffix used in `coordinate_identifier()` outputs.

No deprecated alias map is introduced in `dea-metamodel` itself (the metamodel has no legacy aliases; the previous rename `PeopleAndOrganization` → `AgencyAndOrganization` likewise did not preserve aliases in this repo). The alias map lives in `dea-metaframework:tools/ecf_coordinates.py:DOMAIN_ALIASES` and is consumed by the metamodel's validators via the shared `dea-metaframework` dependency.

## Files changed

- **3 entity schemas** (`schemas/entities/`): `business-object.json`, `organizational-unit.json`, `process.json` — kebab-case enum updated.
- **1 SQLite schema** (`sqlite/schema.sql`): all CHECK constraints that referenced `operations-enablement` updated to `enablement-operations`. The `sqlite/dea-metamodel.db` database is regenerated from the updated schema (the DB file is a binary asset regenerated from the schema).
- **1 Pydantic literal** (`pydantic/process.py`): `process_audience` Literal updated to `enablement_and_operations`.
- **1 TypeScript type alias** (`typescript/src/interfaces.ts`): `EcfDomain` + `ProcessAudience` updated.
- **1 validator** (`scripts/validate_ecf_kebab_restatement.py`): `DOMAIN_KEBAB_TO_PASCAL` mapping table updated (lines 18, 86, and the docstring narrative at line 18).
- **1 detector** (`scripts/detect_drift.py`): `DOMAIN_ID` PascalCase → lowerCamelCase mapping updated (line 53).
- **1 controlled vocabulary** (`metamodel/vocabularies/classifications.yaml`): 3 controlled-vocabulary enums (BusinessObject, OrganizationalUnit, Process) updated.
- **5 docs files**: `docs/process-type-taxonomy.md`, `docs/concepts/terminology-alignment.md`, `docs/ecf-profile.md`, `docs/glossary.md`, and the v2.3.0 carrier `change-requests/CR-MM-ECF-01.md` (add §13 documenting the v2.5.0 migration).
- **2 CR records**: `change-requests/CR-MM-ECF-01.md` (status + new §13); `change-requests/CR-MM-ECF-03.md` (this file; the new carrier).
- **1 CHANGELOG section**: `[2.5.0-migration] - 2026-09-08` added.
- **1 README update**: `change-requests/README.md` (CR-MM-ECF-03 row added).

Total: **14 files modified** + **1 new CR carrier** + **1 CHANGELOG section**.

## Verification

- `tests/conformance/`: 133/133 pass (validator's kebab-case 1:1 mapping now includes `enablement-operations`).
- `tests/runtime/`: 290/290 pass (TypeScript/Pydantic schemas regenerable from the updated enums).
- `scripts/validate_ecf_kebab_restatement.py`: PASS (every kebab-case value in the restating schemas resolves 1:1 to the canonical PascalCase enum).
- `scripts/validate_ecf_kebab_restatement.py --self-test`: PASS (the validator still detects broken restatement schemas).
- `sqlite/dea-metamodel.db`: regenerated (99 tables rebuilt from the updated schema).
- `scripts/detect_drift.py`: passes the in-house drift detector (Domain 6 in canonical position, no mismatch).

## What did NOT change

- **No new Domain introduced.** The cardinality remains seven Domains (CR-ECF-008 §18 non-goal).
- **No Domain ordering change.** Domain 6 remains row 6 (CR-ECF-008 §18 non-goal).
- **No matrix construction change.** `ECF = Domain × Stage = 49 coordinates` is preserved (CR-ECF-008 §18 non-goal).
- **No semantic anchor change.** Domain 6 remains anchored on `Execution` (CR-ECF-008 §5).
- **No lifecycle change.** All seven Stages are unchanged (CR-ECF-008 §18 non-goal); Stage 5 remains `Operate`.
- **No content redistribution.** All entities that previously belonged to Domain 6 remain in Domain 6 (only the name changed; the semantic scope is preserved per CR-ECF-008 §3).

## Downstream impact (cascade)

The metamodel is the **gate** for downstream catalog migrations. Each downstream catalog has its own carrier CR:

- `dea-catalog-processes`: **CR-BP-23** (v2.5.0 migration; 100+ file footprint)
- `dea-catalog-business-capabilities`: **CR-BC-ECF-03** (v2.5.0 migration; 48 file footprint)
- `dea-catalog-business-objects`: **CR-BO-02** (v2.5.0 migration; 4 file footprint)
- `dea-catalog-organizational-units`: **CR-OU-02** (v2.5.0 migration; 3 file footprint)

Other repos audited as having no footprint (no `OperationsAndEnablement` / `operations-enablement` references):
- `dea-catalog-actors` (0 files)
- `dea-catalog-stakeholders` (0 files)
- `dea-catalog-digital-business-service-factory` (0 files)
- `dea-architecture-framework` (0 files)
- `technehub-labs.github.io` (Pages display; updated by CR-ECF-008 itself in `dea-metaframework`)