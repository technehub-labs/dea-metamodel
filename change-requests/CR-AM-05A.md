CR-AM-05A — Hierarchical Assessment Dimensions & Instruments

Status: Proposed
Type: Canonical Metamodel Enhancement
Priority: P0
Repository: technehub-labs/dea-metamodel
Predecessors: CR-AM-01 → CR-AM-02 → CR-AM-03 → CR-AM-04 → CR-AM-05
Purpose: Establish the canonical structure for hierarchical assessment dimensions and extensible assessment instruments/questions without coupling questions to maturity levels.

⸻

1. Change Request

Title

CR-AM-05A — Hierarchical Assessment Dimensions & Instruments

Objective

Extend the canonical OpenDEA Assessment Metamodel to support:

1. Hierarchical Dimensions, including arbitrary levels of sub-dimension.
2. Capabilities organized independently from Dimension hierarchy.
3. Criteria and Indicators as the semantic bridge between assessment evidence and maturity determination.
4. Assessment Instruments as versioned question sets.
5. Questions as independently identifiable and versionable assessment assets.
6. Multiple response types rather than assuming every question returns a maturity score.
7. Explicit mapping from questions → observations/evidence → measures → criteria → maturity.
8. Incremental addition, retirement and revision of questions without requiring changes to the underlying maturity model.
9. Preservation of historical result semantics when assessment instruments evolve.

⸻

2. Problem Statement

The existing canonical assessment architecture establishes the important distinction between:

AssessmentModel
       ↓
AssessmentExecution
       ↓
AssessmentResult

and CR-AM-05 establishes:

AssessmentResult
       ↓
AssessmentView
       ↓
Capability / Scenario / Enterprise Views

However, the model still requires a canonical structure for how a maturity assessment is organized and administered.

In particular, an assessment may need to represent:

Dimension
   └── Sub-Dimension
       └── Sub-Dimension
           └── Capability
               └── Criterion
                   └── Question

while another assessment may use:

Dimension
   └── Capability
       └── Criterion
           └── Question

The metamodel must support both without introducing separate concepts such as:

SubDimension
SubSubDimension

or embedding questions directly within maturity levels.

⸻

3. Architectural Decision

Adopt the following canonical principle:

Dimension is a recursively composable assessment taxonomy. A sub-dimension is simply a Dimension with a parent Dimension.

Therefore:

Dimension
   │
   ├── parentDimension = null
   │       → root Dimension
   │
   └── parentDimension = Dimension
           → child Dimension

There is no SubDimension class.

This supports:

Dimension
└── Dimension
    └── Dimension
        └── Dimension

without requiring metamodel changes as the hierarchy evolves.

⸻

4. Target Conceptual Model

The canonical assessment architecture becomes:

                         MaturityModel
                              │
                              ▼
                         AssessmentModel
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
          Dimension Tree              AssessmentInstrument
                │                           │
        ┌───────┼───────┐                   ▼
        ▼       ▼       ▼               Questions
      Dim.    Dim.    Dim.                 │
        │       │       │                  ▼
        ▼       ▼       ▼               Responses
     Capability Capability Capability       │
        │       │       │                  ▼
        └───────┼───────┘              Observations
                │                           │
                ▼                           ▼
             Criteria ────────────────► Measures
                │                           │
                ▼                           ▼
             Indicators                   Scores
                │                           │
                └─────────────┬─────────────┘
                              ▼
                       Maturity Result
                              │
                              ▼
                      AssessmentResult
                              │
                              ▼
                       AssessmentView

⸻

5. Core Modeling Rule

The hierarchy must distinguish organizational taxonomy from assessment taxonomy.

Therefore:

Dimension hierarchy
        ≠
Capability hierarchy

A Dimension organizes the assessment.

A Capability represents an ability being assessed.

This permits:

Automation
└── Closed-Loop Automation
    └── Decision Automation

to assess:

Capability
├── Event Detection
├── Decision Automation
├── Policy Execution
└── Automated Remediation

while the same capabilities can be reused by another assessment model with a different dimension structure.

⸻

6. Scope

In scope

* Dimension
* Dimension hierarchy
* Capability mapping
* Criterion
* Indicator
* AssessmentInstrument
* Question
* ResponseSpecification
* question/criterion mapping
* question/measure mapping
* question versioning
* instrument versioning
* response types
* evidence requirements
* historical lineage
* schema validation
* examples and conformance tests

Explicitly out of scope

* benchmark ranking;
* percentile calculation;
* peer analytics;
* enterprise aggregation algorithms;
* presentation/UI models;
* replacing AssessmentResult;
* replacing MaturityModel;
* creating SubDimension as a separate class.

Those remain governed by CR-AM-05/06/07.

⸻

7. Canonical Dimension Model

Introduce/normalize:

Dimension

with at least:

id
version
name
description
parentDimension
sequence
status

Conceptually:

class Dimension {
    id
    version
    name
    description
    sequence
    status
}
Dimension "0..1" <-- "0..*" Dimension : parent

Semantics:

* zero parent = root dimension;
* one parent = child dimension;
* many children allowed;
* arbitrary depth permitted;
* hierarchy is directed and acyclic.

⸻

8. Dimension Constraints

The implementation must validate:

No cycles

A → B → C → A

is invalid.

No self-parent

A → A

is invalid.

Unique identity

Two dimensions cannot have the same identity/version within the same model namespace.

Stable identity

Changing the name should not require changing the identity.

Versioned semantics

A semantic change to a Dimension must create a new version according to repository versioning rules.

⸻

9. Dimension Example

Use a representative OpenDEA example:

id: dea:dimension-automation
version: 1.0.0
name: Automation
description: Degree to which operational activities are automated.

Child:

id: dea:dimension-closed-loop-automation
version: 1.0.0
name: Closed Loop Automation
parentDimension:
  id: dea:dimension-automation
  version: 1.0.0

Child:

id: dea:dimension-decision-automation
version: 1.0.0
name: Decision Automation
parentDimension:
  id: dea:dimension-closed-loop-automation
  version: 1.0.0

The resulting hierarchy:

Automation
└── Closed Loop Automation
    └── Decision Automation

⸻

10. Capability Relationship

The relationship should be:

Dimension "0..*" → "0..*" Capability

because:

* one Dimension can organize several capabilities;
* one Capability may be relevant to multiple Dimensions;
* different assessment models may organize the same Capability differently.

Example:

Automation
├── Closed Loop Automation
│
├──── assesses ────► Decision Automation
│
└──── assesses ────► Automated Remediation

Do not make Capability inherit from Dimension.

⸻

11. Criterion

Introduce or formalize:

Criterion

A Criterion represents a condition that must be demonstrated to establish a particular assessment/maturity state.

Example:

Criterion:
Automated Decision Enforcement

It may define:

id
version
name
description
applicability
threshold
evidenceRequirement

The criterion is the semantic bridge between evidence and maturity.

⸻

12. Indicator

Introduce or formalize:

Indicator

An Indicator identifies an observable characteristic relevant to determining whether a Criterion has been met.

Example:

Indicator:
Percentage of operational decisions automatically executed.

Possible value:

78%

This separates:

Question

from:

what is actually being measured.

⸻

13. Canonical Evidence Chain

The target relationship is:

Question
   ↓
Response
   ↓
Observation
   ↓
Indicator / Measure
   ↓
Criterion
   ↓
MaturityLevel

Not:

Question
   ↓
MaturityLevel

This is a critical architectural requirement.

⸻

14. Assessment Instrument

Introduce:

AssessmentInstrument

The Instrument represents the administerable assessment questionnaire/evidence collection mechanism.

It should contain:

id
version
name
description
status
assessmentModel
maturityModel
sections
questions

An instrument is versioned independently of the maturity model.

⸻

15. Why Instrument Must Be Separate

Example:

AOMM v1.0

defines:

L1 Initiating
L2 Emerging
L3 Performing
L4 Advancing
L5 Leading

Instrument v1.0:

30 questions

Instrument v1.1:

42 questions

Both can reference:

AOMM v1.0

This means the assessment questionnaire can improve without changing the underlying maturity semantics.

⸻

16. Question

Define:

Question

with:

id
version
text
description
responseSpecification
required
sequence
status

A Question is a reusable assessment asset.

Example:

id: dea:q-policy-enforcement
version: 1.0.0
text: >
  Are operational policies automatically enforced?
required: true
responseSpecification:
  type: single-choice

⸻

17. Question Must Not Own Maturity Level

Do not implement:

question:
  maturityLevel: L4

Instead:

Question
   ↓
Criterion
   ↓
MaturityLevel

This permits multiple questions to contribute evidence to the same maturity criterion.

⸻

18. Multiple Questions Per Criterion

Example:

Criterion:
Automated Policy Enforcement
Questions:
├── Q1 Policy definition
├── Q2 Policy coverage
├── Q3 Automated enforcement
├── Q4 Exception handling
└── Q5 Auditability

This gives the assessment model depth without changing the maturity model.

⸻

19. Question → Criterion Cardinality

Use:

Question "0..*" → "0..*" Criterion

because:

* one question may support multiple criteria;
* one criterion may require multiple questions.

If implementation experience shows that this is too permissive for governance, constrain it at the AssessmentInstrument binding rather than the global Question definition.

That preserves question reuse.

⸻

20. Response Specification

Questions must support different response types.

Initial controlled vocabulary:

boolean
single-choice
multi-choice
ordinal
numeric
percentage
duration
frequency
text
date
evidence
measurement

Example:

responseSpecification:
  type: percentage
  unit: percent
  min: 0
  max: 100

Another:

responseSpecification:
  type: single-choice
  options:
    - id: none
    - id: partial
    - id: substantial
    - id: complete

⸻

21. Response ≠ Observation

During an AssessmentExecution:

Question
    ↓
Response
    ↓
Observation

Example:

Question:
Are operational policies automatically enforced?
Response:
"Substantial"
Observation:
82% of applicable operational policies are automatically enforced.
Measure:
Policy Enforcement Automation
Value:
82%

The response records what the assessor/assessment mechanism received.

The Observation represents the assessed fact.

⸻

22. Evidence Requirement

A Question may require evidence.

Example:

evidence:
  required: true
  types:
    - system-record
    - policy-document
    - operational-metric

This should not force a single evidence model onto the assessment metamodel.

It should reference the canonical OpenDEA evidence/asset model where one exists.

⸻

23. Assessment Sections

An Instrument should support organization of questions:

AssessmentInstrument
│
├── Section
│   ├── Question
│   ├── Question
│   └── Question
│
├── Section
│   ├── Question
│   └── Question

A Section is organizational/presentation structure.

It must not become another semantic hierarchy competing with Dimension.

Therefore:

Dimension hierarchy
    = semantic assessment taxonomy
Instrument Section
    = questionnaire organization

⸻

24. Question Mapping

The Instrument should bind questions to the model:

AssessmentInstrument
      │
      ├── Question
      │      │
      │      ├── Dimension
      │      ├── Capability
      │      ├── Criterion
      │      └── Measure
      │
      └── ...

This is preferable to putting all of those relationships directly into the global Question definition.

It means the same Question can be used differently in different instruments.

⸻

25. Recommended Binding Concept

I recommend introducing:

AssessmentItem

as the instrument-specific binding.

AssessmentInstrument
        │
        ▼
AssessmentItem
        │
        ├── Question
        ├── Dimension
        ├── Capability
        ├── Criterion
        ├── Measure
        ├── sequence
        ├── required
        └── applicability

This is a significant improvement over putting contextual properties directly on Question.

⸻

26. Resulting Question Architecture

Question
   │
   │ reusable definition
   ▼
AssessmentItem
   │
   ├── Dimension
   ├── Capability
   ├── Criterion
   ├── Measure
   └── ResponseSpecification
         │
         ▼
AssessmentInstrument
         │
         ▼
AssessmentExecution
         │
         ▼
AssessmentResult

This gives us the extensibility we want.

⸻

27. Maturity Model Relationship

The maturity model remains authoritative for maturity semantics.

Conceptually:

MaturityModel
│
├── MaturityScale
│   ├── Level 1
│   ├── Level 2
│   ├── Level 3
│   ├── Level 4
│   └── Level 5
│
├── Dimension
│   ├── Dimension
│   │   └── Dimension
│   │
│   └── Criterion
│
└── ...

The exact repository implementation should reuse existing canonical maturity constructs wherever already established rather than duplicating them.

⸻

28. Maturity Scale

A Dimension should be able to reference a MaturityScale.

Example:

Automation
  → AOMM Scale 1–5
Data Quality
  → DQM Scale 0–4

Do not assume all Dimensions universally share the same scale.

However, the default should remain the parent model’s canonical scale unless explicitly overridden.

⸻

29. Incremental Question Evolution

This is a mandatory acceptance scenario.

Instrument v1.0

Q1
Q2
Q3
Q4
Q5

Instrument v1.1

Q1
Q2
Q3
Q4
Q5
Q6
Q7
Q8

The maturity model remains:

AOMM v1.0

Historical result:

AssessmentInstrument v1.0
MaturityModel v1.0

New result:

AssessmentInstrument v1.1
MaturityModel v1.0

Both remain independently interpretable.

⸻

30. Question Retirement

Questions must support lifecycle state:

draft
active
deprecated
retired

Retiring a Question must not invalidate historical AssessmentResults.

Historical results retain their original Question version.

⸻

31. Question Replacement

If:

Q1 v1.0

is replaced by:

Q1 v2.0

the model should explicitly permit:

supersedes:
  id: dea:q-policy-enforcement
  version: 1.0.0

This creates lineage without destroying the old definition.

⸻

32. Assessment Instrument Versioning

The Instrument itself must also be versioned.

AOM Assessment Instrument
├── v1.0
├── v1.1
├── v1.2
└── v2.0

The semantic meaning of the version must follow the repository’s existing versioning/compatibility governance.

Adding a non-semantic question may be a minor revision.

Changing scoring interpretation or required evidence may require a major/minor change depending on the established compatibility rules.

⸻

33. Historical Result Requirement

Every AssessmentResult generated through an Instrument must preserve:

assessmentInstrument.id
assessmentInstrument.version

and the effective versions of the relevant assessment items/questions.

This is non-negotiable.

Otherwise:

"Why did Organization A receive Level 3?"

cannot be answered reproducibly six months later after the questionnaire has changed.

⸻

34. Assessment Path

The result should be capable of preserving the semantic path:

Dimension
 → Sub-Dimension
 → Sub-Dimension
 → Capability
 → Criterion
 → Indicator
 → Question
 → Observation
 → Measure
 → Score
 → Maturity

This enables the enterprise view to aggregate at any appropriate level.

For example:

Enterprise
└── Automation
    └── Closed Loop Automation
        └── Decision Automation

can be rendered as an enterprise heatmap without losing the detailed assessment lineage.

⸻

35. Proposed UML

The implementation should extend the existing canonical model along these lines:

@startuml
class MaturityModel
class MaturityScale
class MaturityLevel
class AssessmentModel
class AssessmentInstrument
class AssessmentSection
class AssessmentItem
class Question
class ResponseSpecification
class Dimension
class Capability
class Criterion
class Indicator
class Measure
class AssessmentExecution
class Observation
class AssessmentResult
MaturityModel "1" o-- "1..*" MaturityScale
MaturityScale "1" o-- "1..*" MaturityLevel
MaturityModel "1" o-- "1..*" Dimension
Dimension "0..1" <-- "0..*" Dimension : parentDimension
Dimension "0..*" --> "0..*" Capability : assesses
Dimension "1" o-- "0..*" Criterion
Criterion "1" o-- "0..*" Indicator
Dimension "0..1" --> "0..1" MaturityScale
AssessmentModel "1" --> "0..*" AssessmentInstrument
AssessmentInstrument "1" o-- "0..*" AssessmentSection
AssessmentSection "1" o-- "0..*" AssessmentItem
AssessmentItem "*" --> "1" Question
AssessmentItem "*" --> "0..*" Dimension
AssessmentItem "*" --> "0..*" Capability
AssessmentItem "*" --> "0..*" Criterion
AssessmentItem "*" --> "0..*" Measure
Question "1" o-- "1" ResponseSpecification
AssessmentInstrument "1" --> "1" AssessmentModel
AssessmentExecution "1" --> "1" AssessmentInstrument
AssessmentExecution "1" --> "0..*" Observation
Observation "*" --> "1" AssessmentItem
Observation "*" --> "0..*" Measure
AssessmentExecution "1" --> "1" AssessmentResult
@enduml

This is the target logical model, not an instruction to blindly duplicate every class if equivalent canonical constructs already exist in the repository.

⸻

36. Repository Implementation

At technehub-labs/dea-metamodel, first inspect the existing canonical definitions and extend rather than duplicate.

Expected areas:

assessment-models/
├── model/
│   └── assessment-metamodel.puml
│
├── schemas/
│   ├── assessment-model.schema.json
│   ├── assessment-result.schema.json
│   ├── maturity-model.schema.json
│   └── ...
│
├── vocabulary/
│   └── ...
│
├── examples/
│   └── ...
│
├── governance/
│   └── ...
│
└── tests/

If the repository has already established equivalent canonical classes, reuse those names and definitions.

⸻

37. Required New/Modified Artifacts

At minimum:

Model

assessment-models/model/assessment-metamodel.puml

Add/extend:

Dimension
Criterion
Indicator
AssessmentInstrument
AssessmentSection
AssessmentItem
Question
ResponseSpecification

Schemas

Add or extend:

dimension.schema.json
assessment-instrument.schema.json
question.schema.json
assessment-item.schema.json
response-specification.schema.json
criterion.schema.json
indicator.schema.json

Only create separate schemas where the repository’s schema architecture warrants them.

Vocabulary

Add:

dimension-status
question-status
response-type

Examples

Create one complete example:

examples/hierarchical-maturity-assessment.yaml

showing at least:

3-level Dimension hierarchy
2 Capabilities
2 Criteria
5+ Questions
multiple response types
instrument version
maturity model reference
assessment result lineage

⸻

38. Required Conformance Tests

The implementation must test:

Hierarchy

Root Dimension
 └── Child Dimension
      └── Grandchild Dimension

Cycle rejection

A → B → A

must fail.

Question reuse

One Question referenced by two AssessmentItems.

Question evolution

Q1 v1 → Q1 v2.

Instrument evolution

Instrument v1.0 → v1.1 with additional questions.

Historical preservation

Old AssessmentResult continues validating after question retirement.

Multiple response types

Boolean, numeric, percentage, choice and evidence.

Criterion aggregation

Multiple questions contributing to one Criterion.

Dimension/capability independence

Same Capability referenced under different Dimension structures.

⸻

39. Acceptance Criteria

AC-AM05A-01 — Hierarchical Dimensions

The metamodel supports:

Dimension → Dimension → Dimension

without a SubDimension class.

AC-AM05A-02 — Arbitrary Depth

No fixed hierarchy depth is imposed by the metamodel.

AC-AM05A-03 — Cycle Prevention

Dimension hierarchy is acyclic.

AC-AM05A-04 — Capability Independence

Capability is not a subtype of Dimension and can be referenced independently.

AC-AM05A-05 — Criteria

Criteria provide the semantic bridge between evidence and maturity.

AC-AM05A-06 — Indicators

Indicators represent observable characteristics supporting Criteria.

AC-AM05A-07 — Instruments

Assessment Instruments are independently versioned.

AC-AM05A-08 — Questions

Questions are independently identifiable and versionable.

AC-AM05A-09 — Question Reuse

Questions can be reused across Assessment Instruments.

AC-AM05A-10 — Response Types

Questions support multiple response types.

AC-AM05A-11 — Question/Maturity Decoupling

Questions do not directly own MaturityLevels.

AC-AM05A-12 — Criterion Mapping

Multiple Questions may contribute to a Criterion.

AC-AM05A-13 — Historical Integrity

Historical AssessmentResults retain the versions of the Instrument and Questions used.

AC-AM05A-14 — Incremental Evolution

Adding questions does not require modifying the MaturityModel.

AC-AM05A-15 — Question Retirement

Retiring a Question does not invalidate historical Results.

AC-AM05A-16 — Semantic Lineage

Result lineage can traverse:

Dimension
→ Capability
→ Criterion
→ Question
→ Observation
→ Measure
→ Score
→ Maturity

AC-AM05A-17 — Existing Model Preservation

Existing canonical assessment models and results remain valid unless an explicit compatibility correction is required.

⸻

40. Non-Goals

The implementation must not:

* create SubDimension;
* create SubSubDimension;
* make Question inherit from Criterion;
* make Question inherit from MaturityLevel;
* make Capability inherit from Dimension;
* embed questionnaire presentation concerns in the MaturityModel;
* replace AssessmentResult;
* implement benchmark ranking;
* implement enterprise heatmap aggregation;
* hard-code a five-level maturity scale.

⸻

41. Definition of Done

CR-AM-05A is complete when OpenDEA can express this without custom extensions:

Maturity Model
│
└── Automation
    │
    └── Closed Loop Automation
        │
        └── Decision Automation
            │
            ├── Capability
            │
            └── Criterion
                 │
                 ├── Question 1
                 ├── Question 2
                 ├── Question 3
                 └── Question 4

and administer:

AssessmentInstrument v1.0
        ↓
AssessmentExecution
        ↓
Responses
        ↓
Observations
        ↓
Measures
        ↓
Criteria
        ↓
MaturityResult
        ↓
AssessmentResult

Then add:

Question 5
Question 6
Question 7

and produce:

AssessmentInstrument v1.1

without changing the underlying MaturityModel or invalidating v1.0 AssessmentResults.

⸻

42. The Strategic Outcome

This CR establishes the missing assessment-instrument layer in OpenDEA:

             SEMANTIC MODEL
                  │
             MaturityModel
                  │
          ┌───────┴────────┐
          ▼                ▼
   Dimension Tree      Capability
          │                │
          └───────┬────────┘
                  ▼
               Criterion
                  │
                  ▼
             Indicator
                  │
                  ▼
        ┌───────────────────┐
        │ Assessment        │
        │ Instrument        │
        └─────────┬─────────┘
                  │
              Questions
                  │
              Responses
                  │
             Observations
                  │
               Measures
                  │
                Scores
                  │
             Maturity
                  │
          AssessmentResult
                  │
          ┌───────┴────────┐
          ▼                ▼
    Enterprise View   Benchmark

The critical architectural payoff is that the maturity model describes what maturity means, while the assessment instrument describes how we gather enough evidence to determine it.

That is the mechanism that allows OpenDEA to continuously add, refine, retire and reorganize questions while preserving the canonical maturity semantics and historical assessment results.