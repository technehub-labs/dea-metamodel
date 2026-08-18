# The Scenario Concept (CR-10A–C, Phase 1 implementation)

> Concept doc for the CR-10 scenario model. Implementation:
> `runtime/scenario/` · Tests: `tests/runtime/test_scenario_foundation.py` ·
> Golden example: `models/scenarios/customer-platform-replacement.yaml`.

## The principle

> **A scenario is a first-class semantic object, not a copy of the enterprise
> model** (CR-10 §1).

A scenario *references a baseline* and *contains only its delta* (CR-10B).
Evaluating a scenario produces a **simulated state** — a new graph — while the
baseline and the production/current state are never touched:

```
Current State
      │
   Baseline            ← frozen snapshot (CR-9BG baselines)
      │
      ├──────────────┐
      ↓              ↓
 Scenario A       Scenario B      ← deltas only
      │              │
      ↓              ↓
 Simulated        Simulated
 State A          State B
```

## The object model (CR-10A)

```
Scenario
 ├── id                  canonical identity (CR-8 §7)
 ├── name / description / owner / purpose
 ├── baseline            reference, never embedded copy
 ├── assumptions         explicit semantic objects (CR-10D)
 ├── changes             explicit delta operations (CR-10C)
 ├── constraints         explicit semantic objects (CR-10E)
 ├── affectedEntities    derived from the delta
 ├── expectedOutcomes    uncertainty-qualified (CR-10I/O)
 ├── status              lifecycle below
 ├── version             evaluated versions are immutable (CR-10AG)
 └── provenance          creator, source, supersedes chain (CR-10AH)
```

## Lifecycle (CR-10A)

```
Draft → Defined → Evaluating → Evaluated → Approved → Implemented → Closed
```

plus Rejected / Deferred / Superseded / Cancelled. The runtime enforces legal
transitions. **Approved is not self-service:** approval flows through the
decision machinery — a recommendation is never an approved decision
(CR-10AI).

## The delta vocabulary (CR-10C)

Eleven operations keep scenarios compact and traceable:

| Operation | Meaning | Phase-1 semantics |
|---|---|---|
| ADD | introduce an entity | registry-validated node |
| REMOVE | retire an entity | node + cascade edges |
| REPLACE | substitute one entity for another | new node + rewire edges |
| MODIFY | change properties/name/lifecycle | merged properties |
| RECLASSIFY | change an entity's type | registry-validated retype |
| CONNECT | add a relationship | registry-validated edge |
| DISCONNECT | remove a relationship | edge removal |
| ENABLE | activate | lifecycle → active |
| DISABLE | decommission | lifecycle → deprecated |
| MOVE | re-point a relationship | edge retarget, metadata kept |
| SCALE | change capacity | `scale` property |

## Assumptions, constraints, outcomes — never buried (CR-10D/E/I/O)

- **Assumption** — id, statement, value, unit, confidence, source, owner.
  *"Customer migration completes within 12 months" (confidence 0.75).*
- **Constraint** — subject, operator, value, unit, priority, source.
  *Budget ≤ $20M (mandatory), migration ≤ 18 months, availability ≥ 99.95%.*
- **Outcome** — metric, baseline, expected, target, unit, confidence,
  **uncertainty class** (Known / Estimated / Assumed / Predicted / Simulated /
  Unknown), timeframe, evidence. Forecasts are never deterministic facts
  (CR-10O).

## Immutability and reproducibility (CR-10AF/AG)

Once evaluated, a scenario version is **frozen**. Changing it means creating
`v2` — which records `supersedes: <id>@v1` in provenance — never silently
editing v1. Every scenario carries a `reproducibility_hash()` over its
canonical serialization: baseline version + scenario definition + assumptions
+ rules + simulation version must fully determine a result; no hidden mutable
state (CR-10AF).

## Simulation levels (CR-10K) — what Phase 1 does and doesn't do

| Level | Name | Question | Status |
|---|---|---|---|
| 0 | Structural | "What depends on X?" | **Phase 1 — implemented** (delta application + simulated graph) |
| 1 | Rule-based | "If X is removed, Y becomes non-compliant" | Phase 2 |
| 2 | Quantitative | cost, capacity, time, risk, maturity | Phase 2/3 |
| 3 | Probabilistic | Monte Carlo, distributions | interface (CR-10P) |
| 4 | Dynamic | time-dependent behavior | CR-10 Phase 7 |
| 5 | Digital Twin | continuously synchronized state | CR-13 |

Impact propagation (CR-10H, with impact *valence* — a removal can reduce debt
and increase migration risk simultaneously), constraint evaluation, comparison
(CR-10F), ranking (CR-10M/N) and recommendation land in Phases 2–3 on top of
the simulated state this phase produces.

## Security note (CR-10AU)

Scenario data is among the most strategically sensitive content in the
platform — it describes futures, budgets and weaknesses. Scenarios do **not**
automatically inherit baseline visibility: classification, authorization,
tenant isolation, ownership and audit apply per scenario. Enforcement arrives
with the CR-9.8 security profile; the principle is recorded now so no later
design assumes inheritance.
