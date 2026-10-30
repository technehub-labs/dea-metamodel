# CR-MET-017: BusinessCapability Lifecycle Correction

| Field | Value |
|---|---|
| **CR** | CR-MET-017 |
| **Title** | BusinessCapability lifecycle correction: scaffold → existing (index-count defect upstream) |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-02 |
| **Depends on** | CR-MET-014 (audit rules); CR-DEA-BC-61 (the correction that makes the count truthful); dea-metaframework PR #58 (the infer_state fix) |
| **Trigger** | CR-MET-014 recorded `dea:BusinessCapability` as `scaffold` on the strength of a 0-canonical index count. CR-DEA-BC-61 established that the count was wrong: the capabilities catalog's vendored regenerator misclassified all 29 canonical records as candidates since the mv1 id migration (colon-form-only filename lookup vs hyphen-form files). The catalog has been populated throughout. |

## 1. Change

`dea:BusinessCapability` lifecycle `scaffold` → `existing`, per the CR-MET-014 rules applied to the corrected observation (29 canonical records in `dea-catalog-business-capabilities`, verified by the regenerated index under the fixed regenerator).

This reverses this repository's own CR-MET-014 value; the error was an input defect (a toolchain count), not a rule defect. The correction chain is fully cited: metaframework PR #58 (fix + regression test) → capabilities CR-DEA-BC-61 (re-vendor + truthful index) → this CR.

## 2. Regenerated

`metamodel/registry/*`, `specification/*` (one lifecycle value). 369 conformance tests green.

## 3. NOT-list

1. No other entity values change.
2. No entity definitions, artifacts, or pointers change.
3. The three genuine capability candidates remain candidates (their catalog's own record).

## 4. Lesson recorded

Lifecycle backfills in CR-MET-014/015/016 are only as truthful as the catalog indexes they read. The CR-014 reconciler (dea-governance) reads the same indexes; its R3 rule now benefits from the fixed regenerator, and the governance register records the corrected state.
