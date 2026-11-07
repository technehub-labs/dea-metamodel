# CR-MET-020: Plain-Language Attribute Set on Task and BusinessProcess

| | |
|---|---|
| **CR** | CR-MET-020 |
| **Title** | Plain-Language Attribute Set on Task and BusinessProcess |
| **Status** | Proposed (this PR) |
| **Target repository** | dea-metamodel |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-07 |
| **Depends on** | CR-BP-230 (the catalogue-side attribute definition this CR mirrors), CR-BP-233..236 (the authored corpus that gives the attributes content) |
| **Enables** | Cross-repo attribute drift checks (a future test in the `tests/cross_repo_consumer/` family), catalogue→metamodel alignment audits |
| **Trigger** | Owner directive 2026-11-07: proceed with the metamodel companion enabled (but deferred) by catalogue CR-BP-230 §4 — the five plain-language attributes the catalogue landed schema-side and authored corpus-wide (3,723 records) now join the metamodel |

## 1. Executive summary

Five optional attributes — `plain_language_name` (1–200), `plain_language_description` (1–2000), `business_purpose` (1–1000), `practical_context` (1–1000), and `worked_example` (object: `agent_type` ∈ {`human`,`non-human`,`mixed`} + `narrative` 1–2000) — are added to the two executable-work entities, `dea:Task` and `dea:BusinessProcess`, mirroring the catalogue-side attribute set of CR-BP-230 exactly (same names, shapes, and bounds). All optional; no required-set or id changes; VERSION unchanged at 1.0.0 (`metamodel/manifest.yaml` governs). The `dea:agentic` profile (Task) and `dea:business` profile (BusinessProcess) inherit the properties through their schemas without profile-file edits. Ships every artifact in this PR (the artifact-drift ratchet forbids any null window): both JSON schemas, regenerated pydantic, sqlite DDL + migrated checked-in db, TypeScript interfaces (+ a shared `WorkedExample` type), and the regenerated registry/specification. TTL needs no change (datatype properties are not modeled per-entity there; no new entity or relationship). Ratchet: TOTAL FINDINGS 0.

## 2. Changes

1. `schemas/entities/task.json` — five properties inserted after `name`; `metamodel_version` unchanged at 1.0.0 (test_004 fleet pin).
2. `schemas/entities/process.json` — same five properties inserted after `name`.
3. `pydantic/task.py`, `pydantic/process.py` — regenerated via `.github/scripts/generate_pydantic.py` (CI freshness gate: `git diff --exit-code` after regeneration passes).
4. `sqlite/schema.sql` — `processes` gains the five columns (comma style, after `outcome`); `tasks` gains the five columns (the table's existing newline style); `.read` parses clean in a fresh `:memory:` db.
5. `sqlite/dea-metamodel.db` — migrated in place with column-preserving `ALTER TABLE ... ADD COLUMN` (no row loss; entity count unchanged), keeping the checked-in db consistent with the DDL.
6. `typescript/src/interfaces.ts` — new shared `WorkedExample` interface; `Task` and `BusinessProcess` gain the five optional fields.
7. `metamodel/registry/`, `specification/` — regenerated (`generate_registry.py`, `generate_specification.py`; 164 entities / 121 relationships unchanged).
8. `metamodel/dea-metamodel.yaml` — **unchanged**: the normative YAML documents entities and relationships, not per-entity datatype properties (the attribute lives in the entity's declared `json_schema` artifact; the CR-MET-019 precedent keeps the normative file at entity/relationship granularity).
9. `metamodel/vocabularies/classifications.yaml` — **unchanged**: `worked_example.agent_type` is a nested enum; E005 polices top-level schema enums only (the registry decision is recorded here so a future top-level promotion registers it deliberately).
10. `ttl/dea-metamodel-ontology.ttl` — **unchanged**: no new entity/relationship class (per CR-MET-019 NOT-list item 2, no TTL generator work).
11. This CR + `change-requests/README.md` row + `CHANGELOG.md` section.

## 3. Decisions

| # | Decision |
|---|---|
| D1 | Attributes land on **both** `dea:Task` and `dea:BusinessProcess`. The catalogue authors them at L2 (BusinessProcess), L4 (Task), and L3/L1/L0 (which have no metamodel entity — documented as "no `dea:Activity` per user reminder 2026-10-18"). Task carries them because catalogue L4 tasks are its densest authored layer. |
| D2 | `worked_example.agent_type` enum is **deliberately not registered** as a top-level E005 classification — it is embedded. Recorded so a future top-level promotion registers it deliberately. |
| D3 | The checked-in db is migrated **in place** with `ALTER TABLE` (column-preserving) rather than rebuilt from DDL, preserving any environment data and keeping the diff minimal. |
| D4 | Property insertion point: immediately after `name` in both schemas, mirroring the catalogue layout and keeping the two schemas structurally parallel. |
| D5 | All five attributes are **optional** — no required-set change, no breaking change for existing instances. |

## 4. Verification

1. `pytest tests/conformance/`: **369 passed, 10 skipped** (identical to CR-MET-019's counts; E003/E004/E005 clean).
2. `pytest tests/runtime/`: **290 passed**.
3. `validate_artifacts.py --report`: **TOTAL FINDINGS: 0**; sqlite 138/138 declared tables present; typescript 190 exported interfaces; ratchet baseline untouched (all counters 0).
4. `npx tsc --noEmit`: clean.
5. `sqlite3 :memory: ".read sqlite/schema.sql"`: parses clean.
6. Pydantic freshness: regeneration after the schema edit produces a `git diff` of exactly the two intended modules.
7. Registry/specification: 164e/121r unchanged (test_007 sync).

## 5. NOT-list

1. No new entity, no new relationship, no profile-file change, no core-entities change.
2. No TTL change (no new owl:Class; per-entity datatype properties remain unmodeled in TTL).
3. No VERSION change (1.0.0; manifest governs; test_004 fleet pin untouched).
4. No `dea:Activity` entity introduced (the catalogue's L3/L1/L0 plain-language fields have no metamodel home; introducing one is a separate entity CR with its own artifact sweep).
5. No catalogue-repo changes in this PR (the catalogue schemas were already extended by CR-BP-230; this CR aligns the metamodel to them).
6. No E005 vocabulary registration for the nested `agent_type` enum (D2).
