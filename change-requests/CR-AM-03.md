CR-AM-03 — Assessment Catalog Migration & Integration

Change Request ID: CR-AM-03
Title: Assessment Catalog Migration & Integration
Parent: CR-AM-02 — Implement OpenDEA Assessment Metamodel v1
Repository: technehub-labs/dea-metamodel
Type: Architecture / Information Model / Migration / Conformance
Priority: P0
Status: Proposed
Target: OpenDEA Assessment Model v1.x
Dependencies: CR-AM-01, CR-AM-02

⸻

1. Executive Summary

CR-AM-02 establishes the canonical OpenDEA Assessment Metamodel.

CR-AM-03 moves the implementation from metamodel availability to ecosystem adoption.

The objective is to migrate the existing OpenDEA assessment portfolio from the legacy instrument-centric representation into canonical AssessmentModel representations while:

* preserving existing assessment definitions;
* preserving scoring semantics;
* preserving maturity interpretation;
* retaining legacy compatibility;
* establishing reusable Capability, Scenario and Measure references;
* producing conformant AssessmentExecution and AssessmentResult examples;
* establishing assessment portfolio coverage;
* proving that the canonical model works across multiple assessment domains.

The change must be additive and non-destructive.

No existing assessment definition, maturity model or historical result may be invalidated by this CR.

⸻

2. Architectural Context

The OpenDEA assessment architecture now has the following progression:

CR-AM-01
Assessment Architecture
        │
        ▼
CR-AM-02
Canonical Assessment Metamodel
        │
        ▼
┌───────────────────────────────┐
│ CR-AM-03                     │
│ Assessment Catalog Migration │
│ & Integration               │
└───────────────┬───────────────┘
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
   Assessment Capability Scenario
      Models       Models   Models
       │
       ▼
 Assessment Execution
       │
       ▼
 Assessment Result
       │
       ├───────────────┐
       ▼               ▼
 Maturity          Enterprise
 Interpretation       View
       │
       ▼
 Benchmark Eligibility

CR-AM-03 therefore consumes the metamodel rather than extending its core semantics.

⸻

3. Problem Statement

CR-AM-02 has established the canonical information model and schemas.

However, a metamodel alone does not demonstrate that the existing Assessment Models ecosystem can operate using it.

The existing assessment portfolio contains assessment instruments whose semantics were historically expressed through:

Instrument
 ├── Domain
 ├── Dimensions
 ├── Questions
 ├── Scoring
 └── Maturity Target

The canonical architecture instead requires:

AssessmentModel
 ├── Capability
 ├── Scenario
 ├── Measures
 ├── AssessmentDimensions
 ├── AssessmentQuestions
 ├── ScoringModel
 └── MaturityModel References

The immediate architectural risk is therefore no longer the absence of a metamodel.

It is semantic divergence between the canonical metamodel and the assessment content using it.

CR-AM-03 addresses that risk.

⸻

4. Change Objective

Establish a controlled migration and integration mechanism through which existing assessment instruments can be represented as canonical AssessmentModel instances and subsequently executed to produce canonical AssessmentResult instances.

The implementation shall demonstrate:

1. legacy preservation;
2. canonical representation;
3. semantic equivalence;
4. reusable references;
5. versioned lineage;
6. result conformance;
7. maturity interpretation;
8. enterprise aggregation readiness;
9. benchmark eligibility readiness.

⸻

5. Scope

5.1 In Scope

The first migration wave shall cover the existing assessment portfolio:

Technology
Modernization
Operations
Services Delivery

For each assessment, the implementation shall provide:

Legacy Definition
      │
      ▼
Migration Mapping
      │
      ▼
Canonical AssessmentModel
      │
      ▼
Canonical AssessmentExecution
      │
      ▼
Canonical AssessmentResult

⸻

5.2 Out of Scope

CR-AM-03 shall not:

* redesign assessment questions;
* redefine existing maturity levels;
* create a universal enterprise maturity score;
* implement statistical benchmarking;
* implement benchmark normalization;
* create a benchmark engine;
* replace legacy assessment repositories;
* delete legacy assessment definitions;
* introduce new core metamodel entities;
* make every assessment automatically benchmarkable.

⸻

6. Normative Principles

6.1 Additive Migration

Migration must follow:

Existing
   +
Canonical
   +
Mapping

not:

Existing
   →
Replace

⸻

6.2 Semantic Preservation

Migration must preserve the meaning of an existing assessment.

A migration is not considered successful merely because its YAML validates against the canonical schema.

It must demonstrate semantic equivalence.

⸻

6.3 Explicit Mapping

Every transformation from legacy to canonical representation shall be documented.

Implicit mappings are prohibited for normative migration.

⸻

6.4 Versioned References

All canonical references shall identify the exact model version.

For example:

capability:
  id: dea:capability-technology-architecture
  version: 1.0.0

Unversioned semantic references shall not be used in canonical AssessmentResults.

⸻

7. Assessment Portfolio

Create an assessment portfolio index.

Recommended location:

assessment-models/catalog/
    assessment-portfolio.yaml

The portfolio shall identify, at minimum:

assessment:
  id:
  name:
  version:
  lifecycle_status:
  domain:
  capabilities:
  scenarios:
  measures:
  scoring_model:
  maturity_models:
  legacy_source:
  canonical_source:
  migration_status:

The portfolio becomes the authoritative discovery point for assessment models.

⸻

8. Migration Contract

Every migrated assessment shall contain a migration contract.

Recommended structure:

assessment-models/migrations/
    <assessment-id>/
        mapping.yaml
        migration-manifest.yaml
        conformance-report.yaml

Minimum migration metadata:

migration:
  source:
    type: legacy-instrument
    id:
    version:
  target:
    type: assessment-model
    id:
    version:
  migration_version:
  semantic_equivalence:
    status:
    assessed_by:
    assessed_at:
  compatibility:
    schema:
    semantic:
    scoring:
    maturity:
    result:
    benchmark:

⸻

9. Canonical AssessmentModel Requirements

Each migrated AssessmentModel shall contain:

Identity
Description
Purpose
Scope
Capabilities
Scenarios
Measures
AssessmentDimensions
AssessmentQuestions
ScoringModel
MaturityModel References
Evidence Requirements
Lifecycle
Version
Lineage
Compatibility

Not every field must be populated where the source assessment genuinely has no equivalent.

However, absent information must be explicitly distinguishable from omitted information.

⸻

10. AssessmentDimension Semantics

CR-AM-03 formally establishes:

AssessmentDimension and Capability are distinct concepts.

AssessmentDimension

Represents the decomposition of an assessment.

Capability

Represents an independently governed organizational ability.

Therefore:

AssessmentDimension
       ≠
Capability

A dimension may assess one or more capabilities.

A capability may appear in multiple assessment models.

Example:

Capability:
Technology Architecture
AssessmentModel A:
  Dimension = Architecture
AssessmentModel B:
  Dimension = Platform Architecture
AssessmentModel C:
  Dimension = Architecture Governance

This distinction must be preserved during migration.

⸻

11. Scenario Mapping

A Scenario shall represent assessment context.

Where an existing assessment does not explicitly define a scenario, the migration shall:

1. determine whether a valid scenario can be inferred;
2. otherwise leave Scenario explicitly unbound;
3. never invent a scenario merely to satisfy schema requirements.

Scenario creation shall be governed independently from assessment creation.

⸻

12. Measure Mapping

Measures shall be extracted from existing assessment semantics where possible.

A question shall not automatically become a Measure.

The intended pattern is:

AssessmentQuestion
       │
       ▼
Observation
       │
       ▼
Measure

For example:

Question:
"How frequently is automation used?"
Measure:
Automation Adoption Rate
Observation:
72%

Measures should be reusable across assessment models.

⸻

13. Scoring Model Mapping

Existing scoring must be externalized.

For the existing four-point instruments:

0
1
2
3

the canonical representation shall reference:

scoring_model:
  id: dea:scoring-four-point
  version: 1.0.0

The migration shall demonstrate numerical equivalence between legacy and canonical scoring.

No scoring redesign is permitted under this CR.

⸻

14. Maturity Model Mapping

Existing maturity targets shall be converted from implicit references to explicit versioned references.

Legacy:

maturity_target: technology

Canonical:

maturity_models:
  - id: dea:maturity-technology
    version: 1.0.0

The existing maturity model remains independently governed.

The migration shall not alter its level definitions.

⸻

15. Assessment Execution

At least one valid AssessmentExecution shall be created for each migrated AssessmentModel.

The execution shall identify:

AssessmentModel
AssessmentInstrument
Subject
Assessment Period
Scenario
Assessors / Source
Evidence
Execution Status

Example:

assessment_execution:
  id: dea:execution-technology-001
  assessment_model:
    id: dea:assessment-technology
    version: 1.0.0
  assessment_instrument:
    id: dea:instrument-technology
    version: 1.0.0
  scenario:
    id: dea:scenario-enterprise
    version: 1.0.0
  period:
    start:
    end:

⸻

16. Assessment Result

Each migrated assessment shall demonstrate production of a canonical AssessmentResult.

Minimum result content:

Result Identity
Assessment Execution
Assessment Model Reference
Observations
Scores
Findings
Maturity Interpretation
Evidence
Lineage
Compatibility

The result must be independently valid after the AssessmentExecution has completed.

⸻

17. Result Lineage

Every result shall preserve the exact versions of its dependencies.

Minimum:

lineage:
  assessment_model:
    id:
    version:
  assessment_instrument:
    id:
    version:
  capability:
    id:
    version:
  scenario:
    id:
    version:
  measures:
    - id:
      version:
  scoring_model:
    id:
    version:
  maturity_model:
    id:
    version:

A result must not depend on a floating or latest model version.

⸻

18. Semantic Equivalence

For each migrated assessment, the implementation shall establish:

Legacy Result
      │
      │ same source responses
      ▼
Canonical Result

and demonstrate:

Question Count        = equivalent
Dimension Count       = equivalent
Scoring Scale         = equivalent
Weights               = equivalent
Score Calculation     = equivalent
Maturity Interpretation = equivalent
Evidence Semantics    = equivalent

Where equivalence cannot be established, the migration shall explicitly identify the difference.

⸻

19. Migration Conformance Levels

Each assessment migration shall receive one of:

CONFORMANT
CONFORMANT-WITH-NOTES
NON-CONFORMANT

CONFORMANT

Full semantic equivalence established.

CONFORMANT-WITH-NOTES

Canonical representation is valid but one or more source semantics require documented qualification.

NON-CONFORMANT

The canonical representation changes the meaning of the original assessment or cannot be validated.

⸻

20. Assessment Coverage Matrix

The implementation shall generate a coverage matrix.

Minimum dimensions:

Assessment
Capability
Scenario
Measure
Maturity Model
Scoring Model
Evidence
Benchmark Eligibility

Example:

Assessment	Capability	Scenario	Measure	Maturity	Benchmark
Technology	Technology Architecture	Enterprise	Architecture Standardization	Technology	TBD
Technology	Technology Lifecycle	Enterprise	Lifecycle Compliance	Technology	TBD
Operations	Operations Automation	Service Assurance	Automation Rate	Operations	Potential
Modernization	Modernization Capability	Enterprise	Modernization Progress	Modernization	TBD

The matrix is a discovery and governance artifact, not itself an assessment.

⸻

21. Assessment Analytical Levels

CR-AM-03 shall establish three distinct analytical perspectives.

Enterprise Health

Enterprise
  ↓
Multiple Assessment Results
  ↓
Aggregation
  ↓
Enterprise View

Purpose:

diagnosis.

⸻

Capability Performance

Organization
  ↓
Capability
  ↓
Assessment Result

Purpose:

capability management.

⸻

Scenario Performance

Organization
  ↓
Scenario
  ↓
Capability
  ↓
Measure
  ↓
Assessment Result

Purpose:

controlled comparison and future benchmarking.

These perspectives must not be conflated.

⸻

22. Benchmark Eligibility

CR-AM-03 shall validate that AssessmentResults can carry benchmark eligibility information.

However:

Eligibility is not benchmarking.

The result may state:

benchmark_eligibility:
  status: eligible

but CR-AM-03 shall not calculate peer ranking or benchmark position.

Eligibility shall be evaluated against:

AssessmentModel
Capability
Scenario
Measure
ScoringModel
Evidence
Population
Measurement Period

Full BenchmarkModel implementation remains a subsequent CR.

⸻

23. Enterprise Heatmap Readiness

CR-AM-03 shall prove that canonical results contain sufficient information to derive an enterprise heatmap.

Each aggregate must be traceable to:

AssessmentResult
AssessmentModel
AssessmentModel Version
Capability
Measure
Measurement Period

The implementation shall not create a new EnterpriseHeatmapAssessment.

The heatmap remains a projection.

⸻

24. Repository Structure

The following additions are recommended:

assessment-models/
├── catalog/
│   ├── assessment-portfolio.yaml
│   └── assessment-coverage.yaml
│
├── migrations/
│   ├── technology/
│   │   ├── mapping.yaml
│   │   ├── migration-manifest.yaml
│   │   └── conformance-report.yaml
│   │
│   ├── modernization/
│   │   ├── mapping.yaml
│   │   ├── migration-manifest.yaml
│   │   └── conformance-report.yaml
│   │
│   ├── operations/
│   │   ├── mapping.yaml
│   │   ├── migration-manifest.yaml
│   │   └── conformance-report.yaml
│   │
│   └── services-delivery/
│       ├── mapping.yaml
│       ├── migration-manifest.yaml
│       └── conformance-report.yaml
│
├── examples/
│   ├── technology-result.yaml
│   ├── modernization-result.yaml
│   ├── operations-result.yaml
│   └── services-delivery-result.yaml
│
└── tests/
    ├── migration/
    ├── semantic-equivalence/
    ├── result-conformance/
    └── portfolio/

Existing CR-AM-02 artifacts remain unchanged unless required for compatibility corrections.

⸻

25. Schema Identity Correction

CR-AM-03 shall resolve the canonical schema namespace.

The current implementation contains schema $id references associated with the previous repository namespace.

These must be aligned with the canonical repository:

github.com/technehub-labs/dea-metamodel

or, preferably, an explicitly governed OpenDEA namespace if one has been established.

The chosen namespace must be:

* stable;
* documented;
* independent of repository relocation where possible;
* used consistently across $id, $ref, documentation and examples.

This is a P0 integration requirement because external consumers may otherwise establish incompatible references.

⸻

26. Compatibility Documentation Correction

The compatibility documentation shall be synchronized with the canonical schema.

The implementation currently defines six compatibility axes:

schema
semantic
scoring
maturity
result
benchmark

The documentation shall use the same six-axis terminology.

The schema is authoritative.

⸻

27. CR Registry Update

Upon successful acceptance of CR-AM-02:

CR-AM-02
Status: Implemented

CR-AM-03 shall then be registered as:

CR-AM-03
Title: Assessment Catalog Migration & Integration
Status: Proposed
Parent: CR-AM-02

The registry shall explicitly identify dependencies between CRs.

⸻

28. Testing

CI shall implement the following test groups.

Migration Tests

Verify all four assessment migrations.

Schema Tests

Validate every canonical AssessmentModel, Execution and Result.

Reference Tests

Verify every referenced Capability, Scenario, Measure, ScoringModel and MaturityModel resolves.

Semantic Tests

Compare legacy and canonical scoring outputs.

Lineage Tests

Verify all result dependencies contain exact versions.

Compatibility Tests

Verify compatibility declarations are valid against the compatibility schema.

Portfolio Tests

Verify all assessment models are discoverable from the portfolio index.

⸻

29. Acceptance Criteria

CR-AM-03 shall not be marked Implemented until all P0 criteria pass.

AC-AM03-01 — Four Assessments Migrated

Technology, Modernization, Operations and Services Delivery each have canonical AssessmentModels.

AC-AM03-02 — Legacy Preservation

All source instruments remain valid and unchanged.

AC-AM03-03 — Explicit Migration

Every migration has an auditable mapping.

AC-AM03-04 — Semantic Equivalence

All four migrations demonstrate preservation of existing scoring semantics.

AC-AM03-05 — Capability Mapping

Every assessment identifies applicable Capability references where such capabilities are established.

AC-AM03-06 — Dimension Separation

AssessmentDimensions remain distinct from Capabilities.

AC-AM03-07 — Measure Mapping

Measures are represented independently from Questions.

AC-AM03-08 — Scenario Handling

Scenario references are explicit where applicable, and absent scenarios are not fabricated.

AC-AM03-09 — Scoring Model

All migrated scoring mechanisms reference canonical ScoringModels.

AC-AM03-10 — Maturity Decoupling

All migrated maturity relationships use explicit versioned MaturityModel references.

AC-AM03-11 — Execution

Every migrated AssessmentModel has at least one conformant AssessmentExecution example.

AC-AM03-12 — Result

Every migrated AssessmentModel has at least one conformant AssessmentResult example.

AC-AM03-13 — Lineage

Every AssessmentResult contains complete versioned lineage.

AC-AM03-14 — Compatibility

Every result contains the six compatibility dimensions.

AC-AM03-15 — Portfolio

All migrated AssessmentModels are discoverable through the Assessment Portfolio.

AC-AM03-16 — Coverage

An Assessment Coverage Matrix can be generated from canonical references.

AC-AM03-17 — Enterprise View Readiness

AssessmentResults contain sufficient provenance to derive an enterprise assessment view.

AC-AM03-18 — Benchmark Eligibility

Benchmark eligibility can be represented without requiring benchmark calculation.

AC-AM03-19 — Schema Namespace

All canonical schema identifiers and references use the approved namespace consistently.

AC-AM03-20 — CI

All migration, schema, reference, semantic and lineage tests pass.

⸻

30. Non-Functional Acceptance

The implementation must also demonstrate:

Reproducibility

The same versioned inputs produce the same result.

Traceability

Every result can be traced to its originating AssessmentModel and execution.

Evolvability

A new AssessmentModel version can coexist with an earlier version.

Non-Destructiveness

Existing legacy assessments remain operational.

Interoperability

Canonical artifacts can be consumed without requiring knowledge of legacy instrument structures.

⸻

31. Migration Success Test

The definitive test for CR-AM-03 is:

                LEGACY
                  │
                  ▼
          Technology v1
                  │
                  ▼
            Migration
                  │
                  ▼
        Canonical Model v1
                  │
                  ▼
             Execution
                  │
                  ▼
              Result
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
    Capability  Maturity  Enterprise
      View       View       View

and the same process must work for:

Technology
Modernization
Operations
Services Delivery

without requiring the canonical metamodel to be modified for each assessment.

That last condition is particularly important.

If migrating the four assessments requires adding assessment-specific concepts to the core metamodel, CR-AM-02 has not achieved the desired abstraction.

⸻

32. Definition of Done

CR-AM-03 is Implemented when:

                 Canonical Metamodel
                         │
                         ▼
                 Assessment Portfolio
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Technology     Operations     Modernization
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 Canonical Results
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Capability  Maturity   Enterprise
             View       View       View
                         │
                         ▼
                Benchmark Eligibility

is demonstrably operational through validated repository artifacts and CI.

⸻

33. Next CR After CR-AM-03

Once this CR is complete, the next architectural increment should be:

CR-AM-04 — Assessment Result Operations

Its purpose would be to move from example results to a governed result lifecycle:

AssessmentPlan
      ↓
AssessmentExecution
      ↓
Observation
      ↓
AssessmentResult
      ↓
Finding
      ↓
Maturity Interpretation
      ↓
Assessment View

Only after that should we make the larger leap into:

CR-AM-05
Enterprise Assessment Views
        ↓
CR-AM-06
Benchmark Model & Eligibility
        ↓
CR-AM-07
Comparative Benchmarking

This sequencing keeps the core principle intact:

First make assessment definitions interoperable; then make assessment results operational; then aggregate them; only then compare organizations.

That gives the OpenDEA assessment ecosystem an evolutionary path from the existing instruments to enterprise heatmaps, capability assessments, maturity models and eventually controlled organization-to-organization benchmarking—without requiring the existing assessment estate to be torn down.