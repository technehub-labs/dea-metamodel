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
  (ADR-001…ADR-012); new questions land here, not in chat history

## Reference

- [Glossary](glossary.md) — canonical terminology (CR-10 §L)
- [Conformance Model](conformance-model.md) — semantic / runtime /
  interoperability / agentic levels (CR-10 §M)
- [Versioning](versioning.md)
