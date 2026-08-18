# Runtime, Knowledge Graph & Interoperability — CR-9 Architecture Note

> KB note for the OpenDEA runtime programme. Distils the ideas, decisions and
> principles of [CR-9](../change-requests/CR-009.md) into the reasoning behind
> the code, and tracks what is implemented vs deferred.
> Companion notes: [specification-and-conformance.md](specification-and-conformance.md) (CR-8),
> [governance-agentic](.), [temporal](.) (CR-6/CR-7).

## 1. Strategic intent — from specification to substrate

CR-1…CR-7 built the semantic foundations; CR-8 froze them into an
independently implementable specification. CR-9 turns that specification into
an **executable enterprise semantic substrate**: ingestion, graph construction,
querying, reasoning, assessment, decision support, agent interaction and
continuous synchronization with enterprise systems.

The architectural proposition (CR-9 §1): OpenDEA is a **semantic operating
layer for enterprise architecture — not another architecture repository**. The
test of every runtime decision is whether it strengthens the closed loop:

```
Observe → Model → Assess → Reason → Decide → Act → Observe
```

A repository stores the loop's artifacts; a runtime *executes* the loop.

**Design discipline (CR-9 §101): do not overbuild the runtime.** The CR-8
semantic contract remains authoritative. The runtime supplies *interchangeable
implementations* of graph, inference, integration, assessment and agentic
services. This separation is what lets OpenDEA become an ecosystem instead of
coupling to the current web viewer or a particular technology stack.

## 2. The runtime architecture (CR-9A)

Six layers, each with a single responsibility; higher layers depend only on
the interfaces of the layer below:

| Layer | Responsibility | Milestone |
|---|---|---|
| API / Query / Agent Interface | Canonical surface for humans, services and agents (CR-9AU/CC) | CR-9.7/9.8 |
| Semantic Services | Validation, reasoning, assessment, decision, inference | CR-9.3/9.6/9.7 |
| Knowledge Graph | Entities, relationships, assertions, provenance — the *runtime semantic representation* (CR-9C), not a visualization structure | CR-9.1/9.2 |
| Semantic Registry | Core, profiles, schemas, rules, ontologies — the CR-8 artifacts, loaded, never copied | CR-9.1 |
| Integration / Ingestion | APIs, events, files, databases, SaaS, agents (CR-9J) | CR-9.5 |
| Enterprise Systems | Systems of record; the graph federates rather than absorbs them (CR-9BN) | — |

## 3. Model vs runtime state — the distinction that must never collapse (CR-9B)

Five kinds of knowledge, five distinct representations:

| Kind | Question | Representation in the runtime |
|---|---|---|
| Model | What is the enterprise understood to be? | Node/Edge identity + type + properties |
| Runtime state | What is currently observed? | `assertion.status: observed`, `observed_at`, freshness metadata (CR-9AZ) |
| Assertion | What does someone/something claim? | Assertion block: `asserted_by`, `confidence`, `status` (CR-9O: Proposed→Verified→Approved / Rejected / Superseded / Disputed) |
| Evidence | What supports the claim? | Evidence nodes + `supportedBy` edges — an *evidence graph*, not attachments (CR-9P) |
| Derived knowledge | What does the runtime infer? | `provenance.derived_from` + `derivation_rule`, with the reasoning level recorded (CR-9R/T) |

Competing assertions coexist without corrupting the graph; state transitions —
never overwrites — resolve them.

## 4. The graph abstraction (CR-9D/E)

**Vendor independence is a conformance concern, not a preference.** All
semantic services program against the `GraphStore` interface
(`createEntity / updateEntity / deleteEntity / createRelationship / query /
traverse / findPath / infer / transaction`). Neo4j, Neptune, ArangoDB,
PostgreSQL+graph, RDF triplestores and the in-memory reference store are
interchangeable. CR-9CL runtime conformance is demonstrated by passing the
vendor-independent contract suite (`tests/runtime/test_graphstore_contract.py`) —
to conform a new store, subclass the contract and supply a fixture.

**Edges are first-class (CR-9E).** A relationship is not a bare source→target
pair: it carries provenance (`assertedBy`, `sourceSystem`), temporal validity
(`validFrom/validTo`), lifecycle status and arbitrary properties (e.g.
`confidence: 0.94`). This is what makes the graph substantially more useful
than a simple node-arc structure — and what the CR-8 envelope schema already
serializes.

## 5. Time (CR-9F/G)

CR-6 introduced the clocks; CR-9 operationalizes them.

- **Foundation (implemented):** edges carry `valid_from/valid_to` + lifecycle
  status; traversal and neighbour queries accept `at=` — "what is true now /
  was true last year / is expected next year" is answerable today
  (`test_provenance_temporal.py::test_what_is_true_now`). A *planned* edge is
  never read as a current edge (CR-6 §22).
- **CR-9.4 (deferred):** full bitemporal semantics — valid time + transaction
  time — so the system can distinguish "the architecture changed in January"
  from "we learned about it in August" (CR-9G). This is the audit/governance
  backbone. Plus the event model (CR-9H), event-driven synchronization
  (CR-9I), snapshots and `diff(snapshotA, snapshotB)` (CR-9BI).

## 6. Integration principles (CR-9J…O) — deferred to CR-9.5, decided now

1. **No direct core-graph manipulation (CR-9K).** Every integration flows
   Source Schema → Source Mapping → OpenDEA Semantic Model → Validation →
   Graph. Mappings are explicit, versioned, machine-readable (CR-9L:
   `Salesforce.Account → OpenDEA.Organization`).
2. **Identity resolution is a service, not a side effect (CR-9M/N).** Exact,
   identifier, semantic and probabilistic matching produce a *verdict* — same /
   related / different / unknown — with `matchScore`, `matchingMethod`,
   `evidence`, `reviewRequired`, `approvedBy`. **Never automatically merge
   uncertain identities.** This matters doubly when AI performs the matching.
3. **Federation over centralization (CR-9BN/BO).** Entities may be local,
   federated, cached or external references (`externalUri/externalId/
   sourceSystem`). Sensitive data, high-volume telemetry and data sovereignty
   stay in source systems.
4. **Consistency is declared per source (CR-9BQ):** strong / near-real-time /
   eventual / periodic / manual. Cached knowledge never silently becomes
   authoritative (CR-9BR).

## 7. Reasoning principles (CR-9Q…T) — deferred to CR-9.3, decided now

- **Reasoning is levelled (CR-9R):** 1 Deterministic → 2 Ontological →
  3 Graph → 4 Probabilistic → 5 Generative. Every derived result records its
  level. Levels are never blended.
- **Rules are first-class artifacts (CR-9S):** versioned, enabled/disabled,
  profile-scoped, testable, traceable (`DEA-GOV-001` pattern).
- **Every inference answers "Why?" (CR-9T):** conclusion → rule applied →
  supporting assertions → confidence. This is the foundation of the viewer's
  "Why?" navigation (CR-9BZ) and of AI-assisted EA credibility.

## 8. The two security invariants — enforced from the foundation

**CR-9CQ — No silent inference.** The runtime never converts inferred
knowledge into authoritative fact without an explicit state transition
(Observed / Inferred / Proposed / Approved stay distinct). In CR-9.1 this is
structural: `infer()` raises `InferenceUnavailable`, and a test proves loaded
graphs contain exactly the edges the model declared — nothing derived
materializes silently.

**CR-9CR — No autonomous mutation by default.** Agents are read-only by
default; mutation rights arrive only through explicit authority, policy, scope
and approval. In CR-9.1 there is simply no agent write path. Later milestones
add the full chain: Agent → Role → Authority → Policy → Scope → Action
(CR-9AJ), a policy decision point returning ALLOW / DENY / ESCALATE (CR-9AK),
policy-driven human-in-the-loop thresholds (CR-9AL — never hard-coded), and
complete agent action audit (CR-9AM/CI, including model/version and
prompt/context *references* — not raw prompts in the graph).

## 9. Trust and freshness (CR-9AY…BC) — design commitments

- **Data freshness (CR-9AZ):** every externally sourced entity carries
  `lastObserved / lastSynced / freshnessPolicy / stalenessStatus`. "This
  conclusion rests on 17-day-old data" is a first-class warning, not a
  footnote.
- **Confidence is multi-dimensional (CR-9BB):** evidence confidence, identity
  confidence, inference confidence, data quality and source authority are
  distinct axes — a 0.92 assertion from a low-authority source is not a 0.90
  assertion from an authoritative one.
- **Provenance chain (CR-9BC):** Conclusion → Inference → Assertions →
  Evidence → Source Systems. Explainable enterprise intelligence.
- **Architecture observability (CR-9BD/BE):** drift — architecture, policy,
  maturity, dependency, technology, agent behaviour, governance — is detected
  by comparing approved vs observed state, then risk-assessed and decided.
- **Baselines and scenarios (CR-9BG/BJ):** Current / Approved / Target /
  Planned / Simulated states coexist; scenarios never touch the production
  graph (the CR-10 digital-twin foundation, with the CR-9AT discipline:
  architecture model ≠ operational model ≠ observed state ≠ simulation ≠
  digital twin).

## 10. Agentic architecture (CR-9AH…AR) — deferred to CR-9.8, decided now

- Agents interact through a semantic interface: `discover / query / assess /
  reason / recommend / requestDecision / execute / report` — each governed by
  identity, authority, scope, policy, risk, approval, audit (CR-9AH).
- **Context construction beats context dumping (CR-9CD/CE):** the runtime
  supplies the minimal, policy-filtered, authority-filtered subgraph relevant
  to the task — performance, security, explainability and LLM accuracy all
  improve.
- **Semantic access control (CR-9CF/CG):** policy operates at entity /
  relationship / *property* level (an agent may see a Capability but not its
  financial property), via a Security/Governance profile — never polluting Core.
- **Agent ↔ Tool ↔ Capability (CR-9AN/AO):** a semantic tool registry lets the
  graph answer "which agents can act on this capability?" (CR-9CB) and "which
  capabilities are agentization opportunities?" (CR-9AP — an
  `AgentizationOpportunity`, never an auto-created agent).
- **Orchestration stays outside Core (CR-9AQ):** the orchestrator consumes
  OpenDEA; OpenDEA supplies enterprise semantic context and records
  actions/results.

## 11. Economics and decisions (CR-9AD…AF, BK, BL)

Decision support is distinguished from decision execution — the latter
requires explicit authorization (CR-9AD). Decisions follow a lifecycle
(Proposed → UnderReview → Approved → Executed → Observed → Evaluated →
Closed, plus Rejected/Deferred/Superseded/Revoked) and link to change:
Decision → Change → Initiative → Work → Implementation → ObservedOutcome
(CR-9AF) — closing the transformation loop (CR-9AG). Cost/benefit/value
attributes live in a profile, not Core (CR-9BK). Major decisions carry an
evidence matrix across strategic, architecture, financial, risk, capability,
technology, governance and operational dimensions (CR-9BL).

## 12. Quality engineering (CR-9CJ…CP)

- **Performance targets are engineering targets, not semantic requirements
  (CR-9CJ):** validate 10k entities < 2 s; entity query < 200 ms; traversal
  < 500 ms; impact analysis < 2 s — benchmark before treating as SLAs.
- **Scale testing (CR-9CK):** synthetic 1K/10K/100K/1M-entity models expose
  whether the conceptual model is computationally practical.
- **Runtime conformance (CR-9CL):** Core, Profile, API, Query, Validation,
  Provenance, Security — enabling multiple independent implementations.
- **Golden graphs (CR-9CN):** like CR-8 golden models but for runtime state —
  expected node/edge/assertion counts and traversal results as regression
  artifacts. `GraphStore.stats()` is the seed.
- **CI quality gate (CR-9CP):** schema, golden models, semantic, runtime,
  mapping and security tests all gate merges.

## 13. Programme state

| Milestone | Deliverable | Status |
|---|---|---|
| **CR-9.1 Runtime Foundation** | `runtime/` package (GraphStore ABC + in-memory reference store, model loader, identity, RuntimeService), 49-test runtime suite wired into CI | **Implemented** |
| CR-9.2 Knowledge Graph | Canonical graph representation + provenance graph (CR-9O/P) | Proposed |
| CR-9.3 Semantic Reasoning | Rule registry, levelled inference, explainability (CR-9Q…T) | Proposed |
| CR-9.4 Temporal & Event Runtime | Bitemporal semantics, events, snapshots, drift (CR-9F…I, BD…BI) | Proposed |
| CR-9.5 Integration Framework | Adapters, mapping spec, identity resolution (CR-9J…O) | Proposed |
| CR-9.6 Assessment Runtime | Executable CR-5 incl. DMM runtime (CR-9X/Y) | Proposed |
| CR-9.7 Decision & Impact Engine | Impact/dependency analysis, decision lifecycle, change linkage (CR-9Z…AG) | Proposed |
| CR-9.8 Agent Runtime | Discovery, authorization, policy, audit, tool registry (CR-9AH…AR) | Proposed |
| CR-9.9 OpenDEA Explorer | Viewer → Explorer: Explore/Assess/Trace/Compare/Query/Simulate/Govern, API-driven (CR-9BX…CB) | Proposed |
| CR-9.10 Conformance & Interop Release | Golden graphs, interop suite, performance suite, reference runtime release (CR-9CL…CP) | Proposed |

**Deferred explicitly by CR-9 itself:** full enterprise digital twin (CR-10
foundation only, CR-9AS/AT), scenario engine as a major capability (CR-9BJ →
CR-10), cost/value semantics beyond profile placeholders (CR-9BK).

## 14. Definition of Done — CR-9.1 contribution

CR-9 §100 acceptance criteria, with CR-9.1 status:

- [x] OpenDEA models can be loaded into a runtime — `runtime/model/loader.py`, 7 golden models load
- [x] Canonical entities and relationships are preserved — verbatim-envelope test
- [x] Graph queries work independently of graph vendor — `GraphStore` ABC + contract suite
- [x] Provenance is retained — assertion/source/provenance fields round-trip
- [x] Temporal state is supported — `valid_from/valid_to` + `at=` queries (bitemporal → CR-9.4)
- [x] Runtime APIs are defined — programmatic service layer (REST bindings → CR-9.7)
- [ ] External sources can be mapped into OpenDEA — CR-9.5
- [ ] Entity identity can be resolved safely — CR-9.5
- [ ] Rules can generate derived assertions — CR-9.3
- [ ] Every inference is explainable — CR-9.3
- [ ] DMM assessments can execute against the model — CR-9.6
- [ ] Impact analysis can traverse dependencies — CR-9.7 (traversal primitives ready)
- [ ] Decisions can reference evidence and architecture — CR-9.7
- [ ] Agent authority can be evaluated — CR-9.8
- [ ] Agent actions are auditable — CR-9.8
- [ ] Viewer consumes runtime APIs rather than defining semantics — CR-9.9
- [ ] Golden graphs pass — CR-9.10 (seed: `stats()` + contract suite)
- [ ] Interoperability tests pass — CR-9.10
- [ ] Runtime security is enforced — CR-9.8 (invariants CR-9CQ/CR active now)
- [ ] Stale data is detectable — CR-9.4/9.5
- [x] No inferred fact silently becomes authoritative — structural, test-enforced
