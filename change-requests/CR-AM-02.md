CR-AM-02 — Implement OpenDEA Assessment Metamodel v1

Change Request ID: CR-AM-02
Title: Implement OpenDEA Assessment Metamodel v1
Parent: CR-AM-01 — OpenDEA Assessment Metamodel
Type: Architecture / Information Model / Schema
Priority: P0 — Foundation
Status: Proposed
Target Release: OpenDEA Assessment Metamodel v1.0.0
Scope: Phase 1 implementation of the accepted canonical metamodel

⸻

1. Executive Summary

CR-AM-01 establishes the canonical OpenDEA Assessment Metamodel and the target evolution of the Assessment Models ecosystem.

This CR implements that accepted architecture.

The objective is not to replace the existing assessment catalog. It is to introduce the canonical metamodel as a stable semantic foundation while preserving existing assessment instruments, maturity models, results and references through explicit compatibility and migration mechanisms.

The implementation shall establish:

* canonical metamodel definitions;
* normative JSON Schemas;
* UML representation;
* controlled relationship vocabulary;
* versioning and compatibility semantics;
* canonical examples;
* legacy-to-canonical mappings;
* a first migration of the existing Technology Assessment.

The implementation must demonstrate that an existing assessment can be represented using the new metamodel without changing its assessment semantics or invalidating its existing definition.

⸻

2. Parent CR

This CR implements the Phase-1 requirements of:

CR-AM-01 — OpenDEA Assessment Metamodel

CR-AM-01 remains the architectural authority.

Where this CR introduces implementation-level decisions, they shall conform to CR-AM-01. Where an ambiguity exists, CR-AM-01 shall be clarified before implementation rather than silently reinterpreted.

⸻

3. Problem Statement

The existing assessment repositories provide useful assessment instruments and maturity models, but the current implementation is instrument-centric.

The current conceptual pattern is:

Assessment Instrument
        │
        ├── Dimension
        │      └── Question
        │
        ├── Scoring
        │
        └── Maturity Target

This is sufficient to define and administer a questionnaire-based assessment.

It is insufficient to support the broader OpenDEA requirement for:

Enterprise Assessment
Capability Assessment
Scenario Assessment
Maturity Assessment
Benchmark Assessment

using a common information model.

In particular, the current implementation does not provide sufficient independent identity and versioning for:

* Capability;
* Scenario;
* Measure;
* Scoring Model;
* Assessment Execution;
* Assessment Result;
* Benchmark context;
* model lineage;
* compatibility.

Without these boundaries, future extensions risk coupling new assessment content to existing instruments and making historical results difficult to reproduce or compare.

⸻

4. Change Objective

Implement a canonical OpenDEA Assessment Metamodel that separates:

what is assessed, why it is assessed, how it is assessed, what is observed, how observations are interpreted, and what result is produced.

The implementation shall support incremental evolution through independently versioned model components.

The target relationship is:

Capability
     │
     │ assessed-in
     ▼
Scenario
     │
     │ contextualizes
     ▼
AssessmentModel
     │
     ├── uses ──────────────── Measure
     ├── uses ──────────────── ScoringModel
     ├── contains ──────────── AssessmentDimension
     └── specifies ─────────── EvidenceRequirement
                                  │
                                  ▼
                         AssessmentInstrument
                                  │
                                  ▼
                         AssessmentExecution
                                  │
                                  ▼
                          AssessmentResult
                             │       │
                             │       └── Findings
                             │
                             └── interpreted-by
                                      │
                                      ▼
                                MaturityModel

Benchmarking is deliberately enabled by the model but deferred as a full implementation capability.

⸻

5. Design Principles

The implementation shall follow these principles.

5.1 Preserve Existing Work

Existing assessment instruments and maturity models remain valid.

No existing assessment shall need to be destroyed or rewritten merely because the metamodel is introduced.

⸻

5.2 Semantic Separation

The following concepts shall remain distinct:

Capability
Scenario
AssessmentModel
AssessmentInstrument
AssessmentExecution
AssessmentResult
Measure
ScoringModel
MaturityModel
BenchmarkModel
AssessmentView

No implementation shortcut shall collapse these concepts merely because they currently have a one-to-one relationship.

⸻

5.3 Independent Evolution

Each normative model shall have an independently identifiable version.

For example:

AssessmentModel       1.2.0
Capability            1.1.0
Scenario              2.0.0
Measure               1.3.0
ScoringModel          1.0.0
MaturityModel         3.1.0

A result shall preserve the exact versions used.

⸻

5.4 Results Are Historical Records

An AssessmentResult represents a completed assessment and shall preserve the model references necessary to interpret the result historically.

Changing a subsequent model version must not silently alter a historical result.

⸻

5.5 Views Are Projections

An enterprise heatmap is a view over assessment results, not a fundamentally different assessment model.

Therefore:

AssessmentResult
       │
       ├── Enterprise View
       ├── Capability View
       ├── Scenario View
       ├── Maturity View
       └── Trend View

rather than creating a separate EnterpriseHeatmapAssessment.

⸻

6. Canonical Metamodel Scope

CR-AM-02 shall implement the following P0 entities.

Core assessment entities

AssessmentModel
AssessmentInstrument
AssessmentExecution
AssessmentResult
AssessmentDimension
AssessmentQuestion

Semantic entities

Capability
Scenario
Measure
Evidence

Interpretation entities

ScoringModel
MaturityModelReference

Governance entities

ModelReference
ModelVersion
Lineage
Compatibility

BenchmarkModel and AssessmentView shall be represented sufficiently in the metamodel to preserve the architecture defined by CR-AM-01, but their full operational implementations are deferred to later phases.

⸻

7. Entity Semantics

7.1 AssessmentModel

Definition

A normative specification defining what an assessment evaluates, the scope in which it applies, the assessment dimensions and measures involved, and the interpretation requirements for its results.

An AssessmentModel defines what the assessment means.

It does not represent an execution.

⸻

7.2 AssessmentInstrument

Definition

A concrete realization of an AssessmentModel used to administer an assessment.

Examples include:

* questionnaire;
* workshop;
* interview guide;
* automated assessment;
* evidence collection procedure.

Multiple instruments may implement the same AssessmentModel.

AssessmentModel
       │
       ├── Instrument A
       ├── Instrument B
       └── Instrument C

⸻

7.3 AssessmentExecution

Definition

A recorded occurrence in which an AssessmentInstrument is applied to an assessment subject within a defined context and period.

It is an event, not a model.

⸻

7.4 AssessmentResult

Definition

The persistent output of an AssessmentExecution, including observations, scores, interpretations, evidence references and model provenance.

The result must preserve references to the exact model versions used.

⸻

7.5 Capability

Definition

An independently identifiable organizational ability that may be assessed across one or more scenarios or assessment models.

A Capability is not an AssessmentDimension.

⸻

7.6 Scenario

Definition

A defined operational or business context in which a capability is exercised, evaluated or compared.

Scenario provides context for capability assessment and is particularly important for benchmarking.

⸻

7.7 Measure

Definition

A defined observable property, metric or indicator used to characterize an assessment subject.

A Measure must not inherently depend on a questionnaire.

A measure may be populated through:

Questionnaire
Interview
Workshop
System Data
Telemetry
Evidence
Automated Measurement

⸻

7.8 AssessmentQuestion

Definition

A prompt or elicitation mechanism used by an assessment instrument to obtain information relevant to one or more measures.

A question is therefore not itself the measure.

Example:

Question:
"How frequently is closed-loop remediation used?"
        ↓
Measure:
Closed Loop Automation Rate
        ↓
Observation:
82%

⸻

7.9 ScoringModel

Definition

A reusable model defining how observations or responses are transformed into scores.

The current four-point scale shall be representable as a ScoringModel.

⸻

7.10 MaturityModel

Definition

An independently versioned interpretation model that defines maturity levels, characteristics, thresholds and/or progression criteria.

An AssessmentModel may reference a MaturityModel.

A MaturityModel must not be embedded into the AssessmentModel.

⸻

8. Assessment Lifecycle

The canonical lifecycle shall be:

AssessmentModel
      │
      ▼
AssessmentInstrument
      │
      ▼
AssessmentExecution
      │
      ▼
Observations / Evidence
      │
      ▼
AssessmentResult
      │
      ├── Score
      ├── Findings
      ├── Maturity Interpretation
      └── Benchmark Eligibility

The following distinction is normative:

Concept	Represents
AssessmentModel	Definition
AssessmentInstrument	Administration mechanism
AssessmentExecution	Event
AssessmentResult	Determination

⸻

9. Canonical Versioning

All normative model artifacts shall use Semantic Versioning:

MAJOR.MINOR.PATCH

PATCH

Non-semantic correction.

1.0.0 → 1.0.1

⸻

MINOR

Backward-compatible extension.

1.0.0 → 1.1.0

Examples:

* optional property;
* additional evidence type;
* additional relationship;
* additional measure.

⸻

MAJOR

Semantically incompatible change.

1.0.0 → 2.0.0

Examples:

* changed score meaning;
* changed weighting semantics;
* changed capability definition;
* changed maturity interpretation;
* changed benchmark comparability;
* removed required information.

⸻

10. Model Reference

Every cross-model dependency shall use a versioned reference.

Minimum structure:

model_reference:
  id: dea:assessment-technology
  version: 1.0.0

Do not permit unresolved references such as:

maturity_target: technology

in the canonical model.

The existing maturity_target mechanism shall remain supported only as a legacy compatibility construct.

⸻

11. Compatibility

The canonical model shall support explicit compatibility declarations.

Minimum dimensions:

compatibility:
  schema: compatible
  semantic: compatible
  scoring: compatible
  maturity: compatible
  result: compatible
  benchmark: incompatible

Not every model change needs to affect every compatibility dimension.

This allows, for example:

AssessmentModel 1.2
       ↓
AssessmentModel 1.3

to remain result-compatible while becoming benchmark-incompatible.

⸻

12. Lineage

The result shall retain model lineage.

Minimum result lineage:

lineage:
  assessment_model:
    id: ...
    version: ...
  assessment_instrument:
    id: ...
    version: ...
  capability:
    id: ...
    version: ...
  scenario:
    id: ...
    version: ...
  measures:
    - id: ...
      version: ...
  scoring_model:
    id: ...
    version: ...
  maturity_model:
    id: ...
    version: ...

This is required for reproducibility.

⸻

13. Benchmarking Boundary

CR-AM-02 shall establish the data structures required to support benchmark eligibility but shall not implement the full benchmark engine.

The architectural distinction shall be:

AssessmentResult
       │
       ▼
BenchmarkEligibility
       │
       ▼
BenchmarkResult

A score alone shall never imply benchmarkability.

Benchmark eligibility shall eventually consider:

AssessmentModel
Capability
Scenario
Measure
ScoringModel
Evidence
Population
Measurement Period

⸻

14. Enterprise Heatmap Boundary

The enterprise heatmap shall be implemented as a derived view.

AssessmentResult[]
        │
        ▼
Aggregation
        │
        ▼
EnterpriseAssessmentView
        │
        ▼
Heatmap

A heatmap cell should be traceable to:

AssessmentResult
AssessmentModel
Model Version
Measure
Measurement Period

The heatmap must therefore be explainable and reproducible.

⸻

15. Legacy Compatibility

The current instrument schema shall not be removed.

It shall be designated as:

Legacy Instrument Model v1

The existing:

schemas/instrument.schema.json

shall remain valid during the migration period.

The canonical model shall introduce a migration mapping:

Legacy Instrument
       │
       ▼
AssessmentModel

without requiring existing assessment repositories to immediately change their native representation.

⸻

16. Legacy Mapping

The minimum mapping shall be:

Current construct	Canonical construct
instrument.id	AssessmentModel.id
instrument.name	AssessmentModel.name
instrument.version	AssessmentModel.version
instrument.description	AssessmentModel.description
instrument.domain	Classification metadata
instrument.dimensions	AssessmentDimension[]
dimension.questions	AssessmentQuestion[]
question scoring	ScoringModel
question evidence	Evidence / EvidenceRequirement
maturity_target	Versioned MaturityModel reference
current relationships	Canonical relationship vocabulary

The mapping must preserve original meaning.

⸻

17. Technology Assessment Pilot

The existing Technology Assessment shall be the first migration candidate.

The migration shall demonstrate:

Existing Technology Instrument
              │
              ▼
      AssessmentModel
              │
        ┌─────┼─────┐
        ▼     ▼     ▼
   Dimensions Questions Measures
              │
              ▼
       ScoringModel
              │
              ▼
        MaturityModel

The existing five dimensions and 19 questions shall remain semantically equivalent.

The migration shall not redesign the Technology Assessment itself.

⸻

18. Repository Deliverables

Create:

dea-metamodel/

with:

dea-metamodel/
├── README.md
├── CHANGELOG.md
├── VERSION
│
├── model/
│   ├── assessment-metamodel.puml
│   └── assessment-metamodel.md
│
├── schemas/
│   ├── common.schema.json
│   ├── assessment-model.schema.json
│   ├── assessment-instrument.schema.json
│   ├── assessment-execution.schema.json
│   ├── assessment-result.schema.json
│   ├── assessment-dimension.schema.json
│   ├── assessment-question.schema.json
│   ├── capability.schema.json
│   ├── scenario.schema.json
│   ├── measure.schema.json
│   ├── evidence.schema.json
│   └── scoring-model.schema.json
│
├── vocabulary/
│   ├── relationship-types.yaml
│   ├── lifecycle-status.yaml
│   └── compatibility-types.yaml
│
├── examples/
│   ├── assessment-model.yaml
│   ├── assessment-instrument.yaml
│   ├── assessment-execution.yaml
│   └── assessment-result.yaml
│
├── migrations/
│   └── v1-instrument/
│       └── mapping.yaml
│
└── tests/
    ├── schemas/
    ├── examples/
    ├── migration/
    └── compatibility/

⸻

19. Changes to dea-catalog-assessment-tools

The catalog repository shall be extended, not replaced.

Add:

docs/
  metamodel-migration.md
migrations/
  v1-to-metamodel/
tests/
  metamodel/

Existing:

schemas/instrument.schema.json

shall remain available as the legacy schema.

Assessment definitions shall progressively gain canonical references.

⸻

20. Changes to Existing Assessment Repositories

Existing repositories such as:

dea-assessment-technology
dea-assessment-modernization
dea-assessment-operations
dea-assessment-services-delivery

shall remain operational.

Migration shall initially be additive.

For example:

metamodel:
  id: dea:assessment-model
  version: 1.0.0
model:
  id: dea:assessment-technology
  version: 1.0.0

Existing fields shall remain during the compatibility period.

⸻

21. Validation Requirements

CI shall validate:

Schema validity

Every canonical YAML/JSON example validates against its schema.

Reference integrity

Every referenced model ID/version exists.

Relationship integrity

All relationship types belong to the controlled vocabulary.

Version integrity

Referenced versions are syntactically valid SemVer.

Migration integrity

Legacy instruments can be transformed into canonical AssessmentModels.

Semantic equivalence

The migration must preserve:

* question count;
* dimension count;
* scoring scale;
* weights;
* maturity target;
* question semantics.

⸻

22. Acceptance Criteria

CR-AM-02 is complete only when all of the following are true.

AC-01 — Canonical Metamodel

The canonical UML model exists and represents the CR-AM-01 architecture.

AC-02 — Normative Schemas

All P0 entities have JSON Schemas.

AC-03 — Controlled Vocabulary

Relationships and compatibility states are formally defined.

AC-04 — Versioning

Every normative model has an independently identifiable version.

AC-05 — Legacy Preservation

All existing instruments remain valid under the legacy schema.

AC-06 — Canonical Representation

At least one existing assessment is represented as an AssessmentModel.

AC-07 — Technology Migration

The Technology Assessment is migrated without semantic change.

AC-08 — Capability Independence

A Capability can be referenced independently of an AssessmentModel.

AC-09 — Scenario Independence

A Scenario can be referenced independently of an AssessmentModel.

AC-10 — Measure Independence

A Measure can be reused across assessment models.

AC-11 — Scoring Independence

A ScoringModel can be referenced independently.

AC-12 — Maturity Independence

A MaturityModel can be referenced independently and versioned.

AC-13 — Execution Separation

Multiple executions can reference one AssessmentModel.

AC-14 — Result Lineage

Every result identifies the exact model versions used.

AC-15 — Historical Integrity

Changing a model version cannot mutate an existing result.

AC-16 — Heatmap Traceability

A derived enterprise heatmap can trace each value back to source results and model versions.

AC-17 — Compatibility

A backward-compatible model update does not invalidate existing results.

AC-18 — Benchmark Protection

A result cannot be treated as benchmarkable without satisfying explicit eligibility requirements.

AC-19 — Reproducibility

The same versioned assessment inputs produce the same result.

AC-20 — No Breaking Migration

No existing assessment repository is required to adopt the canonical model in a single breaking release.

⸻

23. Explicit Non-Goals

CR-AM-02 shall not:

* redesign existing assessment questions;
* redesign existing maturity levels;
* create a new maturity framework;
* implement statistical benchmarking;
* create a universal enterprise scoring algorithm;
* create capability catalogs for every domain;
* create scenario catalogs for every domain;
* implement a benchmark engine;
* replace the existing repositories;
* invalidate existing assessment results;
* make enterprise heatmaps inherently benchmarkable.

These belong to subsequent phases.

⸻

24. Subsequent CRs

CR-AM-02 establishes the foundation for:

CR-AM-03
Assessment Model Migration
CR-AM-04
Capability And Scenario Catalogs
CR-AM-05
Assessment Result And Evidence Framework
CR-AM-06
Benchmark Model And Eligibility
CR-AM-07
Assessment Views And Enterprise Heatmaps
CR-AM-08
Assessment Analytics And Benchmarking

The sequence is intentional.

Do not implement benchmarking before the canonical result and lineage model is stable.

⸻

25. Target Architecture After CR-AM-02

The resulting architecture should be:

                    ┌──────────────────────┐
                    │   Model Governance   │
                    │ Version • Lineage    │
                    │ Compatibility        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Assessment Model   │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
        Capability          Scenario           Measure
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Assessment Instrument│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Assessment Execution │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Assessment Result   │
                    └──────────┬───────────┘
                               │
               ┌───────────────┼────────────────┐
               ▼               ▼                ▼
           Score          Maturity           Findings
               │               │
               │               ▼
               │         Maturity Model
               │
               ▼
      Benchmark Eligibility
               │
               ▼
        Benchmark Model

with:

AssessmentResult
       │
       ▼
Assessment Views
       │
       ├── Enterprise Heatmap
       ├── Capability View
       ├── Scenario View
       ├── Maturity View
       └── Trend View

⸻

26. Decision Requested

Approve CR-AM-02 for implementation.

The architectural decision has already been made through CR-AM-01. This CR is deliberately narrower: it converts that architecture into the normative metamodel, schemas, vocabulary, compatibility mechanisms and first migration.

The key implementation principle is:

Add the canonical model alongside the existing catalog first; migrate by reference and mapping; only retire legacy constructs after equivalent canonical representations and result integrity have been demonstrated.

That gives OpenDEA the evolutionary path we originally wanted:

Existing Assessment Assets
          │
          │ preserved
          ▼
Canonical Assessment Metamodel
          │
          ├── Enterprise Assessment
          ├── Capability Assessment
          ├── Scenario Assessment
          ├── Maturity Assessment
          └── Benchmark Assessment

without forcing the existing assessment and maturity work to be torn down or re-created.