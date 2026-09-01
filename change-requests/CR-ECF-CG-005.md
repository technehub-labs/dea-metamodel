# CR-ECF-CG-005: Cross-Repository Conformance

| Field | Value |
|-------|-------|
| **CR** | CR-ECF-CG-005 |
| **Title** | Cross-Repository Conformance |
| **Status** | Proposed |
| **Type** | Ecosystem Conformance |
| **Scope** | ECF-consuming OpenDEA repositories |
| **Implements** | CR-ECF-CG-001 |
| **Depends On** | CR-ECF-CG-002, CR-ECF-CG-003, CR-ECF-CG-004 |
| **Author** | Coder (for eaojnr) |
| **Date** | 2026-09-01 |

This is what turns the four individual validations into an actual gate across the ecosystem.

## 1. Purpose

Establish cross-repository validation ensuring that ECF semantics remain consistent across the metamodel and all consuming catalogs.

## 2. Canonical Source Chain

The conformance chain shall be:

dea-metaframework
       |
       | ECF Framework Contract
       V
dea-metamodel
       |
       | Formal Semantic Representation
       V
DEA Catalogs
       |
       | Domain-Specific Instances
       V
Tools / Applications

No downstream repository shall establish a competing canonical definition.

## 3. Cross-Repository Invariants

The following invariants shall be tested:

Invariant 1: Domain Identity

Every ECF Domain reference resolves to the same canonical Domain.

Invariant 2: Stage Identity

Every ECF Stage reference resolves to the same canonical Stage.

Invariant 3: Coordinate Identity

The same (Domain, Stage) pair resolves to the same Coordinate.

Invariant 4: Coordinate Cardinality

The canonical ECF space contains exactly:

7 x 7 = 49

coordinates.

Invariant 5: Contextualization

Catalog-specific contexts reference Coordinates rather than redefining them.

Invariant 6: Identity Preservation

A catalog entry does not acquire its identity from its ECF Coordinate.

Invariant 7: No Cell Population Requirement

No repository assumes that all 49 coordinates must contain catalog entries.

Invariant 8: Terminology

ECF shall consistently expand to:

Enterprise Concept Framework

No competing expansion shall remain.

Invariant 9: Identifier Resolution

All ECF identifiers used downstream resolve to the canonical source.

Invariant 10: Version Compatibility

Repositories shall declare the ECF contract version against which they conform.

## 4. Cross-Repository Validation Matrix

The gate shall produce a matrix similar to:

| Repository | Semantic | Schema | IDs | Terminology | References | Status |
|---|---|---|---|---|---|---|
| dea-metamodel | yes | yes | yes | yes | yes | Gate result |
| dea-catalog-business-capabilities | yes | yes | yes | yes | yes | Gate result |
| dea-catalog-processes | yes | yes | yes | yes | yes | Gate result |

Additional ECF consumers shall be added as they become governed consumers.

## 5. Drift Detection

The gate shall detect:

- changed Domain definitions;
- changed Stage definitions;
- missing Coordinates;
- duplicate Coordinates;
- local ECF enumerations;
- invalid identifiers;
- terminology drift;
- incompatible schema changes;
- undocumented extensions.

## 6. Conformance Manifest

Each repository shall expose a machine-readable conformance declaration:

ecfConformance:
  framework: EnterpriseConceptFramework
  contractVersion: <version>
  status: conformant
  profile: <profile>
  extensions: []

The exact schema shall be finalized during implementation.

## 7. Acceptance Criteria

- [ ] Cross-repository invariants are executable.
- [ ] Canonical identifiers resolve.
- [ ] Terminology drift is detectable.
- [ ] Local redefinitions are detectable.
- [ ] Version compatibility is detectable.
- [ ] Conformance status is machine-readable.
- [ ] A consolidated conformance report can be generated.

## 8. Definition of Done (this proposal PR)

Two files for this CR (verbatim against the source tranche + index row). Implementation PR (matrix YAML + drift detector + cross-repo conformance report generator) ships on subsequent acceptance. The companion CR-ECF-CG-006 ships in the same proposal PR for the gate's enforcement half (recommended per the tranche's CG-005/006 pairing note).

## 9. References

CR-ECF-CG-001 (gate definition); CR-ECF-CG-002 (metamodel conformance); CR-ECF-CG-003 (capability catalog conformance); CR-ECF-CG-004 (process catalog conformance); `dea-metaframework` schemas (canonical ECF).