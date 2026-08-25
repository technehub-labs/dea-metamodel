# Changelog

All notable changes to the OpenDEA Metamodel are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
`docs/versioning.md`.

## [Unreleased] — CR-CM-001 follow-up: registry pointer downgrade

Follow-up slice of CR-CM-001 (terminology registry migration to
`technehub-labs/dea-concepts-model`). Specification and metamodel remain
**1.0.0**; no canonical version bump.

### Changed — terminology registry downgraded to pointer
- **`vocabulary/terminology-registry.yaml`** — the interim canonical
  registry (CR-CM-000 / CR-CM-000A §14) is replaced by a governed
  **pointer** to the canonical home
  (`technehub-labs/dea-concepts-model · governance/terminology-registry.yaml`,
  v1.1.0, `homed_by: CR-CM-001`). All content blocks (terms, verbs,
  prohibitions, Concept Areas, artifacts, rules, planned-repository
  mandate) now live solely in the canonical home — two diverging copies
  are exactly the failure the migration exists to prevent.
- **`tests/conformance/test_015_terminology_registry.py`** — rewritten
  from registry-content conformance to **pointer integrity**: canonical
  home declaration, non-canonical local status, full provenance
  (introduced/extended/homed), version parity, and a drift guard that
  fails if any content block reappears locally. Landed-spec guards
  (CR-CM-000/000A verbatim) and the bare-`domain:` forward guard are
  unchanged. Registry content conformance is owned by the canonical
  home, whose `tools/validate.py` exercises the vocabulary against every
  concept file (proven 11/11 violation classes at foundation).
- **`docs/concepts/terminology-alignment.md`**, **`README.md`**,
  **`change-requests/README.md`** — registry references updated to the
  canonical home + local pointer.

## [Unreleased] — CR-AM-07 Phase 4: Integration & governance

Final implementation phase of CR-AM-07. Specification and metamodel
remain **1.0.0**; additive surfacing + governance, no canonical version
bump.

### Added — comparison report surfacing
- **`runtime/comparison/report.py`** — `render_text` / `render_json`
  surface a `BenchmarkComparison` document as a human-readable report
  or canonical JSON. The report is a view over the derived artifact
  (CR-AM-07 §3): it renders exactly the schema-declared fields, in
  deterministic order (standings sorted by rank, JSON with sorted
  keys), and carries no CR-AM-08 vocabulary — insight, narrative,
  trend, and recommendation remain parked. CLI:
  `python -m runtime.comparison.report <comparison.yaml> [--format text|json]`.
- **`assessment-models/governance/comparison-policy.md`** — the
  comparison policy: eight policy rules (derived-never-truth,
  eligibility-only-door, minimum-sample gate, missing-data-N/A,
  declared methods, ties share standing, one cohort one snapshot,
  additive schema evolution), the Phase 4 surfacing contract, and the
  CR-AM-08 hand-off (what the insight layer consumes, may rely on,
  owns, and is never handed).
- **13 conformance tests**
  (`assessment-models/tests/conformance/test_comparison_report.py`) —
  header/cohort identity, distribution block, rank-ordered standings,
  tie semantics (shared rank 15, competition skip of 16), derivation
  hashes, determinism, JSON round-trip, schema-declared keys only,
  CR-AM-08 vocabulary guard, and CLI behaviour.
- **CI** — new `validate-cr-am-07-phase-4` job runs the report
  conformance suite.

### Changed
- `change-requests/CR-AM-07.md` status → Implemented (all four phases).
- `change-requests/README.md` CR-AM-07 row → Implemented.

## [Unreleased] — CR-AM-07 documentation: authored-scope decision record

Documentation-only follow-up to CR-AM-07. Specification and metamodel
remain **1.0.0**; no schema, runtime, or example changes.

### Added — documentation
- **`assessment-models/governance/comparison-policy.md`** — new
  "Deferred scope from the as-authored proposal (decision record)"
  section: preserves the eight statistical-semantics decisions from the
  original CR-AM-07 proposal that the four landed phases consciously
  narrowed (percentile ≠ absolute attainment, measurement-scale
  constraints, score-vs-maturity separation, metric direction, gap
  analysis, comparison confidence, multi-cohort participation,
  versioned benchmark metrics), with rationale and where each deferred
  item lands (CR-AM-08, extension phase, or a future metric-registry
  CR).
- `assessment-models/README.md` governance-tree annotation updated to
  point at the decision record.

## [Unreleased] — CR-AM-07 Phase 3: Percentile & ranking

Third implementation phase of CR-AM-07. Specification and metamodel
remain **1.0.0**; additive runtime module, no canonical version bump.

### Added — standings engine + comparison composer
- **`runtime/comparison/standings.py`** — `StandingsEngine` computes
  per-member percentile, rank, and peer position (`4/27`) over admitted
  members. Governed enums `PercentileMethod` (inclusive / exclusive) and
  `RankingRule` (competition / dense), values ≡ the Phase 1
  vocabularies. Ties share percentile and rank; competition ranking
  skips after a tie, dense does not. Admission guard, minimum-sample
  enforcement, and exclusion semantics are inherited from the Phase 2
  distribution engine.
- **`runtime/comparison/compose.py`** — `compose_comparison` is the only
  path that assembles a complete, schema-valid `BenchmarkComparison`
  document: distribution and standings derived together from the same
  member input over the same cohort snapshot, with membership hash and
  reproducibility hash (CR-AM-07 §10, §13).
- **17 conformance tests**
  (`assessment-models/tests/conformance/test_comparison_standings.py`) —
  worked-example regression (all 27 standings + hashes reproduced
  exactly), tie semantics under both ranking rules, both percentile
  methods, boundary guards, and composed-document schema validation.

## [Unreleased] — CR-AM-07 Phase 2: Distribution engine

Second implementation phase of CR-AM-07. Specification and metamodel
remain **1.0.0**; additive runtime module, no canonical version bump.

### Added — `runtime/comparison` distribution engine
- **`runtime/comparison/engine.py`** — `DistributionEngine.compute`
  derives cohort statistics (n, min/q1/median/q3/max, mean, sample
  standard deviation, IQR) over admitted members on the comparison axis.
  Exclusive median-of-halves quartiles; sha256 reproducibility hash over
  the canonically sorted score multiset. Emits distribution + exclusions
  only — percentile/rank/peer position remain Phase 3 (CR-AM-07 §11).
- **Enforced by construction** (CR-AM-07 §10): non-admitted members
  raise `ComparisonError` (eligibility is the only door); distributions
  below the cohort `minimum_sample_size` are refused, never silently
  emitted; members with missing/non-numeric scores are excluded with
  explicit machine-actionable reasons — never imputed (missing data is
  N/A, not zero).
- **`vocabulary/comparison-exclusion-reasons.yaml`** — governed reasons
  (`score-missing-on-comparison-axis`, `score-not-numeric`).
- **18 conformance tests**
  (`assessment-models/tests/conformance/test_comparison_distribution.py`),
  including the regression pin that the engine reproduces the Phase 1
  worked example's distribution *and* reproducibility hash exactly.

## [Unreleased] — CR-AM-07 Phase 1: Comparison vocabulary & schema

First implementation phase of CR-AM-07. Specification and metamodel
remain **1.0.0**; sub-tree additive, no canonical version bump. Phase 1
ships the comparison contract only — no distribution engine (Phase 2) or
percentile/ranking engine (Phase 3).

### Added — BenchmarkComparison schema + vocabularies + worked example
- **`assessment-models/schemas/benchmark-comparison.schema.json`** — a
  BenchmarkComparison binds a cohort *snapshot* (membership hash), the
  comparability key inherited verbatim from CR-AM-06, a single declared
  comparison axis, distribution statistics (n, quartiles, mean, spread),
  per-member standings (score, percentile, rank, peer position `4/27`),
  and full derivation metadata (percentile method, ranking rule,
  minimum-sample enforcement, excluded members with explicit reasons,
  reproducibility hash). The schema carries no eligibility or membership
  rules — CR-AM-06's surface is consumed, never redefined (CR-AM-07 §8).
- **`vocabulary/percentile-methods.yaml`** — `inclusive` / `exclusive`,
  with formulas; tied members always share a percentile.
- **`vocabulary/ranking-rules.yaml`** — `competition` (1,2,2,4) / `dense`
  (1,2,2,3); ties share the best rank.
- **`benchmark/comparison-examples/telecom-service-assurance-2026-comparison.yaml`** —
  the CR-AM-06 §10 worked shape made canonical over the §6 worked cohort:
  27 members, org-a at score 82 → percentile 88.5 → peer position 4/27
  (percentile under the declared `inclusive` method; §10's "87" was an
  illustrative shape), with an exercised tie at score 70.
- **16 conformance tests**
  (`assessment-models/tests/conformance/test_benchmark_comparison.py`) —
  schema/example validity, vocabulary ↔ enum parity, tie and ranking-rule
  semantics, minimum-sample enforcement, comparability-key inheritance,
  and the CR-AM-06/CR-AM-08 boundary guards.
- **CI**: `ci-assessment-models.yml` gains a
  `validate-comparison-against-schema` job; the YAML-parse glob now
  covers `benchmark/comparison-examples/`.

## [Unreleased] — CR-AM-07: Comparative Benchmarking & Peer Analytics (proposal)

Spec-only proposal for the CR-AM series successor to CR-AM-06.
Specification and metamodel remain **1.0.0**; no runtime, schema, or
example changes.

### Added — CR-AM-07 specification
- **`change-requests/CR-AM-07.md`** — defines `BenchmarkComparison` as a
  reproducible derivation over an admitted BenchmarkCohort: cohort
  distribution, percentile semantics, peer ranking & peer position, and
  the CR-AM-08 insight hand-off. Consumes CR-AM-06 eligibility without
  redefining it (§8 boundaries). Four-phase implementation plan (§11):
  vocabulary & schema → distribution engine → percentile & ranking →
  integration & governance.

## [Unreleased] — CR-CM-000A: Terminology Alignment (extension)

Extension to CR-CM-000, landed before the Concepts Model repository
exists (CR-CM-001). Specification and metamodel remain **1.0.0**.

### Added — supplement semantics encoded in the registry (v1.1.0)
- **`change-requests/CR-CM-000A.md`** — the extension, landed verbatim
  (md5 `5d2283edffd9ee2a7ccda015589017c2`).
- **`vocabulary/terminology-registry.yaml`** extended with: the §7
  canonical vocabulary (11 terms across MetaFramework / Concepts Model /
  Metamodel / Catalog layers, each with namespace/status/owner); the §9
  conceptual relationship verbs (`has-ecf-context`, `uses-domain`,
  `uses-stage`, `belongs-to`, `includes`, `maps-to` — with `maps-to`
  explicitly distinct from inheritance); the §10 prohibited semantics
  (bare `domain:` attribute, Concept-Area-as-Domain, Profile-as-Domain,
  implicit metamodel typing); the §11 nine initial Concept Areas; and the
  mandated `dea-concepts-model` repository layout (`concept-areas/`,
  never `domains/`; registry's long-term home
  `governance/terminology-registry.yaml`).
- **`docs/concepts/terminology-alignment.md`** — new §7 covering the
  extension.
- **10 new conformance tests** in
  `tests/conformance/test_015_terminology_registry.py` covering every
  supplement section.
- Companion document lands in `dea-metaframework`:
  `docs/terminology/concepts-model-alignment.md` (CR-CM-000A §16).

## [Unreleased] — CR-CM-000: Terminology Alignment

First CR of the Concepts Model (CM) series. Specification and metamodel
remain **1.0.0**; this CR is terminology governance only — no schema,
runtime, or version changes.

### Added — terminology registry + semantic boundaries
- **`vocabulary/terminology-registry.yaml`** — the authoritative
  terminology registry, introduced *before* the first canonical Concepts
  Model (CR-CM-000 AC-7). Bounds the five artifacts (Enterprise Concept
  Framework, OpenDEA Concepts Model, OpenDEA Foundational Metamodel,
  Catalogs, Profiles), reserves **Domain**/**Stage** for the ECF (every use
  must be *ECF Domain*/*ECF Stage* or namespace-qualified), and introduces
  the Concepts Model vocabulary: **Concept Area** (many-to-many
  membership), **Concept Profile**, **Concept Classification**, and
  **ECF Context** (zero-or-more; association, not identity — Concept Area
  ≠ ECF Domain, no automatic 1:1 mapping).
- **`docs/concepts/terminology-alignment.md`** — KB note capturing the
  CR's decisions, the five artifact boundaries, and the non-identity
  principle.
- **`tests/conformance/test_015_terminology_registry.py`** — 9 conformance
  tests covering registry integrity, reserved-term ownership, Concepts
  Model term constraints (AC-1…AC-7), and a forward guard against bare
  `domain:` fields in future Concepts Model artifacts.
- **`change-requests/CR-CM-000.md`** — the CR, landed verbatim (md5
  `2ec1e5c4539835f9b971ae7042280450`).

## [Unreleased] — CR-11 Phase 8: Conformance

Eighth and final phase of CR-11. Specification and metamodel remain
**1.0.0**; this phase realises the public conformance surface
(CR-11AM), conformance test suite (CR-11AN), and golden
interoperability datasets (CR-11AO). The OpenDEA CLI gains an
`opendea-conformance` entry point that emits a typed report.

### Added — conformance profiles + suite + golden datasets
- **`ConformanceClass`** extended with the six CR-11AM interoperability
  classes: `Exchange`, `Identity`, `Mapping`, `Runtime` (CR-11AM's
  "Runtime" side — encoded internally as `MAPPING_RUNTIME` to avoid
  clashing with the runtime's own usage of the word), `Federation`,
  `Agentic`. Adding a class is a contract change; the seven CR-9
  classes remain unchanged.
- **`ConformanceReport.render_text` + `render_json`** produce typed
  reports — the public CR-11AN contract includes `conformanceVersion`,
  `runtimeVersion`, `specVersion`, stable alphabetical
  `classesCovered`, and per-suite declarations.
- **`runtime.conformance.runner`** ships a default interop-roundtrip
  suite (Exchange / Identity / Mapping / Provenance / Federation) and
  an `opendea-conformance` CLI bound to it via `python -m runtime.conformance.runner`
  with `--format {text,json}` + `--runtime-version` + `--spec-version`
  + `--include-golden`.
- **`models/golden/basic-enterprise.yaml`** — the smallest
  conformance-valid OpenDEA graph (7 nodes / 5 edges across
  organisational, capability, application, service, actor, stakeholder
  + data dimensions). Validates against the canonical registry at load.
- **`golden_graph_assertions(basic-enterprise)`** regression baseline
  added; `test_model_loader.py` + `test_014_specification_rules.py`
  golden-suite count update from 7 → 8.
- 13 new runtime tests (384 total in `tests/runtime/`).

## [Unreleased] — CR-11 Phase 7: Federation

Seventh phase of CR-11. Specification and metamodel remain **1.0.0**;
this phase realises the *bounded* federation shape from
CR-11AH/AI/AJ + the CR-11AK boundary rule ("Do not implement a
universal federation engine"). Federation delivers entity-locality
labelling, a structured reference shape, and a query-dispatch facade
that can answer with local + remote sources under three explicit
strategies — never silently.

### Added — federation (`runtime/federation/`)
- **`EntityLocality`** (re-export) — the five canonical states
  (LOCAL / FEDERATED / IMPORTED / DERIVED / VIRTUAL) CR-11AI mandates.
- **`FederatedReference`** — system + adapter + external identifier +
  schema version; rejects incomplete references at construction.
- **`FederatedQuery`** — typed dispatch request with declared sources,
  authority policy name, and one of three strategies.
- **`AuthorityContext`** — the slice of the resolved AuthorityPolicy
  affecting one query; recorded on every result, never invented.
- **`FederationView.dispatch`** + **`FederationView.resolve_reference`**
  — the single entry point for bounded federation dispatch.
- **`SourceResolver`** + **`InGraphResolver`** pluggable resolvers;
  the in-graph resolver matches by entity id for `opendea` and by
  (system, external_identifier) for remote systems.
- **`RemoteSource`** + **`QueryAdapter`** + **`DirectQueryAdapter`** —
  the adapter shape: declare sources, run the chosen adapter, never
  invent identifiers the remote system did not return.
- **`ResolutionStrategy`** — IN_GRAPH_FIRST / SOURCE_PRIORITY / MERGED,
  declared by the caller; the dispatcher never re-orders silently
  (CR-11AK boundary).
- 13 new runtime tests (370 total in `tests/runtime/`).

## [Unreleased] — CR-11 Phase 6: Event Interoperability

Sixth phase of CR-11. Specification and metamodel remain **1.0.0**;
this phase wraps the CR-9H/I canonical event envelope with a
schema-first JSON contract (CR-11AF) and an end-to-end
external-event → knowledge-update pipeline (CR-11AG).

### Added — event envelope + pipeline (`runtime/events/`)
- **`EVENT_JSON_SCHEMA`** + `event_json_schema()` + `validate_envelope()`:
  Draft-07 contract for the canonical envelope. `additionalProperties`
  is `false`, the event-type taxonomy matches the CR-9H enum, and
  the optional `provenance` bag mirrors the CR-11S/T/U Exchange
  envelope so consumers can audit and reconcile events with no extra
  translation step.
- **`EventPublicationService.publish`** is the only path that turns a
  runtime mutation into a canonical event. The service validates
  every payload at the boundary and refuses to publish invalid
  envelopes.
- **`EventPipeline.ingest`** runs the full CR-11AG flow:
  `External Event → Adapter → OpenDEA Event → Knowledge Update →
  Rules → Assessment → Agent/Decision`, with pluggable hooks for
  rules, assessment and agent stages plus a knowledge-update
  applier for the four entity-/relationship-mutating event types.
- **`PassthroughAdapter`** validates an envelope as-is; subclasses
  can lift any external wire format into the canonical shape.
- **`derive_updates(event)`** maps ENTITY_CREATED / ENTITY_CHANGED /
  ENTITY_DELETED / RELATIONSHIP_CHANGED to `KnowledgeUpdate` hints;
  the other event types pass through so downstream stages can react.
- 14 new runtime tests (357 total in `tests/runtime/`).

## [Unreleased] — CR-11 Phase 5: Reference Mappings

Fifth phase of CR-11. Specification and metamodel remain **1.0.0**;
Phase 5 lands canonical mappings from OpenDEA into the four most
relevant EA-domain standards — ArchiMate, BPMN, DMN, DMM — in that
order. Mappings are *informative bridges*: OpenDEA never adopts the
external metamodel (CR-11W); standards-specific concepts without an
OpenDEA counterpart are recorded as Extensions in the standard's own
namespace (CR-11AR), never absorbed into the core.

### Added — reference mappings (`mappings/`, `runtime/interoperability/mapping_loader.py`)
- **`mappings/archimate/mapping.yaml`** — CR-11X extends the CR-8 §45
  matrix with explicit relationship classes, confidence/lossiness on
  every entry, and the document rule that composite/approximate
  alignments are marked, never smoothed over.
- **`mappings/bpmn/mapping.yaml`** (new) — CR-11Y: Process / Task /
  Sub-Process / Event / Gateway mapping to OpenDEA's
  BusinessProcess/Workflow/Task/TemporalEvent/DecisionCriterion shapes.
- **`mappings/dmn/mapping.yaml`** (new) — CR-11Z: the DMN profile
  shape (Decision → Decision → Decision Evidence → Decision Outcome)
  plus FEEL preservation (rule-expression kind: `dmn-feel`).
- **`mappings/dmm/mapping.yaml`** (new) — Phase 5 DMM band
  correspondence: DMM Level 1–5 ↔ OpenDEA maturity v2
  Emergent/Structured/Systematic/Adaptive/Self-Optimising.
- **`MappingRegistry` + `load_reference_mappings`** lifts the YAML
  files into an :class:`InteropRegistry` with governed mappings,
  confidence + lossiness, and an Extension fallback for unmapped
  concepts. 8 new runtime tests (343 total in `tests/runtime/`).

## [Unreleased] — CR-MM-01.1: Maturity v2 Phase B follow-on — vocabulary + governance metadata

Closes two alignment gaps surfaced by the post-CR-MM-01 / CR-AM-01 compliance audit
on 2026-08-21:

1. **`scored-by-v2-bands` registered** in `assessment-models/vocabulary/relationship-types.yaml`
   (CR-MM-01 introduced this relationship type but did not register it; CI did not catch it).
2. **CR-AM-01 §42 governance fields added** to 5 v2-beta maturity models and the 2 Phase A registry
   artefacts: `steward`, `effective_date: 2026-08-21` (or `2026-08-20` for Phase A), `review_date: 2027-02-21` (or `2027-02-20`).

### Added
- `assessment-models/vocabulary/relationship-types.yaml`: new entry `scored-by-v2-bands`
  (source_kinds: maturity-model, target_kinds: maturity-bands).
- `assessment-models/maturity/v2-beta/{ea-capability,modernization,technology,operations,services-delivery}.yaml`:
  each gains `steward`, `effective_date`, `review_date`.
- `assessment-models/maturity/maturity-bands-v2.yaml` and `v2-to-v1-legacy-name-map.yaml`:
  each gains `owner`, `steward`, `effective_date`, `review_date`.
- `.github/workflows/ci-assessment-models.yml`: new CI job `validate-relationship-vocabulary`
  asserts every `relationship_type` value in `maturity/*`, `maturity/v2-beta/*`,
  `maturity/examples/*`, `examples/*` is registered in the controlled vocabulary.

### Behaviour
- None. This is metadata-only. All v2-beta maturity model content (characteristics, exit
  criteria, evidence) is unchanged from CR-MM-01. All v1 → v2 scoring logic is unchanged.
  Phase C consumer tooling remains parked for CR-MM-02.

See [CR-MM-01.1](change-requests/CR-MM-01.1.md).

## [Unreleased] — CR-11 Phase 4: External Provenance

Fourth phase of CR-11. Specification and metamodel remain **1.0.0**;
this phase extends the CR-9.2 / CR-11 Phase 1–3 internal provenance
graph with the *external* source chain so every canonical fact remains
traceable back to where it came from, and exposes a PROV-shaped
projection so the chain is interoperable with established provenance
vocabularies.

### Added — external provenance (`runtime/provenance/external.py`)
- **`ExternalProvenanceService.record_external_source`** registers an
  Evidence + Source pair atomically with its ExternalIdentifier
  correlation in the InteropRegistry (CR-11O).
- **`ExternalProvenanceService.integration_chain`** walks
  OpenDEA Entity → Assertion → Evidence → Mapping → Adapter →
  ExternalIdentifier → External System (CR-11BD).
- **`prov_projection`** exposes any Assertion as PROV-style
  Entity / Activity / Agent / Source (CR-11AE).
- 5 new runtime tests (335 total in `tests/runtime/`).

## [Unreleased] — CR-MM-01: Maturity v2 Phase B — beta maturity model files

A new `assessment-models/maturity/v2-beta/` directory lands five YAML files
— one per canonical maturity domain — that mirror the v1-alpha originals
in `Assessment-Models/dea-catalog-maturity-models` (archived) but use v2
level ids, names, score ranges, and `legacy_name` aliases, plus a new
per-level `effort_multiplier`.

### Added — `assessment-models/maturity/v2-beta/`
- `ea-capability.yaml` — domain: enterprise-architecture
- `modernization.yaml` — domain: modernization
- `technology.yaml` — domain: technology
- `operations.yaml` — domain: operations
- `services-delivery.yaml` — domain: services-delivery
- Each carries `status: beta`, `score_scheme: dea-maturity-v2`, `band_reference: ../maturity-bands-v2.yaml`, `legacy_model: ../v2-to-v1-legacy-name-map.yaml`.
- Content fidelity: every level's `summary`, `characteristics`, `exit_criteria`, `evidence` is preserved byte-identically from v1-alpha.

### Added — CI validator
- New job `validate-v2-beta-models` in `.github/workflows/ci-assessment-models.yml` asserts:
  - exact 5-file count and complete coverage of the five domains
  - every level's `id` / `name` / `score_range` / `effort_multiplier` matches the canonical `maturity-bands-v2.yaml`
  - every level's `legacy_name` round-trips through `v2-to-v1-legacy-name-map.yaml`
  - every level has non-empty `summary`, `characteristics`, `exit_criteria`, `evidence`
- `validate-yaml` glob extended to include `assessment-models/maturity/v2-beta/*.yaml`.

Specification and metamodel remain **1.0.0** — no canonical VERSION bump.
See [CR-MM-01](change-requests/CR-MM-01.md).

## [Unreleased] — CR-015: Assessment-Profile ↔ Assessment-Sub-Tree Cross-Reference

Documentation-only reciprocal cross-link between
`metamodel/profiles/assessment/profile.yaml` and `assessment-models/`.
Closes the integration story left open by CR-014 §3 (explicitly out of scope
for CR-014 itself).

### Added — reciprocal cross-link
- `metamodel/profiles/assessment/profile.yaml` gains a `cross_references:`
  block pointing at `assessment-models/` (kind: internal-sub-tree,
  relation: integrates_with, canonical_url anchor).
- `assessment-models/README.md` gains a `### Upstream profile` subsection
  pointing back at the profile and stating the layering convention.

Specification and metamodel remain **1.0.0** — no canonical version bump.
See [CR-015](change-requests/CR-015.md).

## [Unreleased] — CR-11 Phase 3: Exchange JSON Schema

Third phase of CR-11. Specification and metamodel remain **1.0.0**;
the canonical exchange envelope is now validated against an explicit
JSON Schema and round-trips through import/export with ExternalIdentifier
links.

### Added — exchange service (`runtime/interop/exchange_service.py`)
- **`EXCHANGE_JSON_SCHEMA`** + `exchange_json_schema()` for the canonical
  Exchange envelope.
- **`ExchangeService.export_graph`** produces an Exchange from any
  GraphStore.
- **`ExchangeService.import_exchange`** materialises entities, edges
  and external-identifier links from an Exchange.
- **`ExchangeService.validate`** runs schema + semantic checks.
- 6 new runtime tests (205 total in `tests/runtime/`).

## [Unreleased] — CR-10 Phase 7: Digital Twin Foundation

Final phase of CR-10. Specification and metamodel remain **1.0.0**;
the runtime supports observation, operational state, and drift detection
against the architecture baseline. The full "digital twin" claim remains
deferred until synchronization and behavioral semantics exist (CR-013).

### Added — digital twin foundation (`runtime/twin/`)
- **`DigitalTwin.observe(subject, observed_state, at)`** records an
  observation as both an in-memory event and a graph `Observation` node
  traced from the subject.
- **`current_state(subject)`** returns the latest `OperationalState`.
- **`state_diff(subject)`** compares architecture lifecycle against
  observed state, returning explicit drift signals.
- 6 new runtime tests (199 total in `tests/runtime/`).

## [Unreleased] — CR-10 Phase 6: Agentic Scenario Generation

Sixth phase of CR-10. Specification and metamodel remain **1.0.0**;
agentic scenario generation produces candidates that close a maturity gap,
with humans retained in the approval loop.

### Added — agentic scenario proposal (`runtime/agentic/`)
- **`ScenarioProposer.propose_scenarios_for_gap(gap_id)`** returns a
  `ScenarioProposalReport` with candidate scenarios, impact summaries and
  a recommendation that is **never approved by default** (CR-9CR).
- Candidates are evaluated against the CR-10 Phase 5 simulation adapter.
- 5 new runtime tests (193 total in `tests/runtime/`).

## [Unreleased] — CR-10 Phase 5: Simulation Adapters

Fifth phase of CR-10. Specification and metamodel remain **1.0.0**;
the runtime is the semantic coordination layer; domain simulators live behind
`SimulationAdapter`.

### Added — simulation adapters (`runtime/simulation/`)
- **`SimulationAdapter` ABC** with `prepare / execute / retrieve_results /
  map_results / validate` lifecycle.
- **`ScenarioImpactAdapter`** reference implementation that runs the CR-10
  Phase 2 impact engine locally.
- **`SimulationRegistry`** dispatches by capability.
- **`SimulationRequest` / `PreparedRequest` / `ExecutedRun` /
  `SimulationResult` / `MappedResult`** value objects preserve engine
  contract, model version, parameters and assumptions.
- 6 new runtime tests (188 total in `tests/runtime/`).

## [Unreleased] — CR-10 Phase 4: DMM Integration

Fourth phase of CR-10. Specification and metamodel remain **1.0.0**;
maturity projection is the gap-to-initiative transition layer.

### Added — maturity projection (`runtime/maturity/`)
- **`MaturityProjector.project(gap_id)`** returns a `MaturityProjection`
  with current/target/projected maturity and proposed initiative ids.
- Projects the maturity gap forward using the available ChangeInitiative
  candidates in the graph.
- 6 new runtime tests (182 total in `tests/runtime/`).

## [Unreleased] — CR-9.9: OpenDEA Explorer

Final tenth milestone of CR-9. Specification and metamodel remain **1.0.0**;
the Explorer exposes the runtime through the seven-module API surface.

### Added — Explorer runtime API ()
-  enum with the seven modes (explore / assess / trace /
  compare / query / simulate / govern).
-  wrap the underlying runtime services.
-  exposes conclusion → evidence → source provenance.
- 8 new runtime tests (176 total in ).

## [Unreleased] — CR-9.8: Agent Runtime

Eighth milestone of CR-9. Specification and metamodel remain **1.0.0**; the
agent runtime is the governance surface for discovery, authority, policy,
audit and tool registry.

### Added — agent runtime (`runtime/agent/`)
- **`AgentRuntime.request_authorization`** returns ALLOW / DENY / ESCALATE
  driven by `Policy` nodes carrying `action`, `effect` and optional `actor_role`.
- **`audit_log`** records every decision with agent, action, target, effect,
  policy reference and timestamp.
- **`ToolRegistry`** maintains a `provides -> capability` mapping and supports
  agent → tool binding.
- 7 new runtime tests (168 total in `tests/runtime/`).

## [Unreleased] — CR-9.7: Decision & Impact Engine

Seventh milestone of CR-9. Specification and metamodel remain **1.0.0**; the
decision & impact engine is an executable governance layer over runtime
decisions, gaps and outcome proposals.

### Added — decision & impact engine (`runtime/decision/`)
- **`DecisionImpactEngine.evaluate_decision`** against the live graph: targeted
  outcomes, addressed gaps, dependency paths.
- **`dependency_paths`** BFS through active edges (status `deprecated` / `retired`
  excluded) returning explicit node + edge sequences.
- **`propose_initiatives`** writes `Outcome` nodes into the graph with explicit
  `results-in` authorship from the decision; duplicate ids are skipped.
- **DecisionError** for unknown / non-Decision nodes.
- 5 new runtime tests (161 total in `tests/runtime/`).

## [Unreleased] — CR-9.6: Assessment Runtime

Sixth milestone of CR-9. Specification and metamodel remain **1.0.0**; assessment
is the executability layer for the CR-5 assessment profile.

### Added — assessment runtime (`runtime/assessment/`)
- **`AssessmentService.execute_assessment`** walks the assessment graph,
  aggregates measures, applies the scoring strategy and maturity mapping, and
  persists an `AssessmentResult` with full provenance.
- **AssessmentGap** recorded automatically when current maturity is below
  `target_maturity`.
- **Golden DMM executable** fixture: `models/dmm/executable.yaml`.
- 5 new runtime tests (156 total in `tests/runtime/`).

## [Unreleased] — CR-9.5: Integration Framework

Fifth milestone of CR-9 (Runtime, Knowledge Graph & Interoperability). Specification
and metamodel remain **1.0.0**; integration is additive runtime machinery over
the CR-9.1 graph and the CR-11 interop foundation.

### Added — integration service (`runtime/integration/`)
- **`IntegrationService.run_full_import` / `run_incremental_import`** materialise
  ExternalSystem payloads as OpenDEA entities with source metadata and
  ExternalIdentifier links.
- **Source metadata on every imported entity:** `sourceSystem`, `sourceTag`,
  `sourceRecord` are recorded on the node's properties and the `source`
  envelope.
- **Conflict preservation:** when an incremental import disagrees with an
  existing entity's `lifecycle_state` or `classification`, the disagreement is
  recorded as a `KnowledgeConflict` rather than silently overwritten.
- 5 new runtime tests (146 total in `tests/runtime/`).

## [Unreleased] — CR-9.10b: Interoperability & Performance Suites

Second half of CR-9.10 (Conformance & Interoperability Release). Specification
and metamodel remain **1.0.0**.

### Added — interop + performance suites (`runtime/conformance/`)
- **Interop scenarios (CR-9CM):** three end-to-end scenarios — external-id
  correlation, reasoning materialization, full scenario impact pipeline —
  spanning the CR-9.2 provenance, CR-9.3 reasoning, CR-10 scenario, and
  CR-11 interop layers.
- **Performance suite (CR-9CJ/CK):** synthetic 1K / 10K enterprise models
  exercising load + query + traversal against the reference in-memory store
  with explicit engineering-target budgets.
- **Conformance class coverage:** the interop suite covers API, Validation,
  Provenance; the performance suite covers Query.
- 6 new runtime tests (146 total in `tests/runtime/`).

## [Unreleased] — CR-9.10a: Conformance classes, golden graphs, runner

First half of CR-9.10 (Conformance & Interoperability Release). Specification
and metamodel remain **1.0.0**; conformance is the audit surface for the
runtime programme.

### Added — conformance suite (`runtime/conformance/`)
- **Runtime conformance classes (CR-9CL):** the seven classes — Core, Profile,
  API, Query, Validation, Provenance, Security — are declared explicitly
  (`ConformanceClass` enum) and cannot be silently extended.
- **Excluded endpoints audit:** `EXCLUDED_ENDPOINTS` documents which runtime
  surfaces the public suite deliberately does not exercise, including
  `store.infer` and any future autonomous-mutation endpoints.
- **Golden graphs (CR-9CN):** `GOLDEN_GRAPHS` reuses the existing canonical
  fixtures (`models/golden/{enterprise,dmm}.yaml`,
  `models/scenarios/customer-service-baseline.yaml`) and asserts expected
  node/edge counts and loadability.
- **Conformance runner:** `run_conformance(suites)` produces a `ConformanceReport`
  with the aggregated set of conformance classes covered by the suite catalog.
- 5 new runtime tests (140 total in `tests/runtime/`).


## [Unreleased] — CR-9.4: Temporal & Event Runtime

Fourth milestone of CR-9 (Runtime, Knowledge Graph & Interoperability).
Specification and metamodel remain **1.0.0**; the temporal/event runtime is
additive on the CR-9.1 graph and the CR-9.2 provenance layer.

### Added — temporal/event runtime (`runtime/temporal/`)
- **Bitemporal truth (CR-9G):** `as_of(valid_at, recorded_at=None)` answers
  "what was true at valid_at, as we knew it at recorded_at" using the
  edge `recorded_at` property alongside `valid_from`/`valid_to`.
- **Current-time filter (CR-9F):** `what_is_true_now(store, entity_id)` returns
  only neighbours whose edges are currently valid and non-retired /
  non-planned.
- **Event envelope (CR-9H):** `Event` carries id, type, subject, occurredAt,
  observedAt, source, version, payload and the canonical EventType taxonomy.
- **Event log (CR-9I):** `EventLog` is append-only and exposes
  `filter(subject, type)`.
- **Snapshots and drift (CR-9BI/BD/BE):** `snapshot_graph(store, id, label)`
  freezes any GraphStore; `diff_snapshots(before, after)` reports
  added/removed/modified entities and edges.
- 8 new runtime tests (135 total in `tests/runtime/`).

## [Unreleased] — CR-10 Phase 3: Decision Intelligence

Third phase of CR-10 (Scenario, Simulation, Digital Twin & Strategic Decision
Intelligence). Specification and metamodel remain **1.0.0**; decision
intelligence is additive runtime machinery over Phases 1–2.

### Added — decision intelligence (`runtime/scenario/decision.py`)
- **Metrics as semantic objects** (CR-10J): id, definition, unit, calculation,
  source, baseline and target.
- **Explicit criteria and weights** (CR-10M): `Criterion` requires a visible
  non-zero weight; no weights are hidden in algorithms.
- **Decomposable scoring** (CR-10N): every `ScenarioScore` exposes criterion
  value, normalized weight and weighted contribution.
- **Comparison and ranking** (CR-10F/L): deterministic scenario ordering by
  weighted score with stable tie-breaking.
- **Recommendation ≠ decision** (CR-10AI): `Recommendation.approved_decision`
  is always false; approval remains governed decision machinery.
- **Explainable recommendation** (CR-10AL): rationale, criteria, weights,
  evidence and assumptions are returned with the recommendation.
- 6 new runtime tests (127 total in `tests/runtime/`).

## [Unreleased] — CR-9.3: Semantic Reasoning

Third milestone of CR-9 (Runtime, Knowledge Graph & Interoperability).
Specification and metamodel remain **1.0.0**; reasoning is additive runtime
machinery over the CR-9.1 graph and CR-9.2 provenance layer.

### Added — reasoning engine (`runtime/reasoning/`)
- **Governed rule registry** (CR-9S): rules carry id, name, version,
  enabled/disabled state, profile scope, severity, declared `applies_to` scope
  and executable condition. Duplicate or out-of-scope derivations are rejected.
- **Levelled inference** (CR-9R): Deterministic, Ontological, Graph,
  Probabilistic and Generative levels are explicit and recorded on every
  `Inference`; levels are never blended.
- **Evaluation ≠ materialization** (CR-9CQ): `ReasoningEngine.infer()` derives
  candidate conclusions without mutating the graph. `materialize()` is an
  explicit second step that records the result as a **PROPOSED** assertion via
  the CR-9.2 provenance layer — never as approved fact.
- **Explainability** (CR-9T): every inference records rule, level, supporting
  inputs, explanation steps and confidence; `explain()` returns the structured
  Why chain.
- 7 new runtime tests (121 total in `tests/runtime/`).

## [Unreleased] — CR-11 Phase 2: Identity & Reconciliation

Second phase of CR-11 (Interoperability, Federation & Ecosystem Conformance).
Specification and metamodel remain **1.0.0**; identity reconciliation is
additive runtime machinery over the Phase-1 interoperability foundation.

### Added — identity reconciliation (`runtime/interoperability/identity.py`)
- **EntityResolution** with the full reconciliation-state vocabulary
  (CR-11K/L): `UNMATCHED`, `CANDIDATE`, `MATCHED`, `MERGED`, `CONFLICTING`,
  `REJECTED`. Thresholded exact/candidate matching; below the auto-match
  threshold results are reviewable candidates, never silent merges.
- **KnowledgeConflict** (CR-11L): first-class preservation of source
  disagreement. Every competing value remains in the conflict; resolution
  records the chosen value plus the policy, actor and timestamp.
- **AuthorityPolicy** (CR-11M/N): property-specific source authority across
  `(source, property)` pairs. Five tie-breakers: `highest`, `newest`,
  `most-confident`, `human`, `no-write`. Undeclared authority is rejected
  (CR-11R).
- **No silent merge**: `approve_resolution` requires an explicit actor and
  the chosen entity must be a candidate; `MERGED` without approval is rejected.
- **External ids never adopted**: approved resolutions add an
  `ExternalIdentifier` link; the canonical entity id is unchanged.
- 13 new runtime tests (114 total in `tests/runtime/`).

## [Unreleased] — CR-10 Phase 2: Impact Engine

Second phase of CR-10 (Scenario, Simulation, Digital Twin & Strategic Decision
Intelligence). Specification and metamodel remain **1.0.0**; impact analysis is
additive runtime machinery over the Phase-1 scenario foundation.

### Added — impact engine (`runtime/scenario/impact.py`)
- **Impact graph** (CR-10G): dependency propagation from explicit scenario
  changes, with direct (depth 1) vs indirect (depth > 1) impact and exact
  relationship paths.
- **Impact categories** (CR-10G): strategic, business, capability, process,
  customer, data, application, technology, security, risk, agent, governance,
  financial, operational.
- **Explicit impact valence** (CR-10H): Positive / Negative / Neutral / Mixed /
  Unknown. Affected never automatically means negative; valence changes only
  through caller-supplied rules.
- **Change analysis**: every CR-10C delta operation reports added / removed /
  modified entities plus propagated impacts.
- **Architecture delta**: canonical graph-snapshot diff for added, removed and
  modified entities and relationships.
- **Golden impact report** for the CR-10AS customer-platform replacement
  scenario.
- 5 new runtime tests (101 total in `tests/runtime/`).

## [Unreleased] — CR-9.2: Knowledge Graph & Provenance

Second milestone of CR-9 (Runtime, Knowledge Graph & Interoperability).
Specification and metamodel remain **1.0.0**; the provenance graph is additive
runtime machinery over the frozen semantic contract.

### Added — provenance graph (`runtime/provenance/`)
- **First-class runtime assertions** (CR-9O): claims carry subject, payload,
  `asserted_by`, confidence, validity window and status (`proposed`, `verified`,
  `approved`, `rejected`, `superseded`, `disputed`). Assertions are encoded as
  canonical `KnowledgeAsset` nodes with `provenance_kind=assertion`, preserving
  the frozen Core.
- **Evidence graph** (CR-9P): Evidence and EvidenceSource are graph citizens;
  lineage uses canonical `traces-to`, while loaded models expressing
  `Evidence -supports→ AssessmentResult` join the same explainability path.
- **Provenance chain / Why?** (CR-9T/BC): `ProvenanceService.why(subject)`
  returns Conclusion → Assertions → Evidence → Sources with stable structured
  output — the runtime seed for CR-9BZ "Why?" navigation.
- **Explicit authority transitions** (CR-9CQ): assertions cannot be created
  approved; status changes are actor-stamped, reason-carrying transitions with
  history. Derived assertions retain `derived_from` and `derivation_rule`.
- 9 new runtime tests (96 total in `tests/runtime/`).

## [Unreleased] — CR-11 Phase 1: Semantic Interoperability Foundation

First phase of CR-11 (Interoperability, Federation & Ecosystem Conformance).
Specification and metamodel remain **1.0.0**. Governing principle (CR-11 §2):
OpenDEA is the semantic contract; adapters absorb external complexity.

### Added — interoperability foundation (`runtime/interoperability/`)
- **Four distinct concepts, never conflated** (CR-11A): `ExternalSystem`
  (Source), `IntegrationAdapter` (semantic mechanism — distinct from the
  transport *connector*, CR-11D), `SemanticMapping` (correspondence),
  `Exchange` (the transfer).
- **`SemanticMapping`** with the full mapping vocabulary (CR-11F:
  EQUIVALENT…NO_CORRESPONDENCE), explicit confidence (CR-11G), declared
  lossiness (CR-11AQ), testable transformations (CR-11H), and governance —
  owner/version/status/effective/deprecation dates; SUPERSEDED requires a
  replacement reference (CR-11AT/AU).
- **`ExternalIdentifier`** (CR-11I): external record ids are correlated,
  never adopted as canonical identity. `InteropRegistry.resolve()` is exact
  match only — reconciliation/confidence lands in Phase 2.
- **`Extension`** (CR-11AR): unmappable external concepts are preserved in
  non-`opendea` namespaces — never discarded, never absorbed into Core
  (ADR-013, CR-11 §66).
- **`Exchange` envelope** (CR-11S/V) with schema/profile/mapping version
  declarations; `InteropRegistry.export()` produces the canonical JSON
  exchange from any GraphStore — semantics, not storage layout (CR-11U).
- **Integration error taxonomy** (CR-11AW) and import-mode / sync-direction /
  locality vocabularies (CR-11P/Q/AI).
- Credential safety: `ExternalSystem.authentication` is a credential-store
  reference; inline secrets are rejected (CR-11AY).
- 16 new runtime tests (87 total in `tests/runtime/`).

### Added — interoperability documentation (CR-11BE)
- `docs/interoperability/` — overview, architecture, identity, mappings,
  federation, events, security, exchange-format, provenance, archimate,
  bpmn, dmn, conformance (13 documents).
- `docs/adr/ADR-013-core-non-accumulation.md` — the CR-11 §66 correction:
  the Core does not accumulate; adapters absorb external complexity.
- `change-requests/CR-011.md` — the CR as authored.

## [Unreleased] — CR-10 Phase 1: Scenario Foundation + Documentation Consolidation

First phase of CR-10 (Scenario, Simulation, Digital Twin & Strategic Decision
Intelligence) plus the CR-1→CR-10 documentation consolidation CR-10 calls for
(§A–§P). Specification and metamodel remain **1.0.0**.

### Added — scenario foundation (`runtime/scenario/`)
- **Scenario as a first-class semantic object** (CR-10A): id, owner, purpose,
  baseline reference, assumptions, changes, constraints, affected entities
  (derived), expected outcomes, lifecycle status, version, provenance.
- **Baseline immutability + simulated-state isolation** (CR-10B): baselines are
  frozen snapshots; `ScenarioEngine.simulate()` applies the delta to a *fresh*
  graph — production/current state is never mutated.
- **Explicit delta vocabulary** (CR-10C): ADD, REMOVE, REPLACE, MODIFY,
  RECLASSIFY, CONNECT, DISCONNECT, ENABLE, DISABLE, MOVE, SCALE — structural
  (Level 0, CR-10K) semantics with registry validation.
- **Explicit assumptions, constraints, outcomes** (CR-10D/E/I) with
  **uncertainty classes** (CR-10O: Known/Estimated/Assumed/Predicted/
  Simulated/Unknown) — forecasts are never deterministic facts.
- **Scenario lifecycle enforcement** (CR-10A), **frozen evaluated versions +
  explicit versioning** (CR-10AG), **reproducibility hash** (CR-10AF).
- **Golden scenario** `models/scenarios/customer-platform-replacement.yaml` +
  baseline model — the CR-10AS canonical example, exercised end-to-end in
  `tests/runtime/test_golden_scenario.py`.
- 22 new runtime tests (71 total in `tests/runtime/`).

### Added — documentation consolidation (CR-10 §A–§P)
- `docs/opendea-conceptual-architecture.md` — the authoritative CR-1→CR-10
  narrative: what OpenDEA is (semantic contract, not an EA tool), the layer
  model (§B), reference-implementation-vs-specification (§N), core-vs-profiles
  (§I), normative-vs-informative (§J), the semantic stack (§P), roadmap (§O).
- `docs/concepts/` — four-state model (§C), truth model (§D), semantic
  lifecycle (§E), digital-twin positioning (§H + CR-10AA/AB), scenario.
- `docs/opendea-and-dmm.md` (§F + terrain semantics CR-10AN–AQ) and
  `docs/opendea-and-agents.md` (§G).
- `docs/adr/` — ADR-001…ADR-012 recording settled architectural decisions (§K).
- `docs/glossary.md` (§L) and `docs/conformance-model.md` (§M).
- `docs/README.md` — documentation index with the normative/informative
  convention.
- `change-requests/CR-010.md` — the CR as authored; roadmap rows CR-011…CR-013
  added per CR-10 §O.

## [Unreleased] — CR-9.1: Runtime Foundation

First milestone of CR-9 (Runtime, Knowledge Graph & Interoperability). Additive
tooling only — the specification and metamodel remain **1.0.0** (the CR-8
semantic contract stays authoritative; the runtime provides interchangeable
implementations, CR-9 §101).

### Added
- **`runtime/` — reference OpenDEA runtime** (CR-9BV: demonstrates the semantics;
  not the only valid implementation):
  - `runtime/graph/base.py` — canonical graph model (CR-9E: first-class edges
    with provenance/temporal/status/properties) + `GraphStore`, the
    vendor-independent graph interface (CR-9D). `infer()` raises
    `InferenceUnavailable` — no silent inference (CR-9CQ).
  - `runtime/graph/memory.py` — `InMemoryGraphStore` reference implementation:
    defensive reads, referential integrity, copy-on-write transactions with
    rollback (CR-9BP), temporal traversal (`at=` — "what is true now?", CR-9F;
    planned edges never read as current, CR-6 §22).
  - `runtime/model/loader.py` — canonical model loader: CR-8 reference
    validator (levels 0–3) runs before any mutation; loads are atomic; envelope
    provenance/source/temporal fields preserved verbatim (CR-9K, CR-9 DoD).
  - `runtime/api/service.py` — `RuntimeService`: entity/relationship CRUD with
    registry-backed write validation (types, abstract types, endpoint
    compatibility via the TTL type hierarchy). No agent write path — no
    autonomous mutation by default (CR-9CR).
- **`tests/runtime/`** — 49-test runtime suite (CR-9CO): vendor-independent
  GraphStore contract (CR-9CL seed — conform future Neo4j/Neptune/RDF stores by
  subclassing), golden/negative loader contract, CRUD semantics,
  provenance/temporal retention, transaction rollback, no-silent-inference.
- **`docs/runtime-architecture.md`** — CR-9 KB note: closed-loop intent, layered
  runtime, model-vs-state-vs-assertion-vs-evidence-vs-inference, integration/
  reasoning/agentic principles, trust & freshness commitments, milestone plan
  and DoD tracking.
- **`change-requests/CR-009.md`** — the CR as authored; stale CR-009/CR-010
  placeholder rows in `change-requests/README.md` corrected (drift fix).

## [1.0.0] — 2026-08-17 — CR-008: OpenDEA Semantic Architecture & Conformance Specification

**OpenDEA 1.0.** Consolidation of CR-1…CR-7 into a formal, machine-validatable,
profile-driven semantic specification (CR-8 §63 phases 8.1–8.10).

### Added
- **`specification/`** — the formal specification corpus: 22-section
  `OpenDEA-Semantic-Architecture-Specification.md` (§52), `core-freeze.yaml` (§3-§4,
  18 anchors frozen + §3 candidate evaluation + anti-inflation rule), `naming-conventions.md`
  (§6-§7 incl. reconciled divergences), `type-system.md` (§8-§9/§14-§15),
  `relationship-semantics.md` (§10-§14), `profile-mechanism.md` (§16-§17/§53-§55),
  `conformance-spec.md` (levels 0–5, invariants, error taxonomy, open/closed world,
  assertion provenance), `serialization-versioning.md` (§18-§22).
- **Generated artifacts** (`.github/scripts/generate_specification.py`): semantic inventory
  + reconciliation (§63 8.1/8.2), canonical vocabulary (§5), concept/relationship
  catalogues (§49) — documentation is a generated artifact, never a parallel truth (§50).
- **Reference validator** `tools/opendea_validate.py` (§35): levels 0–3 + governance
  checks, registry-driven, DEA-E/W error taxonomy (§29), structured report (§28),
  `--normalize` canonicalizer (§36).
- **Model envelope schema** `schemas/model-envelope.json` (§23-§24) with context,
  assertion provenance (§40-§41) and source-of-record linkage (§42-§43).
- **Golden + negative model suites** `models/` (§30-§33): 7 golden (incl. all six §31
  scenarios) MUST pass; 8 negative MUST fail for the expected rule — the specification
  as a testable contract.
- **Visualization profile** `visualization/profile/` (§47-§48): the viewer consumes
  presentation hints; dependency direction is specification → … → viewer, never reversed (§67).
- **ArchiMate mapping** `mappings/archimate/` (§45) with documented divergences; DMN
  evaluation (§46); RDF/OWL adopted as derived serialization.
- **test_014** — 13 specification conformance tests (suite now 125).

### Changed
- Version **1.0.0** across all artifacts. Relationship `constrained-by` sources widened
  to Orchestrator/Controller (found by the reference validator during golden-model
  validation — the tool working as intended).

### Deferred
- SHACL-style graph validation (§26) and JSON-LD context (§21) — roadmap.
- DMN/BPMN profiles (§46) — extension candidates.
- Reference API (§62) — semantic contract defined; runtime services are CR-9 scope.

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
