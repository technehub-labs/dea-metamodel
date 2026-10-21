# ADR-MET-008: KPI, KRI, KCI, SLI and Operational are designations on one Metric, not five entities

- Status: Accepted (landed with CR-MET-008)
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-008 (Indicator Designations)
- Supersedes: nothing
- Referenced by: CR-MET-008, ADR-MET-014

## Context

KPI, KRI, KCI, SLI, and Operational are the labels organizations use when they commit to managing a measurement. The user-supplied CR-MET-008 §4 raises the question directly: does a designation change the *measurement* or only the *management commitment*?

Three positions were on the table:

- A: five specialized entities (`dea:KPI`, `dea:KRI`, `dea:KCI`, `dea:SLI`, `dea:OperationalIndicator`), each specializing `dea:Metric`.
- B: one `dea:IndicatorDesignation` entity carrying a `designation_type` discriminator.
- C: designations remain catalog-side labels with no metamodel representation.

## Decision

1. **Position B is adopted.** A designation changes the management commitment, not the measurement. Position A would fork `dea:PerformanceMetric` five ways for what is one definitional fact (how the value is computed) plus one governance fact (who committed to managing it).
2. `dea:IndicatorDesignation` is introduced with `designation_type` as a 5-value controlled set: `KPI`, `KRI`, `KCI`, `SLI`, `Operational`.
3. **One Metric MAY carry multiple designations.** This is the load-bearing consequence of Position B. `dea:metric-customer-retention-rate` in the CR-MET-009 pilot carries both `dea:designation-customer-retention-kpi-lagging` and `dea:designation-customer-retention-kri-leading`. Under Position A this would have been two entities computing the same value.
4. The Metric identity is preserved across designations (EGV-004). A designation never creates a new measurement definition; it attaches a management commitment to an existing one.
5. `dea:IndicatorDesignation` carries `measurement_orientation` (3 values: `leading`, `lagging`, `neutral`) separately from `dea:Metric.orientation_classification` (4 values: `leading`, `lagging`, `diagnostic`, `concurrent`). The Metric axis is analytical; the designation axis is managerial. A designation may declare `neutral` because "KPI" and "leading" are not synonyms, and conflating them would make every leading indicator a KPI by definition.
6. `dea:has-designation` is introduced with source `dea:PerformanceMetric` cardinality 0..* and target `dea:IndicatorDesignation` cardinality 1.
7. A `KCI` designation MUST carry `associated_objective_ref` pointing to a control objective, `accountable_owner_ref` pointing to a control owner, and `escalation_rules` for remediation. This is the binding requirement from user-supplied §5.3: a key control indicator without an accountable owner and an escalation path is a control indicator nobody acts on.
8. `dea:IndicatorDesignation` also carries `management_purpose`, `organizational_scope`, `reporting_frequency` (8 values), `target_reference`, `threshold_reference`, `effective_period`, and `approval_status` (4 values). Governance completeness is therefore enforced on the designation, not only on the Metric.

## Consequences

- Positive: a Metric with two designations is one definition and two management commitments. Reporting over both does not require reconciling two calculation paths.
- Positive: designation governance (owner, escalation, approval) is attached to the thing that is actually managed, not inferred from the Metric.
- Negative: a query for "all KPIs" must filter on `designation_type` rather than resolve an entity type. This is a slower access pattern than a distinct KPI type, and it is the deliberate price of not fragmenting identity.
- Negative: nothing in the metamodel prevents an organization from declaring twenty designations on one Metric. Restraint here is a governance-authority responsibility (ADR-MET-014), not a schema responsibility.
- Forecloses: five specialized entities (Position A). If a future slice finds that one designation genuinely requires different identity, different lifecycle, or different governance, the user-supplied §4 escape clause permits a specialized construct, but it must be justified through an ADR and must use `dea:specializes` (ADR-015), not a fork of Metric.
- Forecloses: catalog-only designations (Position C). The designation carries governance requirements, so leaving it in the catalog would place a governance obligation outside the conformance framework.

## References

- CR-MET-008 (Indicator Designations).
- User-supplied CR-MET-008 §4 (designation versus measurement), §5.3 (KCI requirements), §4 escape clause.
- `schemas/entities/indicator-designation.json`.
- `metamodel/vocabularies/classifications.yaml`: `IndicatorDesignation.designation_type`, `.measurement_orientation`, `.reporting_frequency`, `.approval_status`.
- `dea-catalog-metrics` CR-MET-009 pilot record `dea:metric-customer-retention-rate` (dual designation).
- EGV-004 (identity continuity).
- ADR-MET-014 (Metric Governance and Lifecycle).
- ADR-013 (Core non-accumulation).
- ADR-015 (kernel+specialization template).