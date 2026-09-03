# ECF Conformance Report v0.1

Compiled: 2026-09-03.
Contract version: 1.0.0 (CR-ECF-001..005 series).
Profile: dea:ecf@1.0.0.
Framework: EnterpriseConceptFramework.

## Overall: PASS

| Invariant | Verdict |
|---|---|
| I1_domain_identity | PASS |
| I2_stage_identity | PASS |
| I3_coordinate_identity | PASS |
| I4_coordinate_cardinality | PASS |
| I5_contextualization | PASS |
| I6_identity_preservation | PASS |
| I7_no_cell_population | PASS |
| I8_terminology | PASS |
| I9_identifier_resolution | PASS |
| I10_version_compatibility | PASS |

## Cross-Repository Matrix

| Repository | Status | Profile | Entries | Extensions |
|---|---|---|---|---|
| dea-metamodel | conformant | dea:ecf@1.0.0 | - | (none) |
| dea-catalog-business-capabilities | conformant-with-extension | dea:ecf@1.0.0 | 26 | kebab-case-domain-vocabulary, multiple-contextual-coordinates, held-unmapped |
| dea-catalog-processes | conformant-with-extension | dea:ecf@1.0.0 | True | process-context (ECF Coordinate interpretation), l0-l4-decomposition (catalog-governed), process-audience (single-axis; not an ECF Coordinate) |

## Coordinate Coverage

- Total canonical coordinates: 49
- Referenced by capability catalog: 27
- Unreferenced (legitimate per CG-005 I7): 22

## Evidence

- **I1_domain_identity**: canonical Domain enum has 7 values; capability catalog references resolve to all of them.
- **I2_stage_identity**: canonical Stage enum has 7 values; capability catalog references resolve to all of them.
- **I3_coordinate_identity**: each (Domain, Stage) pair maps to one identifier; 49-space derivable (7 x 7).
- **I4_coordinate_cardinality**: 7 x 7 = 49 coordinates; derivable from canonical sets.
- **I5_contextualization**: capability and process catalogs use ecfConformance as a separate field; do not redefine Domain or Stage.
- **I6_identity_preservation**: capability ids (dea:capability-...) are independent of any ECF Coordinate; 26 entries with no coordinate-driven identity.
- **I7_no_cell_population**: capability catalog references 27 of 49 canonical coordinates; 22 legitimately unreferenced (held-unmapped documented for CAND-019).
- **I8_terminology**: Enterprise Concept Framework (full expansion) consistent across all landed CRs (CG-001..006).
- **I9_identifier_resolution**: all capability identifiers match the canonical lowerCamelCase pattern.
- **I10_version_compatibility**: all consumers declare contractVersion=1.0.0.

## Machine-readable companion

`conformance/conformance-report.json` carries the same data for tooling consumption.

## Drift detection

Run `python3 scripts/detect_drift.py` (or `--strict` to fail on soft warnings).

## References

- CR-ECF-CG-001..006 (gate definition; metamodel; capability; process; cross-repo; enforcement)
- `dea-metaframework/schemas/ecf-{domain,stage,coordinate}.schema.json` (canonical contract)
