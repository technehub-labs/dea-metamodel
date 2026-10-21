# ADR-MET-014: Metric governance integrates with the existing authority; the lifecycle is a declared specialization

- Status: Accepted (landed with CR-MET-010)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-010 (Metric Governance, Quality, Lifecycle and Conformance)
- Supersedes: nothing
- Referenced by: CR-MET-010, ADR-MET-007, ADR-MET-008, ADR-MET-012

## Context

User-supplied CR-MET-010 §10 is explicit: "Metric governance is part of the wider DEA governance architecture. It must not establish an independent governance regime that conflicts with canonical OpenDEAM governance."

Two structural questions had to be settled. First, where does the 7-state Metric lifecycle live relative to the existing metamodel-level lifecycle vocabulary? Second, is one governance approval process enough, or do the four governance concerns need separate ones?

## Decision

1. **No parallel governance regime.** Metric governance integrates with the existing `dea-governance` authority (DEA-ID-000, CR-012, CR-MM-04). All eight governance roles map onto that authority rather than introducing a new one.
2. **The 8 governance roles are `MetricGovernance.governance_role`:** `metric_owner`, `metric_steward`, `measurement_owner`, `data_owner`, `data_steward`, `indicator_owner`, `governance_authority`, `metamodel_authority`. One individual MAY fulfil multiple roles, but accountability MUST remain explicit; a record carrying only a governance object and no role is non-conformant.
3. **Four independent governance objects** are distinguished per Q16a: `dea:MetricGovernance.governance_object` carries `definition`, `measurement`, `observation`, `indicator`. Each has its own lifecycle and approval. Treating all four as one approval process was rejected because a Metric definition can be perfectly governed while its Measurements are not, or vice versa. Indicator governance reuses the `dea:IndicatorDesignation` lifecycle from CR-MET-008.
4. **Q15a-prime: the 7-state Metric lifecycle is declared as a SPECIALIZATION over the base lifecycle vocabulary, not as a widening of it.** The pre-authored CR-MET-010 recommended widening `metamodel/vocabularies/lifecycle.yaml` from 5 values to 10. This was rejected on blast-radius grounds: `test_cr3r_lifecycle_vocabulary` asserts schema-enum **equality** with the vocabulary, so widening forces all **134** entity schemas to admit five governance refinement states they have no governance process for. That is an ADR-013 anti-accumulation violation.
5. The base vocabulary remains the 5 metamodel-level states: `proposed`, `planned`, `active`, `deprecated`, `retired`. A `specializations.metric-governance` block declares the 5 refinement values (`under_review`, `approved`, `published`, `under_revision`, `suspended`) with an explicit `applies_to` list naming exactly four entities: `Metric`, `Measurement`, `MeasurementObservation`, `IndicatorDesignation`.
6. The specialization also declares the canonical chain `proposed -> under_review -> approved -> published -> active`; the `active` branches (`under_revision`, `suspended`, `deprecated`); and the terminal set (`deprecated`, `retired`). Terminal is strictly `deprecated` and `retired`.
7. **`test_cr3r_lifecycle_vocabulary` was relaxed from equality to subset containment and strengthened** with two negative assertions: a specialized schema MUST NOT admit lifecycle values outside its specialization scope, and a non-specialized schema MUST NOT admit refinement values at all. The invariant is now stricter than before, not weaker. This is recorded because a reader should not find a relaxed test and assume a weakened guarantee.
8. **Three conformance levels** are implemented as three test classes: Level 1 structural (`test_029`), Level 2 semantic (`test_030`), Level 3 governance (`test_031`).
9. **The semantic-change assessment process** is encoded as `MetricChange.semantic_change_disposition` (5 values: `revise_in_place`, `new_version`, `new_identity`, `deprecate`, `replace`) and `MetricChange.change_severity` (4 values: `cosmetic`, `additive`, `substantive`, `semantic_breaking`). **Binding rule: a `semantic_breaking` change MUST require a new identity and MUST NOT be represented as a cosmetic version update.** A change that alters the fundamental semantic meaning of a Metric cannot hide behind a version bump.
10. A Metric that is deprecated MUST NOT be silently deleted, particularly when historical Observations reference it.

## Consequences

- Positive: governance composes with the existing authority. No new regime, no new authority, no conflict to resolve later.
- Positive: four governance objects means a governance gap can be located precisely. "This Metric is well defined but nobody owns the collection" is now expressible.
- Positive: the lifecycle refinement reaches exactly four entities instead of all 134. The blast radius of a governance decision is proportionate.
- Positive: the conformance test was strengthened while being relaxed, so the widening that was rejected is now positively forbidden.
- Positive: the semantic-breaking rule prevents the most damaging governance failure in measurement programmes, which is a changed meaning shipped as a patch bump.
- Negative: the declared-specialization form is more complex than a widened vocabulary. A reader must check both the base list and the `applies_to` scope.
- Negative: `test_cr3r_lifecycle_vocabulary` no longer guarantees that every schema uses every vocabulary value. It guarantees the converse, which is the property that actually matters.
- Negative: three conformance levels is three test files to maintain, and Level 3 assertions depend on the fixture declaring complete role accountability.
- Forecloses: widening the base lifecycle vocabulary for domain-specific refinements (unless a future slice demonstrates a shared refinement that genuinely belongs to all entities).
- Forecloses: one blanket governance approval covering definition, measurement, observation, and indicator.
- Forecloses: representing a semantic-meaning change as a version bump.

## References

- CR-MET-010 (Metric Governance, Quality, Lifecycle and Conformance).
- User-supplied CR-MET-010 §3 (four governance objects), §4 (eight roles), §5 (7-state lifecycle), §7 (three conformance levels), §8 (change assessment), §10 (no parallel regime).
- `metamodel/vocabularies/lifecycle.yaml` (`specializations.metric-governance`).
- `metamodel/vocabularies/classifications.yaml`: `MetricGovernance.governance_object`, `.governance_role`, `MetricConformance.conformance_level`, `.conformance_verdict`, `MetricChange.semantic_change_disposition`, `.change_severity`.
- `schemas/entities/metric.json` (`governance`, `conformance`).
- `tests/conformance/test_009_entity_rules.py` (`test_cr3r_lifecycle_vocabulary`, subset-containment invariant).
- `dea-governance` (DEA-ID-000, CR-012, CR-MM-04).
- ADR-MET-007 (Baseline, Target and Threshold Architecture).
- ADR-MET-008 (KPI, KRI and KCI Representation).
- ADR-MET-012 (Measurement Quality and Confidence).
- ADR-013 (Core non-accumulation).