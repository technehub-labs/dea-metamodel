"""CR-AM-04 result operations and maturity interpretation conformance tests."""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from runtime.result_operations import (
    AssessmentResultOperations,
    AggregationMethod,
    MaturityInterpretationError,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
ASSESSMENT_ROOT = REPO_ROOT / "assessment-models"
DOMAINS = ("technology", "modernization", "operations", "services-delivery")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


class TestResultOperations(unittest.TestCase):
    def test_canonical_execution_produces_conformant_result(self) -> None:
        result = AssessmentResultOperations.from_files(
            ASSESSMENT_ROOT / "migrations" / "technology" / "canonical-assessment-model.yaml",
            ASSESSMENT_ROOT / "migrations" / "technology" / "legacy-instrument.yaml",
            ASSESSMENT_ROOT / "migrations" / "technology" / "conformance-report.yaml",
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["assessment_model"]["id"], "dea:assessment-technology")
        self.assertEqual(result["lineage"]["assessment_execution"]["id"], "dea:execution-technology-001")
        self.assertEqual(result["lineage"]["aggregation_model"]["id"], "dea:aggregation-maturity-dominant-level")
        self.assertEqual(result["benchmark_eligibility"]["status"], "eligible")

    def test_result_preserves_complete_versioned_lineage(self) -> None:
        result = AssessmentResultOperations.from_domain("technology")
        required = {
            "assessment_model",
            "assessment_instrument",
            "assessment_execution",
            "capability",
            "scenario",
            "measures",
            "scoring_model",
            "maturity_model",
            "aggregation_model",
        }
        self.assertTrue(required <= set(result["lineage"]))
        for key in required - {"measures"}:
            self.assertEqual(set(result["lineage"][key]), {"id", "version"})
        for ref in result["lineage"]["measures"]:
            self.assertEqual(set(ref), {"id", "version"})

    def test_observation_is_distinguishable_from_score(self) -> None:
        result = AssessmentResultOperations.from_domain("operations")
        self.assertTrue(result["observations"])
        self.assertTrue(result["scores"])
        self.assertNotEqual(result["observations"][0]["id"], result["scores"][0].get("observation_id"))

    def test_score_is_distinguishable_from_maturity_level(self) -> None:
        result = AssessmentResultOperations.from_domain("modernization")
        self.assertIn("determinations", result)
        self.assertNotIn("maturity", result)
        self.assertNotEqual(result["determinations"][0]["score"]["value"], result["determinations"][0]["score"]["normalized_value"])
        self.assertIn("maturity_level", result["determinations"][0])

    def test_maturity_interpretation_references_explicit_model(self) -> None:
        result = AssessmentResultOperations.from_domain("technology")
        determination = result["determinations"][0]
        self.assertEqual(set(determination["maturity_model"]), {"id", "version"})
        self.assertIn("maturity_level", determination)

    def test_multidimensional_maturity_is_supported(self) -> None:
        result = AssessmentResultOperations.from_domain("operations")
        maturity = result["maturity_interpretation"]
        self.assertGreaterEqual(len(maturity["dimensions"]), 2)
        self.assertEqual(maturity["overall"]["method"], "dominant-level")

    def test_overall_aggregation_is_explicit(self) -> None:
        result = AssessmentResultOperations.from_domain("services-delivery")
        aggregation = result["lineage"]["aggregation_model"]
        self.assertEqual(aggregation["id"], "dea:aggregation-maturity-dominant-level")
        self.assertEqual(aggregation["version"], "1.0.0")
        self.assertEqual(result["maturity_interpretation"]["overall"]["method"], "dominant-level")

    def test_evidence_is_traceable_to_conclusions(self) -> None:
        result = AssessmentResultOperations.from_domain("technology")
        self.assertTrue(result["evidence"])
        self.assertEqual(set(result["evidence"][0]), {"id", "version", "description", "confidence"})
        self.assertEqual(result["evidence"][0]["version"], "1.0.0")

    def test_reproducibility_uses_fixed_response_vector(self) -> None:
        first = AssessmentResultOperations.from_domain("technology")
        second = AssessmentResultOperations.from_domain("technology")
        self.assertEqual(first, second)
        first = AssessmentResultOperations.from_domain("technology")
        first["source_responses"][0]["value"] = 0
        self.assertNotEqual(first, second)

    def test_existing_migrated_assessments_generate_results(self) -> None:
        for domain in DOMAINS:
            with self.subTest(domain=domain):
                result = AssessmentResultOperations.from_domain(domain)
                self.assertEqual(result["status"], "completed")
                self.assertIn("determinations", result)
                self.assertIn("maturity_interpretation", result)

    def test_views_are_derived_without_new_assessment_model(self) -> None:
        result = AssessmentResultOperations.from_domain("operations")
        views = AssessmentResultOperations.views_for(result)
        self.assertEqual(set(views), {"enterprise", "capability", "scenario"})
        self.assertEqual(views["enterprise"]["result_id"], result["id"])
        self.assertEqual(views["capability"]["capability_id"], "dea:capability-incident-response-capability")
        self.assertEqual(views["scenario"]["scenario_id"], "dea:scenario-service-assurance-operations")

    def test_no_benchmark_calculation_is_introduced(self) -> None:
        result = AssessmentResultOperations.from_domain("services-delivery")
        self.assertNotIn("percentile", result)
        self.assertNotIn("rank", result)
        self.assertEqual(result["benchmark_eligibility"]["status"], "eligible")

    def test_aggregation_method_does_not_implicitly_average(self) -> None:
        values = [{"level": 4}, {"level": 3}, {"level": 3}, {"level": 2}]
        self.assertEqual(AssessmentResultOperations.aggregate_levels(values, AggregationMethod.DOMINANT_LEVEL), 3)
        with self.assertRaises(MaturityInterpretationError):
            AssessmentResultOperations.aggregate_levels(values, AggregationMethod.UNKNOWN)
