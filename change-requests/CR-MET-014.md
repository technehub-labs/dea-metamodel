# CR-MET-014: Org-Wide Entity Lifecycle Audit and Backfill

| Field | Value |
|---|---|
| **CR** | CR-MET-014 |
| **Title** | Org-wide entity lifecycle audit: backfill `lifecycle` to observed catalog realization |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-30 |
| **Depends on** | dea-catalog-information-assets PR #4 (CR-IA-CAT-04, landed); dea-catalog-information-classes PR #14 (CR-IC-CAT-10, landed) |
| **Blocks** | nothing |
| **Trigger** | Metamodel review (2026-10-29) found `dea:InformationClass` marked `lifecycle: planned` while its catalog is live (8 canonical records), and `dea:InformationAsset` marked `proposed` with no catalog at all. Pickaxe audit of history confirmed no commit has ever backfilled an entity lifecycle value; the field has been stale since inception. The repo owner directed an org-wide audit rather than an information-family-only fix. |

## 1. Background

`docs/semantics.md` (Entity status vs lifecycle) defines the entity-level `lifecycle` field as the maturity of the entity's catalog realization: `existing` (realization present), `scaffold` (hosting catalog exists, no canonical content), `proposed`/`planned` (no realization; planned adds approval). `tests/conformance/test_001_entities.py` enforces the closed set. Nothing verifies the values against the org's actual repositories: `detect_drift.py` covers ECF drift only, and `.github/scripts/validate_cross_repo.py` (which checks `catalog_repo` existence) is not wired into any workflow. Meanwhile the org has stood up and populated catalogs without the metamodel following: 45 repos are named as `catalog_repo` values; several are live with canonical content.

## 2. Objective

Make every entity's `lifecycle` value truthful against the observed GitHub state of its declared `catalog_repo`, using one mechanical rule set, in a single auditable backfill.

## 3. Audit method (2026-10-30)

For each distinct `catalog_repo` (45): repository existence via contents listing (with retries; single-flight flakes observed and excluded), then `CATALOG.yaml` presence, then `counts.canonical`. Classification:

| Observed state | Rule |
|---|---|
| Repo missing | keep current value (`planned`/`proposed`) |
| Repo exists, no `CATALOG.yaml` or `canonical == 0` | `scaffold` |
| Repo exists, `canonical > 0` | `existing` |

`proposed` entities whose repo exists move to `scaffold` on the reading that a stood-up hosting repo is the org-level creation decision (the capabilities U-2 framing); `status: normative` already places them in the governed inventory. Downgrades are out of scope (§7).

## 4. Decisions

| # | Decision |
|---|---|
| D1 | The backfill is upward-only: `proposed/planned/scaffold` may rise; `existing` is never lowered in this CR, even where observation contradicts it (three such cases are named in §7 as follow-up CRs). |
| D2 | `canonical > 0` in the hosting repo's `CATALOG.yaml` is the sole test for `existing`. |
| D3 | A repository's existence (any content state) is sufficient for `scaffold`. |
| D4 | `dea-catalog-information-assets` joins `KNOWN_CATALOG_REPOS` in `.github/scripts/catalog_summary_builder.py` so the viewer renders its catalog summary card (CR-CATALOG-STRUCT-07b mechanism). |

## 5. Changes (42 entity lifecycle values; the only semantic lines touched)

To `existing` (6): `dea:Actor` (3 canonical), `dea:BusinessObject` (74), `dea:InformationAsset` (7; catalog stood up and populated this week under CR-IA-CAT-01..04), `dea:InformationClass` (8), `dea:Role` (1), `dea:ValueStream` (111).

To `scaffold` (36): from `planned` (24): AIMLModel, API, ApplicationComponent, ArchitecturePattern, Blueprint, BusinessCapability (repo live, 32 candidates, 0 canonical post-reset), DataEntity, DataProduct, DigitalIdentity, Event, Guardrail, InfrastructureComponent, InformationSystemComponent, InformationSystemFunction, InformationSystemService, IntegrationComponent, IntegrationInterface, InvestmentInitiative, JourneyTouchpoint, PlatformService, StrategicObjective, SystemFunction, Technology, Tenet; from `proposed` (12): ChangeInitiative, Concept, Control, EcosystemPlatform, Experiment, ModelDeployment, ModelFeedbackSignal, Regulation, Risk, Signal, Skill, TechnologyRadarEntry.

Unchanged as accurate: `dea:BusinessProcess`, `dea:OrganizationalUnit`, `dea:Stakeholder` (`scaffold`, repos exist without canonical content); `dea:FinancialResource`, `dea:IntangibleResource`, `dea:KnowledgeAsset`, `dea:PhysicalResource` (`proposed`, repos do not exist); entities without `catalog_repo`.

Regenerated in-PR: `metamodel/registry/entities.yaml`, `specification/semantic-inventory.yaml` (via `generate_registry.py` / `generate_specification.py`). All 369 conformance tests pass; the artifact-drift ratchet stays at zero findings; the authorship gate passes.

## 6. Findings named for follow-up CRs (not fixed here)

1. **Stale `existing` (3 entities):** `dea:BusinessService` and `dea:SolutionComponent` point at `dea-catalog-digital-business-service-factory` (18 candidates, 0 canonical); `dea:PerformanceMetric` points at `dea-catalog-metrics` (index present but empty). Each needs a downgrade or a repoint decision.
2. **`catalog_repo` naming drift (2):** the metamodel points at `dea-catalog-processes` while the org's processes work repo is `dea-catalog-business-processes`; likewise `dea-catalog-digital-business-service-factory` vs `dea-catalog-business-services`. Repointing is a semantic change requiring per-entity verification and is out of scope.
3. **No CI wiring:** `validate_cross_repo.py` (catalog_repo existence + C1) is not wired into any workflow; this audit was manual. Wiring it (network-gated, non-blocking or scheduled) would prevent recurrence.
4. **Viewer lag:** `viewer/entity-graph.json` follows the upstream OpenDEAM pin, not this file; the graph's entity statuses catch up at the next pin bump.

## 7. NOT-list

1. No entity definitions, relationships, artifacts declarations, or `catalog_repo` pointers change.
2. No `lifecycle` value is lowered (D1).
3. No viewer/Puml/SVG regeneration (upstream-pinned; §6.4).
4. No new lifecycle vocabulary values (the test_001 closed set stands; the DRIFT-3 vocabulary alignment remains parked).
5. No TTL changes (DRIFT-6 stands; the information-family TTL gaps named in the 2026-10-29 review remain a separate CR).

## 8. Definition of Done

1. `pytest tests/conformance/` green; `validate_artifacts.py --report` zero findings; authorship gate conformant.
2. Registry and specification regenerated with no diff beyond the lifecycle values.
3. CHANGELOG `[Unreleased]` entry and programme-index row landed in this PR.

## 9. References

- dea-catalog-information-assets: CR-IA-CAT-01..04 (repository, PRs #1-#4).
- dea-catalog-information-classes: CR-IC-CAT-10 (first mapped-from crosswalks, PR #14).
- `docs/semantics.md` Entity status vs lifecycle; `tests/conformance/test_001_entities.py`.
