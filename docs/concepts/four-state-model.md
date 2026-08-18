# The Four-State Model

> **KB note — Current, Target, Scenario, and Observed are four semantic
> dimensions, not four flavours of "the model". Conflating them is the
> single most common way enterprise-architecture data becomes
> untrustworthy.** Source: CR-10 §C, grounded in [CR-6 §9–§13](../change-requests/CR-006.md)
> and [CR-9AT / CR-9BG](../change-requests/CR-009.md). Companion notes:
> [truth-model.md](truth-model.md), [digital-twin.md](digital-twin.md),
> [../temporal-semantics.md](../temporal-semantics.md).

## 1. The four dimensions

OpenDEA represents an enterprise's architecture along four semantic
dimensions. Each answers a different question; each is structurally
distinct in the graph.

| Dimension | Question it answers | Anchor CR | Why it must not collapse |
|---|---|---|---|
| **Current** | *"What is the approved-current state of the architecture?"* | CR-6 §11, CR-9BG | It is what decisions are made against and what governance cites. |
| **Target** | *"What is the intended future state?"* | CR-6 §12, CR-9BH | Conflating Target with Current collapses "we want to be" into "we are" — the source of every EA integrity failure. |
| **Scenario** | *"What would the architecture look like under declared assumptions?"* | CR-6 §25–§26, CR-9BJ | Reading a Scenario as Current (or as Target) turns hypothetical exploration into authoritative fact. |
| **Observed** | *"What does evidence from the real world say is happening?"* | CR-9BD, CR-9AZ | Presenting Observed as Approved/Current hides drift and destroys auditability. |

## 2. The diagram (CR-10 §C)

```
                ┌───────────────────────────────┐
                │          Observed             │
                │  (evidence-derived real-world)│
                └──────────────┬────────────────┘
                               │ drift / freshness
                               ▼
        ┌──────────────────────────────────────────────┐
        │                   Current                    │
        │      (approved / authoritative now)          │
        └──────────────┬───────────────────────────────┘
                       │ approved change
                       ▼
        ┌──────────────────────────────────────────────┐
        │                   Target                     │
        │      (intended future condition)              │
        └──────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────┐
        │                  Scenario                    │
        │   (hypothetical — assumptions declared,       │
        │    never touches the production graph)       │
        └──────────────────────────────────────────────┘
```

The four boxes are **peers**. They are not stages in a pipeline and they
are not fields on a single entity. Each is a first-class dimension with
its own provenance, lifecycle and conformance rules.

## 3. Why conflating them corrupts architecture

Each pair has a characteristic corruption pattern. The CR-10 §C
discipline is to keep the four pairs separate in *every* artefact, model
and dashboard.

### 3.1 Current ↔ Target

| Symptom | What went wrong |
|---|---|
| A roadmap reads "current state = hybrid cloud" but the production evidence says on-prem dominates. | Target has been quietly used as Current — or Current has not been refreshed against Observed. |
| A board paper says "we are migrating to Platform B" but the Current State still contains Platform A. | Target has been allowed to *write back* into Current without a formal Change. |
| A target-architecture diagram is shown to auditors as evidence of compliance. | A *future intention* was used as a *present fact*. |

`Target ≠ Current` (CR-6 §12, T006). They are distinct
`ArchitectureState` nodes, with `valid-during` intervals that do not
overlap; the runtime MUST reject an attempt to read Target as Current
at a Current timestamp.

### 3.2 Current ↔ Scenario

| Symptom | What went wrong |
|---|---|
| A "what-if" run that retires Application A begins to show Application A missing from dashboards the next morning. | Scenario entities escaped their container and contaminated the authoritative architecture (CR-6 §26, T007). |
| Two scenarios (Cloud-first, Hybrid) are merged into one "current" view to make the choice look decided. | Scenario was used as a fait accompli, not as exploration. |

Scenarios MUST be contained inside `dea:Scenario`. They MUST NOT
insert hypothetical elements directly into `CurrentArchitecture`
(CR-6 §26, CR-9BJ).

### 3.3 Current ↔ Observed

| Symptom | What went wrong |
|---|---|
| The dashboard says "all applications healthy" but the monitoring system has been paging on Service X for 17 days. | Observed state was never bound to Current, so the divergence was invisible. |
| An audit report claims Application A is "active and in use" because the architecture repository says so. | Observed is the actual real-world signal; Current is the approved claim. They are not the same. |

The drift engine (CR-9BD/BE) exists precisely to detect when Observed
and Current diverge. The two MUST stay structurally distinct.

### 3.4 Target ↔ Scenario

| Symptom | What went wrong |
|---|---|
| A Scenario becomes "the" Target by attrition. | A hypothetical state quietly turned into the approved future without a Decision. |
| Scenarios are reviewed in the same meeting as the Target. | The reviewer's mind blurs hypothetical and approved. |

The Target is approved; a Scenario is not. The separation is procedural
as much as technical.

### 3.5 Observed ↔ Target (the silent killer)

| Symptom | What went wrong |
|---|---|
| "We're on track for the Target — see, the dashboard is green" — but the Observed state shows maturity dropping. | The green dashboard was an Approved-state view, not an Observed-state view. The two need different colours. |

When Observed and Target diverge, the right action is a Decision about
how to close the gap (CR-9AG), not a re-painting of Observed to match
Target.

## 4. Provenance per dimension

Each dimension carries its own provenance. The four-column rule (CR-10 §C):

| Dimension | Provenance | Confidence basis |
|---|---|---|
| Current | Architecture repository; approved by governance | Approved — high confidence in *intent*, not necessarily in *actuality* |
| Target | Approved roadmap / target-state document | Approved — must be reached via Change |
| Scenario | Hypothesis; declared `ScenarioAssumption`s | Variable; recorded per-assumption |
| Observed | Live integration / sensors / agents | Evidence-derived; freshness-tagged |

Observed ≠ Approved ≠ Inferred ≠ Proposed (see
[truth-model.md](truth-model.md) for the discipline that keeps them
distinct at the assertion level).

## 5. Linkage to CR-6 state model

CR-6 introduced five `ArchitectureState` kinds
([temporal-semantics.md](../temporal-semantics.md) §3):

```
Baseline ──→ Current ──→ Transition 1 ──→ … ──→ Target
                          (plateaux, never a jump)
```

CR-10 §C subsumes these as **different *uses* of the four dimensions**:

| CR-6 State | CR-10 Dimension(s) | Notes |
|---|---|---|
| **Baseline** | Current (snapshot) — *also* a snapshot of any dimension | A declared, immutable reference; adoption is an act, not a default (CR-6 §31, T010). |
| **Current** | Current | The authoritative *actual* state — planned, proposed, target, hypothetical elements excluded (T003). |
| **Target** | Target | Intended future condition. `Target ≠ Current ≠ Planned Change ≠ Forecast` (CR-6 §12, §27). |
| **Transition** | Current (plateau), Target (next) | A transition *between* two states, with from-state, to-state, caused-by Change, starts/ends/status (CR-6 §14). |
| **Scenario** | Scenario | Hypothetical, under declared assumptions, contained in `dea:Scenario`; never contaminates authoritative architecture (§25–§26, T007). |

CR-10 adds **Observed** as a distinct dimension that CR-6 did not
separately name — but the CR-9 runtime exposes it explicitly through
`assertion.status: observed` and the drift engine (CR-9BD/BE).

## 6. Linkage to CR-9BG baselines

CR-9BG (Architecture Baseline) enumerates the five baseline kinds:

```
Baseline
  ├── Current
  ├── Approved
  ├── Target
  ├── Planned
  └── Simulated
```

Read with the four-state model:

- **Current** baseline = Current dimension, declared snapshot.
- **Approved** baseline = Current dimension, *as approved by governance*.
- **Target** baseline = Target dimension, declared snapshot.
- **Planned** baseline = Target dimension in transition (a change
  scheduled but not yet effective).
- **Simulated** baseline = Scenario dimension that has been *executed*
  against a behavioural model — a simulated *result* (see
  [digital-twin.md](digital-twin.md) for the difference between
  "simulated" and "digital twin").

All five baselines coexist without touching one another.

## 7. Practical rules for the four-state discipline

1. **Every entity has a `state_dimension` marker** (Current / Target /
   Scenario / Observed). Cross-dimension reads are explicit, not
   implicit.
2. **Every dashboard states which dimension(s) it shows.** A "current
   architecture" view MUST NOT silently mix Target arrows. An
   "observed" view MUST NOT silently show Approved claims without a
   freshness tag.
3. **Scenarios are sandboxed.** A scenario MUST NOT write back to the
   production graph; the only path from Scenario to Current is through
   a Decision and a Change.
4. **Observed is the real-world signal.** If Observed says one thing
   and Approved says another, that is *drift* — a Decision is required
   to reconcile, not a quiet rewrite.
5. **Each dimension is auditable.** Every transition between dimensions
   is a named event with a timestamp and an actor.

These are the rules that keep the closed loop
(Observe → Model → Assess → Reason → Decide → Act → Observe,
[semantic-lifecycle.md](semantic-lifecycle.md)) honest. They are the
rules that prevent an enterprise semantic system from collapsing into
a wishlist.

---

*Companion concepts: [truth-model.md](truth-model.md) (no silent
inference, CR-9CQ); [semantic-lifecycle.md](semantic-lifecycle.md)
(the operating cycle); [digital-twin.md](digital-twin.md) (where the
four states sit in the twin maturity ladder); [../temporal-semantics.md](../temporal-semantics.md)
(CR-6 state model).*