# ECF Profile — `dea-metamodel`

> **Status**: Live. Authoritative conformance record for the
> Enterprise Concept Framework (ECF) profile in `dea-metamodel`.
> Source of authority: CR-MM-ECF-01 (lands as part of this document's
> first commit) and the upstream gate CR-ECF-005 in `dea-metaframework`.

## 1. Authority chain

The canonical ECF Coordinate contract lives upstream of `dea-metamodel`.

| Layer | Repository | Path | Authority since |
|---|---|---|---|
| Coordinate contract | `technehub-labs/dea-metaframework` | `specification/ecf-coordinates.md` | CR-ECF-005 (merged 2026-09-01, PR #8) |
| Canonical PascalCase enums | `technehub-labs/dea-metaframework` | `schemas/ecf-{domain,stage,coordinate}.schema.json` | CR-ECF-005 |
| Terminology registry | `technehub-labs/dea-concepts-model` | `governance/terminology-registry.yaml` | CR-CM-001 (2026-08-25) |
| Pointer (this repo) | `technehub-labs/dea-metamodel` | `vocabulary/terminology-registry.yaml` | CR-CM-000A §14 |

`dea-metamodel` is a downstream consumer of both authorities. It does
not redefine Domain or Stage; it adopts the canonical PascalCase enum
and either restates it in kebab-case (governed, see §3) or omits it by
design (governed, see §4).

## 2. ECF profile mechanism

The metamodel carries two profiles:

- `dea:core@1.0.0` — the canonical anchor for the metamodel itself.
- `dea:ecf@1.0.0` — the conformance profile added by CR-ECF-CG-001..006,
  declaring that the metamodel conforms to the ECF Coordinate contract.

The profile declaration is the contract surface for cross-repo
conformance checks. Consumers (catalogs, tools) reference this profile
to mean "the ECF semantics used here match the canonical contract; the
mapping table in §3 applies".

## 3. F1 — kebab-case restatement (governed)

Two entity schemas in this repo restate the canonical Domain/Stage
enums in kebab-case:

- `schemas/entities/business-object.json`
- `schemas/entities/organizational-unit.json`

The kebab-case restatement is **intentional and governed**, not a
defect. Consumer entries in `dea-catalog-business-capabilities` and
`dea-catalog-processes` use kebab-case values; the restatement keeps
the metamodel's schemas interoperable with consumer data without
forcing a one-shot migration.

### 3.1 Mapping table (normative)

The kebab-case → PascalCase mapping is normative for these two schemas.
Updates require a new CR.

| kebab-case (in-schema) | PascalCase (canonical, in `dea-metaframework`) | lowerCamelCase (identifier suffix) |
|---|---|---|
| `governance-existence` | `GovernanceAndExistence` | `governanceExistence` |
| `supply-resources` | `SupplyAndResources` | `supplyResources` |
| `people-organization` | `PeopleAndOrganization` | `peopleOrganization` |
| `customer-demand` | `CustomerAndDemand` | `customerDemand` |
| `product-offering` | `ProductAndOffering` | `productOffering` |
| `operations-delivery` | `OperationsAndDelivery` | `operationsDelivery` |
| `finance-value` | `FinanceAndValue` | `financeValue` |

Stage mapping (kebab-case is identical to lowerCamelCase for all
seven Stages):

| kebab-case | PascalCase (canonical) |
|---|---|
| `conceive` | `Conceive` |
| `design` | `Design` |
| `build` | `Build` |
| `activate` | `Activate` |
| `operate` | `Operate` |
| `improve` | `Improve` |
| `retire` | `Retire` |

### 3.2 Validator

`scripts/validate_ecf_kebab_restatement.py` enforces this table at CI
time. The validator:

1. Reads the two restating schemas' `ecf_domain` and `ecf_stage` enums.
2. Resolves each kebab-case value through the table above.
3. Compares the resolved PascalCase set against the canonical enum
   in `dea-metaframework/schemas/ecf-{domain,stage}.schema.json`.
4. Exits 0 only if every value resolves 1:1 and the set is equal to
   the canonical enum (no missing, no extra).
5. Ships a built-in broken-schema self-test to detect validator
   regressions.

CI runs the validator on every push/PR via `.github/workflows/ci.yml`.

### 3.3 Detector interaction

`scripts/detect_drift.py` (CR-ECF-CG-005 §5) detects "local ECF
enumerations (kebab-case values where canonical PascalCase should be
used in canonical references)" as a soft warning. After CR-MM-ECF-01
lands, the metamodel's two restating schemas are sanctioned; the
detector still flags unsanctioned kebab-case enums elsewhere.

## 4. F2 — by-design absence (governed)

Two entity schemas in this repo carry no `ecf_domain` or `ecf_stage`
fields:

- `schemas/entities/capability.json` — uses `capability_layer`
  (`strategic | operational | support`) per CR-016 (ADR-015).
- `schemas/entities/process.json` — uses `process_intent`
  (`operational | support | management`) per the Business Process
  catalog schema (CR-ECF-CG-004).

The omission is **by design and governed**, not a defect:

- **Capability**: `capability_layer` is the orthogonal classification
  axis. Adding Domain/Stage fields would be an axis collision.
- **Process**: `process_intent` is the catalog-specific audience/intent
  axis. Adding Domain/Stage fields would re-introduce the "ECF cell"
  ambiguity the gate forbids (CG-004 §10).

Future contributors who propose adding Domain/Stage fields to these
two schemas should be redirected to this section; a CR is required to
reverse the by-design absence.

## 5. F3 — terminology authority citation (governed)

The terminology registry pointer in `vocabulary/terminology-registry.yaml`
is preserved unchanged per CR-CM-000A §14. The canonical home for the
registry is `dea-concepts-model/governance/terminology-registry.yaml`
since CR-CM-001 (2026-08-25).

ECF reserved terms — `Domain`, `Stage`, `ECF` (expanding to
`Enterprise Concept Framework`) — are governed there. Local use in
this repo must follow the canonical expansion. The drift detector
flags any non-canonical expansion (e.g. `Enterprise Composition
Framework`, `Enterprise Concepts Framework`, `Enterprise Conceptual
Framework`).

## 6. Conformance evidence

- `conformance/matrix.yaml` — declarative state; invariants I1..I10
  + structural findings F1/F2/F3.
- `conformance/CONFORMANCE-REPORT-v0.1.md` — human-readable report,
  regenerated by `scripts/build_conformance_report.py`.
- `conformance/conformance-report.json` — machine-readable companion.
- `scripts/detect_drift.py --strict` — drift detector; exits non-zero
  on any drift finding or hard failure.
- `scripts/validate_ecf_kebab_restatement.py` — kebab-case resolver;
  closes F1 at CI time.
- `.github/workflows/ci.yml` — runs the conformance suite on every
  push/PR (CR-MM-1.9 tests 001-006 + CR-1.11 drift enforcement +
  CR-MM-ECF-01 kebab-case validator).

## 7. References

- CR-ECF-001..005 — ECF framework tranche (`dea-metaframework`).
- CR-ECF-CG-001..006 — cross-repo conformance gate enforcement.
- CR-MM-02 — capability schema hygiene (CR-016 lineage).
- CR-MM-ECF-01 — this profile's establishment CR.
- `dea-concepts-model/governance/terminology-registry.yaml` — canonical
  terminology registry.