# CR-MM-ECF-01: ECF Profile Conformance Sweep

| Field | Value |
|---|---|
| **CR** | CR-MM-ECF-01 |
| **Title** | ECF Profile Conformance Sweep |
| **Status** | Proposed |
| **Type** | ECF Profile Conformance |
| **Scope** | `technehub-labs/dea-metamodel` |
| **Predecessor** | CR-ECF-005 (ECF Conformance Gate; merged PR #8) |
| **Depends On** | CR-ECF-001..005 (all merged) |
| **Sequencing** | post-gate downstream reconciliation, first in sequence |
| **Resolves** | matrix findings F1, F2, F3 |
| **Author** | Coder (for eaojnr) |
| **Date** | 2026-09-03 |

## 1. Change Request

Resolve the three residual structural findings recorded in
`conformance/matrix.yaml` for `dea-metamodel`:

- **F1**: `schemas/entities/business-object.json` and
  `schemas/entities/organizational-unit.json` restate the canonical
  Domain/Stage enums in kebab-case (the same seven values, but
  `governance-existence` instead of `GovernanceAndExistence`, etc.).
  Recorded as "fix-on-implementation".
- **F2**: `schemas/entities/capability.json` and
  `schemas/entities/process.json` carry no ECF fields by design
  (orthogonal axis vs `capability_layer` and `process_intent`).
  Recorded as "by design".
- **F3**: ECF semantic reservations live in `dea-concepts-model`
  (canonical home); this repo's `vocabulary/terminology-registry.yaml`
  is a pointer per CR-CM-000A §14 / CR-CM-001. Recorded as "by design".

The metamodel already passes 10/10 conformance invariants. This CR
closes the three findings to **PASS** by:

1. **F1** — keeping the kebab-case restatement (lowest blast radius;
   consumer catalogs and entries already use kebab-case), but adding a
   **canonical-resolution validator** that proves every kebab-case value
   in the metamodel's schemas resolves to the canonical PascalCase enum
   in `dea-metaframework`. The validator runs in CI on every push/PR.
2. **F2** — recording the by-design reasoning as a normative note in
   `docs/ecf-profile.md` so the choice is governed and discoverable.
3. **F3** — citing `dea-concepts-model` as the canonical terminology
   authority in `docs/ecf-profile.md`, preserving the existing pointer
   in `vocabulary/terminology-registry.yaml`.

The conformance matrix and `conformance/CONFORMANCE-REPORT-v0.1.md`
are updated to reflect the closed findings.

## 2. Authority chain

The canonical ECF Coordinate contract lives in:

- **`dea-metaframework`** — `schemas/ecf-{domain,stage,coordinate}.schema.json`
  (PascalCase enum, normative since CR-ECF-005).
- **`dea-concepts-model`** — `governance/terminology-registry.yaml`
  (canonical terminology registry since CR-CM-001).
- **`dea-metamodel`** — downstream consumer; ECF profile conformance is
  the responsibility of this CR.

No competing canonical definition is introduced.

## 3. F1 resolution: kebab-case restatement + canonical-resolution validator

The `ecf_domain` and `ecf_stage` enums in `business-object.json` and
`organizational-unit.json` are kept as kebab-case (no schema rename). The
canonical-resolution validator proves every value in those enums maps
1:1 to the canonical PascalCase enum.

### 3.1 Mapping table (normative)

The kebab-case → PascalCase mapping is normative for the two
restating schemas:

| kebab-case (in-schema) | PascalCase (canonical, in `dea-metaframework`) | lowerCamelCase (identifier suffix) |
|---|---|---|
| `governance-existence` | `GovernanceAndExistence` | `governanceExistence` |
| `supply-resources` | `SupplyAndResources` | `supplyResources` |
| `people-organization` | `PeopleAndOrganization` | `peopleOrganization` |
| `customer-demand` | `CustomerAndDemand` | `customerDemand` |
| `product-offering` | `ProductAndOffering` | `productOffering` |
| `operations-delivery` | `OperationsAndDelivery` | `operationsDelivery` |
| `finance-value` | `FinanceAndValue` | `financeValue` |

Stage mapping (kebab-case is the same as PascalCase lowerCamelCase for
all seven Stages; the validator proves the Stage enum values resolve
1:1 as well):

| kebab-case | PascalCase (canonical) |
|---|---|
| `conceive` | `Conceive` |
| `design` | `Design` |
| `build` | `Build` |
| `activate` | `Activate` |
| `operate` | `Operate` |
| `improve` | `Improve` |
| `retire` | `Retire` |

### 3.2 Validator behaviour

`scripts/validate_ecf_kebab_restatement.py` (new, stdlib only):

1. Reads `schemas/entities/business-object.json` and
   `schemas/entities/organizational-unit.json`.
2. For each enum under `properties.ecf_domain` and
   `properties.ecf_stage`, parses the kebab-case values and resolves
   each through the mapping table.
3. Compares the resolved PascalCase set against the canonical enum in
   `dea-metaframework/schemas/ecf-{domain,stage}.schema.json`.
4. **Exit codes**:
     - `0` — every kebab-case value resolves 1:1 to a canonical
       PascalCase enum value; sets of resolved values equal canonical.
     - `1` — at least one kebab-case value does not resolve, or the set
       of resolved values is not equal to the canonical set (extra or
       missing values).
5. The validator runs in `.github/workflows/ci.yml` (the existing
   metamodel CI workflow) after the existing schema-validation step.

### 3.3 Detector update

`scripts/detect_drift.py` (existing) already detects "local ECF
enumerations (kebab-case values where canonical PascalCase should be
used in canonical references)" as a soft warning. This CR upgrades
the **metamodel's own schemas** (the two restating ones) so the
detector's strict run continues to PASS while still flagging any
unsanctioned kebab-case enums in consumer schemas. The detector itself
is not modified (it already reports the right behaviour).

## 4. F2 record: by-design absence

`capability.json` and `process.json` carry no `ecf_domain` /
`ecf_stage` fields. Reasoning:

- **Capability** uses `capability_layer` (`strategic | operational | support`)
  per CR-016 (ADR-015). This is an orthogonal classification axis;
  introducing Domain/Stage fields would be an axis collision.
- **Process** uses `process_intent` (`operational | support | management`)
  per the Business Process catalog schema (CR-ECF-CG-004). This is the
  catalog-specific audience/intent axis; introducing Domain/Stage fields
  would re-introduce the ECF-cell ambiguity the gate forbids.

`docs/ecf-profile.md` records this reasoning normatively so future
contributors do not propose adding Domain/Stage fields to these two
schemas.

## 5. F3 record: terminology authority citation

`docs/ecf-profile.md` cites the canonical terminology registry
(`dea-concepts-model/governance/terminology-registry.yaml`, CR-CM-001)
as the authority for ECF reserved terms (`Domain`, `Stage`, `ECF`).
The existing `vocabulary/terminology-registry.yaml` pointer is
preserved unchanged (CR-CM-000A §14 already established it as a
governed pointer; CR-CM-001 made it authoritative in `dea-concepts-model`).

## 6. ECF profile document

New file `docs/ecf-profile.md`:

1. **Authority chain** — cites `dea-metaframework/specification/ecf-coordinates.md`
   as the canonical ECF Coordinate contract and
   `dea-concepts-model/governance/terminology-registry.yaml` as the
   canonical terminology registry.
2. **ECF profile mechanism** — `dea:core@1.0.0` is the canonical
   anchor; `dea:ecf@1.0.0` is the conformance profile added by
   CR-ECF-CG-001..006.
3. **F1 resolution** — the kebab-case restatement is intentional and
   governed by the validator. The canonical-resolution table is
   reproduced and dated; updates require a new CR.
4. **F2 by-design absence** — `capability.json` and `process.json`
   deliberately omit ECF fields; reasoning recorded.
5. **F3 terminology pointer** — the vocabulary/terminology-registry.yaml
   pointer is preserved per CR-CM-000A §14.
6. **Conformance evidence** — CI run id and conformance report
   (`conformance/CONFORMANCE-REPORT-v0.1.md`) are linked.

## 7. Conformance matrix update

`conformance/matrix.yaml`:

- F1 → **PASS** (kebab-case restatement validated; validator run id
  recorded as evidence).
- F2 → **PASS** (by-design absence documented in `docs/ecf-profile.md`).
- F3 → **PASS** (terminology pointer preserved; canonical home cited).
- `structural_findings` block updated to reflect the resolved state.
- `compiled_at` updated.

`conformance/CONFORMANCE-REPORT-v0.1.md` regenerated by
`scripts/build_conformance_report.py` after the matrix update.

## 8. Required changes

`dea-metamodel` shall:

- Add `scripts/validate_ecf_kebab_restatement.py` (stdlib only).
- Wire the validator into `.github/workflows/ci.yml` after the existing
  schema-validation step.
- Add `docs/ecf-profile.md` recording the F1/F2/F3 governance.
- Update `conformance/matrix.yaml` to close F1, F2, F3 to PASS with
  evidence pointers.
- Regenerate `conformance/CONFORMANCE-REPORT-v0.1.md` and
  `conformance/conformance-report.json` via
  `scripts/build_conformance_report.py`.
- Add `change-requests/CR-MM-ECF-01.md` (this file) to the canonical
  CR index.
- Update `change-requests/README.md` (status row).
- Update `CHANGELOG.md` (Unreleased entry).

## 9. Acceptance criteria

- [ ] Canonical PascalCase enum used as the resolution target (no
    in-repo entity data needs migration).
- [ ] All kebab-case values in `business-object.json` and
    `organizational-unit.json` resolve 1:1 to canonical PascalCase
    enum values.
- [ ] `scripts/validate_ecf_kebab_restatement.py` exits 0 on the
    current schemas.
- [ ] `scripts/validate_ecf_kebab_restatement.py` exits non-zero on a
    deliberately-broken schema (test case shipped with the validator).
- [ ] `.github/workflows/ci.yml` runs the validator on every push/PR.
- [ ] `docs/ecf-profile.md` records the F1/F2/F3 governance with
    citation of canonical authorities.
- [ ] `conformance/matrix.yaml` closes F1, F2, F3 to PASS with
    evidence pointers; `compiled_at` updated.
- [ ] `conformance/CONFORMANCE-REPORT-v0.1.md` regenerated; overall
    verdict remains PASS.
- [ ] `vocabulary/terminology-registry.yaml` pointer preserved
    unchanged (CR-CM-000A §14 / CR-CM-001 governance).
- [ ] No competing Domain or Stage set introduced; no consumer entry
    migration required.
- [ ] `CHANGELOG.md` and `change-requests/README.md` updated.

## 10. Out of scope

- The downstream Business Capability catalog
  (`"Enterprise Composition Framework"` wording; `"earliest initiation"`
  rule) — scope of CR-BC-ECF-01.
- The downstream Business Process catalog (`"ECF cell"` usage;
  Process Context identifier binding) — scope of CR-BP-ECF-01.
- A new metamodel CR redefining the canonical PascalCase contract.
  The contract lives in `dea-metaframework` and is unchanged.
- Re-architecting `capability.json` / `process.json` to add ECF
  fields. The by-design absence (F2) is the governed outcome.