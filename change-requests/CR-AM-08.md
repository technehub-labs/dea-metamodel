CR-AM-08 — Assessment Insights & Decision Support

Status: Proposed
Predecessors: CR-AM-02 → CR-AM-03 → CR-AM-04 → CR-AM-05 → CR-AM-06 → CR-AM-07
Umbrella: CR-AM-01 (Assessment Metamodel Evolution)
Siblings: CR-AM-09 (Assessment-to-Value & Outcome Traceability — future)
Primary objective: Define the canonical model for answering “what does the
evidence tell us?” — governed insights, structured gaps, and improvement
objectives derived from assessment results, views, and benchmark
comparisons — without prescribing actions or embedding strategy into the
assessment metamodel.

⸻

1. The key architecture

AssessmentResult
      │
      ├──► AssessmentView            (CR-AM-05 — “what is our state?”)
      │
      └──► BenchmarkEligibility      (CR-AM-06)
                    │
                    ▼
             BenchmarkCohort
                    │
                    ▼
          BenchmarkComparison        (CR-AM-07 — “how do we compare?”)
                    │
                    ▼
          ┌─────────────────────┐
          │ CR-AM-08            │
          │ AssessmentInsight   │  ← interpretation over evidence
          │ AssessmentGap       │  ← structured current-vs-reference
          │ ImprovementObjective│  ← what the evidence indicates
          └─────────┬───────────┘
                    ▼
          (TRANSFORM — deliberately out of scope)

This preserves the distinction built across the CR-AM series:

Assessment  = measurement            (CR-AM-02…04)
Aggregation = views                  (CR-AM-05)
Benchmark   = controlled comparison  (CR-AM-06 eligibility → CR-AM-07 comparison)
Insight     = interpretation         (this CR)
Transform   = action                 (future — outside the assessment metamodel)

⸻

2. Why this is the correct next CR

CR-AM-07 deliberately stopped at comparison. Its spec (§7) and the
comparison policy (governance/comparison-policy.md, “Hand-off to
CR-AM-08”) fix the contract: CR-AM-07 produces standings, distribution,
snapshot identity, and derivation metadata; the interpretive layer above
comparison — trends, movement, peer-gap narratives — is CR-AM-08 scope.
The deferred-scope decision record in the same policy designates gap
analysis, comparison confidence, and metric direction as CR-AM-08
candidates. This CR picks them up.

Without this CR, the architecture can say where an organisation stands
but not what the evidence means. With it, the canonical statement
becomes:

“Company A achieved Level 4 under Maturity Model X, for Capability Y, in
Scenario Z, using Measure M; the result is eligible for Benchmark Cohort
C, where it stands at percentile 87, peer position 4/27; the evidence
supports insight I (benchmark-gap, high significance, high confidence),
identifying gap G and informing improvement objective O.”

Everything before “the evidence supports” is CR-AM-02…07. Everything
after it is this CR.

⸻

3. Canonical AssessmentInsight

An AssessmentInsight is a governed, evidence-bound interpretation:

- identity + version
- type (controlled vocabulary — §4)
- subject (capability / measure / scenario reference)
- evidence (mandatory — assessment results, views, comparisons)
- interpretation (the statement)
- confidence (level + evidence coverage + limitations)
- significance (independent of confidence — §5)
- lineage (source artifacts + insight rule + versions — §6)

An insight is derived. The truth remains the underlying
AssessmentResult / AssessmentView / BenchmarkComparison. An insight must
never assert more than its evidence supports, and must never appear more
authoritative than its evidence.

Insight ≠ Finding. A Finding is an observation attached to one
assessment result (CR-AM-04). An AssessmentInsight is an interpretation
derived across assessment evidence. The finding belongs to the
assessment; the insight belongs to the analytical layer.

⸻

4. Insight types

Controlled vocabulary (vocabulary/insight-types.yaml). Initial set:

strength, weakness, gap, risk, opportunity, trend, anomaly,
benchmark-gap, maturity-gap, coverage-gap, confidence-warning

No domain-specific types at this stage (no “AI-readiness-insight”, no
“autonomous-network-insight”); those are derived through domain models
later.

⸻

5. Confidence and significance are independent

Confidence — how well the evidence supports the statement (level +
evidence coverage + limitations). Significance — how much the statement
matters (controlled vocabulary, vocabulary/significance-levels.yaml).

High confidence + low significance: the gap certainly exists and is not
strategically material. Low confidence + high significance: potentially
important, evidence insufficient. Collapsing these into one scale
destroys the distinction enterprise decision-making needs most.

⸻

6. InsightRule — governed, reproducible derivation

InsightRule is the mechanism that turns evidence into insight:

InsightRule
├── condition   (evidence selector + operator + threshold)
├── result      (insight type + interpretation template)
├── severity
└── confidence

Architecture: InsightRule → applied to evidence → produces
AssessmentInsight. Never AssessmentResult → hard-coded interpretation.
Same definitional separation as the rest of OpenDEA: specification vs
instance.

Every insight carries lineage: source results / views / comparisons,
the insight rule id + version, and the generation method — one of
rule / analyst / algorithm / ai-assisted (controlled vocabulary). An
AI-assisted interpretation is an interpretation of authoritative
evidence, never a new fact. The chain Evidence → Rule → (optional AI
interpretation) → Insight is auditable end-to-end; AI never becomes the
authority.

⸻

7. AssessmentGap — three gap types, never conflated

An AssessmentGap is a structured comparison between a current state and
an explicit reference. The reference type is mandatory and controlled
(vocabulary/gap-types.yaml):

- target-gap    — current vs declared target state
- benchmark-gap — current vs cohort reference (median, quartile, …)
- trend-gap     — current vs previous state of the same subject
- threshold-gap — current vs a governed threshold
- coverage-gap  — assessed scope vs required scope

Same numbers, different meanings: current L3 vs target L4, vs peer
median L4, vs previous L2 are three different statements. The model must
identify the reference explicitly; “gap = 1” without a reference type is
not canonical.

⸻

8. ImprovementObjective — the hand-off, not the plan

ImprovementObjective captures what improvement the evidence indicates:

- subject, current state, target state (typed: maturity level / score /
  measure / capability state / benchmark position / business outcome
  reference)
- rationale: the insights (and gaps) that justify it

Objective ≠ Action. CR-AM-08 ends at the objective. Projects, programs,
initiatives, investments, business cases, transformation actions,
benefit realization, roadmaps — all deliberately excluded (§9). A
lightweight DecisionContext reference (priority, horizon, constraints)
may accompany an objective; it is a reference point, not an enterprise
decision model. Intended business outcomes may be named by reference;
the value-realization model is CR-AM-09 territory.

⸻

9. Boundaries with other CRs

| CR | Boundary |
|---|---|
| CR-AM-04 | Findings are observations on one result; insights interpret across evidence. Findings stay untouched. |
| CR-AM-05 | Views aggregate one organisation’s results; insights may cite views as evidence but views carry no interpretation. |
| CR-AM-06 | Eligibility is consumed, never redefined. Frozen surface stays frozen. |
| CR-AM-07 | Comparisons are immutable analytical facts; insights derive from them. The comparison-policy hand-off contract (consume standings/distribution/derivation; own all narrative vocabulary; never receive raw eligibility state) binds this CR. |
| CR-012 | Signals/observations interpret live runtime state; insights interpret assessment evidence. Different evidence base, different lifecycle, no shared artifacts. |
| CR-AM-09 (future) | Value/outcome traceability consumes improvement objectives; CR-AM-08 does not model value realization. |

⸻

10. Non-goals

- No actions, projects, programs, initiatives, investments, business
  cases, benefit realization, roadmaps (TRANSFORM stage — excluded).
- No changes to assessment result, view, eligibility, cohort, or
  comparison schemas — insights consume them as-is.
- No domain-specific insight types.
- No AI-authority semantics — generation method is metadata; evidence is
  the authority.
- No enterprise decision model — DecisionContext is a reference, not a
  decision system.
- No new maturity levels, scoring models, or comparison metrics.

⸻

11. Design constraints

1. Evidence is mandatory. An insight without evidence references is
   refused by the schema.
2. Interpretation is derived, never stored as truth. The truth is the
   evidence chain; insights are reproducible from evidence + rule +
   versions.
3. Confidence ≤ evidence. No insight may present confidence its evidence
   coverage does not support; limitations are explicit.
4. Confidence ≠ significance — independent axes, both controlled
   vocabularies.
5. Gap reference type is explicit and controlled. No untyped gaps.
6. Rule versions are part of lineage. Same evidence + same rule version
   → same insight (reproducible interpretation).
7. Generation method is declared (rule / analyst / algorithm /
   ai-assisted). AI-assisted text is interpretation, never fact.
8. Additive schema evolution only (the CR-AM-06 enum-widening lesson);
   every pre-existing example must still validate.
9. Spec/metamodel stay 1.0.0 — this CR extends the `assessment-models/`
   sub-tree; no canonical version bump.

⸻

12. Phase plan

Each phase is one PR.

- Phase 1 — Insight vocabulary & schema. `AssessmentInsight` schema,
  insight-types + significance-levels vocabularies, evidence/lineage
  shape, worked example. Boundary guards (no comparison/eligibility
  redefinition; no action vocabulary). No engine.
- Phase 2 — InsightRule & derivation. insight-rule schema, generation
  methods vocabulary, rule-driven insight derivation with reproducible
  lineage, confidence/coverage enforcement, conformance tests (including
  the evidence-supports-interpretation guard).
- Phase 3 — AssessmentGap. gap schema, gap-types vocabulary, explicit
  reference semantics for all five gap types, worked examples
  (target/benchmark/trend), conformance tests.
- Phase 4 — ImprovementObjective + governance. objective schema,
  decision-context reference shape, objectives examples,
  governance/insights.md (insight policy + CR-AM-09 hand-off),
  CHANGELOG + docs.

⸻

13. Acceptance criteria (proposal PR)

1. This spec lands at `change-requests/CR-AM-08.md`.
2. `change-requests/README.md` carries the CR-AM-08 row (status:
   Proposed).
3. The README rationale table references CR-AM-08.
4. CHANGELOG `[Unreleased]` entry records the proposal.
5. No runtime, schema, or example changes ship with the proposal.
6. Full test suite remains green (no behaviour change).
7. The phase plan in §12 is the implementation roadmap; Phase 1 scope is
   fixed as vocabulary + schema only.

⸻

14. The most important CR-AM-08 design principle

An insight is an interpretation of evidence — never a fact, and never
more authoritative than the evidence it cites.
