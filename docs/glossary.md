# OpenDEA Glossary

> **KB note — the authoritative vocabulary of OpenDEA.** Distils the canonical
> definitions from the CR sequence (CR-1…CR-10) into a single reference so that
> every other document, profile and tool uses the same word for the same thing.
> Sources: [CR-9B](../change-requests/CR-009.md) (model / state / assertion /
> evidence / inference), [CR-9E](../change-requests/CR-009.md) (canonical graph
> model), [CR-9O](../change-requests/CR-009.md) (assertion architecture),
> [CR-9AT](../change-requests/CR-009.md) (digital-twin distinction), CR-10 §L
> (this glossary).

## Contents

- [Agent](#agent)
- [Architecture Debt](#architecture-debt)
- [Architecture Runway](#architecture-runway)
- [Assertion](#assertion)
- [Assessment](#assessment)
- [Authority](#authority)
- [Baseline](#baseline)
- [Capability](#capability)
- [Concept Area](#concept-area)
- [Concept Classification](#concept-classification)
- [Concept Profile](#concept-profile)
- [Current State](#current-state)
- [Decision](#decision)
- [Digital Twin](#digital-twin)
- [ECF Context](#ecf-context)
- [ECF Domain](#ecf-domain)
- [ECF Stage](#ecf-stage)
- [Entity](#entity)
- [Evidence](#evidence)
- [Inference](#inference)
- [Model](#model)
- [Observed State](#observed-state)
- [Observation](#observation)
- [Outcome](#outcome)
- [Policy](#policy)
- [Profile](#profile)
- [Relationship](#relationship)
- [Scenario](#scenario)
- [Simulation](#simulation)
- [Target State](#target-state)
- [Tool](#tool)

---

## Agent

A participant that performs Actions within the enterprise semantic system,
bounded by Authority, Policy, Scope and approval (CR-7 §1, CR-9AH).

It is NOT an autonomous centre of the metamodel; Agents are participants in
the causal/governance loop (Intent → Objective → Policy → Decision → Action
→ Change → Outcome → Evidence). An LLM, a renamed application, or a workflow
is not automatically an Agent (CR-7 §21/§31/§57, the "anti-AI-washing"
guards).

## Architecture Debt

The accumulated cost — operational, strategic, risk, capability or technical
— of divergence between the **Current State** and the **Target State**, made
first-class so transformation programmes can quantify, prioritise and pay it
down deliberately.

It is NOT the same as technical debt at the code level, nor a vague sense of
"the architecture is not ideal". Architecture Debt is structurally connected
to Change (CR-6E §15), to Assessment gaps (CR-5 §25), and to the
TargetState→Current gap analysis (CR-9BH). Introduced as an explicit concept
in CR-10 §L.

## Architecture Runway

The remaining capacity — time, budget, technical currency, capability
maturity, governance headroom — before accumulated Architecture Debt causes
material harm (delivery failure, compliance breach, security exposure,
strategic miss).

It is NOT a generic roadmap or a wishlist. Architecture Runway is measured
against the **Current → Target** trajectory and is consumed by deferring
necessary decisions; it is introduced in CR-10 §L as the forward-looking
complement to Architecture Debt.

## Assertion

A claim about the enterprise made by some actor (human, system, agent) at a
specific time, with attached provenance (`assertedBy`, `sourceSystem`,
`confidence`, `status`) (CR-9O, CR-9B).

It is NOT a statement of truth. An assertion may be Proposed, Verified,
Approved, Rejected, Superseded or Disputed (CR-9O) and competing assertions
coexist without corrupting the graph — state transitions resolve them, never
overwrites (CR-9B).

## Assessment

An *evaluation* of an entity (most often a Capability) against a declared
framework (CR-5 §4), yielding a result with evidence, confidence and
provenance rather than a score on the entity itself.

It is NOT a property of the entity. Maturity (DMM, ECF, AI-readiness) lives on
the `AssessmentResult`, never on the Capability (rule A008, CI-enforced).
One entity can be assessed by many frameworks at different dates and scopes
without conflict.

## Authority

The structurally declared right of an Actor or Agent to take a specific kind
of Decision or Action within a Scope and validity window (CR-7 §18–§19,
CR-9AJ).

It is NOT Capability. An agent *capable* of approving payments may be
*authorized* only up to $10k — the distinction is structural, not documentary
(CR-7 §18). An Agent gets mutation rights only through explicit Authority →
Policy → Scope → Approval (CR-9CR, CR-9AJ–AL).

## Baseline

An *explicitly captured* state of the enterprise architecture at a defined
temporal point, identified by `state_id`, `captured_at`, `valid_at`, `scope`
and `source` (CR-6 §10, CR-9BG).

It is NOT "whatever the current model happens to contain". A Baseline is a
declared snapshot, optionally adopted as the reference for transformation
(CR-9BG `Baseline ├── Current ├── Approved ├── Target ├── Planned ├──
Simulated`). Baselines are immutable except via `revision_of` (T010).

## Capability

An abstract ability of the enterprise ("what it can do") — Core anchor
(CR-4), independent of who performs it or how it is realised.

It is NOT a Service, Application or Actor. A Capability is *realized-by*
Services, *supported-by* Applications, *owned-by* Organizations, and
*assessed-by* Assessments. Capability does not carry maturity scores —
those live on AssessmentResult (rule A008).

## Concept Area

A thematic grouping of Concepts within the OpenDEA Concepts Model
(CR-CM-000). A Concept may belong to **multiple** Concept Areas.

It is NOT an ECF Domain. Concept Area and ECF Domain are different
concepts; no automatic one-to-one mapping is assumed between them.
See [concepts/terminology-alignment.md](concepts/terminology-alignment.md).

## Concept Classification

The assignment of a Concept to one or more classification targets
(Concept Areas, Concept Profiles) within the OpenDEA Concepts Model
(CR-CM-000).

## Concept Profile

A named, purpose-bound selection of Concepts and their groupings within
the OpenDEA Concepts Model (CR-CM-000).

## Current State

The best authoritative representation of what *actually exists* in the
enterprise at a specified time: actual elements, actual relationships,
actual lifecycle states (CR-6 §11).

It MUST NOT automatically include planned, proposed, target or hypothetical
elements (T003). The Current State is distinct from the Target State
(`Current ≠ Target`, CR-6 §12) and from Approved/Planned/Simulated baselines
(CR-9BG).

## Decision

A *commitment* that authorises a Change or an Action, following a declared
lifecycle (Proposed → UnderReview → Approved → Executed → Observed →
Evaluated → Closed, plus Rejected/Deferred/Superseded/Revoked) (CR-7 §12,
CR-9AD/AE).

It is NOT a Change and NOT an Action. Decision = authorisation; Change =
architecture modification; Action = execution. Decision Support is
distinguished from Decision Execution — the latter requires explicit
authorisation (CR-9AD). A Decision carries an evidence matrix across
strategic, architecture, financial, risk, capability, technology,
governance and operational dimensions (CR-9BL).

## Digital Twin

A persistently synchronised, behaviourally faithful virtual counterpart of a
physical or operational system — **not** merely an architecture model that
contains entities and relationships (CR-9AT, CR-10AA/AB).

OpenDEA today is between the Enterprise Model and Observed Architecture
levels; CR-10 Phase 7 lays the foundation but MUST NOT be claimed complete
until **state synchronization** and **behavioural semantics** exist.
See [concepts/digital-twin.md](concepts/digital-twin.md) for the maturity
ladder and the minimum requirements.

## ECF Context

An optional association between a Concept and ECF coordinates
(ECF Domain, ECF Stage) (CR-CM-000). A Concept may carry **zero or more**
ECF Contexts; the association is not an identity — it never implies that a
Concept Area IS an ECF Domain.

## ECF Domain

One of the seven axiom-derived rows of the Enterprise Concept Framework
foundation matrix (Governance & Existence, Supply & Resources, People &
Organization, Customer & Demand, Product & Offering, Operations &
Delivery, Finance & Value) — answers *"what does the enterprise do?"*
(CR-CM-000; ECF home: `technehub-labs/dea-metaframework`).

The bare word **Domain** is reserved to the ECF: every use must be
explicitly *ECF Domain* or namespace-qualified. It is NOT a generic
thematic grouping in the Concepts Model — that is a Concept Area.

## ECF Stage

One of the seven lifecycle columns of the Enterprise Concept Framework
foundation matrix (Conceive, Design, Build, Activate, Operate, Improve,
Retire) — answers *"how does the work evolve?"* (CR-CM-000). The bare word
**Stage** is reserved to the ECF; every use must be explicitly *ECF Stage*
or namespace-qualified.

## Entity

A typed node in the semantic graph — anything the enterprise cares to name
and reason about (Capability, Service, Application, Information, Actor,
Organization, Decision, Outcome, Change, Assessment, Agent, Tool, Policy,
Authority, …) (CR-9E, CR-4 Core anchors).

It is NOT a node in a visualisation structure. The entity carries identity,
type and properties; relationships, assertions, evidence and inferences are
attached separately — never folded into the entity representation
(CR-9B: "do not collapse these into a single entity representation").

## Evidence

A graph node (not an attachment) that *supports* an assertion, itself
*derivedFrom* a source (CR-9P).

It is NOT a document. The evidence graph pattern is:

```
Assertion ── supportedBy ──→ Evidence ── derivedFrom ──→ Source
```

This is what makes an assessment auditable (CR-9BC: Conclusion → Inference
→ Assertions → Evidence → Source Systems — explainable enterprise
intelligence).

## Inference

A derived result produced by applying a declared rule at a declared
reasoning level (1 Deterministic → 2 Ontological → 3 Graph → 4
Probabilistic → 5 Generative) (CR-9Q/R).

It is NOT authoritative fact. The runtime MUST NOT silently convert
inferred knowledge into authoritative fact (CR-9CQ — "no silent
inference"). Every inference MUST answer **Why** (CR-9T — conclusion →
rule applied → supporting assertions → confidence) and MUST record its
reasoning level. The five statuses Observed / Inferred / Proposed /
Approved remain distinct.

## Model

The enterprise understood *to be what* — entity types, relationship types,
properties, semantics, profiles, rules. The "what does this mean?" layer
(CR-9 §101, CR-8 v1.0).

It is NOT runtime state and NOT observed state (CR-9B). The Model answers
"What is the enterprise understood to be?"; Runtime state answers "What is
currently observed?"; Assertions, Evidence and Derived Knowledge are kept
distinct from both. Collapsing model and state destroys the entire
truth-model discipline (see [concepts/truth-model.md](concepts/truth-model.md)).

## Observed State

The architecture as *evidence-derived real-world*: data that arrived from
enterprise systems, agents, sensors, or human assertions, attached to the
graph with `observed_at`, `assertion.status: observed` and freshness
metadata (`lastObserved`, `lastSynced`, `freshnessPolicy`,
`stalenessStatus`) (CR-9AZ, CR-9BD).

It is NOT the Current State and NOT the Approved State. Observed state may
diverge from Approved state; that divergence is *drift*, detected by the
drift engine and risk-assessed (CR-9BD/BE). "This conclusion rests on
17-day-old data" is a first-class warning, not a footnote.

## Observation

A recorded signal from the world — an event, a metric, an assertion made
by a system outside the graph — that *can become* evidence for an
Assertion but is not itself an Assertion (CR-9E).

It is NOT evidence and NOT an inference. Observations feed the
evidence/assertion pipeline; they MUST be timestamped, sourced and
attributed before they may upgrade to evidence for an Approved state.

## Outcome

A measured result of an executed Change, Action or Initiative, linked
back to the Decision that authorised it and forward to the next Assessment
or Evidence (CR-7 §6, CR-9AF/AG).

It is NOT an Objective. Intent ≠ Objective ≠ Outcome (CR-7 §3–§6) —
direction, measurement and actuality are three distinct concepts. The
causal loop closes: Outcome → Evidence → (re)Assessment → new Decision
(CR-9AG).

## Policy

A *directive* that constrains or guides Decisions and Actions — distinct
from a Constraint (which merely limits) (CR-7 §9–§10, CR-9AK).

It is NOT a Constraint. Policies direct; Constraints limit. Constraint
strength (hard / soft / preference / guideline) enables automated
decisions. Policy operates at entity, relationship and *property* level
(CR-9CF/CG) and is enforced by a Policy Decision Point returning ALLOW /
DENY / ESCALATE (CR-9AK).

## Profile

A versioned, declared bundle that *extends* the OpenDEA Core with new
entity types, relationship types, properties, rules and vocabularies,
without redefining Core (ADR-002, CR-8 profile-mechanism).

It is NOT a new Core. Profiles MUST reference Core types rather than
redefining them; where a conflict is found, Core wins and the profile is
invalid. New domain semantics (scenario, simulation, assessment, agent,
cost/value) enter OpenDEA via a profile, not via Core mutation.

## Relationship

A typed, directed, inverse-aware edge between two entities, carrying
provenance, temporal validity, lifecycle status and properties
(`confidence`, etc.) — first-class, never a bare source→target pair
(CR-2 §4–§13, CR-9E).

It is NOT a property of either endpoint. Edge instances are authoritative;
entities carry no relationship state (CR-3). A *planned* edge MUST NEVER
render as a current edge (CR-6 §22, T004). Direction is canonical; inverses
are declared and generated, never stored as independent relationships
(CR-2 §8).

## Scenario

A *hypothetical* architecture state under a defined set of
`ScenarioAssumption`s — for example "Cloud-first", "Hybrid",
"On-premise modernisation" (CR-6 §25, CR-9BJ, CR-10).

It is NOT the Target State and NOT the Current State. Scenarios are
contained inside `dea:Scenario`; they MUST NOT contaminate the
authoritative architecture (§26, T007). Scenarios A/B/C coexist without
affecting the production graph (CR-9BJ) and form the input to the
simulation / digital-twin foundation.

## Simulation

The *execution* of a Scenario against a behavioural model to produce a
predicted outcome graph without mutating the production graph
(CR-9AS/AT, CR-10AA).

It is NOT an Observation and NOT a Decision. The engine produces an
impact graph (affected capabilities, cost assumptions, risk,
dependencies, maturity impact, agent impact — CR-9BJ) while Current
State, Approved State, Target State and Planned State remain untouched.

## Target State

The *intended future* condition of the enterprise — represented as a
distinct state, not as an annotation on Current (CR-6 §12, CR-9BH).

`Target ≠ Current`, `Target ≠ Planned Change`, `Target ≠ Forecast`
(CR-6 §12, §27; T006). The Forecast is what is *expected* to happen; the
Target is what the organisation *intends* to achieve; they may differ
deliberately (Forecast maturity 3.5 vs Target 4.0, CR-6 §27).

## Tool

A registered capability that an Agent may invoke, with declared inputs,
outputs, side-effects, scope and authority requirements (CR-7 §31,
CR-9AN/AO/AP).

It is NOT an Agent and NOT an Action. The tool registry is itself a
semantic graph: the graph can answer "which agents can act on this
capability?" (CR-9CB) and "which capabilities are agentization
opportunities?" (CR-9AP — an `AgentizationOpportunity`, never an
auto-created agent). Orchestration stays outside Core (CR-9AQ).