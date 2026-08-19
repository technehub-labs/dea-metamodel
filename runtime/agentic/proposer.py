"""CR-10 Phase 6 — Agentic scenario proposal (CR-10AJ/AK).

Generates a small set of candidate scenarios that close a maturity gap,
evaluates each via the CR-10 Phase 5 simulation adapter, and returns a
`ScenarioProposalReport` with a recommendation. The recommendation is never
approved by default — humans stay in the loop (CR-7 governance, CR-9CR).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..api import RuntimeService
from ..simulation import (SimulationAdapter, SimulationError,
                          SimulationRequest, SimulationResult)


class ScenarioProposerError(Exception):
    """Scenario proposer invariant violated."""


@dataclass(frozen=True)
class CandidateScenario:
    id: str
    scenario_id: str
    scenario_yaml: str
    rationale: str
    impact_summary: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scenarioId": self.scenario_id,
            "scenarioYaml": self.scenario_yaml,
            "rationale": self.rationale,
            "impactSummary": self.impact_summary,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ProposedRecommendation:
    """CR-10AI — never approved by default."""

    scenario_id: str
    rationale: str
    approved: bool = False
    approved_by: str = ""
    confidence: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scenarioId": self.scenario_id,
            "rationale": self.rationale,
            "approved": self.approved,
            "approvedBy": self.approved_by,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ScenarioProposalReport:
    assessment_id: str
    gap_id: str
    candidate_scenarios: List[CandidateScenario]
    recommendation: ProposedRecommendation

    def as_dict(self) -> Dict[str, Any]:
        return {
            "assessmentId": self.assessment_id,
            "gapId": self.gap_id,
            "candidateScenarios": [c.as_dict() for c in self.candidate_scenarios],
            "recommendation": self.recommendation.as_dict(),
        }


class ScenarioProposer:
    """CR-10AJ — agentic scenario generation for a maturity gap."""

    def __init__(self, service: RuntimeService,
                 scenarios: Dict[str, str],
                 adapter: SimulationAdapter):
        self.service = service
        self.scenarios = scenarios
        self.adapter = adapter

    def propose_scenarios_for_gap(self, gap_id: str) -> ScenarioProposalReport:
        store = self.service.store
        if not store.has_entity(gap_id):
            raise ScenarioProposerError(f"unknown gap {gap_id!r}")
        gap = store.get_entity(gap_id)
        if gap.type != "AssessmentGap":
            raise ScenarioProposerError(
                f"node {gap_id!r} is a {gap.type}, not an AssessmentGap")
        current = int(gap.properties.get("current_maturity", 0))
        target = int(gap.properties.get("target_maturity", 0))
        assessment_id = gap.properties.get("assessment_id", "")

        if current >= target:
            return ScenarioProposalReport(
                assessment_id=assessment_id, gap_id=gap_id,
                candidate_scenarios=[],
                recommendation=ProposedRecommendation(
                    scenario_id="",
                    rationale="no gap — current maturity already at or above target",
                    approved=False),
            )

        candidates = self._evaluate_candidates(assessment_id, gap_id)
        chosen = self._choose(candidates)
        return ScenarioProposalReport(
            assessment_id=assessment_id, gap_id=gap_id,
            candidate_scenarios=candidates,
            recommendation=ProposedRecommendation(
                scenario_id=chosen[0].scenario_id if chosen else "",
                rationale=(chosen[1] if chosen else
                           "no candidate scenario available"),
                confidence=chosen[0].confidence if chosen else None,
            ),
        )

    def _evaluate_candidates(self, assessment_id: str,
                              gap_id: str) -> List[CandidateScenario]:
        candidates: List[CandidateScenario] = []
        for idx, (scenario_id, yaml_path) in enumerate(self.scenarios.items()):
            request = SimulationRequest(
                id=f"sim.candidate.{idx}.{assessment_id}",
                scenario_id=scenario_id,
                baseline_id=gap_id,
                engine=self.adapter.engine,
                engine_version=self.adapter.engine_version,
                parameters={"gap_id": gap_id},
                assumptions=("current-maturity-from-gap",),
                timestamp="2026-08-19T00:00:00Z",
            )
            try:
                prepared = self.adapter.prepare(request)
                executed = self.adapter.execute(prepared)
                result = self.adapter.retrieve_results(executed)
                mapped = self.adapter.map_results(result, self.service)
                self.adapter.validate(mapped)
            except RuntimeError as exc:
                continue
            except Exception as exc:
                # If the scenario adapter fails on this candidate, skip it
                # but record the failure for transparency.
                candidates.append(CandidateScenario(
                    id=f"candidate.{idx}", scenario_id=scenario_id,
                    scenario_yaml=yaml_path,
                    rationale=f"evaluation failed: {exc}",
                    impact_summary={},
                    confidence=None,
                ))
                continue
            except SimulationError as exc:
                continue
            candidates.append(CandidateScenario(
                id=f"candidate.{idx}",
                scenario_id=scenario_id,
                scenario_yaml=yaml_path,
                rationale=f"closes {current_maturity_text(gap_id)} gap",
                impact_summary={
                    "added_entities": list(mapped.added_entities),
                    "removed_entities": list(mapped.removed_entities),
                    "modified_entities": list(mapped.modified_entities),
                },
                confidence=result.confidence,
            ))
        return candidates

    def _choose(self, candidates: List[CandidateScenario]
                 ) -> Optional[Any]:
        if not candidates:
            return None
        return candidates[0], "single candidate scenario evaluated"


def current_maturity_text(gap_id: str) -> str:
    """Synthetic helper — exposes the gap reference for rationale."""
    return f"maturity assessment gap {gap_id}"
