# Semantic Mappings, Transformations & Governed Mapping Lifecycle

> **KB note — mappings are the load-bearing piece of CR-11.** A
> mapping says "this concept in the outside world corresponds to that
> concept in OpenDEA, with this confidence, this transformation, and
> this lossiness." Treat it as a first-class governed asset, not as
> glue code in an import job. Source: CR-11E/F/G/H/AQ/AR/AS/AT/AU.
> Companion notes: [overview.md](overview.md), [architecture.md](architecture.md),
> [identity.md](identity.md), [federation.md](federation.md),
> [events.md](events.md), [security.md](security.md).

## 1. SemanticMapping is a first-class object (CR-11E)

| Field | Purpose |
|---|---|
| `id` | Mapping id. |
| `source` | ref → `ExternalSystem` (or namespace). |
| `sourceConcept` | The external concept (e.g. `cmdb_ci_appl`, `ArchiMate:ApplicationComponent`). |
| `targetConcept` | The OpenDEA concept (e.g. `dea:Application`). |
| `relationship` | see §2 — the kind of correspondence. |
| `transformation` | ref (see §4). Optional, testable. |
| `confidence` | see §3. Honest expression of certainty. |
| `lossiness` | see §5. CR-11AQ declared information loss. |
| `status` | `DRAFT` / `ACTIVE` / `DEPRECATED` / `RETIRED` / `SUPERSEDED` (see §8). |
| `owner` | ref. Person/team accountable. |
| `version` | Mappings are versioned like code. |
| `effectiveDate` | When the mapping became canonical. |
| `deprecationDate` | When it stops being authoritative. |
| `replacedBy` | ref. If superseded, pointer to successor. |
| `approval` | ref. Change record that approved this version. |
| `description` | Markdown rationale. |

A mapping is **declarative**, not procedural. It says *what* the
correspondence is, with enough metadata for an Adapter to *execute*
it.

## 2. Mapping relationships beyond `=` (CR-11F)

> Real-world interop is almost never clean equivalence. CR-11F makes
> this explicit so that downstream reasoning does not assume `=`.

| Relationship | Meaning | Example |
|---|---|---|
| `EQUIVALENT` | Same meaning, interchangeable. | `ArchiMate:ApplicationComponent` ≡ `dea:Application` (with no transformation). |
| `SUBTYPE_OF` | The source concept is narrower than the target. | `cmdb_ci_business_app` (business app) ⊑ `dea:Application`. |
| `SUPERSET_OF` | The target is narrower than the source. | `dea:ApplicationService` ⊇ `cmdb_ci_service`. |
| `MAPS_TO` | Loose correspondence; a real transformation is required. | `cmdb.environment=production` → `lifecycle.state=OPERATIONAL`. |
| `COMPOSES` | The source concept is built from several target concepts. | `cmdb_ci` (a CI) decomposes into Application + Infrastructure + Configuration. |
| `SPLITS_INTO` | The source concept fans out to several target concepts. | A `business_service` splits into several `dea:ApplicationService`. |
| `MERGES_FROM` | The target concept is the union of several source concepts. | `dea:Application` ← `cmdb_ci_appl` ∪ `leanix.factSheet`. |
| `RELATED_TO` | A documented semantic relationship without a direct mapping. | Used for crosswalks and discovery. |
| `NO_CORRESPONDENCE` | The source concept has no OpenDEA analogue. | Captured for completeness; never silently dropped. |

## 3. Confidence (CR-11G)

| Confidence | When to use | Implication |
|---|---|---|
| `EXACT` | Two concepts are formally the same. | Adapters can treat source values as canonical. |
| `HIGH` | Concepts agree in practice across the enterprise, with documented edge cases. | Adapters may auto-apply with a `KnowledgeConflict` audit row. |
| `MEDIUM` | Concepts overlap, but the Source has known exceptions. | Adapters apply with a flag; scenarios and assessments see a quality signal. |
| `LOW` | Concepts are loosely related. | Adapters apply only with explicit policy approval. |
| `UNCERTAIN` | We don't know yet. | Mapped values are quarantined; not visible to canonical reasoning. |

**Confidence prevents false semantic precision.** A mapping at
`MEDIUM` that is treated as `EXACT` is a future incident.

## 4. Transformations are explicit and testable (CR-11H)

A transformation is a *named, versioned, tested* function. It is not
a string buried in a config file.

| Field | Purpose |
|---|---|
| `id`, `name`, `version` | Identity. |
| `language` | enum | `js` / `python` / `jq` / `sparql` / `cel` / `declarative`. |
| `source` | ref | The transformation code or expression. |
| `tests` | set of refs | A transformation MUST ship with positive *and* negative tests. |
| `owner` | ref | Person/team accountable. |
| `approval` | ref | Change record. |

**Example.** `ApplicationStatus 'Retired'` → `lifecycle.state RETIRED`:

```yaml
id: tx-cmdb-status-to-lifecycle
version: "1.2.0"
language: declarative
source: |
  when source.status in ["Retired", "Decommissioned", "End of Life"]
    then target.state = "RETIRED"
       target.observedAt = source.last_modified
  when source.status == "In Maintenance"
    then target.state = "MAINTENANCE"
  else target.state = map(source.status, default="OPERATIONAL")
tests:
  - { in: {status: "Retired"},    out: {state: "RETIRED"} }
  - { in: {status: "Decommissioned"}, out: {state: "RETIRED"} }
  - { in: {status: "In Maintenance"}, out: {state: "MAINTENANCE"} }
  - { in: {status: "Production"},  out: {state: "OPERATIONAL"} }
```

A transformation without tests is not a transformation; it is a guess
with a version number.

## 5. Lossiness declaration (CR-11AQ)

> CR-11AQ calls lossiness *"extremely useful for serious
> interoperability"*. Knowing *what you lose* is the difference
> between honest interop and silent data corruption.

| Lossiness | Meaning |
|---|---|
| `LOSSLESS` | Every piece of source information is preserved in the canonical form (typically with extensions). |
| `PARTIAL` | Some source information is preserved; the rest is dropped or summarised, and the dropped information is *named* in the mapping description. |
| `LOSSY` | The mapping materially distorts the source. Allowed only with explicit `LOW`/`UNCERTAIN` confidence and an owner. |
| `UNKNOWN` | We have not analysed the lossiness yet. Treated as `LOSSY` for safety until reviewed. |

## 6. Extensions — for what doesn't map (CR-11AR)

External systems will always have concepts OpenDEA does not model. The
discipline is: **let them exist in OpenDEA, but never in the Core
namespace.**

| Field | Purpose |
|---|---|
| `namespace` | URI prefix (e.g. `vendorX:`). |
| `name` | string | The local name. |
| `version` | string | The version of the external vocabulary. |
| `definition` | string | The external definition, verbatim or summarised with citation. |
| `source` | ref | Where it came from. |
| `canonical?` | bool | Always `false` for external concepts. |

A `vendorX:SpecializedCapability` stays in `external:`, is governed by
the vendor's namespace, and never contaminates the OpenDEA Core
(`opendea:`, `dmm:`, `ai:`, `security:`, `industry:`). The extension
*is* the integration boundary.

## 7. Namespaces (CR-11AS)

| Prefix | Owner | Purpose |
|---|---|---|
| `opendea:` | OpenDEA core | The canonical metamodel. |
| `dmm:` | DMM | Digital maturity model. |
| `ai:` | OpenDEA | AI/agent concepts. |
| `security:` | OpenDEA | Security & control concepts. |
| `industry:` | OpenDEA | Industry vertical extensions (Banking, Healthcare, Public Sector). |
| `external:` | Per-Source | Anything from a `vendorX:` namespace. |

The Core namespaces are governed by the OpenDEA change process. The
`external:` namespace is governed by its Source's owner, with OpenDEA
acting as host.

## 8. Mappings as governed assets (CR-11AT/AU)

> **Mapping changes alter enterprise meaning.** A mapping that says
> `cmdb.environment=Production` is `lifecycle.state=OPERATIONAL` is a
> semantic claim about what "operational" *means* — not a config
> change. CR-11AT/AU require lifecycle governance equal to a schema
> change.

### Mapping lifecycle (CR-11AU)

| Status | Meaning | Required fields |
|---|---|---|
| `DRAFT` | Proposed, not yet authoritative. | `owner`, `version`. |
| `ACTIVE` | Authoritative; Adapters may apply. | `owner`, `version`, `approval`, `effectiveDate`. |
| `DEPRECATED` | Still applicable but scheduled for retirement. | `deprecationDate`, `replacedBy`. |
| `RETIRED` | No longer applied. | `replacedBy` or terminal reason. |
| `SUPERSEDED` | Replaced by a newer mapping. | `replacedBy` (mandatory). |

`SUPERSEDED` and `RETIRED` always carry a `replacedBy` pointer so
historical data can still be traced to the mapping that *was* active
when it was imported. A mapping without `replacedBy` and without a
retirement reason is an orphan — and orphans are how enterprises
forget why their data looks the way it does.
