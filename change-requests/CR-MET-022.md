# CR-MET-022: Catalog Repository Renames — catalog_repo Pointer Repoint

| Field | Value |
|---|---|
| **CR** | CR-MET-022 |
| **Title** | Repoint `catalog_repo` for `dea:BusinessProcess`, `dea:BusinessService`, `dea:SolutionComponent` to the renamed GitHub repositories |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-12 |
| **Depends on** | CR-MET-014 §6.2 (the pre-authorization: "Repointing is a semantic change requiring per-entity verification and is out of scope" — this CR performs it); dea-governance CR-013 §4 finding 1 (naming drift, 2); CR-MET-018 (DEFAULT_ROOTS already reads the new names); `dea-catalog-business-processes` v0.5.0 (released 2026-11-07, CR-BP-30h) |
| **Trigger** | The 2026-11-11/12 org portfolio sweep confirmed both renames are live on GitHub with working redirects: `dea-catalog-processes` → `dea-catalog-business-processes` and `dea-catalog-digital-business-service-factory` → `dea-catalog-business-services`. GitHub redirects keep every old-name URL green today; this CR makes the metamodel's pointers record the real names instead of relying on redirect leniency. Landing order constraint: this CR must merge **before** the governance register v12 (dea-governance CR-022) renames the same rows, so reconciler R1 never sees an unregistered `catalog_repo` value (CR-017 window precedent). |

## 1. Change

Three `catalog_repo` values in `metamodel/dea-metamodel.yaml`, per-entity verified (each target repo exists on origin under the new name, resolves without redirect, and hosts the entity's canonical corpus):

| Entity | Old pointer | New pointer |
|---|---|---|
| `dea:BusinessProcess` | `dea-catalog-processes` | `dea-catalog-business-processes` |
| `dea:BusinessService` | `dea-catalog-digital-business-service-factory` | `dea-catalog-business-services` |
| `dea:SolutionComponent` | `dea-catalog-digital-business-service-factory` | `dea-catalog-business-services` |

This resolves CR-013 §4 finding 1 / CR-MET-014 §6.2 (naming drift, 2) in the **repoint** direction — the org's work repos under the new names are the canonical homes (the business-processes repo holds the 3,723-record corpus and the v0.5.0 release; the services repo holds the 535-record CR-SVC-004-admitted corpus). The declared old names no longer exist as distinct repositories; they are rename redirects.

Per-entity verification evidence (2026-11-11/12 sweep + follow-up): `gh api repos/technehub-labs/dea-catalog-business-processes` and `repos/technehub-labs/dea-catalog-business-services` return the new `name` fields directly (no redirect); record corpora verified by file census (3,882 files / 3,723 records; 535 records active).

## 2. Regenerated

- `metamodel/registry/entities.yaml` — regenerated via `.github/scripts/generate_registry.py` (164 entities, 121 relationships; the three pointers flow through `project_entity()` verbatim).
- `specification/semantic-inventory.yaml` — regenerated via `.github/scripts/generate_specification.py`; **no diff** (correct: the inventory does not project `catalog_repo`).
- Conformance suite must stay green: `tests/conformance/test_007_registry_and_drift.py` (registry sync), lifecycle closed-set, artifact-drift ratchet.

## 3. NOT-list

1. **No legacy index change**: `metamodel.yaml` line 95 (`Process` → `catalog_repo: dea-catalog-processes`) stays stale — the legacy index is frozen consumer-compat surface (deprecated since v0.6.0, CR-001; CR-MET-014/CR-MET-019 precedent: never maintained).
2. **No viewer change**: `viewer/entity-graph.json` carries stale `catalog_repo`/`repo_url` for the three entities but is generated from the pinned upstream root model (`model/opendeam-model.yaml`), not from this metamodel — it catches up at the next opendeam sync (CR-MET-014 §6.4 viewer-lag precedent).
3. **No functional-reference renames**: the metamodel-side functional references to the old names are unchanged and recorded as follow-up CR material (they are documented lock-step with the metaframework tracker `docs/standards/catalog-repository-pattern-adoption.md`, so a clean fix is a cross-repo change): `.github/workflows/ecf-conformance.yml` (clone URL + `ECF_PROCESSES_ROOT`/`ECF_CATALOG_ROOTS`), `KNOWN_CATALOG_REPOS` in `.github/scripts/catalog_summary_builder.py` and `cross_repo_consumer/cli.py` (+ the lock-step test `tests/cross_repo_consumer/test_catalog_summary_builder.py`), `scripts/build_conformance_report.py`, `CONTRIBUTING.md` title. All keep working via GitHub redirects.
4. **No historical record changes**: CHANGELOG historical lines, landed CR files, and `change-requests/README.md` historical rows keep the old names as written-at-the-time history.
5. **No lifecycle changes**: the three entities' `lifecycle: existing` values are unaffected (the pointed-to repos are populated; the values are already truthful).
6. **No VERSION bump**: pointer values are allocation metadata, not schema surface (CR-MET-021 §3.3 precedent).
7. **No GitHub-side actions**: this CR renames nothing on GitHub; the renames already happened upstream.

## 4. Verification

1. `grep -rn "dea-catalog-processes\|dea-catalog-digital-business-service-factory" metamodel/dea-metamodel.yaml metamodel/registry/` → zero hits.
2. `pytest tests/conformance/` green (369 tests, incl. registry-sync test_007 and lifecycle closed-set).
3. `git diff --exit-code -- pydantic/` clean after regeneration (CI drift gate).
4. Post-merge, the governance reconciler (R1 completeness) accepts the three new pointer values — landed in the window **before** governance register v12 so R1 never sees an unregistered value.
