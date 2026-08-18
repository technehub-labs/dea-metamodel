# Federation — OpenDEA Does Not Have to Own Every Fact

> **KB note — federation is the most-misnamed feature in
> enterprise interop.** A "federated knowledge graph" that copies
> every fact from every source is a data warehouse with extra
> steps. CR-11's federation is a *query and reasoning* boundary,
> not a replication boundary. Source: CR-11AH/AI/AJ/AK/BB/BC.
> Companion notes: [overview.md](overview.md), [architecture.md](architecture.md),
> [identity.md](identity.md), [mappings.md](mappings.md),
> [events.md](events.md), [security.md](security.md).

## 1. Federated knowledge (CR-11AH)

OpenDEA need not own every fact it reasons over. The canonical
metamodel stays small; the federated view across Sources is what
makes the *enterprise knowledge graph* answer real questions. The
CR §AH diagram, verbatim:

```
                       ┌──────────────┐
                       │   OpenDEA    │
                       │  (canonical) │
                       └──────┬───────┘
                              │ semantic
                              │ contracts
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼─────┐         ┌─────▼────┐          ┌─────▼────┐
   │  EA Repo │         │   CMDB   │          │   GRC    │
   │  (Arch…) │         │ (Service │          │ (Archer) │
   │          │         │   Now)   │          │          │
   └──────────┘         └──────────┘          └──────────┘
```

Each Source remains the authority for its own facts. OpenDEA is the
*joint* across them.

## 2. Entity locality (CR-11AI)

Every entity has a *locality* — where the canonical truth lives.

| Locality | Meaning | When to use |
|---|---|---|
| `LOCAL` | Authoritative in OpenDEA itself. | Core concepts, assessments, scenarios, decisions. |
| `FEDERATED` | Not stored in OpenDEA; resolved by live query. | Real-time operational facts (e.g. "is app X healthy *right now*?"). |
| `IMPORTED` | A snapshot in OpenDEA, refreshed on a schedule. | Periodic reference data (org chart, asset inventory). |
| `DERIVED` | Computed in OpenDEA from other entities; not stored in a Source. | Aggregations, maturity scores, scenario results. |
| `VIRTUAL` | A view assembled on demand from multiple federated sources. | Cross-source questions that have no single home. |

## 3. Query federation pipeline (CR-11AJ)

OpenDEA answers cross-Source questions by walking a pipeline. A
query that cannot be expressed as a pipeline needs governance, not
more code.

```
   OpenDEA query
         │
         ▼
   (1) Determine source(s)        — which ExternalSystem(s) can answer?
         │
         ▼
   (2) Route to Adapter(s)        — translate canonical → source query
         │
         ▼
   (3) Execute at source(s)       — call via Connector
         │
         ▼
   (4) Normalise                  — apply inverse Mapping, validate shape
         │
         ▼
   (5) Compose semantic result    — re-attach canonical ids, authority, conflicts
         │
         ▼
   OpenDEA semantic answer
```

### Worked example: "Applications supporting Capability X that are currently operational"

1. Planner sees `Application` (local), `operational status` (often CMDB-owned), `supports Capability` (EA-owned).
2. Routes to the CMDB Adapter for status and the EA Adapter for capability support, then composes.
3. Both Sources are queried with their own idioms.
4. Results are normalised through the relevant Mappings ([mappings.md §4](mappings.md)) and CMDB status transformation.
5. Result: canonical `Application` ids with provenance, confidence, and a `KnowledgeConflict` row if CMDB and EA disagree on "operational".

## 4. The 5-phase federation boundary (CR-11AK)

CR-11 deliberately scopes what it builds. It does **not** build a
universal federation engine.

| Phase | What OpenDEA does | What OpenDEA deliberately does NOT do |
|---|---|---|
| **1. Import / Export** | Batch and scheduled bulk movement via `IMPORT`/`EXPORT` capabilities. | Replace the Source. |
| **2. Incremental sync** | Cursor-based incremental updates. | Real-time change-data-capture for every Source. |
| **3. Event integration** | Receive and emit events (see [events.md](events.md)). | Build a Source's event bus. |
| **4. Federated query** | Live `QUERY`-capable adapters, normalised results, authority applied. | Cache or replicate transparently. |
| **5. Distributed reasoning** | Cross-source reasoning with provenance, conflict preservation, declared authority. | Hide the fact that knowledge is distributed. |

The phases are *additive*. A deployment may live at Phase 1 for years
before it has a business need for Phase 4. The discipline is to ship
the lower phases honestly, not to skip ahead and call it federation.

## 5. External deletion discipline (CR-11BB)

> **CR-11BB: when a Source deletes a record, OpenDEA MUST mark
> `sourceState=deleted`; it MUST NOT auto-destroy historical
> knowledge.** This is essential for temporal reasoning.

The temptation is to mirror the Source: when ServiceNow deletes a CI,
delete the canonical entity. The discipline is the opposite: the
canonical entity is historical knowledge; the *Source state* is one
observation of it.

| Field | Purpose |
|---|---|
| `id` | The historical entity id. |
| `sourceState` | `active` / `deleted` / `merged` / `retired`. |
| `deletionObservedAt` | timestamp | When a Source first reported deletion. |
| `deletionSource` | ref | Which Source reported the deletion. |
| `historicalFacts` | preserved | All previous observations, mappings, relationships remain. |
| `visibility` | enum | `visible` / `quarantined` / `archived` (per [security.md](security.md)). |

A scenario asking "what applications did we have on 2024-12-31?"
must still return a record that was deleted in 2025-03. A federated
graph that forgets deletion forgets the past.

## 6. Temporal interoperability (CR-11BC)

Five temporal fields, **none of which are interchangeable**:

| Field | Meaning | Set by |
|---|---|---|
| `effectiveAt` | When the fact is *true in the world* (e.g. the contract started 2024-01-01). | Authoritative Source. |
| `observedAt` | When the fact was *observed* (e.g. the agent saw the service healthy at 14:03:12). | Observing system. |
| `receivedAt` | When OpenDEA *received* the observation (e.g. the event landed 14:03:14). | OpenDEA integration layer. |
| `validFrom` | The start of the *canonical* belief window. | OpenDEA, on import. |
| `validTo` | The end of the *canonical* belief window. | OpenDEA, on update or retirement. |

### The Jan 1 vs Jan 5 example (CR-11BC)

A control is `EFFECTIVE` from `2024-01-01` (`effectiveAt`). An
assessment on `2024-01-05` observes `COMPLIANT` (`observedAt`). The
event reaches OpenDEA at `2024-01-05T09:14:00Z` (`receivedAt`); the
canonical belief spans `validFrom=2024-01-05T09:14:00Z` to
`validTo=∞` until contradicted.

Conflating these — e.g. using `effectiveAt` as `observedAt`, or
`receivedAt` as `validFrom` — is the most common temporal bug in
interop. CR-11BC names the five fields separately so the bug is
*visible* in the schema.
