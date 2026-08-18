# Interoperability Architecture — Source, Adapter, Mapping, Exchange

> **KB note — CR-11 deliberately separates four concepts that
> interoperability designs routinely conflate.** Conflating them is the
> single most common reason enterprise interop projects fail: a
> "source" is treated as an "adapter", a "mapping" is buried in
> transport code, an "exchange" is mistaken for a "mapping". Source:
> CR-11A and CR-11D. Companion notes: [overview.md](overview.md),
> [identity.md](identity.md), [mappings.md](mappings.md),
> [federation.md](federation.md), [events.md](events.md),
> [security.md](security.md).

## 1. The four distinct concepts (CR-11A)

| # | Concept | What it is | What it is not |
|---|---|---|---|
| 1 | **Source** | The external system or artifact whose knowledge OpenDEA reasons over (ServiceNow CMDB, ArchiMate export, SAP GRC). | Not a transport mechanism. Not a schema. |
| 2 | **Adapter** | The technical access mechanism that knows how to talk to a Source, normalise its payloads, and present a canonical-shaped surface. | Not a Source. Not a Mapping. |
| 3 | **Mapping** | The semantic correspondence between a Source concept and an OpenDEA concept (ServiceNow `cmdb_ci_appl` ↔ `dea:Application`, with confidence and transformation). | Not a transport. Not a runtime import job. |
| 4 | **Exchange** | The actual transfer of data — an import run, a webhook receipt, a federated query — bound by an Adapter, driven by Mappings, over a Connector. | Not a Source. Not a Mapping. |

The four MUST be modelled independently. A change in a Source's
schema is an Adapter concern; a change in a Source's *meaning* is a
Mapping concern; a change in a Source's *transport* is a Connector
concern; a change in the run that pulls data is an Exchange concern.

## 2. Connector vs Adapter (CR-11D)

A **Connector** is pure transport. It knows how to move bytes and
nothing else. An **Adapter** is semantic integration — it knows what
the bytes *mean*.

| Connector (transport) | Examples |
|---|---|
| REST | `GET /api/now/table/cmdb_ci` |
| GraphQL | Shopify admin API |
| SQL | `SELECT * FROM cmdb_ci` over JDBC |
| SFTP | file drop polling |
| Kafka | topic subscription |
| Webhook | inbound HTTPS push |
| File | CSV, JSON, XML, XLSX drops |

**Adapter** examples: `ServiceNow → OpenDEA`, `ArchiMate → OpenDEA`,
`LeanIX → OpenDEA`, `DMM assessment → OpenDEA observation`.

The CR §D chain — verbatim:

```
   Source ──► Connector ──► Transport ──► Adapter ──► Mapping ──► OpenDEA
   (data)    (protocol)    (bytes)       (semantic)   (concept)   (canonical)
```

Transport alone makes the data move; semantic mapping makes the data
*mean something*. OpenDEA cares about Adapter and Mapping, not the
Connector, which is a commodity concern delegated to the runtime
(CR-9J).

## 3. ExternalSystem model (CR-11B)

`ExternalSystem` is the canonical record for a Source. It captures
identity, ownership, and integration posture — not schema or
semantics, which live in Mappings.

| Field | Type | Purpose |
|---|---|---|
| `id` | IRI | OpenDEA canonical id (`opendea:external:...`). |
| `name` | string | Human label. |
| `kind` | enum | `cmdb` / `ea_repo` / `itsm` / `grc` / `dmm` / `data_catalog` / `cloud` / `hr` / `agent_registry` / `other`. |
| `vendor` | string | E.g. `ServiceNow`, `Bizzdesign`. |
| `version` | string | Vendor release (e.g. `Vancouver`). |
| `owner` | ref | The person or team accountable for the system. |
| `environment` | enum | `production` / `staging` / `dev` / `sandbox`. |
| `tenantId` | string | For multi-tenant sources. |
| `dataClassification` | enum | `PUBLIC` / `INTERNAL` / `CONFIDENTIAL` / `RESTRICTED` (see [security.md](security.md)). |
| `description` | string | Markdown. |
| `lifecycle` | ref | Linked to the system lifecycle. |

## 4. IntegrationAdapter model (CR-11C)

`IntegrationAdapter` declares what an Adapter *can do*. A single
Source may have several Adapters (e.g. a CMDB may have one for
snapshot import, one for event streaming, one for federated query).

| Field | Purpose |
|---|---|
| `id`, `name`, `description` | Canonical identity. |
| `source` | ref → `ExternalSystem`. |
| `version` | Adapter implementation version. |
| `connectorType` | `rest` / `graphql` / `sql` / `sftp` / `kafka` / `webhook` / `file` / `custom`. |
| `capabilities` | set of capability flags (see below). |
| `configSchema` | ref | The schema describing what configuration values the Adapter accepts (endpoint, credentials ref name, polling interval, etc.). |
| `credentialRef` | ref | A pointer to a **secret-store entry** — never an inline value (see [security.md](security.md)). |
| `mappings` | set of refs | The Mappings this Adapter is permitted to apply. |
| `owner` | ref | Person/team accountable. |
| `status` | enum | `active` / `paused` / `deprecated` / `retired`. |

**Capabilities** (CR-11C). An Adapter declares which it supports:

| Capability | Meaning |
|---|---|
| `READ` | Pull data from the Source. |
| `WRITE` | Push canonical entities back to the Source. |
| `IMPORT` | Run a one-shot or scheduled import (creates/updates entities). |
| `EXPORT` | Run a one-shot or scheduled export (publishes scenarios, assessments, evidence). |
| `SYNC` | Bidirectional reconciliation against declared authority. |
| `EVENT` | Subscribe to Source events (webhook, Kafka). |
| `QUERY` | Live federated query — no local copy. |
| `BULK` | Optimised bulk endpoint, not per-record. |
| `STREAM` | Continuous streaming, not batch. |

## 5. Import modes (CR-11P)

| Mode | Behaviour | When to use |
|---|---|---|
| `FULL` | Replace the local view of the Source's data wholesale. | Rare; only when the Source is the single authority. |
| `INCREMENTAL` | Pull only what changed since the last cursor. | Default for snapshot sources. |
| `DELTA` | Compute the precise diff and apply it transactionally. | When the Source supports change-data-capture. |
| `OBSERVATION` | Never writes to canonical entities; only emits Observations. | Telemetry, agent reports, weak signals. |
| `ON_DEMAND` | Runs only when explicitly invoked. | Ad hoc analysis, audits. |

## 6. Synchronisation directions (CR-11Q)

| Direction | Meaning | Risk note |
|---|---|---|
| `INBOUND` | Source → OpenDEA only. | Safe baseline. |
| `OUTBOUND` | OpenDEA → Source only. | E.g. publishing a scenario back to ITSM. |
| `BIDIRECTIONAL` | Both ways. | **Requires declared authority per property** (see [identity.md](identity.md) CR-11R). Without it, sync oscillates or corrupts. |

## 7. API gateway boundary (CR-11AV)

| Path prefix | Owner | Purpose |
|---|---|---|
| `/api/opendea/*` | OpenDEA canonical API | Read/write the canonical graph, scenarios, assessments. |
| `/api/integration/*` | Integration runtime | Source/Adapter/Exchange management; **does not write the canonical graph directly** — it goes through Mapping + Reconciliation. |
| `/api/scenario/*` | Scenario engine (CR-10) | Scenario authoring, simulation, decisions. |
| `/api/assessment/*` | Assessment engine | Maturity, risk, compliance scoring. |

The boundary is the practical expression of the design principle:
canonical writes flow through `/api/opendea/*`; everything else is an
input that must be mapped, reconciled, and authorised first.
