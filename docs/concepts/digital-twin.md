# OpenDEA and the Digital Twin

> **KB note — OpenDEA is *not* a digital twin merely because it models
> entities and relationships. A digital twin is a much stronger claim
> with explicit minimum requirements, and the gap between OpenDEA today
> and a real twin is the work CR-10 §28–29 (CR-10AA/AB) and §H are
> designed to close.** Source: CR-10 §28–29 (CR-10AA/AB), §H, grounded
> in [CR-9AT](../change-requests/CR-009.md) (digital-twin distinction)
> and [CR-9AS](../change-requests/CR-009.md) (simulation boundary).
> Companion notes: [four-state-model.md](four-state-model.md),
> [truth-model.md](truth-model.md), [semantic-lifecycle.md](semantic-lifecycle.md).

## 1. The plain statement

**OpenDEA is NOT a digital twin merely because it models entities and
relationships.** Saying so would collapse four distinct concepts into
one — the exact collapse [CR-9AT](../change-requests/CR-009.md) warns
against:

```
Architecture Model
       ↓
Operational Model
       ↓
Observed State
       ↓
Simulation Model
       ↓
Digital Twin
```

CR-9AT's discipline is that **the prerequisites be established, not
that the concepts be prematurely collapsed** ([runtime-architecture.md §9](../runtime-architecture.md)).
CR-10 §28–29 (CR-10AA/AB) and §H reinforce that discipline: CR-10
Phase 7 is the **twin foundation**, and it **MUST NOT be claimed
complete** until the twin-grade requirements below are met.

## 2. Minimum digital-twin requirements

A digital twin is a persistently synchronised, behaviourally faithful
virtual counterpart of a physical or operational system. The CR-10 §H
minimum requirements are six. OpenDEA MUST demonstrate all six before
*twin* is a defensible label:

| # | Requirement | What it means | Where OpenDEA stands today |
|---|---|---|---|
| 1 | **A physical or operational counterpart** | The twin represents a specific, named system — a plant, a fleet, a service, an enterprise portfolio — not "architecture in general". | **Partial.** OpenDEA can name any entity, but the counterpart is typically the *enterprise*, not a specific operational system. Twin deployments scope down. |
| 2 | **Persistent identity** | The same entity in the twin maps to the same entity in the world, across time, across reorganisations, across integrations. | **Implemented.** `dea:` namespace + identity resolution (CR-9M/N) — verdict same/related/different/unknown, `matchScore`, never-merge-on-uncertain. |
| 3 | **State synchronisation** | The twin's state is *kept in step* with its counterpart via integration pipelines — not periodically reconciled by hand. | **Partial.** CR-9.4 (events, snapshots, drift) is proposed; today the runtime can ingest via CR-9J adapters but synchronisation is not continuous. |
| 4 | **Observations** | The twin receives signals from the world — telemetry, events, assessments, human reports — timestamped and attributable. | **Implemented** at the data-shape level (CR-9E, CR-9AZ), **partial** at the integration level (CR-9.4, CR-9.5). |
| 5 | **Temporal state** | The twin knows *what is true now*, *what was true then*, and *what is expected next* — with valid time, transaction time, observation time, planned time, effective time. | **Implemented** for the foundations (CR-6: `valid_from / valid_to`, `at=` queries); **proposed** for full bitemporal (CR-9G, CR-9.4). |
| 6 | **Behavioural model** | The twin can answer "what would happen if X?" — not merely "what is?". Behaviour is a first-class semantic concept, with declared rules, declared reasoning level, declared uncertainty. | **Proposed.** CR-9Q (reasoning engine), CR-9BJ (scenario engine), CR-10AA (simulation), CR-10AB (twin semantics) — the largest single programme of work in CR-10. |

A system that has 1–5 but not 6 is a *digitally shadowed architecture
model*, not a twin. A system that has 6 but not 3 is a *simulation*,
not a twin. The label is reserved for the intersection.

## 3. The maturity ladder (CR-10 §H)

OpenDEA does not jump from "metamodel" to "digital twin". It climbs a
ladder. CR-10 §H names six rungs:

```
Semantic Metamodel
       ↓
Enterprise Model
       ↓
Observed Architecture
       ↓
Operational Model
       ↓
Dynamic Simulation
       ↓
Digital Twin
```

Each rung adds a structural capability that the rung below did not
have. The ladder is the *only* honest progression: claiming rung 6
without rung 5 is unfounded; claiming rung 5 without rung 4 is
unsafe; and so on.

### 3.1 Semantic Metamodel

A normative semantic specification: Core, profiles, envelope,
naming, conformance rules. **OpenDEA is here as of CR-4 / CR-8.**
This rung is necessary but not sufficient for any EA value beyond
catalogue consistency.

### 3.2 Enterprise Model

The semantic metamodel *applied* to a specific enterprise: a
canonical model of the customer's capabilities, services, applications,
information, organisations, decisions, outcomes. **OpenDEA is here
in practice** — customers load their enterprise into OpenDEA and the
runtime can answer structural queries, validate conformance, and
serve a viewer. This is *not* a twin.

### 3.3 Observed Architecture

The Enterprise Model with *evidence-derived* signals bound to it:
freshness-tagged observations (`lastObserved`, `lastSynced`,
`stalenessStatus`), assessment results from declared frameworks,
assertion statuses, evidence graphs. **OpenDEA is approaching this
rung**: CR-5/CR-9 added the substrate (assessments, evidence,
assertion lifecycle); CR-9.4 (proposed) adds continuous event-driven
observation. The drift engine (CR-9BD/BE) detects divergence
between observed and current — a structural capability that exists
*only* at this rung and above.

### 3.4 Operational Model

The Observed Architecture with *decision and change* as
first-class semantic operations. Decisions are linked to evidence
and architecture (CR-7 §12, CR-9AD/AE/AF); Changes realise Target
State and result in Outcomes (CR-6E, CR-9AF/AG); Outcomes feed
back to Evidence. **OpenDEA is approaching this rung**: the
closed-loop transformation CR-9AG) and the decision-change
linkage (CR-9AF) are defined, but the operational discipline
(decision lifecycle, change linkage, outcome capture) is not yet
the primary use of the runtime. CR-10 closes that gap.

### 3.5 Dynamic Simulation

The Operational Model with a *behavioural engine* attached:
Scenarios are run, predictions produced, impact graphs computed,
without mutating production. **OpenDEA is not yet at this rung.**
The scenario engine (CR-9BJ) and the simulation boundary
(CR-9AS) define the prerequisites; the simulation engine itself
is CR-10AA. Until CR-10AA, calling a Scenario "a simulation" is
the truth-model slip discussed in
[truth-model.md §7](truth-model.md) (Simulated class) — the
output is *Predicted* (Forecast), not *Simulated* (engine
output).

### 3.6 Digital Twin

Dynamic Simulation with *persistent state synchronisation* and
*behavioural fidelity*. The twin reflects the world's state, not
only its structure. The twin's predictions close the loop with
reality, and reality's changes close the loop with the twin.
**OpenDEA is not yet at this rung.** CR-10AB (twin semantics)
plus the synchronisation work of CR-9.4 plus the simulation
engine of CR-10AA together define the rung. It is the largest
single scope in the CR programme; it is also the rung most
often mis-claimed, and CR-10 §H is explicit that the claim
MUST NOT be made prematurely.

## 4. The conceptual progression (CR-9AT, verbatim)

CR-9AT draws the progression explicitly:

```
Architecture Model
       ↓
Operational Model
       ↓
Observed State
       ↓
Simulation Model
       ↓
Digital Twin
```

CR-9AT's argument is that CR-9 should "establish the
prerequisites, not prematurely collapse these concepts". CR-10
extends the argument: CR-10 §28–29 (CR-10AA/AB) and §H establish
the next rung on the ladder — simulation and twin semantics —
without collapsing any of the four concepts below into it. Each
remains a first-class, separately-confused subject.

## 5. The simulation boundary (CR-9AS, CR-10AA)

The simulation boundary separates "what we believe" from "what would
happen if". OpenDEA draws the boundary structurally:

```
Current State
   +
Proposed Change
   →
Simulated State
```

For example: "What would happen if Application X were retired?"
The engine produces an impact graph — affected capabilities, cost
assumptions, risk, dependencies, maturity impact, agent impact
(CR-9BJ) — **without modifying production state**. This is the
foundation CR-9 lays for the CR-10 simulation engine.

Three structural rules keep the boundary intact (CR-9AS, CR-10AA):

1. **Scenarios are sandboxed** ([four-state-model.md §3.2](four-state-model.md)).
   They MUST NOT contaminate the production graph; only a Decision
   followed by a Change can move a Scenario into Current.
2. **Simulated states are first-class.** They are not "draft
   Current" or "almost Target". They are outputs of a behavioural
   engine, with their own provenance, their own confidence, their
   own decay (a simulation older than its inputs is no longer
   trustworthy).
3. **The simulation engine is replaceable.** Different
   implementations may compute different Simulated states from
   the same Scenario — and that's expected. The semantic
   contract is on the *boundary*, not on the internal model.

## 6. Where OpenDEA stands today

Today OpenDEA sits **between the Enterprise Model rung and the
Observed Architecture rung**:

| Rung | OpenDEA status |
|---|---|
| Semantic Metamodel | **Reached** (CR-4, CR-8) |
| Enterprise Model | **Reached** (CR-1, CR-9.1 runtime) |
| Observed Architecture | **Approaching** — CR-9.4 (events, snapshots, drift) is proposed and is the rung-3 closure |
| Operational Model | **Approaching** — CR-9.7 (decision engine) and CR-9AG (closed-loop transformation) are proposed |
| Dynamic Simulation | **Foundation** — CR-9AS/BJ define the boundary; the engine is CR-10AA |
| Digital Twin | **Not reached** — CR-10AB (twin semantics) plus CR-9.4 synchronisation plus CR-10AA engine are required |

Concretely:

- **CR-9.1 implemented** — model loader, `GraphStore` ABC, in-memory
  reference store, provenance/temporal-retaining graph, vendor-
  independent contract suite, no silent inference (CR-9CQ), no
  autonomous mutation by default (CR-9CR). This is the
  Enterprise Model rung.
- **CR-9.4 (proposed)** adds the event model, bitemporal semantics,
  event-driven synchronisation, snapshots, `diff()`, and the drift
  engine. This is the Observed Architecture rung.
- **CR-10 Phase 7 (proposed)** lays the twin foundation — the
  simulation engine (CR-10AA) and the twin semantics (CR-10AB)
  atop the CR-9.4 synchronisation. **CR-10 Phase 7 MUST NOT be
  claimed as "twin delivered"** until both (a) **state synchronisation**
  is operational and (b) **behavioural semantics** are first-class.
  Without (a) the system is a model; without (b) it is a shadow.
  Neither alone is a twin.

## 7. The five anti-patterns to avoid

When teams start saying "we have a digital twin", CR-10 §H prescribes
checking for these failures:

1. **The catalogue twin.** The system models entities but receives no
   signals from the world. It is an architecture model, not a twin.
2. **The projection twin.** The system has a dashboard of the world
   but no underlying semantic model. It is a report, not a twin.
3. **The shadow twin.** The system has both, but synchronisation is
   periodic and lossy. It is a snapshot, not a twin.
4. **The simulation twin.** The system has scenarios and predictions
   but no live synchronisation. It is a simulator, not a twin.
5. **The AI twin.** The system has an LLM that talks about the
   enterprise fluently but cannot ground its answers in observed
   state with provenance. It is a storyteller, not a twin — and
   the [truth-model.md](truth-model.md) discipline is what prevents
   the storyteller from being mistaken for the twin.

## 8. The honest position

> OpenDEA is the **semantic foundation** that a digital twin needs.
> It is not, today, a digital twin in the strict sense. It is the
> substrate on which a twin is built — provided the next rungs
> (synchronisation, behavioural semantics, twin conformance) are
> built deliberately and the claim is held back until they are.

This is the position CR-9AT establishes, CR-10 §H reinforces, and
the conformance model in [../conformance-model.md](../conformance-model.md)
codifies. A claim of "digital twin" made before the requirements of
§2 are met is the [truth-model.md §3](truth-model.md) slip in its
most consequential form: an Inferred / Predicted / Simulated
artefact presented as if it were Observed reality.

---

*Companion concepts: [four-state-model.md](four-state-model.md)
(Current / Target / Scenario / Observed — the four dimensions a
twin must keep distinct); [truth-model.md](truth-model.md) (no
silent inference — the discipline that keeps simulation honest);
[semantic-lifecycle.md](semantic-lifecycle.md) (the loop that a
twin runs); [../runtime-architecture.md](../runtime-architecture.md)
§9 (CR-9AT, CR-9BG — architecture baselines that coexist).*