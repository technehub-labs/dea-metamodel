# CR-MET-018: ECF Identifier Mirror and Detector Truthfulness

| Field | Value |
|---|---|
| **CR** | CR-MET-018 |
| **Title** | ECF identifier mirror test + drift-detector truthfulness fixes (closes the dual-source-of-truth defect) |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-31 |
| **Depends on** | CR-ECF-012 (dea-metaframework PR #59: the DOMAIN_ID table is now normative in the metaframework) |
| **Trigger** | A capability-admission PR failed the consumer drift gate on identifier form, exposing that `detect_drift.py`'s `DOMAIN_ID` (And-stripped, CI-authoritative) and the metaframework's `coordinate_identifier()` (And-kept generic camelization) were contradictory conventions with no bridging check anywhere. |

## 1. Changes

1. **`tests/conformance/test_035_ecf_identifier_mirror.py`** (new): for all 49 coordinates, asserts the metaframework's `coordinate_identifier()` (normative per CR-ECF-012) equals `ecf:{DOMAIN_ID[d]}.{STAGE_ID[s]}`; plus a full-49-space equality test and a DOMAIN_ID table-equality test. Skips when `ECF_FRAMEWORK_ROOT` is absent (offline runs stay green); `ecf-conformance.yml` already exports it after cloning, so the check is enforced online. If either repo changes its identifier convention without the other, a CI fails.
2. **`scripts/detect_drift.py` truthfulness fixes:**
   - `DEPRECATED_DOMAIN_ALIASES`/`DEPRECATED_DOMAIN_ID_ALIASES` gain the Domain-3 forms (`PeopleAndOrganization`/`peopleAndOrganization`) that the section's own comment claims to mirror.
   - The entity scan excludes `research/`, `candidates/`, `retired/` subtrees (the capabilities `check_ecf_conformance.py` precedent; previously latent over-scan of non-canonical state files).
   - `DEFAULT_ROOTS` names the real processes repo (`dea-catalog-business-processes`).
   - Header comment updated: the map is normative per CR-ECF-012 with the mirror test as the drift alarm.

## 2. Census disposition (what this CR does and does not repair)

The capabilities catalog is clean (verified: 0 hard, 0 soft against the detector). The processes catalog carries 11 entity files + reconciliation/script forms that would hard-fail once scanned; its mechanical repair is its own CR (cites this CR and CR-ECF-012 as the reconciled authority). Named follow-ups, not fixed here: stale pre-CR-ECF-006 coordinate ids in `conformance/matrix.yaml`; the consumer workflows' floating `--depth 1 main` pins.

## 3. Acceptance criteria

1. Mirror test passes with `ECF_FRAMEWORK_ROOT` set (9 cases) and skips without it.
2. `pytest tests/conformance/` green (369 + skips).
3. `detect_drift.py` against the capabilities root: 0 hard, 0 soft.

## 4. NOT-list

1. No DOMAIN_ID value changes (the map is the ecosystem convention; CR-ECF-012 adopted it, this CR mirrors it).
2. No catalog data repairs in this repo.
3. No workflow pin discipline changes (follow-up).
