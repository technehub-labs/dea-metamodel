# Assessment Views & Aggregation

CR-AM-05 establishes the canonical view layer over `AssessmentResult`. The
result is the persistent analytical fact; a view is a governed projection of
that fact, never the source of truth.

## Architectural principle

```text
AssessmentModel  →  AssessmentExecution  →  AssessmentResult  →  AssessmentView
                                       (canonical fact)     (derived projection)
```

`AssessmentView ≠ AssessmentModel`, `AssessmentView ≠ MaturityModel`,
`AssessmentView ≠ EnterpriseHeatmapAssessment`. The view layer introduces
exactly two new entity kinds — `AssessmentView` and `AggregationModel` —
plus one cell structure (`ViewCell`). No new first-class `EnterpriseAssessment`,
`HeatmapAssessment`, or `CapabilityHeatmapAssessment` is introduced
(CR-AM-05 §35).

## View types

The closed vocabulary lives in `vocabulary/view-types.yaml`. Five initial
types ship with CR-AM-05:

| Type | Purpose |
|------|---------|
| `enterprise_profile` | Whole-organisation profile aggregating capabilities and scenarios |
| `capability_profile` | Single-capability view of measures, scores, and maturity |
| `scenario_profile` | Scenario-anchored aggregation across capabilities and measures |
| `heatmap` | Multi-dimensional cell-structured view |
| `trend` | Time-series view over historical AssessmentResults |

Presentation formats (`radar`, `table`, `bar-chart`) are explicitly **not**
view types and remain outside the metamodel.

## Aggregation contract

Every view declares its aggregation method and AggregationModel version:

```yaml
aggregation:
  method: dominant-level
  model:
    id: dea:aggregation-capability-maturity
    version: 1.0.0
```

`AggregationModel.method` is one of the closed set declared in
`vocabulary/aggregation-methods.yaml`. CR-AM-05 §11 explicitly refuses to
hard-code "average" as the canonical enterprise rule.

### Score vs Maturity aggregation are distinct

`AggregationModel.input.type` declares which result-level quantity the
aggregation consumes (`score`, `maturity`, `measure`, or `observation`).
A view consuming `score` and one consuming `maturity` are different views;
conflating them is forbidden by construction.

## Missing data is not zero

CR-AM-05 §26: if `Technology Architecture = 78` and `Technology Platform`
has no assessment, the heatmap must show `Platform = N/A`, not `0`.
Coverage is reported explicitly:

```yaml
coverage:
  value: 0.5          # assessed / applicable
  assessed: 1
  applicable: 2
```

`AggregationModel.missing_data.method` declares how missing inputs are
handled: `exclude`, `propagate`, `explicit-unknown`, or `treat-as-zero`.

## Compatibility guard

CR-AM-05 §15: incompatible model versions cannot silently participate in a
trend or aggregate. `AggregationModel.compatibility.required_axes` and
`min_compatible_axes` declare the guard. `AssessmentViewEngine.aggregate`
excludes results whose compatibility declaration does not satisfy the guard.

## Coverage is a first-class dimension

CR-AM-05 §28: every cell carries coverage + confidence, not just a value:

```yaml
cells:
  - subject: { id: dea:capability-technology-architecture, type: capability }
    value: { score: 78, normalized: 0.78, level: 4 }
    maturity: { model: { id: dea:maturity-technology, version: 1.0.0 }, level: 4 }
    confidence: high
    coverage: { value: 1.0, assessed: 2, applicable: 2 }
    source_results: [dea:result-technology-2026-q1, dea:result-technology-2026-q2]
```

## Confidence survives aggregation

The aggregated `confidence` is the **lowest** source confidence. If the
sources carry `high` and `medium`, the cell is `medium`. This preserves
precision and prevents false-precise cells.

## Benchmark separation

CR-AM-05 §17, §18: enterprise views do not imply benchmark status.
`AssessmentView` does not include `benchmark` or `benchmark_eligibility`
fields. A view can filter source results by `benchmark_eligibility.status`
when preparing data for the future benchmark layer (CR-AM-06, CR-AM-07).

## Reproducibility

Every view lists its `source_results` with exact versions and records
`lineage` with versioned references to the source `assessment_models`,
`scoring_models`, `maturity_models`, and `aggregation`. Re-running the
engine against the same source results and AggregationModel produces an
identical view.

## Reference

- CR-AM-05 §3, §5, §6, §17, §18, §25, §26, §28
- `schemas/assessment-view.schema.json`
- `schemas/aggregation-model.schema.json`
- `vocabulary/view-types.yaml`
- `vocabulary/aggregation-methods.yaml`
- `model/assessment-metamodel.puml` (Assessment View package)
- `runtime/views/`
