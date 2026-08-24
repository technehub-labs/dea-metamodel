This is CR-CM-000A — Terminology Alignment, before we establish the repository itself. This is the right sequencing because the Domain collision needs to be resolved as an architectural vocabulary decision first; otherwise we risk encoding the ambiguity into the Concepts Model.

CR-CM-000 — OpenDEA Concepts Terminology Alignment

Status: Proposed
Scope: dea-metaframework, dea-concepts-model
Type: Conceptual Architecture / Governance
Priority: Critical
Depends on: Existing Enterprise Concept Framework in dea-metaframework
Precedes: CR-CM-001 — OpenDEA Concepts Model Foundation

1. Objective

Establish an unambiguous terminology architecture for the OpenDEA body of work so that the Enterprise Concept Framework (ECF), OpenDEA Concepts Model, Foundational Metamodel, catalogs and domain repositories do not use the same terms with different meanings.

The immediate concern is the overloaded use of Domain.

The ECF already gives Domain a precise structural meaning as one axis of its Domain × Stage enterprise concept coordinate system. The proposed Concepts Model previously used “Domain” merely as a thematic grouping mechanism.

This CR eliminates that ambiguity and establishes the vocabulary rules that all subsequent Concepts Model work must follow.

⸻

2. Problem Statement

OpenDEA is evolving several complementary semantic layers:

Enterprise Concept Framework
          │
          ▼
OpenDEA Concepts Model
          │
          ▼
Foundational Metamodel
          │
          ▼
Catalogs / Domain Models / Implementations

These layers currently use overlapping terminology.

The most significant collision is:

ECF Domain
       ≠
Concept Model thematic domain

An ECF Domain is a structural enterprise dimension.

A thematic grouping of concepts is merely an organizational classification.

Treating both as Domain creates several risks:

* ambiguous model semantics;
* incorrect mappings into the metamodel;
* accidental inheritance relationships;
* confusion in PlantUML models;
* inconsistent YAML/JSON representations;
* unclear repository ownership;
* difficulty mapping TM Forum and other external models;
* future incompatibility between dea-metaframework and dea-concepts-model.

⸻

3. Architectural Decision

3.1 Reserve Domain

Within OpenDEA:

Domain is reserved for the Enterprise Concept Framework meaning.

The canonical construct is:

ECF Domain

and its semantics are defined by dea-metaframework.

No Concepts Model artifact may introduce an independent construct called Domain to mean “collection of related concepts.”

⸻

4. Introduce Concept Area

The Concepts Model shall use:

Concept Area

to represent a thematic grouping of related concepts.

Examples:

Enterprise Concept Area
Operations Concept Area
Intelligence Concept Area
Execution Concept Area
Control Concept Area
Scenario Concept Area
Value Concept Area
Systems Concept Area

These are organizational classifications, not enterprise structural dimensions.

Therefore:

Concept Area
      │
      └── organizes → Concept

rather than:

Domain
      │
      └── contains → Concept

⸻

5. Introduce Concept Profile

The Concepts Model shall use:

Concept Profile

for a purposeful selection and relationship view of concepts addressing a particular problem, capability, architecture or transformation perspective.

Examples:

Agentic Enterprise Profile
Autonomous Operations Profile
Autonomous Networks Profile
Value Realization Profile
Agentic Workflow Profile

A profile is therefore compositional, rather than hierarchical.

Concept Profile
     │
     ├── includes → Concept
     ├── includes → Relationship
     └── references → ECF Context

⸻

6. Introduce ECF Context

An individual concept may need to be contextualized against the Enterprise Concept Framework.

Rather than adding an ambiguous domain attribute directly to a concept, introduce:

ECF Context

An ECF Context identifies the applicable:

ECF Domain
+
ECF Stage

Therefore:

Concept
   │
   └── has-context
             │
             ▼
        ECF Context
          ├── Domain
          └── Stage

This makes the semantic boundary explicit.

⸻

7. Canonical Vocabulary

The following vocabulary shall be established:

Term	Canonical Meaning	Layer
Domain	Enterprise structural dimension defined by ECF	MetaFramework
Stage	Enterprise lifecycle dimension defined by ECF	MetaFramework
ECF Context	Domain + Stage context for an enterprise concept	Concepts Model
Concept	A defined unit of meaning	Concepts Model
Concept Area	Thematic organization of concepts	Concepts Model
Concept Profile	Purposeful composition of concepts and relationships	Concepts Model
Concept Classification	Mechanism for categorizing concepts	Concepts Model
Entity	Formal information-model construct	Metamodel
EntitySpec	Specification of an entity type	Metamodel
Relationship	Formal association between information constructs	Metamodel
Catalog	Curated reusable collection of semantic artifacts	Catalog Layer

⸻

8. Semantic Distinction

The following distinction becomes normative:

                    ECF
                     │
             ┌───────┴───────┐
             │               │
          Domain           Stage
             │               │
             └───────┬───────┘
                     │
                     ▼
                ECF Context
                     │
                contextualizes
                     │
                     ▼
                  Concept
                     │
          ┌──────────┴──────────┐
          │                     │
    classified-by          composed-in
          │                     │
          ▼                     ▼
   Concept Area          Concept Profile

The terms must not be collapsed.

⸻

9. Relationship Semantics

The CR establishes the following canonical conceptual relationship verbs.

ECF

Concept ── has-ecf-context ──> ECF Context
ECF Context ── uses-domain ──> ECF Domain
ECF Context ── uses-stage ──> ECF Stage

Concept Organization

Concept ── belongs-to ──> Concept Area
Concept Profile ── includes ──> Concept
Concept Profile ── includes ──> Concept Relationship

Metamodel Bridge

Concept ── maps-to ──> Metamodel EntitySpec

The maps-to relationship is deliberately different from:

is-a
specializes
inherits-from

because conceptual classification does not automatically imply metamodel inheritance.

⸻

10. Prohibited Semantics

The following patterns shall be explicitly prohibited.

❌ Generic Domain

concept:
  domain: Operations

unless Operations is an actual canonical ECF Domain.

❌ Concept Area as ECF Domain

Operations Concept Area
       =
Operations ECF Domain

This equivalence shall not be assumed.

❌ Profile as Domain

Agentic Enterprise Domain

when the intention is a conceptual perspective.

It should be:

Agentic Enterprise Profile

❌ Implicit Metamodel Type

A concept such as:

Agentic Operations

must not automatically become:

AgenticOperations : Capability

without a separate metamodel mapping decision.

⸻

11. Concept Area Model

The initial Concept Areas should be treated as organizational scaffolding, not as a permanent ontology.

Recommended initial set:

Concept Areas
│
├── Enterprise
├── Operations
├── Intelligence
├── Execution
├── Control
├── Scenario
├── Value
├── Measurement
└── Systems

These are intentionally not called Domains.

They may evolve as the Concepts Model matures.

⸻

12. Application to the Agentic–Autonomous Model

For example:

Agentic Operations

could be represented as:

name: Agentic Operations
conceptAreas:
  - Operations
  - Intelligence
ecfContexts:
  - domain: <ECF-Domain>
    stage: <ECF-Stage>
profiles:
  - Agentic Enterprise
  - Autonomous Operations
metamodelMapping:
  status: candidate

Notice that:

Operations

under conceptAreas does not claim that Operations is an ECF Domain.

⸻

13. Application to HVS and VOF

This distinction becomes particularly useful for the work we just established.

For example:

High-Value Scenario

could belong to:

Concept Areas
├── Scenario
├── Value
└── Measurement

and participate in:

Concept Profiles
├── Autonomous Operations
└── Value Realization

while being contextualized by:

ECF Context
└── ECF Domain + ECF Stage

Similarly:

Value Operations Framework

would belong to:

Concept Areas
├── Value
└── Measurement

and:

Value Realization Profile

without creating a new “Value Domain.”

⸻

14. Repository Governance

dea-concepts-model shall maintain a canonical terminology registry:

governance/
└── terminology-registry.yaml

The registry shall contain at minimum:

terms:
  - name: Domain
    namespace: ECF
    status: reserved
    owner: dea-metaframework
  - name: Stage
    namespace: ECF
    status: reserved
    owner: dea-metaframework
  - name: Concept Area
    namespace: ConceptModel
    status: canonical
    owner: dea-concepts-model
  - name: Concept Profile
    namespace: ConceptModel
    status: canonical
    owner: dea-concepts-model
  - name: ECF Context
    namespace: ConceptModel
    status: canonical
    owner: dea-concepts-model

This becomes the first piece of cross-repository semantic governance.

⸻

15. Acceptance Criteria

CR-CM-000 is complete when:

* Domain is formally reserved for ECF semantics.
* Stage remains reserved for ECF semantics.
* Concept Area replaces the generic use of “Domain” in the Concepts Model.
* Concept Profile is established as the compositional view mechanism.
* ECF Context is established as the Domain × Stage contextualization mechanism.
* The distinction between ECF Domain and Concept Area is documented.
* A canonical terminology registry exists.
* The proposed dea-concepts-model repository structure uses concept-areas/, not domains/.
* PlantUML conventions reflect the distinction.
* Machine-readable concept examples do not use ambiguous domain attributes.
* The metamodel bridge distinguishes maps-to from inheritance/specialization.
* Existing dea-metaframework semantics are referenced rather than redefined.
* Subsequent Concepts Model CRs reference this terminology decision.

⸻

16. Deliverables

The CR should produce:

dea-metaframework/
└── docs/
    └── terminology/
        └── concepts-model-alignment.md
dea-concepts-model/
├── README.md
├── GOVERNANCE.md
├── governance/
│   └── terminology-registry.yaml
│
├── concept-areas/
├── profiles/
├── concepts/
├── relationships/
├── mappings/
│   └── ecf/
│
└── models/
    └── terminology-alignment.puml

The dea-concepts-model repository itself can be created as part of CR-CM-001; CR-CM-000 should establish the semantic contract first.

⸻

17. Definition of Done

The strongest test is whether a reader can encounter the word Domain anywhere in OpenDEA and answer:

“Do you mean an Enterprise Concept Framework Domain?”

If the answer is yes, Domain is appropriate.

If the answer is:

“No, I just mean a grouping of related concepts.”

then the correct term is Concept Area.

If the answer is:

“I mean a selected set of concepts for a particular architectural perspective.”

then the correct term is Concept Profile.

If the answer is:

“I mean where this concept sits in the ECF’s Domain × Stage coordinate system.”

then the correct construct is ECF Context.

That gives us a clean semantic contract before we proceed to CR-CM-001 — OpenDEA Concepts Model Foundation.