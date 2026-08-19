"""CR-10 Phase 6 — Agentic scenario proposal tests."""
from pathlib import Path

import pytest

from runtime.agentic import (CandidateScenario, ScenarioProposalReport,
                              ScenarioProposer, ScenarioProposerError)
from runtime.api import RuntimeService
from runtime.assessment import AssessmentService
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.simulation import ScenarioImpactAdapter

from conftest import BASE


def _runtime():
    service = RuntimeService(InMemoryGraphStore())
    load_model(BASE / "models" / "dmm" / "executable.yaml", service.store)
    load_model(BASE / "models" / "scenarios" / "customer-service-baseline.yaml",
               service.store)
    AssessmentService(service.store).execute_assessment("asm.2026-q3")
    return service


def _proposer(service):
    scenarios = {
        "scenario.replace-customer-platform": str(
            BASE / "models" / "scenarios" / "customer-platform-replacement.yaml"),
    }
    return ScenarioProposer(
        service,
        scenarios=scenarios,
        adapter=ScenarioImpactAdapter(service, scenarios=scenarios),
    )


def _gap_id(service):
    return service.store.query(type="AssessmentGap")[0].id


def test_proposer_returns_proposal_report_for_kn_assessment_gap():
    service = _runtime()
    proposer = _proposer(service)

    report = proposer.propose_scenarios_for_gap(_gap_id(service))

    assert isinstance(report, ScenarioProposalReport)
    assert report.assessment_id == "asm.2026-q3"
    assert report.gap_id == _gap_id(service)
    assert len(report.candidate_scenarios) >= 1
    assert report.recommendation.approved is False


def test_recommendation_is_not_approved_by_default():
    service = _runtime()
    proposer = _proposer(service)

    report = proposer.propose_scenarios_for_gap(_gap_id(service))

    assert report.recommendation.approved is False
    assert report.recommendation.approved_by == ""


def test_candidate_carries_impact_summary_from_adapter():
    service = _runtime()
    proposer = _proposer(service)

    report = proposer.propose_scenarios_for_gap(_gap_id(service))
    candidate = report.candidate_scenarios[0]
    assert isinstance(candidate, CandidateScenario)
    assert candidate.impact_summary is not None
    assert "platform.customer-v2" in candidate.impact_summary.get(
        "added_entities", [])


def test_proposer_returns_empty_when_current_at_or_above_target():
    service = _runtime()
    gap_id = _gap_id(service)
    gap = service.store.get_entity(gap_id)
    service.store.update_entity(
        gap_id, properties={**gap.properties, "current_maturity": 5})
    proposer = _proposer(service)

    report = proposer.propose_scenarios_for_gap(gap_id)
    assert report.candidate_scenarios == []
    assert "no gap" in report.recommendation.rationale.lower()


def test_proposer_unknown_gap_raises():
    service = _runtime()
    proposer = _proposer(service)
    with pytest.raises(ScenarioProposerError, match="unknown gap"):
        proposer.propose_scenarios_for_gap("asm.2026-q3.gap.9999")
