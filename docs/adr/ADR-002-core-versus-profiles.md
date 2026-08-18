# ADR-002: Core versus Profiles

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

CR-8 froze the semantic core (the 18 anchors plus their core relationships)
and introduced the profile mechanism to extend it without fragmenting the
contract. The risk addressed here is that every new domain ("add a
sustainability anchor", "add a privacy relationship") would, if allowed into
core, force a new conformance level, a new spec version, and break the
implementations that already conformed. CR-10 relies on the discipline that
CR-8 established: scenario semantics (CR-10 §D), simulation semantics
(CR-10 §30–32), and decision semantics (CR-10 §F) all enter OpenDEA as
profiles rather than as core additions.

## Decision

- The OpenDEA **Core** (CR-8 core-freeze) **MUST** remain small, stable, and
  closed: 18 anchors plus their core relationships, plus the envelope,
  naming, and conformance rules. New core elements **MUST NOT** be added
  except by a new major version of the specification.
- Profiles **MAY** extend Core by declaring new entity types, relationship
  types, properties, rules, and vocabularies, provided they reference Core
  types rather than redefining them.
- Profiles **MUST NOT** redefine, narrow, or contradict Core semantics.
  Where a conflict is found, Core wins and the profile is invalid.
- New domain semantics (e.g. scenario, simulation, assessment profiles)
  **MUST** enter OpenDEA via a profile, not via Core mutation.
- A conformant implementation **MUST** support Core; support for any given
  profile is declared per-implementation in its conformance statement.

## Consequences

- Positive: Core is implementable once and stable across years; profiles
  evolve at domain speed.
- Positive: an implementation can be "Core-conformant" without committing
  to every domain that uses it.
- Negative: the cost of mis-classifying a concept (it goes in a profile when
  it should have been in Core, or vice-versa) is paid over years.
- Forecloses: ad-hoc widening of Core; profiles that override Core;
  vendors who advertise "extended OpenDEA" without publishing the profile.

## References

- CR-8 — core-freeze, profile mechanism
- specification/profile-mechanism.md
- specification/core-freeze.yaml
- CR-10 §D (truth model), §F (decision loop) — implemented as profiles