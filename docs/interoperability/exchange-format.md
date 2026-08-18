# Exchange Format (CR-11S / T / U / V / AP)

> **KB note — the envelope that carries OpenDEA across organisational and
> tool boundaries, and the versioning claims every exchange document MUST make.**
> Companion to [overview.md](overview.md), [archimate.md](archimate.md) and
> [provenance.md](provenance.md). Informative; the normative contract is in
> `specification/serialization-versioning.md` and `schemas/model-envelope.json`.

## 1. Why a dedicated exchange format (CR-11S)

Interoperability, federation and ecosystem conformance collapse unless the
thing being moved across the boundary has a stable, self-describing shape.
The exchange envelope is what makes OpenDEA portable: a single document a
third party can validate, route and replay without an out-of-band
conversation. CR-11S specifies nine mandatory envelope fields:

| Field            | Purpose                                              |
|------------------|------------------------------------------------------|
| `id`             | Globally unique identifier of this exchange document |
| `source`         | Producing system, adapter, agent or runtime          |
| `target`         | Intended recipient (`null`/wildcard = broadcast)      |
| `timestamp`      | Production time (RFC 3339, UTC)                      |
| `schemaVersion`  | Version of `schemas/model-envelope.json`              |
| `mappingVersion` | Version of the mapping/transformer used (CR-11V)     |
| `operation`      | One of `import`, `export`, `query`, `validate`, `subscribe` |
| `payload`        | The semantic content (canonical serialization, CR-11U) |
| `provenance`     | Source chain + transformation record (see provenance.md) |

A document without all nine fields MUST NOT be accepted as an OpenDEA
exchange (CR-11V). The envelope is the unit of policy, audit and replay.

## 2. Format strategy (CR-11T): one primary, others derived

JSON is the **primary developer exchange format**. It is what tooling,
agents and runtimes consume by default and what every reference test
suite in `tests/conformance/` accepts first.

RDF/OWL serialization is **adopted where graph interop requires it**
(serialization-versioning.md §1: `ttl/dea-metamodel-ontology.ttl` is a
*derived* representation, never the accidental ontology). CR-11T is
deliberate: not every external system needs RDF, and forcing it on JSON
tooling is a needless barrier. Conforming products MUST emit JSON and
MAY emit RDF/Turtle and JSON-LD as additional serializations.

Initial conformance therefore targets JSON. RDF coverage is the L3
interoperability level (conformance.md), not the L1 baseline.

## 3. The canonical payload is not the database (CR-11U)

This is the rule CR-11U exists to make unmistakable. The payload MUST
represent **Entities, Relationships, Assertions, Evidence, Profiles,
State, Events, Scenarios, Decisions** — the semantic fabric defined by
the canonical metamodel — and MUST NOT simply serialize the internal
schema of any one runtime or database.

Concretely:

- An internal table layout, an RDF-blob store, or a vendor's
  property-bag node is not a payload. Hand them through the canonical
  shape first; the mapping is observable, the provenance is
  attributable, the rules apply.
- Internal IDs become stable `dea:` identifiers; convenience joins
  become typed relationships; computed columns become derived
  views (never authoritative properties, CR-3 §30).
- The CRUD sanity of one store never leaks into the exchange. A
  reader who has never heard of your database can still understand,
  validate and reason over what arrives.

## 4. Version declarations on every exchange (CR-11V)

Three declarations travel with every document, individually versioned:

```
schemaVersion      — e.g. "1.0.0" (schemas/model-envelope.json)
profile versions   — e.g. ["dea:core@1.0.0", "dea:assessment@1.0.0"]
mappingVersion     — e.g. "archimate-1.0.0" for an ArchiMate import
```

A runtime that receives an envelope declares which schemas and profile
versions it understands; unknown schemaVersions are refused, unknown
profile versions fall back to base Core, unknown mappingVersions refuse
the document. This is how CR-11V keeps an OpenDEA from CR-5 talking to an
OpenDEA from CR-11 — they negotiate forward, not by version sniffing.

## 5. Round-trip principle (CR-11AP) — *semantic*, not byte-for-byte

> **CRITICAL DISTINCTION.** CR-11AP calls out a confusion the
> marketplace constantly makes: round-trip preservation is **semantic**,
> not byte-for-byte.

Serialize an OpenDEA document to JSON → reconstruct → reserialize → the
two serializations will not be byte-equal. They will be *semantically*
equal: same entities, same typed relationships, same evidence chain,
same profile bindings, same validity intervals. Properties may be
reordered; absent defaults may be filled in; presentation views may be
expanded or folded; the envelope may gain a new `schemaVersion`-keyed
annotation.

What MUST be preserved semantically:

- all `dea:` entity identities and types,
- all typed, directed, inverse-declared relationships,
- all evidence, provenance and source citations (provenance.md),
- all binding profile versions and decisions (governance profile).
- all temporal validity bounds (CR-6): `valid_from`/`valid_to`
  survive any round-trip.

What MAY legitimately change across a round-trip:

- byte ordering, key ordering, whitespace, comment-style prefaces,
- presentation-only conveniences (`metadata.author_name` formatting),
- derived properties that the canonical model declares as generated.

A conformance test fails when **semantic** content is lost — when an
entity drops, when a relationship gets its endpoints swapped, when
provenance is severed from its assertion. It does NOT fail on
formatting drift.

## 6. See also

- [overview.md](overview.md) — interoperability framing and levels
- [provenance.md](provenance.md) — what travels inside the `provenance` envelope field
- [mappings.md](mappings.md) — versioned mapping registries
- [conformance.md](conformance.md) — Exchange class and the conformance suite
