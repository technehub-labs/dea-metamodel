# Maturity Scale, Progression & Conformance Governance (CR-AM-09 Phase 1)

Policy for model-owned maturity scales. The core principle:

**The canonical OpenDEA Assessment Metamodel standardizes HOW maturity
scales are represented; it does not standardize the substantive maturity
scale of individual maturity models. A maturity model owns its maturity
interpretation.**

CR-AM-09 establishes explicit boundaries so that two maturity models —
5-level linear-exponential and 6-level linear-logarithmic, 3-level
gated-threshold and 7-level state-based, 0–100 weighted and categorical
satisfaction — can coexist in the same OpenDEA ecosystem without
either being forced to conform to the other's scale, terminology,
scoring, or progression logic.

## 1. Identity is (MaturityModel, MaturityScale, MaturityLevel)

L0 in one model and L0 in another are different statements.
`L-3` in the autonomous-operations scale is `Automated`; `L3` in the
proactive-operations scale is `Proactive`. Benchmarks MUST compare via
the full triple — never via the level id or name alone.

The conformance suite pins this contract (CR-AM-09 §9).

## 2. Topology and function are independent

A maturity model declares its progression in two independent axes:

- **Topology** (the shape of the path): `linear`, `branching`, `gated`,
  `state-based`, `custom` — controlled vocabulary
  `vocabulary/progression-topologies.yaml`.
- **Function** (how the rate behaves): `linear`, `exponential`,
  `logarithmic`, `stepwise`, `threshold`, `custom` — controlled
  vocabulary `vocabulary/progression-functions.yaml`.

Linear topology with exponential function is the maturity-v2 effort-
coefficient insight, formalised: levels remain ordered, but later
levels cost disproportionately more than earlier ones. The schema
allows any combination.

## 3. Levels carry explicit semantics

Every level carries a name AND a definition. Identifiers (L0, L1, L2,
…) are structural; semantics are model-owned. The metamodel never
prescribes L0 = Absent / L1 = Initial / … globally. Different models
legitimately use different names for the same ordinal position.

The conformance suite explicitly verifies that an alternate-naming
maturity scale (Not Present / Reactive / Managed / Proactive /
Optimized) validates without referencing the autonomous-operations
naming pattern.

## 4. Scoring bands, resolution rules, and baseline locking

These are out of Phase 1 scope and ship in subsequent phases:

- **Phase 3** — `ProgressScoringBand` (numeric, non-numeric,
  multi-dimensional) + `LevelResolutionRule` (the seam between a raw
  score and a level attribution)
- **Phase 4** — `MaturityScaleBaseline` (immutable, benchmark-locked)
  and the migration of existing CR-014 / CR-MM-01 v1 / v2-beta
  maturity content into the scale structure

The Phase 1 schema enforces no pre-emption of these — the conformance
suite asserts the scale schema carries no scoring-band or
resolution-rule vocabulary, preserving the additive, evolutionary
migration principle.

## 5. Conformance outcomes are explicit

A maturity result declares how well it conformed: `conformant`,
`partially-conformant`, `non-conformant`, `indeterminate`, or
`not-assessable`. The resolution logic (Phase 3) determines the
outcome from the evidence; the outcome vocabulary is Phase 1.

When `highest_conformant_level_resolution` is true, a level is assigned
only when all lower-level prerequisites AND its own conditions are
satisfied — never from a raw accumulated score (CR-AM-09 §26).

## 6. CR-AM-09 Phase 1 acceptance — confirmed

| AC | Status |
|---|---|
| MaturityScale canonical | Phase 1 — this PR |
| MaturityLevel canonical (id + ordinal + name + definition) | Phase 1 — this PR |
| 3 progression vocabs (topology / function / conformance status) | Phase 1 — this PR |
| 5-level model validates (spec test 1) | Phase 1 — this PR |
| 6-level model validates (spec test 2) | Phase 1 — this PR |
| Alternate-naming model validates without canonical terminology (spec test 3) | Phase 1 — this PR |
| Topology independent of function (spec test 6) | Phase 1 — this PR |
| Identity rule: (model, scale, level), never normalised | Phase 1 — this PR |
| Spec + metamodel remain **1.0.0** | Confirmed |

## 7. Boundaries with other CRs

| CR | Boundary |
|---|---|
| CR-014 / CR-MM-01 | Existing maturity content is a scale instance; migration into the scale structure ships in Phase 4 (no destructive migration, CR-AM-09 §36). |
| CR-AM-04 | AssessmentResult aggregates maturity resolution outputs; CR-AM-09 defines how a level is resolved, not how results aggregate. |
| CR-AM-05A | Dimensions/criteria/instruments are the STRUCTURE side; CR-AM-09 owns the SCALE side. Level expectations attach to criteria without merging the two. |
| CR-AM-06 / CR-AM-07 | Cohorts/comparisons consume maturity results as axes; benchmark baseline locking (Phase 4) uses CR-AM-09 baselines. Eligibility and comparison semantics unchanged. |
| CR-AM-10 (future) | Component reuse builds on the explicit Structure/Evaluation/Scale boundaries; CR-AM-09 establishes them but implements no reuse. |