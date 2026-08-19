"""CR-9.6 — assessment runtime tests."""
from pathlib import Path

import pytest

from runtime.assessment import AssessmentReport, AssessmentService
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model

from conftest import BASE


def test_assessment_service_executes_dmm_scenario():
    """CR-9X/9Y: an Assessment is executed against the graph and produces
    an AssessmentResult entity with provenance."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    service = AssessmentService(store)

    report = service.execute_assessment("asm.2026-q3")

    assert report.assessment_id == "asm.2026-q3"
    assert report.measure_count == 2
    assert report.score == pytest.approx(2.5)
    assert report.maturity_level == 2
    aResult = service.get_result(report.result_id)
    assert aResult is not None
    assert aResult.properties["score"] == pytest.approx(2.5)
    assert aResult.properties["maturity_level"] == 2
    assert aResult.properties["target_maturity"] == 4
    assert store.has_entity(report.result_id)


def test_assessment_produces_gap_when_target_maturity_above_actual():
    """CR-9Y: a gap is recorded when current maturity is below target."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    report = AssessmentService(store).execute_assessment("asm.2026-q3")

    assert report.gap_id is not None
    gap = store.get_entity(report.gap_id)
    assert gap.properties["current_maturity"] == 2
    assert gap.properties["target_maturity"] == 4
    assert gap.properties["gap"] == 2


def test_assessment_records_provenance_for_inferred_result():
    """CR-9T: the AssessmentResult carries provenance of the rule and inputs."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    service = AssessmentService(store)
    report = service.execute_assessment("asm.2026-q3")
    aResult = store.get_entity(report.result_id)

    assert aResult.properties["assessment_id"] == "asm.2026-q3"
    assert aResult.properties["framework_id"] == "fw.dmmv5"
    assert aResult.properties["scoring_strategy"] == "average"
    derived = aResult.properties["derived_from"]
    assert "me.decision-rights.observed" in derived
    assert "me.tooling-automation.observed" in derived


def test_assessment_without_maturity_levels_record_level_one():
    """CR-9Y: missing maturity levels fall back to level 1, not zero."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    node = store.get_entity("asm.2026-q3")
    props = dict(node.properties)
    props.pop("maturity_levels", None)
    store.update_entity("asm.2026-q3", properties=props)
    report = AssessmentService(store).execute_assessment("asm.2026-q3")
    assert report.maturity_level == 1


def test_assessment_unknown_id_raises():
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    with pytest.raises(Exception, match="unknown assessment"):
        AssessmentService(store).execute_assessment("asm.nonexistent")
