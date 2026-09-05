# CR-CATALOG-STRUCT-07b: Viewer Integration of Cross-Repo Consumer

**Status**: Proposed
**Layer**: L0 (Metaframework; tooling) + L1 (Viewer)
**Owner**: TechNeHub Labs
**Depends on**: CR-CATALOG-STRUCT-07a (consumer module landed in PR #19)
**Companion to**: CR-CATALOG-STRUCT-07 (the full STRUCT-07 slice); 07a (consumer module) merged, 07b (this PR) lands viewer integration, 07c lands AF smoke test.

## What this CR is

Second PR of the three-PR STRUCT-07 stack. Integrates the cross-repo consumer (STRUCT-07a) into the metamodel viewer so each entity card surfaces live CATALOG.yaml data from the corresponding conformant adopter.

Three changes:

1. **Vendoring** the consumer module into `dea-metamodel/.github/scripts/cross_repo_consumer/` so the regeneration script can run in CI without network round-trips to `dea-metaframework`. Plus a `catalog_summary_builder.py` helper at `.github/scripts/` that wraps the consumer.
2. **Regenerator extension**: `.github/scripts/generate_entity_graph.py` now attaches a `catalog_summary` field per entity whose `catalog_repo` matches a known conformant adopter. The summary is fetched at build time from `https://raw.githubusercontent.com/technehub-labs/<repo>/main/CATALOG.yaml` and embedded into `viewer/entity-graph.json`. The viewer JS reads this directly; no runtime fetches.
3. **Viewer UI**: `dea-web-viewer/src/components/EntityDrawer.tsx` renders a new "Catalog content" card with the per-catalog counts (entity_count, canonical, candidates, retired, research_files), `latest_modified`, `metamodel_version`, and `abbreviation`. The card shows only when `catalog_summary` is present (i.e., the entity's `catalog_repo` is one of the four known adopters).

## Decisions locked during planning

- **Q1 (build-time vs runtime fetch)**: build-time. The viewer bundles the data at generation time; the JS does NOT make cross-origin fetches from `technehub-labs.github.io` to `raw.githubusercontent.com`. Pages sites cannot easily do CORS cross-origin fetches from the browser; build-time bundling sidesteps that and also gives a static, versionable entity-graph.json.
- **Q2 (summary field name)**: `catalog_summary` (nested object, not flat fields at the entity root). Keeps the schema clean and matches the standard's "Catalog" abstraction.
- **Q3 (which entities get the summary)**: only entities whose `catalog_repo` matches one of the four known conformant adopters. Other catalogs (e.g., `dea-catalog-ecosystem-platforms`, `dea-catalog-journey-touchpoints`) are not yet adopters; their entities show the existing "Catalog linkage" card but no "Catalog content" data.
- **Q4 (CI)**: the `opendeam-sync.yml` workflow already runs `generate_entity_graph.py` on every model pin bump; this PR adds the `CATALOG_SUMMARY_CACHE` env var pointing at a per-job cache directory so the consumer can run offline in CI. The consumer is tolerant: a failed fetch leaves `catalog_summary` absent (not a CI failure).

## What changes

### dea-metamodel

- **Added**: `.github/scripts/cross_repo_consumer/` (vendored copy of the consumer module from `dea-metaframework/tools/cross_repo_consumer/`).
- **Added**: `.github/scripts/catalog_summary_builder.py` (~140 lines): wraps the consumer; defines `build_catalog_summaries()` + `attach_catalog_summaries()`; lists the four adopters as a module-level tuple.
- **Modified**: `.github/scripts/generate_entity_graph.py`: imports the builder, calls `attach_catalog_summaries()` before writing `entity-graph.json`. The new `description` field documents the addition (CR-CATALOG-STRUCT-07b).
- **Modified**: `viewer/entity-graph.schema.json`: adds explicit `catalog_summary` property with full schema (entity_count, canonical, candidates, retired, research_files, latest_modified, metamodel_version, abbreviation, catalog_name, generated_at). The schema is strict enough to reject malformed entries.
- **Added**: `tests/cross_repo_consumer/test_catalog_summary_builder.py` (~150 lines): 7 tests covering offline path, schema completeness, attachment filtering, and graceful no-data behavior.
- **Modified**: `.github/workflows/opendeam-sync.yml`: set `CATALOG_SUMMARY_CACHE` to a per-job cache directory so the consumer runs offline.

### dea-web-viewer

- **Modified**: `src/types.ts`: add `CatalogSummary` interface and optional `catalog_summary?: CatalogSummary` field on `MetamodelEntity`.
- **Modified**: `src/data/syncedMetamodel.ts`: extend `EntityGraphEntity` interface with `catalog_summary` (raw from `dea-metamodel`'s JSON) and pass it through in the entity assembly.
- **Modified**: `src/components/EntityDrawer.tsx`: add a new "Catalog content" card that renders when `entity.catalog_summary` is present. Uses the existing `Database` icon (already imported).

## Verification

- `python -m pytest tests/cross_repo_consumer/test_catalog_summary_builder.py` returns `7 passed`.
- `npx tsc -p tsconfig.json --noEmit` exits 0 (no type errors).
- `python -c "import json, jsonschema; jsonschema.validate(json.load(open('viewer/entity-graph.json')), json.load(open('viewer/entity-graph.schema.json')))"` exits 0.
- Manual regeneration with a populated cache: `python .github/scripts/generate_entity_graph.py --model ...` with `CATALOG_SUMMARY_CACHE` set produces `viewer/entity-graph.json` with 5 entities carrying `catalog_summary` (one per known adopter: business-process, capability, business-service, solution-component, stakeholder).
- Dash sweep on new prose: clean.
- Secret scan: 0.
- `git diff --check`: clean.

## Sequencing

| Slice | Status |
|---|---|
| STRUCT-01 | Merged |
| STRUCT-06a + 06b | Merged |
| STRUCT-02..05 (four adopters) | Merged |
| STRUCT-07a (consumer module) | Merged (#19) |
| STRUCT-07b (viewer integration) | **This PR** |
| STRUCT-07c (AF smoke test) | next slice |

## Out of scope (STRUCT-07c)

The `dea-architecture-framework/` smoke test that verifies cataloged entities match the OpenDEAM model lands separately as STRUCT-07c. It uses the same consumer module but lives in `dea-architecture-framework/scripts/check_catalog_index_matches_model.py` rather than the viewer.