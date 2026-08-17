# Temporal, Lifecycle & Transition Semantics (CR-6)

> **Architecture is a time-dependent state of an enterprise, not a static catalogue of entities. (CR-6 §1)**

This note is the knowledge-base companion to [`change-requests/CR-006.md`](../change-requests/CR-006.md).
It captures the key ideas that shape the lifecycle profile so readers can understand the
thinking embedded in the artefacts, not just the artefacts themselves.

## 1. Nine things that must not be conflated (§1)

EXISTENCE · VALIDITY · VERSION · STATE · LIFECYCLE · CHANGE · TRANSITION · INTENTION · REALIZATION

"Application A exists", "A existed in 2024", "A is planned for 2027", "A is being replaced",
"A was scheduled for retirement" and "A was actually retired" are different statements.
A metamodel that cannot tell them apart cannot govern transformation.

## 2. The five clocks (§5–§6)

| Clock | Fields | Meaning |
|---|---|---|
| Transaction | `recorded_at`, `updated_at` | when the model **knows** something |
| Valid | `valid_from`, `valid_to` | when something **is true** in the enterprise |
| Observation | `observed_at` | when something was **observed** (CR-5 §22 aligned) |
| Planned | `planned_start`, `planned_end` | when something is **expected** — never actual |
| Effective | `effective_from`, `effective_to` | when a decision/change **takes effect** |

Canonical example (§6): retirement decided in Aug 2026 for Jan 2027 yields
`recorded_at=2026-08-17`, `planned_end=2027-01-01`, `valid_to=2027-01-01` — three facts,
never one `retirement_date`.

## 3. State model (§9–§13)

```
Baseline ──→ Current ──→ Transition 1 ──→ … ──→ Target
                          (plateaux, never a jump)
```

- **CurrentState** — authoritative *actual* elements/relationships/lifecycle states.
  Planned, proposed, target and hypothetical elements are excluded (T003).
- **BaselineState** — a *formally adopted* reference; not "whatever the model contains" (§10).
- **TargetState** — intended future condition. Target ≠ Current ≠ Planned Change ≠ Forecast (§12/§27; T006).
- **TransitionState** — real transformation moves through plateaux (§13).
- **ScenarioState** — hypothetical, under declared `ScenarioAssumption`s, contained inside
  `dea:Scenario`; never contaminates the authoritative architecture (§25–§26; T007).

## 4. Lifecycle ≠ maturity; event ≠ state (§8, §29)

An Application can be **Active** (lifecycle) while its Capability sits at **DMM Level 3**
(assessment, CR-5). A **LifecycleEvent** (retired, 2027-03-15, architecture-board) is the
audit record; the resulting **Retired** state is temporally bounded — history is never
overwritten (§17).

## 5. Version ≠ lifecycle ≠ supersession (§18–§20)

`CRM v1.0 → v1.1 → v2.0` is identity evolution (`Version` + `precedes`, acyclic — T008).
Operational state is lifecycle. "Application A superseded-by Application B" spans different
products. Three concepts, three mechanisms.

## 6. Snapshots, baselines, deltas (§30–§33)

- **ArchitectureSnapshot** — a capture (audit, regulation, comparison). Approved snapshots
  are immutable except via `revision_of` (T010).
- A snapshot `may-become` a Baseline — adoption is an act, not a default (§31).
- **ArchitectureDelta** — the *derived* semantic difference between two states:
  added / removed / modified / replaced / reclassified + relationship changes.
  This is the native answer to *"what must change to move from here to there?"* — the
  bridge between DMM, target architecture, transformation and roadmaps (§33).

## 7. Temporal relationships (§21–§22)

Edges are time-aware too: `supports` between Application A and Capability X may hold
2024→2027, then Application B takes over. Relationship instances carry
`valid_from` / `valid_to` / `status` / `recorded_at`. A **planned** edge must never render
as a current edge (T004).

## 8. Change formalized (§15–§16, §34–§35)

Change introduces / removes / modifies / replaces elements, realizes TargetState, and
results-in Outcomes. Changes depend on and enable other Changes (dependency-aware
transition). Transition constraints ("B cannot start until A completes", "Capability X
must reach maturity ≥ 3 first") are declared rules, not application logic. Planned vs
actual is mandatory: intended retirement 2027-01-01 vs actual 2027-03-15 are both
first-class.

## 9. The practical test (§38/§44)

*What supported Customer Service in 2025?* → A. *Today?* → A. *Planned?* → B.
*After the transition?* → B. If the graph answers these without undocumented application
logic, CR-6 has succeeded.

## 10. What this enables next (§45–§46)

```
CORE ONTOLOGY + ASSESSMENT + LIFECYCLE
        │            │            │
     Elements     DMM/results   Time/State/Version/Event/Change/Transition
        └────────────┼────────────┘
                     ↓
             TRANSFORMATION
        Current → Delta → Change → Target → Outcome → Reassessment
```

**Structure + Assessment + Time + Change** is the foundation CR-7 builds on for
Decision, Intent, Policy, Governance & Agentic semantics.

---

*Artifacts: `metamodel/profiles/lifecycle/` (temporal.yaml · lifecycle.yaml · states.yaml ·
transitions.yaml · constraints.yaml) · T001–T010 in `tests/conformance/test_012_temporal_rules.py`.*
