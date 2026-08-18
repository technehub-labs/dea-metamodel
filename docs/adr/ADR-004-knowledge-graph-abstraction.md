# ADR-004: Knowledge graph abstraction

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

CR-9 §5 (CR-9D) defines the `GraphStore` interface as the single boundary
between semantic services (validation, reasoning, assessment, decision,
agent interaction) and the persistence technology that backs them. CR-9BV
calls out the risk of conflating the *reference* in-memory implementation
with the *only* valid implementation. The runtime must be able to run on
Neo4j, Neptune, ArangoDB, PostgreSQL+graph, RDF triplestores, or other
stores, with conformance demonstrated against the contract suite rather
than against a chosen product. The closed-loop scenarios in CR-10 inherit
this: scenario evaluation, simulation, and decision support must work
against any conformant `GraphStore`.

## Decision

- All OpenDEA semantic services **MUST** depend only on the `GraphStore`
  interface (CR-9D): `createEntity`, `updateEntity`, `deleteEntity`,
  `createRelationship`, `query`, `traverse`, `findPath`, `infer`,
  `transaction`.
- Vendor-specific features **MAY** be used inside a `GraphStore`
  implementation, but **MUST NOT** leak through the interface into the
  semantic services that consume it.
- The in-memory reference implementation (`InMemoryGraphStore`) is the
  reference contract demonstrator and the test fixture; it **MUST NOT**
  be treated as the production default, and its API **MUST NOT** be
  copied verbatim into other implementations.
- A new store **MUST** demonstrate conformance by passing the
  vendor-independent contract suite
  (`tests/runtime/test_graphstore_contract.py`) under the CR-9CL conformance
  regime.
- Edges **MUST** be first-class (CR-9E): they carry provenance, temporal
  validity, lifecycle status, and arbitrary properties — never bare
  source→target pairs.

## Consequences

- Positive: the runtime is technology-neutral; deployments can pick the
  store that fits scale, ops, and licensing.
- Positive: the same scenario / simulation / decision logic runs against
  every conformant store.
- Negative: a feature available in one store but not expressible through
  the interface must wait for an interface extension, not a leak.
- Forecloses: product lock-in; semantic services that import a vendor
  driver directly; reference-implementation behaviour treated as
  normative.

## References

- CR-9 §5 (CR-9D) — GraphStore interface
- CR-9E — first-class edges
- CR-9BV — reference vs production implementations
- CR-9CL — runtime conformance regime
- docs/runtime-architecture.md §4