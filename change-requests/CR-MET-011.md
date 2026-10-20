# CR-MET-011 -- Establish Temporal Measurement Semantics, Historical Traceability and Provenance Architecture

| Field | Value |
|---|---|
| Status | Accepted (landed via PR #187) |
| Target repository | `technehub-labs/dea-metamodel`, `technehub-labs/dea-governance`, future measurement runtime |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Phase | 6 (Runtime and intelligence) |
| Depends on | CR-MET-001, CR-MET-003, CR-MET-004, CR-MET-005, CR-MET-006, CR-MET-010; ADR-MET-010, ADR-MET-011, ADR-MET-012, ADR-MET-014 |
| Kanban | T-MET umbrella #429; this CR is card #441 |
| Programme stream | Stream C (Historical intelligence and decision support) |

## 1. Background and problem statement

Enterprise measurements are inherently temporal. A measurement is meaningful only when its timing, reporting period, validity, and measurement definition are understood.

Consider an enterprise reporting that its employee turnover rate is 12%. That result is incomplete without knowing: whether it represents a month, quarter, or year; which employee population was included; which calculation method was used; which organizational structure applied; when the data was captured; whether the Metric definition has changed; whether the value has subsequently been corrected.

OpenDEAM must therefore establish temporal and provenance semantics as first-class architectural concerns. The key architectural decision (per the user-supplied CR-MET-011 §10): "Historical Observations must retain their original semantic context. Updating a Metric must not retrospectively change the meaning of previously recorded results."

## 2. Objective

Establish a reusable architecture for recording, tracing, reconstructing, and interpreting historical Measurements and Observations.

## 3. Temporal architecture (per the user-supplied CR §3)

7 temporal dimensions are distinguished.

| Temporal dimension | Meaning |
|---|---|
| Observation time | When the value was observed |
| Measurement time | When the measurement was performed |
| Reporting period | Period the result represents |
| Valid time | Period during which the result applies |
| Transaction time | When the information was recorded in the system |
| Effective time | When a definition or configuration becomes applicable |
| Publication time | When the result becomes available to consumers |

These dimensions must not be collapsed into one timestamp. The disposition question (see Section 9, Q17) is whether each dimension is a first-class field on Observation / Measurement, a structured nested object, or a referenced temporal entity.

## 4. Reporting period semantics (per the user-supplied CR §4)

The architecture must support:

- Instantaneous measurements.
- Point-in-time measurements.
- Fixed-duration reporting periods.
- Rolling periods.
- Cumulative periods.
- Event-based measurements.
- Irregular measurement intervals.

A `dea:ReportingPeriod` entity carries the period type, the start, the end (or null for instantaneous), and the period semantics (calendar, fiscal, rolling, event-based).

## 5. Provenance architecture (per the user-supplied CR §5)

Every important Observation must be traceable to its origins. 11 provenance elements are defined.

| Provenance element | Description |
|---|---|
| Source | Original data source |
| Source record | Specific originating record or dataset |
| Collection activity | How information was acquired |
| Calculation activity | How the result was derived |
| Transformation | Processing and conversion applied |
| Responsible party | Person, system, or AI process responsible |
| Configuration | Measurement configuration used |
| Formula version | Calculation definition applied |
| Metric version | Metric definition applied |
| Evidence | Supporting source material |
| Timestamp | Relevant temporal information |

The architecture should investigate alignment with W3C PROV concepts (Entity, Activity, and the responsible-party concept) where appropriate, and reuse existing OpenDEAM provenance concepts if they already provide equivalent functionality.

## 6. Historical reconstruction (per the user-supplied CR §6)

A core requirement is the ability to reconstruct a previously reported result. Given an Observation, the system should be able to identify: the Metric definition used, the Measurement configuration, the formula version, the source data, the transformations applied, the subject and organizational scope, the reporting period, the applicable baseline and target, the validation and approval status, and any subsequent correction or supersession.

This should enable reproducibility without requiring every historical result to be recalculated whenever a Metric definition changes.

## 7. Correction and supersession (per the user-supplied CR §7)

5 record states are distinguished.

| State | Meaning |
|---|---|
| Original Observation | First recorded result |
| Corrected Observation | Revised result that replaces the original |
| Superseded Observation | Replaced by a newer Observation |
| Invalid Observation | Marked as not to be used |
| Retracted Observation | Withdrawn from publication |

Corrections must preserve historical auditability. A correction must not silently overwrite the original value. The relationship between original and corrected records must be explicit (a `dea:corrects` or `dea:supersedes` relationship).

## 8. Decision points

### Q17 (new from CR-MET-011 §3). Temporal dimension representation

- **(a) Each of the 7 dimensions is a separate field on Observation / Measurement with the corresponding type (timestamp, period, range)**. Recommended; matches the user-supplied "must not be collapsed into one timestamp" guidance.
- **(b) The 7 dimensions are encoded as a structured nested object on Observation (`temporal: { observed_at, measured_at, reporting_period, valid_from, valid_to, transaction_at, effective_from, publication_at }`)**. Same content, structured for namespace cleanliness.
- **(c) Each dimension is a referenced entity (`dea:ObservationTime`, `dea:MeasurementTime`, `dea:ReportingPeriod`, `dea:ValidTime`, `dea:TransactionTime`, `dea:EffectiveTime`, `dea:PublicationTime`)**. Loses the field-level simplicity; gains reusability across records.

**DISPOSITION (binding): Q17b, as recommended.** One nested `temporal` object on `dea:MeasurementObservation` carrying all 7 dimensions; `dea:ReportingPeriod` as a referenced entity.

Audit finding: `dea:TemporalInterval` (CR-6 §5) already carries the interval clocks (`valid_from`, `valid_to`, `recorded_at`, `observed_at`, `planned_start`, `planned_end`, `effective_from`, `effective_to`) and its definition already states that the clocks are not interchangeable. `dea:ReportingPeriod` therefore **specializes** `dea:TemporalInterval` via `dea:specializes` rather than duplicating the interval payload; the period type and period semantics are the specialization payload. This is the kernel+specialization pattern of CR-016 / ADR-015.

`EffectiveTime` is NOT introduced as a separate entity. It is carried as the `effective_from` / `effective_to` pair on the Provenance record and in the Observation temporal object, because effective time describes the governing definition rather than a separately identified object.

The pre-existing `temporal` placeholder on `measurement-observation.json` (which read "Full specification in CR-MET-011") is now fully specified with 9 named fields and `observed_at` + `recorded_at` required.

### Q18 (new from CR-MET-011 §5). Provenance representation

- **(a) A `dea:Provenance` entity with 11 attributes (Section 5) referenced by Observation via `dea:has-provenance`**. Recommended; matches the W3C PROV-inspired approach.
- **(b) A nested `provenance: {...}` object on Observation**. Same content; namespace cleanliness.
- **(c) Each provenance element is a referenced entity**. Entity proliferation; not recommended.

**DISPOSITION (binding): Q18a, as recommended.** A `dea:Provenance` entity with the 11 Section 5 attributes, referenced by Observation via `dea:has-provenance`.

Audit findings that shaped the binding:

- No `dea:Provenance` entity exists today. The nearest constructs are `dea:Evidence`, `dea:EvidenceSource`, `dea:EvidenceArtifact` (CR-5 §16) and the `dea:traces-to` / `dea:derived-from` relationships. None of them carries the 11 elements as a single reconstructable record.
- The pre-existing `provenance_reference` field on `measurement-observation.json` was a placeholder reading "Full provenance model in CR-MET-011". It is now the typed binding reference to the `dea:Provenance` record. No duplicate field was introduced.
- `dea:Provenance` **reuses** the CR-5 evidence entities rather than duplicating evidence semantics: `source_ref` points at a `dea:EvidenceSource`, `evidence_refs` at `dea:Evidence` / `dea:EvidenceArtifact`.

Cardinality is 1:1 (`has-provenance` target cardinality `1`). Provenance is a fact about a single recorded result; sharing one Provenance record between two results would make the version pins ambiguous. A re-run (for example a correction) is a new calculation activity and therefore a new Provenance record. This is enforced by `test_section5_provenance_is_one_to_one_with_observation`.

W3C PROV alignment (Section 5 / Section 9): the Observation is the PROV **entity**; `collection_activity` and `calculation_activity` are PROV **activities**; `responsible_party_ref` is the PROV **responsible-party concept**. The implementation deliberately uses the term "responsible party" rather than the PROV role name, to avoid a collision with the metamodel's own accountable-entity vocabulary entry while preserving the semantics.

The 11 elements map to: `source_ref` (1), `source_record_ref` (2), `collection_activity` (3), `calculation_activity` (4), `transformation_chain` (5), `responsible_party_ref` (6), `configuration_ref` (7), `formula_version_ref` (8), `metric_version_ref` (9), `evidence_refs` (10), `timestamps` (11). All 11 are required.

### Q19 (new from CR-MET-011 §7). Correction / supersession relationship

- **(a) Two relationships: `dea:corrects` (between an original Observation and its corrected successor) and `dea:supersedes` (between an original Observation and a later Observation that replaces it for the same period)**. Recommended; matches the user-supplied distinction between "Corrected" and "Superseded" states.
- **(b) A single `dea:supersedes` relationship covering both**. Loses the semantic distinction.
- **(c) Corrections are encoded as a `correction_of` field on Observation**. Inline state; loses reusability.

**DISPOSITION (binding): Q19a, as recommended.** A new `dea:corrects` relationship; `dea:supersedes` retained.

Audit finding that reduces the work: `dea:supersedes` was extended by CR-MET-004 to carry `dea:MeasurementObservation` on **both** the source and the target, so supersession is already modelled and needs no new relationship. Only `dea:corrects` is genuinely new.

The two relationships carry different governance implications and are not interchangeable:

| Relationship | Assertion | Meaning |
|---|---|---|
| `dea:corrects` | the target was WRONG | a revised restatement of an erroneous result |
| `dea:supersedes` | a NEWER AUTHORITATIVE value exists for the same period | a later result replaces an earlier one |

The pre-existing `supersedes_observation` field conflated the two: its description read "Reference to the prior observation this observation corrects", which is correction semantics carried in a supersession field. It is **DEPRECATED** and new records MUST use `corrects_observation_ref` for correction and the `dea:supersedes` relationship for supersession. Retained for one release cycle for backward compatibility.

The 5 record states are encoded on `MeasurementObservation.record_state`: `original`, `corrected`, `superseded`, `invalid`, `retracted`. A correction never overwrites the original value; the original is retained with `observation_status: superseded` and a distinct value, enforced by `test_section7_correction_never_overwrites_the_original`.

## 9. Reconciliation with existing temporal / provenance constructs

| Existing construct | Disposition |
|---|---|
| Existing OpenDEAM `temporal: true` flag on relationships (per the dea-metamodel canonical source) | RETAIN. The relationship-level temporal flag indicates that the relationship is time-aware; the new Observation-level temporal architecture complements it. All 3 new relationships set `temporal: true`. |
| `dea:TemporalInterval` (CR-6 §5) | SPECIALIZE. `dea:ReportingPeriod` specializes it via `dea:specializes` rather than duplicating the interval clocks. |
| Pre-existing `temporal` placeholder on `measurement-observation.json` | SPECIFY in place. The placeholder carried `additionalProperties: true` and the note "Full specification in CR-MET-011"; it is now fully specified. |
| Pre-existing `provenance_reference` field on `measurement-observation.json` | SPECIFY in place as the typed binding reference to `dea:Provenance`. No duplicate field introduced. |
| Pre-existing `supersedes_observation` field on `measurement-observation.json` | DEPRECATE. It conflated correction with supersession (Q19a). Retained one release cycle. |
| `dea:supersedes` relationship (CR-MET-004 extension) | RETAIN. Already carries `dea:MeasurementObservation` on both endpoints; no new supersession relationship required. |
| `dea:Evidence`, `dea:EvidenceSource`, `dea:EvidenceArtifact` (CR-5 §16) | REUSE. `dea:Provenance` references them rather than duplicating evidence semantics. |
| `dea:Evidence` provenance relationship taxonomy | RECONCILE. `dea:has-provenance` uses the declared `traceability` category; `provenance` is not a member of the controlled relationship category set. |
| `provenance-dimension` | REGISTER as a new dimension, consistent with `measurement-dimension` and `temporal-dimension`. Also added to the visualization overlay dimensions. |
| Existing `valid_from` / `valid_to` semantics (per the dea-metamodel skill's CR-006 lineage) | RETAIN -- the new `valid_time` dimension extends the existing validity semantics. |
| W3C PROV alignment | INVESTIGATE -- CR-MET-011 must document the alignment decision; per the user-supplied CR §5, the architecture should investigate alignment. |

## 10. Definition of Done

- [x] 7 temporal dimensions encoded on Observation as a nested `temporal` object (Q17b) with `observed_at` + `recorded_at` required and 9 named fields; asserted by `test_section3_*`.
- [x] `dea:ReportingPeriod` introduced as a **specialization** of `dea:TemporalInterval`; 7 period types, period semantics, and the conditional-field rules (instantaneous and point-in-time carry no interval; rolling requires `anchor_reference` + `window_size`; irregular requires `interval_count`; fiscal requires `calendar_reference` + `fiscal_year_ref`).
- [x] `dea:Provenance` introduced with all 11 attributes required (Q18a); 1:1 with Observation.
- [x] W3C PROV alignment documented (Q18a disposition): entity / activity / responsible-party mapping recorded in the schema description and the entity definition.
- [x] 5 record states encoded on `MeasurementObservation.record_state`; `dea:corrects` introduced; `dea:supersedes` retained (already carried Observation on both endpoints via CR-MET-004). The conflated `supersedes_observation` field is deprecated.
- [x] Historical reconstruction test cases implemented and passing (28 tests in `test_032_temporal_provenance.py`).
- [x] Schema validation passes; conformance suite passes; registry and specification regenerated.
- [x] Backward compatibility: existing Observation records (under the assessment-profile `dea:Observation`) remain valid; the deprecated `supersedes_observation` field is retained for one release cycle.

## 11. NOT-list

- This CR does NOT collapse the 7 temporal dimensions into one timestamp.
- This CR does NOT silently overwrite original Observations with corrections. Historical auditability is preserved.
- This CR does NOT require recalculation of historical results when a Metric definition changes. Reproducibility is achieved via the provenance and version references.

## 12. Cross-references

- User-supplied CR-MET-011: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-006-012.md` (lines 1311-1542).
- CR-MET-000 reconciliation: `/home/hermes/dea-work/dea-metamodel/change-requests/CR-MET-000.md` §4.
- Existing temporal semantics: CR-006 (Temporal & Lifecycle Semantics) and the `temporal: true` flag on relationships.
- W3C PROV: https://www.w3.org/TR/prov-overview/ (alignment investigation).
- Kanban: T-MET umbrella #429; this CR is card #441; ADR-MET-011 is card #453.
- Stream: Stream C (Historical intelligence and decision support).
