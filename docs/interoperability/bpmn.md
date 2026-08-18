# BPMN Interoperability (CR-11Y)

> **KB note — what OpenDEA takes from BPMN, what it returns, and
> where the two stop pretending to be the same thing.** Companion to
> [archimate.md](archimate.md), [dmn.md](dmn.md) and
> [overview.md](overview.md).

## 1. Why BPMN is a candidate, not a default

BPMN is the most successful notation for executable business-process
diagrams. OpenDEA is a semantic contract for the enterprise. They
overlap on `dea:BusinessProcess` and then diverge. CR-8 §46 listed
BPMN as a **candidate** ("not yet mapped"); CR-11Y promotes it to a
first-class mapping candidate with explicit honesty about where the
boundary lies.

This file is an *informative* mapping sketch and a conformance seed;
it is not a normative BPMN profile. A `dea:bpmn` profile (CR-11Y §2) is
the right vehicle if a concrete deployment needs the bridge.

## 2. What OpenDEA is NOT

OpenDEA should not attempt to become BPMN. Concretely:

- OpenDEA does not adopt BPMN's swimlanes, lane inheritance or
  choreography semantics.
- OpenDEA does not try to model BPMN's full sequence-flow
  machinery (event-based gateways, complex gateways, conditional and
  default flows as first-class graph edges).
- OpenDEA does not try to match BPMN's interchange richness for
  executable engine replay.

Where OpenDEA lacks an equivalent, three honest options exist; CR-11Y
adopts all three:

1. **Extension namespace.** A separate `bpmn:` vocabulary lives in
   the consumer's metadata, addresses BPMN-only constructs as their
   own objects, and references OpenDEA `dea:` entities by ID. The
   OpenDEA core contract is unchanged.
2. **Composite mapping.** A BPMN construct decomposes into
   multiple OpenDEA entities (e.g. a BPMN *sub-process* with
   *multi-instance* behaviour becomes a `dea:BusinessProcess` plus
   several `dea:ScenarioAssumption`s; the mapping records the
   decomposition).
3. **Lossy with note.** The mapping *keeps the BPMN construct as
   opaque metadata* on the OpenDEA entity, plus a typed
   `provenance.transformation` note explaining what is lost.

Choice 1 (the extension namespace) is the default for concepts that
do not decompose cleanly.

## 3. Mapping table

| BPMN concept            | OpenDEA concept(s)                | Relationship | Confidence | Lossiness   |
|-------------------------|------------------------------------|--------------|------------|-------------|
| Process                 | `dea:BusinessProcess`              | Exact        | high       | lossless    |
| Task (Abstract/Service/Send/Receive/User/Manual/Business Rule/...) | `dea:Task` (Activity profile) | Approximate | high      | minor-loss  |
| Start / Intermediate / End Event | `dea:Event` (Event profile) | Exact  | high       | lossless    |
| Gateway — Exclusive / Inclusive / Parallel / Event-based | *(extension namespace `bpmn:`)* | No direct equivalent  | high | lossy |
| Sequence Flow           | `dea:flows-to` (Flow)              | Approximate  | medium     | minor-loss  |
| Message Flow            | `dea:exchanges` (Information)      | Approximate  | medium     | minor-loss  |
| Lane / Pool             | `dea:OrganizationalUnit` / `dea:Actor` | Composite | high     | minor-loss  |
| Sub-Process             | `dea:BusinessProcess` (nested)     | Composite    | high       | minor-loss  |
| Data Object / Data Store | `dea:DataEntity` / `dea:InformationAsset` | Composite | high | minor-loss  |
| Choreography            | `dea:CollaborationAgreement` / `dea:EcosystemActor` | Composite | medium | minor-loss |

Notes:

- **Gateways** have no direct equivalent because OpenDEA's
  `BusinessProcess` semantics are descriptive ("this process
  realizes this capability") not executable. Routing logic is
  carried by `dea:ScenarioAssumption`, `dea:DecisionOption` and
  the rules below. Forcing gateways into the core would expand the
  metamodel — exactly what CR-11Y forbids.
- **Sequence Flow → `dea:flows-to`.** BPMN sequence flow is
  ordered; OpenDEA flow is structural. Order is captured on
  `dea:BusinessProcess` as an ordered step list in property
  `process:steps` and/or via a companion `dea:Scenario`.
- **Lanes / Pools** are composite — a BPMN pool typically maps
  to a `dea:EcosystemActor`, lanes within it to `dea:Actor`s, both
  bound to a `dea:OrganizationalUnit`.

## 4. What conformance tests assert

The BPMN tests under `/conformance/mapping-tests/` (see
[conformance.md](conformance.md)) cover:

- Round-trip of one canonical BPMN sample (chosen so it exercises
  Process, three Task types, Start/End Events, one Exclusive
  Gateway, one Sub-Process) → OpenDEA → BPMN sample. All
  `Exact` rows survive byte-equal *semantically* (CR-11AP).
- An `Approximate` row preserves identity but emits a typed
  lossiness record (no silent rounding).
- A gateway becomes an extension-namespace entry; the canonical
  `dea:` graph does not.
- Every imported entity carries Source + Timestamp (CR-11O).

## 5. See also

- [archimate.md](archimate.md) — the EA sibling of this mapping
- [dmn.md](dmn.md) — the decision-model sibling; DMN and BPMN pair
  for executable process+decision engines
- [overview.md](overview.md) — interoperability framing and the
  position of mapping in the levels
- [provenance.md](provenance.md) — what survives any BPMN round-trip
