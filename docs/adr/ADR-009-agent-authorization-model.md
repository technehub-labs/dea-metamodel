# ADR-009: Agent authorization model

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

CR-9 introduces agents that act on the graph: read, query, infer, propose,
and — under explicit authority — write. CR-9CR establishes the safe
default: agents are read-only unless they have been granted write
authority. CR-9AJ defines the authority chain `Agent → Role → Authority →
Policy → Scope → Action` as the only path by which a write is admitted.
CR-9AK specifies the policy decision point (PDP) decision outcomes
`ALLOW / DENY / ESCALATE`. CR-9AL mandates policy-driven human-in-the-loop
(HITL): any action above the agent's autonomous authority is escalated to
a human approver and the decision is recorded. CR-10 inherits all of this
unchanged; scenarios, simulations, and decision support are all agent
surfaces and must operate under the same authorization discipline.

## Decision

- Agents **MUST** be read-only by default (CR-9CR). Write authority **MUST
  NOT** be granted by default, by inheritance, or by convenience.
- An agent's authority to act **MUST** be derivable from the chain
  `Agent → Role → Authority → Policy → Scope → Action` (CR-9AJ). Every
  step **MUST** be resolvable; missing links **MUST** result in `DENY`.
- The PDP **MUST** return one of three outcomes: `ALLOW`, `DENY`, or
  `ESCALATE` (CR-9AK). There is no fourth silent outcome.
- A write that exceeds the agent's authority **MUST** be escalated via a
  policy-driven HITL path (CR-9AL). The escalation **MUST** record the
  policy, the proposed action, the approver, the decision, and the
  resulting state transition.
- The authorization decision **MUST** be logged in the same provenance
  chain as the action it permitted or denied (ADR-005): an action without
  a resolvable authorization trail **MUST NOT** be admitted.
- Scenario evaluation, simulation, and decision support in CR-10 **MUST**
  operate as agents under this model — they **MUST NOT** bypass it to
  write directly.

## Consequences

- Positive: every write is attributable to an authorised, logged
  decision; the closed loop is auditable end-to-end.
- Positive: the default (read-only) keeps a misbehaving agent from
  corrupting the graph; escalation is the norm, not the exception.
- Negative: more ceremony for legitimate writes; performance-critical
  paths need pre-resolved authority caches, not shortcut checks.
- Forecloses: service accounts with broad write authority; agents that
  write "because they're useful"; implicit trust between a viewer and
  the runtime.

## References

- CR-9CR — read-only by default
- CR-9AJ — authority chain
- CR-9AK — PDP `ALLOW / DENY / ESCALATE`
- CR-9AL — policy-driven HITL
- ADR-005 — provenance model