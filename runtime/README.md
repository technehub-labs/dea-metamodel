# OpenDEA Runtime — CR-9 Reference Implementation

> **Status:** CR-9.1 (Runtime Foundation) + CR-9.2 (Knowledge Graph / Provenance) + CR-9.3 (Semantic Reasoning) + CR-9.4 (Temporal & Event Runtime) implemented · CR-9.5…CR-9.10 queued
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

## What exists today

| Component | Path | CR-9 section |
|---|---|---|
| Canonical graph model (Node/Edge, first-class edge metadata) | `runtime/graph/base.py` | §6 (CR-9E) |
| `GraphStore` — vendor-independent graph interface | `runtime/graph/base.py` | §5 (CR-9D) |
| `InMemoryGraphStore` — reference implementation | `runtime/graph/memory.py` | §75 (CR-9BV) |
| Canonical model loader (validate → atomic load) | `runtime/model/loader.py` | §73 (CR-9BT.2/.3), §12 (CR-9K) |
| Canonical identity helpers (CR-8 §7) | `runtime/model/identity.py` | §14 (CR-9M prerequisite) |
| `RuntimeService` — entity/relationship CRUD with registry validation | `runtime/api/service.py` | §74 Phase 1 (CR-9BU) |
| `ProvenanceService` — Assertion / Evidence / Source graph and `why()` chain | `runtime/provenance/` | §16–§17 (CR-9O/P), §21/§56 (CR-9T/BC) |
| `RuleRegistry` + `ReasoningEngine` — governed rules, levelled inference, explainability | `runtime/reasoning/` | §18–§21 (CR-9Q/R/S/T) |
| Vendor-independent contract suite | `tests/runtime/test_graphstore_contract.py` | §91 (CR-9CL seed) |
| `Snapshot` + `diff_snapshots` + `as_of` + `EventLog` — bitemporal queries, events, drift | `runtime/temporal/` | §7–§9 (CR-9F/G/H/I), §56 (CR-9BI/BD) |
| Runtime test suite (135 tests: graph, loader, CRUD, provenance, reasoning, scenario, impact, decision, temporal, interop) | `tests/runtime/` | §94 (CR-9CO) |

## Usage

```python
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.api import RuntimeService
from runtime.provenance import AssertionStatus, ProvenanceService

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

# CR-9.2 provenance graph: claims never mutate their subject
prov = ProvenanceService(store)
prov.register_source("src.cmdb", "Enterprise CMDB", system="ServiceNow")
prov.register_evidence("ev.inventory", "Application Inventory", confidence=0.9)
prov.assert_fact("assertion.cs-maturity", "cap.customer-service",
                 {"maturity": 2.7}, asserted_by="architect-42",
                 status=AssertionStatus.PROPOSED, confidence=0.92,
                 evidence=["ev.inventory"], source="src.cmdb")
prov.why("cap.customer-service")   # Conclusion → Assertion → Evidence → Source
```

## Design principles enforced in code

1. **Validation before the graph (CR-9K).** Nothing enters the store without
   passing the CR-8 reference validator. The loader *uses*
   `tools/opendea_validate.py` — it never re-implements rules.
2. **The graph is the runtime semantic representation, not a visualization
   structure (CR-9C).** Edges are first-class and carry provenance, temporal
   validity, lifecycle status and properties (CR-9E).
3. **Model ≠ runtime state ≠ assertion ≠ evidence ≠ inference (CR-9B).** These
   are distinct graph citizens: entities/relationships carry the model;
   `ProvenanceService` records claims as Assertion nodes, support as Evidence
   nodes and origins as EvidenceSource nodes — nothing collapses them.
4. **No silent inference (CR-9CQ).** `GraphStore.infer()` raises
   `InferenceUnavailable` — reasoning lands in CR-9.3 and must always carry
   provenance and explicit state transitions. Assertions cannot be created
   `approved`; approval is an explicit, audited transition.
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
| CR-9.2 | Knowledge Graph — canonical graph representation and provenance | **Implemented** |
| CR-9.3 | Semantic Reasoning — rules, inference, explainability (CR-9Q/R/S/T) | **Implemented** |
| CR-9.4 | Temporal & Event Runtime — bitemporal truth, events, snapshots, drift (CR-9F/G/H/I) | **Implemented** |
| CR-9.4 | Temporal & Event Runtime — events, snapshots, bitemporal queries (CR-9F/G/H/I) | Proposed |
| CR-9.5 | Integration Framework — adapters, mapping, identity resolution (CR-9J…O) | Proposed |
| CR-9.6 | Assessment Runtime — DMM execution (CR-9X/Y) | Proposed |
| CR-9.7 | Decision & Impact Engine (CR-9Z…AG) | Proposed |
| CR-9.8 | Agent Runtime — discovery, authority, policy, audit (CR-9AH…AR) | Proposed |
| CR-9.9 | OpenDEA Explorer — viewer decoupled, API-driven (CR-9BX…CB) | Proposed |
| CR-9.10 | Conformance & Interoperability Release — golden graphs, interop suite (CR-9CL…CP) | Proposed |

## CR-10 — Scenario & Decision Intelligence (Phases 1–3 implemented)

`runtime/scenario/` adds the CR-10 Phase 1 scenario foundation on top of the
CR-9 graph: first-class scenarios referencing immutable baselines, an explicit
eleven-operation delta vocabulary, explicit assumptions/constraints/outcomes
with uncertainty classes, simulated-state isolation (production never
mutated), frozen evaluated versions and reproducibility hashes.

`runtime/scenario/impact.py` adds Phase 2: impact graphs with direct/indirect
dependency paths, change analysis over every scenario delta, architecture
delta between baseline and simulated state, and explicit impact valence —
affected never automatically means negative (CR-10G/H).

`runtime/scenario/decision.py` adds Phase 3: semantic metrics, explicit
criteria and weights, decomposable scenario scores, deterministic comparison
and ranking, and explainable recommendations that remain decision support —
never approved decisions (CR-10F/J/M/N/AI/AL). Golden example:
`models/scenarios/customer-platform-replacement.yaml`. Concept doc:
[`docs/concepts/scenario.md`](../docs/concepts/scenario.md). Phases 4–7
(DMM integration, simulation adapters, agentic generation, digital-twin
foundation) are queued.

## CR-11 — Interoperability & Federation (Phases 1–2 implemented)

`runtime/interoperability/` adds the CR-11 Phase 1 semantic interoperability
foundation: first-class ExternalSystem / IntegrationAdapter (connector ≠
adapter) / SemanticMapping (relationship, confidence, lossiness, governed and
versioned) / ExternalIdentifier (correlated, never adopted) / Exchange
envelope, plus namespaced Extensions that never touch the Core (ADR-013).

`runtime/interoperability/identity.py` adds Phase 2: EntityResolution with
thresholded exact/candidate matching, the full reconciliation-state vocabulary,
KnowledgeConflict preservation, property-specific AuthorityPolicy and governed
conflict resolution. Merges require explicit approval; external ids remain
correlated links and are never adopted as canonical identity. Docs:
[`docs/interoperability/`](../docs/interoperability/overview.md), especially
[`identity.md`](../docs/interoperability/identity.md). Phases 3–8 (exchange
schemas, provenance, reference mappings, events, federation, conformance) are
queued.

Full rationale: [`docs/runtime-architecture.md`](../docs/runtime-architecture.md).
Change requests: [`change-requests/CR-009.md`](../change-requests/CR-009.md) ·
[`CR-010`](../change-requests/CR-010.md) ·
[`CR-011`](../change-requests/CR-011.md).
