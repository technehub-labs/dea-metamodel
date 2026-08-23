"""CR-AM-06 benchmark model & eligibility conformance tests.

One test per acceptance criterion (CR-AM-06 §14), plus the §15
architectural principle guard. Positive and negative eligibility tests
are both present (AC-AM06-13).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

import sys

sys.path.insert(0, str(REPO_ROOT))

from runtime.eligibility import (  # noqa: E402
    BENCHMARK_STATUSES,
    ELIGIBILITY_DIMENSIONS,
    ELIGIBILITY_REASONS,
    REASON_STATUS,
    BenchmarkEligibilityEngine,
    CohortRegistry,
    CompatibilityDeclaration,
    EligibilityStatus,
)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def _preserve_timestamp_strings(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> str:
    """Keep ISO timestamps as raw strings (schema declares date-time strings)."""
    return loader.construct_scalar(node)


def base_result() -> dict:
    """A well-formed AssessmentResult eligible for the reference cohort."""
    return {
        "id": "dea:result-org-a-service-assurance-2026",
        "version": "1.0.0",
        "assessment_model": {"id": "cla-assessment-v1", "version": "1.0.0"},
        "assessment_instrument": {"id": "cla-instrument-v1", "version": "1.0.0"},
        "assessment_execution": {"id": "cla-exec-a-2026", "version": "1.0.0"},
        "subject": {"id": "dea:org-a", "type": "organization"},
        "assessment_period": {
            "start": "2026-01-15T00:00:00Z",
            "end": "2026-03-15T00:00:00Z",
        },
        "status": "completed",
        "confidence": "high",
        "compatibility": {
            "schema": "compatible",
            "semantic": "compatible",
            "scoring": "compatible",
            "maturity": "compatible",
            "result": "compatible",
            "benchmark": "compatible",
        },
        "observations": [
            {
                "id": "dea:obs-a-1",
                "measure": {"id": "automation-coverage", "version": "1.0.0"},
                "value": 82,
            }
        ],
        "evidence": [
            {"id": "dea:evidence-a-1", "version": "1.0.0", "description": "telemetry", "confidence": "high"}
        ],
        "lineage": {
            "assessment_model": {"id": "cla-assessment-v1", "version": "1.0.0"},
            "assessment_instrument": {"id": "cla-instrument-v1", "version": "1.0.0"},
            "assessment_execution": {"id": "cla-exec-a-2026", "version": "1.0.0"},
            "capability": {"id": "closed-loop-automation", "version": "1.0.0"},
            "scenario": {"id": "service-assurance", "version": "1.0.0"},
            "measures": [{"id": "automation-coverage", "version": "1.0.0"}],
            "scoring_model": {"id": "cla-score-v1", "version": "1.0.0"},
            "maturity_model": {"id": "cla-maturity-v1", "version": "1.0.0"},
        },
    }


def reference_cohort() -> dict:
    """The §6 worked cohort: Telecom Operators + Service Assurance + CLA + Automation Coverage + CLA-Maturity v1 + 2026."""
    return {
        "id": "telecom-service-assurance-2026",
        "version": "1.0.0",
        "name": "Telecom Service Assurance 2026",
        "status": "stable",
        "definition": {"population_segment": "telecom-operators"},
        "eligibility_criteria": {
            "minimum_confidence": "medium",
            "minimum_evidence_records": 1,
            "minimum_coverage": 1.0,
            "required_compatibility": {"benchmark": "compatible"},
        },
        "comparability_key": {
            "scenario": {"id": "service-assurance", "version": "1.0.0"},
            "capability": {"id": "closed-loop-automation", "version": "1.0.0"},
            "measure": {"id": "automation-coverage", "version": "1.0.0"},
            "assessment_model": {"id": "cla-assessment-v1", "version": "1.0.0"},
            "scoring_model": {"id": "cla-score-v1", "version": "1.0.0"},
            "maturity_model": {"id": "cla-maturity-v1", "version": "1.0.0"},
        },
        "minimum_sample_size": 2,
        "temporal_boundary": {
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-12-31T23:59:59Z",
        },
        "governance": {"owner": "dea-benchmark-board"},
    }


class TestCRAM06(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = BenchmarkEligibilityEngine()
        cls.cohort = reference_cohort()

    # AC-AM06-01 — AssessmentResult has normative benchmark eligibility semantics
    def test_ac_am06_01_normative_benchmark_semantics(self) -> None:
        schema = load_json("assessment-models/schemas/assessment-result.schema.json")
        bench = schema["$defs"]["benchmarkResult"]
        self.assertIn("CR-AM-06", bench["description"])
        self.assertIn("never inferred", bench["description"])
        self.assertIn("status", bench["required"])
        self.assertIn("model", bench["required"])

    # AC-AM06-02 — Eligibility status is controlled vocabulary
    def test_ac_am06_02_status_controlled_vocabulary(self) -> None:
        vocab = load_yaml("assessment-models/vocabulary/benchmark-status.yaml")
        vocab_ids = {v["id"] for v in vocab["values"]}
        self.assertEqual(vocab_ids, set(BENCHMARK_STATUSES))
        schema = load_json("assessment-models/schemas/assessment-result.schema.json")
        schema_enum = set(schema["$defs"]["benchmarkResult"]["properties"]["status"]["enum"])
        self.assertEqual(schema_enum, vocab_ids)
        self.assertEqual(len(vocab_ids), 6)

    # AC-AM06-03 — Comparability is explicitly represented
    def test_ac_am06_03_comparability_key_explicit(self) -> None:
        common = load_json("assessment-models/schemas/common.schema.json")
        key_def = common["$defs"]["comparabilityKey"]
        self.assertEqual(
            set(key_def["required"]),
            {"scenario", "capability", "measure", "assessment_model", "scoring_model", "maturity_model"},
        )
        result = base_result()
        determination = self.engine.evaluate(result, self.cohort)
        self.assertEqual(determination.comparability_key.scenario, "service-assurance")
        self.assertEqual(determination.comparability_key.maturity_model, "cla-maturity-v1")

    # AC-AM06-04 — Scenario/capability/measure compatibility is validated
    def test_ac_am06_04_semantic_dimension_mismatches(self) -> None:
        # §2 example: same labels, different scenario -> not comparable.
        result = base_result()
        result["lineage"]["scenario"] = {"id": "network-operations", "version": "1.0.0"}
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-comparable")
        self.assertIn("scenario-definition-mismatch", det.reasons)

        result = base_result()
        result["lineage"]["capability"] = {"id": "other-capability", "version": "1.0.0"}
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-comparable")
        self.assertIn("capability-mismatch", det.reasons)

        result = base_result()
        result["lineage"]["measures"] = [{"id": "other-measure", "version": "1.0.0"}]
        # Keep coverage intact so only the measure-key dimension fails.
        result["observations"][0]["measure"] = {"id": "other-measure", "version": "1.0.0"}
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-comparable")
        self.assertIn("measure-mismatch", det.reasons)

    # AC-AM06-05 — Assessment/scoring/maturity model compatibility is validated
    def test_ac_am06_05_model_version_compatibility(self) -> None:
        # §2 example: AOMM v1 result vs AOMM v2 cohort must not compare.
        result = base_result()
        result["lineage"]["maturity_model"] = {"id": "cla-maturity-v1", "version": "2.0.0"}
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-comparable")
        self.assertIn("maturity-model-incompatible", det.reasons)

        # Same model ids, same majors -> eligible.
        det = self.engine.evaluate(base_result(), self.cohort)
        self.assertEqual(det.status, "eligible")

        # §9: explicit mapping can bridge a version difference.
        engine = BenchmarkEligibilityEngine(
            compatibility_declarations=[
                CompatibilityDeclaration(
                    model_id="cla-maturity-v1",
                    from_version="2.0.0",
                    to_version="1.0.0",
                    benchmark="compatible",
                    basis="explicit-mapping",
                )
            ]
        )
        result = base_result()
        result["lineage"]["maturity_model"] = {"id": "cla-maturity-v1", "version": "2.0.0"}
        det = engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "eligible")

        # Explicit declaration of incompatibility is honoured even within same major.
        engine = BenchmarkEligibilityEngine(
            compatibility_declarations=[
                CompatibilityDeclaration(
                    model_id="cla-score-v1",
                    from_version="1.1.0",
                    to_version="1.0.0",
                    benchmark="incompatible",
                    basis="explicit-mapping",
                )
            ]
        )
        result = base_result()
        result["lineage"]["scoring_model"] = {"id": "cla-score-v1", "version": "1.1.0"}
        det = engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-comparable")
        self.assertIn("scoring-model-incompatible", det.reasons)

    # AC-AM06-06 — Evidence, coverage and confidence can influence eligibility
    def test_ac_am06_06_evidence_coverage_confidence(self) -> None:
        result = base_result()
        result["evidence"] = []
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "insufficient-data")
        self.assertIn("evidence-insufficient", det.reasons)
        self.assertFalse(det.eligibility["evidence"])

        result = base_result()
        result["lineage"]["measures"] = [
            {"id": "automation-coverage", "version": "1.0.0"},
            {"id": "unobserved-measure", "version": "1.0.0"},
        ]
        # Cohort requires measure id automation-coverage; add a cohort that
        # only keys on automation-coverage so the key matches but coverage
        # drops to 0.5.
        det = self.engine.evaluate(result, self.cohort)
        self.assertIn("coverage-insufficient", det.reasons)
        self.assertFalse(det.eligibility["coverage"])

        result = base_result()
        result["confidence"] = "low"
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-eligible")
        self.assertIn("confidence-below-threshold", det.reasons)
        self.assertFalse(det.eligibility["confidence"])

    # AC-AM06-07 — Benchmark cohorts have explicit definitions
    def test_ac_am06_07_cohort_schema_and_definition(self) -> None:
        from jsonschema import Draft202012Validator, RefResolver

        schema = load_json("assessment-models/schemas/benchmark-cohort.schema.json")
        Draft202012Validator.check_schema(schema)
        for field in (
            "definition",
            "eligibility_criteria",
            "comparability_key",
            "minimum_sample_size",
            "temporal_boundary",
            "governance",
        ):
            self.assertIn(field, schema["required"])

        common = load_json("assessment-models/schemas/common.schema.json")
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        import glob

        for path in sorted(glob.glob(str(REPO_ROOT / "assessment-models/benchmark/cohort-examples/*.yaml"))):
            doc = yaml.safe_load(Path(path).read_text())
            resolver = RefResolver(base_uri="", referrer=schema, store=store)
            validator = Draft202012Validator(schema, resolver=resolver)
            errs = list(validator.iter_errors(doc))
            self.assertEqual(errs, [], f"{path}: {[e.message for e in errs]}")

    # AC-AM06-08 — Historical results retain their original eligibility determination
    def test_ac_am06_08_deterministic_determination(self) -> None:
        result = base_result()
        first = self.engine.evaluate(result, self.cohort)
        second = self.engine.evaluate(result, self.cohort)
        self.assertEqual(first, second)
        # Determinism extends to the rendered benchmark entry.
        model_ref = {"id": "dea:benchmark-cla", "version": "1.0.0"}
        self.assertEqual(
            first.as_benchmark_entry(model_ref), second.as_benchmark_entry(model_ref)
        )

    # AC-AM06-09 — Eligibility does not calculate rankings (§10)
    def test_ac_am06_09_no_ranking_fields(self) -> None:
        det = self.engine.evaluate(base_result(), self.cohort)
        entry = det.as_benchmark_entry({"id": "dea:benchmark-cla", "version": "1.0.0"})
        for forbidden in ("percentile", "rank", "sample_size", "quartile", "peer_position"):
            self.assertNotIn(forbidden, entry)
        # The dataclass itself carries no ranking surface.
        self.assertFalse(hasattr(det, "percentile"))
        self.assertFalse(hasattr(det, "rank"))

    # AC-AM06-10 — Ineligible results cannot silently enter a benchmark cohort
    def test_ac_am06_10_no_silent_cohort_entry(self) -> None:
        registry = CohortRegistry(self.engine)
        registry.register_cohort(self.cohort)

        good = base_result()
        det = registry.admit(good, "telecom-service-assurance-2026")
        self.assertEqual(det.status, "eligible")
        self.assertEqual(len(registry.population("telecom-service-assurance-2026")), 1)

        bad = base_result()
        bad["id"] = "dea:result-org-b-2026"
        bad["confidence"] = "low"
        det = registry.admit(bad, "telecom-service-assurance-2026")
        self.assertEqual(det.status, "not-eligible")
        # Population is unchanged: no silent entry.
        self.assertEqual(len(registry.population("telecom-service-assurance-2026")), 1)
        self.assertEqual(
            registry.population("telecom-service-assurance-2026")[0]["id"],
            "dea:result-org-a-service-assurance-2026",
        )
        # Cohort below minimum sample size produces no benchmark (§6).
        self.assertFalse(registry.meets_minimum_sample("telecom-service-assurance-2026"))

    # AC-AM06-11 — Existing enterprise heatmaps remain unaffected
    def test_ac_am06_11_enterprise_views_unaffected(self) -> None:
        from jsonschema import Draft202012Validator, RefResolver

        yaml.SafeLoader.add_constructor(
            "tag:yaml.org,2002:timestamp",
            _preserve_timestamp_strings,
        )
        common = load_json("assessment-models/schemas/common.schema.json")
        view_schema = load_json("assessment-models/schemas/assessment-view.schema.json")
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        for path in [
            "assessment-models/views/enterprise/technology-heatmap.yaml",
            "assessment-models/views/capability/technology-architecture-profile.yaml",
            "assessment-models/views/scenario/service-assurance-profile.yaml",
            "assessment-models/views/trend/technology-maturity-trend.yaml",
        ]:
            doc = load_yaml(path)
            resolver = RefResolver(base_uri="", referrer=view_schema, store=store)
            validator = Draft202012Validator(view_schema, resolver=resolver)
            errs = list(validator.iter_errors(doc))
            self.assertEqual(errs, [], f"{path}: {[e.message for e in errs]}")

    # AC-AM06-12 — Existing assessment results remain schema-compatible
    def test_ac_am06_12_existing_results_schema_compatible(self) -> None:
        from jsonschema import Draft202012Validator, RefResolver

        # Result examples quote their timestamps; plain safe_load preserves
        # them as strings, so no SafeLoader override is required here.
        common = load_json("assessment-models/schemas/common.schema.json")
        result_schema = load_json("assessment-models/schemas/assessment-result.schema.json")
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        for path in [
            "assessment-models/examples/zero-touch-operations-result.yaml",
            "assessment-models/examples/technology-result-am04.yaml",
            "assessment-models/examples/modernization-result-am04.yaml",
            "assessment-models/examples/operations-result-am04.yaml",
            "assessment-models/examples/services-delivery-result-am04.yaml",
        ]:
            doc = load_yaml(path)
            resolver = RefResolver(base_uri="", referrer=result_schema, store=store)
            validator = Draft202012Validator(result_schema, resolver=resolver)
            errs = list(validator.iter_errors(doc))
            self.assertEqual(errs, [], f"{path}: {[e.message for e in errs][:3]}")

    # AC-AM06-13 — Positive and negative eligibility tests exist
    def test_ac_am06_13_positive_and_negative_paths(self) -> None:
        positive = self.engine.evaluate(base_result(), self.cohort)
        self.assertEqual(positive.status, "eligible")
        self.assertEqual(positive.reasons, ())

        negative = base_result()
        negative["confidence"] = "low"
        negative["evidence"] = []
        det = self.engine.evaluate(negative, self.cohort)
        self.assertNotEqual(det.status, "eligible")
        self.assertGreaterEqual(len(det.reasons), 2)

    # AC-AM06-14 — §11 worked shapes: expired + provisional + status distinction
    def test_ac_am06_14_status_distinctions(self) -> None:
        # expired: period entirely before the cohort window.
        result = base_result()
        result["assessment_period"] = {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T23:59:59Z",
        }
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "expired")
        self.assertIn("result-expired", det.reasons)

        # expired via supersession.
        result = base_result()
        result["status"] = "superseded"
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "expired")

        # provisional: only under a condition declared by the cohort.
        cohort = reference_cohort()
        cohort["eligibility_criteria"]["conditions"] = [
            {"id": "cond-pilot-segment", "description": "Pilot-segment operators may participate provisionally."}
        ]
        det = self.engine.evaluate(
            base_result(), cohort, provisional_condition_id="cond-pilot-segment"
        )
        self.assertEqual(det.status, "provisional")

        # provisional under an undeclared condition is refused by construction.
        with self.assertRaises(Exception):
            self.engine.evaluate(
                base_result(), cohort, provisional_condition_id="cond-not-declared"
            )

        # §11 worked shape: not-comparable carries machine-actionable reasons.
        result = base_result()
        result["lineage"]["maturity_model"] = {"id": "cla-maturity-v1", "version": "2.0.0"}
        result["lineage"]["scenario"] = {"id": "network-operations", "version": "1.0.0"}
        det = self.engine.evaluate(result, self.cohort)
        self.assertEqual(det.status, "not-comparable")
        self.assertIn("maturity-model-incompatible", det.reasons)
        self.assertIn("scenario-definition-mismatch", det.reasons)

    # §15 architectural guard — eligibility is never inferred from a score
    def test_am06_15_no_inference_from_score(self) -> None:
        result = base_result()
        result["scores"] = [{"dimension": "automation", "value": 99.0, "normalized_value": 99.0, "scale": "0-100"}]
        result["maturity"] = [{"model": {"id": "cla-maturity-v1", "version": "1.0.0"}, "level": 5}]
        result["lineage"]["scenario"] = {"id": "network-operations", "version": "1.0.0"}
        det = self.engine.evaluate(result, self.cohort)
        # A perfect score under the wrong scenario is still not comparable.
        self.assertEqual(det.status, "not-comparable")

    # Vocabulary integrity — engine constants mirror the YAML vocabularies
    def test_am06_vocab_integrity(self) -> None:
        reasons_vocab = load_yaml("assessment-models/vocabulary/eligibility-reasons.yaml")
        vocab_ids = {v["id"] for v in reasons_vocab["values"]}
        self.assertEqual(vocab_ids, set(ELIGIBILITY_REASONS))
        # Every reason's `produces` mapping matches the engine's REASON_STATUS.
        for v in reasons_vocab["values"]:
            self.assertEqual(REASON_STATUS[v["id"]], v["produces"])
        # Twelve §8 dimensions are all represented.
        self.assertEqual(len(ELIGIBILITY_DIMENSIONS), 12)
        vocab_dims = {v["dimension"] for v in reasons_vocab["values"]}
        self.assertTrue(vocab_dims.issubset(set(ELIGIBILITY_DIMENSIONS) | {"currency"}))

    # Enum sanity — EligibilityStatus mirrors the schema/vocabulary set
    def test_am06_status_enum_complete(self) -> None:
        self.assertEqual({s.value for s in EligibilityStatus}, set(BENCHMARK_STATUSES))


if __name__ == "__main__":
    unittest.main()
