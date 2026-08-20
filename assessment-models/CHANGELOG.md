# Changelog — assessment-models/

All notable changes to the `assessment-models/` sub-tree of `technehub-labs/dea-metamodel` are recorded here. The sub-tree follows [Semantic Versioning](https://semver.org/) with [explicit compatibility metadata](../governance/compatibility.md).

## [Unreleased] — CR-014 landing

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