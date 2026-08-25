# Assessment Insights Governance (CR-AM-08 Phase 4)

Policy for the assessment insight layer — what AssessmentInsights,
AssessmentGaps, and ImprovementObjectives are, how they relate to each
other and to the upstream evidence, and where the assessment metamodel
hands off to the next stage (the future value-traceability CR; CR-AM-09
is the maturity-scale CR and is not in scope here).

This document governs the **interpretation layer** added by CR-AM-08.
CR-AM-08 closes the assessment evidence chain:

```
AssessmentResult     (CR-AM-04)
   ↓
AssessmentView       (CR-AM-05)
   ↓
BenchmarkEligibility (CR-AM-06) + BenchmarkCohort
   ↓
BenchmarkComparison  (CR-AM-07)
   ↓
─────────────────────────────────────────
 AssessmentInsight   (CR-AM-08 §3)
       ↓
 AssessmentGap       (CR-AM-08 §7)
       ↓
 ImprovementObjective  (CR-AM-08 §9)
─────────────────────────────────────────
                  ↓
            (value-CR — future, unnumbered)
```

The boundary after ImprovementObjective is deliberate: **actions,
projects, initiatives, programs, investments, and value tracing belong
to TRANSFORM, not to the assessment metamodel**. CR-AM-08 fixes the
seam; the value-CR consumes it.

## 1. Three kinds, never conflated

| Type | Purpose | Authority |
|---|---|---|
| AssessmentInsight | Interpret evidence into a meaningful statement | Evidence is authoritative; the insight is interpretation (CR-AM-08 §3) |
| AssessmentGap | Quantify current-vs-reference on an explicit axis | The reference determines what the number means; same number, different reference = different statement (CR-AM-08 §7) |
| ImprovementObjective | Hand off intent to the value-CR | The objective carries evidence + target + priority — never the action (CR-AM-08 §9) |

Each is schema-validated by its own JSON Schema, structurally refuses
the others' vocabulary (`additionalProperties: false`), and is
defended by the conformance suite against accidental cross-pollution.

## 2. Evidence is the only authority

Every AssessmentInsight cites at least one governed artifact
(AssessmentResult, AssessmentView, or BenchmarkComparison). The cited
artifacts appear identically in `lineage.sources`. Rule-derived
insights additionally carry `lineage.insight_rule` (id + version).
ImprovementObjectives cite the AssessmentInsights and AssessmentGaps
that motivated them — citation discipline, never free-floating intent.

Conformance enforces this in three places:

- `test_assessment_insight.py` — evidence / lineage / rule reference
  refused when missing or inconsistent
- `test_assessment_gap.py` — lineage.sources citation; `identified_by`
  when sourced from an insight
- `test_improvement_objective.py` — evidence / lineage citation;
  worked-example chain asserts every cited ID resolves

## 3. Confidence ≠ Significance

The two axes are independent. An insight can be **high-confidence +
low-significance** (a certain but immaterial gap) or **low-confidence +
high-significance** (a strategically important but under-evidenced
concern). The schema enforces this with two separate vocabularies and
disjoint enums; the conformance suite asserts the scales differ.

## 4. Generation methods and AI's place

The generation method is declared per insight:

- `rule` — derived by an InsightRule (reproducible; same evidence + same
  rule version → same insight)
- `analyst` — produced by a human analyst interpreting evidence
- `algorithm` — derived by a deterministic algorithm (e.g. statistical
  outlier detection)
- `ai-assisted` — narrative/interpretation produced with AI assistance
  over the cited evidence

AI-assisted insights remain interpretations of evidence, never
substitute facts. The generation metadata is audit metadata; the
underlying evidence keeps the authority. The conformance suite asserts
`additionalProperties: false` on the schema so accidental TRANSFORM
vocabulary (`project`, `initiative`, `investment`, `recommendation`,
…) is structurally refused at validation time.

## 5. Gap reference semantics are explicit

The five gap reference kinds (`target`, `benchmark`, `trend`,
`threshold`, `coverage`) are never conflated — same gap number on the
same axis can mean three different things depending on the reference.
The conformance suite asserts that every example's `reference.kind`
is permitted for its declared `type`, and that benchmark-gap and
trend-gap cite their source artifact (the BenchmarkComparison and the
previous AssessmentResult, respectively).

## 6. Objective = intent; action = the next CR

An ImprovementObjective declares:

- what the target state is,
- what the priority is,
- which insights and gaps motivate it, and
- when it was declared.

It does not declare **how** the target will be reached. Initiatives,
projects, programs, investments, roadmaps, business cases, and value
realisation belong to the future value-traceability CR. The objective
is the seam: it carries the citation the value-CR needs to consume
without ambiguity.

## 7. CR-AM-08 acceptance — confirmed

| AC | Status |
|---|---|
| AssessmentInsight canonical + worked example + boundary guards | Phase 1 — merged |
| InsightRule canonical + derivation runtime + reproducibility | Phase 2 — merged |
| AssessmentGap canonical + 5 explicit reference semantics | Phase 3 — merged |
| ImprovementObjective canonical + hand-off to value-CR | Phase 4 — this PR |
| `governance/insights.md` documents the seam and boundary | Phase 4 — this PR |
| Spec + metamodel remain **1.0.0** throughout | Confirmed |
| `additionalProperties: false` on all three schemas (TRANSFORM vocabulary structurally refused) | Confirmed |
| CR-AM-06/07 frozen surfaces untouched | Confirmed |
| Insight ≠ Finding (CR-AM-04 boundary), AssessmentInsight is interpretation across evidence | Confirmed |

CR-AM-08 closes. The next architectural step is **CR-AM-09 — Maturity
Scale, Progression & Conformance Architecture** (proposal merged as
#133; implementation phases to follow). Beyond that, the value-CR
takes over, where assessment evidence meets organisational capability
evolution.