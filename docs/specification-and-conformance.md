# From Metamodel to Standard — the CR-8 Consolidation (OpenDEA 1.0)

> **CR-8 is not another expansion of the metamodel. It is the consolidation phase that
> turns the metamodel into a specification. (CR-8 preamble)**

This note records why CR-8 exists and the decisions that shaped OpenDEA 1.0. The formal
specification itself lives in [`specification/`](../specification/OpenDEA-Semantic-Architecture-Specification.md).

## 1. The question CR-8 answers

After CR-1…CR-7 the metamodel could describe, assess, govern and orchestrate an enterprise.
What it could *not* answer: **exactly what does it mean for a model to be
OpenDEA-conformant?** If two independent implementations can reach different conclusions
about the same model, there is no standard yet — only a rich model (§69).

## 2. The test that defines "done"

A third party, without access to our development conversations, takes only:

```
Specification + Schema + Profiles + Conformance Rules
```

and independently determines whether a model is conformant. Everything in CR-8 serves that:
canonical vocabulary, envelope schema, reference validator, golden models that MUST pass,
negative models that MUST fail for the expected reason.

## 3. Key decision points

| Decision | Rationale |
|---|---|
| **Core frozen at 18 anchors** (not the wider §3 candidate list) | §4 anti-inflation rule: a concept enters Core only if removing it breaks the general DEA semantic system. Intent/Policy/Agent/Assessment stay in profiles; promotion is a future governance act, not a consolidation side-effect. |
| **Repo conventions beat CR-text suggestions** | Where CR-8 §6 conflicted with conventions established since CR-1 (enum case, relationship id style), §22 itself defers to the existing schema. Consistency across 100+ artifacts > case aesthetics. Divergences are documented, not hidden. |
| **The viewer is a consumer, never a definer** (§47-§48, §67) | The repo must not simultaneously be conceptual model, schema, viewer data structure, visualization model and runtime model. Dependency direction: specification → schema → validator → reference models → viewer. Never reversed. |
| **Golden AND negative models** (§32-§33) | A specification you cannot test is prose. The negative suite makes conformance a contract: each invalid model fails for exactly its expected DEA-E code. |
| **Documentation is generated** (§49-§50) | Inventory, vocabulary and catalogues regenerate from the normative source (`generate_specification.py`) — no parallel hand-maintained truth to drift. |
| **Open-world Core, closed-world profiles** (§57) | Absence of evidence is not evidence of absence in Core; profiles may *require* semantics within their scope (a production Agent without policy is unknown to Core, non-conformant to the agentic profile). |
| **AI-generated assertions are marked, never equal** (§40-§41) | declared · observed · imported · inferred · generated · validated · approved — an LLM assertion is not a human-approved architectural fact. Provenance travels with the fact. |

## 4. What the reference validator already caught

On its first exercise the validator failed a golden model: `Orchestrator` could not be
`constrained-by` a Policy because the relationship's source types predated CR-7's
orchestration roles. The normative source was fixed the same day. That is the specification
working as intended — an executable interpretation finding semantic drift that prose review
missed.

## 5. What OpenDEA is after CR-8 (§68)

Not merely a model for *describing* enterprise architecture — a semantic framework for
representing the enterprise's architecture, intent, governance, decisions, change,
measurement, outcomes and increasingly autonomous actors as **one coherent system**:

DESCRIBE → ASSESS → DECIDE → CHANGE → OUTCOME → EVIDENCE → LEARNING → DECISION → HUMAN/AGENT ACTION.

## 6. What comes next (CR-9)

CR-8 established the language and the rules. **CR-9 — Execution, Interoperability &
Knowledge-Graph Runtime** establishes the runtime ecosystem: knowledge graph, query and
reasoning, assessment engine, decision engine, agentic orchestration, enterprise-system
integration, observed outcomes feeding back into the model. From "a metamodel that can
describe an enterprise" to "an executable semantic architecture substrate."

---

*Artifacts: `specification/` (22-section spec, core freeze, naming, type system,
relationship semantics, profile mechanism, conformance spec, serialization/versioning) ·
`tools/opendea_validate.py` · `models/golden/` + `models/invalid/` · `mappings/` ·
`visualization/profile/` · `tests/conformance/test_014_specification_rules.py`.*
