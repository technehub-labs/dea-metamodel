# Change Requests — `dea-metamodel`

This index tracks every Change Request (CR) that has landed in this repository.

CRs follow the **land-as-authored** convention: the file in `change-requests/` is byte-identical to the originating attachment (md5-verified) where the full CR lives here.

| CR | Title | Type | Status | Source |
|----|-------|------|--------|--------|
| [CR-AM-01-supplement-metamodel-v1](CR-AM-01-supplement-metamodel-v1.md) | OpenDEA Assessment Metamodel v1 — PlantUML, JSON Schemas, vocabulary, governance | Reference | Accepted | This repo (verbatim, md5 `c0f086be...`) |

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