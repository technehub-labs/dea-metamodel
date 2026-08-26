# Legacy Maturity Catalog Migration Plan

**CR-AM-11 Phase 6, §26.** Plans the migration from
`Assessment-Models/dea-catalog-maturity-models` (v1-alpha, "Legacy"
classification per the org's §26 catalogue) to the federated
ecosystem's v2-canonical maturity scheme. The fold-v2-in vs
freeze-as-legacy decision itself is **deferred to CR-AM-01 Release 1**
(per §26 closing-action record); this document is the *migration plan
shape*, not the migration execution.

## Why this document exists

The legacy catalog carries five v1-alpha maturity models (Operations,
Modernization, Technology, Services-Delivery, EA-Capability). v1-alpha
predates the v2 maturity architecture (non-linear bands Emergent /
Structured / Systematic / Adaptive / Self-Optimising, superlinear effort
multipliers) and is therefore not a target consumer for the new
ecosystem's contract suite — its scale contract predates CR-AM-09
§17's topology/function independence.

Two paths are possible once CR-AM-01 Release 1 decides:

1. **Fold v2 in** — port each v1-alpha model to v2-canonical using the
   maturity-v2 migration plan (`assessment-models/maturity/governance/migration.md`).
   The legacy catalog's repo is archived; its models become v2 editions
   under their canonical owners (Operations Lead, Technology Lead, etc.).
2. **Freeze as legacy** — keep the legacy catalog unchanged and recorded
   in `assessment-registry` with status `legacy`. New consumers must use
   the v2 editions from the federated ecosystem.

This document captures the migration plan for **both paths** so the
release-1 decision is a one-line commit rather than a re-derivation.

## Scope of the legacy catalog

| Model | Status | Plan A (fold v2) | Plan B (freeze legacy) |
|---|---|---|---|
| Operations | v1-alpha | Re-author as v2-canonical under Operations Lead; archive legacy repo at the v2 promotion commit | Register with `status: legacy`, `superseded_by: dea:scale-operations-v2` |
| Modernization | v1-alpha | Same shape as Operations | Same shape as Operations |
| Technology | v1-alpha | Same shape | Same shape |
| Services-Delivery | v1-alpha | Same shape | Same shape |
| EA-Capability | v2-beta (in `dea-metamodel`) | **Already v2-canonical** — no migration; reference instance published in Phase 3 | Reference instance is the canonical entry |

## What already exists (Phase 0–5 footprint)

- **Phase 0** classified `dea-catalog-maturity-models` as **Legacy**
  in the org `assessment-models` profile README.
- **Phase 1** registered the legacy catalog as a pinned metadata-only
  record in `Assessment-Models/assessment-registry` (asset id
  `dea-catalog-maturity-models`, pinned to commit
  `fa2f9d57b75227a65d052fa13f426171c1cd295c`).
- **Phase 3** formalised the v2-canonical maturity scheme (Bands v2 +
  effort-multiplier semantics) and published the OpenDEA EA reference
  instance demonstrating it.
- **Phase 4** demonstrated the federated ecosystem end-to-end on a
  Digital Transformation composite model (consumer-side reference
  architecture).
- **Phase 5** published four composite dimensions back to the
  maturity-component registry, completing the round-trip.

## Release-1 decision checklist

When CR-AM-01 Release 1 begins, the decision needs:

- [ ] Owner sign-off for each of the five models (who carries the
      v2 port if Plan A is chosen).
- [ ] A confirmed consumer list for the legacy catalog (anyone using
      v1-alpha must migrate; Phase 5 component registry entries are
      the canonical replacement).
- [ ] A migration PR template (port-v1-to-v2 checklist) per model.
- [ ] An archival commit for the legacy catalog under Plan A, or a
      `superseded_by` registry field under Plan B.

## What this Phase 6 PR ships (the migration plan shape)

1. **`governance/legacy-migration-plan.md`** — this document.
2. **`Assessment-Models/dea-catalog-maturity-models`** — added a
   `MIGRATION.md` supersession note pointing to this plan; status
   badge updated to `legacy`.
3. **`Assessment-Models/assessment-registry`** — the existing legacy
   catalog record gains a `superseded_by` field pointing at the v2
   canonical scheme (`dea:maturity-bands-v2 v1.0.0`).
4. **`assessment-models/contracts/contract-suite.yaml`** — Annex A
   note recording that legacy assets are exempt from the §16 contract
   suite by design; consumers must check `status: legacy` and route
   to the canonical replacement.

Spec/metamodel stay **1.0.0**. No model content changes.