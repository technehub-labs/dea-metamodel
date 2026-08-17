# Decision, Intent, Policy, Governance & Agentic Semantics (CR-7)

> **An Agent is not the center of the metamodel. Decision, intent, authority, policy, evidence,
> action and accountability are. Agents are participants in that semantic system. (CR-7 §1)**

This note is the knowledge-base companion to [`change-requests/CR-007.md`](../change-requests/CR-007.md).
It records the principles and justifications behind the governance and agentic profiles so
readers understand the thinking embedded in the artefacts.

## 1. Why a causal/governance layer (§1)

After CR-6, OpenDEA knows *what exists, how mature it is, when it exists, how it changes,
and what the target state is*. What it could not say: **why** a change is desired, **who**
may decide it, **what** constrains it, **what evidence** informs it, and **whether an
autonomous agent may participate**. Without that, "agentic EA" degenerates into an agent
inventory (name, description, model, tools) — a catalogue, not an architecture.

## 2. The closed causal loop (§2, §68)

```
Intent → Objective → Policy → Decision → Action → Change → Architecture State
     ↑                                                            ↓
     └────────── new Decision ← Assessment ← Evidence ← Outcome ←─┘
```

This loop is the strategic significance of CR-7: the metamodel stops being descriptive and
becomes a **governed, measurable, adaptive enterprise system**.

## 3. Distinctions that carry the load

| Distinction | Section | Why it matters |
|---|---|---|
| Intent ≠ Objective ≠ Outcome | §3–§6 | Direction, measurement and actuality — the measurable causal loop |
| Policy ≠ Constraint | §9–§10 | Directing vs limiting; constraint strength (hard/soft/preference/guideline) enables automated decisions |
| Decision ≠ Change ≠ Action | §12–§13 | Authorization, execution and architecture modification are three events |
| Capability ≠ Authority | §18 | An agent *capable* of approving payments may be *authorized* only ≤ $10k — structural, not documentary |
| Enterprise Decision ≠ Policy Decision | §39 | "Deploy Agent A" vs "Agent A may access Dataset X" |
| Agent ≠ AI Model ≠ Tool ≠ Workflow | §21/§31/§57 | The anti-AI-washing guards: an LLM is a component; a renamed application is not an agent |
| Accountability ≠ Responsibility ≠ Ownership ≠ Authority | §36–§37 | RACI becomes implementable as a profile — never collapsed into "owner" |

## 4. The reuse rule (§65) — enforced in CI

**Agentic semantics reuse core DEA semantics wherever the concept already exists.**

- *Agent Decision* = `Decision` + `made-by → Agent`
- *Agent Action* = `Action` + `performed-by → Agent`
- *Agent Outcome* = `Outcome` + `results-in → AgenticSystem`

`AgentDecision`, `AgentAction`, `AgentKnowledge` types are forbidden — test_013 fails if they
appear. The agent participates in the enterprise semantics; it does not fork them.

## 5. Authority, delegation and autonomy (§18–§25)

- **Authority** carries scope, limits and validity; **Delegation** adds delegator, conditions,
  duration and revocation (G005).
- **Autonomy is not a boolean** (§23): AutonomyPolicy + configurable AutonomyLevels
  (0 Inform … 5 Autonomous, illustrative) + HumanOversight patterns.
- **Oversight patterns are materially different** (§25): approve-before vs review-after vs
  intervene-on-exception vs continuous supervision.
- **Risk-aware autonomy** (§41/§43): reversibility and materiality drive control strictness —
  `Agent wants to act → Policy evaluation → Risk evaluation → Permitted | Escalate`.
  More defensible than any autonomy number.

## 6. Orchestration roles (§46)

**Agent** (bounded cognitive/action role) ≠ **Orchestrator** (coordinates actors/actions toward
a goal) ≠ **Controller** (enforces execution/state/control conditions, triggers escalation).
Collapsing them destroys the governance boundary of multi-agent systems.

## 7. The agentic system boundary (§58–§59)

`AgenticSystem` composes agents, models, tools, services, policies, orchestration, memory and
human oversight — the proper architecture boundary for multi-agent solutions, wired through
`dea:composes`.

## 8. End-to-end example (§63)

Intent "improve customer service" → Objective "−40% resolution time" → DMM assessment (3.1) →
AgentOpportunity (derived) → Decision "deploy agent" → Policy "escalate legal claims" →
Authority "resolve ≤ $500" → Agent + Skills + Tools → Orchestration with policy check →
Human oversight for refunds > $500 → Change → Outcome "−43%" → Reassessment 3.1 → 3.8.
Every hop is a typed node and edge in the graph.

## 9. What CR-7 deliberately excludes (§66)

LLM architecture, prompts, RAG, vector stores, training, vendor agent frameworks, MCP
implementation details — those are technology-profile concerns. OpenDEA models **enterprise
semantics**, not AI engineering stacks.

## 10. Where next (CR-7's own recommendation)

CR-8 should consolidate CR-1…CR-7 into a formal **OpenDEA Semantic Architecture & Conformance
Specification** — canonical ontology rules, cardinalities, inheritance/composition rules,
profile mechanism, machine-readable schemas, validation suite, examples, migration rules and a
reference implementation. The transition from improving the metamodel to making it an
implementable, testable, interoperable standard.

---

*Artifacts: `metamodel/profiles/governance/` (intent · objectives · policy · authority ·
governance · constraints) · `metamodel/profiles/agentic/` (agent · agent-profile · skill ·
tool · orchestration · autonomy · oversight · constraints) · G001–G016 in
`tests/conformance/test_013_governance_rules.py`.*
