# ADR-007: Runtime/API separation

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

The CR-8 specification is normative for *what* OpenDEA means; the CR-9
runtime is normative for *how* the semantics are executed. CR-10 §N
warns explicitly against collapsing the viewer into the specification:
visualisation choices, query ergonomics, and product UX are not semantic
truth. CR-9BX makes the same point at the boundary: a viewer or agent
surface consumes runtime APIs, never the spec files directly; the
specification is consumed by the runtime itself when it loads core,
profiles, and conformance rules. The risk is silent coupling: a viewer
or tool that reads `metamodel.yaml` or the `ttl/` files directly becomes
a fork of the spec on the day those files change.

## Decision

- A viewer, agent interface, or any external surface **MUST** consume the
  runtime through its public APIs. It **MUST NOT** read, parse, or
  import the CR-8 specification artefacts (`metamodel.yaml`, `ttl/`,
  `core-freeze.yaml`, `semantic-inventory.yaml`) directly.
- The runtime **MUST** consume the specification: it loads core, profiles,
  schemas, rules, and vocabularies via the model loader (gated by the
  CR-8 validator `tools/opendea_validate.py`) and exposes their semantics
  through the service API.
- The relationship `Viewer → Runtime → Specification` is one-way and
  strictly layered. The reverse `Specification → Viewer` is forbidden.
- Visualisation-specific concerns (layout, colour, traversal ordering,
  query ergonomics) **MUST** live in the viewer's domain, never in the
  specification.
- Versioning of the viewer **MUST** track the runtime's API contract,
  not the specification's internal file layout.

## Consequences

- Positive: the specification can evolve its internal representation
  without breaking viewers, agents, or downstream tools.
- Positive: the runtime is the only place that needs to know how the spec
  is serialised, validated, and loaded.
- Negative: viewers cannot use the spec as a shortcut for "what types
  exist?" — they must ask the runtime, which has a cost.
- Forecloses: viewer-typed coupling; rendering choices becoming part of
  the semantic contract; vendors who distribute a "spec-aware" viewer
  that ships its own copy of the metamodel.

## References

- CR-10 §N — viewer ≠ specification
- CR-9BX — viewer/runtime/spec layering
- CR-8 — specification artefacts
- docs/runtime-architecture.md §2 (six layers)