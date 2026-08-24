CR-AM-07 — Comparative Benchmarking & Peer Analytics

Status: In progress (Phase 1 comparison vocabulary & schema + Phase 2 distribution engine + Phase 3 percentile & ranking implemented; Phase 4 Proposed)
Predecessors: CR-AM-02 → CR-AM-03 → CR-AM-04 → CR-AM-05 → CR-AM-06
Umbrella: CR-AM-01 (Assessment Metamodel Evolution)
Siblings: CR-AM-08 (Benchmark Analytics & Insights — parked)
Primary objective: Define the canonical model for answering “how do we
compare it?” — distribution, percentile, rank, and peer position over a
BenchmarkCohort — consuming CR-AM-06 eligibility without redefining it.

⸻

1. The key architecture

AssessmentResult
      │
      ▼
BenchmarkEligibility            (CR-AM-06 — “is it comparable?”)
      │
      ▼
BenchmarkCohort                 (CR-AM-06 — population construct)
      │
      ▼
CR-AM-07 Comparison             (this CR — “how do we compare it?”)
      │
      ├── Cohort Distribution   (n, mean, median, quartiles, spread)
      ├── Percentile            (per-member standing in the cohort)
      ├── Peer Ranking          (rank + peer position, e.g. 4/27)
      │
      ▼
Benchmark Insight               (derived, governed — feeds CR-AM-08)

This preserves the distinction built across the CR-AM series:

Enterprise View  = aggregation          (CR-AM-05)
Benchmark        = controlled comparison (CR-AM-06 eligibility → CR-AM-07 comparison)
Insight          = interpretation        (CR-AM-08 — parked)

⸻

2. Why this is the correct next CR

CR-AM-06 deliberately stopped at eligibility. Its §10 boundary is
explicit: percentile, rank, quartile, top-performer, and peer-position
were NOT implemented — they belong to CR-AM-07. The legacy
`benchmarkResult` schema shape carries those fields as optional and
unused, documented as CR-AM-07 fields.

Without this CR, a cohort can say who is comparable but not what the
comparison shows. With it, the canonical statement becomes:

“Company A achieved Level 4 under Maturity Model X, for Capability Y,
in Scenario Z, using Measure M; the result is eligible for Benchmark
Cohort C, where it stands at percentile 87, peer position 4/27.”

Every clause before the semicolon is CR-AM-02…06. Everything after it is
this CR.

CR-AM-07 consumes CR-AM-06; it does not redefine eligibility. Membership
in a cohort still flows only through the eligibility engine — comparison
operates exclusively on admitted members.

⸻

3. Canonical BenchmarkComparison

A BenchmarkComparison is a governed, reproducible derivation over a
BenchmarkCohort at a point in time:

- cohort reference + cohort version/snapshot identity
- comparability key (inherited verbatim from CR-AM-06 — six required
  modelReferences; comparison never widens it)
- distribution statistics over the admitted population
- per-member standings (percentile, rank, peer position)
- derivation metadata (method, tie rules, minimum-sample enforcement,
  reproducibility hash)

A comparison is a derived artifact. It is never the truth: the truth is
the set of eligible AssessmentResults. The same principle as CR-AM-05 —
never store the heatmap as the truth — applies here: never store the
ranking as the truth. Recompute from the cohort.

⸻

4. Cohort distribution

The distribution describes the population, not any member:

- n (admitted population size)
- mean, median, quartiles (Q1/Q3), min/max
- optional spread measures (standard deviation, IQR)

Distribution statistics are computed only when the cohort satisfies its
declared `minimum_sample_size` (CR-AM-06 §6). Below threshold, the
comparison is refused with an explicit reason — small-population
statistics are not silently emitted.

⸻

5. Percentile semantics

Percentile is a per-member standing within the cohort distribution:

- percentile 87 = the member outperforms 87% of the admitted population
- deterministic tie rule declared up front (members with equal scores
  share the same percentile; no arbitrary ordering by member id)
- the percentile method (e.g. inclusive vs exclusive) is declared in the
  derivation metadata and is stable across recomputations

Percentile is computed against the score axis declared by the cohort’s
comparability key (scoring model + measure), never against a mixture of
axes.

⸻

6. Peer ranking & peer position

Ranking is the ordinal companion of percentile:

- rank 1 = highest standing under the declared ordering
- peer position renders as rank/n (e.g. 4/27)
- ties share a rank; the ranking rule (competition vs dense ranking) is
  declared in derivation metadata
- “top-performer” is a derived label governed by an explicit cohort
  threshold, never an implicit property of rank 1

⸻

7. Benchmark Insight (hand-off to CR-AM-08)

A Benchmark Insight is the interpretive layer above comparison — trends,
movement between snapshots, peer-gap narratives. This CR establishes
only the comparison outputs that insights consume. Insight generation,
narrative, and recommendation are CR-AM-08 scope and remain parked.

⸻

8. Boundaries with other CRs

| CR | Boundary |
|---|---|
| CR-AM-05 | Views aggregate one organisation’s results; CR-AM-07 compares across organisations. Aggregation ≠ comparison. |
| CR-AM-06 | Eligibility is consumed, never redefined. CR-AM-07 adds no membership rules, no status vocabulary, no reason codes. |
| CR-AM-08 | Insights interpret comparisons; CR-AM-07 produces comparisons. No narrative/recommendation layer here. |
| CR-MM-01 | Maturity v2 bands define score meaning; comparison operates on whatever axis the comparability key declares. |

⸻

9. Non-goals

- No changes to the eligibility engine, cohort registry, status
  vocabulary, or reason codes (CR-AM-06 surface is frozen for this CR).
- No insight, narrative, or recommendation generation (CR-AM-08).
- No new maturity levels, scoring models, or axes.
- No cross-cohort comparison (a comparison is bound to exactly one
  cohort snapshot).
- No anonymisation/privacy machinery beyond the minimum-sample gate
  (governance policy may tighten this later; the schema does not invent
  it now).

⸻

10. Design constraints

1. Derived, never stored as truth. A BenchmarkComparison is reproducible
   from its cohort snapshot; the derivation carries a reproducibility
   hash (same input → same output).
2. Missing data is N/A, not zero (CR-AM-05 principle). A member with
   missing measures on the comparison axis is excluded from the
   distribution with an explicit reason — never imputed.
3. Minimum sample size is enforced before any statistic is emitted.
4. Eligibility is the only door. Comparison input = admitted cohort
   members only (CR-AM-06 §7).
5. Deterministic tie rules, declared in metadata.
6. Additive schema evolution only — enum widening over field requiring
   (the CR-AM-06 lesson); every pre-existing example must still
   validate.
7. Spec/metamodel stay 1.0.0 — this CR extends the `assessment-models/`
   sub-tree; no canonical version bump.

⸻

11. Phase plan

Each phase is one PR.

- Phase 1 — Comparison vocabulary & schema. `BenchmarkComparison`
  schema, distribution/percentile/rank vocabularies, derivation-metadata
  shape, worked examples. No engine.
- Phase 2 — Distribution engine. Cohort statistics over admitted
  members; minimum-sample enforcement; missing-data exclusion with
  explicit reasons.
- Phase 3 — Percentile & ranking. Per-member percentile, rank, peer
  position; declared tie rules; reproducibility hash; conformance tests
  against worked examples (including tie cases).
- Phase 4 — Integration & governance. Views/CLI surfacing of comparison
  outputs, governance doc (comparison policy), CHANGELOG + docs,
  CR-AM-08 hand-off notes.

⸻

12. Acceptance criteria (proposal PR)

1. This spec lands at `change-requests/CR-AM-07.md`.
2. `change-requests/README.md` carries the CR-AM-07 row (status:
   Proposed).
3. The README rationale table references CR-AM-07.
4. CHANGELOG `[Unreleased]` entry records the proposal.
5. No runtime, schema, or example changes ship with the proposal.
6. Full test suite remains green (no behaviour change).
7. The phase plan in §11 is the implementation roadmap; Phase 1 scope is
   fixed as vocabulary + schema only.

⸻

13. The most important CR-AM-07 design principle

A ranking is a reproducible derivation over an eligible population —
never a property of a score, and never a stored truth.
