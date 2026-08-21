# CR-MM-01.1 — Maturity v2 Phase B follow-on: vocabulary registration + governance metadata

| Field | Value |
|-------|-------|
| **CR** | CR-MM-01.1 (sub-CR of CR-MM-01) |
| **Title** | Register `scored-by-v2-bands` in the controlled vocabulary + add CR-AM-01 §42 governance fields (`steward`/`effective_date`/`review_date`) to v2-beta maturity models and Phase A registry artefacts |
| **Status** | Proposed |
| **Date** | 2026-08-21 |
| **Author** | Coder (for eaojnr) |
| **Version** | additive (no canonical `VERSION` bump; no schema, governance-policy, or model-content changes) |
| **Depends on** | CR-MM-01 (which landed the v2-beta maturity models), CR-AM-01 §41 (controlled relationship vocabulary) + §42 (every-model governance fields), CR-014 (Phase A registry artefacts) |
| **Scope** | Two small metadata-only changes that close two gaps surfaced by the post-CR-MM-01 / CR-AM-01 compliance audit (2026-08-21): (a) one entry added to `assessment-models/vocabulary/relationship-types.yaml` registering the new `scored-by-v2-bands` relationship type used by all 5 v2-beta YAMLs; (b) `steward`, `effective_date`, `review_date` added to all 5 v2-beta maturity YAMLs and to the 2 Phase A registry artefacts. Plus a new CI validator that asserts every `relationship_type:` value in maturity+v2-beta+examples is registered in the vocabulary (fail-fast on this gap class in the future). |
| **Out of scope** | Any model content change (characteristics/exit_criteria/evidence are byte-identical from v1-alpha per CR-MM-01); any band/range/effort_multiplier change; schema content changes; consumer-side tooling (Phase C); any change to assessment-instrument.schema.json or assessment-result.schema.json; CR-MM-02 (Phase C). |

---

## 1. Context

On 2026-08-21, a reconciled compliance audit was performed against CR-MM-01 + CR-AM-01 + CR-015 together as a cohesive set. 6/6 of CR-MM-01's acceptance criteria passed. CR-015's 6/6 passed. CR-AM-01's Definition of Done was 19/20 (1 cosmetic) and Acceptance Criteria was 7/10 PASS + 3 PARTIAL (correctly parked).

The audit surfaced two **specific, small alignment gaps** that are addressable without changing the shipped behaviour. Both are documented-truth improvements; neither introduces a behavioural regression:

### 1.1 Gap G1 — `scored-by-v2-bands` not in the controlled vocabulary

CR-AM-01 §17 and §41 require that *all* relationship types be registered in `assessment-models/vocabulary/relationship-types.yaml`. CR-MM-01 (merged 2026-08-21) introduced a new relationship type, `scored-by-v2-bands`, used in all 5 v2-beta YAMLs to link each v2 maturity model to `dea:maturity-bands-v2`. The vocabulary was not updated.

Consequence: no CI validator caught the omission (none existed). Future consumers (Phase C — `dea-cli`, `dea-web-viewer`) that introspect the vocabulary will not see `scored-by-v2-bands` as a known type even though it is used in canonical YAML.

### 1.2 Gap G2 — CR-AM-01 §42 governance fields not present on v2-beta models or Phase A artefacts

CR-AM-01 §42 (Governance) says *every model shall have* `owner`, `steward`, `status`, `effective_date`, `review_date`. Survey:

| Artefact | owner | steward | status | effective_date | review_date |
|----------|-------|---------|--------|----------------|-------------|
| 5 v2-beta maturity YAMLs | ✅ (preserved from v1) | ❌ | ✅ (`beta`) | ❌ | ❌ |
| `maturity-bands-v2.yaml` (Phase A) | ❌ | ❌ | ✅ (`beta`) | ❌ | ❌ |
| `v2-to-v1-legacy-name-map.yaml` (Phase A) | ❌ | ❌ | ✅ (`beta`) | ❌ | ❌ |

Consequence: governance dashboards that consume `effective_date` / `review_date` cannot render. The metadata is harmless if present and trivial to set, so closing the gap is straightforward.

### 1.3 What this CR is NOT

- **Not a behavioural change.** No maturity model changes (characteristics, exit criteria, evidence are still byte-equal to v1-alpha). No schema changes. No range changes.
- **Not a re-architecture.** This is the minimum-viable closure of two known gaps, nothing else.
- **Not a Phase C work.** Consumer tooling lands in CR-MM-02 (queued, parked).
- **Not a v1 → v2 promotion.** v1 stays canonical until Phase D.

## 2. Changes

### 2.1 Register `scored-by-v2-bands` in `vocabulary/relationship-types.yaml`

Add one entry to the `values:` list:

```yaml
- id: scored-by-v2-bands
  description: |
    MaturityModel scored by the canonical v2 maturity scoring bands (non-linear
    20/25/25/18/12 with effort_multiplier 1.0/1.5/2.5/4.0/6.0). Distinct from
    `scored-by` (legacy alias for `interpreted-by`) so v1 and v2 scoring paths
    are first-class at the relationship-type layer.
  source_kinds: [maturity-model]
  target_kinds: [maturity-bands]
```

(`scored-by` is listed as a legacy alias for `interpreted-by` in the same file. The new `scored-by-v2-bands` is distinct and stands alone — there is no aliasing.)

### 2.2 Add CR-AM-01 §42 governance fields to v2-beta YAMLs (5 files × 3 new fields)

For each v2-beta file, add three lines after `owner:` (preserved verbatim from v1-alpha) and before the `levels:` block:

```yaml
steward:              <chief of the matching role; preserved from v1-alpha owner>
effective_date:       2026-08-21       # CR-MM-01 merge date
review_date:          2027-02-21       # effective + 6 months
```

Per file, the `steward:` value tracks the v1-alpha `owner:` (the canonical human in the role):

| File | steward |
|------|---------|
| `ea-capability.yaml` | Chief Architect |
| `modernization.yaml` | Modernisation Lead |
| `technology.yaml` | CTO / Platform Engineering |
| `operations.yaml` | Head of Operations / SRE Lead |
| `services-delivery.yaml` | Head of Delivery / VP Engineering |

### 2.3 Add CR-AM-01 §42 governance fields to Phase A artefacts (2 files × 4 new fields)

For both `maturity-bands-v2.yaml` and `v2-to-v1-legacy-name-map.yaml`, add four lines after `status: beta`:

```yaml
owner:                Chief Architect       # CR-MM-01.1
steward:              Chief Architect       # CR-MM-01.1
effective_date:       2026-08-20            # CR-014 merge date for these artefacts
review_date:          2027-02-20            # effective + 6 months
```

### 2.4 New CI validator — `validate-relationship-vocabulary`

A new CI job in `.github/workflows/ci-assessment-models.yml`:

- Loads the controlled vocabulary (`vocabulary/relationship-types.yaml`).
- Builds the permitted set from canonical `values:` ids + `legacy_aliases:` keys.
- Iterates every `relationships:` block in `maturity/*.yaml`, `maturity/v2-beta/*.yaml`, `maturity/examples/*.yaml`, `examples/*.yaml`.
- Fails fast (exit 1) if any `relationship_type:` value is not in the permitted set; logs the offending file + value + the permitted set.

This is the **fail-fast guard** for gap G1 — any future YAML that introduces an unregistered relationship type will not get past this job.

## 3. Out of scope (re-stated)

- **Behaviour changes.** None proposed. The 5 v2-beta maturity models still preserve every `characteristic`, `exit_criterion`, `evidence` byte-identically from v1-alpha per CR-MM-01.
- **Schema content changes.** `assessment-models/schemas/*.schema.json` is unchanged.
- **Governance policy changes.** `governance/versioning.md`, `governance/compatibility.md`, `governance/lifecycle.md` are unchanged.
- **Band changes.** `maturity-bands-v2.yaml` is unchanged semantically (governance metadata is metadata, not band logic).
- **Phase C consumer support.** CR-MM-02.
- **v1 → v2 promotion.** Phase D.

## 4. Acceptance criteria

1. ✅ `vocabulary/relationship-types.yaml` lists `scored-by-v2-bands` with `source_kinds: [maturity-model]` and `target_kinds: [maturity-bands]`.
2. ✅ All 5 v2-beta YAMLs carry `steward`, `effective_date: 2026-08-21`, `review_date: 2027-02-21`.
3. ✅ Both Phase A artefacts carry `owner: Chief Architect`, `steward: Chief Architect`, `effective_date: 2026-08-20`, `review_date: 2027-02-20`.
4. ✅ New CI job `validate-relationship-vocabulary` runs against `maturity/*`, `maturity/v2-beta/*`, `maturity/examples/*`, `examples/*`. Asserts every `relationship_type` is in the canonical-or-legacy vocabulary set.
5. ✅ Existing CR-MM-01 CI jobs (5 of 5) remain green with no regression. Existing CR-014-era CI jobs remain green.
6. ✅ `change-requests/CR-MM-01.1.md`, `change-requests/README.md` row, `CHANGELOG.md [Unreleased]` entry.

## 5. References

- **CR-MM-01** (parent CR): [CR-MM-01.md](CR-MM-01.md) — which introduced `scored-by-v2-bands` and the v2-beta YAMLs (this CR's gap G1 source).
- **CR-014** (Phase A landing): [CR-014.md](CR-014.md) — which produced `maturity-bands-v2.yaml` and `v2-to-v1-legacy-name-map.yaml` (this CR's gap G2 source).
- **CR-AM-01** (umbrella): §17 (Required Relationship Model), §41 (Relationship Vocabulary), §42 (Governance).
- **CR-015** (assessment-profile cross-link): [CR-015.md](CR-015.md) — the audit that surfaced the gaps was performed in its wake.
- **Compliance audit report**: session 2026-08-21 12:xx UTC; documented in the previous turn's scorecard.

## 6. Post-CR-MM-01.1 state

After this CR merges:

| Section | Status |
|---------|--------|
| Phase A — registry artefacts | ✅ shipped (CR-014) + governance fields added (CR-MM-01.1) |
| Phase B — beta files | ✅ shipped (CR-MM-01) + governance fields added + vocabulary checks (CR-MM-01.1) |
| Phase C — consumers | 🔜 next (CR-MM-02) |
| Phase D — promotion | 🔜 future CR after one full v2 assessment cycle |
