# OpenDEA Semantic Architecture Specification

**Version 1.0.0** · Status: Stable · Supersedes: CR-1…CR-7 working drafts
Normative source: `metamodel/dea-metamodel.yaml` · Validator: `tools/opendea_validate.py`

---

## 1. Scope

This specification defines what it means for a model to be **OpenDEA-conformant** (CR-8 §1):
the semantic vocabulary, canonical metamodel, type system, relationship system, constraints,
profiles, machine-readable schema, validation behavior, conformance levels and reference
models. It consolidates CR-1 through CR-7 into an independently implementable standard (§69:
a third party, given only this specification + schema + profiles + conformance rules, must
reach the same conformance conclusion as any other implementation).

## 2. Design principles

1. **One normative source** (CR-1). Everything else is generated or validated against it.
2. **Separate semantic core from profiles, implementation schemas and visualization** (§2/§67).
3. **Small stable Core + composable profiles + explicit mappings** — never the mega-model (§55).
4. **Architecture is a time-dependent state**, not a static catalogue (CR-6 §1).
5. **Assessment is a separate semantic layer** — never intrinsic attributes (CR-5 §1).
6. **Agents are participants, not the center** (CR-7 §1); agentic semantics reuse core semantics (CR-7 §65).
7. **Documentation, schemas, validators and viewers are generated/consuming artifacts** (§49-§50).

## 3. Terminology

Authoritative per-concept definitions: [`vocabulary.yaml`](./vocabulary.yaml) (generated).
One canonical definition per semantic concept (§5).

## 4. Semantic architecture

```
OpenDEA Core (18 anchors)
   ├── profiles: business · ecosystem · digital · data · technology · ai · governance · ecf
   ├── assessment (CR-5) + dmm
   ├── lifecycle (CR-6)
   └── governance (CR-7) + agentic (CR-7)
        ↓
   serialization: YAML (authoring) · JSON (interchange) · RDF/OWL (derived, optional)
        ↓
   validation → conformance (levels 0–5)
```

## 5. Core concepts

Frozen at 18 anchors — see [`core-freeze.yaml`](./core-freeze.yaml), including the §3
candidate evaluation and the anti-inflation rule (§4). Full catalogue:
[`catalogues/entities.md`](./catalogues/entities.md).

## 6. Relationship semantics

104 typed, directed, inverse-aware relationship types; single canonical direction; full
descriptors (cardinality, transitivity, symmetry, temporality, provenance). See
[`relationship-semantics.md`](./relationship-semantics.md) and
[`catalogues/relationships.md`](./catalogues/relationships.md).

## 7. Type system

Shallow by design: type + composition + typed relationships over deep hierarchies; concept
kinds (abstract/concrete/profile-defined/derived/deprecated); composition vs reference;
isA vs specializes vs implements. See [`type-system.md`](./type-system.md).

## 8. Identity

Names are not identities (§7). Stable `dea:` concept ids; stable instance ids; external
identifiers never substitute (CR-3 E004); identity resolution via `sameAs`/`source` (§43).
See [`naming-conventions.md`](./naming-conventions.md).

## 9. Context

Every model declares a `ModelContext` in its envelope (§24): enterprise, business-unit,
program, product, solution, capability-domain, assessment, transformation, agentic-system.
A fragment is never interpreted as a complete enterprise architecture.

## 10. Lifecycle

Five clocks (transaction/valid/observation/planned/effective); per-type lifecycles;
event ≠ state; history never overwritten; planned ≠ actual. Profile: `dea:lifecycle` (CR-6).

## 11. Assessment

Assessment is a separate semantic layer: frameworks own maturity; results carry evidence,
confidence and provenance; gaps derive and connect to Change. Profiles: `dea:assessment`,
`dea:dmm` (CR-5). Maturity is never an intrinsic property (A008).

## 12. Governance

Intent → Objective → Policy → Decision → Action; authority ≠ capability; delegation with
scope/validity; governance bodies set policy, grant authority, approve, enforce. Profile:
`dea:governance` (CR-7). G001–G016 enforced.

## 13. Agentic semantics

Agent ⊑ Actor; profile, skills, tools, orchestration roles (Agent/Orchestrator/Controller),
configurable autonomy, human oversight patterns, agentic system boundary; reuse rule (§65)
CI-enforced. Profile: `dea:agentic` (CR-7).

## 14. Profiles

Extension mechanism, declaration, third-party namespaces, anti-mega-model rule. See
[`profile-mechanism.md`](./profile-mechanism.md).

## 15. Constraints

Constraint language levels: required property, cardinality, type compatibility,
relationship validity, enumeration, uniqueness, conditional and cross-object rules (§25).
Machine-readable rule families: O (ontology), R (relationship), E (entity), A (assessment),
T (temporal), G (governance) — 112 automated conformance tests in `tests/conformance/`.
Graph-level (SHACL-style) validation evaluated as roadmap (§26).

## 16. Serialization

YAML authoring · JSON interchange · RDF/OWL derived. See
[`serialization-versioning.md`](./serialization-versioning.md). Envelope schema:
`schemas/model-envelope.json`.

## 17. Validation

Reference validator: `tools/opendea_validate.py` — levels 0–3 + governance checks,
registry-driven, structured reports. Normalize operation (`--normalize`, §36).

## 18. Conformance

Levels 0–5, invariants INV-*, error taxonomy DEA-E/W, report format, open/closed world,
assertion provenance. See [`conformance-spec.md`](./conformance-spec.md).

## 19. Interoperability

ArchiMate mapping (v1.0.0); DMN evaluation; BPMN candidate; RDF/OWL adopted as derived
serialization; PROV alignment. See [`mappings/`](../mappings/).

## 20. Versioning

SemVer with two-level (syntax + semantic) compatibility; deprecation contract; migration
rules per breaking change. See [`serialization-versioning.md`](./serialization-versioning.md).

## 21. Extension mechanisms

Profiles (§16/§53), `ext:` namespaces (§54), visualization profile (§48), external mappings
(§44). Core remains frozen.

## 22. Reference models

Golden suite (`models/golden/` — 7 models incl. the six §31 scenarios) and negative suite
(`models/invalid/` — 8 models with expected failures). Both are CI-enforced regression
tests: goldens MUST pass, negatives MUST fail for the expected rule (§32-§33).

---

*This document is maintained alongside generated artifacts per §49-§50; the catalogues,
inventory and vocabulary are regenerated from the normative source by
`.github/scripts/generate_specification.py`. Dependency direction (§67): specification →
schema → validator → reference models → viewers/consumers. Never reversed.*
