# Comparison Policy

CR-AM-07 establishes comparative benchmarking over admitted benchmark
cohorts. This document is the governance policy for producing,
surfacing, and consuming `BenchmarkComparison` artifacts. It binds every
producer (engines, composers, report renderers) and every consumer
(dashboards, exports, future insight layers) to the same rules.

## Architectural principle (CR-AM-07 §13)

> A ranking is a reproducible derivation over an eligible population —
> never a property of a score, and never a stored truth.

The consequence for every consumer: never say "Company A is 4th". The
precise statement is:

> Company A holds peer position 4/27 in BenchmarkComparison C, derived
> over BenchmarkCohort snapshot S, on measure M, under percentile method
> P and ranking rule R.

## The comparison pipeline

```text
AssessmentResult
      │
      ▼
BenchmarkEligibility            ← CR-AM-06, frozen for CR-AM-07
      │
      ▼
BenchmarkCohort                 ← population construct (CR-AM-06 §6, §7)
      │
      ▼
BenchmarkComparison             ← derived artifact (CR-AM-07 §3)
      │                             distribution + standings + derivation
      ▼
Benchmark Insight               ← interpretive layer (CR-AM-08, parked)
```

## Policy rules

1. **Derived, never stored as truth.** A comparison is recomputed from
   its cohort snapshot. Every derivation carries the cohort reference,
   snapshot identity, membership hash, and a reproducibility hash; the
   same inputs must produce the same artifact byte-for-byte.
2. **Eligibility is the only door.** Comparison input is the admitted
   membership of the cohort — nothing else. No membership rules, status
   vocabulary, or reason codes are added by comparison (CR-AM-06 §7
   surface is frozen).
3. **Minimum sample before any statistic.** Below the cohort's declared
   `minimum_sample_size` the comparison is refused with an explicit
   reason. Small-population statistics are never silently emitted.
4. **Missing data is N/A, never zero.** A member with missing measures
   on the comparison axis is excluded from the distribution with an
   explicit reason in `derivation.excluded_members` — never imputed.
5. **Declared methods, stable across recomputation.** The percentile
   method (`inclusive` / `exclusive`) and ranking rule (`competition` /
   `dense`) are drawn from the governed vocabularies and recorded in
   derivation metadata. Changing a method produces a new comparison, not
   an edit of an existing one.
6. **Ties share standing.** Equal scores share percentile and rank; the
   declared ranking rule only governs what follows a tie. Ties are never
   broken by member identity.
7. **One cohort, one snapshot.** No cross-cohort comparison: a
   comparison is bound to exactly one cohort snapshot.
8. **Additive schema evolution only.** New fields may be added; existing
   fields are never required-tightened. Every pre-existing example must
   still validate (the CR-AM-06 enum-widening lesson).

## Surfacing (Phase 4)

Comparison outputs are surfaced through the report renderer and CLI:

```bash
python -m runtime.comparison.report <comparison.yaml> [--format text|json]
```

The report is a *view over the derivation*: it renders exactly the
fields the schema declares, in deterministic order, and adds no
interpretation. It is regenerated on demand from the comparison
document — it is never persisted as an artifact in its own right.

## Hand-off to CR-AM-08 (Benchmark Insight)

The interpretive layer above comparison — trends across snapshots,
movement, peer-gap narratives, recommendations — is CR-AM-08 scope and
remains parked. This policy fixes the hand-off contract:

- **CR-AM-08 consumes:** per-member standings (percentile, rank, peer
  position), the cohort distribution, snapshot identity (cohort version
  + snapshot timestamp + membership hash), and derivation metadata
  (methods, minimum-sample outcome, exclusions, reproducibility hash).
- **CR-AM-08 may rely on:** deterministic recomputation — insights can
  always be traced back to the exact derivation that produced them.
- **CR-AM-08 owns:** all narrative, trend, and recommendation
  vocabulary. No insight terms appear in comparison artifacts, reports,
  or schemas.
- **Never handed off:** raw eligibility state (CR-AM-06 surface),
  imputed data, and any ranking that has not passed the minimum-sample
  gate.
