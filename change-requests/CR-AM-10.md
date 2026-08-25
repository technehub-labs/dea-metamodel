CR-AM-10 — Maturity Component Composition & Reuse

Status: Proposed
Predecessors: CR-AM-09, CR-AM-05A, CR-AM-04, CR-MM-01
Umbrella: CR-AM-01 (Assessment Metamodel Evolution)
Siblings: CR-AM-09 (Maturity Scale, Progression & Conformance —
  implemented), value-traceability CR (future)
Driving use case: the Digital Transformation maturity model — a composite
  model spanning operations, technology, and services-delivery child
  models plus its own dimensions.
Primary objective: Let maturity models be composed — from reusable,
  versioned component packages (dimensions, criteria, level
  expectations) and from other maturity models — through explicit,
  typed, acyclic references, so that models feed one another without
  copy-paste drift and without silent inheritance. The metamodel
  standardizes HOW composition is declared; it never standardizes WHAT a
  composite model means.

⸻

1. The key architecture

MaturityModel
      │
      ├── MaturityStructure          (dimensions / capabilities — CR-AM-05A)
      │
      ├── MaturityEvaluationModel    (criteria, evidence, native scoring)
      │
      ├── MaturityScale              (CR-AM-09 — implemented)
      │
      └── MaturityComposition        (this CR)
            ├── ComponentReference   (typed, versioned: import / extend / override)
            ├── ChildModelReference  (maturity model → maturity model)
            └── CompositionRules
                  ├── acyclicity
                  ├── reconciliation  (name/id collisions)
                  └── result-aggregation binding (→ CR-AM-04 / CR-AM-09)

The assessment flow becomes:

Component packages + child model results
      → MaturityComposition (typed references, reconciliation)
      → MaturityStructure / MaturityEvaluationModel (assembled view)
      → Native Score(s) → MaturityScale (CR-AM-09)
      → Composite Maturity Result
      → MaturityScaleBaseline (locks the resolved composition — §7)

⸻

2. Why this is the correct next CR

CR-AM-09 made every maturity model own its scale. As models proliferate
(digital transformation, domain-specific models, sector variants), the
next failure mode is uncontrolled duplication: the same dimension or
criterion copied into five models, edited in three, silently divergent
in two. Worse, composite models ("digital transformation maturity" as a
function of operations + technology + services-delivery maturity) have
no canonical way to exist at all — today they could only be hand-rolled
assessment aggregations with no typed relationship to their child
models.

Without this CR, composition happens by copy-paste and the provenance
chain Evidence → Rule → Insight (CR-AM-08) breaks at the model boundary:
a composite score cannot say which version of which child model it
consumes. With it, every composite model is reproducible from explicit
references, and benchmarks lock the resolved composition (§7).

⸻

3. MaturityComponent — the unit of reuse

A MaturityComponent is a versioned, independently-governed package of
reusable maturity content:

- id, version, name, description
- kind (controlled vocabulary): dimension-package / criterion-package /
  level-expectation-package / evidence-requirement-package
- content (references into the owning model's structure/evaluation
  artefacts — CR-AM-05A dimensions and criteria by id:version)
- status, owner, steward, effective_date, review_date (CR-MM-01.1
  governance fields)

Components are published by a model and consumed by reference. A
component is never inlined into a consumer — the reference IS the reuse.

⸻

4. Reference kinds — no silent inheritance

Every ComponentReference declares a kind (controlled vocabulary):

- import   — consume the component exactly as published at the pinned
             version. Consumer cannot modify it.
- extend   — consume and add consumer-local items (additional criteria,
             additional characteristics). The published component is
             unchanged; additions are visibly the consumer's.
- override — consume with declared replacements. Every override must
             name what it replaces and why. Overrides are the
             highest-drift-risk kind and are surfaced in conformance
             reports.

There is no fourth, implicit kind. A reference without a kind is
refused by the schema.

⸻

5. Composite maturity models — models composed of models

A MaturityModel may declare ChildModelReference entries: other maturity
models, pinned by id:version, whose results are inputs to the
composite's own evaluation.

Rules:

1. The composition graph is directed and acyclic (the CR-AM-05A §8
   discipline applied at model granularity). A cycle is a schema-time
   and CI-time error, not a runtime surprise.
2. Child results are inputs, never conclusions. A composite level is
   resolved only through the composite's own MaturityScale
   (CR-AM-09): its own bands, its own resolution rules. Child L3 +
   child L3 never implies composite L3 — no cross-model level
   equivalence (CR-AM-09 §10 carries through).
3. Each child reference declares how child results enter the
   composite's native evaluation (as dimension scores, as mandatory
   criteria, as evidence) via the CR-AM-09 evaluation-rule vocabulary.
4. A composite model has its own identity, scale, and governance. It
   is a new authority over its composition, not a view over children.

⸻

6. Reconciliation — collisions are resolved explicitly

When two imported components (or a component and consumer-local
content) collide on name or id, the consumer must declare the
resolution in CompositionRules: rename-with-prefix, keep-both-scoped,
or select-one. There is no default merge. Undeclared collisions fail
validation.

⸻

7. Baselines lock the resolved composition

A composite model's MaturityScaleBaseline (CR-AM-09 §8) additionally
records the resolved composition: every component reference (kind +
id + version), every child model reference (id + version), and the
reconciliation rules in effect. Historical reproducibility therefore
extends through composition: given "Benchmark 2027", the exact child
model versions and component versions are reconstructable without
depending on today's model versions. Composite baselines never mutate;
evolution produces a new baseline version.

⸻

8. Boundaries with other CRs

| CR | Boundary |
|---|---|
| CR-AM-05A | Owns Structure: dimension/criterion definitions and their recursive hierarchy. CR-AM-10 references structure; it does not redefine it. |
| CR-AM-09 | Owns Scale: levels, progression, bands, resolution, baselines. Composition feeds INTO a model's own scale; it never merges two scales. |
| CR-AM-04 | Owns result aggregation mechanics. Composite evaluation binds to aggregation via declared rules; CR-AM-10 does not re-implement aggregation. |
| CR-AM-07 | Benchmarks consume locked baselines. CR-AM-10 extends what a baseline records (resolved composition); comparison semantics unchanged. |
| CR-AM-08 | Insights/gaps may cite composite results; interpretation layer untouched. |
| Value traceability (future) | Consumes improvement objectives; no overlap. |

⸻

9. Non-goals

- No changes to existing maturity model content — the five v2-beta
  models are untouched; they may be PUBLISHED as components but are
  not re-authored.
- No cross-model level equivalence claims (inherits CR-AM-09 §10).
- No transitive auto-import: importing a component does not silently
  import that component's own references; depth-1 resolution with
  explicit declaration.
- No UI or catalogue rendering (catalogue track is separate).
- No changes to assessment result, view, eligibility, cohort,
  comparison, insight, gap, or objective schemas.
- No runtime federation of models (CR-11 federation is runtime state;
  this is model content).

⸻

10. Design constraints

1. References, never copies. Reuse is by typed, versioned reference;
   inlining component content into a consumer is a conformance error.
2. Explicit reference kinds. import / extend / override — no implicit
   inheritance.
3. Acyclic composition. Enforced at schema validation and in CI.
4. Children are inputs. Composite levels resolve only through the
   composite's own CR-AM-09 scale.
5. Baselines lock composition. A locked composite baseline records the
   full resolved reference set; it never mutates.
6. Additive schema evolution only (the CR-AM-06 enum-widening lesson);
   every pre-existing example must still validate.
7. Spec/metamodel stay 1.0.0 — this CR extends the
   `assessment-models/` sub-tree; no canonical version bump.

⸻

11. Phase plan

Each phase is one PR.

- Phase 1 — Component identity & reference model. `maturity-component`
  and `component-reference` schemas, component-kinds and reference-kinds
  vocabularies, registry catalogue file, collision-rejection guards,
  worked example (one published dimension-package imported by a second
  model). (Spec tests 1–2.)
- Phase 2 — Composite maturity models. `child-model-reference` schema,
  acyclicity guard (schema + CI), evaluation-binding rules, worked
  example (a two-child composite resolving through its own scale).
  (Spec tests 3–4.)
- Phase 3 — Reconciliation & governance. reconciliation-rules schema
  and vocabulary, override surfacing in conformance output, deprecation
  /supersede semantics for components and child references. (Spec
  test 5.)
- Phase 4 — Baseline locking & the Digital Transformation composite.
  Composite-baseline extension of `maturity-scale-baseline`, historical
  reproducibility test across composition, landing of the Digital
  Transformation maturity model as the first composite + own-scale
  instance, governance doc. (Spec tests 6–8.)

⸻

12. Acceptance criteria (proposal PR)

1. This spec lands at `change-requests/CR-AM-10.md`.
2. `change-requests/README.md` carries the CR-AM-10 row (status:
   Proposed).
3. The README rationale table references CR-AM-10.
4. CHANGELOG `[Unreleased]` entry records the proposal.
5. No runtime, schema, or example changes ship with the proposal.
6. Full test suite remains green (no behaviour change).
7. The phase plan in §11 is the implementation roadmap; Phase 1 scope
   is fixed as component identity + reference model only.

⸻

13. The most important CR-AM-10 design principle

Reuse is by explicit, versioned reference — a composed model is a new
authority over its components and children, never a silent copy and
never a view that drifts when its sources drift.
