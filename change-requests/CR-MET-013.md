# CR-MET-013 -- Canonical Unit Records

| Field | Value |
|---|---|
| Status | Proposed (this PR) |
| Target repository | `technehub-labs/dea-metamodel` |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-26 |
| Depends on | CR-MET-005 (unit semantics; dimensionality vocabulary); dea-catalog-metrics CR-MET-016 (seed ingestion) and CR-MET-017 (canonical unit references) |
| Blocks | dea-catalog-metrics unit-resolution follow-up (its records' `unit_ref` becomes resolvable) |
| Cardinal authority | dea-metamodel (canonical semantics) |
| Kanban | board 9, card #650 |

## 1. Background and problem statement

The `dea:Unit` entity type is admitted in the metamodel, with a schema
(`schemas/entities/unit.json`) and a controlled vocabulary for
`dimensionality` (CR-MET-005). But no Unit RECORDS exist anywhere: the three
known units (`dea:unit-minute`, `dea:unit-usd`, `dea:unit-throughput-tps`)
live only as conformance fixtures in
`tests/conformance/fixtures/measurement_semantics.yaml`.

The dea-catalog-metrics seed ingestion (dea-catalog-metrics CR-MET-016) put
real unit references into real records: 21 distinct `unit_ref` values across
4,428 catalog records. None of them resolves to anything. A consumer that
follows a record's `unit_ref` gets nothing, because the id names an entity
that has never been admitted.

The owner ruled on this as Q20 (board card #642, 2026-10-26): the unit ids
must become real entities, and the slice lands in dea-metamodel.

## 2. Objective

Admit the canonical Unit records that the catalog's references resolve to, as
a canonical data file of this repository, validated like any other canonical
surface.

## 3. Decisions (binding)

### D1: The units are data, not new types

No entity type is introduced: `dea:Unit` exists. This CR admits 19 Unit
records. The manifest's `vocabularies` section is the established pattern for
canonical data files in this repository (classifications, lifecycle), so the
records land at `metamodel/vocabularies/units.yaml` and are registered there.

### D2: The canonical names are the catalog's form

Per the Q19 ruling (dea-catalog-metrics CR-MET-017): the ratio form and
singular names are canonical. The 19 records are named accordingly
(`dea:unit-ratio-percent`, `dea:unit-minute`, ...). The seed's flat and
plural spellings (13 of them) ride on each record's `aliases` list, so a
consumer holding a legacy spelling resolves to exactly one canonical unit.

### D3: `aliases` is a data-level field, not yet a schema field

`unit.json` does not declare `aliases`. The schema is open
(`additionalProperties` is unset), so the records are valid, and the
conformance test added here pins the field's discipline (unique across all
records, never colliding with a canonical id, well-formed). Promoting
`aliases` into the schema is left to a future CR if other entity types need
the same mechanism.

### D4: Two units are composite because the vocabulary says so

The `dimensionality` vocabulary has no `volume` or `energy` value
(CR-MET-005's 11-value enum). `dea:unit-kilolitre` and
`dea:unit-megawatthour` are therefore declared `composite` with their
dimensional formulas (length cubed; mass times length squared over time
squared), per the CR-MET-005 composite-dimension rule. Extending the
vocabulary is a separate decision and is recorded as a decision point.

### D5: No fixed conversion for calendar units

`dea:unit-month` and `dea:unit-year` declare no `conversion_to_base_factor`:
a calendar month is variable in length, and a nominal factor would misstate
real durations. This matches the fixture pattern, where a factor is declared
only when it is exact.

## 4. Changes

1. `metamodel/vocabularies/units.yaml`: the 19 canonical Unit records.
2. `metamodel/manifest.yaml`: registers the file under
   `metamodel.vocabularies.units`.
3. `tests/conformance/test_034_canonical_units.py`: schema validation of
   every record against `unit.json`; dimensionality against the controlled
   vocabulary; composite units must declare their dimensional formula; id
   and alias discipline; manifest registration; and, when the catalog
   checkout is present, every `unit_ref` the catalog corpus carries resolves
   to a canonical unit or an alias.
4. `change-requests/CR-MET-013.md`, this document.
5. `change-requests/README.md`: the index row.

## 5. Decision points

### Q21: should the `dimensionality` vocabulary gain `volume` and `energy`?

Open. D4 works within the current vocabulary; extending it is the cleaner
long-run form, but it touches the E005 vocabulary surface and belongs in its
own CR with the audit the vocabulary's consumers require.

### Q22: should `aliases` be promoted into `unit.json` (and the shared entity
schema)?

Open. If other entity types need legacy-spelling resolution, the field
belongs in the schema rather than as an open-schema convention.

## 6. Definition of Done

- The full conformance suite and runtime suite pass, including the new
  test_034.
- `validate_json_schemas.py` passes (the new file is data, not a schema, but
  the suite is run to prove nothing else moved).
- The deterministic generators produce no diff (no entity type changed).
- Every `unit_ref` in the dea-catalog-metrics corpus resolves to a canonical
  unit or an alias (the cross-repo test, run with the catalog checkout
  present).
- D-004, D-005, and the embargo denylist are clean on every touched file.

## 7. NOT-list

- No entity type is added, deprecated, or re-scoped.
- No relationship is introduced or extended.
- No catalog record changes; the catalog-side resolution check lands in the
  catalog repo's own follow-up.
- No dimensionality vocabulary extension (Q21).
- No schema change (Q22).

## 8. References

- Board cards #642 (the Q20 ruling), #650 (this slice).
- dea-catalog-metrics CR-MET-016 (seed ingestion; found the gap) and
  CR-MET-017 (canonical unit references; established the names).
- CR-MET-005 (unit semantics; the dimensionality vocabulary and the
  composite-dimension rule).
