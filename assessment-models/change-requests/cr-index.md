# Change Requests — `dea-metamodel`

This index tracks every Change Request (CR) that has landed in this repository.

CRs follow the **land-as-authored** convention: the file in `change-requests/` is byte-identical to the originating attachment (md5-verified) where the full CR lives here.

| CR | Title | Type | Status | Source |
|----|-------|------|--------|--------|
| [CR-AM-01-supplement-metamodel-v1](CR-AM-01-supplement-metamodel-v1.md) | OpenDEA Assessment Metamodel v1 — PlantUML, JSON Schemas, vocabulary, governance | Reference | Accepted | This repo (verbatim, md5 `c0f086be...`) |
| CR-014 (cross-ref → [../../../change-requests/CR-014.md](../../../change-requests/CR-014.md)) | Assessment Metamodel v1 + Maturity Scoring v2 — single-authority migration into this sub-tree | Implementation | Implemented | Parent `change-requests/CR-014.md` (merge commit `62beb35`) |
| CR-015 (cross-ref → [../../../change-requests/CR-015.md](../../../change-requests/CR-015.md)) | Assessment-Profile ↔ Assessment-Sub-Tree Cross-Reference | Documentation | Implemented | Parent `change-requests/CR-015.md` (merge commit `36d7452`) |
| CR-MM-01 (cross-ref → [../../../change-requests/CR-MM-01.md](../../../change-requests/CR-MM-01.md)) | Maturity v2 Phase B — beta maturity model files (`v2-beta/`) | Implementation | Proposed | Parent `change-requests/CR-MM-01.md` (this index's CR row) |

---

## CR-AM-01 supplement quick links

| Document | Purpose |
|----------|---------|
| [`CR-AM-01-supplement-metamodel-v1.md`](CR-AM-01-supplement-metamodel-v1.md) | The supplement (1430 lines, 16 sections) — PlantUML verbatim, three core JSON Schemas verbatim, four canonical YAML examples |
| [`../model/assessment-metamodel.puml`](../model/assessment-metamodel.puml) | PlantUML source from §2 |
| [`../schemas/`](../schemas/) | All 11 JSON Schemas |
| [`../vocabulary/`](../vocabulary/) | Controlled vocabularies |
| [`../examples/`](../examples/) | Canonical YAML examples |
| [`../governance/`](../governance/) | Versioning, compatibility, lifecycle policy docs |

---

## Convention notes

- **Naming**: `CR-<series>-NN[-suffix].md` where `<series>` is a short tag.
- **Status values**: `Proposed` → `Accepted` → `Implemented` → `Superseded`.
- **Reference CRs** document design intent; **Implementation CRs** land code or schema changes.