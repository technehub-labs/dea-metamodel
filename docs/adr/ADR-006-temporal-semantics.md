# ADR-006: Temporal semantics

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

Time in an enterprise is multi-dimensional: things are observed at one
moment, asserted at another, valid from a third to a fourth, planned to
come into existence, and superseded by something newer. CR-6 §22
introduced the discipline that *planned ≠ current*: a planned application
is not yet observed; a deprecated one is no longer current. CR-9G
formalized the bitemporal direction the runtime must support
(`assertion_time` and `valid_time`). CR-10 scenario evaluation (CR-10 §3,
CR-10B) depends on the same discipline: scenarios operate on a baseline
"as of" a temporal point, and the difference between what *is* and what
*is planned to be* is the very input scenarios act on.

## Decision

- OpenDEA **MUST** carry the five clocks established in CR-6:
  **observed_at**, **asserted_at**, **valid_from** / **valid_to**,
  **planned_from** / **planned_to**, and **superseded_at**.
- The runtime **MUST** support bitemporal indexing per CR-9G: assertions
  are indexed by both *assertion time* (when the claim was made) and
  *valid time* (when the claim held in the world). Both axes are
  independent and both are queryable.
- `planned` **MUST NOT** be treated as `current`. A planned application,
  transition, or relationship has its own lifecycle status and **MUST
  NOT** appear in current-state queries unless explicitly requested.
- A claim's effective state at any moment `t` **MUST** be derivable by
  querying `valid_time ∩ assertion_time ∩ lifecycle_status` — never by
  reading a single "current" flag.
- Scenario evaluation **MUST** operate against a baseline `as_of` a
  declared temporal point plus deltas; the temporal discipline above
  applies to the baseline just as it does to production state.

## Consequences

- Positive: scenarios, retrospectives, and audits can all be answered
  from the same graph without separate "historical" replicas.
- Positive: planned vs current is unambiguous, preventing premature
  promotion of planned artefacts to authoritative status.
- Negative: every state-bearing edge carries more metadata; consumers
  must learn to ask "as of when?" rather than expecting a single
  current view.
- Forecloses: a single `is_current: true` flag per entity; silent
  promotion of planned artefacts; collapsing assertion time and valid
  time into one timestamp.

## References

- CR-6 §22 — planned ≠ current, five clocks
- CR-9G — bitemporal direction
- CR-10 §3, CR-10B — scenario baseline + deltas
- docs/temporal-semantics.md