# CR-ECF-CG-002: Metamodel Conformance

| Field | Value |
|-------|-------|
| **CR** | CR-ECF-CG-002 |
| **Title** | Met Model Conformance: ECF Profile + crosswalk |
| **Status** | Proposed |
| **Type** | Metamodel Reconciliation |
| **Repository** | technehub-labs/dea-metamodel |
| **Implements** | CR-ECF-CG-001 |
| **Depends On** | CR-ECF-005, CR-ECF-CG-001 |
| **Author** | Coder (for eaojnr) |
| **Date** | 2026-09-01 |

## 1. Purpose

Verify that the DEA Metamodel ECF Profile conforms exactly to the established ECF contract.

The metamodel shall remain the canonical formal representation of OpenDEA semantics; `dea-metaframework` remains authoritative for the ECF framework and coordinate contract (CR-ECF-001..005).

## 2. Required ECF Semantics

The ECF Profile shall represent:

ECF Domain
ECF Stage
ECF Coordinate

without redefining their semantics.

The canonical relationship is:

ECF Domain
      +
ECF Stage
      ↓
ECF Coordinate

## 3. Required Separation

The metamodel shall preserve the distinction:

ECF Coordinate ≠ Entity
ECF Coordinate ≠ Capability
ECF Coordinate ≠ Process
ECF Coordinate ≠ State
ECF Coordinate ≠ Process Level

## 4. Identifier Conformance

The metamodel shall use stable semantic identifiers for:

- Domains;
- Stages;
- Coordinates;
- profile relationships.

No display label shall be treated as semantic identity.

## 5. Enumeration Conformance

The canonical seven Domains and seven Stages shall be represented from the ECF specification rather than independently recreated.

All 49 Coordinates shall be derivable from the canonical sets.

## 6. Extension Rule

The ECF Profile may define OpenDEA-specific relationships involving ECF Coordinates.

It shall not:

- redefine a Domain;
- redefine a Stage;
- change Coordinate semantics;
- create alternative ECF Coordinate identities;
- introduce a competing ECF taxonomy.

## 7. Schema Conformance

All generated or maintained schema representations shall validate against the normative metamodel.

The implementation shall identify the source of truth for:

normative semantics
schema
examples
documentation

and prevent uncontrolled divergence.

## 8. Required Deliverables

Produce:

ECF Profile Conformance Report
ECF Identifier Crosswalk
ECF Schema Validation Results
ECF Extension Register
ECF Documentation Reconciliation

## 9. Acceptance Criteria

- [ ] ECF Profile conforms to CR-ECF-001..005.
- [ ] Domain and Stage semantics are canonical.
- [ ] Coordinate semantics are canonical.
- [ ] No coordinate/entity conflation exists.
- [ ] Stable IDs resolve.
- [ ] 49 coordinates are derivable.
- [ ] Schema validation passes.
- [ ] No competing local ECF definition remains.
- [ ] Extensions are explicitly registered.
- [ ] Documentation matches implementation.

## 10. Definition of Done (this proposal PR)

Two files: this CR (verbatim against the source tranche) and the change-requests index row. Implementation PR(s) for the deliverables ship on subsequent acceptance.

## 11. References

CR-ECF-CG-001 (gate definition); CR-ECF-005 (coordinate specification); `dea-metaframework` schemas (`ecf-domain.schema.json`, `ecf-stage.schema.json`, `ecf-coordinate.schema.json`); `dea-concepts-model` terminology registry (canonical home for ECF semantic reservations).