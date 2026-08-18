# Events — The Continuous-Intelligence Pipeline

> **KB note — events are how the canonical graph stays in step with
> the world between scheduled imports.** CR-11's event model is
> aligned with CR-9's runtime event model (landing in CR-9.4); the
> two share a canonical envelope so that an OpenDEA-native event and
> an external-system event are not two different things. Source:
> CR-11AF/AG, cross-referenced with CR-9H/I. Companion notes:
> [overview.md](overview.md), [architecture.md](architecture.md),
> [identity.md](identity.md), [mappings.md](mappings.md),
> [federation.md](federation.md), [security.md](security.md).

## 1. The canonical event envelope (CR-11AF)

Every event — internal or external — uses the same shape. This is
deliberate: it lets an `EVENT`-capable Adapter (see
[architecture.md §4](architecture.md)) translate *into* this envelope
and lets every downstream consumer (rules, assessments, agents)
reason over one type.

| Field | Type | Purpose |
|---|---|---|
| `id` | IRI | Globally unique event id. |
| `type` | enum (see §2) | What happened. |
| `subject` | ref | The canonical entity (or external entity reference) the event is about. |
| `occurredAt` | timestamp | When the event *occurred in the world* (aligns with `effectiveAt` — see [federation.md §6](federation.md)). |
| `observedAt` | timestamp | When the event was *observed* (aligns with `observedAt`). |
| `source` | ref → `ExternalSystem` (or internal) | Who reported it. |
| `version` | string | Schema/envelope version. |
| `payload` | structured | Event-specific body, validated against the event-type schema. |
| `correlationId` | string (optional) | For tracing a chain of derived events. |
| `causationId` | ref (optional) | For lineage: this event was *caused by* that one. |

> **`occurredAt` vs `observedAt` aligns with CR-11BC temporal
> interoperability.** A CMDB event may *occur* at 14:03:00 and be
> *observed* by the event bus at 14:03:14. The gap is information,
> not noise.

## 2. Event types (CR-11AG)

The canonical set covers the full enterprise-knowledge lifecycle:

| Type | Meaning |
|---|---|
| `ENTITY_CREATED` | A new canonical entity was created (from import, observation, or human input). |
| `ENTITY_CHANGED` | A property of an existing entity was updated, with provenance. |
| `ENTITY_DELETED` | An entity was marked `sourceState=deleted` per [federation.md §5](federation.md) — never a hard destroy. |
| `RELATIONSHIP_CHANGED` | A relationship was created, updated, or ended. |
| `OBSERVATION_RECEIVED` | A new `Observation` was recorded (telemetry, agent report, audit finding). |
| `ASSESSMENT_UPDATED` | A maturity, risk, or compliance assessment's score or status changed. |
| `SCENARIO_CREATED` | A scenario was authored (CR-10). |
| `DECISION_APPROVED` | A decision was approved through governance (CR-7). |

The set is **small on purpose**. Vendor-specific event types are
normalised at the Adapter boundary; the canonical graph only speaks
canonical types.

## 3. The event-driven pipeline (CR-11AG)

This is the foundation of *continuous enterprise intelligence* — the
end state the CR-9/10/11 sequence is building toward:

```
   External Event
         │
         ▼
   Event Adapter            ← CR-11: Event Adapter, source-specific
         │                    (ServiceNow webhook, Kafka topic, MCP tool, …)
         ▼
   OpenDEA Event            ← CR-11AF: canonical envelope
         │
         ▼
   Knowledge Update         ← CR-11K: reconciliation, identity, mapping
         │
         ▼
   Rules                    ← CR-7: governance rules
         │
         ▼
   Assessment               ← CR-10: maturity, risk, compliance
         │
         ▼
   Agent / Decision         ← CR-7 + CR-9: notify an agent, or escalate to a decision
```

The pipeline is **idempotent and replayable**. An `Event Adapter`
that receives the same event twice produces the same outcome; a
replay of the last 24 hours reconstructs the same canonical state.

## 4. Cross-reference: CR-9 runtime event model (CR-9H/I)

The runtime event model lands in **CR-9.4**. CR-11 does not redefine
it; CR-11's contribution is the *interop surface* (the Event Adapter
boundary) and the *normative alignment* with CR-9.

| Concern | Owner |
|---|---|
| Canonical envelope shape (id, type, occurredAt, observedAt, source, payload) | CR-9H, ratified by CR-11AF. |
| Event bus, persistence, replay | CR-9.4 (runtime). |
| External event ingestion, normalisation, ordering | CR-11AF/AG (interop). |
| Event-driven rule firing | CR-7 + CR-9.4. |
| Agent notification | CR-7 + CR-9.5. |

When CR-9.4 lands, an `EVENT`-capable Adapter (see
[architecture.md §4](architecture.md)) becomes a thin shim: it
validates the inbound payload, translates it into the canonical
envelope, and hands it to the runtime event bus.

## 5. CR-11 Phase 6 — where events land

CR-11's own delivery is phased (see [overview.md](overview.md) and
the CR-11 roadmap). Events are **Phase 6**: the last piece of the
interop surface to be hardened, because it depends on Mappings,
Identity, Authority, and Federation already being in place. An event
that cannot be reconciled, mapped, and authority-checked is just
faster noise.

The criterion for "Phase 6 complete" is not that all Sources emit
events; it is that the canonical graph can answer, in real time,
"what is true *right now*?" for any entity, with provenance, with
authority, and with conflicts preserved.
