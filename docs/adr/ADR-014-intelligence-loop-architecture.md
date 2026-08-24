# ADR-014: Intelligence loop architecture

- **Status:** Accepted
- **Date:** 2026-08-22
- **Deciders:** OpenDEA architecture programme (CR sequence)

## Context

CR-9 built the runtime, CR-10 built scenario/decision intelligence, CR-11 built the
interoperability & federation boundary. CR-012 (Enterprise Intelligence & Advanced
Agentic Runtime) closes the loop described in CR-10 §P:

```
REPRESENT → UNDERSTAND → EVOLVE → GOVERN & ACT → CONTINUOUS ENTERPRISE
```

The runtime has the primitives — graph, reasoning, assessment, scenarios, agents,
federation — but **no composition layer** ties them into a continuous enterprise
intelligence cycle. Existing runtimes stop at "ask a question, get an answer".
CR-012's goal is to add the ability to:

1. Continuously observe the canonical semantic state.
2. Promote recurring situations to *signals* (governed artifacts, not raw output).
3. Route signals to the right owners under declared authority.
4. Allow agents to propose actions that traverse the policy decision point.
5. Audit the entire loop end-to-end.

The CR-9 / CR-10 / CR-11 work has already produced all the building blocks; CR-012
**composes** them. ADR-014 records the architectural decisions that govern that
composition.

## Decision

The intelligence loop is composed of **five well-bounded layers**, each additive
over the existing canonical contract (CR-8 §1, ADR-007, ADR-002):

1. **Observation** — the raw, governed output of a reasoning cycle
   (`runtime/intelligence/signal.py:Observation`). An Observation is recorded
   evidence, never an inference (ADR-008, CR-9R/T).
2. **Signal** — a governed promotion of an Observation to enterprise attention
   (`runtime/intelligence/signal.py:Signal`). A Signal MUST carry classification,
   severity, confidence, owner, entities and rationale (CR-012 §3.2, §6.3).
3. **Pattern library** — declarative pattern definitions the loop can match
   against the graph (Phase 3).
4. **IntelligenceLoop** — the declarative, observable, pausable loop itself
   (Phase 4).
5. **ActionProposal** — a governed agent-initiated mutation that traverses the
   existing policy decision point (CR-9AK) before execution (Phase 5).

The architectural rules binding every layer:

- **A1 — Core is never extended.** Signals, patterns, loops, proposals ship in
  `runtime/intelligence/` and `metamodel/profiles/intelligence/`. The 18 core
  anchors are unchanged (CR-8 core-freeze, ADR-002).
- **A2 — Signals are governed observations, never assertions.** A signal without
  owner / classification / severity / confidence is malformed and rejected at
  construction.
- **A3 — Critical signals MUST declare an escalation policy.** A signal of
  severity `critical` without `escalation_policy_ref` is rejected at construction
  (CR-012 §3.5 severity vocabulary invariant).
- **A4 — Unbounded reasoning is rejected.** A loop without a declared `scope`
  cannot register (CR-012 §6.2).
- **A5 — Lifecycle is a directed graph.** No skipping: `open → acknowledged →
  in_review → ... → resolved`. Terminal states (`dismissed`, `resolved`) reject
  further transitions (CR-012 lifecycle.yaml invariant).
- **A6 — Agents never act silently.** Every agent-initiated mutation is an
  ActionProposal that traverses the existing policy decision point (CR-9AK,
  ADR-009). Approval is a one-way gate; execution is by the runtime APIs,
  not by the agent directly (ADR-007).
- **A7 — Audit chain is end-to-end.** Observation → Signal → ActionProposal →
  approval → execution is a single traceable chain (CR-9AM extended with
  `proposalId`).
- **A8 — Declarative loop, not procedural orchestration.** The loop is
  describable in the metamodel / profile. Implementations can short-circuit,
  replace components, or pause the loop. OpenDEA governs the *contract*:
  what enters, what exits, what is auditable.

## Consequences

Positive:
- The five layers compose cleanly over the existing runtime, scenarios, agents,
  and federation without forcing a migration.
- The `Signal` first-class type makes recurring situations visible at the
  governance surface; the previous "ask, answer, forget" pattern is replaced
  by an audit-traceable artifact.
- The ActionProposal lifecycle (Phase 5) makes "what did the agent do and
  why?" answerable from a single query — answering a long-standing gap
  identified in CR-7 governance and CR-9.8 PDP work.

Negative / foreclosed:
- The intelligence layer cannot be a hard-coded Python orchestration loop that
  consumers cannot override (A8). This rules out the simplest implementation
  paths and pushes declarative description to the profile.
- A loop that wants to produce `critical` severity signals MUST declare an
  escalation policy (A3). Loops that cannot or will not are rejected. This
  is intentionally strict: it prevents the worst failure mode of an
  intelligence layer (silent critical events).
- Signals cannot carry `approved: true` in `proposed_action` — that field is
  reserved for ActionProposal (Phase 5). This forces the governance seam
  between "what the situation is" and "what we will do about it".

## References

- CR-012 §3.1 (Observation), §3.2 (Signal), §6 (design constraints)
- `runtime/intelligence/signal.py` — Signal / Observation model
- `runtime/intelligence/store.py` — SignalStore
- `metamodel/profiles/intelligence/` — profile + 8 vocabularies
- ADR-002 (Core vs Profiles) — explains why signals ship in a profile
- ADR-007 (Runtime/API separation) — explains why the loop consumes APIs
- ADR-008 (Inference vs authoritative knowledge) — explains why Signals
  are governed observations, not silent assertions
- ADR-009 (Agent authorization model) — explains the PDP that
  ActionProposals will traverse