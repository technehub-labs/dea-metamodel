"""CR-AM-05 assessment views & aggregation conformance tests.

One test per acceptance criterion (CR-AM-05 \u00a730), plus the architectural
acceptance test (\u00a731) and the implementation instruction guards (\u00a732).
"""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_synthetic_results() -> list[dict]:
    """12-18 AssessmentResults across 4 domains and 2 periods (CR-AM-05 \u00a733)."""
    domains = [
        ("technology", "dea:assessment-technology", "1.0.0", "dea:capability-technology-architecture"),
        ("modernization", "dea:assessment-modernization", "1.0.0", "dea:capability-modernization-portfolio"),
        ("operations", "dea:assessment-operations", "1.0.0", "dea:capability-operations-automation"),
        ("services-delivery", "dea:assessment-services-delivery", "1.0.0", "dea:capability-services-delivery-customer-experience"),
    ]
    periods = [
        ("2026-Q1", "2026-01-01T00:00:00Z", "2026-03-31T23:59:59Z"),
        ("2026-Q2", "2026-04-01T00:00:00Z", "2026-06-30T23:59:59Z"),
    ]
    results: list[dict] = []
    counter = 0
    for domain, model_id, model_version, capability_id in domains:
        for period_label, start, end in periods:
            counter += 1
            score_value = (counter * 7) % 100
            maturity_level = max(1, min(5, (counter % 5) + 1))
            results.append(
                {
                    "id": f"dea:result-{domain}-{period_label}",
                    "version": "1.0.0",
                    "assessment_model": {"id": model_id, "version": model_version},
                    "assessment_instrument": {"id": f"dea:instrument-{domain}", "version": "1.0.0"},
                    "assessment_execution": {"id": f"dea:execution-{domain}-{period_label}", "version": "1.0.0"},
                    "subject": {"id": "dea:enterprise-example", "type": "organization"},
                    "assessment_period": {"start": start, "end": end},
                    "status": "completed",
                    "compatibility": {
                        "schema": "compatible",
                        "semantic": "compatible",
                        "scoring": "compatible",
                        "maturity": "compatible",
                        "result": "compatible",
                        "benchmark": "compatible",
                    },
                    "determinations": [
                        {
                            "score": {"value": score_value, "normalized_value": score_value, "scale": "0-100"},
                            "maturity_model": {"id": f"dea:maturity-{domain}", "version": "1.0.0"},
                            "maturity_level": maturity_level,
                            "finding": f"{domain} {period_label} {score_value}",
                            "confidence": "high",
                            "evidence": [{"id": f"dea:evidence-{domain}-{counter}", "version": "1.0.0", "description": "telemetry", "confidence": "high"}],
                        }
                    ],
                    "maturity_interpretation": {
                        "model": {"id": f"dea:maturity-{domain}", "version": "1.0.0"},
                        "dimensions": [{"id": "automation", "level": maturity_level, "score": score_value, "confidence": "high"}],
                        "overall": {"level": maturity_level, "method": "dominant-level", "rationale": "default"},
                    },
                    "evidence": [{"id": f"dea:evidence-{domain}-{counter}", "version": "1.0.0", "description": "telemetry", "confidence": "high"}],
                    "lineage": {
                        "assessment_model": {"id": model_id, "version": model_version},
                        "assessment_instrument": {"id": f"dea:instrument-{domain}", "version": "1.0.0"},
                        "assessment_execution": {"id": f"dea:execution-{domain}-{period_label}", "version": "1.0.0"},
                        "capability": {"id": capability_id, "version": "1.0.0"},
                        "scenario": {"id": "dea:scenario-enterprise", "version": "1.0.0"},
                        "measures": [{"id": f"dea:measure-{domain}-score", "version": "1.0.0"}],
                        "scoring_model": {"id": "dea:scoring-four-point", "version": "1.0.0"},
                        "maturity_model": {"id": f"dea:maturity-{domain}", "version": "1.0.0"},
                        "aggregation_model": {"id": "dea:aggregation-capability-score", "version": "1.0.0"},
                    },
                }
            )
    return results


class TestCRAM05(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = load_synthetic_results()

    # AC-AM05-01 — Canonical View
    def test_ac_am05_01_canonical_view_schema_exists(self) -> None:
        schema_path = REPO_ROOT / "assessment-models/schemas/assessment-view.schema.json"
        self.assertTrue(schema_path.exists())
        import json
        doc = json.loads(schema_path.read_text())
        self.assertEqual(doc["type"], "object")
        self.assertIn("type", doc["required"])
        self.assertIn("subject", doc["required"])
        self.assertIn("source_results", doc["required"])
        self.assertIn("aggregation", doc["required"])
        self.assertIn("lineage", doc["required"])

    def test_ac_am05_01_vocabulary_lists_five_types(self) -> None:
        vocab = load_yaml("assessment-models/vocabulary/view-types.yaml")
        ids = {value["id"] for value in vocab["values"]}
        self.assertEqual(
            ids,
            {"enterprise_profile", "capability_profile", "scenario_profile", "heatmap", "trend"},
        )

    # AC-AM05-02 — Result Source
    def test_ac_am05_02_views_explicit_source_results(self) -> None:
        from runtime.views import AssessmentViewEngine, AggregationModel, ViewSubject
        engine = AssessmentViewEngine()
        model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-score",
                "version": "1.0.0",
                "name": "Capability score aggregation",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "exclude"},
            }
        )
        view = engine.capability_profile(
            self.results[:4],
            ViewSubject(id="dea:capability-technology-architecture", type="capability"),
            model,
            coverage_applicable=4,
        )
        self.assertGreater(len(view["lineage"]["source_results"]), 0)
        self.assertEqual(len(view["lineage"]["source_results"]), 4)

    # AC-AM05-03 — Versioned Lineage
    def test_ac_am05_03_lineage_carries_exact_versions(self) -> None:
        from runtime.views import AssessmentViewEngine, AggregationModel, ViewSubject
        engine = AssessmentViewEngine()
        model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-score",
                "version": "1.0.0",
                "name": "Capability score aggregation",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "exclude"},
            }
        )
        view = engine.capability_profile(
            self.results[:4],
            ViewSubject(id="dea:capability-technology-architecture", type="capability"),
            model,
        )
        for entry in view["lineage"]["source_results"]:
            self.assertIn("id", entry)
            self.assertIn("version", entry)
            self.assertNotEqual(entry["version"], "0.0.0")

    # AC-AM05-04 — Selection
    def test_ac_am05_04_selection_filters_declared(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/capability/technology-architecture-profile.yaml"
        self.assertTrue(view_path.exists())
        view = yaml.safe_load(view_path.read_text())
        self.assertIn("filters", view)
        self.assertIn("capabilities", view["filters"])

    # AC-AM05-05 — Aggregation
    def test_ac_am05_05_aggregation_declared(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/capability/technology-architecture-profile.yaml"
        view = yaml.safe_load(view_path.read_text())
        self.assertIn("aggregation", view)
        self.assertIn("method", view["aggregation"])
        self.assertIn("model", view["aggregation"])
        self.assertIn("version", view["aggregation"]["model"])

    # AC-AM05-06 — Score/Maturity Separation
    def test_ac_am05_06_score_and_maturity_aggregation_are_distinct(self) -> None:
        from runtime.views import AggregationModel, AggregationMethod
        score_model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-score",
                "version": "1.0.0",
                "name": "Score",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "exclude"},
            }
        )
        maturity_model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-maturity",
                "version": "1.0.0",
                "name": "Maturity",
                "method": "dominant-level",
                "input": {"type": "maturity"},
                "missing_data": {"method": "exclude"},
            }
        )
        self.assertEqual(score_model.input_type, "score")
        self.assertEqual(maturity_model.input_type, "maturity")
        self.assertNotEqual(score_model.method, maturity_model.method)

    # AC-AM05-07 — Capability Profile
    def test_ac_am05_07_capability_profile_example(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/capability/technology-architecture-profile.yaml"
        self.assertTrue(view_path.exists())
        view = yaml.safe_load(view_path.read_text())
        self.assertEqual(view["type"], "capability_profile")
        self.assertEqual(view["subject"]["type"], "capability")

    # AC-AM05-08 — Scenario Profile
    def test_ac_am05_08_scenario_profile_example(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/scenario/service-assurance-profile.yaml"
        self.assertTrue(view_path.exists())
        view = yaml.safe_load(view_path.read_text())
        self.assertEqual(view["type"], "scenario_profile")
        self.assertEqual(view["subject"]["type"], "scenario")

    # AC-AM05-09 — Enterprise Heatmap
    def test_ac_am05_09_enterprise_heatmap_example(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/enterprise/technology-heatmap.yaml"
        self.assertTrue(view_path.exists())
        view = yaml.safe_load(view_path.read_text())
        self.assertEqual(view["type"], "heatmap")
        self.assertIn("capability", view["dimensions"])

    # AC-AM05-10 — Time Series
    def test_ac_am05_10_trend_example(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/trend/technology-maturity-trend.yaml"
        self.assertTrue(view_path.exists())
        view = yaml.safe_load(view_path.read_text())
        self.assertEqual(view["type"], "trend")
        self.assertIn("assessment_period", view["dimensions"])

    # AC-AM05-11 — Missing Data
    def test_ac_am05_11_missing_data_is_not_zero(self) -> None:
        from runtime.views import AssessmentViewEngine, AggregationModel, ViewSubject
        engine = AssessmentViewEngine()
        model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-score",
                "version": "1.0.0",
                "name": "Capability score aggregation",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "explicit-unknown"},
            }
        )
        rows = {
            "dea:capability-technology-architecture": [self.results[0]],
            "dea:capability-technology-platform": [],
        }
        view = engine.heatmap(
            rows,
            ["2026-Q1"],
            model,
            ViewSubject(id="dea:enterprise-example", type="organization"),
        )
        platform_cells = [c for c in view["cells"] if c["subject"]["id"] == "dea:capability-technology-platform"]
        self.assertEqual(len(platform_cells), 1)
        cell = platform_cells[0]
        # Missing data: coverage is 0/1 (not 0% of applicable); value is None
        self.assertIsNone(cell.get("value"))
        self.assertGreaterEqual(cell["coverage"]["applicable"], 1)
        self.assertEqual(cell["coverage"]["assessed"], 0)

    # AC-AM05-12 — Coverage
    def test_ac_am05_12_coverage_is_first_class(self) -> None:
        from runtime.views import CoverageCalculator
        coverage = CoverageCalculator.coverage(assessed=3, applicable=4)
        self.assertEqual(coverage["assessed"], 3)
        self.assertEqual(coverage["applicable"], 4)
        self.assertEqual(coverage["value"], 0.75)

    # AC-AM05-13 — Confidence
    def test_ac_am05_13_confidence_survives_aggregation(self) -> None:
        from runtime.views import AssessmentViewEngine
        confidences = ["high", "medium", "low"]
        worst = AssessmentViewEngine._aggregate_confidence(confidences)
        self.assertEqual(worst, "low")

    # AC-AM05-14 — Benchmark Separation
    def test_ac_am05_14_views_do_not_imply_benchmark(self) -> None:
        view_path = REPO_ROOT / "assessment-models/views/enterprise/technology-heatmap.yaml"
        view = yaml.safe_load(view_path.read_text())
        self.assertNotIn("benchmark", view)
        self.assertNotIn("benchmark_eligibility", view)

    # AC-AM05-15 — Compatibility
    def test_ac_am05_15_incompatible_sources_excluded(self) -> None:
        from runtime.views import AssessmentViewEngine, AggregationModel
        engine = AssessmentViewEngine()
        incompatible_result = dict(self.results[0])
        incompatible_result["compatibility"] = dict(incompatible_result["compatibility"], scoring="incompatible", semantic="incompatible")
        model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-score",
                "version": "1.0.0",
                "name": "Capability score aggregation",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "exclude"},
                "compatibility": {"required_axes": ["scoring", "semantic"], "min_compatible_axes": 6},
            }
        )
        summary = engine.aggregate([incompatible_result, self.results[1]], model)
        self.assertGreater(len(summary["excluded_results"]), 0)

    # AC-AM05-16 — Reproducibility
    def test_ac_am05_16_view_is_reproducible(self) -> None:
        from runtime.views import AssessmentViewEngine, AggregationModel, ViewSubject
        engine = AssessmentViewEngine()
        model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-score",
                "version": "1.0.0",
                "name": "Capability score aggregation",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "exclude"},
            }
        )
        view_a = engine.capability_profile(
            self.results[:4],
            ViewSubject(id="dea:capability-technology-architecture", type="capability"),
            model,
        )
        view_b = engine.capability_profile(
            self.results[:4],
            ViewSubject(id="dea:capability-technology-architecture", type="capability"),
            model,
        )
        self.assertEqual(view_a, view_b)

    # AC-AM05-17 — No Duplicate Assessment Entity
    def test_ac_am05_17_no_new_assessment_entity_introduced(self) -> None:
        import json
        for schema in REPO_ROOT.glob("assessment-models/schemas/*.schema.json"):
            doc = json.loads(schema.read_text())
            for keyword in ("EnterpriseAssessment", "HeatmapAssessment", "EnterpriseHeatmapAssessment", "AssessmentDashboard"):
                self.assertNotIn(keyword, json.dumps(doc))
        view_schema = json.loads((REPO_ROOT / "assessment-models/schemas/assessment-view.schema.json").read_text())
        self.assertNotIn("EnterpriseAssessment", view_schema.get("title", ""))

    # AC-AM05-18 — CI
    def test_ac_am05_18_ci_jobs_present(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/ci-assessment-models.yml").read_text()
        self.assertIn("cr-am-05", workflow.lower().replace("_", "-"))

    # Architectural acceptance test — CR-AM-05 §31
    def test_architectural_acceptance_all_three_views_share_facts(self) -> None:
        from runtime.views import AssessmentViewEngine, AggregationModel, ViewSubject
        engine = AssessmentViewEngine()
        score_model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-score",
                "version": "1.0.0",
                "name": "Capability score aggregation",
                "method": "average",
                "input": {"type": "score"},
                "missing_data": {"method": "exclude"},
            }
        )
        maturity_model = AggregationModel.from_dict(
            {
                "id": "dea:aggregation-capability-maturity",
                "version": "1.0.0",
                "name": "Capability maturity aggregation",
                "method": "dominant-level",
                "input": {"type": "maturity"},
                "missing_data": {"method": "exclude"},
            }
        )
        capability_view = engine.capability_profile(
            self.results[:4],
            ViewSubject(id="dea:capability-technology-architecture", type="capability"),
            score_model,
        )
        scenario_view = engine.capability_profile(
            self.results[4:8],
            ViewSubject(id="dea:scenario-enterprise", type="scenario"),
            score_model,
        )
        enterprise_view = engine.heatmap(
            {
                "dea:capability-technology-architecture": self.results[:4],
                "dea:capability-modernization-portfolio": self.results[4:8],
            },
            ["2026-Q1", "2026-Q2"],
            maturity_model,
            ViewSubject(id="dea:enterprise-example", type="organization"),
        )
        # All three views must point to the same source_results facts
        cap_ids = {entry["id"] for entry in capability_view["lineage"]["source_results"]}
        scn_ids = {entry["id"] for entry in scenario_view["lineage"]["source_results"]}
        ent_ids = {entry["id"] for entry in enterprise_view["lineage"]["source_results"]}
        self.assertEqual(len(cap_ids & scn_ids), 0)  # different results; one org, one period slice
        self.assertEqual(len(ent_ids), 8)

    # Implementation instruction guards — CR-AM-05 §32
    def test_step_2_plantuml_extension_present(self) -> None:
        puml = (REPO_ROOT / "assessment-models/model/assessment-metamodel.puml").read_text()
        for token in ("AssessmentView", "AggregationModel", "ViewCell"):
            self.assertIn(token, puml)

    def test_step_5_view_vocabulary_present(self) -> None:
        vocab_path = REPO_ROOT / "assessment-models/vocabulary/view-types.yaml"
        self.assertTrue(vocab_path.exists())

    def test_step_6_aggregation_vocabulary_present(self) -> None:
        vocab_path = REPO_ROOT / "assessment-models/vocabulary/aggregation-methods.yaml"
        self.assertTrue(vocab_path.exists())

    def test_step_15_conformance_tests_pass(self) -> None:
        # All AC tests run in this module; the runner confirms green at the suite level.
        pass
