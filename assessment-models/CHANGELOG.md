# Changelog — assessment-models/

All notable changes to the `assessment-models/` sub-tree of `technehub-labs/dea-metamodel` are recorded here. The sub-tree follows [Semantic Versioning](https://semver.org/) with [explicit compatibility metadata](../governance/compatibility.md).

## [Unreleased] — CR-AM-03 assessment catalog migration

CR-AM-03 migrates the Technology, Modernization, Operations, and Services Delivery legacy instruments into canonical AssessmentModel v1.0.0 projections, preserving source instruments byte-for-byte beside explicit mapping, manifest, and conformance contracts. The change also adds the four-domain assessment portfolio, reference catalogue, coverage matrix, completed AssessmentExecution examples, versioned AssessmentResult lineage, benchmark eligibility declarations, and CR-AM-03 schema/test coverage. Canonical schema `$id` values now use the `technehub-labs/dea-metamodel/assessment-models/schemas/` namespace.

## [CR-014 landing] — superseded by CR-AM-03 assessment catalog migration

### Added — Assessment sub-metamodel v1

The first landing of the assessment sub-metamodel inside the canonical repository. The supplementary CR (CR-AM-01-supplement-metamodel-v1.md) is byte-identical to the source attachment (md5 `c0f086be67791444995237ceb0c20765`).

#### model/

- `assessment-metamodel.puml` — canonical PlantUML class diagram (verbatim from supplement §2). Renders via PlantUML CLI or `https://www.plantuml.com/plantuml/uml/~1<encoded>`.

#### schemas/ (12 JSON Schemas, Draft 2020-12)

- `common.schema.json` — shared `$defs` (identifier, version, modelReference, assessmentPurpose, lifecycleStatus, changeType, lineage, compatibility). **Verbatim from supplement §5.**
- `assessment-model.schema.json` — central contract. **Verbatim from supplement §4.**
- `assessment-result.schema.json` — persistent output. **Verbatim from supplement §6.**
- `assessment-instrument.schema.json` — executable realisation of an AssessmentModel.
- `assessment-execution.schema.json` — specific instance of running an instrument.
- `capability.schema.json` — first-class reusable capability.
- `scenario.schema.json` — context for capability evaluation.
- `measure.schema.json` — observable characteristic with unit and rule.
- `evidence.schema.json` — provenance layer supporting observations.
- `scoring-model.schema.json` — pluggable aggregation/normalisation rules.
- `compatibility.schema.json` — explicit compatibility declaration.
- `relationship.schema.json` — controlled-vocabulary edge.

#### vocabulary/ (4 controlled vocabularies)

- `assessment-types.yaml` — 10 declared purposes (CR-AM-01 §49).
- `relationship-types.yaml` — 17 controlled relationship types + legacy aliases (CR-AM-01 §17, §41).
- `lifecycle-status.yaml` — 7 lifecycle states (CR-AM-01 §42, §43), including `retired`.
- `evidence-types.yaml` — open vocabulary of evidence classifications.

#### examples/ (5 canonical YAML examples)

- `legacy-technology-instrument.yaml` — current-style instrument with migration-layer interpretation.
- `canonical-technology-assessment.yaml` — the same assessment in canonical form.
- `zero-touch-operations-assessment.yaml` — scenario-based capability assessment, **no maturity model required**.
- `zero-touch-operations-result.yaml` — independently useful AssessmentResult.
- `benchmark-eligibility.yaml` — explicit benchmark eligibility declaration.

#### governance/ (3 policy docs)

- `versioning.md` — SemVer + explicit compatibility metadata.
- `compatibility.md` — five compatibility properties and benchmark eligibility rules.
- `lifecycle.md` — seven lifecycle states and the **retired ≠ deleted** rule.

### Added — Maturity scoring v2 (CR-014's other landing)

The maturity-scoring-v2 proposal (previously filed as `Assessment-Models/dea-catalog-maturity-models` PR #1, archived) is accepted as the canonical **v2** scoring scheme. Lands alongside v1; v1 stays canonical until Phase D promotion.

#### maturity/

- `README.md` — entry point for the v2 scheme.
- `maturity-bands-v2.yaml` — canonical v2 band definitions (Emergent / Structured / Systematic / Adaptive / Self-Optimising, non-linear bands 20/25/25/18/12, per-level `effort_multiplier` 1.0×/1.5×/2.5×/4.0×/6.0×).
- `v2-to-v1-legacy-name-map.yaml` — explicit alias table v2 ↔ v1. Every v2 level has exactly one `legacy_name`. v1 ids remain valid forever.
- `examples/effort-adjusted-value.yaml` — worked example: score 80 → 49.2 effort-adjusted value units (acceptance tolerance ±0.1).
- `governance/migration.md` — 4-phase migration plan (Phase A registry advisory, B beta files, C consumer support, D promotion).

### Status

| Component | Status |
|---|---|
| Assessment sub-metamodel (PlantUML + 12 schemas + governance) | v1.0.0 |
| Maturity scoring v2 | beta (advisory; promotion to stable at Phase D) |
| Maturity scoring v1 (lives in archived `Assessment-Models/dea-catalog-maturity-models`) | alpha (canonical until Phase D promotion) |

### Notes

- **No change to canonical `VERSION`** — this sub-tree is additive. The canonical repository's frozen v1.0.0 spec is unaffected.
- **No change to existing canonical files** outside `assessment-models/`, except an additive cross-link in `../../README.md` (and possibly a forward-pointer in `metamodel/profiles/assessment/profile.yaml`, deferred to a follow-on CR).
- **The PR #1 on the archived `Assessment-Models/dea-catalog-maturity-models` repo** remains open as historical reference. A comment pointing to this CR will be added there.
- **DMM-01 names-line** (Discrete / Converged / Composable / Cognitive / Autonomous) is parked — surfaces as input to a Capability Model in a future CR, not a maturity ladder.

### Migration status (per `maturity/governance/migration.md`)

- **Phase A — registry advisory:** ✅ complete (this PR)
- **Phase B — beta files:** pending (separate CR)
- **Phase C — consumer support:** pending (separate CRs in `technehub-labs/dea-cli`, `technehub-labs/dea-web-viewer`)
- **Phase D — promotion:** pending (requires one full assessment cycle on v2)

---

## [CR-AM-02] — Phase 1 implementation landed

CR-AM-02 implements the Phase-1 requirements of the accepted CR-AM-01
architecture. Repository state after this land:

- **Implementation** of 22 CR-AM-02 acceptance criteria.
- **Migration layer** that projects the legacy `instrument.schema.json`
  (vendored at `migrations/v1-instrument/legacy-instrument.schema.json`,
  byte-equal to the archived
  `Assessment-Models/dea-catalog-assessment-tools/schemas/instrument.schema.json`)
  into the canonical `AssessmentModel` shape.
- **First migration output** — the Technology Assessment — at
  `migrations/v1-instrument/canonical-technology-migration.yaml` + a
  sidecar `migration-manifest.yaml` carrying the legacy fields that have
  no canonical equivalent (CR-AM-02 §22 AC-15).
- **Compatibility vocabulary** at `vocabulary/compatibility-types.yaml`
  declaring the six-axis compatibility declaration (CR-AM-02 §11).
- **Tests** at `tests/{schemas,migration,compatibility}/` — 31 unit tests
  covering the schema set (AC-02), the migration integrity (AC-07/15/20),
  the compatibility states (AC-17), and the AC-08/09/10/11/12/13/14
  independence assertions.
- **CI** — `validate-cr-am-02-tests` and `validate-migration-integrity`
  jobs added to `.github/workflows/ci-assessment-models.yml`.

### Schema changes vs CR-014

- `compatibility.schema.json` — the compatibility declaration was
  redefined from a 5-axis shape (`backward_compatible`, `*_compatible`)
  to the canonical 6-axis shape (`schema`, `semantic`, `scoring`,
  `maturity`, `result`, `benchmark`) per CR-AM-02 §11. The string
  values are `compatible` / `incompatible` (verified by the existing
  examples which already use the 6-axis shape).
- `common.schema.json` `$defs.compatibility` — same 6-axis redefinition.
- `common.schema.json` `$defs.lineage` — was `previous_version +
  change_type + supersedes` (model-side lineage). Now uses `allOf` to
  compose model-side AND result-side (CR-AM-02 §12) — the result-side
  declares `assessment_model`, `assessment_instrument`, `capability`,
  `scenario`, `measures`, `scoring_model`, `maturity_model`.
- `assessment-result.schema.json` — `lineage` is now a required field
  (CR-AM-02 §22 AC-14).

### Compatibility export

The existing `examples/canonical-technology-assessment.yaml` and
`examples/zero-touch-operations-result.yaml` were updated to the 6-axis
compatibility + the required lineage block. They re-validate against
their respective schemas.

### Acceptance criteria mapping

- AC-01 Canonical Metamodel: `model/assessment-metamodel.puml` + `model/assessment-metamodel.md`
- AC-02 Normative Schemas: `schemas/*.schema.json` (12 files)
- AC-03 Controlled Vocabulary: `vocabulary/relationship-types.yaml` + `vocabulary/compatibility-types.yaml` + `vocabulary/lifecycle-status.yaml`
- AC-04 Versioning: `common.schema.json` `$defs.version` + `governance/versioning.md`
- AC-05 Legacy Preservation: `migrations/v1-instrument/legacy-instrument.schema.json` (vendor copy) + `migrations/v1-instrument/legacy-technology-instrument.yaml` validates against it
- AC-06 Canonical Representation: `migrations/v1-instrument/canonical-technology-migration.yaml` (validated against `assessment-model.schema.json`)
- AC-07 Technology Migration: `tests/migration/test_v1_to_metamodel.py` (15 tests)
- AC-08..11 Independence: `tests/schemas/test_assessment_schema_set.py` (capability, scenario, measure, scoring-model)
- AC-12 Maturity Independence: `maturity/v2-beta/*.yaml` (5 maturity models with explicit `version` field)
- AC-13 Execution Separation: `assessment-execution.schema.json` requires `assessment_model` reference
- AC-14 Result Lineage: `assessment-result.schema.json` requires `lineage`
- AC-15 Historical Integrity: `governance/lifecycle.md` retired-definition retention rule + `tests/migration/test_v1_to_metamodel.py` round-trip
- AC-16 Heatmap Traceability: `assessment-result.schema.json` carries `maturity`/`benchmark` array of modelReferences — every heatmap cell traces back to a result + model version
- AC-17 Compatibility: `vocabulary/compatibility-types.yaml` + `tests/compatibility/test_compatibility_states.py`
- AC-18 Benchmark Protection: `governance/compatibility.md` §6 + `examples/benchmark-eligibility.yaml`
- AC-19 Reproducibility: result lineage + ModelVersion + Compatibility declared
- AC-20 No Breaking Migration: `migrations/v1-instrument/mapping.yaml` is the explicit non-breaking migration contract
