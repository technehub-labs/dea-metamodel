# CR-MET-012 -- Establish Measurement Analytics, Performance Intelligence and Decision Intelligence Integration

| Field | Value |
|---|---|
| Status | Accepted (landed via PR #188) |
| Target repository | `technehub-labs/dea-metamodel`, `technehub-labs/dea-architecture-framework`, future measurement runtime / analytics repos |
| Author | Emmanuel A. Otchere |
| Date | 2026-10-18 |
| Phase | 6 (Runtime and intelligence) |
| Depends on | CR-MET-001 through CR-MET-011; ADR-MET-009, ADR-MET-011, ADR-MET-013, ADR-MET-016 |
| Kanban | T-MET umbrella #429; this CR is card #442 |
| Programme stream | Stream C (Historical intelligence and decision support) |

## 1. Background and problem statement

The Metric capability becomes strategically valuable when measurement information can be used to understand enterprise conditions, evaluate performance, anticipate outcomes, and inform decisions.

OpenDEAM must progress beyond simply storing Metrics and Observations. It should enable an enterprise to answer questions such as:

- Are we achieving our strategic objectives?
- Which capabilities are underperforming?
- What is driving deterioration in operational performance?
- Are our investments producing the expected outcomes?
- Which risks are increasing?
- Where should transformation investments be directed?
- What is likely to happen if current performance trends continue?
- Which interventions are likely to produce the greatest improvement?

These require an integrated measurement intelligence architecture. The key architectural decision (per the user-supplied CR-MET-012 §12): "OpenDEAM's Metric capability provides the semantic measurement foundation for enterprise decision intelligence. It should not absorb the responsibilities of analytical engines, forecasting platforms, or workflow orchestration systems."

## 2. Objective

Establish the architectural foundation for using Metric definitions, Measurements, Observations, Assessments, Targets, Outcomes, and contextual enterprise information to support analytical and decision-intelligence capabilities.

## 3. Analytical capability architecture (per the user-supplied CR §3)

6 complementary analytical capabilities are established.

| Capability | Question | Examples |
|---|---|---|
| Descriptive | What happened? | Current / historical performance; performance by org unit; capability performance; process performance; technology reliability; strategic objective attainment |
| Diagnostic | Why did it happen? | Variance analysis; contributing factor analysis; root-cause investigation; cross-domain correlation; process bottleneck; risk driver analysis |
| Predictive | What is likely to happen? | Customer churn prediction; capacity demand forecasting; operational failure prediction; revenue projections; workforce attrition; risk exposure forecasting |
| Prescriptive | What should we do? | Recommended interventions; resource allocation; optimization recommendations; capability improvement priorities; risk mitigation; transformation sequencing |
| Comparative | How do we compare? | Organizational benchmarking; business-unit comparison; industry benchmarking; historical comparison; target vs actual; capability maturity comparison |
| Scenario and simulation | What would happen if? | Alternative investment scenarios; transformation scenarios; resource allocation; operational capacity; risk mitigation; strategic outcome scenarios |

## 4. Measurement intelligence architecture (per the user-supplied CR §4)

4 layers are distinguished.

| Layer | Contents |
|---|---|
| Enterprise semantic foundation | Metric, Measurement, Observation, Subject, Classification |
| Measurement context | Baseline, Target, Threshold, Benchmark, Reporting Period, Provenance |
| Analytical services | Descriptive, Diagnostic, Predictive, Prescriptive, Comparative, Simulation |
| Enterprise decision intelligence | Strategic decisions, investment prioritization, transformation, performance management, risk management |

The layers describe architectural responsibilities, not necessarily separate repositories or deployable applications.

## 5. Information type separation (per the user-supplied CR §7)

8 information types are distinguished; the first 6 are differentiated outputs that must not be conflated or published as equivalent measurement facts.

| Information type | Meaning |
|---|---|
| Observation | Recorded measurement result |
| Estimate | Estimated value based on available information |
| Forecast | Predicted future value |
| Simulation result | Output of a modeled scenario |
| Recommendation | Suggested course of action |
| Decision | Authorized management choice |
| Metric | Defines what is measured |
| Assessment | Interprets evidence against criteria |

The user-supplied CR §7 explicitly states "These must not be conflated or published as equivalent measurement facts." The disposition question (see Section 9, Q20) is whether the 6 differentiated outputs are 6 separate entities or a single `result_type` enum on one Result entity.

## 6. Integration with Assessment, Outcome, Decision (per the user-supplied CR §8)

10 existing OpenDEAM concepts are integrated.

| OpenDEAM concept | Measurement intelligence role |
|---|---|
| Metric | Defines what is measured |
| Observation | Provides measurement evidence |
| Assessment | Interprets evidence against criteria |
| Outcome | Describes an intended or achieved result |
| Strategic Objective | Establishes strategic direction |
| Scenario | Supports alternative future analysis |
| Decision | Records an authorized choice |
| Initiative | Implements an intervention |
| Capability | Provides an enterprise performance context |
| Value Stream | Provides value-delivery performance context |
| Risk | Provides risk-monitoring context |

The relationship between Outcome and Observation is particularly important: an Outcome may be supported by multiple Observations over time; one Observation may contribute evidence to multiple related assessments or outcomes.

## 7. Decision points

### Q20 (new from CR-MET-012 §7). Information type representation

- **(a) 6 separate entities: `dea:Observation` (already in scope), `dea:Estimate`, `dea:Forecast`, `dea:SimulationResult`, `dea:Recommendation`, `dea:Decision`**. Each has its own lifecycle and provenance; the 6 are first-class.
- **(b) A single `dea:AnalyticalResult` entity with a `result_type` enum (observation | estimate | forecast | simulation_result | recommendation | decision)**. Recommended; reduces entity proliferation; preserves the user-supplied distinction via the type discriminator.
- **(c) Reuse the existing `dea:Observation` for all 6 types with a `kind` field**. Loses the independent lifecycle; not recommended.

**DISPOSITION (binding): Q20b-prime.** A `dea:AnalyticalResult` entity with a **4-value** `result_type` enum: `estimate`, `forecast`, `simulation_result`, `recommendation`.

Audit findings that reduced the enum from 6 to 4:

- `observation` is **already** a first-class entity: `dea:MeasurementObservation` (CR-MET-001). Adding `observation` to an `AnalyticalResult` enum would create a second identity for the same concept.
- `decision` is **already** a first-class entity: `dea:Decision` (CR-4 §13), with its own schema carrying `statement`, `rationale`, `authority_ref`, `confidence`, `uncertainty`, and `assumptions`. Absorbing it as an enum value would destroy that identity and conflate an authorized management choice with a derived analytical output.

The user-supplied §7 requirement that these types "must not be conflated or published as equivalent measurement facts" is therefore enforced **structurally**, not merely by a discriminator: `dea:MeasurementObservation` and `dea:Decision` cannot appear as `AnalyticalResult.result_type` values at all. `dea:informs-decision` is the explicit relationship from an analytical result to the Decision it supports, keeping the distinction visible without duplicating identity.

The 4 remaining types share a common provenance, quality, and confidence model. Every result MUST cite `evidence_refs`, MUST carry `provenance_reference` (CR-MET-011 §5), and MUST declare `confidence`.

### Q21 (new from CR-MET-012 §5). Aggregation rules

- **(a) Reuse the CR-MET-005 aggregation operators and the new `dea:MeasurementAggregation` entity (per CR-MET-000 Q4a)**. Aggregation compatibility rules (percentages not summed; ratios not averaged; weighted means need explicit weights) are inherited from CR-MET-005. Recommended.
- **(b) Introduce a new `dea:AnalyticsAggregation` entity with a different operator set**. Loses the binding with CR-MET-005; not recommended.
- **(c) Compute aggregations on demand without a model entity**. No reusable model; not recommended.

**DISPOSITION (binding): (a), as recommended.** Aggregation reuses the CR-MET-005 `dea:AggregationRule` and its 11-operator controlled set (`SUM`, `COUNT`, `MIN`, `MAX`, `MEAN`, `WEIGHTED_MEAN`, `MEDIAN`, `PERCENTILE`, `RATE`, `RATIO`, `DISTINCT_COUNT`). No new aggregation entity is introduced.

`AnalyticalResult.aggregation_rule_ref` is REQUIRED on every result, so an aggregate without a declared rule is inadmissible. The CR-MET-005 rule that a simple arithmetic average is **not** a universal aggregation method is asserted directly: a rollup across organizational units on a ratio-valued Metric MUST declare a weighted rule.

### Q22 (new from CR-MET-012 §6). Correlation vs causation

- **(a) A `dea:Correlation` entity that records the observed correlation without implying causation**. Recommended.
- **(b) A `dea:CausalHypothesis` entity that records an analytical hypothesis with explicit confidence and uncertainty**. Distinct from Correlation.
- **(c) Both `dea:Correlation` and `dea:CausalHypothesis` are first-class entities; the distinction is preserved**. Matches the user-supplied CR §6.

**DISPOSITION (binding): (c), as recommended.** `dea:Correlation` and `dea:CausalHypothesis` are both introduced as first-class entities.

The distinction is enforced structurally, not merely by naming:

- `dea:Correlation` carries a REQUIRED `confusion_guard` field that MUST be `false`. A correlation asserts association only.
- `dea:CausalHypothesis` requires a `mechanism` (a hypothesis without a mechanism is an assertion) plus a `validation_state` recording how far it has been tested: `asserted`, `correlation_supported`, `experiment_running`, `validated`, `refuted`.
- `dea:correlates` is **symmetric** (correlation has no direction); `dea:tests-hypothesis` is directed from Correlation to CausalHypothesis.
- A hypothesis MUST record `counter_evidence` and a `falsification_test`. A hypothesis with no recorded counter-evidence is either trivially true or not honestly recorded.
- A hypothesis's `confidence` MAY NOT exceed the absolute coefficient of its strongest supporting correlation. A 0.63 correlation cannot license a 0.9 causal confidence.

The Metric metamodel does **not** become a causal inference engine; it provides the semantic references and provenance needed by analytical services.

## 8. Reconciliation with existing analytics constructs

| Existing construct | Disposition |
|---|---|
| CR-010 (Scenario, Simulation, Digital Twin & Decision Intelligence) | RETAIN -- the new Metric capability extends CR-010's Phases 4-7 (DMM Integration, Simulation Adapters, Agentic Scenario Generation, Digital Twin Foundation). |
| CR-012 (Enterprise Intelligence & Advanced Agentic Runtime) | RETAIN -- the new Metric capability provides measurement evidence for CR-012's signal-promotion and governed-agentic-action layer. |
| `dea:Scenario`, `dea:Decision`, `dea:Initiative` (existing) | RETAIN -- the new analytics integration references these via the existing relationship vocabulary. |
| `dea:AnalyticalService` | DOES NOT EXIST. Audited: no entity matching AnalyticalService, Estimate, Forecast, Prediction, SimulationResult, Recommendation, Correlation, or CausalHypothesis exists in the metamodel. `dea:Signal` and `dea:Scenario` exist but are environmental-indicator and temporal-scenario constructs respectively, not analytical outputs. |
| `dea:Decision` (CR-4 §13) | RETAIN UNCHANGED. Already first-class with `authority_ref`, `rationale`, `confidence`, `uncertainty`, `assumptions`. Excluded from `result_type`; reached via `dea:informs-decision`. |
| `dea:MeasurementObservation` (CR-MET-001) | RETAIN UNCHANGED. Already first-class. Excluded from `result_type`. |
| `dea:derives-from` | EXTEND. Source gains `dea:AnalyticalResult`, target gains `dea:MeasurementObservation`: the evidence chain from an analytical output back to its source Observations. |
| `dea:produces` | NOT EXTENDED. An analytical output is deliberately NOT a produced measurement result; the relationship is `dea:derives-from`, which preserves the distinction the user-supplied §7 requires. |

## 9. Definition of Done

- [x] 6 analytical capabilities (Section 3) encoded as `AnalyticalResult.analytical_capability` with all 6 exercised by the fixture.
- [x] 4 intelligence-stack layers (Section 4) verified to map onto existing entities by `test_section4_four_stack_layers_have_a_home_in_the_metamodel`; the layers are architectural responsibilities, not separate applications.
- [x] `dea:AnalyticalResult` introduced with a 4-value `result_type` enum (Q20b-prime).
- [x] 5 end-to-end reference scenarios (user-supplied §11) encoded as conformance fixtures and validated:
  - Scenario A -- Strategic performance management (Objective to KPI to Observation to Assessment to Decision).
  - Scenario B -- Digital maturity improvement (DMM dimension to Metric to Assessment evidence to Maturity evaluation to Improvement Initiative to Outcome measurement).
  - Scenario C -- Operational optimization (Business Process to Operational Metric to Variance to Root-cause to Intervention to Re-measurement).
  - Scenario D -- Enterprise risk intelligence (Risk to KRI to Observation to Threshold breach to Risk Assessment to Mitigation Decision).
  - Scenario E -- Transformation benefits realization (Initiative to Expected Outcome to Baseline to Target to Observations to Benefits Realization to Investment Decision).
- [x] Aggregation rules inherited from CR-MET-005 via `dea:AggregationRule` (Q21a); `aggregation_rule_ref` required on every result.
- [x] `dea:Correlation` and `dea:CausalHypothesis` introduced (Q22c) with the confusion guard, the mechanism requirement, counter-evidence, falsification test, and the confidence-ceiling rule.
- [x] Schema validation passes; conformance suite passes; registry and specification regenerated.
- [x] The 5 reference scenarios are documented as conformance test cases with per-hop type resolution.

## 10. NOT-list

- This CR does NOT absorb the responsibilities of analytical engines, forecasting platforms, or workflow orchestration systems. The metamodel provides the semantic foundation; runtime systems provide the engines.
- This CR does NOT conflate Observation, Estimate, Forecast, Simulation result, Recommendation, and Decision. They are differentiated by `result_type`.
- This CR does NOT collapse Correlation and Causal Hypothesis into a single entity.
- This CR does NOT redefine existing Scenario, Decision, or Initiative concepts. The new analytics integration references them.

## 11. Cross-references

- User-supplied CR-MET-012: `/home/hermes/dea-work/dea-catalog-metrics/00_inbox/CR-MET-006-012.md` (lines 1547-1969).
- CR-MET-000 reconciliation: `/home/hermes/dea-work/dea-metamodel/change-requests/CR-MET-000.md` §4.
- CR-010 (Scenario / Decision Intelligence): `change-requests/CR-010.md` Phases 4-7.
- CR-012 (Enterprise Intelligence): `change-requests/CR-012.md`.
- Kanban: T-MET umbrella #429; this CR is card #442; ADR-MET-016 is card #458.
- Stream: Stream C (Historical intelligence and decision support).
