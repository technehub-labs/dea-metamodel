# Result Lineage & Operations

CR-AM-04 turns an AssessmentExecution into a reproducible AssessmentResult and
formalises the chain:

```text
Observation → Score → AssessmentDetermination → MaturityLevel → AssessmentResult
                                              → Evidence         → Confidence
                                              → Finding
```

## Versioned lineage

Every AssessmentResult carries an exact-version lineage block (see
`schemas/common.schema.json#/$defs/lineage`):

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
  aggregation_model:      { id: ..., version: ... }
```

Subsequent model changes do **not** mutate historical results. The lineage
is the canonical anchor for reproducibility and auditability (AC-AM04-02,
AC-AM04-09, AC-AM04-13).

## Lifecycle

```text
AssessmentModel
      │
      ▼
AssessmentExecution (status: completed)
      ├── Observation
      ├── Evidence
      └── Finding
             │
             ▼
      AssessmentResult (status: completed)
             │
      ┌──────┼───────────┐
      ▼      ▼           ▼
    Score  Maturity    Findings
             │
             ▼
       MaturityLevel (interpretation, not model property)
```

## Result views

The AssessmentResult is the canonical analytical primitive. Three views are
derived over the same result (AC-AM04-11):

| View | Anchor |
|------|--------|
| Enterprise | assessment, period, capability, measure |
| Capability | capability version, measure references, scores |
| Scenario   | scenario version, capability version, measure references, observation references |

These are projections, not separate assessment models. Adding a fourth view
(Mode A diagnostic heatmap, Mode C scenario benchmark) does not require a new
AssessmentModel.

## Evidence traceability

Every determination references the evidence that supports it. Result-level
evidence is now a first-class field (see `$defs/evidenceRecord`):

```yaml
evidence:
  - { id: dea:evidence-technology-core, version: 1.0.0, description: ..., confidence: high }
```

The result lineage records the same evidence references through the execution.

## Result package

The AssessmentResult combines:

- lineage (model version references)
- compatibility declaration (six-axis)
- observations (measure values)
- scores (per-dimension)
- determinations (score, maturity level, finding, confidence, evidence)
- maturity_interpretation (model, dimensions, overall)
- benchmark_eligibility (declared, with versioned requirements)
- source_responses (deterministic reproduction vector)

A canonical result is generated for every CR-AM-03 migrated assessment
(technology / modernization / operations / services-delivery) by the new
runtime module `runtime/result_operations/service.py`.

## Reproducibility

Every result carries a `source_responses` vector that records the question IDs
and values used. Re-running the result operations with the same vector
produces the same result by construction (AC-AM04-09).

## Reference

- CR-AM-04 §1, §2, §3, §4, §7, §9, §11 (AC-AM04-01..14)
- `runtime/result_operations/service.py`
- `schemas/assessment-result.schema.json`
- `schemas/common.schema.json#/$defs/lineage`
- `governance/maturity-interpretation.md`
