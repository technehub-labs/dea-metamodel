# OpenDEA Assessment Metamodel v1 — Narrative companion

This is the text companion to [`assessment-metamodel.puml`](./assessment-metamodel.puml),
the canonical PlantUML class diagram of the OpenDEA Assessment Metamodel v1
(implemented by CR-AM-02; architecture per CR-AM-01).

The PlantUML is the **normative visual**. This document explains the
**why** behind the visual and links each entity to the schema that
declares it, the CR that defines it, and the acceptance criterion it
satisfies.

## 1. Why the metamodel exists

Before CR-AM-01, the assessment ecosystem was **instrument-centric**:

```
Assessment Instrument
    ├── Dimension
    │      └── Question
    ├── Scoring
    └── Maturity Target
```

This was sufficient for questionnaire-based assessments. It was
insufficient for CR-AM-01's broader requirements: enterprise, capability,
scenario, maturity, benchmark, and longitudinal assessments using a
common information model.

CR-AM-01 separated the concepts. CR-AM-02 implements that separation as
the canonical metamodel.

## 2. Entity index

The metamodel has **four clusters of entities**, each realising a phase
of the assessment lifecycle.

### 2.1 Core assessment entities (CR-AM-02 §6 P0)

| Entity | Schema | Defining CR | Purpose |
|---|---|---|---|
| **AssessmentModel** | `schemas/assessment-model.schema.json` | CR-AM-01 §7.1, CR-AM-02 §7.1 | Normative specification of what an assessment evaluates. |
| **AssessmentInstrument** | `schemas/assessment-instrument.schema.json` | CR-AM-01 §7.2, CR-AM-02 §7.2 | Concrete realisation of an AssessmentModel (questionnaire, workshop, etc.). |
| **AssessmentExecution** | `schemas/assessment-execution.schema.json` | CR-AM-01 §7.3, CR-AM-02 §7.3 | A recorded occurrence of running an instrument. |
| **AssessmentResult** | `schemas/assessment-result.schema.json` | CR-AM-01 §7.4, CR-AM-02 §7.4 | The persistent output of an execution. |
| **AssessmentDimension** | `schemas/assessment-dimension.schema.json` (referenced) | CR-AM-01 §17, CR-AM-02 §6 | A dimension within an AssessmentModel. |
| **AssessmentQuestion** | `schemas/assessment-question.schema.json` (referenced) | CR-AM-01 §17, CR-AM-02 §7.8 | A prompt used to obtain information relevant to one or more measures. |

### 2.2 Semantic entities (CR-AM-02 §6 P0)

| Entity | Schema | Defining CR | Purpose |
|---|---|---|---|
| **Capability** | `schemas/capability.schema.json` | CR-AM-01 §8, CR-AM-02 §7.5 | An independently identifiable organisational ability. Reusable across AssessmentModels. |
| **Scenario** | `schemas/scenario.schema.json` | CR-AM-01 §9, CR-AM-02 §7.6 | The defined context in which a capability is exercised. Critical for benchmarking. |
| **Measure** | `schemas/measure.schema.json` | CR-AM-01 §10, CR-AM-02 §7.7 | A defined observable property. Independent of questionnaire scoring. |
| **Evidence** | `schemas/evidence.schema.json` | CR-AM-01 §11, CR-AM-02 §6 | Provenance layer supporting observations. |

### 2.3 Interpretation entities (CR-AM-02 §6 P0)

| Entity | Schema | Defining CR | Purpose |
|---|---|---|---|
| **ScoringModel** | `schemas/scoring-model.schema.json` | CR-AM-01 §12, CR-AM-02 §7.9 | Reusable transformation of observations into scores. |
| **MaturityModelReference** | (within `assessment-model.schema.json`) | CR-AM-01 §13, CR-AM-02 §7.10 | Versioned reference to a MaturityModel — replaces the legacy `maturity_target` denormalisation. |

### 2.4 Governance entities (CR-AM-02 §6 P0)

| Entity | Schema | Defining CR | Purpose |
|---|---|---|---|
| **ModelReference** | `schemas/common.schema.json` (`$defs.ModelReference`) | CR-AM-01 §22, CR-AM-02 §10 | The shape of every cross-model dependency. |
| **ModelVersion** | (within `common.schema.json`) | CR-AM-01 §9, CR-AM-02 §9 | SemVer-stamped version identifier. |
| **Lineage** | (within `common.schema.json`) | CR-AM-01 §24, CR-AM-02 §12 | Result lineage — exact model versions used. |
| **Compatibility** | `schemas/compatibility.schema.json` | CR-AM-01 §25, CR-AM-02 §11 | Six-axis compatibility declaration. |

### 2.5 Deferred-but-declared entities (CR-AM-02 §6)

| Entity | Schema | Status |
|---|---|---|
| **BenchmarkModel** | (referenced from `assessment-result.schema.json`) | Schema-stubbed in v1.0.0; full implementation in CR-AM-06. |
| **AssessmentView** | (referenced from `assessment-result.schema.json`) | Schema-stubbed in v1.0.0; full implementation in CR-AM-07. |

## 3. Lifecycle of an assessment (CR-AM-02 §8)

```
AssessmentModel
       │
       ▼
AssessmentInstrument
       │
       ▼
AssessmentExecution
       │
       ▼
Observations / Evidence
       │
       ▼
AssessmentResult
       │
       ├── Score
       ├── Findings
       ├── Maturity Interpretation
       └── Benchmark Eligibility
```

The distinction per CR-AM-02 §8:

| Concept | Represents |
|---|---|
| AssessmentModel | Definition |
| AssessmentInstrument | Administration mechanism |
| AssessmentExecution | Event |
| AssessmentResult | Determination |

## 4. Independence across the entities (CR-AM-02 §5.2 + §22 AC-08..AC-12)

The metamodel enforces **semantic separation**:

- A **Capability** is not an AssessmentDimension.
- A **Scenario** is not an Assessment.
- A **Measure** is not an AssessmentQuestion.
- A **ScoringModel** is not an assessment question inline scoring.
- A **MaturityModel** is not embedded in an AssessmentModel.

Each entity has its own identifier (URI), its own version (SemVer), and
its own lifecycle. This is what allows a Capability to be referenced
by multiple AssessmentModels (AC-08), a Scenario to be referenced by
multiple Assessments (AC-09), a Measure to be reused (AC-10), a
ScoringModel to be swapped (AC-11), and a MaturityModel to be referenced
and versioned independently (AC-12).

## 5. Versioning (CR-AM-02 §9, §11)

All normative models use **Semantic Versioning**. The compatibility
declaration (CR-AM-02 §11) is a six-axis declaration:

- schema
- semantic
- scoring
- maturity
- result
- benchmark

A model version declares each as `compatible` or `incompatible` against
the previous version. **Not all dimensions need to move together** — a
PATCH may legitimately set `benchmark: incompatible` while keeping
`schema`, `semantic`, `scoring`, `maturity`, `result` all `compatible`.

The full vocabulary is at
[`vocabulary/compatibility-types.yaml`](../vocabulary/compatibility-types.yaml).

## 6. Lineage and historical integrity (CR-AM-02 §5.4, §12, §22 AC-14 + AC-15)

Every AssessmentResult carries a `lineage:` block listing the exact
versions of every model artefact used:

```yaml
lineage:
  assessment_model: { id: ..., version: ... }
  assessment_instrument: { id: ..., version: ... }
  capability: { id: ..., version: ... }
  scenario: { id: ..., version: ... }
  measures: [...]
  scoring_model: { id: ..., version: ... }
  maturity_model: { id: ..., version: ... }
```

Changing a model version **must not** mutate a historical result. The
result is an immutable record that survives across model evolution.

## 7. Benchmarking boundary (CR-AM-02 §13, §22 AC-18)

CR-AM-02 establishes the **data structures** for benchmark eligibility but
does not implement the benchmark engine:

```
AssessmentResult
       │
       ▼
BenchmarkEligibility  ← declared explicitly per result
       │
       ▼
BenchmarkResult       ← deferred to CR-AM-06
```

A score alone **never** implies benchmarkability. The eligibility
declaration considers the AssessmentModel, Capability, Scenario, Measure,
ScoringModel, Evidence, Population, and MeasurementPeriod — all listed
in CR-AM-02 §13.

## 8. Enterprise heatmap as a derived view (CR-AM-02 §14, §22 AC-16)

The enterprise heatmap is **not** a separate assessment model. It is a
view over assessment results:

```
AssessmentResult[]
       │
       ▼
Aggregation
       │
       ▼
EnterpriseAssessmentView
       │
       ▼
Heatmap
```

Each heatmap cell traces back to a specific AssessmentResult, the
AssessmentModel version that produced it, the Measure, and the measurement
period. The heatmap is therefore **explainable and reproducible**.

## 9. Legacy compatibility (CR-AM-02 §15 + §16)

The legacy `instrument.schema.json` (vendor-copied at
`migrations/v1-instrument/legacy-instrument.schema.json`) is **not
removed**. It is the **Legacy Instrument Model v1** — supported
indefinitely.

The formal migration mapping at
[`migrations/v1-instrument/mapping.yaml`](../migrations/v1-instrument/mapping.yaml)
projects every legacy field to a canonical field. The first migration
output (Technology Assessment, AC-07) is at
[`migrations/v1-instrument/canonical-technology-migration.yaml`](../migrations/v1-instrument/canonical-technology-migration.yaml).

Round-trip preservation is asserted by `tests/migration/test_v1_to_metamodel.py`.

## 10. Acceptance criteria mapping (CR-AM-02 §22)

| AC | Where satisfied |
|---|---|
| AC-01 Canonical Metamodel | `model/assessment-metamodel.puml` + this document |
| AC-02 Normative Schemas | `schemas/*.schema.json` (12 files) |
| AC-03 Controlled Vocabulary | `vocabulary/relationship-types.yaml`, `vocabulary/compatibility-types.yaml`, `vocabulary/lifecycle-status.yaml` |
| AC-04 Versioning | `common.schema.json` `$defs.semver` + `governance/versioning.md` |
| AC-05 Legacy Preservation | `migrations/v1-instrument/legacy-instrument.schema.json` + `compatibility.schema.json` |
| AC-06 Canonical Representation | `examples/canonical-technology-assessment.yaml` |
| AC-07 Technology Migration | `migrations/v1-instrument/canonical-technology-migration.yaml` + `tests/migration/test_v1_to_metamodel.py` |
| AC-08 Capability Independence | `capability.schema.json` — no required foreign reference to AssessmentModel |
| AC-09 Scenario Independence | `scenario.schema.json` — no required foreign reference to AssessmentModel |
| AC-10 Measure Independence | `measure.schema.json` — no required foreign reference to AssessmentModel |
| AC-11 Scoring Independence | `scoring-model.schema.json` — no required foreign reference to AssessmentModel |
| AC-12 Maturity Independence | `maturity-bands-v2.yaml` + `v2-to-v1-legacy-name-map.yaml` (v2-beta model files) — required independent `version` field |
| AC-13 Execution Separation | `assessment-execution.schema.json` `assessment_model: ... required` — multiple executions may reference one model |
| AC-14 Result Lineage | `assessment-result.schema.json` `required: [lineage, ...]` |
| AC-15 Historical Integrity | `governance/lifecycle.md` §5 retired-definition retention rule |
| AC-16 Heatmap Traceability | `sections/14` of CR-AM-02 — view as derived aggregation + the explicit `AssessmentView` schema stub |
| AC-17 Compatibility | `compatibility.schema.json` + `vocabulary/compatibility-types.yaml` + `tests/compatibility/test_compatibility_states.py` |
| AC-18 Benchmark Protection | `governance/compatibility.md` §6 + `benchmark-eligibility.example.yaml` |
| AC-19 Reproducibility | Result lineage + ModelVersion + Compatibility — declared |
| AC-20 No Breaking Migration | `migrations/v1-instrument/mapping.yaml` is the explicit non-breaking migration contract |

## 11. Subsequent CRs (CR-AM-02 §24)

The metamodel is the foundation for the following queued CRs:

- **CR-AM-03** — Assessment Model Migration (broad migration of all current instruments)
- **CR-AM-04** — Capability and Scenario Catalogs
- **CR-AM-05** — Assessment Result and Evidence Framework (broader)
- **CR-AM-06** — Benchmark Model and Eligibility (full benchmark engine)
- **CR-AM-07** — Assessment Views and Enterprise Heatmaps
- **CR-AM-08** — Assessment Analytics and Benchmarking

The sequence is intentional. **Do not implement benchmarking before
the canonical result and lineage model is stable.** CR-AM-02 establishes
that stability.
