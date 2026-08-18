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

## Status

All twelve ADRs in this index were authored as part of CR-10 (scenario
foundation) and are **Accepted** as of 2026-08-18. They form the
architectural baseline for the scenario / simulation / decision-support
work in CR-10 and beyond.