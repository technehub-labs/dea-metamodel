# The Truth Model

> **KB note — knowledge in OpenDEA comes from somewhere, has a confidence
> of a particular kind, and reaches Approved only by an explicit
> transition. The four statuses Observed / Asserted / Inferred / Approved
> must never be implicitly conflated.** Source: CR-10 §D, grounded in
> [CR-9B](../change-requests/CR-009.md), [CR-9O](../change-requests/CR-009.md),
> [CR-9P](../change-requests/CR-009.md), [CR-9Q…T](../change-requests/CR-009.md),
> [CR-9CQ](../change-requests/CR-009.md), and CR-10 §O (uncertainty
> classes). Companion notes: [four-state-model.md](four-state-model.md),
> [glossary.md](../glossary.md), [../runtime-architecture.md](../runtime-architecture.md) §3.

## 1. The critical rule

> **Observed, Asserted, Inferred, and Approved knowledge MUST NOT be
> implicitly conflated.** (CR-10 §D)

Each is a distinct kind of claim, attached to the graph with distinct
provenance, and promoted along a one-way path. Collapsing them is how
enterprise-architecture data becomes marketing.

## 2. The knowledge-flow diagram

```
                       ┌──────────────────────┐
                       │      KNOWLEDGE       │
                       │  (the universe of    │
                       │  possible claims)    │
                       └──────────┬───────────┘
                                  │
        ┌─────────────────────────┼──────────────────────────┐
        ▼                         ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   OBSERVED    │         │   ASSERTED    │         │   INFERRED    │
│ (real-world   │         │ (someone/some- │         │ (a rule, at a │
│  signal)      │         │  thing claims) │         │  declared     │
│               │         │               │         │  level, says) │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        │ Evidence                │ Source                  │ Rule-or-Model
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │       APPROVED       │
                       │  (governance has     │
                       │  endorsed the claim) │
                       └──────────────────────┘
```

Three streams of knowledge flow into one Approved status:

- **Observed** is grounded in **evidence** — measurements, sensors,
  integration pipelines, agent reports.
- **Asserted** is grounded in **source** — a named human, system or
  organisation explicitly claims the knowledge.
- **Inferred** is grounded in **rule-or-model** — a declared reasoning
  step at a declared level produces the knowledge.

**None of these is Approved by default.** Approved is a separate
transition (Proposed → Verified → Approved, CR-9O) carried out by named
governance. CR-9CQ — *no silent inference* — is the runtime
enforcement of this rule: an inferred claim cannot quietly rewrite
itself as authoritative fact.

## 3. The five kinds of knowledge in the runtime (CR-9B)

CR-9B established that OpenDEA distinguishes five kinds of knowledge in
the runtime representation. They MUST stay separate:

| Kind | Question | Runtime representation |
|---|---|---|
| **Model** | What is the enterprise understood to be? | Node/Edge identity + type + properties |
| **Runtime state** | What is currently observed? | `assertion.status: observed`, `observed_at`, freshness metadata (CR-9AZ) |
| **Assertion** | What does someone/something claim? | Assertion block: `assertedBy`, `confidence`, `status` (CR-9O: Proposed → Verified → Approved / Rejected / Superseded / Disputed) |
| **Evidence** | What supports the claim? | Evidence nodes + `supportedBy` edges — an *evidence graph*, not attachments (CR-9P) |
| **Derived knowledge** | What does the runtime infer? | `provenance.derived_from` + `derivation_rule`, with the reasoning level recorded (CR-9R/T) |

Conceptually (CR-9B):

```
Model
  │
  ├── Assertion ── Evidence
  │
  ├── Observation
  │
  └── Inference
```

The discipline "do not collapse these into a single entity
representation" (CR-9B) is the same discipline as "do not implicitly
conflate the four statuses" (CR-10 §D) — they are the same truth
expressed at the assertion level and at the runtime-representation
level.

## 4. The four-status discipline

CR-10 §D names the four statuses explicitly:

| Status | Where it comes from | How it is allowed to advance |
|---|---|---|
| **Observed** | Real-world signal, captured | → Asserted (when a human/system attests), → Inferred (when a rule derives from it), → Approved (via governance) |
| **Asserted** | A named source claims it | → Verified, → Approved, or → Rejected via the assertion lifecycle (CR-9O) |
| **Inferred** | A rule, at a declared level, derives it | → Asserted (when a human attests), → Approved (via governance) — *never directly authoritative* |
| **Approved** | Governance endorses it | Terminal; supersession is a new transition, not a rewrite |

Three rules follow (CR-10 §D):

1. **Implicit conflation is forbidden.** A system MUST NOT present an
   Inferred fact as Approved, an Observed fact as Asserted (or vice
   versa), without an explicit transition.
2. **The transition is named.** Every promotion from one status to
   another carries the rule, the actor, the timestamp and (where
   applicable) the policy that authorised it.
3. **The four statuses remain distinct in queries.** A query that asks
   "is this true?" MUST distinguish "true because observed",
   "true because asserted", "true because inferred" and "true because
   approved" — and the answer is the union only when the consumer asks
   for the union explicitly.

## 5. No silent inference (CR-9CQ)

The runtime rule that enforces the model-vs-state distinction at
inference time (see also
[../runtime-architecture.md](../runtime-architecture.md) §8):

> The runtime **MUST NOT** silently convert inferred knowledge into
> authoritative fact. Instead, Observed / Inferred / Proposed / Approved
> remain distinct. (CR-9CQ)

An AI can propose:

```
Capability X appears strategic.
```

But it cannot silently rewrite:

```
Capability X = strategic
```

without an explicit state transition. In CR-9.1 this is structural:
`GraphStore.infer()` raises `InferenceUnavailable`, and a test proves
loaded graphs contain exactly the edges the model declared — nothing
derived materialises silently. This is the structural enforcement of
the truth-model discipline.

## 6. Every inference answers "Why?" (CR-9T)

The complement of "no silent inference" is "every inference is
explainable":

> Never produce: `Capability X is strategic.` without being able to
> answer: `Why?` (CR-9T)

The runtime MUST return:

```
Inference:
  Capability X = Strategic
Because:
  1. supports Objective Y
  2. Objective Y = Strategic
  3. rule DEA-INF-007 applied
Confidence:
  0.96
```

This is the foundation of the viewer's *"Why?"* navigation
(CR-9BZ) — and the credibility precondition for any AI-assisted
enterprise-architecture claim. An inference without provenance is not
an inference in OpenDEA; it is speculation wearing a tie.

## 7. Uncertainty classes (CR-10 §O)

CR-10 §O introduces six uncertainty classes that span the four
statuses. Every claim in the graph should declare which one it is in
(or be marked Unknown until classified):

| Class | Meaning | Typical source |
|---|---|---|
| **Known** | Approved, with evidence | Governance transition with attached evidence |
| **Estimated** | Inferred at a deterministic or graph level | Rule application, traversal |
| **Assumed** | Asserted, awaiting verification | Architectural hypothesis, scoping assumption |
| **Predicted** | Forecast from a model | Forecast (CR-6 §27), target-state planning |
| **Simulated** | Output of a scenario execution | Simulation engine (CR-9AS, CR-10AA) |
| **Unknown** | None of the above can be asserted yet | Gap, declared uncertainty |

The six classes are not statuses — they are *uncertainty
characterisations* of a claim. A single claim may carry both a status
(Observed) and an uncertainty class (Known), or (Inferred) and
(Estimated), and the combination is the full truth. The six classes
exist so that consumers (humans, agents, dashboards) can reason about
how much to trust a claim without having to derive the uncertainty
themselves.

## 8. The agent-era importance

The four-status discipline becomes load-bearing the moment AI agents
begin to participate in the enterprise semantic system. Three reasons:

1. **Agents propose. They do not assert.** An LLM that produces
   `Capability X appears strategic` is making an *Inferred / Estimated*
   claim — never an Approved one. Collapsing the status would let the
   LLM silently rewrite governance.
2. **Agents must be auditable.** Every agent action carries an audit
   record (CR-9AM/CI) that includes the **status of the knowledge that
   triggered it**. An action taken on Inferred evidence is not the
   same — legally, operationally or reputationally — as an action
   taken on Approved evidence.
3. **Agents must be policy-bounded.** The Policy Decision Point
   (CR-9AK) evaluates Authority, Policy and Scope against the live
   graph. If the graph has silently merged Observed with Approved,
   the policy decision is made on the wrong facts.

The agent era therefore re-states the CR-9CQ rule more sharply: **an
agent that confuses Inferred with Approved has not merely made an
epistemic error — it has produced an unsafe action**. The truth model
is the safety case.

## 9. Practical rules

- Every assertion declares its status (Observed / Asserted / Inferred
  / Approved).
- Every assertion declares its uncertainty class (Known / Estimated /
  Assumed / Predicted / Simulated / Unknown).
- Every Inferred assertion carries `provenance.derived_from` and
  `derivation_rule`, with the reasoning level recorded (CR-9R).
- Every Inferred assertion can be replayed to answer "Why?" (CR-9T).
- Approved is reached only via an explicit transition in the
  assertion lifecycle (CR-9O).
- Scenarios (CR-6 §25, [four-state-model.md](four-state-model.md) §3.2)
  cannot leak into Approved without a Decision.
- A query that returns facts MUST distinguish the statuses in its
  answer, and MUST NOT present an Inferred fact as Approved without
  the consumer's explicit consent.

These are the rules that keep "the graph says X" honest.

---

*Companion concepts: [four-state-model.md](four-state-model.md) (the
four semantic dimensions); [glossary.md](../glossary.md) (terms);
[../runtime-architecture.md](../runtime-architecture.md) §3, §8
(CR-9B, CR-9CQ, CR-9CR in code).*