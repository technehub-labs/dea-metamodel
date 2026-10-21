# Metric Capability Map

A single human-facing view of the OpenDEAM Metric capability: what the 13 entities mean, how they connect, and which CR and ADR established each one.

- Status: Authoritative overview. Where this document and the canonical source disagree, **the canonical source wins** (`metamodel/dea-metamodel.yaml`).
- Programme: CR-MET-000..012 (sealed 2026-10-18)
- Entities: 13 introduced or re-membershiped by the programme
- Vocabulary version: 0.16.0
- Canonical entity count: 163 entities, 120 relationships

---

## 1. What this capability is

The Metric capability answers one question: **how do we know what we are measuring is real, comparable, and trustworthy?**

It does not compute metrics, schedule collections, or run analytics. It defines what a measurement *is*, what makes it *valid*, and what must be recorded for someone to reconstruct it years later. Analytics engines, forecasting platforms, and workflow orchestration systems provide the runtime (ADR-MET-015, ADR-MET-016).

The capability sits on three commitments:

1. **A measurement is a definition plus a collection plus a recorded value.** Each is separately identified, because a correct formula that was never run is not a measurement, and a run with no recorded definition cannot be reproduced.
2. **A past result must remain interpretable.** Metric definitions evolve; a 2024 value must not silently acquire 2026 semantics (ADR-MET-010, ADR-MET-011).
3. **An inferred value is never the same kind of thing as a measured one.** This is enforced structurally, not by convention (ADR-MET-016).

---

## 2. The map

Six functional layers. Read top to bottom for the lifecycle of a measurement; read left to right within a layer for the parts that serve it.

```
                      DEFI NITION LAYER
  ┌────────────────────────────────────────────────────────────┐
  │  PerformanceMetric          IndicatorDesignation           │
  │  what to measure, how      KPI / KRI / KCI / SLI /        │
  │  it is computed            Operational: the management     │
  │  (CR-MET-001, 002, 005,    commitment, separate from       │
  │   008, 010)                the definition (CR-MET-008)     │
  └───────────────┬──────────────────────────────┬─────────────┘
                  │ applies-metric               │ has-designation
                  ▼                              ╰──▶ (same Metric, many designations)
      COLLECTION LAYER                          ╭─────────────╮
  ┌──────────────────────────────────────────┐   │ Governance, │
  │  Measurement                             │◀──╯ quality,   │
  │  the governed act of collecting a        │    conformance │
  │  value; 10 lifecycle states,             │    (CR-MET-010)│
  │  8 execution modes (CR-MET-001, 004)     │                │
  └───────────────┬──────────────────────────┴────────────────┘
                  │ produces
                  ▼
                  RESULT LAYER
  ┌────────────────────────────────────────────────────────────┐
  │  MeasurementObservation    Provenance     ReportingPeriod │
  │  the recorded value,      version-pinned   the interval   │
  │  its unit, its confidence  evidence of what (CR-MET-011)   │
  │  (CR-MET-001, 003, 011)    was actually run  │             │
  └───────────────┬──────────────────────────────┤             │
                  │                              │ applies-period
                  ▼                              ▼             │
              EVALUATION LAYER            (7 entity kinds report│)
  ┌────────────────────────────────────────────────────────────┐
  │  Baseline  PerformanceTarget  Threshold                    │
  │  reference  aspiration       breach boundary                │
  │  ────────────────────────────────────────────────────────   │
  │  PerformanceInterpretation  the recorded JUDGMENT           │
  │  (CR-MET-006; ADR-MET-007: Variance is a derived view,      │
  │   not an entity. What must be auditable is the judgement.)  │
  └───────────────┬────────────────────────────────────────────┘
                  │ informs-decision
                  ▼
              ANALYSIS LAYER                          (ADR-MET-016)
  ┌────────────────────────────────────────────────────────────┐
  │  AnalyticalResult      Correlation      CausalHypothesis   │
  │  estimate, forecast,   association      asserted           │
  │  simulation_result,    ONLY; required   mechanism; needs   │
  │  recommendation        confusion_guard  counter-evidence;  │
  │  (CR-MET-012)          = false (Q22c)  confidence ceiling  │
  └────────────────────────────────────────────────────────────┘
```

---

## 3. The entities

| Entity | Alias | Role | CR | ADR |
|---|---|---|---|---|
| `dea:PerformanceMetric` | MTR | What to measure and how it is computed | CR-MET-001, 002, 005, 010 | ADR-MET-001, 002, 003 |
| `dea:IndicatorDesignation` | | KPI / KRI / KCI / SLI / Operational commitment | CR-MET-008 | ADR-MET-008 |
| `dea:Measurement` | MMT | The governed act of collecting a value | CR-MET-001, 003, 004 | ADR-MET-002, 015 |
| `dea:MeasurementObservation` | MOBS | The recorded value, with unit and confidence | CR-MET-001, 003, 011 | ADR-MET-002, 011 |
| `dea:Provenance` | | Version-pinned evidence of what was actually run | CR-MET-011 | ADR-MET-010 |
| `dea:ReportingPeriod` | | The reporting interval | CR-MET-011 | ADR-MET-011 |
| `dea:Baseline` | | Reference point for comparison | CR-MET-006 | ADR-MET-007 |
| `dea:PerformanceTarget` | | Aspiration, with direction | CR-MET-006 | ADR-MET-007 |
| `dea:Threshold` | | Breach boundary, with severity level | CR-MET-006 | ADR-MET-007 |
| `dea:PerformanceInterpretation` | | The recorded judgement | CR-MET-006 | ADR-MET-007 |
| `dea:AnalyticalResult` | | Inferred output: estimate, forecast, simulation, recommendation | CR-MET-012 | ADR-MET-016 |
| `dea:Correlation` | | Association only | CR-MET-012 | ADR-MET-016 |
| `dea:CausalHypothesis` | | Asserted mechanism, with validation state | CR-MET-012 | ADR-MET-016 |

`dea:PerformanceMetric`, `dea:Measurement`, and `dea:MeasurementObservation` already existed before the programme and were **re-membershiped and extended**, not created. `dea:PerformanceMetric` retains `class_alias: MTR` from the assessment profile.

---

## 4. The relationships

23 relationships touch the capability. Grouped by what they do:

### Core flow
| Relationship | Source | Target | Says |
|---|---|---|---|
| `dea:applies-metric` | PerformanceMetric | Measurement | This Metric definition is the one this Measurement applies |
| `dea:produces` | Measurement | MeasurementObservation | The Measurement executed produced the recorded Observation |
| `dea:has-provenance` | Measurement, MeasurementObservation, PerformanceMetric | Provenance | The record of what was actually run |
| `dea:corrects` | MeasurementObservation | MeasurementObservation | The target was **wrong** and this is the restatement |
| `dea:supersedes` | (10 types) | (10 types) | A **newer authoritative** value exists for the same period |

`corrects` and `supersedes` are not interchangeable. Correction asserts the original was wrong; supersession asserts something newer exists.

### Design-time versus runtime
| Relationship | Cardinality | Says |
|---|---|---|
| `dea:applies-subject` | 3 sources, 2 targets | This Metric is *intended* to apply to these subjects |
| `dea:measured-by` | **16** sources | This subject *was* measured by this Metric |
| `dea:measures-subject` | 1 source, **16** targets | The subject this Measurement covered |

The design-time declaration and the runtime fact are separate relations; neither implies the other. The 16-type lists are mirrored deliberately so a Metric cannot declare applicability to a subject it could never be measured against.

### Temporal
| Relationship | Says |
|---|---|
| `dea:applies-period` | Measurement, Observation, Baseline, Target, Threshold, Interpretation, and Designation all report on this ReportingPeriod |

### Evaluation
| Relationship | Says |
|---|---|
| `dea:references` | PerformanceMetric to Baseline |
| `dea:specifies-target` | PerformanceMetric to PerformanceTarget |
| `dea:has-target` | StrategicObjective to PerformanceTarget |
| `dea:interprets` | PerformanceInterpretation to a MeasurementObservation or the assessment-side `dea:Observation` |
| `dea:constrains` | **Also now** Threshold to PerformanceMetric, alongside Requirement and Guardrail |
| `dea:benchmarked-against` | **Also now** PerformanceMetric to its benchmark peers, alongside AssessmentResult and Technology |

### Governance
| Relationship | Says |
|---|---|
| `dea:has-designation` | PerformanceMetric to IndicatorDesignation |
| `dea:informs-decision` | AnalyticalResult or PerformanceInterpretation to `dea:Decision` |

### Analysis
| Relationship | Says |
|---|---|
| `dea:analyses-metric` | AnalyticalResult to the PerformanceMetric, Observation, Baseline, Target, or Threshold it draws on |
| `dea:derives-from` | **Extended** so AnalyticalResult and MeasurementObservation are both valid: the evidence chain |
| `dea:correlates` | **Symmetric** (Correlation, PerformanceMetric, Observation) |
| `dea:tests-hypothesis` | Correlation to CausalHypothesis, directed |

---

## 5. Integration surface

The capability is not an island. These are the pre-existing relationships the programme extended, which is how Metric semantics reach the rest of the metamodel:

- `dea:measured-by` grew from **7 to 16** source types: AssessmentDimension, Control, DataEntity, MaturityModel, OrganizationalUnit, Policy, Risk, Service, ValueStream, ApplicationComponent.
- `dea:assessed-by` : AIMLModel, BusinessCapability, BusinessProcess, SolutionComponent, and TechnologyRadarEntry are assessed by a PerformanceMetric.
- `dea:constrains` : Threshold and PerformanceMetric now constrain alongside Requirement, Guardrail, Regulation, and Constraint.
- `dea:specializes` : **ReportingPeriod specializes TemporalInterval**, adding period semantics to an existing kernel rather than duplicating its clocks.
- `dea:produces` : Measurement and Observation now produce results alongside BusinessProcess and BusinessCapability.
- `dea:informs-decision` reaches `dea:Decision`, keeping an analytical recommendation distinct from an authorized management choice.
- `dea:supersedes` carries Measurement and MeasurementObservation on both endpoints.

`dea:Activity` is deliberately **not** a Metric endpoint. `dea:BusinessProcess` is the decomposition path; activity-level measurement is sub-measurement through the catalog-internal Activity/Task hierarchy.

---

## 6. The catalog: 5 admitted Metrics

`dea-catalog-metrics` publishes reusable definitions. It does **not** redefine Metric: canonical semantics stay in `dea-metamodel`.

| Catalog record | Subject | Direction | Domain lesson it teaches |
|---|---|---|---|
| `dea:metric-customer-retention-rate` | customer | higher is better | Dual designation: one definition, both a lagging KPI and a leading KRI |
| `dea:metric-operating-margin` | financial | higher is better | A ratio. May **not** be summed across business units; requires a weighted rule |
| `dea:metric-mean-time-to-recovery` | technology architecture | lower is better | Time-based, so it requires a ReportingPeriod to be interpretable |
| `dea:metric-data-completeness` | information architecture | higher is better | Bounded 0 to 100; its Threshold semantics differ from a ratio's |
| `dea:metric-control-effectiveness-rate` | governance | higher is better | Demonstrates the KCI designation and its mandatory owner plus escalation path |

Six validation gates govern admission: schema, measurement conformance, MECE coverage, evidence anchors, threshold semantics, and the dual-anchor model (measurable-entity kind plus reputability tier).

---

## 7. The rules a reader is most likely to violate

Six constraints do most of the work. Each is machine-checked.

1. **An inferred value is never a measurement.** `AnalyticalResult.result_type` cannot be `observation` or `decision`; both already exist as first-class entities. The types are separated structurally, not by a soft discriminator.
2. **A correlation is never a causation.** Every Correlation carries a required `confusion_guard` that must be `false`. A CausalHypothesis requires a mechanism, counter-evidence, and a falsification test, and **its confidence may not exceed the absolute coefficient of its strongest supporting correlation**.
3. **A ratio is never summed.** A ratio or dimensionless index must aggregate with `WEIGHTED_MEAN` and an explicit weight basis. This is the single most consequential rule in the programme: an enterprise margin that is the average of its units' margins is arithmetically valid and analytically meaningless.
4. **Every forecast carries uncertainty.** `forecast` and `simulation_result` must declare uncertainty, model reference, and horizon. A recommendation must carry `value: null` and record alternatives considered.
5. **A correction never overwrites.** The original Observation is retained; the correction is a new record citing what it replaces.
6. **Governance is per-object, not blanket.** Definition, Measurement, Observation, and Indicator each have their own governance object and approval. A Metric can be perfectly defined and nobody owns its collection.

---

## 8. What this capability does not do

- It does not compute metrics, schedule collections, or orchestrate workflows. No executor, no scheduler, no queue, no retry policy, no concurrency model (ADR-MET-015).
- It does not implement an analytics engine, a forecasting platform, or a causal inference engine (ADR-MET-016).
- It does not establish a parallel governance regime. Metric governance composes with the existing authority (ADR-MET-014).
- It does not model Variance as an entity, nor Expected Value as an entity, nor Benchmark as a new entity (ADR-MET-007).
- It does not widen the base lifecycle vocabulary. The five governance refinement states are a declared **specialization** scoped to exactly four entities, so that the other 159 entity schemas are unaffected (ADR-MET-014).

---

## 9. Known gaps

Stated plainly rather than left to be discovered:

1. **`viewer/metamodel.svg` is stale.** It was last regenerated 2026-09-05, before this programme. It contains zero references to any Metric entity. `viewer/entity-graph.json` holds 54 entities against the canonical 163.
2. **No entity carries the `measurement-dimension` tag** that CR-MET-000 assigned to `dea:PerformanceMetric`, while `visualization/profile/visualization.yaml` lists `measurement-dimension` as an overlay dimension. The overlay declares a dimension nothing populates.
3. **No `dea:AnalyticalService` entity exists.** `dea:analyses-metric` records the semantic dependency; the service itself is properly a runtime and deployment concern.
4. **Expression well-formedness is unchecked.** `Metric.formula_definition.expression` is a string. Nothing validates that it parses or matches its declared operators and inputs.

Items 1 and 2 mean the visual map will not agree with this document until a regeneration pipeline exists.

---

## 10. Where to go next

| Want to | Read |
|---|---|
| Understand a decision and what it forecloses | `docs/adr/ADR-MET-001..016` |
| See the full change with rationale | `change-requests/CR-MET-001..012` |
| Understand the Metric *definition* attributes | ADR-MET-001, 002, 003 |
| Understand units, formulas, aggregation | ADR-MET-005, 006, 013 |
| Understand governance and conformance | ADR-MET-014 |
| Understand history and reproducibility | ADR-MET-010, 011 |
| Understand analytics and causation | ADR-MET-016 |
| See working instances | `dea-catalog-metrics` (5 Metrics, 6 gates) |
| See machine-readable truth | `metamodel/dea-metamodel.yaml`, `specification/semantic-inventory.yaml` |

---

Cardinal author: Emmanuel A. Otchere (per CR-MM-04 R1).