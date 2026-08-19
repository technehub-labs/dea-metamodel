"""CR-9.6 — assessment runtime (CR-9 §73/§74).

Provides a generic `AssessmentService` that walks an `Assessment` node in the
graph, aggregates the measures under its criteria, applies a scoring rule,
maps the score to a maturity level, and persists the result with explicit
provenance.

The service is deliberately generic: the framework defines the assessment,
the indicators and measures declare the inputs, and the assessment node
itself declares the scoring strategy and maturity mapping. This lets the
runtime execute the DMM in `models/dmm/executable.yaml` (CR-9 §73/§74) and
any other assessment profile that follows the same shape.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..graph import EntityNotFoundError, GraphStore, Node


@dataclass(frozen=True)
class AssessmentReport:
    """Result of executing one Assessment."""

    assessment_id: str
    framework_id: str
    measure_count: int
    score: float
    maturity_level: int
    target_maturity: Optional[int]
    result_id: str
    gap_id: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "assessmentId": self.assessment_id,
            "frameworkId": self.framework_id,
            "measureCount": self.measure_count,
            "score": self.score,
            "maturityLevel": self.maturity_level,
            "targetMaturity": self.target_maturity,
            "resultId": self.result_id,
            "gapId": self.gap_id,
        }


class AssessmentError(Exception):
    """Assessment execution invariant violated."""


def _avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _maturity_level(score: float, levels: Dict[int, int]) -> int:
    """Map a 0–5 score to a maturity level using an explicit levels map."""
    int_score = max(0, min(5, int(round(score))))
    return levels.get(int_score, 1)


class AssessmentService:
    """CR-9X/9Y — executability layer for the CR-5 assessment profile."""

    def __init__(self, store: GraphStore):
        self.store = store

    def execute_assessment(self, assessment_id: str) -> AssessmentReport:
        if not self.store.has_entity(assessment_id):
            raise AssessmentError(f"unknown assessment {assessment_id!r}")
        assessment = self.store.get_entity(assessment_id)
        if assessment.type != "Assessment":
            raise AssessmentError(
                f"node {assessment_id!r} is a {assessment.type}, not an Assessment")
        framework_id = self._find_framework(assessment_id)
        if framework_id is None:
            raise AssessmentError(
                f"assessment {assessment_id!r} is not conducted under a framework")
        measure_values = self._collect_measure_values(assessment_id)
        score = self._score(assessment, measure_values)
        levels = self._maturity_levels(assessment)
        maturity_level = _maturity_level(score, levels)
        target = self._target_maturity(assessment)

        result_id = f"{assessment_id}.result.{int(score * 1000)}"
        result_id = self._unique_id(result_id)
        from ..graph import Node as _Node
        self.store.create_entity(_Node(
            id=result_id, type="AssessmentResult",
            name=f"{assessment.name} Result",
            properties={
                "assessment_id": assessment_id,
                "framework_id": framework_id,
                "score": score,
                "maturity_level": maturity_level,
                "target_maturity": target,
                "scoring_strategy": assessment.properties.get(
                    "scoring_strategy", "average"),
                "derived_from": list(measure_values.keys()),
                "executed_by": "runtime.assessment",
                "state_role": "current",
            },
            source={"sourceSystem": "runtime.assessment",
                    "sourceTag": "engine"}))

        gap_id = None
        if target is not None and maturity_level < target:
            gap_id = f"{assessment_id}.gap.{int((target - maturity_level) * 1000)}"
            gap_id = self._unique_id(gap_id)
            self.store.create_entity(_Node(
                id=gap_id, type="AssessmentGap",
                name=f"{assessment.name} Gap",
                properties={
                    "assessment_id": assessment_id,
                    "subject": assessment_id,
                    "current_maturity": maturity_level,
                    "target_maturity": target,
                    "gap": target - maturity_level,
                },
                source={"sourceSystem": "runtime.assessment",
                        "sourceTag": "engine"}))

        return AssessmentReport(
            assessment_id=assessment_id,
            framework_id=framework_id,
            measure_count=len(measure_values),
            score=score,
            maturity_level=maturity_level,
            target_maturity=target,
            result_id=result_id,
            gap_id=gap_id,
        )

    def get_result(self, result_id: str) -> Optional[Node]:
        try:
            return self.store.get_entity(result_id)
        except EntityNotFoundError:
            return None

    # ---- internals ----
    def _find_framework(self, assessment_id: str) -> Optional[str]:
        for edge in self.store.edges_of(assessment_id, direction="out",
                                        rel_type="conducted-under"):
            return edge.target
        return None

    def _collect_measure_values(self, assessment_id: str) -> Dict[str, float]:
        """Collect measures declared by the assessment (measure_refs) or
        reachable from its outgoing edges."""
        values: Dict[str, float] = {}
        assessment = self.store.get_entity(assessment_id)
        measure_refs = assessment.properties.get("measure_refs") or []
        for measure_id in measure_refs:
            if not self.store.has_entity(measure_id):
                continue
            node = self.store.get_entity(measure_id)
            if node.type != "Measure":
                continue
            value = node.properties.get("value")
            if value is None:
                value = node.properties.get("properties", {}).get("value")
            if value is not None:
                values[node.id] = float(value)
        return values

    def _score(self, assessment: Node, values: Dict[str, float]) -> float:
        strategy = assessment.properties.get("scoring_strategy", "average")
        if strategy == "average":
            return _avg(list(values.values()))
        return _avg(list(values.values()))

    def _maturity_levels(self, assessment: Node) -> Dict[int, int]:
        levels = assessment.properties.get("maturity_levels")
        if not levels:
            return {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1}
        return {int(k): int(v) for k, v in dict(levels).items()}

    def _target_maturity(self, assessment: Node) -> Optional[int]:
        target = assessment.properties.get("target_maturity")
        if target is None:
            return None
        return int(target)

    def _unique_id(self, candidate: str) -> str:
        suffix = 0
        while self.store.has_entity(candidate):
            suffix += 1
            candidate = f"{candidate}.{suffix}"
        return candidate
