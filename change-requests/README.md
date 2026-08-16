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
| CR-004 | Core DEA Ontology | Small, stable normative core | Proposed |
| CR-005 | Assessment & Measurement | Separate DMM/measurement from architectural entities | Proposed |
| CR-006 | Temporal & Lifecycle Semantics | Current/target/transition/time-aware architecture | Proposed |
| CR-007 | Decision & Agentic Architecture | Decisions and agents first-class | Proposed — must not start before CR-2/3/4 |
| CR-008 | Governance, Risk & Control | Formalized governance semantics | Proposed |
| CR-009 | Extensions & Profiles | Modularize Data, AI, Security, Ecosystem, DMM | Proposed |
| CR-010 | Conformance, Validation & Migration | Automated validation and migration of existing models | Proposed |

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
