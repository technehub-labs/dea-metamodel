# ADR-MET-010: Provenance is a first-class record, version-pinned, aligned with W3C PROV

- Status: Accepted (landed with CR-MET-011)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-011 (Temporal Semantics, Provenance and Historical Traceability)
- Supersedes: nothing
- Referenced by: CR-MET-011, ADR-MET-011, ADR-MET-016

## Context

CR-MET-011 §5 requires 11 provenance elements on every important Observation, and closes by asking the architecture to investigate alignment with W3C PROV while reusing existing OpenDEAM provenance concepts where they already provide equivalent functionality.

Three positions were on the table:

- A: a `dea:Provenance` entity with the 11 elements, referenced by Observation via `dea:has-provenance`.
- B: a nested `provenance: {...}` object on the Observation.
- C: each provenance element as its own referenced entity.

Position C is entity proliferation. Position B has no independent identity, so it cannot be referenced by anything that needs to reason about provenance as a whole.

## Decision

1. **Position A is adopted.** `dea:Provenance` is introduced with all 11 elements as required properties: `source_ref`, `source_record_ref`, `collection_activity`, `calculation_activity`, `transformation_chain`, `responsible_party_ref`, `configuration_ref`, `formula_version_ref`, `metric_version_ref`, `evidence_refs`, `timestamps`.
2. **`formula_version_ref` and `metric_version_ref` MUST be version-pinned**, carrying an explicit `@version` suffix. This is the mechanism that satisfies the CR-MET-011 §10 architectural decision: historical Observations retain their original semantic context because the Provenance record names the exact definition versions in force, not merely the current ones.
3. **`dea:has-provenance` is 1:1.** Target cardinality is `1`. Provenance is a fact about a single recorded result; sharing one Provenance record between two results would make the version pins ambiguous. A re-run, including a correction, is a new calculation activity and therefore a new Provenance record.
4. **W3C PROV alignment is recorded as follows.** The Observation is the PROV *entity*. `collection_activity` and `calculation_activity` are PROV *activities*. `responsible_party_ref` is the PROV *responsible-party concept*. The implementation deliberately uses the term "responsible party" rather than the PROV role name, to avoid a collision with the metamodel's own accountable-entity vocabulary entry while preserving the semantics.
5. **`dea:Evidence`, `dea:EvidenceSource`, and `dea:EvidenceArtifact` are REUSED, not duplicated.** `source_ref` points at a `dea:EvidenceSource`; `evidence_refs` points at `dea:Evidence` / `dea:EvidenceArtifact` (CR-5 §16). OpenDEAM already had evidence semantics; the Provenance record composes them rather than restating them.
6. The pre-existing `provenance_reference` field on `dea:MeasurementObservation` is a placeholder reading "Full provenance model in CR-MET-011". It is **upgraded in place** to the typed binding reference. No duplicate field is introduced.
7. `dea:Provenance` carries a `reproducibility` block declaring `reproducible`, `reproduction_notes`, and `retention_class`. A record that is not reproducible MUST state why and what retention class governs the retained source. Silently non-reproducible results are how audit trails become decorative.
8. `dea:Provenance` is registered in the `provenance-dimension`, consistent with `measurement-dimension` and `temporal-dimension`, and is added to the visualization overlay dimensions.
9. `dea:has-provenance` uses the **declared `traceability` relationship category**. `provenance` is not a member of the controlled relationship category set, and adding a category for two relationships is not worth the vocabulary cost.

## Consequences

- Positive: the CR-MET-011 §10 architectural decision is implemented by a version pin rather than by immutability. A Metric can evolve normally; what a past Observation *meant* is fixed by its Provenance record.
- Positive: evidence semantics are reused rather than restated, honouring the user-supplied §5 instruction.
- Negative: 1:1 cardinality means a re-run creates a second Provenance record even when the inputs are identical. Storage cost is real; the ambiguity cost of the alternative is worse.
- Negative: the version pin is a string convention (`dea:metric-x@1.2.0`), not a structured reference. Nothing in the metamodel verifies that the pinned version exists or that it matches the `formula_definition.version` on the Metric.
- Negative: `provenance-dimension` is a new dimension, and a new entity dimension requires the visualization profile to be updated or the overlay assertion fails.
- Forecloses: nested provenance object (Position B). It has no identity, so nothing could reference or audit it as a unit.
- Forecloses: per-element provenance entities (Position C).
- Forecloses: a `provenance` relationship category. `traceability` is used instead.

## References

- CR-MET-011 (Temporal Semantics, Provenance and Historical Traceability).
- User-supplied CR-MET-011 §5 (the 11 provenance elements; W3C PROV alignment instruction).
- W3C PROV Overview: https://www.w3.org/TR/prov-overview/
- `schemas/entities/provenance.json`.
- `metamodel/dea-metamodel.yaml`: `dea:has-provenance`; `provenance-dimension`.
- CR-5 §16 (`dea:Evidence`, `dea:EvidenceSource`, `dea:EvidenceArtifact`).
- ADR-011 (Temporal Measurement Architecture).
- ADR-MET-016 (Metric Analytics and Decision Intelligence).
- ADR-013 (Core non-accumulation).