# Benchmark Eligibility

CR-AM-06 establishes the canonical model for determining whether an
`AssessmentResult` may legitimately participate in a cross-organisation
comparison. It answers **"is it comparable?"** — CR-AM-07 will answer
"how do we compare it?".

## Architectural principle (CR-AM-06 §15)

> Benchmark eligibility is a governed determination about the
> comparability of an AssessmentResult; it is not a property inferred
> from the existence of a score or maturity level.

The consequence for every consumer of this sub-metamodel: never say
"Company A is Level 4". The precise statement is:

> Company A achieved Level 4 under Maturity Model X, for Capability Y,
> in Scenario Z, using Measure M, and the resulting assessment is
> eligible for comparison within Benchmark Cohort C.

## The eligibility pipeline

```text
AssessmentResult
      │
      ▼
BenchmarkEligibility          ← governed determination (this CR)
      │
      ▼
BenchmarkCohort               ← population construct (§6, §7)
      │
      ▼
CR-AM-07 Comparison           ← percentile / rank / peer position
```

The benchmark exists **between** comparable results, not inside an
individual organization (§7). Enterprise views (CR-AM-05) remain useful
without pretending to be benchmarks (§12).

## The comparability key (§5)

Every benchmark determination carries the result's canonical
comparability identity:

| Dimension | Source |
|-----------|--------|
| `scenario` | result lineage |
| `capability` | result lineage |
| `measure` | result lineage |
| `assessment_model` | result lineage |
| `scoring_model` | result lineage |
| `maturity_model` | result lineage |

Two results belong to the same benchmark population only when their
relevant semantic dimensions are compatible. This prevents the classic
benchmark problem: comparing things that share a label but not a
meaning (§2 — an AOMM v1 result under Service Assurance is not
comparable with an AOMM v2 result under Network Operations, even though
the capability and measure labels are identical).

## Status vocabulary (§4)

The closed vocabulary lives in `vocabulary/benchmark-status.yaml`.
Six states, mutually exclusive:

| Status | Meaning |
|--------|---------|
| `eligible` | Satisfies every dimension of at least one cohort |
| `provisional` | Participates only under explicitly declared cohort conditions |
| `not-eligible` | Fails a participation rule (confidence, population) |
| `not-comparable` | Valid result, but no compatible comparison population |
| `insufficient-data` | Result lacks required evidence or coverage |
| `expired` | Outside the cohort's temporal boundary, or superseded |

The `not-eligible` / `not-comparable` distinction is load-bearing:
the first is about the result breaking a rule, the second is about the
absence of a compatible population.

## Reason codes

Every non-eligible determination MUST carry at least one
machine-actionable reason from `vocabulary/eligibility-reasons.yaml`.
Each reason names the §8 dimension that failed and maps to the status
it produces. Reasons are codes, not prose — consumers can aggregate,
filter, and alert on them.

## The twelve eligibility dimensions (§8)

Scenario · Capability · Measure · Assessment Model · Scoring Model ·
Maturity Model · Period · Evidence · Coverage · Confidence · Version ·
Population.

Deterministic precedence when several dimensions fail at once:
`expired` → `insufficient-data` → `not-comparable` → `not-eligible`.
All failures are reported; the status reflects the most fundamental
class.

## Version compatibility (§9)

Version-number proximity is never sufficient. Compatibility reuses the
six-axis declaration architecture of CR-AM-02 §11:

- Same model version → compatible.
- Explicit declaration (`basis: explicit-mapping`) → governs, in either
  direction.
- Silent declaration → CR-AM-02 §11 default: same major version is
  compatible; a major-version boundary is not.

## What CR-AM-06 does not do (§10)

The eligibility engine and the cohort schema carry **no** percentile,
rank, quartile, top-performer, or peer-position computation. Those
fields exist on the legacy `benchmarkResult` shape for CR-AM-07's use;
CR-AM-06 determinations never emit them. CR-AM-07 will consume CR-AM-06;
it must not redefine eligibility itself.

## Historical determinations (§14)

The engine is a pure function of (result, cohort, compatibility
declarations, subject attributes). Identical inputs always reproduce
the historical determination — a result's recorded eligibility remains
its original eligibility.
