CR-AM-11 — Federated Assessment Model Ecosystem

Status: Proposed
Type: Architecture, Repository Governance & Integration Change
Priority: P0 — Foundational
Scope: Assessment-Models and technehub-labs OpenDEA ecosystem
Umbrella: CR-AM-01 (Assessment Metamodel Evolution)
Depends on: Existing canonical OpenDEA Assessment Metamodel; CR-AM-09 (Maturity
  Scale, Progression & Conformance Architecture); CR-AM-10 (Maturity Component
  Composition & Reuse — proposal + Phase 1 landed, PR #143/#144)
Siblings: CR-AM-09 (implemented), CR-AM-10 (in flight — its component machinery
  gains its ecosystem home here in sections 18-20 and Phase 5)
Supersedes: the standalone-org dual-authority attempt retired by CR-014 (this CR
  revives the Assessment-Models organization in an ECOSYSTEM role only; it does
  NOT re-attempt dual-authority over the metamodel — see section 7)
Enables: Independent maturity model repositories, component reuse, cross-model interoperability and ecosystem CI

⸻

1. Change Request

Title

Federated Assessment Model Ecosystem

Objective

Re-establish the Assessment-Models organization⁠ as the canonical, independently managed ecosystem for OpenDEA-compatible:

* maturity models;
* assessment models;
* assessment tools;
* reusable assessment components; and
* model ecosystem integration.

At the same time, reposition technehub-labs/dea-metamodel⁠ as the canonical engineering authority for:

* the OpenDEA metamodel;
* assessment and maturity model semantics;
* schemas;
* conformance contracts;
* canonical vocabularies;
* validation specifications; and
* OpenDEA reference model instances.

The architecture shall enable both organizations to evolve independently while remaining interoperable through versioned, machine-readable contracts, registry references, compatibility declarations and automated CI validation.

⸻

2. Problem Statement

The current OpenDEA assessment and maturity-model assets have evolved incrementally.

Historically, the architecture has tended toward catalog repositories containing multiple models and a mixture of:

Architecture
Model Definitions
Scoring Conventions
Maturity Levels
Assessment Content
Documentation

This creates several problems.

2.1 Model lifecycle coupling

A centralized catalog means unrelated maturity models share:

Repository
Release lifecycle
Issues
Pull requests
Governance
CI

This inhibits independent evolution.

⸻

2.2 Architecture and instance coupling

The same repository structure can blur the distinction between:

Metamodel
        vs
Model Instance

The metamodel defines the language.

A maturity model is an instance using that language.

These must remain distinct.

⸻

2.3 Lack of a formal integration layer

Independent repositories alone do not solve:

Which models exist?
Which version is active?
Which metamodel version applies?
Which components are reused?
Are dependencies compatible?
Can two models interoperate?
Are mappings valid?

A formal integration architecture is required.

⸻

2.4 Cross-organization dependency ambiguity

Assessment-Models must be able to use OpenDEA canonical contracts without being structurally embedded inside technehub-labs.

Likewise:

technehub-labs must not become operationally dependent upon the lifecycle of every assessment model.

The dependency must therefore be contractual rather than repository-structural.

⸻

3. Target Architecture

The target architecture shall be:

                         OPENDEA ECOSYSTEM
                                │
                ┌───────────────┴────────────────┐
                │                                │
                ▼                                ▼
        TECHNEHUB-LABS                    ASSESSMENT-MODELS
                │                                │
                │                                │
        Engineering Authority             Ecosystem Authority
                │                                │
                ▼                                ▼
          dea-metamodel                  Assessment Registry
                │                                │
                │                                │
         Publishes Contracts          Registers Model Assets
                │                                │
                └──────────────┬─────────────────┘
                               │
                               ▼
                      Contract Integration
                               │
                               ▼
                         Ecosystem CI
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       Maturity Model A  Maturity Model B  Assessment Tool C

⸻

4. Architectural Principle

The following principle shall be adopted.

Centralize contracts, governance and integration; decentralize model ownership, lifecycle and evolution.

Therefore:

Decentralized

Maturity Model Content
Assessment Model Content
Maturity Scales
Scoring Logic
Model Releases
Issues
Roadmaps
Contributors

Centralized

Model Registration
Conformance Contracts
Compatibility Rules
Reference Resolution
Cross-Model Validation
Integration Testing
Ecosystem Governance

⸻

5. Organizational Responsibilities

5.1 technehub-labs

technehub-labs shall remain the canonical engineering organization for OpenDEA.

Primary responsibility:

Canonical Architecture
+
Metamodel
+
Contracts
+
Schemas
+
Reference Implementations

The principal repository is:

technehub-labs/dea-metamodel

It shall own:

dea-metamodel/
│
├── metamodel/
├── schemas/
├── vocabularies/
├── contracts/
├── validation/
├── assessment-models/
│
│   └── opendea-enterprise-architecture/
│
├── examples/
└── docs/

⸻

6. OpenDEA Assessment Model Instance

The existing:

dea-metamodel/assessment-models/

shall be explicitly positioned as containing OpenDEA-specific reference assessment model instances, rather than the catalog of all assessment or maturity models.

The primary target instance shall be:

OpenDEA Enterprise Architecture Assessment Model

Its purpose is to assess:

Use
Adoption
Implementation
Application
Maturity

of OpenDEA within an enterprise architecture context.

Conceptually:

DEA Metamodel
       │
       │ defines
       ▼
Assessment Metamodel
       │
       │ instantiated by
       ▼
OpenDEA Enterprise Architecture Assessment Model

⸻

7. Assessment-Models Organization

The Assessment-Models organization shall be revived as an active organization responsible for the OpenDEA-compatible assessment ecosystem.

Its role shall be:

Govern, publish, integrate and validate independently managed assessment and maturity model assets.

It shall not own the canonical OpenDEA metamodel.

Instead:

Assessment-Models
        │
        │ consumes
        ▼
Versioned OpenDEA Contracts
        │
        │ publishes
        ▼
Conformant Assessment Assets

⸻

8. Target Repository Taxonomy

The following repository classes shall be established.

Assessment-Models/
│
├── .github
│
├── assessment-registry
├── assessment-ci
├── maturity-components
│
├── maturity-model-*
│
├── assessment-model-*
│
└── assessment-tool-*

The architecture deliberately separates:

Registry
Integration
Reusable Components
Model Instances
Tools

⸻

9. Repository: .github

Create:

Assessment-Models/.github

This repository shall contain organization-level defaults.

Minimum scope:

.github/
├── README.md
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── SECURITY.md
│
├── ISSUE_TEMPLATE/
│
└── workflows/

It shall establish:

* organization purpose;
* contribution expectations;
* repository taxonomy;
* naming conventions;
* lifecycle conventions;
* baseline CI policies.

⸻

10. Repository: assessment-registry

Create:

Assessment-Models/assessment-registry

This repository is the ecosystem integration spine.

It shall not contain maturity model content.

It shall register assets.

⸻

10.1 Registry responsibilities

The registry shall answer:

What exists?
Where is it?
What version exists?
Which version is active?
Which contract does it conform to?
Which components does it depend on?
Which relationships exist?

⸻

10.2 Target structure

assessment-registry/
│
├── README.md
│
├── registry/
│
│   ├── maturity-models/
│   │
│   ├── assessment-models/
│   │
│   ├── assessment-tools/
│   │
│   └── components/
│
├── compatibility/
│
├── dependencies/
│
├── schemas/
│
├── examples/
│
└── tests/

⸻

11. Canonical Model Registration

Each maturity model shall have a registration record.

Example:

id: digital-transformation-maturity-model
type: maturity-model
name: Digital Transformation Maturity Model
source:
  organization: Assessment-Models
  repository: maturity-model-digital-transformation
release:
  version: 1.0.0
  reference: v1.0.0
conformsTo:
  contract:
    id: opendea-assessment-metamodel
    version: 1.x
status: active

The registry record shall contain metadata and references only.

It shall not duplicate:

Dimensions
Sub-dimensions
Criteria
Maturity Levels
Scoring Rules

Those remain owned by the model repository.

⸻

12. Immutable Version References

The registry shall never depend on:

main
master
latest

as a model reference.

Registry references must resolve to an immutable version identifier, such as:

Release
Tag
Commit SHA
Content Digest

Example:

release:
  version: 1.2.0
  tag: v1.2.0
  commit: 8a6c...

This is mandatory for reproducibility.

⸻

13. Repository: assessment-ci

Create:

Assessment-Models/assessment-ci

This repository shall contain cross-repository validation and ecosystem integration logic.

It shall not own assessment model content.

⸻

13.1 CI responsibility

The integration CI shall validate:

Registry integrity
Reference resolution
Contract compatibility
Version compatibility
Component dependencies
Cross-model mappings
Scale interoperability
Benchmark compatibility
Duplicate identifiers

⸻

14. Three-Level CI Model

The ecosystem shall implement three validation levels.

Level 1 — Local Model CI

Executed within each model repository.

Maturity Model
      │
      ▼
Local CI

Minimum checks:

Syntax
Schema Validation
Reference Integrity
Internal Consistency
Version Consistency
Documentation
Examples
Tests

⸻

Level 2 — Contract Conformance CI

Executed against the declared OpenDEA contract.

Model
  │
  ▼
Contract Declaration
  │
  ▼
DEA Metamodel Release
  │
  ▼
Conformance Validation

The model must declare a specific supported contract version.

⸻

Level 3 — Ecosystem CI

Executed through:

Assessment Registry
        │
        ▼
Assessment CI

It validates relationships across repositories.

        MM-A
          │
        MM-B
          │
        MM-C
          │
          ▼
     Registry
          │
          ▼
   Ecosystem CI

⸻

15. Contract Handshake

Every assessment ecosystem asset shall explicitly declare its metamodel contract dependency.

Example:

conformance:
  contract:
    id: opendea-assessment-metamodel
  source:
    organization: technehub-labs
    repository: dea-metamodel
  version: 1.0

The dependency shall be machine-readable.

The CI shall resolve and validate the declared version.

⸻

16. Contract Publication

The canonical contracts shall be published from:

technehub-labs/dea-metamodel

Initial contract families should include:

Assessment Contract
Maturity Model Contract
Maturity Scale Contract
Scoring Contract
Conformance Contract
Benchmark Contract

These may initially be implemented as a coordinated contract suite, but shall remain independently identifiable.

⸻

17. Compatibility

Introduce the concept:

Compatibility Declaration

A model shall be able to declare:

compatibility:
  metamodel:
    minimum: 1.0.0
    maximum: <2.0.0

or:

compatibility:
  contracts:
    - id: maturity-model-contract
      version: "^1.0"

The exact syntax shall be selected based on the existing schema conventions in dea-metamodel.

⸻

18. Repository: maturity-components

Create:

Assessment-Models/maturity-components

This repository shall contain reusable, independently versioned maturity-model components.

Examples:

maturity-components/
│
├── dimensions/
├── sub-dimensions/
├── capabilities/
├── criteria/
├── indicators/
├── evidence-requirements/
└── level-expectations/

The initial implementation may start with only the components required by the first participating models.

⸻

19. Component Reuse Principle

A reusable component shall be independently referenceable.

For example:

Digital Transformation MM
       │
       └── uses
             │
             ▼
       Digital Culture Component v1.2

Another model:

Agentic Enterprise MM
       │
       └── uses
             │
             ▼
       Digital Culture Component v1.2

This shall not require either model to inherit:

Maturity Scale
Scoring Model
Progression Model
Benchmark Rules

unless explicitly declared.

⸻

20. Component Reference Contract

A component reference shall identify:

Component ID
Component Type
Source Repository
Version
Immutable Reference

Conceptual example:

component:
  id: digital-culture
  type: sub-dimension
  source:
    repository: Assessment-Models/maturity-components
  version: 1.2.0
  reference: v1.2.0

⸻

21. Individual Maturity Model Repositories

Each maturity model shall reside in its own repository.

Naming:

maturity-model-<domain>

Examples:

maturity-model-digital-transformation
maturity-model-autonomous-operations
maturity-model-agentic-enterprise

Each repository shall be independently:

Versioned
Released
Tested
Documented
Governed

⸻

22. Standard Maturity Model Repository Structure

The precise structure shall conform to the OpenDEA contracts, but the initial target is:

maturity-model-<domain>/
│
├── README.md
│
├── model/
│
├── structure/
│
├── evaluation/
│
├── scale/
│
├── mappings/
│
├── components/
│
├── examples/
│
├── tests/
│
├── CHANGELOG.md
└── model.yaml

The root manifest shall declare:

Identity
Version
Contract Dependency
Components
Dependencies
Compatibility

⸻

23. No Git Submodules

The architecture shall not use Git submodules as the primary integration mechanism.

The following is prohibited as the ecosystem integration model:

registry/
├── model-a [submodule]
├── model-b [submodule]
└── model-c [submodule]

Integration shall use:

Repository References
+
Versioned Releases
+
Immutable References
+
Registry Resolution
+
Automated CI

⸻

24. OpenDEA Reference Assessment Instance

Within:

technehub-labs/dea-metamodel/assessment-models/

establish:

opendea-enterprise-architecture

This is a reference assessment model instance, not the ecosystem registry.

It shall demonstrate:

Maturity Structure
Maturity Scale
Evaluation Model
Scoring
Conformance
Benchmark Baseline

Its specific subject is:

Enterprise use, adoption and implementation of OpenDEA.

⸻

25. Separation of Canonical Layers

The architecture shall explicitly maintain:

LAYER 1 — METAMODEL
technehub-labs/dea-metamodel
Defines:
• concepts
• relationships
• schemas
• contracts
LAYER 2 — REFERENCE INSTANCE
technehub-labs/dea-metamodel/assessment-models
Contains:
• OpenDEA EA assessment model
LAYER 3 — ECOSYSTEM
Assessment-Models
Contains:
• independent maturity models
• assessment models
• tools
• reusable components
LAYER 4 — INTEGRATION
Assessment-Models/assessment-registry
Assessment-Models/assessment-ci
Manages:
• references
• compatibility
• integration
• ecosystem validation

⸻

26. Legacy Repository Strategy

Existing repositories shall not be destructively rewritten as the first implementation step.

They shall be classified:

Legacy
Candidate for Migration
Reference
Deprecated
Superseded

The initial architecture shall support coexistence.

Example:

dea-catalog-maturity-models
        │
        ▼
Legacy Catalog
        │
        ├── historical models preserved
        │
        └── selected models migrated individually

Migration shall occur only after the new architecture has been validated.

Superseded proposal closure: the open maturity-scoring-v2 proposal PR on
dea-catalog-maturity-models (docs/maturity-scoring-v2-proposal) is superseded by
the canonical CR-AM-09 scale machinery already landed in dea-metamodel. It shall
be closed with a pointer to the canonical scale contract as part of Phase 0
housekeeping (the repository is currently unarchived; if it is re-archived, the
closure must happen before archiving, since archived repos are read-only).

⸻

27. Migration Strategy

Migration shall follow:

IDENTIFY
   │
   ▼
CLASSIFY
   │
   ▼
EXTRACT
   │
   ▼
NORMALIZE
   │
   ▼
VALIDATE
   │
   ▼
REGISTER
   │
   ▼
RELEASE

No migration shall require rewriting unrelated models.

⸻

28. Documentation Architecture

Documentation shall exist at three levels.

Level 1 — Canonical Architecture

Located in:

technehub-labs/dea-metamodel/docs/

Covers:

Metamodel
Assessment Architecture
Maturity Architecture
Scale Architecture
Scoring
Conformance
Benchmarking
Versioning

⸻

Level 2 — Ecosystem Architecture

Located in:

Assessment-Models/assessment-registry

Covers:

Registry
Repository Taxonomy
Asset Lifecycle
Dependencies
Integration
Compatibility

⸻

Level 3 — Model Documentation

Located within each individual maturity or assessment model repository.

Covers:

Purpose
Scope
Structure
Scale
Levels
Progression
Evaluation
Scoring
Conformance
Version History

⸻

29. Organization-Level README

The revived Assessment-Models organization shall provide a clear architectural landing page.

It shall explain:

What Assessment-Models is
What assets it contains
Relationship to OpenDEA
Relationship to technehub-labs
How to find models
How models conform
How integration works
How to contribute

It shall not redefine the OpenDEA metamodel.

Instead, it shall reference the canonical metamodel contract.

⸻

30. Initial Implementation Sequence

Implementation shall proceed in the following order.

Phase 0 — Organizational Re-establishment

Deliver:

Assessment-Models Organization Profile
Organization README
.github Repository
Governance
Repository Taxonomy
Naming Conventions
Initial Legacy Classification Table (per section 26): all six existing org
  repositories (dea-catalog-maturity-models, dea-catalog-assessment-tools,
  dea-assessment-modernization, dea-assessment-technology,
  dea-assessment-operations, dea-assessment-services-delivery) classified as
  Legacy / Candidate for Migration / Reference / Deprecated / Superseded —
  classification ONLY, no content moves

Exit Criteria

The organization has an explicit identity and repository governance model.
Every pre-existing org repository carries an explicit section-26 classification.

⸻

Phase 1 — Integration Spine

Create:

assessment-registry
assessment-ci

Implement:

Asset Registration
Reference Resolution
Basic Contract Validation

Prerequisite:

An organization-level PAT (or GitHub App credential) stored as an org secret for
cross-repository repository_dispatch. GITHUB_TOKEN cannot dispatch across repos.
Until this secret exists, every fan-out / ecosystem-trigger workflow shall be
workflow_dispatch-only (manual trigger) so that main never goes red on push.

Exit Criteria

A repository can be registered and resolved through the registry.

⸻

Phase 2 — Contract Handshake

Publish the required canonical assessment and maturity contracts from:

technehub-labs/dea-metamodel

Implement:

Contract Identity
Contract Version
Compatibility Declaration
Conformance Validation

Contract Extraction & Subtree Reduction (structural pre-step within this phase):

The current dea-metamodel/assessment-models/ sub-tree holds BOTH the contract
machinery (schemas/, vocabulary/, governance/, maturity/ scale machinery,
tests/, tools/) AND model content. Per section 5, the contracts are identified,
inventoried (see Annex A) and published from dea-metamodel at their canonical
locations; assessment-models/ is reduced toward containing only the
opendea-enterprise-architecture reference instance (section 24). Each extraction
lands as its own PR with dea-metamodel main green throughout; the sub-tree
README authority clause is amended in the same PR that completes the reduction.

Exit Criteria

An external repository can declare and validate conformance to a specific OpenDEA contract.
Every contract family in Annex A is published from a declared canonical location
in dea-metamodel, and assessment-models/ contains no contract machinery that
duplicates those locations.

⸻

Phase 3 — Reference Implementation

Formalize:

dea-metamodel/assessment-models/opendea-enterprise-architecture

Exit Criteria

The metamodel has a real assessment model instance demonstrating the architecture.

⸻

Phase 4 — First Independent Model

Create one maturity model repository in Assessment-Models.

Recommended initial candidate:

maturity-model-digital-transformation

Validate:

Independent Lifecycle
+
Versioned Contract
+
Registry Registration
+
Local CI
+
Contract CI
+
Ecosystem CI

Exit Criteria

One complete external model successfully operates through the federated architecture.

⸻

Phase 5 — Reusable Components

Introduce:

maturity-components

Implement the minimum reusable component contract required by at least two models.

Exit Criteria

At least one component is reused by two independently versioned models.

⸻

Phase 6 — Legacy Migration

Classify and progressively migrate existing repositories and model assets.

No bulk migration is required.

⸻

31. Acceptance Criteria

CR-AM-11 shall be complete when the following conditions are satisfied.

Organizational

* Assessment-Models has an active architectural purpose.
* Organization governance is documented.
* Repository taxonomy is documented.
* technehub-labs and Assessment-Models responsibilities are explicit.

Metamodel

* OpenDEA contracts are published independently of model repositories.
* Contracts are versioned.
* External repositories can declare dependencies.

Registry

* assessment-registry exists.
* Maturity models can be registered.
* References are immutable.
* Active versions can be identified.
* Dependencies can be resolved.

CI

* Model-level validation exists.
* Contract-level validation exists.
* Ecosystem-level validation exists.
* Cross-repository dependencies are validated.
* Compatibility failures are detectable.
* All three CI levels (Local, Contract Conformance, Ecosystem) are demonstrated
  by the SAME first model — the Phase 4 initial candidate — so that no level is
  claimed green against a different fixture.

Independence

* Each maturity model can evolve independently.
* Each maturity model has independent versioning.
* No model requires a shared repository release.
* No Git submodule dependency is required.

Referenceability

* Each model declares its contract dependency.
* Each external reference is versioned.
* Registry references are immutable.
* CI can resolve referenced assets.

Reuse

* Reusable components are independently referenceable.
* Component reuse does not implicitly import scoring or scale semantics.
* Component versions are explicit.

OpenDEA Reference Model

* dea-metamodel/assessment-models contains the OpenDEA EA assessment model instance.
* The instance conforms to the canonical contracts.
* The instance demonstrates the assessment and maturity architecture.

⸻

32. Definition of Done

CR-AM-11 is complete when the following architecture is operational:

┌─────────────────────────────────────────────────────────────┐
│                      TECHNEHUB-LABS                         │
│                                                             │
│                     dea-metamodel                           │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 CANONICAL CONTRACTS                 │   │
│   │                                                     │   │
│   │ Assessment • Maturity • Scale • Scoring             │   │
│   │ Conformance • Benchmark • Validation                │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │                              │
│                      Versioned Contract                      │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT-MODELS                        │
│                                                             │
│                    assessment-registry                      │
│                              │                              │
│                ┌─────────────┼──────────────┐               │
│                ▼             ▼              ▼               │
│             Model A       Model B        Model C             │
│                │             │              │               │
│                └─────────────┼──────────────┘               │
│                              ▼                              │
│                         assessment-ci                       │
│                                                             │
│       Compatibility • Dependencies • Integration            │
└─────────────────────────────────────────────────────────────┘

The decisive outcome is that OpenDEA’s canonical metamodel can evolve as an engineering asset within technehub-labs, while an independent Assessment-Models organization manages a federated ecosystem of maturity models and assessment assets that remain explicitly versioned, contractually conformant and continuously integrated.
⸻

33. Annex A — Contract Inventory (initial mapping)

The six contract families of section 16 map to already-landed dea-metamodel
artifacts as follows. This annex is the Phase 2 objective checklist; Phase 2
publishes each family from its declared canonical location rather than
interpreting the families from scratch.

Assessment Contract
  assessment-models/schemas/assessment-model.schema.json (central contract)
  assessment-models/schemas/assessment-instrument.schema.json
  assessment-models/schemas/assessment-execution.schema.json
  assessment-models/schemas/assessment-result.schema.json (CR-AM-04 result ops)
  assessment-models/schemas/capability.schema.json, scenario.schema.json,
  measure.schema.json, evidence.schema.json

Maturity Model Contract
  assessment-models maturity sub-tree (v2 canonical model structure, CR-014)
  CR-AM-10 Phase 1 maturity-component + component-reference schemas (PR #144)

Maturity Scale Contract
  CR-AM-09 Phase 1 maturity-scale schema + Phase 3 band/resolution schemas
  assessment-models/maturity/ v2 canonical bands (Emergent / Structured /
  Systematic / Adaptive / Self-Optimising; non-linear 20/25/25/18/12;
  per-level effort_multiplier)

Scoring Contract
  assessment-models/schemas/scoring-model.schema.json
  CR-AM-09 Phase 2 maturity-evaluation schema + v2 band arithmetic (validated
  worked example in CI)

Conformance Contract
  assessment-models/schemas/compatibility.schema.json
  assessment-models/schemas/relationship.schema.json
  assessment-models/schemas/common.schema.json ($defs incl. modelReference)
  assessment-models/governance/versioning.md + compatibility.md

Benchmark Contract
  CR-AM-06 benchmark-eligibility schema + governance/benchmark-eligibility.md
  CR-AM-07 benchmark-comparison schema + governance/comparison-policy.md
  assessment-models/benchmark/ sub-tree

Versioning note: contract families are independently identifiable (section 16)
but initially versioned together with the dea-metamodel release that publishes
them; independent per-family versioning is a Phase 2 design decision to be
recorded in the contract-publication ADR.
