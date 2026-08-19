"""CR-9.9 — OpenDEA Explorer runtime API (CR-9BX…CB).

The Explorer exposes seven runtime modes — explore, assess, trace, compare,
query, simulate, govern — as a thin facade over the runtime services
already shipped. The web Explorer UI would consume this surface; nothing
here replaces the existing Vite viewer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..api import RuntimeService
from ..assessment import AssessmentReport, AssessmentService
from ..decision import DecisionEvaluation, DecisionImpactEngine
from ..graph import GraphStore, Node
from ..provenance import ProvenanceService


class ExplorerMode(str, Enum):
    """The seven Explorer modes (CR-9 §73/§74)."""

    EXPLORE = "explore"
    ASSESS = "assess"
    TRACE = "trace"
    COMPARE = "compare"
    QUERY = "query"
    SIMULATE = "simulate"
    GOVERN = "govern"


@dataclass(frozen=True)
class TraceChain:
    """Conclusion -> evidence -> source chain (CR-9BZ)."""

    subject: str
    through: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "through": self.through,
            "evidence": list(self.evidence),
        }


class ExplorerService:
    """CR-9.9 — the runtime surface that an Explorer UI consumes."""

    def __init__(self, service: RuntimeService):
        self.service = service
        self.assessment = AssessmentService(service.store)
        self.decision = DecisionImpactEngine(service)
        self.provenance = ProvenanceService(service.store)

    @property
    def modes(self):
        return list(ExplorerMode)

    def explore(self, type: Optional[str] = None,
                lifecycle_status: Optional[str] = None,
                limit: int = 100) -> List[Node]:
        nodes = self.service.query(type=type)
        if lifecycle_status is not None:
            nodes = [n for n in nodes if n.lifecycle_status == lifecycle_status]
        return nodes[:limit]

    def assess(self, assessment_id: str) -> Dict[str, Any]:
        report: AssessmentReport = self.assessment.execute_assessment(assessment_id)
        return report.as_dict()

    def trace(self, subject: str, through: str = "supports") -> TraceChain:
        evidence = []
        for edge in self.service.store.edges_of(subject, direction="in",
                                               rel_type=through):
            evidence.append({
                "entity_id": edge.source,
                "entity_type": self.service.store.get_entity(edge.source).type,
                "edge": list(edge.key),
            })
        return TraceChain(subject=subject, through=through, evidence=evidence)

    def query(self, type: Optional[str] = None) -> List[Node]:
        return self.service.query(type=type)

    def compare(self, evaluations, criteria,
                scenario_engine: Optional[Any] = None,
                baseline_id: Optional[str] = None) -> Dict[str, Any]:
        from ..scenario import (ScenarioEngine, ScenarioStatus,
                                  load_scenario)
        engine = scenario_engine or ScenarioEngine()
        if baseline_id is not None:
            from ..scenario.engine import snapshot_store
            baseline = baseline_id
        from ..scenario.decision import DecisionIntelligenceEngine
        report = DecisionIntelligenceEngine().compare(evaluations, criteria)
        return {
            "criteria": [c.as_dict() for c in report.criteria],
            "scores": [s.as_dict() for s in report.scores],
            "recommendation": report.recommendation.as_dict(),
        }

    def simulate_from_yaml(self, yaml_path: str, baseline_id: str) -> Dict[str, Any]:
        from ..scenario import ScenarioEngine, ScenarioStatus, load_scenario
        from ..scenario.impact import ImpactEngine
        scenario = load_scenario(yaml_path)
        scenario.baseline = baseline_id
        scenario.transition(ScenarioStatus.DEFINED)
        baseline_snapshot = ScenarioEngine().create_baseline(
            self.service.store, baseline_id, 'Explorer Baseline')
        report = ImpactEngine().evaluate(scenario, baseline_snapshot)
        return {
            'scenario': scenario.id,
            'delta': report.delta.as_dict(),
            'impacts': [i.as_dict() for i in report.impacts[:5]],
        }

    def simulate(self, scenario_id: str, baseline_id: str,
                 scenario_engine: Optional[ScenarioEngine] = None
                 ) -> Dict[str, Any]:
        from ..scenario import (ScenarioEngine, ScenarioStatus,
                                  load_scenario)
        from ..scenario.engine import snapshot_store
        from ..scenario.impact import ImpactEngine
        engine = scenario_engine or ScenarioEngine()
        baseline_snapshot = engine.create_baseline(
            self.service.store, baseline_id, "Explorer Baseline")
        scenario = load_scenario(scenario_id) if scenario_id.endswith(".yaml") \
            else None
        if scenario is None:
            return {"scenario": scenario_id, "status": "not-found"}
        scenario.transition(ScenarioStatus.DEFINED)
        report = ImpactEngine().evaluate(scenario, baseline_snapshot)
        return {
            "scenario": scenario.id,
            "delta": report.delta.as_dict(),
            "impacts": [i.as_dict() for i in report.impacts[:5]],
        }

    def govern(self, decision_id: str) -> Dict[str, Any]:
        evaluation = self.decision.evaluate_decision(decision_id)
        return evaluation.as_dict()
