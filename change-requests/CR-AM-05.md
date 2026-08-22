Yes. Based on the actual state of technehub-labs/dea-metamodel@657e7b3, I would make CR-AM-05 the change that establishes the canonical assessment-view and aggregation layer.

This is an important refinement to the earlier roadmap: CR-AM-05 should not create a second “Enterprise Assessment” metamodel. The existing AssessmentResult is already the persistent analytical fact: it contains observations, scores, maturity results, benchmark results, findings, confidence, status and lineage. 

The purpose of CR-AM-05 is therefore to define how multiple canonical results are selected, grouped, aggregated and projected into enterprise/capability/scenario views.

OpenDEA Assessment Models at commit 657e7b3⁠

CR-AM-05 — Assessment Views & Aggregation

Status: Proposed
Priority: P0
Parent: CR-AM-04
Depends on: CR-AM-01, CR-AM-02, CR-AM-03, CR-AM-04
Scope: Assessment results, aggregation, analytical views, enterprise heatmaps
Core principle: AssessmentResult is the canonical fact; an assessment view is a derived projection.

⸻

1. Executive Summary

CR-AM-05 establishes the canonical mechanism for transforming individual AssessmentResult instances into governed analytical views.

The change addresses a fundamental distinction:

An enterprise heatmap is not itself an assessment. It is a view over assessment results.

The canonical architecture becomes:

AssessmentModel
      │
      ▼
AssessmentExecution
      │
      ▼
AssessmentResult
      │
      │
      ├───────────────┐
      │               │
      ▼               ▼
Capability View   Scenario View
      │               │
      └───────┬───────┘
              ▼
       Assessment View
              │
       ┌──────┼───────────┐
       ▼      ▼           ▼
    Profile Heatmap     Trend
              │
              ▼
       Enterprise View

This creates the missing layer between assessment results and enterprise decision views.

⸻

2. Why CR-AM-05 Is Needed

The current canonical result already contains the right primitives.

AssessmentResult supports:

* observations;
* scores;
* maturity;
* benchmark information;
* findings;
* confidence;
* status;
* lineage. 

The repository also explicitly identifies Enterprise Heatmap as one of the four architectural tests:

Enterprise
 → Multiple Capabilities
 → Assessment Results
 → Heatmap

and distinguishes it from:

Organisation
 → Capability
 → Scenario
 → Assessment
 → Result

and from benchmark comparison. 

What is missing is the formal contract for the arrow:

Multiple AssessmentResults
             │
             ▼
       Aggregation / View
             │
             ▼
       Enterprise Heatmap

CR-AM-05 establishes that contract.

⸻

3. Architectural Decision

Adopt the following rule:

AssessmentResult is the canonical analytical fact. AssessmentView is a derived representation of one or more results.

Therefore:

AssessmentResult
      ≠
AssessmentView

and:

AssessmentView
      ≠
AssessmentModel

and:

AssessmentView
      ≠
MaturityModel

This keeps the architecture normalized.

⸻

4. Canonical Four-Layer Assessment Architecture

After CR-AM-05:

┌────────────────────────────────────────────────────────────┐
│  1. DEFINITION                                             │
│                                                            │
│  AssessmentModel                                           │
│  Capability                                                │
│  Scenario                                                  │
│  Measure                                                   │
│  ScoringModel                                              │
│  MaturityModel                                             │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│  2. EXECUTION                                              │
│                                                            │
│  AssessmentExecution                                       │
│  Observation                                               │
│  Evidence                                                  │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│  3. FACT                                                   │
│                                                            │
│  AssessmentResult                                          │
│                                                            │
│  The authoritative record of what was determined.          │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│  4. VIEW                                                   │
│                                                            │
│  AssessmentView                                            │
│  CapabilityProfile                                         │
│  ScenarioProfile                                           │
│  EnterpriseHeatmap                                         │
│  TrendView                                                 │
│                                                            │
│  Derived from AssessmentResults.                           │
└────────────────────────────────────────────────────────────┘

This is the architecture I recommend making normative.

⸻

5. Do We Need an AssessmentView Schema?

Yes—but carefully.

I would introduce a small, generic assessment-view.schema.json.

I would not create separate first-class schemas for:

* EnterpriseHeatmap;
* CapabilityHeatmap;
* ScenarioHeatmap;
* MaturityHeatmap;
* TrendView.

Those should initially be view types, not separate metamodel entities.

The canonical structure should be:

view:
  id:
  type:
  subject:
  period:
  filters:
  aggregation:
  source_results:
  dimensions:
  measures:
  cells:
  lineage:

with:

type =
    enterprise-profile
    capability-profile
    scenario-profile
    heatmap
    trend

This prevents the metamodel from proliferating around presentation formats.

⸻

6. Canonical AssessmentView

Conceptually:

AssessmentView
│
├── identity
├── view_type
├── subject
├── assessment_period
├── filters
├── source_results
├── dimensions
├── measures
├── aggregation
├── cells
└── lineage

The key point is that every view has a query/selection boundary and an aggregation declaration.

⸻

7. Source Results

Every view must explicitly identify its source results.

Example:

source_results:
  - id: dea:result-001
    version: 1.0.0
  - id: dea:result-002
    version: 1.0.0
  - id: dea:result-003
    version: 1.0.0

This provides reproducibility.

The view is therefore not:

“current state of the organization.”

It is:

“derived state based on these exact AssessmentResults.”

⸻

8. View Subject

The subject identifies what the view represents.

Examples:

subject:
  id: dea:enterprise-example
  type: organization

or:

subject:
  id: dea:capability-technology-architecture
  type: capability

or:

subject:
  id: dea:scenario-service-assurance
  type: scenario

⸻

9. Selection Context

CR-AM-05 should define a canonical filter context.

Minimum:

AssessmentModel
Capability
Scenario
Measure
MaturityModel
AssessmentPeriod
Organization
ResultStatus

For example:

filters:
  assessment_models:
    - dea:assessment-technology
  capabilities:
    - dea:capability-technology-architecture
    - dea:capability-technology-platform
  scenarios:
    - dea:scenario-enterprise
  assessment_period:
    start:
    end:

This is essential for preventing meaningless aggregation.

⸻

10. Aggregation Model

This is the central addition.

A view must declare how its values are derived.

Conceptually:

AssessmentResults
       │
       ▼
Selection
       │
       ▼
Grouping
       │
       ▼
Aggregation
       │
       ▼
View Cell

The aggregation declaration should contain:

aggregation:
  method:
  input:
  grouping:
  weighting:
  missing_data:
  normalization:

⸻

11. Do Not Hard-Code “Average”

This is a critical design constraint.

Do not define:

Enterprise maturity =
average(all capability maturity)

as the canonical rule.

Different maturity models have different semantics.

Possible methods include:

minimum
maximum
average
weighted-average
median
threshold
dominant-level
coverage
custom

But CR-AM-05 should define these as aggregation semantics, not prescribe one universal enterprise maturity algorithm.

⸻

12. Separate Score Aggregation from Maturity Aggregation

This distinction is essential.

For example:

Score:
    73%
Maturity:
    Level 3

These are not interchangeable.

Therefore:

Score Aggregation
        ≠
Maturity Aggregation

A view may legitimately show:

Technology Architecture
Score:     78%
Maturity:  Level 4

while another dimension may show:

Technology Lifecycle
Score:     61%
Maturity:  Level 3

⸻

13. Enterprise Heatmap

The canonical Enterprise Heatmap should be defined as:

Enterprise
    │
    ▼
AssessmentResults
    │
    ▼
Group By Capability
    │
    ▼
Select Measure / Score / Maturity
    │
    ▼
Heatmap Cells

Example:

Capability	Score	Maturity
Technology Architecture	78	4
Technology Platform	71	3
Technology Lifecycle	61	3
Automation	84	4
Self-Governance	58	3

The heatmap is therefore a projection, not a new assessment.

⸻

14. Enterprise Heatmap Must Support Multiple Dimensions

A single flat heatmap is insufficient.

The view should support:

Rows:
Capability
Columns:
Assessment Period
Cell:
Score / Maturity / Measure

or:

Rows:
Capability
Columns:
Scenario
Cell:
Maturity

or:

Rows:
Capability
Columns:
Assessment Model
Cell:
Score

The same AssessmentView structure should support all of these.

⸻

15. Capability Profile

A Capability Profile is a constrained view:

AssessmentView
  type = capability-profile

Example:

Capability:
Technology Architecture
        Measures
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
 Standard Reuse  Debt
    │      │      │
    ▼      ▼      ▼
   82%    76%    41%
           │
           ▼
      Maturity L4

This is the principal view for capability-level assessment.

⸻

16. Scenario Profile

A Scenario Profile represents performance within a defined context.

Scenario:
Service Assurance
Capabilities:
 ├── Automation
 ├── Self-Governance
 └── Self-Adaptation
Measures:
 ├── Closed-loop rate
 ├── Exception rate
 └── Adaptation latency

This is particularly important because scenario + capability + measure is the future controlled benchmark grain.

⸻

17. Enterprise View Is Not a Benchmark

CR-AM-05 must explicitly prohibit the following inference:

Enterprise Heatmap
       ↓
Benchmark

Instead:

Enterprise Heatmap
       =
Internal aggregation
Benchmark
       =
Controlled comparison across eligible populations

The repository already separates these architectural paths: enterprise heatmap is Test A, while multi-organization benchmark is Test D. 

This distinction should now become normative.

⸻

18. Benchmark Eligibility Remains a Property

The current AssessmentResult already has a benchmark structure with statuses such as:

eligible
not-comparable
insufficient-data
provisional

and optional percentile/rank/sample size fields. 

CR-AM-05 should not calculate benchmark ranks.

Instead, it should allow an enterprise view to filter:

benchmark_eligible = true

when preparing data for the future benchmark layer.

⸻

19. Time-Series Views

CR-AM-05 should also introduce the concept of a time-aware view.

Example:

              2026-Q1   2026-Q2   2026-Q3
Architecture    L2        L3        L4
Platform        L3        L3        L4
Lifecycle       L2        L2        L3

This is important because maturity assessment is not only about current state.

It is also:

Current State
     ↓
Trajectory
     ↓
Progression

⸻

20. Never Infer Progression from Different Models

A trend is valid only where the source results are sufficiently compatible.

For example:

Maturity Model v1
       ↓
Maturity Model v2

must not automatically be interpreted as:

Level 3 → Level 4

unless an explicit compatibility/equivalence mapping exists.

The existing repository already has versioning and compatibility governance and explicitly preserves historical result interpretation. 

CR-AM-05 should enforce that principle in view generation.

⸻

21. View Lineage

Every view must preserve:

lineage:
  source_results:
    - id:
      version:
  assessment_models:
    - id:
      version:
  scoring_models:
    - id:
      version:
  maturity_models:
    - id:
      version:
  aggregation:
    id:
    version:

This allows:

Enterprise Heatmap
       ↓
Source Results
       ↓
Original Evidence

to be traced.

That is essential for executive and audit-grade use.

⸻

22. Proposed Repository Changes

Add:

assessment-models/
├── schemas/
│   ├── assessment-view.schema.json
│   └── aggregation-model.schema.json
│
├── model/
│   └── assessment-view.puml
│
├── views/
│   ├── enterprise/
│   │   └── technology-heatmap.yaml
│   ├── capability/
│   │   └── technology-architecture-profile.yaml
│   ├── scenario/
│   │   └── service-assurance-profile.yaml
│   └── trend/
│       └── technology-maturity-trend.yaml
│
├── aggregation/
│   ├── aggregation-methods.yaml
│   └── examples/
│
├── governance/
│   └── views.md
│
└── tests/
    └── views/

⸻

23. Important: Do We Need AggregationModel?

Yes, but keep it minimal.

The reason is versioning.

If:

Enterprise View v1

uses:

weighted-average

and later:

Enterprise View v2

uses:

threshold

then historical views must remain interpretable.

Therefore:

AggregationModel

should be a versioned model reference.

Conceptually:

AggregationModel
│
├── method
├── grouping
├── weighting
├── normalization
├── missing-data rule
└── eligibility rule

This should not become a generic mathematical engine in CR-AM-05.

⸻

24. Proposed AggregationModel

Example:

id: dea:aggregation-capability-score
version: 1.0.0
name: Capability Score Aggregation
method: weighted-average
input:
  type: score
grouping:
  dimension: capability
weighting:
  source: measure-weight
missing_data:
  method: exclude
normalization:
  required: true

The model describes the aggregation contract.

An implementation may execute that contract independently.

⸻

25. View Cell

A heatmap cell should be a structured result, not merely a number.

Example:

cell:
  subject:
    id: dea:capability-technology-architecture
    type: capability
  measure:
    id: dea:measure-architecture-standardization
    version: 1.0.0
  value:
    score: 78
    normalized: 0.78
  maturity:
    model:
      id: dea:maturity-technology
      version: 1.0.0
    level: 4
  confidence: high
  source_results:
    - dea:result-001
    - dea:result-004

This allows a UI to display a heatmap while retaining semantic traceability.

⸻

26. Missing Data Is Not Zero

This should be a normative rule.

If:

Technology Architecture = 78
Technology Platform = no assessment

the heatmap must show:

Architecture  78
Platform      N/A

not:

Platform      0

unless the source AssessmentResult explicitly says zero.

This is essential for enterprise heatmaps because otherwise assessment coverage gaps become false capability deficiencies.

⸻

27. Confidence Must Survive Aggregation

If source results contain:

high
medium
low

confidence, the view must not silently discard it.

At minimum:

View Cell
 ├── Value
 ├── Confidence
 └── Coverage

should be available.

This allows:

Score = 78
Confidence = Low
Coverage = 42%

rather than presenting “78” as false precision.

⸻

28. Coverage Is a First-Class Analytical Dimension

The enterprise heatmap should therefore support:

Value
Coverage
Confidence

Example:

Capability	Maturity	Coverage	Confidence
Architecture	L4	100%	High
Platform	L3	75%	Medium
Lifecycle	L3	40%	Low

This makes the heatmap diagnostically useful.

⸻

29. Assessment Coverage vs Capability Performance

CR-AM-05 must distinguish:

Performance

from:

Assessment Coverage

A capability with no assessment is:

Unknown

not:

Low

This is one of the most important controls in the enterprise view.

⸻

30. Acceptance Criteria

AC-AM05-01 — Canonical View

A generic AssessmentView contract exists.

AC-AM05-02 — Result Source

Every view explicitly identifies source AssessmentResults.

AC-AM05-03 — Versioned Lineage

All source models and results are versioned.

AC-AM05-04 — Selection

A view can explicitly define its selection context.

AC-AM05-05 — Aggregation

A view explicitly identifies its aggregation method/model.

AC-AM05-06 — Score/Maturity Separation

Score aggregation and maturity aggregation are distinct.

AC-AM05-07 — Capability Profile

A capability-level view is demonstrated.

AC-AM05-08 — Scenario Profile

A scenario-level view is demonstrated.

AC-AM05-09 — Enterprise Heatmap

An enterprise heatmap is demonstrated from multiple AssessmentResults.

AC-AM05-10 — Time Series

A historical/trend view is demonstrated.

AC-AM05-11 — Missing Data

Missing assessments are represented as unknown/N/A, not zero.

AC-AM05-12 — Coverage

View cells can expose assessment coverage.

AC-AM05-13 — Confidence

View cells preserve or explicitly aggregate confidence.

AC-AM05-14 — Benchmark Separation

Enterprise views do not imply benchmark status.

AC-AM05-15 — Compatibility

Incompatible model versions cannot silently participate in a trend or aggregate.

AC-AM05-16 — Reproducibility

A view can be reconstructed from its declared source results and aggregation model.

AC-AM05-17 — No Duplicate Assessment Entity

No new EnterpriseAssessment or HeatmapAssessment entity is introduced.

AC-AM05-18 — CI

All schemas, examples, lineage and view tests pass.

⸻

31. Architectural Acceptance Test

The decisive test is:

                    Organization
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        Capability     Scenario     Assessment
            │            │            │
            └────────────┼────────────┘
                         ▼
                 AssessmentResult
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       Capability      Scenario    Enterprise
         View           View         View
                                       │
                                       ▼
                                    Heatmap

All three views must use the same AssessmentResult facts.

If separate data structures are required for each view, CR-AM-05 has failed.

⸻

32. Implementation Instruction

The implementation should be done in the following order.

Step 1 — Freeze CR-AM-04 dependency

Do not implement CR-AM-05 against an assumed result structure.

First ensure CR-AM-04 has established:

Observation
Score
MaturityResult
Finding
AssessmentResult
Lineage

The current result schema already provides these basic structures. 

⸻

Step 2 — Add the View Concept to the PlantUML

Extend:

assessment-models/model/assessment-metamodel.puml

with:

AssessmentView
AggregationModel
ViewCell

but keep them on the view/analytical side of the model.

Do not change the semantics of:

AssessmentModel
AssessmentExecution
AssessmentResult
Capability
Scenario
Measure
MaturityModel

unless required by a concrete conformance defect.

⸻

Step 3 — Create aggregation-model.schema.json

Implement the minimum contract:

id
version
name
method
input
grouping
weighting
missing_data
normalization
compatibility

Use the repository’s existing common definitions and versioning patterns.

⸻

Step 4 — Create assessment-view.schema.json

Require:

id
version
type
subject
assessment_period
source_results
aggregation
lineage

Allow:

filters
dimensions
measures
cells

as optional but structured components.

⸻

Step 5 — Add Controlled View Vocabulary

Create:

vocabulary/view-types.yaml

with initial types:

enterprise-profile
capability-profile
scenario-profile
heatmap
trend

Do not create a vocabulary entry for every visualization.

For example:

heatmap

is a view type.

radar
table
bar-chart

are presentation formats and should remain outside the metamodel.

⸻

Step 6 — Add Aggregation Vocabulary

Create:

vocabulary/aggregation-methods.yaml

Initial controlled values:

identity
sum
count
minimum
maximum
average
weighted-average
median
threshold
dominant-level
coverage

Include semantic descriptions and applicability.

⸻

Step 7 — Implement Enterprise Heatmap Example

Create:

views/enterprise/technology-heatmap.yaml

Use multiple existing canonical results.

The implementation must demonstrate:

multiple AssessmentResults
        ↓
group by Capability
        ↓
select Score
        ↓
aggregate
        ↓
heatmap cells

⸻

Step 8 — Implement Capability Profile

Create:

views/capability/technology-architecture-profile.yaml

It should demonstrate:

Capability
   ↓
Measures
   ↓
Scores
   ↓
Maturity
   ↓
Evidence / Confidence

⸻

Step 9 — Implement Scenario Profile

Create:

views/scenario/service-assurance-profile.yaml

Demonstrate:

Scenario
   ↓
Capabilities
   ↓
Measures
   ↓
AssessmentResults

⸻

Step 10 — Implement Trend Example

Create:

views/trend/technology-maturity-trend.yaml

Use multiple historical results.

The example must prove that:

same AssessmentModel
same ScoringModel
same MaturityModel

can be compared across assessment periods.

⸻

Step 11 — Add Compatibility Guard

Before including two results in a trend or aggregate, validate:

AssessmentModel compatibility
ScoringModel compatibility
MaturityModel compatibility
Measure compatibility
Scenario compatibility

Do not silently normalize incompatible results.

⸻

Step 12 — Add Coverage Calculation

For each view:

coverage =
assessed applicable population
/
total applicable population

The exact denominator must be defined by the view.

Never infer coverage merely from the number of source results.

⸻

Step 13 — Add Confidence Handling

Define a deterministic policy for aggregation.

For example:

high + high → high
high + medium → medium
medium + low → low

But this should be represented as an explicit policy/model, not buried in application code.

If confidence cannot be safely aggregated, preserve source confidence rather than inventing an aggregate confidence.

⸻

Step 14 — Add View Lineage

Every generated view must contain:

source_results
aggregation_model
assessment_models
scoring_models
maturity_models

with exact versions.

⸻

Step 15 — Add Conformance Tests

Tests should validate:

Schema
References
Source Results
Aggregation
Lineage
Compatibility
Coverage
Missing Data
Confidence

⸻

33. Recommended Test Dataset

Use a deliberately small synthetic enterprise:

Enterprise A
Capabilities:
  Technology Architecture
  Technology Platform
  Technology Lifecycle
  Automation
  Self-Governance
  Self-Adaptation
Scenarios:
  Enterprise
  Service Assurance
Assessment periods:
  2026-Q1
  2026-Q2

Then create:

12–18 AssessmentResults

rather than trying to construct a giant dataset.

The test should demonstrate:

                    Enterprise A
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 Technology         Operations       Modernization
        │                │                │
        ▼                ▼                ▼
   Results           Results           Results
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  Assessment Views

⸻

34. Important Existing-Repo Corrections to Include

The implementation should also clean up two inconsistencies already visible at 657e7b3.

First, the repository describes the compatibility governance as having five properties, while the current result schema and implementation use six compatibility dimensions in the architecture discussed earlier. The documentation needs to be synchronized. The repository’s README also still calls the compatibility documentation “five compatibility properties.” 

Second, the result schema’s $id still uses the retired Assessment-Models/dea-metamodel namespace:

https://github.com/Assessment-Models/dea-metamodel/...

even though the repository explicitly states that technehub-labs/dea-metamodel/assessment-models/ is now the single source of authority. 

CR-AM-05 should resolve the namespace issue before introducing additional externally consumed schemas.

⸻

35. What CR-AM-05 Must Not Do

Do not implement:

EnterpriseAssessment
EnterpriseMaturity
EnterpriseHeatmapAssessment
CapabilityHeatmapAssessment
AssessmentDashboard
Benchmark

as new core assessment entities.

Those would prematurely couple the information model to specific analytical or presentation use cases.

Instead:

AssessmentResult
       ↓
AssessmentView
       ↓
Presentation

is the correct abstraction.

⸻

36. Definition of Done

CR-AM-05 is Implemented when OpenDEA can take:

≥ 2 AssessmentModels
≥ 2 Capabilities
≥ 2 Scenarios
≥ multiple AssessmentResults
≥ multiple AssessmentPeriods

and generate, using only canonical result data:

1. Capability Profile
2. Scenario Profile
3. Enterprise Heatmap
4. Historical Trend

with:

✓ explicit selection
✓ explicit aggregation
✓ explicit source results
✓ versioned lineage
✓ coverage
✓ confidence
✓ missing-data handling
✓ compatibility validation
✓ maturity interpretation

and no new assessment-specific entity is required.

⸻

37. Resulting Architecture After CR-AM-05

The OpenDEA assessment architecture then becomes:

                         ┌─────────────────┐
                         │ AssessmentModel │
                         └────────┬────────┘
                                  │
                         AssessmentExecution
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ AssessmentResult│
                         └────────┬────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
                    ▼             ▼              ▼
               Capability      Scenario       Enterprise
                 View           View            View
                    │             │              │
                    └─────────────┼──────────────┘
                                  ▼
                          AssessmentView
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                 Profile       Heatmap        Trend
                                  │
                                  ▼
                       Future Benchmark Layer

This is the point at which the original enterprise problem becomes tractable:

enterprise heatmaps are useful for diagnosis, capability/scenario views provide semantic granularity, and only the appropriately controlled result population proceeds toward benchmarking.

The current repository already explicitly identifies these four architectural tests, including Enterprise Heatmap, Capability Assessment, Maturity Assessment and Benchmark; CR-AM-05 should now make the first three operational without prematurely implementing the fourth. 

Recommended next sequence

CR-AM-03
Assessment Catalog Migration
        ↓
CR-AM-04
Assessment Result Operations
        ↓
CR-AM-05
Assessment Views & Aggregation   ← NEXT
        ↓
CR-AM-06
Benchmark Model & Eligibility
        ↓
CR-AM-07
Comparative Benchmarking

The architectural guardrail for CR-AM-05 is simple:

Never store the heatmap as the truth. Store the AssessmentResults; derive the heatmap.

That principle is what will allow the OpenDEA assessment ecosystem to evolve incrementally without having to rebuild enterprise assessments whenever a capability, maturity model, scenario, scoring model or visualization changes.