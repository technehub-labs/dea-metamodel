# Maturity Scoring v2 — Migration Governance

Additive migration only. No existing v1 file is modified. v2 lands as a sibling.

## Phase A — Registry advisory (current phase)

**Goal:** Publish v2 bands + legacy-name map as advisory artefacts. v1 stays canonical.

**Lands:**
- `maturity/maturity-bands-v2.yaml`
- `maturity/v2-to-v1-legacy-name-map.yaml`
- `maturity/examples/effort-adjusted-value.yaml`
- `maturity/README.md` (this sub-tree's entry point)
- `maturity/governance/migration.md` (this file)

**Status:** `status: beta` on every v2 YAML.

**What consumers see:** nothing changes for them. v1 instruments, scoring rubrics, and radar charts behave exactly as before. v2 is documentation-only at this point.

**Exit criterion for Phase B:**
- At least one consumer team (dea-cli, dea-web-viewer, or an Assessment-Models instrument) signals intent to read v2 bands.
- Worked example reproduced by hand or by a unit test.

## Phase B — Beta files + consumer preview

**Goal:** v2 maturity model YAMLs in the assessment-models sub-tree gain `legacy_name` aliases and `score_range` matches v2 bands. Consumers may preview v2 behind a flag.

**Lands:**
- A `v2-beta/` directory with one YAML per maturity domain (EA Capability, Modernization, Technology, Operations, Services Delivery), mirroring `maturity-models/v1-alpha/*.yaml` but with v2 ids + ranges.
- Each v2 file carries `legacy_name` on every level for cross-resolution.

**Status:** `status: beta` on every v2-beta file.

**Exit criterion for Phase C:**
- At least one assessment cycle runs end-to-end against v2-beta files.
- Tooling confirms `value_realised(score)` produces stable values across runs (acceptance_tolerance met).

## Phase C — Consumer support

**Goal:** Consumers gain native v2 support behind a feature flag. v1 still canonical.

**Lands (in other repos, not this one):**
- `technehub-labs/dea-cli`: `--scoring v2` flag on `dea maturity score`; reports both v1 and v2 mappings during transition.
- `technehub-labs/dea-web-viewer`: feature flag rendering v2 bands alongside v1 bands.
- `Assessment-Models/dea-catalog-assessment-tools` (archived, mirrored locally): mapping tables updated.

**Exit criterion for Phase D:**
- At least one full assessment cycle completed using v2 in production.
- No regression in v1 consumers (i.e. v1 still works identically for everyone who hasn't opted in).

## Phase D — Promotion

**Goal:** v2 becomes canonical. v1 deprecated.

**Lands:**
- v1 maturity model YAMLs gain `superseded-by` pointers to their v2 counterparts.
- v1 bands YAMLs gain `status: deprecated` and a `retired_target_date` (one full assessment cycle in the future).
- `maturity-bands-v2.yaml` gains `status: stable`.

**Exit criterion for retirement of v1 (post-D):**
- One full assessment cycle on v2 complete.
- All consumers that read v1 have v2 support.
- Migration guide published.
- v1 is then `status: retired`, retained per the lifecycle governance rules in `../governance/lifecycle.md`.

## Rules binding every phase

1. **No v1 file is ever modified to incorporate v2 changes.** v1 stays frozen at v1-alpha.
2. **Every v2 file carries `legacy_name`** so existing data resolves.
3. **Every promotion step is recorded** in the CHANGELOG.md of this sub-tree.
4. **The `migration_phase` field in `maturity-bands-v2.yaml`** is updated at each phase boundary.
5. **Phase D requires a separate CR** — promotion is not implicit in Phase A.

---

Cross-references:
- [CR-014](../../change-requests/CR-014.md) — the parent CR
- [maturity-bands-v2.yaml](../maturity-bands-v2.yaml) — the canonical band definitions
- [v2-to-v1-legacy-name-map.yaml](../v2-to-v1-legacy-name-map.yaml) — explicit alias table
- [examples/effort-adjusted-value.yaml](../examples/effort-adjusted-value.yaml) — worked example
- [../../governance/versioning.md](../../governance/versioning.md) — repo-wide versioning policy
- [../../governance/compatibility.md](../../governance/compatibility.md) — explicit compatibility metadata
- [../../governance/lifecycle.md](../../governance/lifecycle.md) — seven lifecycle states including retired