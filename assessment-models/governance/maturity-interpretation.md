# Maturity Interpretation

CR-AM-04 formalises maturity as an **interpretation** of an AssessmentResult, not a
property of the AssessmentModel itself. The AssessmentModel declares a
versioned MaturityModel reference; the AssessmentResult records the actual
determination produced for a subject, period, scenario, and execution.

## Chain of derivation

```text
MaturityModel
     │ defines
     ▼
MaturityLevel
     ▲
     │ determines
     │
AssessmentDetermination
     ▲
     │ aggregates
     │
AssessmentResult
     ▲
     │ summarises
     │
AssessmentExecution
     ▲
     │ executes
     │
AssessmentModel
```

## Determination contract

A result-level `determination` (see `schemas/assessment-result.schema.json#/$defs/determination`) carries:

- `score` — exact-value result from the versioned ScoringModel
- `maturity_model` — versioned MaturityModel reference
- `maturity_level` — interpreted integer level
- `finding` — assessment conclusion text
- `confidence` — `low` / `medium` / `high`
- `evidence` — versioned evidence references

A `maturity_interpretation` (see `$defs/maturityInterpretation`) carries:

- `model` — versioned MaturityModel reference
- `dimensions[]` — per-dimension level, score, confidence
- `overall.level` — declared aggregate level
- `overall.method` — declared aggregation rule
- `overall.rationale` — narrative explanation of the chosen method

## Aggregation contract

Aggregation is **declared**, never implicit. Allowed methods:

| Method | Behaviour |
|--------|-----------|
| `min` | Overall = minimum dimension level |
| `average` | Overall = rounded arithmetic mean |
| `weighted-average` | Requires explicit per-dimension weights |
| `threshold` | Requires an explicit threshold rule |
| `dominant-level` | Overall = most-frequent level (ties broken by the lower level) |
| `custom` | Requires an explicit custom rule and rationale |

`weighted-average`, `threshold`, and `custom` are explicitly refused by the runtime
unless the supplementary rule is supplied (see `runtime/result_operations/service.py::aggregate_levels`).
The default worked method is `dominant-level`; no method silently averages.

## Multi-dimensional maturity

A single result can carry multiple per-dimension levels:

```yaml
maturity_interpretation:
  model: { id: dea:maturity-operations, version: 1.0.0 }
  dimensions:
    - { id: automation, level: 4, score: 2.0, confidence: high }
    - { id: self-governance, level: 3, score: 2.0, confidence: medium }
    - { id: self-adaptation, level: 2, score: 1.0, confidence: low }
  overall:
    level: 3
    method: dominant-level
    rationale: Declared aggregation rule applied to versioned dimension determinations.
```

This prevents the dangerous simplification `enterprise = Level 3` while the actual
result is `Automation L4 / Self-Governance L3 / Self-Adaptation L2`.

## Lineage

Every result retains the exact model versions used. The
`lineage.aggregation_model` reference records the versioned MaturityAggregationModel
that produced the overall level:

```yaml
lineage:
  assessment_model:       { id: ..., version: ... }
  assessment_instrument:  { id: ..., version: ... }
  assessment_execution:   { id: ..., version: ... }
  capability:             { id: ..., version: ... }
  scenario:               { id: ..., version: ... }
  measures:               [{ id: ..., version: ... }]
  scoring_model:          { id: ..., version: ... }
  maturity_model:         { id: ..., version: ... }
  aggregation_model:      { id: dea:aggregation-maturity-dominant-level, version: 1.0.0 }
```

If the maturity model becomes v2, historical results keep their v1
`maturity_interpretation.model` reference and the v2 interpretation is a separate
result. Old results remain interpretable.

## Out of scope

- Statistical benchmarking, peer ranking, or population comparison.
- A generic aggregation engine.
- EnterpriseHeatmapAssessment as a new canonical entity.

## Reference

- CR-AM-04 §2, §5, §6, §8, §11 (AC-AM04-02, AC-AM04-05..07, AC-AM04-09, AC-AM04-11, AC-AM04-12)
- `runtime/result_operations/service.py`
- `schemas/assessment-result.schema.json`
- `schemas/common.schema.json#/$defs/lineage`
