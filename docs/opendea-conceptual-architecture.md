# OpenDEA — Conceptual Architecture

> The single authoritative narrative consolidating CR-1 → CR-10 (CR-10 §A).
> **Informative** documentation (see [Normative vs Informative](#normative-vs-informative))
> — the normative contract lives in [`specification/`](../specification/OpenDEA-Semantic-Architecture-Specification.md).
> Settled decisions referenced here are recorded in [`docs/adr/`](adr/README.md).

## 1. What is OpenDEA?

OpenDEA is a **semantic contract for representing, connecting, governing,
assessing, reasoning about, and evolving an enterprise** (CR-10 §P).

It is not limited to an architecture repository, a visualization tool, a
knowledge graph, an AI framework, an assessment framework, or a digital twin.
Those are implementation and application layers that consume and extend the
OpenDEA semantic foundation.

Concretely (CR-10 §A):

```
OpenDEA
   =
Semantic Foundation        (the metamodel — CR-1…CR-8)
+  Enterprise Knowledge Graph   (the runtime semantic backbone — CR-9)
+  Runtime Services             (validation, reasoning, integration — CR-9)
+  Decision Intelligence Interfaces (scenarios, simulation, recommendation — CR-10)
```

—not “an EA modeling tool.”

## 2. What problem does it solve?

Enterprise architecture knowledge is scattered across repositories, diagrams,
CMDBs, assessment spreadsheets and people's heads — each with its own
vocabulary, none connected, none queryable, none governable. When AI agents
arrived, they inherited that chaos: no canonical semantics to reason over, no
authority model to act within, no provenance to trust.

OpenDEA provides one semantic contract so that:

- **every representation means the same thing** (CR-1 canonical model, CR-8
  specification + conformance),
- **every connection is typed and traceable** (CR-2/CR-3 relationship
  semantics),
- **time, change and maturity are first-class** (CR-5/CR-6),
- **decisions, authority and agents are governed** (CR-7),
- **the model is executable** — loadable, queryable, extensible by machines
  (CR-9 runtime),
- **the future is explorable without touching the present** — scenarios,
  simulation, decision intelligence (CR-10).

## 3. What is the metamodel?

The normative semantic definition: **142 entity types, 104 relationship
types**, organized as a small frozen **Core** (18 anchors) plus **profiles**
that extend but never redefine it (CR-4, CR-8 §3-§4). Everything else —
schemas, Turtle, TypeScript, Pydantic, SQLite, documentation — is a *derived,
version-pinned, drift-tested* artifact of the one normative source
(`metamodel/dea-metamodel.yaml`, CR-1).

The metamodel answers: **"What does this mean?"**

## 4. What is the runtime?

The CR-9 reference implementation of the semantic contract: a
vendor-independent `GraphStore`, a canonical model loader that validates
before it loads, and registry-validated entity/relationship APIs. The runtime
answers: **"What can we do with it?"**

Two invariants govern everything the runtime does:

- **No silent inference (CR-9CQ):** inferred knowledge never becomes
  authoritative fact without an explicit state transition.
- **No autonomous mutation by default (CR-9CR):** agents are read-only unless
  explicitly authorized through authority, policy, scope and approval.

**The reference implementation is an implementation of OpenDEA, not OpenDEA
itself** (CR-10 §N). The dependency direction is strict:

```
Specification
      ↑
Reference Runtime
      ↑
     Viewer
```

— never `Viewer = Specification`. This separation is what allows independent
implementations to exist (CR-9BV, CR-9CL).

## 5. The canonical layer model (CR-10 §B)

```
┌────────────────────────────────────────────────────────────┐
│                  EXPERIENCE & AGENTS                       │
│ Explorer | Architects | Executives | AI Agents             │
├────────────────────────────────────────────────────────────┤
│                 DECISION INTELLIGENCE                      │
│ Scenario | Impact | Assessment | Recommendation | Decision │
├────────────────────────────────────────────────────────────┤
│                    RUNTIME SERVICES                        │
│ Query | Reasoning | Policy | Events | Integration          │
├────────────────────────────────────────────────────────────┤
│                  KNOWLEDGE GRAPH                           │
│ Entities | Relationships | Assertions | Evidence | State   │
├────────────────────────────────────────────────────────────┤
│                 SEMANTIC FOUNDATION                        │
│ Core | Profiles | Schemas | Rules | Vocabularies           │
├────────────────────────────────────────────────────────────┤
│                    ENTERPRISE                              │
│ Strategy | Business | Data | Apps | Technology | AI        │
└────────────────────────────────────────────────────────────┘
```

Each layer consumes the layer below through defined interfaces; no layer
reaches around another. CR-1…CR-8 built the Semantic Foundation; CR-9 built
the Knowledge Graph and started Runtime Services; CR-10 builds Decision
Intelligence; the Explorer and agent experiences (CR-9.9) sit on top.

## 6. What is the relationship to enterprise architecture?

OpenDEA is a **semantic operating layer for enterprise architecture** (CR-9 §1)
— not another EA repository. A repository stores artifacts of the architecture
loop; OpenDEA *executes* the loop: Observe → Model → Assess → Reason → Decide
→ Act → Observe (CR-9CS). EA frameworks (ArchiMate, TOGAF content) map *into*
OpenDEA semantics (`mappings/archimate/`); OpenDEA does not adopt their
metamodels.

## 7. What is the relationship to DMM?

DMM measures **how capable/mature the enterprise is**; OpenDEA represents
**what exists, how it relates, how it operates, and how it can change**. DMM
is the diagnostic instrument; OpenDEA is the semantic architecture and
transformation substrate. Full treatment:
[opendea-and-dmm.md](opendea-and-dmm.md).

## 8. What is the relationship to AI and agents?

Three distinct roles (CR-10 §G): OpenDEA as **knowledge** (enterprise semantic
context), as **governance** (authority, policy, decision, evidence), and as
**agent infrastructure** (discovery, context, capability, tool, authority,
action, audit). OpenDEA is **not itself an AI agent framework**. Full
treatment: [opendea-and-agents.md](opendea-and-agents.md).

## 9. What is the relationship to digital twins?

OpenDEA is on a maturity ladder toward digital-twin capability — Semantic
Metamodel → Enterprise Model → Observed Architecture → Operational Model →
Dynamic Simulation → Digital Twin — and does not claim twin status it cannot
substantiate (CR-10AA/AB). Full treatment:
[concepts/digital-twin.md](concepts/digital-twin.md).

## 10. What is explicitly outside OpenDEA?

- **Physics, process, financial, network and AI simulation engines** — they
  integrate through the `SimulationAdapter` boundary; OpenDEA is the semantic
  coordination layer (CR-10AC/AD).
- **Project/programme management** — Initiatives reference execution systems;
  OpenDEA is not a PM tool (CR-10V).
- **An AI agent framework** — OpenDEA provides the semantic context and
  governance substrate agentic systems operate upon (CR-10 §G).
- **A complete financial model in Core** — cost/value attributes live in a
  profile (CR-9BK).
- **A digital twin (today)** — CR-10 Phase 7 lays the foundation and MUST NOT
  be claimed complete until synchronization and behavioral semantics exist
  (CR-10AW Phase 7).

## 11. Core vs Profiles (CR-10 §I)

> **Core defines stable enterprise semantics. Profiles define domain-specific
> semantics.**

The Core stays deliberately small (18 anchors, anti-inflation rule, CR-8 §4).
Candidate profiles: DMM, AI/Agent, Security, Data Architecture, Technology
Architecture, Risk, Governance, Industry profiles. Profiles declare
`depends_on`, extend, and never redefine (CR-4 O001–O009). See
[ADR-002](adr/ADR-002-core-versus-profiles.md).

## 12. Normative vs Informative (CR-10 §J)

| | Normative | Informative |
|---|---|---|
| Language | MUST, MUST NOT, SHOULD, SHOULD NOT, MAY | examples, guidance, patterns, rationale, tutorials |
| Lives in | `specification/` (+ `metamodel/`, `schemas/`) | `docs/` |
| Change control | CR + conformance suite | review |

This document and everything under `docs/` is **informative**: it explains and
interprets. Where informative text and the specification disagree, the
specification wins — and the documentation is drift.

## 13. The semantic stack (CR-10 §P)

```
                         OPENDEA
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    REPRESENT           UNDERSTAND          EVOLVE
        │                   │                   │
    Metamodel          Knowledge Graph     Scenarios
    Profiles           Assessment          Simulation
    Relationships      Reasoning           Decisions
    State              Evidence            Transformation
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                       GOVERN & ACT
                            │
                   Policies / Agents
                   Authority / Change
                            │
                            ↓
                   CONTINUOUS ENTERPRISE
```

This is the point at which the CR sequence becomes a coherent platform
architecture — not a sequence of metamodel enhancements.

## 14. Roadmap (CR-10 §O)

| CR | Theme | Status |
|---|---|---|
| CR-1…CR-3 | Foundation, semantic structure, relationships | Implemented |
| CR-4 | Core ontology / governance of the vocabulary | Implemented |
| CR-5…CR-7 | Assessment, temporal, agents & decisions | Implemented |
| CR-8 | Specification & conformance (**OpenDEA 1.0**) | Implemented |
| CR-9 | Runtime & knowledge graph | CR-9.1 implemented; 9.2–9.10 queued |
| CR-10 | Scenario, simulation & decision intelligence | Phase 1 implemented; Phases 2–7 queued |
| CR-11 | Interoperability, federation & ecosystem conformance — consolidation, *not* another conceptual expansion; mapping to external EA standards and enterprise sources without compromising the canonical model | Proposed |
| CR-12 | Enterprise intelligence / advanced agentic runtime | Proposed |
| CR-13 | Digital twin / continuous enterprise model | Proposed |
