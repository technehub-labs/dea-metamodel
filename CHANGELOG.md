# Changelog

All notable changes to the OpenDEA Metamodel are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
`docs/versioning.md`.

## [0.12.0] — 2026-08-17 — CR-007: Decision, Intent, Policy, Governance & Agentic Semantics

### Added
- **Governance profile** `metamodel/profiles/governance/` — 14 entities: Intent, Objective,
  Policy, PolicyRule, PolicyEvaluation, PolicyDecision, DecisionOption, DecisionCriterion,
  DecisionRecord, Authority, Delegation, GovernanceBody, GovernanceRule, Action.
- **Agentic profile** `metamodel/profiles/agentic/` — 18 entities: Agent (specializes Actor),
  AgentProfile, AgentSkill, Tool, ToolPermission, Orchestrator, Controller, Orchestration,
  Workflow, Task, AutonomyPolicy, AutonomyLevel, HumanOversight, Approval, Escalation,
  AgenticSystem, AgentOpportunity, Memory.
- **24 relationships**: motivates, seeks, constrained-by, authorizes, performed-by,
  informed-by, delegates, grants, authorized-by, approves, establishes, consults, mitigates,
  escalates-to, evaluates, has-skill, invokes, coordinates, enforces, permits, prohibits,
  requires-approval, has-oversight, accesses.
- **G001–G016 conformance** (test_013) — suite now 112 tests.
- Core schema extensions: Decision + rationale/confidence/uncertainty/assumptions/authority_ref
  (§11/§17); Constraint + strength hard/soft/preference/guideline (§10);
  Action reversibility (§41).

### Changed
- Endpoint extensions: agents make Decisions (§65), GovernanceBody governs/establishes,
  owns covers Agents (G007), composes covers AgenticSystem (§58) and Decision options,
  accountable-for covers Decision/Action (G016), specializes wires Agent/Orchestrator/
  Controller under Actor (§27/§46).
- The causal loop is now complete: Intent → Objective → Policy → Decision → Action →
  Change → State → Outcome → Evidence → Assessment → new Decision (§2/§45/§68).

### Deferred
- 32 governance/agentic entities await upstream OpenDEAM allocation before entering the
  viewer graph.
- RACI profile (§37), AI Agent Maturity assessment profile (§54), agent readiness
  scoring (§55) → follow-up profiles reusing CR-5 machinery.
- LLM/prompt/RAG/vendor-framework specifics → technology profiles, deliberately out of
  scope (§66).

## [0.11.0] — 2026-08-17 — CR-006: Temporal, Lifecycle & Transition Semantics

### Added
- **Lifecycle profile** `metamodel/profiles/lifecycle/` — 18 entities: TemporalInterval
  (the five clocks: transaction/valid/observation/planned/effective — §5), TemporalEvent +
  TemporalState abstracts, LifecycleState/Event/Transition (§7/§28), Transition (§14),
  ArchitectureState + Baseline/Current/Target/Transition/Scenario specializations (§9–§13),
  Scenario + ScenarioAssumption (§25), ArchitectureSnapshot (§30), ArchitectureDelta (§32),
  Version (§19).
- **14 temporal relationships**: valid-during, contains, from-state, to-state, caused-by,
  introduces, removes, modifies, in-state, records, captures, may-become, version-of,
  precedes. New CR-2 category **L — temporal**.
- **temporal-dimension** — fifth cross-cutting overlay dimension for lifecycle entities
  (mirrors the measurement-dimension precedent).
- **Temporal pattern** on the entity base schema (§4) + **temporal relationship instances**
  (§21/§22): valid_from/valid_to/status/recorded_at on relationship-instance.json.
- **Temporal integrity rules** T001–T010 automated (test_012) — suite now 88 tests.

### Changed
- Endpoint extensions: Change → replaces/introduces/removes/modifies elements and realizes
  TargetState (§15); Change depends-on/enables Change (§34); supersedes widened to
  applications/services/technology (§20); type hierarchy wired via specializes.
- Change formalized with per-type lifecycles (§7): proposed→approved→in-progress→completed/
  cancelled; planned vs actual mandatory (§16); history never overwritten (§17).

### Deferred
- 18 lifecycle entities await upstream OpenDEAM allocation before entering the viewer graph.
- Timeline/state-selector/delta visualization → dea-web-viewer (CR-6 §42 Phase 9).
- Instance-level temporal validation (T001 ordering, T005 contradictions, T008 cycles) →
  validation services; metamodel-level guarantees automated here.

## [0.10.0] — 2026-08-17 — CR-005: Assessment, Measurement & DMM Integration

### Added
- **Assessment profile** `metamodel/profiles/assessment/` — 28 entities: Assessment,
  Framework, Dimension, Criterion, Indicator, Observation, Measure, Score, Scale, Unit,
  Result, Subject, Scope, Target, Gap, MaturityModel/Level/Scale/Rule, Aggregation/Scoring/
  MaturityMappingRule, Evidence/Source/Artifact, Benchmark/Population/Reference.
- **13 assessment relationships** + supports/produces endpoint extensions (§17/§10).
- **DMM profile** `metamodel/profiles/dmm/` — DMMv5 as AssessmentFramework instance:
  6 dimensions, maturity shell, scoring container, §23 dimension→DEA mappings;
  independently versioned (§33/A012).
- **A001–A013 conformance** (test_011); `generate_registry.py` (registry regen scripted).

### Changed
- **A008 enforced**: removed `Capability.maturity_level` classification — the §2
  anti-pattern found live in the vocabulary. Maturity now exists only via
  AssessmentResult + framework-owned MaturityLevel.

### Deferred
- 28 assessment entities await upstream OpenDEAM allocation; DMMv5 substantive content
  import; viewer assessment overlay (§39 Phase 9).

## [0.9.0] — 2026-08-16 — CR-004: OpenDEA Core Ontology

### Added
- **Core ontology** `metamodel/core/` — 18 anchors: 8 existing (Entity, Actor,
  OrganizationalUnit, BusinessCapability, Resource ×3 kinds) + 5 new abstracts
  (ArchitectureElement, Behavior, Service, Information, Organization) + 5 new concretes
  (Decision, Outcome, Requirement, Constraint, Change — each with schema, SQLite table,
  pydantic model, TTL class).
- **10 profiles** under `metamodel/profiles/` (business, ecosystem, digital, data,
  technology, ai, governance, assessment, dmm placeholder, ecf viewpoint) with explicit
  `depends_on` declarations; no circular dependencies (O004).
- **Core relationship grammar** (25 types) + 5 new registry relationships:
  `makes`, `results-in`, `targets`, `affects`, `contributes-to`.
- **Membership classification**: every entity carries `membership: core|profile`;
  viewer graph entities carry it too (viewer can render Core/Profile independently).
- **Ontology conformance** O001–O009 automated — suite now 59 tests.

### Changed
- Semantic backbone wired per CR-4 §20 (14 relationships gained core-anchor endpoints).
- CR-2 parked `targets` label RESOLVED → `dea:affects` (crosswalk updated).

### Deferred
- 10 new core anchors are not yet allocated in the upstream root model
  (dea-architecture-framework) — root model v0.6.0 candidate; viewer graph picks them
  up on the next sync.
- DMM profile content (CR-5), Agent ontology (CR-7), viewer Core/Profile rendering
  (dea-web-viewer PR).

## [0.8.0] — 2026-08-16 — CR-003: Entity & Relationship Normalization

### Removed (CR-3A — breaking for schemas, reversible via migration matrix)
- **70 relationship-state properties removed from 25 entity schemas** — the 37
  CR-2F-deprecated properties plus 32 ID-reference arrays (`processes`, `metrics`,
  `owned_*`, `parties`, `mitigates`, `technology_stack`, …) and `Capability.maturity_level`.
  Every removal has a disposition (target relationship or explicit re-assertion
  requirement) in `metamodel/migration/entity-normalization.yaml`.
- SQLite projection: `owner` columns (6), `parent_ou` (+index), `parent_concept`,
  `capabilities.maturity_level` dropped.

### Added
- `lifecycle_status` on every entity schema, driven by the new centralized vocabulary
  `metamodel/vocabularies/lifecycle.yaml` (CR-3R).
- `external_references {system, identifier}` on every entity schema + SQLite
  `entity_external_references` table (CR-3P) — external IDs never replace OpenDEA identity.
- `metamodel/vocabularies/classifications.yaml` — 55 controlled classification
  vocabularies, CI-synced against schema enums (E005).
- Entity conformance rules E001–E010 as automated tests (suite now 48 tests).
- `metamodel/migration/entity-normalization.yaml` (CR-3U/3V): 54 entity actions,
  58 property dispositions, migration metadata 0.7.0 → 0.8.0 (reversible).

### Changed
- `Technology.lifecycle_status` renamed to `adoption_status` (adoption posture is a
  classification, not the universal entity lifecycle).
- Relationship endpoints extended (normative, MINOR): supports+Actor source,
  realizes+BusinessObject, represents+EcosystemActor, composes+Actor,
  owns+BusinessProcess, informs+Entity targets.

### Deferred
- Abstract entity categories (CR-3L) → CR-4 consolidation.
- Agent as specialized entity (CR-3D) → CR-7.
- Assessment/maturity model (CR-3B target) → CR-5.

## [0.7.0] — 2026-08-16 — CR-002: Authoritative Relationship Semantics

### Added
- **Canonical relationship ontology**: 49 normative relationships (48 stored + 1 virtual
  inverse view) with full §3 structure — category (A–K taxonomy), canonical direction,
  typed source/target endpoints, cardinality at both ends, inverse declarations,
  transitive/symmetric flags, temporality, provenance requirement, lifecycle
  (`proposed | active | deprecated | retired`).
- **Relationship crosswalk** `metamodel/migration/relationship-crosswalk.yaml` — all 59
  viewer labels + 10 legacy instance-enum values explicitly dispositioned; nothing
  silently reinterpreted.
- **Instance metadata** (§6/§21/§22): `relationship-instance.json` v2 supports
  `effective_from/to`, `status`, `confidence`, `asserted_by`, `rationale`, `evidence`,
  structured `provenance` incl. `agent_id` + `verification_status` for AI-asserted
  relationships, and `mapping.kind` for narrowed `maps-to`.
- **Viewer graph-side migration** (2I): every edge carries canonical `rel_ids`;
  `relationship_definitions` embedded for viewer definition display; generator
  hard-fails on unmapped labels (R012).
- **Conformance rules R001–R012** as automated tests (suite now 37 tests).

### Changed
- `maps-to` narrowed to crosswalk/classification/traceability/equivalence semantics (§9).
- Overloaded relationships decomposed (§17): `governance`→governs/mandates/controls/owns/
  responsible-for; `implements` disambiguated from `realizes`/`operationalizes`/`supports`;
  `influences`→`informs`; split labels (`produces / consumes`, `publishes / subscribes`)
  decomposed.
- SQLite `relationships` table rebuilt from the registry: 48-type CHECK constraint,
  metadata columns; pre-0.7.0 columns retained but deprecated.
- TTL ObjectProperties regenerated from the canonical registry (48).
- Legacy viewer rel_types (7) demoted to rendering styles; categories are the semantics.

### Deprecated
- 35 duplicated relationship-state properties across 20 entity schemas (CR-2F) —
  physical removal in CR-003.
- Instance types `influenced-by`, `decomposes` (superseded — see crosswalk);
  instance fields `weight`, `bidirectional`.

## [0.6.0] — 2026-08-16 — CR-001: Canonical Metamodel

### Added
- **Normative metamodel source** `metamodel/dea-metamodel.yaml` — the single
  authoritative semantic definition (CR-1.1).
- **Metamodel manifest** `metamodel/manifest.yaml` (CR-1.2).
- **Entity and relationship registries** under `metamodel/registry/` with stable
  semantic IDs for all 54 entities and 17 relationships (CR-1.4, CR-1.5).
- **Governance docs**: `docs/architecture.md`, `docs/semantics.md`,
  `docs/versioning.md` (CR-1.7, CR-1.12).
- **Change-control mechanism** `change-requests/` with CR-001 as the first record
  (CR-1.8).
- **Conformance suite** `tests/conformance/` (tests 001–006, CR-1.9).
- CI enforcement of version consistency, referential integrity, duplicate IDs, and
  generated-artifact freshness (CR-1.11).

### Changed
- Unified version baseline: all artifacts converge on **0.6.0** (previously
  metamodel.yaml 0.3.0, VERSION 0.4.0, entity-graph 0.5.0, sqlite 0.1.0-alpha).
- README restructured: explicit Normative / Derived / Informative separation.
- `metamodel.yaml` (legacy root index) deprecated in favour of the normative source;
  retained for consumer compatibility until the catalog migration phase.

### Governance
- Semantic expansion freeze in effect until CR-003 closes (CR-1.6).
- Component versions separated: metamodel / JSON Schema / SQLite projection / viewer
  (CR-1.3).

## [0.5.0] — 2026-08-15
- ADR-0005: entity_role / completeness_contract; Resource abstract same-layer root.
  Synced from OpenDEAM root model v0.5.0 (53 entities, 2 dimension entities, 70 edges).

## [0.4.0] — 2026-08
- ADR-0004 renames: Principle→Tenet, Standard→Guardrail, Reference Model→Blueprint.

## [0.3.0] — 2026-08
- Root-model pin v0.3.0; entity-graph generation from OpenDEAM root.

## [0.1.0-alpha] — 2026-08
- Initial scaffold: schemas, SQLite projection, TTL ontology, viewer graph.
