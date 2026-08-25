CR-AM-09 — Maturity Scale, Progression & Conformance Architecture

Status: Proposed
Predecessors: CR-014, CR-MM-01, CR-AM-04, CR-AM-05A
Umbrella: CR-AM-01 (Assessment Metamodel Evolution)
Supersedes: the earlier CR-AM-09 concept (Composable Maturity Model
  Architecture)
Siblings: CR-AM-10 (Maturity Component Composition & Reuse — future)
Primary objective: Make every maturity model own its scale — level set,
level semantics, progression logic, scoring bands, resolution and
conformance rules — as explicit, versioned, benchmark-lockable model
content. The metamodel standardizes HOW maturity scales are represented;
it never standardizes WHAT an individual model's maturity scale means.

⸻

1. The key architecture

MaturityModel
      │
      ├── MaturityStructure          (dimensions / capabilities — CR-AM-05A)
      │
      ├── MaturityEvaluationModel    (criteria, evidence, native scoring)
      │
      └── MaturityScale              (this CR)
            ├── MaturityLevel        (identity + ordinal + semantics)
            ├── ProgressionModel     (topology + function + transitions)
            └── ConformanceModel
                  ├── ProgressScoringBand
                  ├── LevelResolutionRule
                  └── LevelConformance

The assessment flow becomes:

Assessment Subject → Structure → Evaluation → Native Score(s)
      → MaturityScale (progression + bands + resolution)
      → Maturity Level → Maturity Result
      → MaturityScaleBaseline (locked, immutable, versioned)
      → Benchmark Assessment Contract

⸻

2. Why this is the correct next CR

Today's maturity content (CR-014 v1, CR-MM-01 v2-beta bands) implicitly
assumes a shared five-level shape. The as-authored CR-AM-09 demonstrates
that this assumption does not hold: models may carry 3–7+ levels, start
at L0 or L1, use different names and definitions, progress linearly or
non-linearly, score on 0–100 or 0–10 or categorical conditions, and
require mandatory criteria in addition to scores.

L0/L1/L2 are structural identifiers, not semantics. Model A's L3 and
Model B's L3 are not equivalent statements. A maturity level is
identified only within (MaturityModel, MaturityScale, MaturityLevel).

Without this CR, benchmarks built on maturity results can silently
change meaning when a maturity model is edited. With it, every benchmark
locks an immutable MaturityScaleBaseline and stays reproducible
indefinitely (§8).

⸻

3. MaturityScale — the model-owned maturity contract

A MaturityScale is the complete model-specific progression and
conformance framework through which evaluated performance is classified
into maturity levels:

- id, version, name, description
- levels (2..* — a maturity model has at least two levels)
- ordering (ordinal)
- progressionModel
- conformanceModel

MaturityModel 1—1 MaturityScale; MaturityScale 1—2..* MaturityLevel.
`levelCount` is derived from the level collection; if materialized for
exchange, validation must enforce consistency.

⸻

4. MaturityLevel — identity is structural, semantics are explicit

Required: id, ordinal, name, definition.

- The identifier (L0…Ln) is structural. The metamodel never prescribes
  L0 = Absent / L1 = Initial / … globally. “Absent”, “Not Present”,
  “Unaware” are all valid L0 names in different models.
- The ordinal supports ordering only. It does not define semantic
  equivalence, scoring, or progression difficulty, and never implies
  cross-model comparability.
- Semantics are mandatory: every level carries an explicit definition;
  richer models add characteristics, expected practices / capabilities /
  behaviors, evidence expectations, conformance description.
- LevelCharacteristic is descriptive — observable properties of a level,
  not automatically scoring rules.
- CriterionLevelExpectation lets each criterion state how it manifests
  at each level — maturity is demonstrated through progressive behavior
  change, not merely a score.

⸻

5. ProgressionModel — topology and function are independent

ProgressionModel = topology + function + transitionRules.

Topology (controlled vocabulary): linear, branching, gated, state-based,
custom. Function (controlled vocabulary): linear, exponential,
logarithmic, stepwise, threshold, custom.

Topology linear does NOT imply function linear. A model may be
topologically linear with exponentially increasing progression effort
(the maturity-v2 effort-coefficient insight), or branching with
threshold gating. The two axes are declared independently; the
metamodel must not assume a simple linear staircase.

⸻

6. Native evaluation and scoring stay model-owned

MaturityEvaluationModel carries criterion / indicator /
evidence-requirement / evaluation-rule / scoring-rule /
level-resolution-input. Native scoring mechanisms are model-specific:
weighted, threshold, criterion-satisfaction, mandatory-criterion, expert
assessment, evidence-based classification, multi-factor, hybrid, custom.

No universal 0–100. A model may score 0–5, 0–10, percentage, weighted
index, categorical, boolean conformance, multi-dimensional vector, or
custom. The scoring mechanism is part of the model's native evaluation
contract.

⸻

7. ProgressScoringBand + LevelResolutionRule — scores never imply levels

ProgressScoringBand is a first-class scale component: a model-specific
classification rule identifying the range or conditions under which
assessed progress conforms to a level. Bands belong to the scale and
resolve to defined levels. Three band families must be supported:

- numeric intervals (min/max/inclusivity/score domain → level);
- non-numeric conditions (e.g. governance_conformance = true AND
  automation_score ≥ 75 AND evidence_confidence ≥ 0.80 → L4);
- multi-dimensional conditions (overall + dimension scores + mandatory
  criteria + evidence requirements).

LevelResolutionRule determines which level is achieved given evaluation
outputs. Canonical flow: Evidence → Native Evaluation → Native Score(s)
→ Progress Scoring Bands → Level Resolution Rule → Maturity Level.
Highest-level resolution (a level is achieved only when all lower-level
prerequisites AND its own conditions hold) must be expressible — a raw
score never automatically represents accumulated maturity.

LevelConformance is explicit per result: conformant / non-conformant /
partially-conformant / indeterminate / not-assessable (controlled
vocabulary; models may extend semantics).

⸻

8. MaturityScaleBaseline — benchmarks lock the scale

A MaturityScaleBaseline is an immutable snapshot of the effective scale
contract within a defined assessment/benchmark context: scale identity +
version, level definitions, progression model, scoring bands, resolution
rules, effective date.

A benchmark references a locked baseline. The Benchmark Assessment
Contract = assessment model + version + maturity model + scale baseline
+ scoring rules + bands + resolution rules; every participant is
evaluated under that contract. Historical reproducibility is a mandatory
acceptance criterion: given “Benchmark 2027”, the exact model, version,
scale, levels, progression, bands, and resolution rules must be
reconstructable without depending on today's model version. This extends
the CR-AM-06 cohort snapshot and CR-AM-07 reproducibility-hash discipline
to maturity semantics.

⸻

9. Boundaries with other CRs

| CR | Boundary |
|---|---|
| CR-014 / CR-MM-01 | v1 and v2-beta maturity content are scale instances; CR-AM-09 maps them into the explicit scale structure (migration, §11) — it does not re-author their level content. |
| CR-AM-04 | Maturity interpretation consumes resolution outputs; CR-AM-09 defines how a level is resolved, not how results aggregate. |
| CR-AM-05A | Dimensions/criteria/instruments are the STRUCTURE side; CR-AM-09 owns the SCALE side. Level expectations attach to criteria without merging the two. |
| CR-AM-06 / CR-AM-07 | Cohorts/comparisons consume maturity results as axes; benchmark locking uses CR-AM-09 baselines. Eligibility and comparison semantics unchanged. |
| CR-AM-10 (future) | Component reuse builds on the explicit Structure/Evaluation/Scale boundaries; CR-AM-09 establishes them but implements no reuse. |

⸻

10. Non-goals

- No universal level count, names, scoring ranges, or progression
  semantics — ever.
- No component reuse machinery (CR-AM-10).
- No destructive migration of existing maturity models or results.
- No cross-model level equivalence claims.
- No changes to assessment result, view, eligibility, cohort, or
  comparison schemas.

⸻

11. Design constraints

1. The model owns its scale. Scale, progression, bands, and resolution
   are maturity-model content, versioned with it.
2. Identifiers are structural; semantics are explicit. No global
   five-level assumption remains anywhere in the sub-tree.
3. Topology ≠ function — independently declared.
4. A score is never interpreted as a maturity level without the model's
   resolution logic.
5. Baselines are immutable. A locked baseline never mutates; model
   evolution produces a new version, not an edit.
6. Evolutionary migration: existing levels/scoring map INTO the new
   structure; nothing is reconstructed from scratch; historical results
   keep their scale version.
7. Additive schema evolution only (the CR-AM-06 enum-widening lesson).
8. Spec/metamodel stay 1.0.0 — this CR extends the `assessment-models/`
   sub-tree; no canonical version bump.

⸻

12. Phase plan

Each phase is one PR.

- Phase 1 — Maturity scale & level semantics. `maturity-scale` schema,
  level identity/ordinal/semantics shape, progression-topologies /
  progression-functions / conformance-statuses vocabularies, worked
  examples (5-level, 6-level, alternate-naming), no-global-scale
  boundary guards. (Spec tests 1–3.)
- Phase 2 — Progression & native evaluation. ProgressionModel
  (topology/function/transition rules), MaturityEvaluationModel and
  native scoring domains (incl. 0–10), CriterionLevelExpectation,
  non-linear worked example. (Spec tests 4, 6.)
- Phase 3 — Scoring bands & level resolution. `progress-scoring-band` +
  `level-resolution-rule` schemas, numeric / non-numeric /
  multi-dimensional bands, highest-conformant-level resolution, level
  conformance semantics. (Spec test 5.)
- Phase 4 — Baseline locking & migration. `maturity-scale-baseline`
  schema, benchmark lock + historical reproducibility, mapping of
  existing v1 / v2-beta maturity content into the scale structure,
  governance doc. (Spec tests 7–8.)

⸻

13. Acceptance criteria (proposal PR)

1. This spec lands at `change-requests/CR-AM-09.md`.
2. `change-requests/README.md` carries the CR-AM-09 row (status:
   Proposed).
3. The README rationale table references CR-AM-09.
4. CHANGELOG `[Unreleased]` entry records the proposal.
5. No runtime, schema, or example changes ship with the proposal.
6. Full test suite remains green (no behaviour change).
7. The phase plan in §12 is the implementation roadmap; Phase 1 scope is
   fixed as scale + level-semantics vocabulary and schema only.

⸻

14. The most important CR-AM-09 design principle

The canonical metamodel standardizes HOW maturity scales are
represented — a maturity model alone defines WHAT maturity means.
