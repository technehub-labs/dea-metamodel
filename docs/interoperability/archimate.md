# ArchiMate Interoperability (CR-11W / X)

> **KB note — the mapping OpenDEA maintains into the ArchiMate
> language, why it lives where it does, and why a mapping is not an
> adoption.** Companion to [bpmn.md](bpmn.md), [dmn.md](dmn.md) and
> [mappings.md](mappings.md). Build on the existing artifacts in
> `mappings/archimate/`; this file is informative and consolidates what
> CR-8 §45 began with what CR-11X adds.

## 1. Why ArchiMate gets special attention (CR-11X §1)

OpenDEA operates in the enterprise-architecture (EA) domain. ArchiMate
3.2 is the EA-domain lingua franca. A first-class mapping between the
two is therefore not optional — it is what lets OpenDEA serve existing
EA programmes rather than asking them to start over. CR-8 §45 produced
the seed matrix; CR-11X extends it with explicit relationship classes,
confidence and lossiness, and a starter table that the conformance
suite can test against.

## 2. Where the existing work lives

The CR-8 era mapping artifacts are:

- [`mappings/archimate/mapping.yaml`](../../mappings/archimate/mapping.yaml)
  — the CR-8 §44/§45 matrix (entities with documented divergences).
- [`mappings/README.md`](../../mappings/README.md) — registry of all
  external-standard mappings (ArchiMate v1.0.0; DMN evaluated; BPMN
  candidate; RDF/OWL derived; PROV/Dublin Core alignment notes).
- [`change-requests/CR-008.md` §45](../../change-requests/CR-008.md) —
  the matrix in narrative form (Capability, Business Process, Service,
  Application, Technology, Outcome, Requirement, Stakeholder).

This file (`docs/interoperability/archimate.md`) is what CR-11X
explicitly asks to exist at this path. It does not contradict
`mappings/archimate/`; it summarises, links, and adds CR-11-era
material: relationship classes, confidence, lossiness, and the rule
that a mapping does not imply metamodel adoption.

## 3. A mapping does not imply metamodel adoption (CR-11W)

> **RULE.** Supporting an ArchiMate import/export does NOT mean
> OpenDEA adopts ArchiMate's metamodel, its viewpoints, its layering,
> or its modelling discipline. The `dea:` namespace remains canonical
> for every round-tripped element.

Concretely:

- An import creates OpenDEA entities and relationships. It does
  *not* silently promote ArchiMate "Application" into OpenDEA's
  `dea:ApplicationComponent` shape; the mapping declares the
  `mapping.kind` that records what changed.
- A consumer of the imported graph sees OpenDEA. ArchiMate is
  one possible source.
- Adoption of ArchiMate as the *primary* modelling language is a
  programme decision a particular enterprise may take; CR-11W is
  silent on that question and is not an endorsement.

## 4. Relationship classes for the matrix (CR-11X §3)

The matrix below uses four relationship classes, none of which force
false equivalence (CR-11X):

| Class                | Meaning                                                                    |
|----------------------|----------------------------------------------------------------------------|
| **Exact**            | The two concepts name the same idea; no knowledge is lost either way.      |
| **Approximate**      | Close but not identical; the matrix MUST call out what differs.            |
| **Composite**        | The ArchiMate concept decomposes cleanly into multiple OpenDEA entities.   |
| **No direct equivalent** | OpenDEA either has the richer concept or ArchiMate lacks the concept entirely. |

In addition, the table uses the `dea:maps-to` `mapping.kind` vocabulary
from the canonical relationship registry (`metamodel/dea-metamodel.yaml`
§dea:maps-to, originally CR-2 §9):

- `equivalent` — Exact
- `narrower` / `broader` — Approximate (declare direction)
- `related` — Composite link
- `external-crosswalk` — mappings to foreign metamodel concepts

A confidence value (`high | medium | low`) and a lossiness note
(`lossless | minor-loss | major-loss`) travel with every row. These are
what `tests/conformance/` validates.

## 5. Starter mapping table

The relationships in OpenDEA are typed, directed, inverse-aware and
temporally boundable (CR-2/CR-6); ArchiMate relationships are typed
but not temporal. That asymmetry alone rules out exact 1:1 of the
relationship layer — captured in `relationship_notes` of
`mappings/archimate/mapping.yaml`.

| ArchiMate concept        | OpenDEA concept(s)                       | Class                  | Confidence | Lossiness   |
|--------------------------|------------------------------------------|------------------------|------------|-------------|
| Application Component    | `dea:ApplicationComponent`               | Exact                  | high       | lossless    |
| Business Actor           | `dea:Actor`                              | Approximate            | medium     | minor-loss  |
| Business Process         | `dea:BusinessProcess`                    | Exact                  | high       | lossless    |
| Business Service         | `dea:BusinessService`                    | Exact                  | high       | lossless    |
| Capability               | `dea:BusinessCapability`                 | Exact                  | high       | lossless    |
| Technology Component     | `dea:Technology` / `dea:InfrastructureComponent` | Composite       | high       | minor-loss  |
| Driver / Goal (Motivation) | `dea:StrategicObjective`               | Approximate            | medium     | minor-loss  |
| Plateau                  | `dea:ArchitectureState` (baseline)       | Composite              | medium     | minor-loss  |
| Outcome                  | `dea:Outcome`                            | Exact                  | high       | lossless    |
| Requirement              | `dea:Requirement`                        | Exact                  | high       | lossless    |
| Stakeholder              | `dea:Stakeholder`                        | Exact                  | high       | lossless    |
| Decision                 | *(no direct equivalent)*                 | No direct equivalent   | —          | —           |

Notes on the rows that diverge:

- **Business Actor ≈ `dea:Actor` (Approximate).** `dea:Actor` is
  broader than ArchiMate's *business* Actor — it includes system and
  AI agents (CR-7 §27). The mapping declares `narrower` from OpenDEA
  to ArchiMate when projected back.
- **Technology Component is Composite.** ArchiMate separates
  Technology Node, Technology Service, Technology Interface and
  Artifact; OpenDEA uses `dea:Technology` (the substrate) plus
  `dea:InfrastructureComponent` (a deployed instance) plus
  `dea:PlatformService`. The mapping records the decomposition.
- **Driver / Goal → `dea:StrategicObjective` is Approximate.**
  ArchiMate motivation elements have richer narrative semantics
  (Assessment, Constraint, Meaning, Value); OpenDEA's `dea:Tenet`
  and `dea:Regulation` carry some of that. The map is honest about
  what is not captured.
- **Plateau ≈ `dea:ArchitectureState` (baseline).** ArchiMate
  models plateaux as states; OpenDEA states are first-class with
  validity intervals (CR-6). One ArchiMate plateau becomes one
  OpenDEA `ArchitectureState` referenced by a `dea:Baseline`.
- **Decision has no direct ArchiMate equivalent.** ArchiMate has no
  first-class decision with authority and governance; the DMN
  mapping (see [dmn.md](dmn.md)) is the right place for that.

## 6. Conformance and see also

The ArchiMate tests in `/conformance/` validate: round-trip of an
ArchiMate sample preserves all entities, all `equivalent`/`narrower`
relationships, with a typed lossiness record for the rest
(CR-11AP, CR-11U, CR-11O); the `mappings/archimate/mapping.yaml`
matrix matches this table (no silent additions); every imported entity
retains Source + Timestamp (CR-11O; see [provenance.md](provenance.md)).

**See also:** [bpmn.md](bpmn.md), [dmn.md](dmn.md), [provenance.md](provenance.md),
[conformance.md](conformance.md); CR-8 artifact in `mappings/archimate/mapping.yaml`.
