# Identity, Reconciliation & Source Authority

> **KB note — interop without a discipline for *who is who* and *who
> is right* produces an enterprise knowledge graph that is internally
> consistent and externally wrong.** CR-11 splits this into two
> distinct problems: identity reconciliation (which record in the
> outside world is this canonical entity?) and source authority
> (when two sources disagree, which one wins for *this* property?).
> Source: CR-11I/J/K/L/M/N/R. Companion notes:
> [overview.md](overview.md), [architecture.md](architecture.md),
> [mappings.md](mappings.md), [federation.md](federation.md),
> [events.md](events.md), [security.md](security.md).

## 0. Phase 2 implementation status

`runtime/interoperability/identity.py` now implements the executable core of
this document:

| Concept | Runtime object / method |
|---|---|
| Entity reconciliation (CR-11J/K) | `EntityResolution`, `ResolutionCandidate`, `InteropRegistry.reconcile_external()` |
| Reconciliation states (CR-11K/L) | `ReconciliationState`: `UNMATCHED / CANDIDATE / MATCHED / MERGED / CONFLICTING / REJECTED` |
| Conflict preservation (CR-11L) | `KnowledgeConflict`, `ConflictValue`, `InteropRegistry.record_conflict()` |
| Property-specific authority (CR-11M/N) | `AuthorityPolicy`, `TieBreaker`, `InteropRegistry.register_authority_policy()` |
| Governed conflict resolution | `InteropRegistry.resolve_conflict()` — chooses via policy while preserving every losing value |
| No silent merge | `InteropRegistry.approve_resolution()` — explicit actor required; MERGED without approval is rejected |
| External ids never adopted | approved resolutions add an `ExternalIdentifier` link; the canonical entity id remains unchanged |

```python
resolution = registry.reconcile_external(
    "system.servicenow", "CI-009999",
    candidates=[ResolutionCandidate(entity="app.customer-platform", score=0.82)])
# CANDIDATE — review required; no merge, no canonical-id adoption

merged = registry.approve_resolution(
    resolution.id, entity="app.customer-platform",
    approved_by="ea-governance")
# MERGED — auditable, and the external id is preserved as a link
```

## 1. The canonical identity rule (CR-11I)

> **OpenDEA MUST NOT default an external system's identifier to the
> OpenDEA canonical identity.** The external identifier is an
> `ExternalIdentifier` — a *reference* — not a canonical `id`.

If a CMDB record's `sys_id` were taken as the OpenDEA `id`, the
canonical graph would inherit every rename, merge, and retire in the
CMDB, and the same real-world entity would accumulate dozens of
canonical ids across sources. Canonical identity is governed by CR-9
identity resolution, not by Source convenience.

## 2. ExternalIdentifier (CR-11J)

`ExternalIdentifier` is the bridge record. One canonical entity may
have many; an ExternalIdentifier belongs to exactly one.

| Field | Purpose |
|---|---|
| `id` | OpenDEA-internal id of the bridge record. |
| `system` | ref → `ExternalSystem`. Which Source. |
| `identifier` | The Source's own id (e.g. ServiceNow `sys_id`, ArchiMate element id). |
| `identifierType` | `primary` / `secondary` / `business_key` / `urn` / `uri` / `email` / `tag`. |
| `entity` | ref → OpenDEA entity. The canonical entity this id points to. |
| `validFrom`, `validTo` | When this bridge was true. |
| `sourceState` | `active` / `deleted` / `merged` / `retired` (see [federation.md](federation.md) CR-11BB). |
| `confidence` | float 0–1. How sure the reconciliation is. |

## 3. Entity reconciliation (CR-11K)

`EntityResolution` decides whether a record arriving from a Source is
*same as*, *related to*, or *brand new* relative to a canonical
entity. CR-9M/N establishes the verdict shape (`same` / `related` /
`different` / `unknown`, `matchScore`); CR-11K refines it for interop
— "is the record from `ServiceNow` referring to an entity we
already have from `Archi`?"

**Worked example.** An Application arrives from three sources:

| Source | Identifier | Name hint | Owner | Lifecycle |
|---|---|---|---|---|
| ServiceNow CMDB | `sys_id=ab12…` | "ClaimsPortal" | team-alpha | `operational` |
| LeanIX | `factSheet=987` | "Claims Portal" | team-alpha | `active` |
| AWS Config | `arn=…/claims-portal-prod` | "claims-portal" | (unowned) | `RUNNING` |

CR-11K reconciliation asks: same? Names agree, owner agrees, lifecycle
agrees — the verdict is `same` with high confidence. A new
`ExternalIdentifier` row is added for the AWS ARN. None of the three
Source ids is promoted to canonical; the canonical id is whatever
CR-9 identity resolution produced or assigned.

### Reconciliation states (CR-11L)

| State | Meaning | Action |
|---|---|---|
| `UNMATCHED` | No candidate found. | Create a new canonical entity and link all matching `ExternalIdentifier` rows. |
| `CANDIDATE` | One or more candidates, below auto-match threshold. | Queue for human review (or governance policy). |
| `MATCHED` | One clear candidate above threshold. | Link to existing canonical entity. |
| `MERGED` | Two candidates confirmed identical; consolidated. | Preserve audit trail of the merge. |
| `CONFLICTING` | Multiple candidates, all above threshold, mutually exclusive. | Reject auto-resolution; surface for governance. |
| `REJECTED` | Explicitly determined to be a different entity. | Link, but mark as `RELATED_TO` not `SAME_AS`. |

**CR-11L: never silently merge.** Every merge is auditable, every
conflict is preserved, every uncertain match is queued.

## 4. KnowledgeConflict (CR-11K cont.)

When two Sources disagree, the disagreement is a *first-class* model
object — not an exception, not a log line.

| Field | Purpose |
|---|---|
| `id` | Conflict record id. |
| `entity` | ref | Canonical entity in conflict. |
| `property` | ref | The property in dispute. |
| `sources` | Sources with competing values. |
| `values` | The competing (source, value, observedAt) tuples. |
| `status` | `open` / `resolved` / `deferred` / `overridden`. |
| `resolution` | ref | If resolved, the chosen value and the rule/authority that chose it. |
| `detectedAt` | When the conflict was first observed. |
| `resolvedAt` | When the conflict was closed. |

Conflicts are *preserved*, not auto-resolved. A system that auto-resolves
all conflicts on import is a system that has already lost information.

## 5. Source authority is property-specific (CR-11M)

> CR-11M calls property-specific authority *"one of the most
> important CR-11 concepts"*.

Authority is not a property of a Source; it is a property of a
**(Source, target property)** pair. The same Source may be the
authority for one property of an entity and *not* for another.

| Source | Property it is authoritative for | Why |
|---|---|---|
| **CMDB** (ServiceNow, BMC) | `lifecycle.state`, `hosting.platform`, operational `configuration` | Operational truth lives in the CMDB. |
| **EA repository** (Archi, LeanIX) | `archimateLayer`, `archimateAspect`, classification | Architecture classification is the EA repo's job. |
| **HR / IAM** (Workday, Okta) | `ownership.owner`, `ownership.steward` | People assignments are authoritative in HR. |
| **GRC** (Archer, SAP GRC) | `compliance.controls`, `risk.classification` | Compliance posture is GRC's job. |
| **DMM assessment** | `maturity.score` (per dimension) | Maturity is the assessment's claim. |
| **Agent registry** | `agent.capabilities`, `agent.toolContracts` | Capability claims are the agent's claim. |

This is the practical meaning of "the adapter absorbs external
complexity": the authority question is settled in OpenDEA, not
negotiated ad hoc in the import job.

### AuthorityPolicy (CR-11N)

`AuthorityPolicy` declares per-property weights. It is a first-class
governance object, not a config snippet.

| Field | Purpose |
|---|---|
| `id` | Policy id. |
| `scope` | ref | The entity type or property it covers. |
| `weights` | map<(Source, property) → weight 0.0–1.0> | The actual authority. |
| `tieBreaker` | enum | `highest` / `newest` / `most-confident` / `human` / `no-write`. |
| `effectiveFrom`, `effectiveTo` | temporal | Policy lifecycle. |
| `owner` | ref | Person/team accountable. |
| `approval` | ref | Link to the change record that approved this policy. |

**Example.** For `Application.lifecycle.state`:

| Source | Weight |
|---|---|
| ServiceNow CMDB | 0.95 |
| LeanIX | 0.6 |
| DMM assessment | 0.4 (informational; assessment reports what it sees) |
| Agent registry | 0.3 (an agent *uses* the app, doesn't own its lifecycle) |
| HR | 0.0 (irrelevant) |

When CMDB says `RETIRED` and LeanIX says `active`, the CMDB wins. When
CMDB is silent, LeanIX wins with confidence 0.6 (still well above
`CANDIDATE` threshold). The losing value is preserved in a
`KnowledgeConflict` row.

## 6. Bidirectional sync authority (CR-11R)

`SYNC`-capable Adapters can write back to the Source. Two sources
`A` and `B` that both sync to OpenDEA *and* accept writes back from
OpenDEA form a **bidirectional loop**. Without a declared
`AuthorityPolicy`, the loop oscillates: A→B, B→A, A→B, with each
side overwriting the other. With corrupt timestamps, this is data
corruption, not sync.

CR-11R's discipline:

1. **Declared per (Source, property).** If undeclared, the system MUST refuse bidirectional sync for that property.
2. **Writer of last resort** is the highest-weight Source for the property; others receive but do not write back.
3. **Echo suppression.** A→OpenDEA→B must not flow B→OpenDEA→A within a configurable window (default 5 min).
4. **Audit.** Every cross-source write records originating Source, authorising policy, and before/after values.

> **Undefined authority = oscillation or corruption.** This is not a
> performance concern; it is a correctness invariant.
