# CR-MM-01 — Maturity v2 Phase B: beta maturity model YAML files

| Field | Value |
|-------|-------|
| **CR** | CR-MM-01 (CR Maturity Model — first child of CR-AM-01 umbrella) |
| **Title** | Maturity v2 Phase B: author `v2-beta/` maturity model YAML files for the five canonical maturity domains, with `legacy_name` aliases |
| **Status** | Proposed |
| **Date** | 2026-08-21 |
| **Author** | Coder (for eaojnr) |
| **Version** | additive (no canonical `VERSION` bump — sub-tree is `2.0.0-beta` of its own scope; v1-alpha stays canonical until Phase D) |
| **Depends on** | CR-AM-01 (umbrella), CR-014 (Phase A landed the bands + legacy-name map), CR-015 (assessment-profile ↔ sub-tree cross-reference just landed) |
| **Scope** | A `v2-beta/` directory inside `assessment-models/maturity/` containing one YAML per canonical maturity domain (EA Capability, Modernization, Technology, Operations, Services Delivery). Each `v2-beta/<filename>` mirrors the corresponding `v1-alpha/<filename>` from the archived `Assessment-Models/dea-catalog-maturity-models` repo, preserving every `characteristic`, `exit_criterion`, and `evidence` byte-identically, while rewriting the four scoring fields per level and adding a new `effort_multiplier`. Plus a CI validator that asserts v2-beta semantics (canonical-band alignment, legacy_name round-trip, content-field presence). Plus a `change-requests/CR-MM-01.md` file, a maturity README §6 entry, a CHANGELOG `[Unreleased]` note. |
| **Out of scope** | Consumer support (Phase C — `dea-cli --scoring v2`, `dea-web-viewer` v2 rendering behind a feature flag); v1 deprecation (Phase D); pilot migration of any specific assessment instrument; new schemas or governance policy; any change to `maturity-bands-v2.yaml` or `v2-to-v1-legacy-name-map.yaml` (Phase A is frozen); CR-015 (just shipped). |

---

## 1. Context

Phase A of the maturity-v2 migration (CR-014) published the v2 registry artefacts — `maturity-bands-v2.yaml`, `v2-to-v1-legacy-name-map.yaml`, and `examples/effort-adjusted-value.yaml` — as advisory siblings to v1. Per `governance/migration.md`, Phase B is:

> v2 maturity model YAMLs in the assessment-models sub-tree gain `legacy_name` aliases and `score_range` matches v2 bands. Consumers may preview v2 behind a flag.

This CR is exactly that. The five canonical maturity domains are the same five that CR-AM-01 §2 enumerates: EA Capability, Modernization, Technology, Operations, Services Delivery.

## 2. Why now

1. CR-014 explicitly listed Phase B as "future, gated on consumer signal". The CR-015 cross-link just shipped improves the discoverability of the v2 work, which makes consumer signal more likely. Shipping Phase B **proactively** before any specific consumer asks for it removes the bespoke-cost-per-consumer-of-v2.
2. The five v1-alpha originals live in the archived `Assessment-Models/dea-catalog-maturity-models` repo (frozen / read-only). Without a v2 mirror inside the canonical sub-tree, every consumer that wants to read v2 needs to either pin the archived repo or hand-edit a v1 file. Either is fragile.
3. Phase B is mechanically the lowest-risk slice of the v2 rollout. It is **purely additive**: no v1 file changes; no governance change; no consumer change. Only a new directory and five new files plus a CI validator.

## 3. Changes

### 3.1 Five new files under `assessment-models/maturity/v2-beta/`

| File | Domain | Mirrors v1-alpha |
|------|--------|-----------------|
| `ea-capability.yaml` | enterprise-architecture | yes |
| `modernization.yaml` | modernization | yes |
| `technology.yaml` | technology | yes |
| `operations.yaml` | operations | yes |
| `services-delivery.yaml` | services-delivery | yes |

Each file:

- Has the same `id`, `name` (suffixed with `(v2-beta)`), `domain`, `description` (extended with a v2-vs-v1 explanation paragraph), and `owner` as its v1-alpha twin.
- Bumps `version` from `1.0.0-alpha` to `2.0.0-beta` and `metamodel_version` from `^0.1.0` to `^1.0.0` (the canonical metamodel is now 1.0.0 after CR-008).
- Adds v2-only top-level metadata: `status: beta`, `score_scheme: dea-maturity-v2`, `band_reference: ../maturity-bands-v2.yaml`, `legacy_model: ../v2-to-v1-legacy-name-map.yaml`.
- Rewrites per-level scoring fields:

  | v1 field | v2 field |
  |----------|----------|
  | `id: level-1-ad-hoc` | `id: level-1-emergent` |
  | `name: Ad Hoc` | `name: Emergent` |
  | `score_range: [0, 25]` | `score_range: [0, 20]` |
  | (none) | `legacy_name: Ad Hoc` |
  | (none) | `effort_multiplier: 1.0` |

  Same transformation for L2 (Defined → Structured, 1.0× → 1.5×), L3 (Managed → Systematic, 2.5×), L4 (Quantitatively Managed → Adaptive, 4.0×), L5 (Optimising → Self-Optimising, 6.0×). The new `effort_multiplier` and `score_range` values are sourced **authoritatively** from `maturity-bands-v2.yaml`; the new `id`/`name`/`legacy_name` values are sourced from `v2-to-v1-legacy-name-map.yaml`. The CI validator asserts this in CI.
- Preserves every `summary`, `characteristics`, `exit_criteria`, `evidence` field **byte-identically** from v1. Phase B is name + bands + scoring only.
- Adds ONE new relationship: `scored-by-v2-bands → dea:maturity-bands-v2`.
- Adds `v2-beta` to the `tags:` list.

### 3.2 CI validator (new job)

A new CI job `validate-v2-beta-models` in `.github/workflows/ci-assessment-models.yml`:

- Extends `validate-yaml`'s glob to cover `maturity/v2-beta/*.yaml`.
- Validates every v2-beta file against this contract:
  1. There are exactly 5 files.
  2. Domains cover all five canonical (enterprise-architecture, modernization, technology, operations, services-delivery).
  3. `status: beta`, `score_scheme: dea-maturity-v2`, `band_reference` ends with `maturity-bands-v2.yaml`.
  4. Each level's `id` is in the canonical v2 band registry.
  5. Each level's `name`, `score_range`, and `effort_multiplier` exactly match the canonical band.
  6. Each level's `legacy_name` resolves correctly via the legacy-name map (round-trip).
  7. Each level has non-empty `summary`, `characteristics`, `exit_criteria`, `evidence`.
- Implemented in inline Python in the existing CI workflow (same pattern as `validate-maturity-v2-arithmetic`); no new dependency.

### 3.3 Documentation

- `change-requests/CR-MM-01.md` (this file).
- `change-requests/README.md` — new row referencing CR-MM-01.
- `CHANGELOG.md` — new `[Unreleased]` entry under `CR-MM-01:` heading.
- `assessment-models/maturity/README.md` — new §6 "v2-beta maturity models" section linking to the directory and listing Phase B exit criterion.
- `assessment-models/maturity/governance/migration.md` — Phase B status updated from "future" to "✅ this PR".
- `assessment-models/change-requests/cr-index.md` — add CR-MM-01 to the sub-tree CR index (the canonical cross-reference for everything inside `assessment-models/`).

## 4. Out of scope (re-stated)

- **Phase C — consumer support.** `dea-cli --scoring v2` flag, `dea-web-viewer` v2 rendering behind a feature flag, consumer mirror in `dea-catalog-assessment-tools` (archived). Lives in `technehub-labs/dea-cli`, `technehub-labs/dea-web-viewer`. A separate CR.
- **Phase D — promotion.** v1 deprecation. Requires one full assessment cycle on v2. A separate CR.
- **Pilot migration** of any specific instrument (`dea-assessment-technology`, etc.) to the canonical assessment sub-metamodel. Per CR-AM-01 §3, depends on the catalog being reachable; parked separately.
- **Any change** to `maturity-bands-v2.yaml`, `v2-to-v1-legacy-name-map.yaml`, `examples/effort-adjusted-value.yaml`, or `governance/migration.md`. Phase A is frozen.
- **Schema or governance policy changes** in the assessment sub-metamodel. None proposed.
- **Profile content edits.** None proposed.

## 5. Acceptance criteria

1. ✅ Five files added at `assessment-models/maturity/v2-beta/{ea-capability,modernization,technology,operations,services-delivery}.yaml`.
2. ✅ Per-level content (`summary`, `characteristics`, `exit_criteria`, `evidence`) byte-identical to the v1-alpha originals in the archived `Assessment-Models/dea-catalog-maturity-models` repo.
3. ✅ Each level carries `legacy_name`, new `id`, new `name`, v2 `score_range`, and `effort_multiplier` sourced from the canonical registries.
4. ✅ New CI job `validate-v2-beta-models` validates every level against the contract in §3.2.
5. ✅ Existing CI green (no regression in any of the 7 CR-014 jobs).
6. ✅ `change-requests/CR-MM-01.md`, `change-requests/README.md` row, `CHANGELOG.md` `[Unreleased]` entry, maturity README §6, governance migration Phase B update, sub-tree CR index row.

## 6. Exit criterion towards Phase C

Per `governance/migration.md` Phase B exit criterion: "At least one assessment cycle runs end-to-end against v2-beta files. Tooling confirms `value_realised(score)` produces stable values across runs (acceptance_tolerance met)."

This PR ships the YAMLs themselves. The end-to-end assessment cycle is in Phase C scope and is out of scope here; Phase C will need a consumer that reads v2-beta. PR-MM-02 (queued separately, parked) will then run the cycle.

## 7. References

- **CR-AM-01** (umbrella): https://github.com/Assessment-Models/dea-catalog-assessment-tools/blob/main/change-requests/CR-AM-01.md
- **CR-014** (Phase A landing): [CR-014.md](CR-014.md)
- **CR-015** (just shipped — assessment profile cross-link): [CR-015.md](CR-015.md)
- **CR-AM-01 supplement** (assessment sub-metamodel v1): the abstract model that v2-beta maturity models consume
- **v2 maturity bands**: [../assessment-models/maturity/maturity-bands-v2.yaml](../assessment-models/maturity/maturity-bands-v2.yaml)
- **Legacy-name map**: [../assessment-models/maturity/v2-to-v1-legacy-name-map.yaml](../assessment-models/maturity/v2-to-v1-legacy-name-map.yaml)
- **Worked example**: [../assessment-models/maturity/examples/effort-adjusted-value.yaml](../assessment-models/maturity/examples/effort-adjusted-value.yaml)
- **Migration governance (Phase B spec)**: [../assessment-models/maturity/governance/migration.md](../assessment-models/maturity/governance/migration.md)
- **Archived v1-alpha originals**: https://github.com/Assessment-Models/dea-catalog-maturity-models/tree/main/maturity-models/v1-alpha
- **Original proposal (historical)**: https://github.com/Assessment-Models/dea-catalog-maturity-models/pull/1

## 8. Sub-tree landing

This CR lands as `change-requests/CR-MM-01.md` inside the `assessment-models/` sub-tree (sibling to CR-AM-01 supplement and CR-014). The umbrella → child hierarchy is:

```
CR-AM-01 (umbrella)
├── CR-014   (Phase A — advisory bands; single-authority migration; merged 2026-08-20)
├── CR-015   (assessment profile cross-link; merged 2026-08-21)
└── CR-MM-01 (Phase B — v2-beta model files; this CR)
```

`assessment-models/change-requests/cr-index.md` lists all three sub-tree CRs.
