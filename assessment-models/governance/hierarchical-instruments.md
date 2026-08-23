# Hierarchical Dimensions & Assessment Instruments

CR-AM-05A establishes the canonical structure for hierarchical assessment
dimensions and extensible assessment instruments — without coupling
questions to maturity levels.

## Core principle (§3)

> Dimension is a recursively composable assessment taxonomy. A
> sub-dimension is simply a Dimension with a parent Dimension. There is
> no SubDimension class.

Arbitrary depth is permitted; hierarchy changes never require metamodel
changes. The invariants of §8 are enforced by `runtime/instruments/`:
acyclic, no self-parent, unique (id, version) identity, known parents.

## Two taxonomies, kept apart (§5, §23)

| Construct | Role |
|-----------|------|
| **Dimension hierarchy** | Semantic assessment taxonomy |
| **Capability** | The ability being assessed — never a subtype of Dimension |
| **Instrument Section** | Questionnaire organization — never a competing semantic hierarchy |

The same Capability may be organized under different Dimension
structures by different assessment models (§10).

## The evidence chain (§13)

```text
Question → Response → Observation → Indicator/Measure → Criterion → MaturityLevel
```

Never `Question → MaturityLevel`. A Question is a reusable, versioned
asset (§16) and never owns a maturity level (§17) — enforced by the
`question.schema.json` contract (`additionalProperties: false`, no
level-bearing properties).

## Instrument versioning (§15, §29, §32)

The instrument is versioned **independently** of the maturity model:

```text
AOMM v1.0  ────────────── unchanged ──────────────► AOMM v1.0
Instrument v1.0 (30 questions)  →  Instrument v1.1 (42 questions)
```

Adding questions is incremental evolution (§29); changing the maturity
model alongside an instrument revision is not, and is rejected by
`validate_instrument_evolution`.

## Historical integrity (§30, §31, §33)

- Retiring a Question (`status: retired`) never invalidates historical
  AssessmentResults.
- Question replacement is explicit lineage via `supersedes` — the old
  definition is never destroyed.
- Every AssessmentResult preserves `assessment_instrument.id` +
  `version` and the effective question versions in its lineage.
  Non-negotiable: without it, "why did Organization A receive Level 3?"
  cannot be answered six months later.

## Response types (§20)

Twelve controlled types in `vocabulary/response-type.yaml`: boolean,
single-choice, multi-choice, ordinal, numeric, percentage, duration,
frequency, text, date, evidence, measurement. Constraint fields are
type-scoped (choice types require `options`; percentage is pinned to
0–100/percent).

## AssessmentItem (§25)

Contextual binding — dimension, capability, criterion, measure,
sequence, required, applicability — lives on the AssessmentItem inside
the instrument, not on the global Question. The same Question can serve
different instruments differently.

## Non-goals (§40)

No SubDimension/SubSubDimension classes; no Question→Criterion or
Question→MaturityLevel inheritance; no Capability→Dimension
inheritance; no presentation concerns in the MaturityModel; no
benchmark ranking or heatmap aggregation (CR-AM-05/06/07 own those);
no hard-coded five-level scale.
