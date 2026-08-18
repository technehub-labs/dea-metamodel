# The Semantic Lifecycle

> **KB note — the OpenDEA operating cycle.** Knowledge in OpenDEA is
> not static. It moves through ten named stages — and every stage has
> a CR behind it. Source: CR-10 §E, grounded in the CR sequence:
> [CR-1](../change-requests/CR-001.md)…[CR-9](../change-requests/CR-009.md).
> Companion notes: [four-state-model.md](four-state-model.md),
> [truth-model.md](truth-model.md), [digital-twin.md](digital-twin.md),
> [../runtime-architecture.md](../runtime-architecture.md).

## 1. The cycle

```
DISCOVER ──→ IDENTIFY ──→ MODEL ──→ VALIDATE ──→ OBSERVE
                                                   │
                                                   ▼
CHANGE ◀── DECIDE ◀── REASON ◀── ASSESS ◀───────────┘
   │
   ▼
OBSERVE  (loop closes)
```

Ten stages, one closed loop, ten CRs (CR-1…CR-9 with CR-10 as the
consolidator). Each stage has a single responsibility, a single set of
artefacts, and a single set of conformance rules.

## 2. DISCOVER

Discover what exists — enterprise catalogues, repositories,
spreadsheets, vendor models, agent inventories, public sources. This
is the *outside-in* stage: the world, before OpenDEA's semantic
discipline has touched it. CR-1 (one normative source) and CR-9J
(source adapters) frame the discovery boundary; nothing from this stage
enters the graph until IDENTIFY and MODEL have done their work.

## 3. IDENTIFY

Identify what each discovered artefact *is*. This is the
identity-resolution stage — exact, identifier, semantic and
probabilistic matching produce a *verdict* (same / related / different
/ unknown) with `matchScore`, `matchingMethod`, `evidence`,
`reviewRequired`, `approvedBy` (CR-9M/N). The discipline is
uncompromising: **never automatically merge uncertain identities**
(CR-9M, [runtime-architecture.md §6](../runtime-architecture.md)).
This matters doubly when AI performs the matching.

## 4. MODEL

Model the enterprise — declare entities, relationships, properties,
profiles. This is CR-2 (canonical relationship ontology), CR-3
(entity normalisation), CR-4 (Core + profiles), and CR-8 (frozen
Core, envelope, naming). The output is a normative OpenDEA model.
The discipline from CR-8 is that the Core is small, stable and
closed; everything domain-specific enters via a profile (ADR-002).

## 5. VALIDATE

Validate that the model is conformant. This is the
semantic-conformance stage, anchored by CR-8: the reference
validator (`tools/opendea_validate.py`), the golden models
(models that MUST pass), and the negative models (models that
MUST fail for the expected DEA-E rule). Without validation the
specification is prose. With validation it is a contract
([specification-and-conformance.md §3](../specification-and-conformance.md)).
Runtime validation (CR-9CQ — *no silent inference*) is the
runtime-extension of the same discipline.

## 6. OBSERVE

Observe what the world is *actually* doing. The graph receives
real-world signals: API responses, events, metric streams, agent
reports, human observations. Each is timestamped, sourced, attached
as `assertion.status: observed` with freshness metadata
(`lastObserved`, `lastSynced`, `freshnessPolicy`, `stalenessStatus`)
per CR-9AZ. CR-5 (Assessment) and CR-9.4 (Temporal & Event Runtime)
build the supporting substrate: DMM assessments, bitemporal
semantics, event-driven synchronisation, snapshots and
`diff(snapshotA, snapshotB)` (CR-9BI).

## 7. ASSESS

Assess what the observations mean against declared frameworks.
Maturity (DMM, ECF, AI-readiness, cyber, etc.) lives on the
`AssessmentResult`, never on the entity (rule A008, CI-enforced).
The assessment carries evidence, confidence, provenance and
gaps-to-Change (CR-5 §25). CR-9X/Y operationalise this as the
Assessment Engine and the DMM Runtime — one entity can be assessed
by many frameworks at different dates and scopes without conflict.

## 8. REASON

Reason over the assessed graph. The reasoning engine (CR-9Q)
applies declared rules (CR-9S, the rule registry) at declared
levels (CR-9R: 1 Deterministic → 2 Ontological → 3 Graph → 4
Probabilistic → 5 Generative) to produce derived assertions. Every
inference MUST answer **Why** (CR-9T) and MUST NOT silently
rewrite itself as authoritative fact (CR-9CQ — see
[truth-model.md §5](truth-model.md)). Reasoning is also the
"what-if" stage (CR-9BJ scenario engine, [four-state-model.md
§3.2](four-state-model.md)) — Scenarios A/B/C are reasoned over
without touching the production graph.

## 9. DECIDE

Decide what to do about the reasoned result. Decisions are not
changes and not actions; they are *authorisations* with a declared
lifecycle (CR-9AE: Proposed → UnderReview → Approved → Executed →
Observed → Evaluated → Closed, plus Rejected/Deferred/Superseded/
Revoked). CR-7 §12 introduced the Decision concept; CR-9AD
operationalised the engine; CR-9.7 closes the loop. A decision
that involves an agent MUST also pass through Authority
evaluation (CR-9AJ), Policy enforcement (CR-9AK) and, where
required, Human-in-the-loop (CR-9AL — *policy-driven*, never
hard-coded). Decision Support is distinguished from Decision
Execution — the latter requires explicit authorisation (CR-9AD).

## 10. CHANGE

Change the enterprise to enact the decision. Changes introduce,
remove, modify, replace elements, realise Target State, and
result-in Outcomes (CR-6E §15, CR-9AF). They depend on and enable
other Changes (CR-6 §34–§35 dependency-aware transition); Planned
vs Actual is mandatory — a retirement planned for 2027-01-01 and
actually retired 2027-03-15 are both first-class. CR-9AF is the
decision-to-change linkage; CR-9AG is the closed-loop
transformation that brings the Outcome back to Evidence; CR-10
consolidates the change discipline under the four-state model
([four-state-model.md §2](four-state-model.md)).

## 11. OBSERVE (again)

Observe what the change actually produced. The cycle returns to
OBSERVE — the same stage, a different content. The new observations
may agree with the predicted outcome (the change worked) or diverge
(drift, CR-9BD/BE). Either way, the graph is the new starting point
for the next iteration.

## 12. Why this is the loop, not a pipeline

Three properties distinguish a loop from a pipeline:

1. **It has no terminal stage.** Every output is the input to the next
   observation. The semantic enterprise is permanently under revision.
2. **Every stage can trigger re-entry.** A new observation (drift,
   exception, audit) may short-circuit back to ASSESS or REASON. A
   failed CHANGE re-enters DECIDE. An emerging DECISION re-enters
   MODEL.
3. **Each transition has provenance.** Closing the loop is not the
   same as forgetting the previous iteration. Every transition is
   auditable; every assertion keeps its status (Observed / Asserted /
   Inferred / Approved, [truth-model.md §4](truth-model.md)).

## 13. CR coverage at a glance

| Stage | Anchor CRs | Status |
|---|---|---|
| DISCOVER | CR-1, CR-9J (source adapters) | **Implemented** (CR-1 normative source; CR-9.5 in CR-9 deferred) |
| IDENTIFY | CR-9M/N | **Proposed** (CR-9.5) |
| MODEL | CR-2, CR-3, CR-4, CR-8 | **Implemented** |
| VALIDATE | CR-8 (semantic), CR-9CQ (runtime) | **Implemented** |
| OBSERVE | CR-5, CR-6, CR-9AZ, CR-9.4 | **Partial** (foundations in CR-9.1; full bitemporal/event runtime → CR-9.4) |
| ASSESS | CR-5, CR-9X/Y | **Implemented** (semantic) / **Proposed** (DMM runtime → CR-9.6) |
| REASON | CR-9Q…T, CR-9.3, CR-9BJ | **Proposed** (CR-9.3) |
| DECIDE | CR-7, CR-9AD/AE, CR-9.7 | **Partial** (semantic in CR-7; engine → CR-9.7) |
| CHANGE | CR-6E, CR-9AF/AG, CR-10 | **Partial** (semantic in CR-6; closed-loop in CR-9AG; CR-10 consolidates) |
| OBSERVE (loop) | Same as stage 6 | Same |

## 14. The closed loop in one sentence

> **Observe → Model → Assess → Reason → Decide → Act → Observe**
> ([runtime-architecture.md §1](../runtime-architecture.md), CR-9 §101).

That is the point at which OpenDEA stops being primarily a metamodel
and starts becoming an architecture intelligence platform. The
discipline of every stage — and the discipline of the
truth-model that ties them together — is what keeps the loop honest.

---

*Companion concepts: [four-state-model.md](four-state-model.md) (the
four semantic dimensions that frame OBSERVE); [truth-model.md](truth-model.md)
(no silent inference — the OBSERVE→REASON→CHANGE discipline);
[digital-twin.md](digital-twin.md) (where this loop becomes a twin);
[../runtime-architecture.md](../runtime-architecture.md) (the runtime
that executes the loop).*