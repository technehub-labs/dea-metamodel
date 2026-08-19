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
| [CR-010](CR-010.md) | Scenario, Simulation, Digital Twin & Decision Intelligence | What-if without mutating live state; transformation decision platform | In progress (Phase 1 Scenario Foundation + Phase 2 Impact Engine + Phase 3 Decision Intelligence implemented; Phases 4–7 Proposed) |
| [CR-011](CR-011.md) | Interoperability, Federation & Ecosystem Conformance | Canonical semantic layer; adapters absorb external complexity | In progress (Phase 1 Semantic Interoperability Foundation + Phase 2 Identity & Reconciliation implemented; Phases 3–8 Proposed) |
| CR-012 | Enterprise Intelligence / Advanced Agentic Runtime | Advanced intelligence and agentic capabilities (per CR-10 §O) | Proposed |
| CR-013 | Digital Twin / Continuous Enterprise Model | Synchronized operational state and behavioral semantics (per CR-10 §O) | Proposed |

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
