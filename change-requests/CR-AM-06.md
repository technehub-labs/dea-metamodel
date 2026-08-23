The next CR should be CR-AM-06 — Benchmark Model & Eligibility.

CR-AM-05 establishes the missing aggregation/view layer. The next logical step is to establish when an AssessmentResult is actually fit for comparison across organizations.

The important architectural progression is:

CR-AM-02  Canonical Assessment Metamodel
     ↓
CR-AM-03  Assessment Catalog Migration
     ↓
CR-AM-04  Assessment Result Operations
     ↓
CR-AM-05  Assessment Views & Aggregation
     ↓
CR-AM-06  Benchmark Model & Eligibility       ← NEXT
     ↓
CR-AM-07  Comparative Benchmarking
     ↓
CR-AM-08  Benchmark Analytics & Insights

CR-AM-06 — Benchmark Model & Eligibility

Objective

Define the canonical model for determining:

Can this assessment result legitimately participate in a cross-organization comparison?

This is deliberately different from CR-AM-07.

CR-AM-06 answers “is it comparable?”

CR-AM-07 answers “how do we compare it?”

⸻

1. The key architecture

AssessmentResult
      │
      ▼
BenchmarkEligibility
      │
      ├── Scenario compatibility
      ├── Capability compatibility
      ├── Measure compatibility
      ├── AssessmentModel compatibility
      ├── ScoringModel compatibility
      ├── MaturityModel compatibility
      ├── Evidence sufficiency
      ├── Assessment currency
      └── Population requirements
              │
              ▼
       Benchmark Cohort
              │
              ▼
       CR-AM-07 Comparison

This preserves the distinction we have been building:

Enterprise View
    = aggregation
Benchmark
    = controlled comparison

⸻

2. Why this is the correct next CR

CR-AM-05 lets us say:

“Organization A has maturity L3 in Capability X.”

CR-AM-06 lets us establish:

“Organization A’s L3 result is comparable with Organization B’s L4 result.”

That second statement requires substantially more governance.

For example, these two results should not automatically be compared:

Organization A
Scenario: Service Assurance
Capability: Closed Loop Automation
Measure: Automation Coverage
Maturity Model: AOMM v1

versus:

Organization B
Scenario: Network Operations
Capability: Closed Loop Automation
Measure: Automation Coverage
Maturity Model: AOMM v2

Even though the labels appear identical.

⸻

3. Canonical BenchmarkEligibility

I would make this a structured component of AssessmentResult, rather than immediately creating a separate benchmark-result entity.

Conceptually:

AssessmentResult
│
├── observations
├── scores
├── maturity
├── findings
├── confidence
├── lineage
│
└── benchmark
     ├── eligibility
     ├── eligibilityReasons
     ├── comparabilityKey
     └── status

The repository already has a benchmark structure in AssessmentResult; CR-AM-06 should make its semantics normative rather than replacing it.

⸻

4. Eligibility status

Establish a controlled vocabulary:

eligible
provisional
not-eligible
not-comparable
insufficient-data
expired

I would distinguish:

not-eligible

The result fails a benchmark participation rule.

not-comparable

The result is valid, but there is no compatible comparison population.

insufficient-data

The result itself lacks required evidence/coverage.

provisional

The result can participate only under explicitly defined conditions.

That distinction becomes valuable for benchmark governance.

⸻

5. Comparability Key

This is probably the most important addition.

A benchmark result needs a canonical comparability identity.

For example:

comparability:
  key:
    scenario: service-assurance
    capability: closed-loop-automation
    measure: automation-coverage
    assessment_model: aom-assessment
    scoring_model: aom-score-v1
    maturity_model: aom-v1

Two results belong to the same benchmark population only when their relevant semantic dimensions are compatible.

This prevents the classic benchmark problem:

comparing things that happen to have the same label but do not have the same meaning.

⸻

6. Benchmark Cohort

CR-AM-06 should introduce the concept of a BenchmarkCohort.

BenchmarkCohort
│
├── cohort definition
├── eligibility criteria
├── comparability key
├── population
├── minimum sample size
├── temporal boundary
└── governance

Example:

Telecom Operators
+
Service Assurance
+
Closed Loop Automation
+
Automation Coverage
+
AOMM v1
+
2026

That produces a legitimate comparison population.

⸻

7. Benchmark is therefore a population construct

This is an important conceptual improvement.

Don’t model:

Organization → Benchmark

Model:

AssessmentResult
      │
      ▼
Eligibility
      │
      ▼
BenchmarkCohort
      │
      ▼
Comparison

The benchmark exists between comparable results, not inside an individual organization.

⸻

8. Benchmark eligibility dimensions

CR-AM-06 should establish at least these:

Dimension	Question
Scenario	Same defined scenario?
Capability	Same capability semantics?
Measure	Same measurement definition?
Assessment Model	Same compatible assessment method?
Scoring Model	Same scoring semantics?
Maturity Model	Same compatible maturity semantics?
Period	Same comparison period?
Evidence	Sufficient evidence?
Coverage	Sufficient assessment coverage?
Confidence	Meets minimum confidence?
Version	Compatible versions?
Population	Meets cohort requirements?

⸻

9. Version compatibility

This should reuse the compatibility architecture already established rather than inventing another mechanism.

For example:

MaturityModel v1.0
       │
       │ compatible
       ▼
MaturityModel v1.1

may permit comparison.

But:

MaturityModel v1
       X
MaturityModel v2

should not be assumed comparable.

Where versions differ, the result should carry:

compatibility:
  status: compatible
  basis: explicit-mapping

rather than relying on version-number proximity.

⸻

10. Benchmark eligibility ≠ benchmark ranking

This is the CR-AM-06 boundary.

Do not implement:

percentile
rank
quartile
top-performer
peer-position

yet.

Those belong to CR-AM-07.

CR-AM-06 produces:

Eligible

CR-AM-07 produces:

Organization A
    ↓
Score = 82
    ↓
Percentile = 87
    ↓
Peer position = 4/27

⸻

11. Benchmark Eligibility Example

A valid result might contain:

benchmark:
  status: eligible
  comparability:
    key:
      scenario: service-assurance
      capability: closed-loop-automation
      measure: automation-coverage
      assessment_model: cla-assessment-v1
      scoring_model: cla-score-v1
      maturity_model: cla-maturity-v1
  eligibility:
    evidence: true
    coverage: true
    confidence: true
    currency: true
    compatibility: true
  cohort:
    id: telecom-service-assurance-2026

An invalid one:

benchmark:
  status: not-comparable
  reasons:
    - maturity-model-incompatible
    - scenario-definition-mismatch

⸻

12. This completes the enterprise → benchmark transition

We then have:

                     AssessmentResults
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
      Enterprise View              Eligibility Filter
             │                             │
             ▼                             ▼
        Heatmap                     Benchmark Cohort
                                           │
                                           ▼
                                      Comparison

This is the architecture you originally needed.

The enterprise heatmap remains useful without pretending to be a benchmark.

⸻

13. Implementation scope

The CR should modify approximately:

assessment-models/
├── schemas/
│   ├── assessment-result.schema.json
│   └── benchmark-cohort.schema.json
│
├── model/
│   └── assessment-metamodel.puml
│
├── vocabulary/
│   ├── benchmark-status.yaml
│   └── eligibility-reasons.yaml
│
├── benchmark/
│   ├── cohort-examples/
│   └── eligibility-examples/
│
├── governance/
│   └── benchmark-eligibility.md
│
└── tests/
    └── benchmark/

I would not introduce a generic BenchmarkResult yet.

⸻

14. Acceptance criteria

CR-AM-06 should not be considered complete until:

* AssessmentResult has normative benchmark eligibility semantics.
* Eligibility status is controlled vocabulary.
* Comparability is explicitly represented.
* Scenario/capability/measure compatibility is validated.
* Assessment/scoring/maturity model compatibility is validated.
* Evidence, coverage and confidence can influence eligibility.
* Benchmark cohorts have explicit definitions.
* Historical results retain their original eligibility determination.
* Eligibility does not calculate rankings.
* Ineligible results cannot silently enter a benchmark cohort.
* Existing enterprise heatmaps remain unaffected.
* Existing assessment results remain schema-compatible.
* CI contains positive and negative eligibility tests.

⸻

15. The most important CR-AM-06 design principle

I would put this directly into the CR:

Benchmark eligibility is a governed determination about the comparability of an AssessmentResult; it is not a property inferred from the existence of a score or maturity level.

That prevents OpenDEA from eventually producing misleading statements such as:

"Company A is Level 4"

when the actual semantic statement should be:

"Company A achieved Level 4 under Maturity Model X,
for Capability Y, in Scenario Z, using Measure M,
and the resulting assessment is eligible for comparison
within Benchmark Cohort C."

That is the level of semantic precision needed before building the actual benchmarking machinery.

After CR-AM-06

The next CR should then be CR-AM-07 — Comparative Benchmarking & Peer Analytics:

AssessmentResult
      ↓
Eligibility
      ↓
BenchmarkCohort
      ↓
CR-AM-07
      ↓
┌──────────────┬─────────────┬──────────────┐
│ Distribution │ Percentile  │ Peer Ranking │
└──────────────┴─────────────┴──────────────┘
      ↓
Benchmark Insight

And importantly, CR-AM-07 should consume CR-AM-06; it should not redefine eligibility itself. 