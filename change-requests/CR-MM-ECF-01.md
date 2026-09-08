# CR-MM-ECF-01: ECF Profile Conformance Sweep

| Field | Value |
|---|---|
| **CR** | CR-MM-ECF-01 |
| **Title** | ECF Profile Conformance Sweep |
| **Status** | Implemented (PR #161); v2.3.0 migration (PR #TBD) |
| **Type** | ECF Profile Conformance |
| **Scope** | `technehub-labs/dea-metamodel` |
| **Predecessor** | CR-ECF-005 (ECF Conformance Gate; merged PR #8) |
| **Depends On** | CR-ECF-001..005 (all merged); CR-ECF-006 (v2.3.0 domain restructure) |
| **Sequencing** | post-gate downstream reconciliation, first in sequence |
| **Resolves** | matrix findings F1, F2, F3 |
| **Author** | Coder (for eaojnr) |
| **Date** | 2026-09-03 (proposal); 2026-09-07 (v2.3.0 migration) |

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
| `strategy-direction` | `StrategyAndDirection` | `strategyDirection` |
| `agency-organization` | `AgencyAndOrganization` | `agencyOrganization` |
| `party-relationship` | `PartyAndRelationship` | `partyRelationship` |
| `product-value` | `ProductAndValue` | `productValue` |
| `enablement-operations` | `EnablementAndOperations` | `enablementAndOperations` |
| `finance-accounting` | `FinanceAndAccounting` | `financeAccounting` |

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
## 11. v2.3.0 migration (2026-09-07)

When the `dea-metaframework` v2.3.0 release landed
(CR-ECF-006 + ADR-ECF-001), five of the seven canonical ECF Domains
were renamed and one was replaced:

| Before (v2.2.0) | After (v2.3.0) |
|------------------|------------------|
| `governance-existence` | `governance-existence` (unchanged) |
| `supply-resources` | `strategy-direction` |
| `agency-organization` | `agency-organization` (unchanged) |
| `customer-demand` | `party-relationship` |
| `product-offering` | `product-value` |
| `operations-delivery` | `enablement-operations` |
| `finance-value` | `finance-accounting` |

This CR's F1 closure (the kebab-case restatement validated by
`scripts/validate_ecf_kebab_restatement.py`) is the *only* place in
`dea-metamodel` that holds the canonical Domain identifier set, so
this is the right CR to carry the v2.3.0 update.

### 11.1 What changed in this repo

- `DOMAIN_KEBAB_TO_PASCAL` in `scripts/validate_ecf_kebab_restatement.py`
- `ecf_domain` enums in `schemas/entities/business-object.json` and
  `schemas/entities/organizational-unit.json`
- `process_audience` enum in `schemas/entities/process.json` (the only
  place the by-design F2 absence gives way to a real audience
  classification)
- The three `CHECK` constraints in `sqlite/schema.sql` (on `processes`,
  `business_objects`, `organizational_units`) and the regenerated
  `sqlite/dea-metamodel.db`
- `process_audience: Literal[...]` in `pydantic/process.py`
- The three controlled-vocabulary enums in
  `metamodel/vocabularies/classifications.yaml` (`BusinessObject.ecf_domain`,
  `OrganizationalUnit.ecf_domain`, `Process.process_audience`)
- `DOMAIN_ID` in `scripts/detect_drift.py`
- The `EcfDomain` and `ProcessAudience` type aliases in
  `typescript/src/interfaces.ts`
- All narrative references in `docs/concepts/terminology-alignment.md`,
  `docs/ecf-profile.md`, `docs/glossary.md`,
  `docs/process-type-taxonomy.md`

### 11.2 What did NOT change

- The `F2 by-design absence` for `capability.json` (Capability uses
  `capability_layer`; orthogonal axis) — unchanged.
- The `F2 by-design absence` for `capability.json` and `process.json`
  is recorded in `docs/ecf-profile.md`. The `process_audience` field
  on `Process` is a *catalog-internal* axis, not the ECF Domain axis;
  the v2.3.0 rename of the Domain set happens to also be the rename of
  the process_audience values because the two are axiom-derived from
  the same source.

### 11.3 Verification

- `scripts/validate_ecf_kebab_restatement.py`: **PASS** (every kebab-case
  value in the restating schemas resolves 1:1 to the v2.3.0 canonical
  PascalCase enum in `dea-metaframework`).
- `scripts/validate_ecf_kebab_restatement.py --self-test`: **PASS**.
- `tests/conformance/`: **133/133 pass** (E005 classification-vocabularies
  confirms `Process.process_audience` enum matches the controlled
  vocabulary in `classifications.yaml`).
- `tests/runtime/`: **290/290 pass**.
- `scripts/detect_drift.py`: surfaces expected downstream drift in
  `dea-catalog-processes` and `dea-catalog-business-capabilities` (the
  follow-up per-repo migration PRs).

## 12. v2.4.0 migration (2026-09-07)

CR-MM-ECF-02 is the v2.4.0 migration carrier (see
`change-requests/CR-MM-ECF-02.md`). ECF Domain 3 is renamed from
`PeopleAndOrganization` (v2.3.0) to `AgencyAndOrganization` (v2.4.0),
driven by the Substrate Independence Stress Test
(`technehub-labs/dea-metaframework` ADR-ECF-002 §5; CR-ECF-007).

### 12.1 What changed

The kebab-case restatement values in the entity schemas are updated to the
v2.4.0 set: `people-organization` -> `agency-organization`. The PascalCase
enum in `dea-metaframework` v2.4.0 is the source of truth
(`AgencyAndOrganization`). The other six Domains are unchanged.

Same artifacts re-keyed as in section 11: the 3 entity schemas, the sqlite
schema + regenerated db, the pydantic Literal, the typescript type alias,
the detector `DOMAIN_ID` map, the validator `DOMAIN_KEBAB_TO_PASCAL`
mapping, the controlled vocabulary, and the docs files.

### 12.2 Verification

- `scripts/validate_ecf_kebab_restatement.py`: **PASS** (kebab-case values
  resolve 1:1 to the v2.4.0 canonical PascalCase enum).
- `scripts/validate_ecf_kebab_restatement.py --self-test`: **PASS**.
- `tests/conformance/`: **133/133 pass**.
- `tests/runtime/`: **290/290 pass**.

### 12.3 Backward compatibility

`technehub-labs/dea-metaframework` v2.4.0 preserves the deprecated
identifiers in `tools/ecf_coordinates.py:DOMAIN_ALIASES` for at least 2
release cycles. Downstream consumers that have not yet migrated MAY
resolve the alias and use the canonical value.

## 13. v2.5.0 migration — Domain 6 rename (`OperationsAndEnablement` -> `EnablementAndOperations`)

CR-MM-ECF-03 (2026-09-08): Domain 6 of the canonical seven-Domain ECF
set is renamed from `OperationsAndEnablement` (v2.4.0) to
`EnablementAndOperations` (v2.5.0), driven by the Domain/Stage
Orthogonality Stress Test
(`technehub-labs/dea-metaframework` ADR-ECF-003 §5; CR-ECF-008).

### 13.1 What changed

The kebab-case restatement values in the entity schemas are updated to
the v2.5.0 set: `operations-enablement` -> `enablement-operations`.
The PascalCase enum in `dea-metaframework` v2.5.0 is the source of
truth (`EnablementAndOperations`). The other six Domains are
unchanged.

Same artifacts re-keyed as in section 11: the 3 entity schemas, the
sqlite schema + regenerated db, the pydantic Literal, the typescript
type alias, the detector `DOMAIN_ID` map, the validator
`DOMAIN_KEBAB_TO_PASCAL` mapping, the controlled vocabulary, and the
docs files.

### 13.2 Verification

- `scripts/validate_ecf_kebab_restatement.py`: **PASS** (kebab-case
  values resolve 1:1 to the v2.5.0 canonical PascalCase enum).
- `scripts/validate_ecf_kebab_restatement.py --self-test`: **PASS**.
- `tests/conformance/`: **133/133 pass**.
- `tests/runtime/`: **290/290 pass**.

### 13.3 Backward compatibility

`technehub-labs/dea-metaframework` v2.5.0 preserves the deprecated
identifiers in `tools/ecf_coordinates.py:DOMAIN_ALIASES` for at least
2 release cycles (the alias map covers all five deprecated forms:
`OperationsAndEnablement`, `operationsAndEnablement`,
`operations-enablement`, `Operations & Enablement`,
`operations_and_enablement`). Downstream consumers that have not yet
migrated MAY resolve the alias and use the canonical value.

### 13.4 Rationale

Domain 6 is renamed so that the leading noun (`Enablement`) is
lexically distinct from any of the seven lifecycle Stage names. The
previous name shared a Latin root with Stage 5 (`Operate`), obscuring
the orthogonality that the ECF requires between the Domain axis and
the Stage axis. See ADR-ECF-003 §5 for the lexical collision
analysis.
