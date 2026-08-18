# Interoperability Security, Error Model & Observability

> **KB note — interop is a major attack surface.** Every `Connector`
> is a network boundary, every `Adapter` is an untrusted input
> parser, every `Mapping` is a code-execution path, and every
> `Exchange` is a credential-handling moment. CR-11's security
> discipline is to assume all four are compromised until proven
> otherwise. Source: CR-11AY/AZ/BA/AW/AX, cross-referenced with
> CR-9AV. Companion notes: [overview.md](overview.md),
> [architecture.md](architecture.md), [identity.md](identity.md),
> [mappings.md](mappings.md), [federation.md](federation.md),
> [events.md](events.md).

## 1. The threat surface (CR-11AY)

Interop expands the OpenDEA security boundary from "the canonical
graph" to:

| Surface | Threat |
|---|---|
| **Inbound connectors** | Malformed payloads, injection, oversized responses, replay. |
| **Credentials for Sources** | Secret leakage, lateral movement, account compromise. |
| **Mappings / Transformations** | Code-execution paths; a malicious mapping is an arbitrary-code vector. |
| **Federated queries** | SSRF, exfiltration via crafted queries, query-cost DoS. |
| **Exports** | Data exfiltration, classification leakage. |
| **Event ingestion** | Event flood, event-ordering attacks, schema-confusion. |
| **Agent/MCP integrations** | Tool-injection, prompt-injection via payloads. |

CR-11's stance: **no trust by default**. Every layer is hardened
*and* every layer is observable, so that a breach is detected
quickly and traced to a specific source.

## 2. Core controls (CR-11AY/AZ)

| Control | Requirement |
|---|---|
| **OAuth2 / OIDC** | Outbound: client-credentials or auth-code. Inbound: bearer tokens validated against the configured issuer. |
| **TLS** | All interop traffic TLS 1.2+; certificate pinning for high-trust Sources. |
| **Credential isolation** | Credentials MUST live in a secret store (Vault, AWS Secrets Manager, K8s secrets). The metamodel and Adapters hold *references*, not values. |
| **Secret management** | Rotation supported; rotation MUST NOT require an OpenDEA schema change. |
| **Least privilege** | Outbound credentials scoped to the minimum Source permissions required (read-only where possible; write only with declared `AuthorityPolicy`). |
| **Tenant isolation** | Per-tenant credential scopes; per-tenant data classification enforcement at the API gateway. |
| **Audit logging** | Every Exchange, every credential use, every authority decision, every export — auditable, signed, retained per governance policy. |
| **Payload validation** | Schemas enforced on inbound and outbound; unknown fields rejected or quarantined, never silently dropped. |
| **Rate limiting** | Both inbound (per source) and outbound (per source) to prevent both abuse and runaway cost. |

> **CR-11AY: credentials MUST NEVER exist in the metamodel itself.**
> Not in a Mapping, not in a `Mapping.configSchema`, not in a
> transformation, not in a comment. The metamodel is shared;
> credentials are per-deployment.

## 3. Data classification propagates through everything (CR-11BA)

A `PUBLIC` record from a public source stays `PUBLIC` end-to-end. A
`RESTRICTED` record from a GRC tool stays `RESTRICTED` even after
federation, even after export. The classification is a *property of
the data*, not a property of the path it travelled.

| Classification | Examples | Default handling |
|---|---|---|
| `PUBLIC` | Published reference architectures, open DMM data. | No restriction. |
| `INTERNAL` | Most EA data, application inventory. | Authenticated OpenDEA users only. |
| `CONFIDENTIAL` | GRC findings, security control state, risk scores. | Tenant-scoped; access logged; export requires approval. |
| `RESTRICTED` | Personal data, M&A material, certain compliance evidence. | Field-level redaction by default; access on a per-entity basis with explicit approval. |

The classification flows through:

- **Federation**: a `RESTRICTED` Source value is never returned in a
  federated query to a user without `RESTRICTED` clearance, even if
  the answer is correct.
- **Export**: an export bundle MUST declare the highest
  classification it contains; bundles of mixed classification are
  split, not merged.
- **Agents**: an agent without `RESTRICTED` capability MUST NOT
  receive `RESTRICTED` data, even indirectly.

## 4. Export controls (CR-11BA)

| Visibility level | What is exported |
|---|---|
| `entity` | Whole canonical entities (with classification ceiling enforced). |
| `property` | Selected properties only (e.g. `name`, `owner` — never `compliance.controls` for a `CONFIDENTIAL` view). |
| `relationship` | Only relationships the consumer is authorised to see. |
| `scenario` | A scenario's inputs, results, and provenance. |
| `evidence` | The evidence chain backing a scenario or assessment. |

Every export carries: who requested it, who approved it (if
required), what was included, what was redacted, and a content hash
for downstream verification.

## 5. Integration error model (CR-11AW)

A failed record is a first-class outcome. CR-11AW's error model is
explicit that **records are never silently discarded**:

| Error | Meaning |
|---|---|
| `AUTHENTICATION_FAILED` | Credential invalid, expired, or revoked. Exchange aborted. |
| `AUTHORIZATION_FAILED` | Credential valid but lacks scope. Exchange aborted. |
| `RATE_LIMITED` | Source or OpenDEA rate limit hit; backoff and retry per policy. |
| `PAYLOAD_INVALID` | Inbound payload failed schema validation; record quarantined. |
| `MAPPING_NOT_FOUND` | No active Mapping covers a field; record quarantined with reason. |
| `TRANSFORMATION_FAILED` | Transformation threw; record quarantined, **never silently dropped**. |
| `IDENTITY_UNRESOLVED` | Could not reconcile the Source identifier; held for review. |
| `AUTHORITY_CONFLICT` | Disagreement between Sources; preserved as `KnowledgeConflict` (see [identity.md §4](identity.md)). |
| `PARTIAL_IMPORT` | Some records accepted, others quarantined; the Exchange is a *partial* success, not a failure. |
| `TEMPORAL_INVALID` | Timestamp outside acceptable bounds; record rejected. |

A `PARTIAL_IMPORT` is still an import. The summary MUST distinguish
"all records failed" from "some records failed" — both are common,
and the response posture is different.

## 6. Integration observability (CR-11AX)

Every Exchange produces a structured, queryable record. The CR-11AX
discipline is: if you cannot see it, you cannot govern it.

| Metric | Meaning |
|---|---|
| `recordsReceived` | Total inbound records, including rejected. |
| `recordsAccepted` | Successfully mapped and written to canonical. |
| `recordsRejected` | Hard-failed (auth, schema, temporal). |
| `recordsTransformed` | Passed through a declared transformation. |
| `recordsConflicted` | Produced a `KnowledgeConflict`. |
| `recordsUnresolved` | Identity could not be reconciled; held for review. |
| `processingTime` | p50 / p95 / p99 latency. |
| `lastSuccessfulSync` | timestamp | The most recent full or partial success. |
| `errorBreakdown` | histogram by `error` code. |

These metrics feed the OpenDEA operational dashboard, the per-Source
health page, and the per-Mapping quality view (which surfaces
`recordsRejected` and `recordsConflicted` so a degraded mapping is
visible before a human notices).
