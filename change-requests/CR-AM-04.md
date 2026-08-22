Given the current state of dea-metamodel and the CR-AM-03 we just implemented, I would make the next CR CR-AM-04 — Assessment Result Operations & Maturity Interpretation.

The key reason is that we should not create another metamodel layer yet. CR-AM-02 established the canonical structures; CR-AM-03 makes the existing assessment catalog conform to them. The next missing capability is turning an assessment definition into a repeatable, traceable assessment result, including the maturity determination.

CR-AM-04 — Assessment Result Operations & Maturity Interpretation

Parent: CR-AM-03
Type: Assessment Execution / Results / Maturity
Priority: P0
Status: Proposed

Objective

Establish the canonical operational lifecycle:

AssessmentModel
      │
      ▼
AssessmentExecution
      │
      ├── Observation
      ├── Evidence
      └── Finding
              │
              ▼
       AssessmentResult
              │
       ┌──────┼───────────┐
       ▼      ▼           ▼
     Score  Maturity    Findings
              │
              ▼
        MaturityLevel

The CR should prove that the same canonical machinery can support:

1. capability assessment;
2. scenario assessment;
3. maturity assessment;
4. enterprise assessment;
5. future benchmarking.

⸻

1. The crucial distinction

CR-AM-04 should formally establish this chain:

MaturityModel
     │
     │ defines
     ▼
MaturityLevel
     ▲
     │ determines
     │
AssessmentResult
     ▲
     │ summarizes
     │
AssessmentExecution
     ▲
     │ executes
     │
AssessmentModel

Therefore:

Maturity is an interpretation of an AssessmentResult, not a property of the AssessmentModel itself.

The AssessmentModel can declare that it uses a MaturityModel, but the actual maturity level belongs to the resulting assessment determination.

⸻

2. Add the missing semantic layer: Determination

I would make one important refinement before implementing this CR.

Currently the architecture has:

Observation → AssessmentResult

I recommend making the conceptual chain:

Observation
     │
     ▼
Score
     │
     ▼
AssessmentDetermination
     │
     ├── Score
     ├── MaturityLevel
     ├── Finding
     ├── Confidence
     └── Evidence
     │
     ▼
AssessmentResult

You do not necessarily need to introduce AssessmentDetermination as a new schema immediately.

It can initially be a conceptual construct represented within AssessmentResult.

But the semantic distinction should be documented:

* Observation = what was observed;
* Score = numerical/ordinal evaluation;
* MaturityLevel = interpreted maturity position;
* Finding = assessment conclusion;
* AssessmentResult = authoritative result package.

This will prevent the result model from becoming a “score bag.”

⸻

3. Result granularity

CR-AM-04 should support results at multiple levels:

Enterprise
   │
   ├── Capability
   │      ├── Measure
   │      └── Scenario
   │
   └── Assessment

A result should therefore be traceable down to:

Organization
 → Assessment
 → Scenario
 → Capability
 → Measure
 → Observation
 → Score
 → Maturity

That becomes the fundamental analytical grain.

⸻

4. Maturity interpretation

The CR should establish a normative interpretation pipeline:

Observation
     │
     ▼
Measure Value
     │
     ▼
ScoringModel
     │
     ▼
Score
     │
     ▼
MaturityModel
     │
     ▼
MaturityLevel

For example:

Automation Adoption = 72%
          │
          ▼
     ScoringModel
          │
          ▼
        Score 3
          │
          ▼
 Autonomous Operations
     Maturity Model v1
          │
          ▼
        Level 3

This gives you an auditable explanation of why an organization received a particular maturity level.

⸻

5. Maturity must support multiple dimensions

This becomes especially important for the models you’ve been developing.

A maturity result should be able to say:

maturity:
  model:
    id: dea:maturity-autonomous-operations
    version: 1.0.0
  dimensions:
    - id: automation
      level: 4
    - id: self-governance
      level: 3
    - id: self-adaptation
      level: 2
  overall:
    level: 3

This prevents the dangerous simplification:

Enterprise = Level 3

when the actual result is:

Automation       L4
Self-Governance  L3
Self-Adaptation  L2

The overall level must therefore be an explicit aggregation/interpretation, not an implicit average.

⸻

6. Introduce aggregation semantics

This is probably the most important new capability.

Define:

MaturityAggregationModel

conceptually as:

Dimension Results
       │
       ▼
Aggregation Rule
       │
       ▼
Overall Maturity

For example:

min
average
weighted-average
threshold
dominant-level
custom

But I would not immediately create a generic aggregation engine.

Instead, CR-AM-04 should define the contract for declaring the aggregation method.

That prevents us from hardcoding:

overall maturity = average(dimensions)

which is almost certainly wrong for many maturity models.

⸻

7. Evidence becomes first-class

The result must establish:

Claim
  │
  ├── Observation
  ├── Evidence
  └── Confidence

For example:

Capability:
Closed Loop Automation
Measure:
Automation Coverage
Observation:
72%
Evidence:
Production telemetry
Confidence:
High
Score:
3
Maturity:
Performing

This is essential if the assessment is eventually used for:

* executive decisions;
* investment justification;
* benchmarking;
* governance;
* AI/agentic decision-making.

⸻

8. Result lineage

Every result must remain reproducible after model evolution.

Therefore:

lineage:
  assessment_model:
    id:
    version:
  scoring_model:
    id:
    version:
  maturity_model:
    id:
    version:
  aggregation_model:
    id:
    version:
  measures:
    - id:
      version:

If the maturity model subsequently becomes v2:

Maturity v1
     │
     ├── Result 2026-A
     │
     └── Result 2026-B
Maturity v2
     │
     └── Result 2027-A

Old results must remain interpretable.

This is one of the central reasons for the entire canonical architecture.

⸻

9. AssessmentResult becomes the enterprise analytical primitive

This is where CR-AM-04 connects directly to your original enterprise heatmap problem.

Instead of benchmarking a heatmap:

Enterprise Heatmap
       ↓
"Organization = 73%"

we have:

AssessmentResults
       │
       ├── Capability Results
       ├── Scenario Results
       ├── Maturity Results
       └── Measure Results
              │
              ▼
       Enterprise View

The heatmap becomes a projection of results, rather than a separate assessment model.

That is the correct architecture.

⸻

10. This enables the three assessment modes

Mode A — Enterprise Diagnostic

Many Results
     ↓
Aggregation
     ↓
Heatmap

Good for enterprise transformation management.

Not necessarily benchmarkable.

Mode B — Capability Assessment

Organization
    ↓
Capability
    ↓
Measures
    ↓
Result

Good for capability management.

Mode C — Scenario Benchmark

Organization
    ↓
Scenario
    ↓
Capability
    ↓
Measures
    ↓
Result
    ↓
Comparable Population

Good candidate for benchmarking.

This distinction should become normative in CR-AM-04.

⸻

11. Acceptance Criteria

I would make these the core ACs.

ID	Acceptance Criterion
AC-AM04-01	Canonical AssessmentExecution produces a conformant AssessmentResult
AC-AM04-02	Result preserves complete versioned lineage
AC-AM04-03	Observation is distinguishable from Score
AC-AM04-04	Score is distinguishable from MaturityLevel
AC-AM04-05	Maturity interpretation references an explicit MaturityModel
AC-AM04-06	Multi-dimensional maturity results are supported
AC-AM04-07	Overall maturity aggregation is explicit
AC-AM04-08	Evidence is traceable to assessment conclusions
AC-AM04-09	Result can be reproduced from versioned dependencies
AC-AM04-10	Existing CR-AM-03 migrated assessments can generate results
AC-AM04-11	Enterprise, Capability and Scenario result views can be derived
AC-AM04-12	No benchmark calculation is introduced
AC-AM04-13	Historical results remain valid after model version changes
AC-AM04-14	CI validates result, lineage and maturity conformance

⸻

12. The resulting OpenDEA architecture

After CR-AM-04, the architecture becomes:

                         ASSESSMENT DEFINITION
                                  │
                         ┌────────▼────────┐
                         │ AssessmentModel │
                         └────────┬────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
             Capability        Scenario          Measure
                                  │
                                  ▼
                       AssessmentExecution
                                  │
                     ┌────────────┼────────────┐
                     ▼            ▼            ▼
                Observation    Evidence      Finding
                     │
                     ▼
                   Score
                     │
                     ▼
             ┌────────────────┐
             │ MaturityModel  │
             └───────┬────────┘
                     ▼
               MaturityLevel
                     │
                     ▼
              AssessmentResult
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   Capability     Enterprise    Scenario
      View          View          View
        │
        └──────────────────────┐
                               ▼
                       Benchmark Eligibility

⸻

13. Then the roadmap becomes very clean

CR-AM-01
Architecture
    ↓
CR-AM-02
Canonical Metamodel
    ↓
CR-AM-03
Catalog Migration
    ↓
CR-AM-04
Result Operations & Maturity
    ↓
CR-AM-05
Enterprise Assessment Views
    ↓
CR-AM-06
Benchmark Model
    ↓
CR-AM-07
Comparative Benchmarking

And CR-AM-05 is where I would finally formalize the enterprise heatmap/portfolio view.

The critical architectural principle is:

Don’t make the heatmap the canonical assessment object. Make AssessmentResult the canonical fact, and make the heatmap a governed aggregation/view over those facts.

That gives OpenDEA the ability to support enterprise maturity heatmaps, capability assessments and scenario-based organizational benchmarking from the same underlying assessment evidence, without creating competing assessment models.