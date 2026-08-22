# CR-AM-04 — Assessment Result Operations & Maturity Interpretation

**Parent:** CR-AM-03  
**Priority:** P0  
**Status:** Proposed

## Objective

Turn a canonical AssessmentModel into a repeatable, traceable result package that distinguishes observations, scores, determinations, evidence, findings, and maturity interpretation—without adding another competing assessment model.

## Result lifecycle

```text
AssessmentModel
      │
      ▼
AssessmentExecution
      ├── Observation
      ├── Evidence
      └── Finding
             │
             ▼
      AssessmentResult
             │
      ┌──────┼───────────┐
      ▼      ▼           ▼
    Score  Maturity    Findings
             │
             ▼
       MaturityLevel
```

The AssessmentModel declares references; the AssessmentResult records the actual determination produced for a subject, period, scenario, and execution.

## Semantic separation

- **Observation** — what was observed, with measure reference and value.
- **Score** — numerical or ordinal evaluation produced by a ScoringModel.
- **Determination** — explicit result-level conclusion containing score, maturity level, finding, confidence, and evidence.
- **Maturity interpretation** — versioned MaturityModel interpretation with per-dimension levels and a declared overall aggregation method.
- **AssessmentResult** — authoritative result package and historical record.
- **Enterprise/capability/scenario view** — projections over result facts, never new assessment models.

## Result granularity

Every result is traceable to:

```text
Organization → Assessment → Scenario → Capability → Measure
          → Observation → Score → Determination → Maturity
```

The existing CR-AM-03 portfolios and examples remain valid inputs. CR-AM-04 adds a deterministic result package without introducing a new core assessment entity.

## Maturity interpretation

Maturity is an interpretation of a result, not a property of an AssessmentModel. The result records:

```yaml
maturity_interpretation:
  model: { id: dea:maturity-operations, version: 1.0.0 }
  dimensions:
    - { id: automation, level: 4, score: 2.0, confidence: high }
    - { id: self-governance, level: 3, score: 2.0, confidence: medium }
  overall:
    level: 3
    method: dominant-level
    rationale: Declared aggregation rule applied to versioned dimension determinations.
```

`lineage.maturity_model` and `lineage.aggregation_model` are both exact-version references. The default worked method is `dominant-level`; `min`, `average`, `weighted-average`, `threshold`, and `custom` require explicit declarations. No method implies a hard-coded average.

## Evidence and reproducibility

A result must include:

- `observations` with versioned measure references;
- `scores` derived from a versioned ScoringModel;
- `determinations` with confidence and evidence references;
- top-level `evidence` and complete lineage;
- `benchmark_eligibility.requirements` with a governed population reference;
- a fixed `source_responses` vector or equivalent deterministic inputs;
- no calculated `rank` or `percentile`.

## Existing artifacts and changes

- New runtime module: `runtime/result_operations/`.
- New conformance tests: `assessment-models/tests/conformance/test_result_operations.py`.
- Canonical schema extensions:
  - `assessment-models/schemas/assessment-result.schema.json`
  - `assessment-models/schemas/assessment-execution.schema.json`
  - `assessment-models/schemas/common.schema.json`
- Add an explicit `aggregation_model` lineage reference and multi-dimensional maturity interpretation contract.
- Keep `compatibility` required on result schemas and preserve the six-axis vocabulary.
- Update registry status to `Implemented` only after AC-AM04-01..14 pass.
- No canonical VERSION bump; this CR is additive and does not introduce a new metamodel entity.

## Acceptance criteria

| ID | Criterion |
|---|---|
| AC-AM04-01 | Canonical AssessmentExecution produces a conformant AssessmentResult. |
| AC-AM04-02 | Result preserves complete versioned lineage. |
| AC-AM04-03 | Observation is distinguishable from Score. |
| AC-AM04-04 | Score is distinguishable from MaturityLevel. |
| AC-AM04-05 | Maturity interpretation references an explicit MaturityModel. |
| AC-AM04-06 | Multi-dimensional maturity results are supported. |
| AC-AM04-07 | Overall maturity aggregation is explicit. |
| AC-AM04-08 | Evidence is traceable to assessment conclusions. |
| AC-AM04-09 | Result can be reproduced from versioned dependencies. |
| AC-AM04-10 | Existing CR-AM-03 migrated assessments can generate results. |
| AC-AM04-11 | Enterprise, Capability, and Scenario result views can be derived. |
| AC-AM04-12 | No benchmark calculation is introduced. |
| AC-AM04-13 | Historical results remain valid after model version changes. |
| AC-AM04-14 | CI validates result, lineage, and maturity conformance. |

## Out of scope

- Generic aggregation engine.
- EnterpriseHeatmapAssessment as a new canonical entity.
- Statistical benchmarking, peer ranking, or population comparison.
- New core metamodel entities.
- Redesign of CR-AM-02/03 assessment instruments or maturity definitions.
