# CR-MET-015: Wave-1 Boundary Lifecycle Sync

| Field | Value |
|---|---|
| **CR** | CR-MET-015 |
| **Title** | Wave-1 boundary: lifecycle corrections for the six Wave-1-populated entities |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-02 |
| **Depends on** | CR-MET-014 (audit + rules); the Wave-1 catalog populations (CR-DE-CAT-02, CR-CTL-CAT-02, CR-REG-CAT-02, CR-KA-CAT-02) |
| **Trigger** | Org-wide catalog advancement programme, Wave 1 boundary. Six entities' catalogs populated or were observed populated since the CR-MET-014 audit; the CR-MET-014 rules (canonical > 0 -> existing) apply. |

## 1. Changes

| Entity | From | To | Observation |
|---|---|---|---|
| dea:DataEntity | scaffold | existing | dea-catalog-data-entities: 9 canonical (CR-DE-CAT-02) |
| dea:Control | scaffold | existing | dea-catalog-controls: 20 canonical (CR-CTL-CAT-02) |
| dea:Regulation | scaffold | existing | dea-catalog-regulations: 8 canonical (CR-REG-CAT-02) |
| dea:KnowledgeAsset | proposed | existing | dea-catalog-knowledge-assets created + 8 canonical (CR-KA-CAT-01/02) |
| dea:Concept | scaffold | existing | dea-catalog-concepts: 29 canonical records observed (bespoke CR-CON series; the CR-MET-014 audit under-read it as skeleton because the repo predates the CATALOG.yaml index discipline) |
| dea:BusinessProcess | scaffold | existing | dea-catalog-processes: 3,722 canonical (detected by the CR-014 reconciler 2026-11-02; the repo is the populated processes home the audit snapshot missed) |

Also: `KNOWN_CATALOG_REPOS` extended with dea-catalog-data-entities, dea-catalog-controls, dea-catalog-regulations, dea-catalog-knowledge-assets (viewer catalog cards). dea-catalog-concepts joins when it adopts the CATALOG.yaml index (named follow-up, its repo).

## 2. Regenerated

metamodel/registry/*, specification/* (lifecycle values only).

## 3. NOT-list

1. No entity definitions, artifacts, or catalog_repo pointers change.
2. The processes/business-processes canonical-home question stays a named follow-up (CR-MET-014 finding 2).
3. Concepts' layout/index adoption is its repo's decision.
