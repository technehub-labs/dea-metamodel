"""CR-10 Phase 3 — decision intelligence.

Metrics, criteria, explicit weights, scenario comparison, ranking and
recommendation. A recommendation is decision support, never an approved
decision (CR-10AI); every score is decomposable and explainable (CR-10N/AL).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class DecisionError(Exception):
    """Decision-intelligence invariant violated."""


@dataclass(frozen=True)
class Metric:
    """CR-10J — reusable semantic metric object."""

    id: str
    definition: str
    unit: str
    calculation: str = ""
    source: str = ""
    baseline: Optional[Any] = None
    target: Optional[Any] = None

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in vars(self).items()
                if v not in (None, "")}


@dataclass(frozen=True)
class Criterion:
    """CR-10M — a weighted decision criterion."""

    id: str
    name: str
    weight: float
    description: str = ""

    def __post_init__(self):
        if self.weight <= 0:
            raise DecisionError("criterion weight must be greater than zero")

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in vars(self).items() if v != ""}


@dataclass(frozen=True)
class CriterionScore:
    """Normalized desirability score for one criterion (0..1, higher is better)."""

    criterion_id: str
    value: float
    evidence: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise DecisionError("criterion scores must be normalized between 0 and 1")


@dataclass(frozen=True)
class ScenarioEvaluation:
    """Criterion scores for one scenario alternative."""

    scenario_id: str
    scores: List[CriterionScore]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def score_for(self, criterion_id: str) -> CriterionScore:
        for score in self.scores:
            if score.criterion_id == criterion_id:
                return score
        raise DecisionError(
            f"scenario {self.scenario_id!r} has no score for criterion "
            f"{criterion_id!r}")


@dataclass(frozen=True)
class ScoreComponent:
    """CR-10N — one inspectable component of a scenario score."""

    criterion_id: str
    value: float
    weight: float
    weighted_value: float
    evidence: List[str]
    assumptions: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return vars(self).copy()


@dataclass(frozen=True)
class ScenarioScore:
    """CR-10N — decomposable total score."""

    scenario_id: str
    total: float
    components: List[ScoreComponent]
    rank: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario_id,
            "total": self.total,
            "rank": self.rank,
            "components": [c.as_dict() for c in self.components],
        }


@dataclass(frozen=True)
class Recommendation:
    """CR-10AI/AL — decision support, not an approved decision."""

    scenario_id: str
    score: float
    rationale: List[str]
    criteria: List[Criterion]
    evidence: List[str]
    assumptions: List[str]
    approved_decision: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "recommendedScenario": self.scenario_id,
            "score": self.score,
            "rationale": self.rationale,
            "criteria": [c.as_dict() for c in self.criteria],
            "evidence": self.evidence,
            "assumptions": self.assumptions,
            "approvedDecision": self.approved_decision,
            "status": "recommendation",
        }


@dataclass(frozen=True)
class ComparisonReport:
    """CR-10F/L — scenario comparison, ranking and recommendation."""

    criteria: List[Criterion]
    scores: List[ScenarioScore]
    recommendation: Recommendation

    def as_dict(self) -> Dict[str, Any]:
        return {
            "criteria": [c.as_dict() for c in self.criteria],
            "scores": [s.as_dict() for s in self.scores],
            "recommendation": self.recommendation.as_dict(),
        }


class DecisionIntelligenceEngine:
    """Weighted, explainable scenario comparison."""

    def compare(self, evaluations: List[ScenarioEvaluation],
                criteria: List[Criterion]) -> ComparisonReport:
        if not evaluations:
            raise DecisionError("at least one scenario evaluation is required")
        if not criteria:
            raise DecisionError("at least one criterion is required")
        total_weight = sum(c.weight for c in criteria)
        normalized = {c.id: c.weight / total_weight for c in criteria}

        scored: List[ScenarioScore] = []
        for evaluation in evaluations:
            components: List[ScoreComponent] = []
            for criterion in criteria:
                score = evaluation.score_for(criterion.id)
                weight = normalized[criterion.id]
                components.append(ScoreComponent(
                    criterion_id=criterion.id,
                    value=score.value,
                    weight=weight,
                    weighted_value=score.value * weight,
                    evidence=score.evidence,
                    assumptions=score.assumptions,
                ))
            scored.append(ScenarioScore(
                scenario_id=evaluation.scenario_id,
                total=sum(c.weighted_value for c in components),
                components=components,
            ))

        scored.sort(key=lambda s: (-s.total, s.scenario_id))
        scored = [ScenarioScore(s.scenario_id, s.total, s.components, rank=i + 1)
                  for i, s in enumerate(scored)]
        top = scored[0]
        evidence = [e for c in top.components for e in c.evidence]
        assumptions = [a for c in top.components for a in c.assumptions]
        rationale = [
            f"{c.criterion_id}: value={c.value:.3f}, weight={c.weight:.3f}, "
            f"weighted={c.weighted_value:.3f}"
            for c in top.components
        ]
        recommendation = Recommendation(
            scenario_id=top.scenario_id,
            score=top.total,
            rationale=rationale,
            criteria=criteria,
            evidence=evidence,
            assumptions=assumptions,
        )
        return ComparisonReport(criteria=criteria, scores=scored,
                                recommendation=recommendation)
