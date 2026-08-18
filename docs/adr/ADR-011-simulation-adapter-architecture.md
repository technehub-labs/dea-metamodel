# ADR-011: Simulation adapter architecture

- Status: Accepted
- Date: 2026-08-18
- Deciders: OpenDEA architecture programme (CR sequence)

## Context

OpenDEA is a semantic coordination layer, not a simulator. Discrete-event,
agent-based, system-dynamics, cost, capacity, and risk simulators each
have their own domain, their own modelling primitives, and their own
vendors. CR-10 §30–32 (CR-10AC, CR-10AD) defines the
`SimulationAdapter` boundary: external simulators plug in via five
operations — `prepare`, `execute`, `retrieveResults`, `mapResults`,
`validate` — and produce results that flow back into the OpenDEA graph as
*inferred* claims with full provenance. CR-10AE/AF require that result
provenance (input scenario, input parameters, simulator identity,
simulator version, run timestamp) be carried with the result so that any
simulation outcome is reproducible from the record alone.

## Decision

- OpenDEA **MUST** act as the semantic coordination layer for simulation,
  not as a simulator itself. The `SimulationAdapter` interface **MUST**
  be the only boundary through which external simulators are invoked.
- The `SimulationAdapter` **MUST** expose five operations: `prepare`
  (translate scenario + baseline + deltas into the simulator's input
  contract), `execute` (run the simulator), `retrieveResults` (pull
  raw outputs back), `mapResults` (translate outputs into OpenDEA
  inferred claims), `validate` (sanity-check mapping and result shape).
- The adapter **MUST NOT** bypass any of these five steps; in particular,
  results **MUST** flow through `mapResults` and **MUST** be validated
  before they enter the graph.
- Simulation results **MUST** enter the graph as inferred claims (see
  ADR-008), carrying the simulator's identity, version, input scenario
  id, parameter set, and run timestamp as provenance (CR-10AE/AF).
- Two runs of the same scenario against the same simulator version and
  the same parameters **MUST** be reproducible from the recorded
  inputs; any deviation **MUST** be visible in the result provenance.
- A conformant simulator **MUST** implement the `SimulationAdapter`
  contract; ad-hoc integrations that read or write the graph directly
  are forbidden.

## Consequences

- Positive: any simulator can be brought into the closed loop without
  modifying OpenDEA itself; the semantic contract stays clean.
- Positive: simulation results inherit the same epistemic discipline
  (inferred, not authoritative) and provenance discipline as other
  derived claims.
- Negative: adapters must be maintained per simulator; the five-step
  contract is heavier than a one-shot integration.
- Forecloses: OpenDEA growing its own simulator; results entering as
  authoritative; simulator outputs that cannot be re-derived from the
  record.

## References

- CR-10 §30–32 — `SimulationAdapter`
- CR-10AC, CR-10AD — five-operation contract
- CR-10AE, CR-10AF — result provenance for reproducibility
- ADR-005 — provenance model
- ADR-008 — inference vs authoritative knowledge