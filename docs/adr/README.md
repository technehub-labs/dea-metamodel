# Architecture Decision Records

This directory holds the Architecture Decision Records (ADRs) for the
OpenDEA programme. ADRs capture the *settled* architectural decisions
that emerge from the CR sequence (CR-1 onward). Each ADR is a short,
immutable record of one decision: its context, the decision itself,
its consequences, and the references that ground it.

## Convention

Write an ADR when a decision is **architecturally significant** —
meaning it constrains the design of OpenDEA going forward, it cannot
be reversed cheaply, or it forecloses alternatives that downstream
programmes depend on. Routine engineering choices do not need an ADR.
An ADR is **immutable once Accepted**: do not rewrite it to retroactively
match a new direction. If a decision changes, **supersede** the ADR by
writing a new one that references the old and explains why it is being
replaced; keep the original intact for the historical record.

## Index

| ADR | Title | Scope |
|-----|-------|-------|
| [ADR-001](ADR-001-opendea-as-semantic-foundation.md) | OpenDEA as semantic foundation | What OpenDEA is — and is not |
| [ADR-002](ADR-002-core-versus-profiles.md) | Core versus Profiles | Where new semantics live |
| [ADR-003](ADR-003-canonical-identity.md) | Canonical identity | How concepts are identified |
| [ADR-004](ADR-004-knowledge-graph-abstraction.md) | Knowledge graph abstraction | Vendor-independent `GraphStore` |
| [ADR-005](ADR-005-provenance-model.md) | Provenance model | Observed / asserted / inferred / approved |
| [ADR-006](ADR-006-temporal-semantics.md) | Temporal semantics | Five clocks; bitemporal; planned ≠ current |
| [ADR-007](ADR-007-runtime-api-separation.md) | Runtime/API separation | Viewer → Runtime → Specification layering |
| [ADR-008](ADR-008-inference-versus-authoritative-knowledge.md) | Inference versus authoritative knowledge | No silent inference; explicit state transitions |
| [ADR-009](ADR-009-agent-authorization-model.md) | Agent authorization model | Read-only by default; PDP ALLOW/DENY/ESCALATE |
| [ADR-010](ADR-010-scenario-isolation-from-production-state.md) | Scenario isolation from production state | Baseline + deltas; scenarios never mutate production |
| [ADR-011](ADR-011-simulation-adapter-architecture.md) | Simulation adapter architecture | `SimulationAdapter` boundary; result provenance |
| [ADR-012](ADR-012-dmm-opendea-relationship.md) | DMM / OpenDEA relationship | Diagnostic instrument vs semantic substrate; closed loop |
| [ADR-013](ADR-013-core-non-accumulation.md) | Core non-accumulation | Adapters absorb external complexity; the Core does not accumulate concepts |
| [ADR-014](ADR-014-intelligence-loop-architecture.md) | Intelligence loop architecture | Five bounded layers (Observation → Signal → Pattern → Loop → ActionProposal); 8 binding rules for the composition layer that closes the CR-10 §P loop |
| [ADR-015](ADR-015-capability-classification-by-specialization.md) | Capability classification by specialization | Abstract `dea:Capability` root; kinds as ADR-WSF-04 specializations in profiles; layer as attribute; ECF remains metadata; WSF federation mapping |

## Status

The ADRs in this index are **Accepted** as of their listed dates. They form
the architectural baseline for OpenDEA. ADR-014 supersedes nothing; it
records the composition-layer decisions for CR-012 (Enterprise
Intelligence & Advanced Agentic Runtime), building on ADR-002 / 007 /
008 / 009.