# ADR-013: The Core does not accumulate — adapters absorb external complexity

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

As CR-1…CR-11 assembled, a subtle architectural risk emerged (CR-11 §66):
the metamodel could become an accumulation of every concept the platform
touches. Each new integration, domain or standard brings candidate concepts;
absorbing them into the Core would turn a semantic contract into a very
sophisticated application schema — coupled, unstable, and unimplementable by
third parties. CR-8 already froze an 18-anchor Core with an anti-inflation
rule; CR-11 makes the complementary rule for the *integration* side explicit.

## Decision

- The OpenDEA Core **MUST** remain close to: Identity (entities, profiles),
  Semantics (relationships, constraints), State (assertions, evidence,
  provenance). Domain and integration concepts **MUST NOT** enter the Core
  to serve a single consumer.
- Everything else **MUST** sit above or beside the Core: applications (DMM,
  AI/agents, scenarios) above; external systems and standards (ArchiMate,
  BPMN, DMN, CMDB, GRC, data catalogs) beside it, connected through
  adapters and mappings (CR-11 §2).
- Every external concept without canonical correspondence **MUST** be
  preserved as a namespaced extension (CR-11AR), never discarded and never
  merged into the Core.
- Integrations **MUST NOT** modify the Core; they extend through profiles
  (ADR-002) or map through governed `SemanticMapping` assets (CR-11AT).

## Consequences

- Positive: the Core stays stable and independently implementable; external
  complexity is absorbed at the boundary; OpenDEA can credibly claim to be
  a semantic layer through which heterogeneous systems interoperate without
  adopting its metamodel (CR-11 strategic outcome).
- Positive: mappings and profiles can evolve (versioned, governed) without
  destabilizing the contract.
- Negative: some external semantics remain lossy at the boundary — declared
  via mapping lossiness (CR-11AQ) rather than hidden.
- Forecloses: vendor-driven Core additions; "just add it to the metamodel"
  as an integration strategy.

## References

- CR-11 §2, §66 — adapters absorb external complexity; the correction
- CR-11 §46-47 (CR-11AR/AS) — extensions and namespaces
- CR-8 §3-§4 — Core freeze and anti-inflation rule
- ADR-002 — Core versus Profiles
- [docs/interoperability/overview.md](../interoperability/overview.md)
