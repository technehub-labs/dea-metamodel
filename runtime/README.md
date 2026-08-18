# OpenDEA Runtime — CR-9 Reference Implementation

> **Status:** CR-9.1 (Runtime Foundation) implemented · CR-9.2…CR-9.10 queued
> **Consumes:** OpenDEA Specification 1.0.0 (CR-8) — the semantic contract stays
> authoritative; the runtime provides *interchangeable implementations* of graph,
> inference, integration, assessment and agentic services (CR-9 §101).

CR-8 defined the language and rules. CR-9 defines the runtime that operates on
that language. The runtime's objective is the closed loop:

```
Enterprise Reality → Ingest → Knowledge Graph → Assess / Reason / Query
     ↑                                                    ↓
     └────────── Action / Change ← Decision Support ←─────┘
```

## What exists today (CR-9.1 — Runtime Foundation)

| Component | Path | CR-9 section |
|---|---|---|
| Canonical graph model (Node/Edge, first-class edge metadata) | `runtime/graph/base.py` | §6 (CR-9E) |
| `GraphStore` — vendor-independent graph interface | `runtime/graph/base.py` | §5 (CR-9D) |
| `InMemoryGraphStore` — reference implementation | `runtime/graph/memory.py` | §75 (CR-9BV) |
| Canonical model loader (validate → atomic load) | `runtime/model/loader.py` | §73 (CR-9BT.2/.3), §12 (CR-9K) |
| Canonical identity helpers (CR-8 §7) | `runtime/model/identity.py` | §14 (CR-9M prerequisite) |
| `RuntimeService` — entity/relationship CRUD with registry validation | `runtime/api/service.py` | §74 Phase 1 (CR-9BU) |
| Vendor-independent contract suite | `tests/runtime/test_graphstore_contract.py` | §91 (CR-9CL seed) |
| Runtime test suite (49 tests) | `tests/runtime/` | §94 (CR-9CO) |

## Usage

```python
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.api import RuntimeService

store = InMemoryGraphStore()

# Load a conformant model — validation (levels 0–3) runs first; a model that
# fails is refused and the graph stays empty (CR-9K, CR-9BP).
report = load_model("models/golden/enterprise.yaml", store)

# Entity/relationship CRUD with registry-backed write validation
svc = RuntimeService(store)
svc.create_entity("app.cs-platform", "ApplicationComponent", "CS Platform")
svc.create_relationship("app.cs-platform", "supports", "cap.customer-service")

# Vendor-independent queries, incl. temporal filtering (CR-9F)
svc.query(type="BusinessCapability")
svc.traverse("app.cs-platform")
svc.find_path("app.cs-platform", "cap.customer-service")
store.neighbors("cap.customer-service", direction="in",
                at="2026-06-01T00:00:00Z")   # "what is true now?"
```

## Design principles enforced in code

1. **Validation before the graph (CR-9K).** Nothing enters the store without
   passing the CR-8 reference validator. The loader *uses*
   `tools/opendea_validate.py` — it never re-implements rules.
2. **The graph is the runtime semantic representation, not a visualization
   structure (CR-9C).** Edges are first-class and carry provenance, temporal
   validity, lifecycle status and properties (CR-9E).
3. **Model ≠ runtime state ≠ assertion ≠ evidence ≠ inference (CR-9B).** These
   are distinct fields on `Node`/`Edge`; nothing collapses them.
4. **No silent inference (CR-9CQ).** `GraphStore.infer()` raises
   `InferenceUnavailable` — reasoning lands in CR-9.3 and must always carry
   provenance and explicit state transitions. Loads materialize exactly the
   edges the model declared (test-enforced).
5. **No autonomous mutation by default (CR-9CR).** The foundation exposes no
   agent write path. Any future agent write passes through authority/policy
   evaluation (CR-9AJ/AK) first.
6. **Vendor independence (CR-9D).** Semantic services depend only on the
   `GraphStore` ABC. Neo4j, Neptune, ArangoDB, PostgreSQL+graph, RDF
   triplestores conform by passing the shared contract suite.
7. **Atomic mutations (CR-9BP).** Loads and multi-writes run in transactions;
   failure rolls back — the graph is never partially updated.
8. **Planned ≠ current (CR-6 §22).** Temporal traversal filters never read a
   planned/proposed/retired edge as a current edge.

## Milestone plan (CR-9CT)

| Milestone | Scope | Status |
|---|---|---|
| CR-9.1 | Runtime Foundation — graph abstraction, model loading, entity/relationship APIs | **Implemented** |
| CR-9.2 | Knowledge Graph — canonical graph representation and provenance | Proposed |
| CR-9.3 | Semantic Reasoning — rules, inference, explainability (CR-9Q/R/S/T) | Proposed |
| CR-9.4 | Temporal & Event Runtime — events, snapshots, bitemporal queries (CR-9F/G/H/I) | Proposed |
| CR-9.5 | Integration Framework — adapters, mapping, identity resolution (CR-9J…O) | Proposed |
| CR-9.6 | Assessment Runtime — DMM execution (CR-9X/Y) | Proposed |
| CR-9.7 | Decision & Impact Engine (CR-9Z…AG) | Proposed |
| CR-9.8 | Agent Runtime — discovery, authority, policy, audit (CR-9AH…AR) | Proposed |
| CR-9.9 | OpenDEA Explorer — viewer decoupled, API-driven (CR-9BX…CB) | Proposed |
| CR-9.10 | Conformance & Interoperability Release — golden graphs, interop suite (CR-9CL…CP) | Proposed |

## CR-10 — Scenario & Decision Intelligence (Phase 1 implemented)

`runtime/scenario/` adds the CR-10 Phase 1 scenario foundation on top of the
CR-9 graph: first-class scenarios referencing immutable baselines, an explicit
eleven-operation delta vocabulary, explicit assumptions/constraints/outcomes
with uncertainty classes, simulated-state isolation (production never
mutated), frozen evaluated versions and reproducibility hashes. Golden
example: `models/scenarios/customer-platform-replacement.yaml`. Concept doc:
[`docs/concepts/scenario.md`](../docs/concepts/scenario.md). Phases 2–7
(impact engine, decision intelligence, DMM integration, simulation adapters,
agentic generation, digital-twin foundation) are queued.

Full rationale: [`docs/runtime-architecture.md`](../docs/runtime-architecture.md).
Change request: [`change-requests/CR-009.md`](../change-requests/CR-009.md).
