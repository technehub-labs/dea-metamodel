# Change Requests — OpenDEA Metamodel (CR-1.8)

Every metamodel modification is governed by a numbered Change Request.
CRs are processed strictly in dependency order: the next CR is parked until the
current one ships.

## Active programme — DEA Metamodel Remediation

| CR | Focus | Primary outcome | Status |
|---|---|---|---|
| [CR-001](CR-001.md) | Canonical Model & Semantic Governance | One authoritative metamodel and controlled versioning | Implemented (v0.6.0) |
| [CR-002](CR-002.md) | Relationship Semantics | Authoritative, typed relationship model | Implemented (v0.7.0) |
| [CR-003](CR-003.md) | Entity/Relationship Normalization | Removed duplicated relationship state; clean entity boundaries | Implemented (v0.8.0) |
| [CR-004](CR-004.md) | Core DEA Ontology | Small, stable normative core + profile architecture | Implemented (v0.9.0) |
| [CR-005](CR-005.md) | Assessment & Measurement | Separate DMM/measurement from architectural entities | Implemented (v0.10.0) |
| [CR-006](CR-006.md) | Temporal & Lifecycle Semantics | Current/target/transition/time-aware architecture | Implemented (v0.11.0) |
| [CR-007](CR-007.md) | Decision & Agentic Architecture | Decisions and agents first-class | Implemented (v0.12.0) |
| [CR-008](CR-008.md) | Semantic Architecture & Conformance Specification | Consolidation into an implementable standard | Implemented (v1.0.0) |
| [CR-009](CR-009.md) | Runtime, Knowledge Graph & Interoperability | Executable semantic substrate — graph, reasoning, integration, agentic runtime | In progress (CR-9.1 Runtime Foundation + CR-9.2 Knowledge Graph / Provenance + CR-9.3 Semantic Reasoning implemented; CR-9.4–9.10 Proposed) |
| [CR-010](CR-010.md) | Scenario, Simulation, Digital Twin & Decision Intelligence | What-if without mutating live state; transformation decision platform | In progress (Phase 1 Scenario Foundation + Phase 2 Impact Engine + Phase 3 Decision Intelligence + Phase 4 DMM Integration + Phase 5 Simulation Adapters + Phase 6 Agentic Scenario Generation + Phase 7 Digital Twin Foundation implemented; Phases 4–7 Proposed) |
| [CR-011](CR-011.md) | Interoperability, Federation & Ecosystem Conformance | Canonical semantic layer; adapters absorb external complexity | In progress (Phase 1 Semantic Interoperability Foundation + Phase 2 Identity & Reconciliation + Phase 3 Exchange JSON Schema implemented; Phases 3–8 Proposed) |
| [CR-012](CR-012.md) | Enterprise Intelligence & Advanced Agentic Runtime | Continuous reasoning → signal promotion → governed agentic action layer over the canonical semantic contract; signals/proposals as governed artifacts; same core-non-extension principle as CR-11 | Proposed (spec landed; phase plan in §7 awaiting sign-off) |
| CR-013 | Digital Twin / Continuous Enterprise Model | Synchronized operational state and behavioral semantics (per CR-10 §O) | Proposed |
| [CR-014](CR-014.md) | Assessment Metamodel v1 + Maturity Scoring v2 | Establish the assessment sub-metamodel as a coherent sub-tree (PlantUML + 12 JSON Schemas + governance); accept the maturity-scoring-v2 proposal (renames Emergent / Structured / Systematic / Adaptive / Self-Optimising, non-linear bands 20/25/25/18/12, per-level `effort_multiplier`) as canonical v2 alongside v1 | Implemented (sub-tree additive; no canonical version bump) |
| [CR-AM-02](CR-AM-02.md) | Implementation of OpenDEA Assessment Metamodel v1 | Phase-1 implementation of CR-AM-01: 12 P0 entity schemas, PlantUML, vocabulary, examples, migrations, CI; first migration (Technology Assessment) preserving legacy semantics. Satisfies all 20 acceptance criteria of CR-AM-02 §22. The 6-axis compatibility declaration (CR-AM-02 §11) and the result-side lineage shape (CR-AM-02 §12) are the architectural changes vs CR-014. | Implemented (Phase 1 implementation; no canonical version bump) |
| [CR-AM-03](CR-AM-03.md) | Assessment Catalog Migration & Integration | Migrates Technology, Modernization, Operations and Services Delivery from legacy instruments to canonical AssessmentModels, executions, results, migration manifests, coverage matrix, and a discoverable portfolio. Parent: CR-AM-02. | Implemented (additive; no canonical version bump) |
| [CR-AM-04](CR-AM-04.md) | Assessment Result Operations & Maturity Interpretation | Turns an AssessmentModel + AssessmentExecution into a reproducible AssessmentResult that distinguishes Observation / Score / Determination / Evidence / Finding / MaturityLevel, supports multi-dimensional maturity interpretation with a declared aggregation method, and derives Enterprise / Capability / Scenario views over the same result facts. Parent: CR-AM-03. | Proposed |
| [CR-015](CR-015.md) | Assessment-Profile ↔ Assessment-Sub-Tree Cross-Reference | Reciprocal doc-only cross-link between `metamodel/profiles/assessment/profile.yaml` and `assessment-models/`; completes the integration story left open by CR-014 §3 | Implemented (docs-only; no canonical version bump) |
| [CR-MM-01](CR-MM-01.md) | Maturity v2 Phase B — beta maturity model files | `assessment-models/maturity/v2-beta/` lands 5 domain YAMLs (EA Capability, Modernization, Technology, Operations, Services Delivery) with `legacy_name` aliases + v2 `effort_multiplier` per level. Content from v1-alpha preserved byte-identically. CI validator asserts v2-band alignment and legacy_name round-trip. | Implemented (additive; no canonical version bump) |
| [CR-MM-01.1](CR-MM-01.1.md) | Phase B follow-on — vocabulary registration + governance metadata | (a) register `scored-by-v2-bands` in `vocabulary/relationship-types.yaml`; (b) add CR-AM-01 §42 `steward`/`effective_date`/`review_date` to 5 v2-beta + 2 Phase A artefacts; (c) new CI `validate-relationship-vocabulary` for fail-fast on future vocabulary gaps. Closes two audit gaps from the CR-MM-01 / CR-AM-01 compliance review. | Proposed (metadata-only; no canonical version bump) |

## Record format

```yaml
CR-NNN
Title: <short title>
Status: Proposed | Accepted | Implemented | Closed
Version: <target metamodel version>
Depends on: <prior CRs>
```

## Freeze lifted (CR-1.6)

The semantic expansion freeze held through CR-003 (closed v0.8.0). New entity types now
enter via the CR process; CR-004 consolidates the core ontology.
