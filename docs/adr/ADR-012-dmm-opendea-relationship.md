# ADR-012: DMM / OpenDEA relationship

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

Two artefacts are routinely confused: the Digital Maturity Model (DMM) and
OpenDEA. They serve different purposes. The DMM (CR-5) is a *diagnostic and
assessment instrument*: it tells an organisation *how mature* it is along
defined capability dimensions, using surveys, scores, and level rubrics.
OpenDEA is the *semantic architecture and transformation substrate*: it
tells you *what exists* in the enterprise, *how it relates*, and *how it
can change* — across the full closed loop. CR-10 §F (CR-10S) wires them
together into one cycle: `DMM → Gap → OpenDEA → Scenarios → Decision →
Change → Reassessment`. The DMM surfaces the gap; OpenDEA expresses the
gap as a graph-level state; scenarios explore ways to close it; a decision
is taken; a change is applied; the DMM is reassessed to see whether the
gap closed. The risk being mitigated is treating the DMM as OpenDEA, or
OpenDEA as the DMM, and collapsing the cycle into a single artefact.

## Decision

- The DMM **MUST** be treated as a *diagnostic / assessment instrument*:
  it answers "how mature is the enterprise along dimension X?".
- OpenDEA **MUST** be treated as the *semantic architecture and
  transformation substrate*: it answers "what exists, how does it
  relate, and how does it change?".
- The two **MUST NOT** be conflated. The DMM is not a graph; OpenDEA is
  not a maturity rubric. Maturity levels **MUST** be carried in OpenDEA
  as assessment results under the assessment profile, with full
  provenance, not as ad-hoc labels on entities.
- The closed loop `DMM → Gap → OpenDEA → Scenarios → Decision → Change
  → Reassessment` (CR-10 §F, CR-10S) **MUST** be the canonical way the
  DMM is consumed inside OpenDEA.
  - A DMM assessment produces a *gap* expressed as a graph state.
  - The gap is the input to one or more scenarios (ADR-010).
  - A scenario outcome leads to a *decision* (assertion lifecycle).
  - The decision is realised as a *change* (transition / new assertion).
  - A *reassessment* runs the DMM again to close the loop.
- A DMM score that influences an authoritative decision **MUST** be
  recorded with full provenance (assessor, rubric version, evidence) so
  the reassessment can be trusted.

## Consequences

- Positive: the two artefacts stay specialised — diagnostic vs semantic —
  and reinforce each other through the closed loop.
- Positive: maturity work and architecture work share a single,
  auditable trajectory instead of two disconnected scoreboards.
- Negative: the loop has more steps and more roles than either
  artefact alone; reassessment discipline must be enforced.
- Forecloses: embedding the DMM inside OpenDEA (or vice-versa); using
  DMM scores as semantic truth; treating OpenDEA assessments as DMM
  scores.

## References

- CR-5 — DMM integration
- CR-10 §F, CR-10S — closed loop
- CR-9B — five kinds of knowledge (assessment is *asserted*, not *observed*)
- ADR-005 — provenance model
- ADR-008 — inference vs authoritative knowledge