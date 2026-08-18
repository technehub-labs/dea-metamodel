# OpenDEA Conformance Model

> **KB note — what it means for an implementation, model, or runtime to be
> *OpenDEA-conformant* today, and where the next level takes us.**
> Distils the conformance commitments of CR-8 (semantic), CR-9 (runtime and
> interop), and the proposed CR-10 agentic layer into one map.
> Sources: [CR-8](../change-requests/CR-008.md), [CR-9CL](../change-requests/CR-009.md),
> [CR-9CM](../change-requests/CR-009.md), [CR-9CN](../change-requests/CR-009.md),
> [CR-9.8](../change-requests/CR-009.md), and CR-10 §M.

## 1. The question conformance answers

A metamodel is not a standard. Two independent implementations that reach
different conclusions about the same model have not implemented a standard
— only a rich model (CR-8 §69). Conformance is what closes that gap: a
third party, given only the specification, schemas, profiles and rules,
independently determines whether an artefact is conformant
([specification-and-conformance.md](specification-and-conformance.md) §2).

CR-8 answered that question for the **semantic** contract.
CR-9 added **runtime** and **interoperability** conformance.
CR-10 adds — and CR-9.8 operationalises — the **agentic** level.

## 2. The four levels

| Level | Question answered | Source CRs | Key artefacts | Status |
|---|---|---|---|---|
| **L1 Semantic** | *"Is this model a valid OpenDEA model?"* | CR-8 | Frozen Core (18 anchors + envelope), canonical vocabulary, profiles (`specification/`), reference validator (`tools/opendea_validate.py`), **golden models** (must pass) and **negative models** (must fail for the expected rule) under `models/golden/` and `models/invalid/`; conformance levels 0–5 (Core, vocabulary, structural, semantic, profile, cross-profile) | **Implemented** |
| **L2 Runtime** | *"Does this runtime behave like an OpenDEA runtime?"* | CR-9CL | Vendor-independent `GraphStore` ABC (`runtime/`), vendor-independent contract suite (`tests/runtime/test_graphstore_contract.py`), and seven conformance categories — **Core / Profile / API / Query / Validation / Provenance / Security** | **Implemented** (CR-9.1; categories grow through CR-9.2–9.8) |
| **L3 Interoperability** | *"Do two independent runtimes produce the same semantic result regardless of source?"* | CR-9CM, CR-9CN | OpenDEA Interoperability Test Suite (`Source → Mapping → OpenDEA → Validation → Graph → Query`) and **golden graphs** (`golden-enterprise.graph` and siblings) with expected node / edge / assertion counts and specific traversal results — regression artefacts seeded from `GraphStore.stats()` | **Partial** (suite seed in CR-9.1; full release → CR-9.10) |
| **L4 Agentic** | *"Can this agent act *as* OpenDEA — evaluate its own authority, audit its own actions, conform to policy?"* | CR-9.8 (CR-9AH…AR), CR-10 §M | Agent Runtime Interface (`discover / query / assess / reason / recommend / requestDecision / execute / report`), Authority evaluation (CR-9AJ), Policy Decision Point returning ALLOW / DENY / ESCALATE (CR-9AK), policy-driven Human-in-the-loop thresholds (CR-9AL — never hard-coded), Agent Action Audit (CR-9AM/CI, including model/version and prompt/context *references* — not raw prompts in the graph) | **Proposed** (CR-9.8 milestone; CR-10 §M consolidates the conformance contract) |

### 2.1 Level 1 — Semantic Conformance (CR-8, levels 0–5)

CR-8 freezes the semantic contract: 18 Core anchors, the canonical
relationship grammar (CR-2), the envelope schema, the naming rules, and
the profile mechanism. Conformance is graded:

| Level | Capability | Typical artefact |
|---|---|---|
| **0** — Core | Recognises the 18 anchors and the envelope | A loader that parses an OpenDEA document |
| **1** — Vocabulary | Uses canonical identifiers (`dea:` namespace) | A validator that fails on legacy IDs |
| **2** — Structural | Enforces type/cardinality/temporal constraints | Schema validation passes |
| **3** — Semantic | Enforces cross-entity rules (A008, T001–T010, G001–G016) | Reference validator (`tools/opendea_validate.py`) passes |
| **4** — Profile | Honours one or more declared profiles | Profile-scoped validator passes |
| **5** — Cross-profile | Resolves conflicts when multiple profiles are composed | Cross-profile test passes |

The **golden / negative contract** is what makes the levels executable:
every golden model MUST pass; every negative model MUST fail for exactly
its expected DEA-E rule code. A specification you cannot test is prose
([specification-and-conformance.md](specification-and-conformance.md) §3,
CR-8 §32-§33).

### 2.2 Level 2 — Runtime Conformance (CR-9CL)

CR-9CL adds the runtime equivalent of the semantic contract: an
implementation MUST demonstrate conformance across seven categories:

```
Core Conformance
Profile Conformance
API Conformance
Query Conformance
Validation Conformance
Provenance Conformance
Security Conformance
```

**Vendor independence is a conformance concern, not a preference**
([runtime-architecture.md](runtime-architecture.md) §4). Every semantic
service programs against the `GraphStore` interface (`createEntity /
updateEntity / deleteEntity / createRelationship / query / traverse /
findPath / infer / transaction`). Neo4j, Neptune, ArangoDB,
PostgreSQL+graph, RDF triplestores and the in-memory reference store are
**interchangeable**. Conformance is demonstrated by passing the
vendor-independent contract suite
`tests/runtime/test_graphstore_contract.py` — to conform a new store,
subclass the contract and supply a fixture.

Two invariants travel with the runtime from the foundation:

- **No silent inference (CR-9CQ).** `GraphStore.infer()` raises
  `InferenceUnavailable`; a test proves loaded graphs contain exactly the
  edges the model declared — nothing derived materialises silently.
- **No autonomous mutation by default (CR-9CR).** In CR-9.1 there is
  simply no agent write path. Later milestones add the full chain:
  Agent → Role → Authority → Policy → Scope → Action.

### 2.3 Level 3 — Interoperability Conformance (CR-9CM, CR-9CN)

Interoperability asks: *does the same input produce the same semantic
result regardless of the source system that provided it, the mapping
that translated it, or the graph store that holds it?*

CR-9CM specifies the interop pipeline:

```
Source
  ↓
Mapping
  ↓
OpenDEA
  ↓
Validation
  ↓
Graph
  ↓
Query
```

CR-9CN adds **golden graphs** to runtime that CR-8 added to models:
expected node / edge / assertion counts and specific traversal results
(`Capability → Service = expected set`, `Agent → Authority = expected set`,
`Objective → Capability = expected set`) become regression artefacts.
`GraphStore.stats()` is the seed; full release lands at CR-9.10.

### 2.4 Level 4 — Agentic Conformance (CR-9.8 + CR-10 §M, proposed)

The next level is the agent itself. An agent that interacts with OpenDEA
through the canonical interface
(`discover / query / assess / reason / recommend / requestDecision /
execute / report`, CR-9AH) MUST be able to demonstrate:

- **Authority evaluation (CR-9AJ).** For every proposed action, the agent
  can prove (or fail to prove) that the action is within the union of
  declared Authorities, Policies and Scopes — evaluated against the live
  graph, not against a cached snapshot.
- **Action audit (CR-9AM/CI).** Every agent action is recorded with
  model/version, prompt/context *references* (never raw prompts in the
  graph), inputs, outputs, decision-id, and the authority/policy
  evaluation that authorised it.
- **Policy conformance (CR-9AK/AL).** The Policy Decision Point returns
  ALLOW / DENY / ESCALATE; Human-in-the-loop thresholds are
  policy-driven, never hard-coded.

The conformance artefacts for L4 (reference agent, audit-log schema,
policy-conformance suite) are scoped to CR-9.8; CR-10 §M consolidates
the contract.

## 3. How the levels stack

```
L4 Agentic        ─── "the agent acts AS OpenDEA"
   │
L3 Interop        ─── "any runtime, any source, same semantics"
   │
L2 Runtime        ─── "this runtime behaves like an OpenDEA runtime"
   │
L1 Semantic       ─── "this model IS an OpenDEA model"
```

A conformant agent (L4) presupposes an interoperable runtime (L3),
which presupposes a conformant runtime (L2), which presupposes a
conformant model (L1). The point of levelling is to keep each level
independently testable: an L2 conformance failure is meaningful even
when L1 conformance holds, and an L4 failure is meaningful even when
L2/L3 hold.

## 4. The CI gate (CR-9CP)

All four levels are gated in CI. A proposed merge MUST fail if:

- schema validation fails
- golden models fail
- semantic tests fail
- runtime tests fail
- mapping / interop tests fail
- security tests fail
- (at L4) agent-conformance tests fail

This is important because CR-9 onwards introduces substantially more
moving semantic machinery ([runtime-architecture.md](runtime-architecture.md) §12).

## 5. What conformance is NOT

- **Conformance is not adoption.** An L4-conformant agent still requires
  deployment, governance and change management to be useful.
- **Conformance is not endorsement.** Conformance demonstrates that an
  artefact speaks OpenDEA correctly; it does not certify its accuracy
  with respect to the enterprise.
- **Conformance is not completeness.** A conformant runtime is one that
  honours the semantic contract on the artefacts it chooses to support.
  The conformance statement MUST declare which profiles it implements
  (ADR-002).
- **Conformance is not a single level.** A serious OpenDEA deployment is
  expected to progress through the levels — semantic first, runtime
  second, interop third, agentic fourth — and to declare its current
  level honestly.