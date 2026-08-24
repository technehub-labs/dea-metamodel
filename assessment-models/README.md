# assessment-models/

> The **assessment sub-metamodel** of OpenDEA. A coherent sub-tree inside the canonical `technehub-labs/dea-metamodel` repository that defines the conceptual model, JSON Schemas, controlled vocabularies, governance policy, and maturity scoring v2 for the assessment domain.

---

## Where this lives

This sub-tree is part of the canonical OpenDEA metamodel. There is **no separate `dea-metamodel` repo for assessment**. The previous attempt to host this in a separate `Assessment-Models/dea-metamodel` repo (with a dual-authority arrangement) has been retired — see the move note on [PR #1 in the archived repo](https://github.com/Assessment-Models/dea-metamodel/pull/1).

**Single source of authority:** `technehub-labs/dea-metamodel/assessment-models/`. Anything that needs to refer to an assessment sub-metamodel concept points here.

---

## What this sub-tree contains

```
assessment-models/
├── README.md                                  ← you are here
├── CHANGELOG.md                               ← version history of this sub-tree
├── LICENSE                                     ← MIT
├── .gitignore
├── .github/workflows/ci.yml                   ← CI validation
│
├── change-requests/
│   ├── CR-AM-01-supplement-metamodel-v1.md     ← the supplementary CR (canonical, md5 c0f086be...)
│   └── cr-index.md                            ← sub-tree CR index
│
├── model/
│   └── assessment-metamodel.puml              ← canonical PlantUML class diagram
│
├── schemas/                                    ← 12 JSON Schemas (Draft 2020-12)
│   ├── common.schema.json                     ← shared $defs (identifier, version, modelReference, ...)
│   ├── assessment-model.schema.json           ← central contract — verbatim from supplement §4
│   ├── assessment-result.schema.json          ← persistent output — verbatim from supplement §6
│   ├── assessment-instrument.schema.json
│   ├── assessment-execution.schema.json
│   ├── capability.schema.json
│   ├── scenario.schema.json
│   ├── measure.schema.json
│   ├── evidence.schema.json
│   ├── scoring-model.schema.json
│   ├── compatibility.schema.json
│   └── relationship.schema.json
│
├── vocabulary/                                 ← 12 controlled vocabularies
│   ├── assessment-types.yaml
│   ├── relationship-types.yaml                ← 17 types + legacy aliases
│   ├── lifecycle-status.yaml                  ← 7 states incl. retired
│   ├── evidence-types.yaml
│   ├── view-types.yaml                        ← CR-AM-05: 5 view types
│   ├── aggregation-methods.yaml               ← CR-AM-05: 12 aggregation methods
│   ├── compatibility-types.yaml
│   ├── benchmark-status.yaml                  ← CR-AM-06: 6 eligibility states
│   ├── eligibility-reasons.yaml               ← CR-AM-06: 13 machine-actionable reason codes
│   ├── dimension-status.yaml                  ← CR-AM-05A: 4 dimension lifecycle states
│   ├── question-status.yaml                   ← CR-AM-05A: 4 question lifecycle states
│   └── response-type.yaml                     ← CR-AM-05A: 12 response types
│
├── examples/                                   ← 5 canonical YAML examples
│   ├── legacy-technology-instrument.yaml      ← current-style + migration-layer interpretation
│   ├── canonical-technology-assessment.yaml   ← canonical form (no longer owns capability or maturity)
│   ├── zero-touch-operations-assessment.yaml  ← proves maturity_models: [] works (CR-AM-01 §13)
│   ├── zero-touch-operations-result.yaml      ← independently useful AssessmentResult
│   └── benchmark-eligibility.yaml             ← explicit benchmark eligibility declaration
│
├── governance/                                 ← 9 policy docs
│   ├── versioning.md                          ← SemVer + explicit compatibility metadata
│   ├── compatibility.md                       ← six compatibility axes + benchmark eligibility
│   ├── result-lineage.md                      ← CR-AM-04 result lineage & operations
│   ├── maturity-interpretation.md             ← CR-AM-04 multi-dimensional maturity interpretation
│   ├── views.md                               ← CR-AM-05 view & aggregation policy
│   ├── benchmark-eligibility.md               ← CR-AM-06 eligibility & cohort policy
│   ├── comparison-policy.md                   ← CR-AM-07 comparison policy + CR-AM-08 hand-off
│   ├── hierarchical-instruments.md            ← CR-AM-05A dimension/instrument policy
│   └── lifecycle.md                           ← seven lifecycle states + retired ≠ deleted
│
└── maturity/                                   ← maturity scoring v2 (this PR's other landing)
    ├── README.md                              ← entry point for the v2 scheme
    ├── maturity-bands-v2.yaml                 ← canonical v2 band definitions (Emergent / Structured / ...)
    ├── v2-to-v1-legacy-name-map.yaml          ← explicit alias table v2 ↔ v1
    ├── examples/
    │   └── effort-adjusted-value.yaml         ← worked example: score 80 → 49.2 effort-adjusted value
    └── governance/
        └── migration.md                       ← 4-phase migration plan (Phase A → D)

├── views/                                      ← CR-AM-05 derived projections over AssessmentResults
│   ├── enterprise/technology-heatmap.yaml     ← capability × period heatmap
│   ├── capability/technology-architecture-profile.yaml  ← capability profile
│   ├── scenario/service-assurance-profile.yaml ← scenario profile
│   └── trend/technology-maturity-trend.yaml   ← historical trend

├── aggregation/                                ← CR-AM-05 AggregationModel contract
│   └── examples/capability-score.yaml         ← canonical AggregationModel example

├── benchmark/                                  ← CR-AM-06 benchmark eligibility & cohorts
│   ├── cohort-examples/
│   │   └── telecom-service-assurance-2026.yaml ← §6 worked cohort
│   └── eligibility-examples/
│       ├── eligible-result.yaml               ← §11 valid determination shape
│       └── not-comparable-result.yaml         ← §11 invalid determination shape
```

The `schemas/` tree additionally contains `benchmark-cohort.schema.json`
(CR-AM-06) and the CR-AM-05A instrument layer: `dimension.schema.json`
(recursive hierarchy — no SubDimension class), `criterion.schema.json`,
`indicator.schema.json`, `question.schema.json`,
`response-specification.schema.json`, and `assessment-item.schema.json`
— 19 schemas total. `examples/hierarchical-maturity-assessment.yaml` is
the CR-AM-05A worked example (3-level dimension hierarchy, 2 capabilities,
2 criteria, 6 questions, instrument v1.0, result lineage).

---

## Architectural principle (canonical)

From CR-AM-01 §5:

> Assessments define how something is measured; capabilities define what can be assessed; scenarios define the context in which it is assessed; maturity models define progression; benchmark models define comparability; assessment results preserve what was observed.

Every schema and example in this sub-tree implements some clause of that sentence. If a proposed change violates any clause, the change is wrong.

---

## Relationship to existing canonical content

This sub-tree is **complementary, not duplicative** with existing canonical content in the parent repo:

| Existing canonical | This sub-tree |
|---|---|
| `metamodel/profiles/assessment/profile.yaml` | — defines constraints for assessment-related entities **inside** the core metamodel |
| `metamodel/profiles/dmm/scoring.yaml` | — DMM scoring profile (maturity-model-specific) |
| `pydantic/assessment.py` + `pydantic/assessment_*.py` | — generated Pydantic models for those core entities |
| `pydantic/benchmark.py`, `pydantic/capability.py`, `pydantic/evidence.py`, `pydantic/measure.py`, `pydantic/scenario.py` | — generated Pydantic models for the same domain |
| `models/scenarios/customer-platform-replacement.yaml`, `customer-service-baseline.yaml` | — concrete scenario examples |
| — | **This sub-tree defines the assessment sub-metamodel** (AssessmentModel, AssessmentInstrument, AssessmentExecution, AssessmentResult + Capability + Scenario + Measure + Evidence + ScoringModel + BenchmarkModel + MaturityModel as optional interpretation). PlantUML + 12 JSON Schemas + governance. |

The existing canonical profile + Pydantic models continue to be authoritative for *entity types within the core metamodel*. This sub-tree is authoritative for the *assessment sub-metamodel*: the schemas that describe what an AssessmentModel is, what an AssessmentResult contains, what a MaturityModel looks like (with v2 scoring), and how compatibility is declared.

Future CRs may add forward-pointers from `metamodel/profiles/assessment/profile.yaml` to this sub-tree. That work is out of scope for CR-014 itself.

### Upstream profile

The OpenDEA assessment profile (`metamodel/profiles/assessment/profile.yaml`, id `dea:assessment`, version 1.0.0) defines the **vocabulary surface** — the `dea:Assessment*`, `dea:Maturity*`, `dea:Evidence*`, and `dea:Benchmark*` entities and the 13 relationships that participate in assessment — that this sub-tree operationalises.

The forward-pointer landed by **CR-015** (committed via this sub-tree's README + the reciprocal `cross_references:` block on `profile.yaml`) makes the relationship explicit: the profile is the *vocabulary contract*; this sub-tree defines the *schemas, conventions, governance, and maturity bands* that any concrete assessment instrument or maturity model consumes. When new `dea:` entities are added to the profile, their counterparts should also be added to the controlled vocabularies under `vocabulary/` in this sub-tree.

Both pieces live in this same repo (`technehub-labs/dea-metamodel`); the split is a layering convention, not a multi-repo split.

---

## Result operations & maturity interpretation (CR-AM-04)

An AssessmentExecution now produces a reproducible AssessmentResult that
distinguishes Observation, Score, AssessmentDetermination, Evidence, Finding,
and MaturityLevel. The result carries:

- a `lineage` block with versioned references to the AssessmentModel, Instrument,
  Execution, Capability, Scenario, Measures, ScoringModel, MaturityModel, **and**
  AggregationModel;
- a multi-dimensional `maturity_interpretation` with a declared overall
  aggregation rule (`min`, `average`, `weighted-average`, `threshold`,
  `dominant-level`, `custom`) — never an implicit average;
- a result-level `evidence` array and per-determination `confidence`;
- a deterministic `source_responses` vector for reproducibility;
- `benchmark_eligibility` declared but never calculated (no percentile/rank).

Enterprise, Capability, and Scenario views are projections over the same
result facts. See `governance/result-lineage.md` and
`governance/maturity-interpretation.md` for the contracts. The runtime
module is `runtime/result_operations/` (Python). The conformance tests are
`assessment-models/tests/conformance/test_result_operations.py`
(13 tests, one per AC).

## Maturity scoring v2 (status: beta)

The v2 maturity scoring scheme lives under `maturity/`:

- 5 levels: Emergent / Structured / Systematic / Adaptive / Self-Optimising (replacing v1 CMMI names)
- Non-linear bands: 20 / 25 / 25 / 18 / 12 points
- Per-level `effort_multiplier`: 1.0× / 1.5× / 2.5× / 4.0× / 6.0×

**v1 stays canonical until Phase D promotion.** v2 is advisory throughout Phases A–C. See [`maturity/README.md`](maturity/README.md) for full context and [`maturity/governance/migration.md`](maturity/governance/migration.md) for the 4-phase rollout.

The v2 scoring scheme enables a second-axis metric, **effort-adjusted value**, that exposes the diminishing-returns curve in numbers rather than prose. Worked example: score 80 → 49.2 effort-adjusted value units. See [`maturity/examples/effort-adjusted-value.yaml`](maturity/examples/effort-adjusted-value.yaml).

---

## The four architectural tests

Before any sub-metamodel promotion from v1 to v2, the following four scenarios must work without special-case constructs (CR-AM-01 §16):

| Test | Path |
|------|------|
| **A — Enterprise Heatmap** | Enterprise → Multiple Capabilities → Assessment Results → Heatmap |
| **B — Capability Assessment** | Organisation → Capability → Scenario → Assessment → Result |
| **C — Maturity Assessment** | Capability → Assessment → Result → Maturity Model → Level |
| **D — Benchmark** | Multiple Organisations × Scenario × Capability × AssessmentModel → Benchmark |

All four paths are supported by the schemas in `schemas/`. Concrete examples are in `examples/`. Maturity v2 supports Test C with the new scoring scheme; the maturity model can be referenced via `maturity_models: []` in any assessment model (proves the decoupling in Test B).

---

## Using this sub-tree

### To author a new AssessmentModel

1. Look at `examples/canonical-technology-assessment.yaml` as a template.
2. Validate your YAML against `schemas/assessment-model.schema.json` (with `$ref` resolved from `schemas/common.schema.json`).
3. Declare `purpose:` from `vocabulary/assessment-types.yaml`.
4. Add `compatibility:` metadata when promoting to `stable`.

### To persist an AssessmentResult

1. Look at `examples/zero-touch-operations-result.yaml` as a template.
2. Validate against `schemas/assessment-result.schema.json`.
3. **Always** store the exact `version` of every model reference. Never store a bare id.

### To interpret a result with a maturity model

- Use `maturity_models: [ { id: dea:maturity-technology, version: 1.0.0 } ]` in the AssessmentModel for v1 scoring (CMMI names, linear bands).
- Use `maturity_models: [ { id: dea:maturity-technology, version: 2.0.0 } ]` for v2 scoring (Emergent/Structured/.../Self-Optimising, non-linear bands, effort multipliers).
- A result can be `interpreted-by` either or both — see `schemas/assessment-result.schema.json#/$defs/maturityResult`.

### To evolve a model version

1. Read `governance/versioning.md` — decide PATCH/MINOR/MAJOR.
2. Read `governance/compatibility.md` — declare the six compatibility axes.
3. Bump the version, add a `lineage:` block.

---

## Related

- [CR-014](../../change-requests/CR-014.md) — the parent CR for this sub-tree landing
- [CR-AM-01 supplement](change-requests/CR-AM-01-supplement-metamodel-v1.md) — the assessment sub-metamodel spec
- [CR-AM-01 parent CR](https://github.com/Assessment-Models/dea-catalog-assessment-tools/blob/main/change-requests/CR-AM-01.md) — historical context, decision-points index, 8-phase roadmap
- Canonical OpenDEA metamodel: see `../../metamodel/`, `../../metamodel.yaml`, `../../specification/`
- Archived maturity-models proposal (historical reference): https://github.com/Assessment-Models/dea-catalog-maturity-models/pull/1
- Archived assessment catalog (read-only, contains CR-AM-01 reference): https://github.com/Assessment-Models/dea-catalog-assessment-tools

## Assessment views & aggregation (CR-AM-05)

An `AssessmentView` is a derived projection over one or more
`AssessmentResult` instances. Five view types ship with CR-AM-05:
`enterprise_profile`, `capability_profile`, `scenario_profile`, `heatmap`,
`trend`. Every view declares its `AggregationModel` (id + version) and
method; score and maturity aggregation are distinct; missing data is
N/A, not zero; compatibility guards prevent incompatible results from
silently participating in trends or aggregates. See
`governance/views.md`, `schemas/assessment-view.schema.json`,
`schemas/aggregation-model.schema.json`, and `runtime/views/`.

## Result operations & maturity interpretation (CR-AM-04)
