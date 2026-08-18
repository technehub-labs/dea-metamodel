# ADR-003: Canonical identity

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

CR-8 §7 established that human-readable names are display affordances and
*not* identity. Every anchor, relationship, assertion, evidence item and rule
in OpenDEA must have a stable, machine-resolvable identifier that survives
re-import, profile extension, federation, and replication. The CR-9 graph
runtime (CR-9D) inherits this: graph identity is a property of the *node or
edge*, never of the *display label*. Treating names as identities causes
silent collisions ("Finance" the application vs "Finance" the capability)
and breaks cross-repository federation.

## Decision

- Every entity, relationship, assertion, evidence item, rule, profile, and
  vocabulary term in OpenDEA **MUST** carry a canonical, stable identifier.
- Identifiers **MUST** be lowercase, dot-namespaced strings
  (e.g. `opendea.entity.capability`, `finance.application.general-ledger`)
  per CR-8 §7 and the naming-conventions specification.
- Identifiers **MUST NOT** change over the lifetime of the concept, even if
  the human-readable label changes. Supersession creates a new identifier
  and an explicit `supersedes` link.
- Human-readable names (`rdfs:label`, `name` properties) **MUST** be
  treated as display hints only; they **MUST NOT** be used as lookup keys
  for identity, merging, or deduplication.
- Profile-defined identifiers **MUST** be namespaced under the profile's
  own prefix to prevent collision with Core or other profiles.

## Consequences

- Positive: stable federation across repositories and tools; correct
  deduplication on re-import; safe renames.
- Positive: identifiers double as URI fragments for serialization, graph
  identity, and rule references.
- Negative: stricter authoring discipline — labels are not enough; every
  new concept needs an explicit identifier at creation time.
- Forecloses: label-based merging; case-variant identifiers ("Finance"
  vs "finance"); identifiers embedded in human copy that drift over time.

## References

- CR-8 §7 — identity and naming
- CR-9D — graph identity in the runtime
- specification/naming-conventions.md
- specification/type-system.md