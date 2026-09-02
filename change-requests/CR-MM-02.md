# CR-MM-02: Capability entity schema hygiene (feedback from dea-catalog-business-capabilities)

| Field | Value |
|-------|-------|
| **CR** | CR-MM-02 |
| **Title** | Reconcile `schemas/entities/capability.json` with ADR-015: drop the deprecated `capability_type` requirement, resolve the undefined required `maturity_level`, and consider a Business Capability specialization schema |
| **Status** | Proposed |
| **Date** | 2026-09-01 |
| **Author** | Coder (for eaojnr) |
| **Version** | Schema patch; version handling deferred to metamodel governance (the schema change removes a requirement, which is breaking for strict consumers) |
| **Depends on** | ADR-015 (capability classification reconciliation) |
| **Scope** | `schemas/entities/capability.json` only; optionally a new `schemas/entities/business-capability.json`. No metamodel semantics change; no consumer change. |
| **Out of scope** | Any other entity schema; the maturity model programme (CR-AM-01 chain); catalog-side changes (dea-catalog-business-capabilities already reconciles catalog-side via CR-DEA-BC-03). |

## 1. Context

While landing CR-DEA-BC-03 (catalog schema + CI reconciliation) in dea-catalog-business-capabilities, the capability entity schema was read closely against ADR-015. Three findings were recorded as U1-U3 in the landed CR and are reported here per that CR's commitment ("reported upstream through a dea-metamodel CR").

## 2. Findings

- **U1: `capability_type` is required and deprecated simultaneously.** `schemas/entities/capability.json` lists `capability_type` in `required`, while its property description marks it deprecated by ADR-015 ("the `kind` string carries the equivalent information"). The capability vocabulary entry (`metamodel/vocabularies/classifications.yaml`) retains the governed enum for backwards compatibility. Effect: every conforming instance must carry a field the architecture has abandoned, and every catalog that omits it (per ADR-015's intent) fails strict upstream validation.
- **U2: `maturity_level` is required but never defined.** `capability.json` requires `maturity_level`, yet no property definition exists in the schema and no governed vocabulary exists in `metamodel/vocabularies/classifications.yaml` (maturity is governed only for ArchitecturePattern). Effect: a required field with no specified type, enum, or semantics; consumers must invent values, which defeats governance.
- **U3: no specialization schema for Business Capability.** ADR-015 settles kind-by-specialization (`dea:BusinessCapability`), and the only catalog consuming capability records (dea-catalog-business-capabilities) fixes `type: BusinessCapability`. Upstream, `capability.json` keeps `type: const "Capability"`, so a strictly upstream-valid Business Capability instance is impossible. The catalog narrows the const catalog-side; that works, but the specialization deserves an upstream home.

## 3. Changes

1. Remove `capability_type` from `required` in `schemas/entities/capability.json`; keep the property (deprecated) for backwards compatibility.
2. Remove `maturity_level` from `required` in `schemas/entities/capability.json`. If a capability maturity concept is wanted upstream, route it through the assessment-models programme (CR-AM-01 chain), where maturity semantics are owned; do not invent a governed vocabulary inside this schema.
3. Add `schemas/entities/business-capability.json`: the specialization schema, `type: const "BusinessCapability"`, otherwise mirroring `capability.json`. Optional within this CR; if governance prefers, the catalog-side narrowing stands and this item defers.

## 4. Acceptance criteria

1. A Business Capability instance without `capability_type` validates against `capability.json`.
2. No required field lacks a property definition.
3. If item 3 is taken: a Business Capability instance validates against `business-capability.json` with `type: BusinessCapability`.
4. Existing v1 instances carrying `capability_type` still validate (property retained, deprecated).

## 5. References

ADR-015 (capability classification reconciliation); dea-catalog-business-capabilities CR-DEA-BC-03 (U1-U3 findings), CR-DEA-BC-01A (record shape decision); `metamodel/vocabularies/classifications.yaml`.
