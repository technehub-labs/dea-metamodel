# Provenance (CR-11O / AE / BD)

> **KB note — how OpenDEA keeps the *because* attached to every *what*.**
> Provenance is not metadata; it is what makes OpenDEA a trustworthy
> enterprise semantic platform (CR-11BD). Companion to
> [exchange-format.md](exchange-format.md), [federation.md](federation.md)
> and [identity.md](identity.md).

## 1. The rule that ordinary imports break (CR-11O)

Most interop failures start the same way: an external fact arrives, is
*normalized* into the target schema, and loses the link back to where
it came from. From that point on the system can answer *"is this true?"*
but not *"who said so, when, on the basis of what evidence?"*. That gap
is what CR-11O exists to close.

The mandatory chain on every imported fact:

```
External Fact       (the raw record as it arrived)
   │
   ▼
OpenDEA Assertion   (our typed claim about the world)
   │
   ▼
Evidence            (DEA Evidence + EvidenceArtifact)
   │
   ▼
Source              (where the fact came from)
   │
   ▼
Timestamp           (when, with what validity bounds — CR-6)
```

**No step in that chain is optional.** A normalizer that takes an
incoming row, rewrites its fields, and overwrites `source` with
"opendea-import" has thrown away the audit trail the platform was
importing to capture. CR-11O will not accept it.

## 2. Provenance interoperability (CR-11AE) — speak the common tongue

The longer OpenDEA lives, the more of its graph is *agent-generated*
or *imported* knowledge (CR-7 §22, CR-9 CR-2.1). For external auditors,
downstream tools and other platforms to consume that graph, the
provenance shape MUST map cleanly to established provenance concepts.

The target alignment is **PROV-O** (the W3C provenance ontology):

| OpenDEA concept | PROV-O concept | Notes |
|---|---|---|
| OpenDEA Entity (asserted fact) | `prov:Entity` | The thing a claim is about |
| OpenDEA Assertion | `prov:Entity` + `dea:asserts` | The claim itself; first-class |
| The recording/import event | `prov:Activity` | When and how the assertion came to be |
| The agent/system responsible | `prov:Agent` (and `prov:SoftwareAgent`) | `actor.id` is the handle |
| The external source record | `prov:Entity` (the *source* entity, not ours) | Cited by `wasDerivedFrom` |
| The mapping that produced this | `prov:Activity` + `mappingVersion` (CR-11V) | Recorded in `provenance.mapping` |

The mapping is *informative* (we never make OpenDEA depend on PROV);
it exists so that any consumer who already speaks PROV-O — many do —
can read our provenance without learning a new vocabulary first. This
is the same discipline as CR-8 §44: OpenDEA's identity is canonical,
external vocabularies are bridges.

## 3. The integration provenance chain (CR-11BD)

CR-11BD calls this *"one of the defining capabilities of a trustworthy
enterprise semantic platform"*, and it deserves a clear picture. When
OpenDEA pulls data in from an external system of record (HR, ITSM,
CMDB, vendor catalogs, agent APIs), the resulting graph carries the
entire journey of every fact:

```
OpenDEA Entity
   │
   └── asserted by — OpenDEA Assertion
            │
            └── derived via — OpenDEA Mapping
                     │
                     └── executed by — OpenDEA Adapter
                              │
                              └── against — External Record
                                       │
                                       └── in — External System
```

Every edge in that chain is a typed, directed, provenance-recorded
relationship. A reader can answer, from the data alone:

- *Which OpenDEA Entity came from which external system?* — walk
  back along `dea:derived-from`.
- *Which mapping produced it, and at what version?* — read the
  `provenance.mappingVersion` (CR-11V).
- *Was the mapping a transformation or a faithful copy?* — see
  §4 below; transformation provenance.
- *Can I trust this entity today?* — check freshness, validity
  interval, and `dea:assertion-status`.

## 4. Transformation provenance — when the mapping changes a value

A mapping that copies a field verbatim keeps provenance trivially. A
mapping that **transforms** a value (lowercases a string, splits a CSV
column, rewrites a foreign key, normalizes a unit) is no longer a
copy. The transformation and its version are part of the provenance
record.

OpenDEA records, per Assertion:

- the `mapping.id` that performed the transform,
- the `mapping.version` (CR-11V guarantees this travels with the
  envelope), and
- a typed `provenance.transformation` entry describing what was
  transformed and how (`lowercase`, `unit-conversion`, `coalesce`,
  `crosswalk`, `derived`, …).

This means the graph is replayable: given the external record, the
mapping, and the transformation list, an implementation can
reconstruct the assertion bit-for-bit. CR-11AP's semantic round-trip
holds. The user's trust in the data holds.

## 5. Agentic and imported knowledge — one audit story

Agent-generated knowledge is indistinguishable from imported knowledge
in the graph except by `prov:Agent.kind = prov:SoftwareAgent` and the
relevant `agent_id`. The audit story for both is identical: an
Assertion backed by Evidence, with a Source, at a Timestamp, in a
particular State (CR-6). One provenance model serves both pipelines.

## 6. What conformance tests assert

The provenance tests in [conformance.md](conformance.md) guarantee:
every imported Assertion has ≥1 Evidence and ≥1 Source; the Source
timestamp respects the model's freshness window (CR-9 CQ, no silent
inference); a `transformation` record exists whenever a mapping
transforms a value; the external-record → OpenDEA → external round-trip
preserves Source citation and Timestamp (CR-11O + CR-11AP combined).

## 7. See also

- [exchange-format.md](exchange-format.md) — the `provenance` envelope field
- [federation.md](federation.md), [conformance.md](conformance.md)
- `models/golden/transformation.yaml` — golden graph with mapped provenance