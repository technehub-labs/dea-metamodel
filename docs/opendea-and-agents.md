# OpenDEA and AI/Agents — the positioning (CR-10 §G)

> OpenDEA plays three distinct roles for agentic systems — and explicitly
> refuses a fourth.

## Role 1 — OpenDEA as knowledge

Agents receive **enterprise semantic context**: the relevant, minimal,
policy-filtered subgraph for the task at hand (CR-9CD/CE). Context
construction beats context dumping — an agent assessing capability maturity
gets the Capability, Assessment, Evidence, Target, relevant services and
policies, not the entire enterprise graph. Performance, security,
explainability and LLM accuracy all improve.

## Role 2 — OpenDEA as governance

Authority, Policy, Decision, Evidence. The graph is where an agent's *license
to act* is evaluated (CR-9AJ):

```
Agent → Role → Authority → Policy → Scope → Action
```

A policy decision point returns **ALLOW / DENY / ESCALATE** (CR-9AK);
human-in-the-loop thresholds are policy-driven, never hard-coded (CR-9AL);
every action is audited — actor, authority, policy decision, result, evidence
(CR-9AM/CI).

## Role 3 — OpenDEA as agent infrastructure

Discovery, Context, Capability, Tool, Authority, Action, Audit. Agents
discover capabilities and tools semantically (CR-9AH/AI/AN), and the
Agent ↔ Tool ↔ Capability pattern (CR-9AO) lets the enterprise reason about
its agentic operating model — "which agents can currently act on this
capability?" (CR-9CB).

## The refusal — OpenDEA is not an AI agent framework

OpenDEA provides the **semantic context and governance substrate upon which
agentic systems operate**. Orchestration lives outside the Core: the
orchestrator consumes OpenDEA; OpenDEA records actions and results (CR-9AQ).
An agent must never infer "I can do this because the API exists" (CR-9AJ) —
and the runtime enforces this: **agents are read-only by default** (CR-9CR).

## Agent-assisted scenarios (CR-10AJ/AK) — the safe pattern

```
Agent
 ↓
Discover architecture context
 ↓
Identify gap
 ↓
Generate alternatives        Scenario A / B / C
 ↓
OpenDEA validates
 ↓
OpenDEA evaluates
 ↓
Agent summarizes
 ↓
Human decides
```

Agents may *propose* scenarios ("based on the maturity gaps, generate three
feasible transformation scenarios"). OpenDEA evaluates them. **The agent does
not get to approve one** (CR-10AJ). Recommendations are distinguishable from
decisions (CR-10AI), and every recommendation is explainable — criteria,
weights, evidence, assumptions, scenario results (CR-10AL). No opaque "AI
recommends Scenario B."

This is why the truth model ([concepts/truth-model.md](concepts/truth-model.md))
matters more every release: once agents produce architecture knowledge,
observed / asserted / inferred / approved must never be implicitly conflated.
