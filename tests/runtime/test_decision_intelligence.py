"""CR-10 Phase 3 — decision intelligence tests (CR-10F/J/M/N/AI/AL)."""

import pytest

from runtime.scenario.decision import (Criterion, CriterionScore,
                                       DecisionError,
                                       DecisionIntelligenceEngine, Metric,
                                       ScenarioEvaluation)


def test_metric_is_reusable_semantic_object():
    """CR-10J: metrics are reusable, explicit objects — not embedded code."""
    metric = Metric(
        id="metric.customer-wait-time",
        definition="Average customer wait time",
        unit="minutes",
        calculation="mean(wait_time)",
        source="crm-analytics",
        baseline=8,
        target=5,
    )

    assert metric.as_dict()["unit"] == "minutes"
    assert metric.as_dict()["baseline"] == 8
    assert metric.as_dict()["target"] == 5


def test_criterion_weights_are_explicit_and_required():
    """CR-10M: weights are visible decision inputs, never hidden in algorithms."""
    criterion = Criterion(id="strategicValue", name="Strategic Value", weight=0.25)
    assert criterion.weight == 0.25

    with pytest.raises(DecisionError, match="weight"):
        Criterion(id="bad", name="Bad", weight=0)


def _criteria():
    return [
        Criterion(id="strategicValue", name="Strategic Value", weight=0.25),
        Criterion(id="capabilityImpact", name="Capability Impact", weight=0.35),
        Criterion(id="cost", name="Cost", weight=0.20),
        Criterion(id="risk", name="Risk", weight=0.20),
    ]


def test_scenario_score_is_decomposable():
    """CR-10N: total score exposes every weighted component."""
    evaluation = ScenarioEvaluation(
        scenario_id="scenario.a",
        scores=[
            CriterionScore("strategicValue", 0.8, evidence=["strategy-map"]),
            CriterionScore("capabilityImpact", 0.7, evidence=["impact-report"]),
            CriterionScore("cost", 0.9, assumptions=["budget ≤ $20M"]),
            CriterionScore("risk", 0.85, evidence=["risk-model"]),
        ])

    report = DecisionIntelligenceEngine().compare([evaluation], _criteria())
    score = report.scores[0]

    assert score.total == pytest.approx(0.795)
    assert [c.criterion_id for c in score.components] == [
        "strategicValue", "capabilityImpact", "cost", "risk"]
    assert score.components[1].weight == pytest.approx(0.35)
    assert score.components[1].weighted_value == pytest.approx(0.245)


def test_comparison_ranks_scenarios_and_recommendation_is_not_decision():
    """CR-10F/L/AI/AL: ranked alternatives + explainable recommendation."""
    evaluation_a = ScenarioEvaluation(
        scenario_id="scenario.a",
        scores=[
            CriterionScore("strategicValue", 0.8, evidence=["strategy-map"]),
            CriterionScore("capabilityImpact", 0.7, evidence=["impact-report"]),
            CriterionScore("cost", 0.9, assumptions=["budget ≤ $20M"]),
            CriterionScore("risk", 0.85, evidence=["risk-model"]),
        ])
    evaluation_b = ScenarioEvaluation(
        scenario_id="scenario.b",
        scores=[
            CriterionScore("strategicValue", 0.6),
            CriterionScore("capabilityImpact", 0.8),
            CriterionScore("cost", 0.5),
            CriterionScore("risk", 0.7),
        ])

    report = DecisionIntelligenceEngine().compare(
        [evaluation_b, evaluation_a], _criteria())

    assert [s.scenario_id for s in report.scores] == ["scenario.a", "scenario.b"]
    assert [s.rank for s in report.scores] == [1, 2]
    recommendation = report.recommendation
    assert recommendation.scenario_id == "scenario.a"
    assert recommendation.approved_decision is False
    assert recommendation.as_dict()["status"] == "recommendation"
    assert "strategy-map" in recommendation.evidence
    assert "budget ≤ $20M" in recommendation.assumptions
    assert any("capabilityImpact" in step for step in recommendation.rationale)


def test_missing_criterion_score_is_rejected():
    evaluation = ScenarioEvaluation(
        scenario_id="scenario.incomplete",
        scores=[CriterionScore("strategicValue", 0.8)])

    with pytest.raises(DecisionError, match="no score"):
        DecisionIntelligenceEngine().compare([evaluation], _criteria())


def test_decision_intelligence_symbols_are_exported():
    from runtime.scenario import DecisionIntelligenceEngine as ExportedEngine
    from runtime.scenario import Metric as ExportedMetric
    assert ExportedEngine is DecisionIntelligenceEngine
    assert ExportedMetric is Metric
