# CR-MM-ECF-02: ECF Domain Enum v2.4.0 Migration

Status: Accepted
Layer: Metamodel
Owner: Coder (for eaojnr)
Depends on: CR-ECF-007 (governed by ADR-ECF-002); CR-MM-ECF-01 (the v2.3.0 migration carrier)
Companion to: CR-BP-18 (dea-catalog-processes); CR-CATALOG-STRUCT-09 (dea-catalog-business-capabilities)
Date: 2026-09-07

## What this CR is

This CR is the **v2.4.0 migration carrier** for `technehub-labs/dea-metamodel`. ECF Domain 3 is renamed from `PeopleAndOrganization` (v2.3.0) to `AgencyAndOrganization` (v2.4.0), driven by the Substrate Independence Stress Test (ADR-ECF-002 §5). The change is a single Domain rename; the other six Domains and the cardinality of the seven-Domain × seven-Stage matrix are unchanged. No content redistribution is required (CR-ECF-007 §6.3): all content that previously belonged to `People & Organization` remains in `Agency & Organization`.

The v2.3.0 carrier (`CR-MM-ECF-01`) is the historical record of the previous migration; the new carrier (`CR-MM-ECF-02`) is the v2.4.0 update.

## Mapping

| Old form (v2.3.0) | New form (v2.4.0) |
|---|---|
| `PeopleAndOrganization` (PascalCase enum value) | `AgencyAndOrganization` |
| `people-organization` (kebab-case enum value) | `agency-organization` |
| `peopleOrganization` (lowerCamelCase identifier) | `agencyOrganization` |
| `people_organization` (Python identifier; pydantic Literal) | `agency_organization` |

## Files changed

- **3 entity schemas** (`schemas/entities/`): `business-object.json`, `organizational-unit.json`, `process.json` — kebab-case enum updated.
- **1 SQLite schema** (`sqlite/schema.sql`): all CHECK constraints that referenced `people-organization` updated to `agency-organization`. The `sqlite/dea-metamodel.db` database is regenerated from the updated schema.
- **1 Pydantic literal** (`pydantic/process.py`): `process_audience` Literal updated to `agency_organization`.
- **1 TypeScript type alias** (`typescript/src/interfaces.ts`): `EcfDomain` + `ProcessAudience` updated.
- **1 validator** (`scripts/validate_ecf_kebab_restatement.py`): `DOMAIN_KEBAB_TO_PASCAL` mapping table updated. The validator's own self-test (broken-schema detection) is unchanged in structure.
- **1 detector** (`scripts/detect_drift.py`): `DOMAIN_ID` PascalCase → lowerCamelCase mapping updated.
- **1 controlled vocabulary** (`metamodel/vocabularies/classifications.yaml`): 3 controlled-vocabulary enums (BusinessObject, OrganizationalUnit, Process) updated.
- **5 docs files**: `docs/process-type-taxonomy.md`, `docs/concepts/terminology-alignment.md`, `docs/ecf-profile.md`, `docs/glossary.md`, and the v2.3.0 carrier `change-requests/CR-MM-ECF-01.md` (add §12 documenting the v2.4.0 migration).
- **2 CR records**: `change-requests/CR-MM-ECF-01.md` (status + new §12); `change-requests/CR-MM-ECF-02.md` (this file; the new carrier).
- **1 CHANGELOG section**: `[2.4.0-migration] - 2026-09-07` added.
- **1 README update**: `change-requests/README.md` (CR-MM-ECF-02 row added).

Total: **15 files modified** + **1 new CR carrier** + **1 CHANGELOG section**.

## Verification

- `tests/conformance/`: 133/133 pass (validator's kebab-case 1:1 mapping now includes `agency-organization`).
- `tests/runtime/`: 290/290 pass (TypeScript/Pydantic schemas regenerable from the updated enums).
- `scripts/validate_ecf_kebab_restatement.py`: PASS (every kebab-case value in the restating schemas resolves 1:1 to the canonical PascalCase enum).
- `scripts/validate_ecf_kebab_restatement.py --self-test`: PASS (the validator still detects broken restatement schemas).
- `sqlite/dea-metamodel.db`: regenerated (99 tables rebuilt from the updated schema).

## What did NOT change

- The cardinality of the seven Domains (7), the matrix M = D × S (49 coordinates), and the no-cell-filling rule are unchanged.
- The five other Domain renames from v2.3.0 (CR-ECF-006) are unchanged.
- No content redistribution is required (CR-ECF-007 §6.3).
- The validator's self-test mechanism is unchanged in structure (only the mapping table is updated).

## Companion migration PRs (parallel sequence)

- **CR-BP-18**: `dea-catalog-processes` v2.4.0 migration
- **CR-CATALOG-STRUCT-09**: `dea-catalog-business-capabilities` v2.4.0 migration

The other 3 catalog repos (`stakeholders`, `actors`, `digital-business-service-factory`) were already v2.3.0 clean and do not need v2.4.0 migration.

## Pause-for-merge

Per CR-programme convention. After you say **Merge**, I will:

1. Merge this PR to main.
2. Open CR-BP-18 in `dea-catalog-processes` (smaller scope; metadata + abbreviation map + docs).
3. Open CR-CATALOG-STRUCT-09 in `dea-catalog-business-capabilities` (schema enum + `DOMAIN_MAP` + 30 entity YAMLs + research files).

Nothing moves until you say Merge.