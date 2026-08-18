# ADR-001: OpenDEA as semantic foundation

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

The CR sequence (CR-1…CR-9) progressively built an enterprise-architecture
semantic metamodel and a frozen specification (CR-8 v1.0.0) plus an executable
runtime (CR-9). CR-10 §P reiterates that OpenDEA is the *semantic contract*
that lets heterogeneous participants **represent, connect, govern, assess,
reason about, and evolve** an enterprise consistently — not "another EA
modelling tool". The tension is between treating OpenDEA as a modelling
language for documents and treating it as the substrate that runs the
`Observe → Model → Assess → Reason → Decide → Act → Observe` loop. Drift
toward the former collapses it into a drawing tool; drift toward the latter
without a semantic contract couples it to one implementation.

## Decision

- OpenDEA **MUST** be treated as the semantic foundation of an enterprise
  architecture programme: the normative contract for representing,
  connecting, governing, assessing, reasoning about, and evolving the
  enterprise.
- OpenDEA **MUST NOT** be positioned, marketed, or extended as an EA
  modelling tool (diagrammers, document repositories, or visualisation
  suites). Such tools consume OpenDEA; they do not define it.
- All CRs that propose a new domain of semantics **MUST** show how the new
  semantics fits the `Observe → Model → Assess → Reason → Decide → Act`
  loop and which existing core/profiles it extends.
- The specification (CR-8) and the runtime (CR-9) **MUST** remain
  authoritative over any viewer, profile, or tool. Tools render or act on
  OpenDEA; they do not redefine it.

## Consequences

- Positive: a single semantic contract for the entire programme; tools are
  interchangeable; the closed loop is the test of fitness.
- Positive: clear ownership — CR-8 owns semantics, CR-9 owns execution,
  CR-10+ owns the closed loop on top of both.
- Negative: any tool that wants to "extend" OpenDEA must do so via a profile
  (ADR-002) rather than by widening the spec.
- Forecloses: collapsing OpenDEA into a repository or diagram tool;
  vendor-specific semantics masquerading as OpenDEA extensions.

## References

- CR-10 §P — OpenDEA as semantic foundation
- CR-8 — OpenDEA Semantic Architecture & Conformance Specification v1.0.0
- CR-9 §1, §101 — runtime strategic intent and design discipline
- docs/runtime-architecture.md §1, §2