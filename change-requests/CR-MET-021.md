# CR-MET-021: Stakeholder Lifecycle Promotion

| Field | Value |
|---|---|
| **CR** | CR-MET-021 |
| **Title** | Stakeholder lifecycle promotion: scaffold → existing (first canonical tranche landed) |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-08 |
| **Depends on** | CR-MET-014 (lifecycle rules); CR-MET-017 (the promotion precedent); `dea-catalog-stakeholders` CR-CATALOG-STRUCT-12/13/14 (foundation modernization + population contract + first canonical tranche, PRs #15/#16/#17) |
| **Trigger** | The Stakeholders catalog landed its first canonical tranche on 2026-11-08: 11 canonical records (3 organisation/governance/community capacities + 8 regulators one-to-one with the regulations catalog's active records), all gates green, CI five-for-five on the tranche PR. CR-MET-014's `scaffold` value was honest at audit time (0 entities) and is now stale by the same rule that promoted BusinessCapability in CR-MET-017. |

## 1. Change

`dea:Stakeholder` lifecycle `scaffold` → `existing`, per the CR-MET-014 rules applied to the observed state (11 canonical records in `dea-catalog-stakeholders`, verified by its regenerated `CATALOG.yaml` under the re-vendored, hyphen-form-correct regenerator). This is the CR-MET-017 precedent applied to the next catalog to cross the populated threshold: forward transition, PR-only (ADR-0002 D5 ladder, root-model side).

Promotion chain fully cited: stakeholders CR-CATALOG-STRUCT-14 (the tranche, PR #17) → this CR. Companion root-model promotion: CR-AR-FMWK-16 (`model/opendeam-model.yaml` status `scaffold` → `existing`, same observation).

## 2. Regenerated

`metamodel/registry/entities.yaml`, `metamodel/dea-metamodel.yaml`, `specification/semantic-inventory.yaml` (one lifecycle value, three mirrors). Conformance suite green.

## 3. NOT-list

1. No other entity values change.
2. No entity definitions, artifacts, schema, or pointers change (the metamodel v1.0.0 Stakeholder schema is already the normative source the catalog projects).
3. No VERSION bump (CR-MET-017 precedent: lifecycle values are governance metadata, not schema surface).

## 4. Lesson carried

Same as CR-MET-017 §4: lifecycle values are only as truthful as the catalog indexes they read — and the Stakeholders index needed its own foundation pass (the vendored regenerator carried the same hyphen-form infer_state defect family; fixed in CR-CATALOG-STRUCT-12 before the first admission) before its count could be trusted.
