# OpenDEA Documentation

Everything under `docs/` is **informative** — it explains, interprets and
guides. The **normative** contract (MUST/SHOULD/MAY) lives in
[`specification/`](../specification/OpenDEA-Semantic-Architecture-Specification.md)
and `metamodel/`. Where this documentation and the specification disagree, the
specification wins and the documentation is drift (CR-10 §J).

## Start here

- **[OpenDEA — Conceptual Architecture](opendea-conceptual-architecture.md)** —
  the single authoritative narrative consolidating CR-1 → CR-10: what OpenDEA
  is, the problem it solves, the layer model, and what is explicitly outside
  it (CR-10 §A/B/P).

## Core concepts

- [The Four-State Model](concepts/four-state-model.md) — Current / Target /
  Scenario / Observed are different semantic dimensions (CR-10 §C)
- [The Truth Model](concepts/truth-model.md) — observed / asserted / inferred /
  approved are never conflated (CR-10 §D)
- [The Semantic Lifecycle](concepts/semantic-lifecycle.md) — the OpenDEA
  operating cycle (CR-10 §E)
- [Scenarios](concepts/scenario.md) — first-class, baseline-referencing,
  delta-only future states (CR-10A–C)
- [Digital Twin positioning](concepts/digital-twin.md) — the maturity ladder,
  and what we do not claim (CR-10 §H, CR-10AA/AB)

## Positioning

- [OpenDEA and DMM](opendea-and-dmm.md) — diagnostic instrument vs
  transformation substrate (CR-10 §F)
- [OpenDEA and AI/Agents](opendea-and-agents.md) — knowledge, governance,
  infrastructure; not an agent framework (CR-10 §G)

## Architecture knowledge base

- [Specification & Conformance (CR-8)](specification-and-conformance.md)
- [Runtime Architecture (CR-9)](runtime-architecture.md)
- [Temporal Semantics (CR-6)](temporal-semantics.md)
- [Governance & Agentic Semantics (CR-7)](governance-agentic-semantics.md)
- [Architecture Decision Records](adr/README.md) — settled decisions
  (ADR-001…ADR-013); new questions land here, not in chat history

## Interoperability

- [Overview](interoperability/overview.md) — the semantic contract holds;
  adapters absorb external complexity (CR-11 §2)
- [Architecture](interoperability/architecture.md) — Source / Adapter /
  Mapping / Exchange; connector ≠ adapter (CR-11A/D)
- [Identity & reconciliation](interoperability/identity.md) — external
  identifiers, conflicts, property-specific authority (CR-11I–N)
- [Mappings](interoperability/mappings.md) — relationships, confidence,
  lossiness, governance (CR-11E–H, AQ–AU)
- [Federation](interoperability/federation.md) — federated knowledge,
  locality, phased boundary (CR-11AH–AK)
- [Events](interoperability/events.md) — canonical event envelope (CR-11AF/AG)
- [Security](interoperability/security.md) — the integration attack surface
  (CR-11AY–BA)
- [Exchange format](interoperability/exchange-format.md) — envelope,
  versioning, semantic round-trip (CR-11S–V, AP)
- [Provenance](interoperability/provenance.md) — the integration provenance
  chain (CR-11O/AE/BD)
- Standard mappings: [ArchiMate](interoperability/archimate.md) ·
  [BPMN](interoperability/bpmn.md) · [DMN](interoperability/dmn.md)
- [Conformance](interoperability/conformance.md) — classes, suites, golden
  datasets (CR-11AM–AO)

## Enterprise Intelligence (CR-012)

- [Signal model](intelligence/signal-model.md) — first-class governed
  artifacts (`Observation` + `Signal`); classification / severity /
  confidence / lifecycle vocabularies; Phase 1 of CR-012

## Reference

- [Glossary](glossary.md) — canonical terminology (CR-10 §L)
- [Conformance Model](conformance-model.md) — semantic / runtime /
  interoperability / agentic levels (CR-10 §M)
- [Versioning](versioning.md)
