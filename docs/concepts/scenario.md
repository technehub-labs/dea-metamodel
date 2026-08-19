# The Scenario Concept (CR-10A–H, Phases 1–2 implementation)

> Concept doc for the CR-10 scenario model. Implementation:
> `runtime/scenario/` · Tests: `tests/runtime/test_scenario_foundation.py`,
> `tests/runtime/test_impact_engine.py` · Golden example:
> `models/scenarios/customer-platform-replacement.yaml`.

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

## Phase 2 — impact engine (CR-10G/H)

Phase 2 turns the simulated state into an explainable impact report:

```text
Scenario
   ↓
Change (explicit delta)
   ↓
Affected Entity
   ↓
Dependency Graph
   ↓
Direct / Indirect Impact
   ↓
Architecture Delta
```

`runtime/scenario/impact.py` provides:

- **Impact graph (CR-10G):** `ImpactEngine.propagate()` walks active dependency
  edges from each change target, records the exact relationship path, and
  classifies depth 1 as **direct impact** and depth > 1 as **indirect impact**.
- **Impact categories:** strategic, business, capability, process, customer,
  data, application, technology, security, risk, agent, governance, financial,
  operational.
- **Impact ≠ valence (CR-10H):** removal is not automatically negative.
  Valence is `Positive / Negative / Neutral / Mixed / Unknown`, defaults to
  `unknown`, and changes only through explicit caller-supplied rules.
- **Change analysis:** each of the eleven delta operations is reported as
  added / removed / modified entities plus its propagated impacts.
- **Architecture delta:** `architecture_delta(before, after)` compares graph
  snapshots by canonical identity — added, removed and modified entities and
  relationships — without conflating a metadata change with a delete/recreate.
- **Impact report:** `ImpactEngine.evaluate(scenario, baseline)` returns the
  frozen simulated-state delta and the merged impact graph; the baseline is
  still never mutated.

```python
from runtime.scenario import ImpactEngine

report = ImpactEngine().evaluate(scenario, baseline)
report.delta.added_entities       # ["platform.customer-v2"]
report.impacts[0].path            # exact dependency path
report.impacts[0].valence         # explicit; unknown unless configured
```

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

## Simulation levels (CR-10K) — current boundary

| Level | Name | Question | Status |
|---|---|---|---|
| 0 | Structural | "What depends on X?" | **Implemented** — delta application, simulated graph, impact graph, architecture delta |
| 1 | Rule-based | "If X is removed, Y becomes non-compliant" | Seeded — explicit valence rules; compliance/rule evaluation lands with decision intelligence |
| 2 | Quantitative | cost, capacity, time, risk, maturity | Phase 3 |
| 3 | Probabilistic | Monte Carlo, distributions | interface (CR-10P) |
| 4 | Dynamic | time-dependent behavior | CR-10 Phase 7 |
| 5 | Digital Twin | continuously synchronized state | CR-13 |

Phase 2 implements structural impact propagation, change analysis and
architecture delta. Constraint evaluation, comparison (CR-10F), scoring,
ranking (CR-10M/N) and recommendation remain Phase 3 decision intelligence.

## Security note (CR-10AU)

Scenario data is among the most strategically sensitive content in the
platform — it describes futures, budgets and weaknesses. Scenarios do **not**
automatically inherit baseline visibility: classification, authorization,
tenant isolation, ownership and audit apply per scenario. Enforcement arrives
with the CR-9.8 security profile; the principle is recorded now so no later
design assumes inheritance.
