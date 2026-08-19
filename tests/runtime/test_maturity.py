"""CR-10 Phase 4 — maturity projection tests."""
from pathlib import Path

import pytest

from runtime.api import RuntimeService
from runtime.assessment import AssessmentService
from runtime.graph import InMemoryGraphStore
from runtime.maturity import (MaturityProjection, MaturityProjector,
                              MaturityProjectorError)
from runtime.model import load_model

from conftest import BASE


def _runtime():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    AssessmentService(service.store).execute_assessment("asm.2026-q3")
    return service


def _gap_id(service):
    return service.store.query(type="AssessmentGap")[0].id


def test_maturity_projector_is_exported():
    from runtime.maturity import MaturityProjector as Exported
    assert Exported is MaturityProjector


def test_project_returns_projection_for_kn_assessment_gap():
    service = _runtime()
    service.create_entity("init.embedded", "ChangeInitiative",
                          "Embedded Tooling Initiative")
    projector = MaturityProjector(service)

    projection = projector.project(_gap_id(service))

    assert isinstance(projection, MaturityProjection)
    assert projection.assessment_id == "asm.2026-q3"
    assert projection.current_maturity == 2
    assert projection.target_maturity == 4
    assert projection.proposed_initiative_ids == ["init.embedded"]
    assert projection.projected_maturity >= projection.current_maturity


def test_project_skips_when_current_at_or_above_target():
    service = _runtime()
    gap_id = _gap_id(service)
    gap = service.store.get_entity(gap_id)
    service.store.update_entity(gap_id, properties={**gap.properties, "current_maturity": 4})
    projector = MaturityProjector(service)

    projection = projector.project(gap_id)

    assert projection.proposed_initiative_ids == []
    assert projection.projected_maturity == 4


def test_project_emits_no_initiatives_when_graph_has_none_for_the_gap():
    service = _runtime()
    projector = MaturityProjector(service)

    projection = projector.project(_gap_id(service))

    assert isinstance(projection, MaturityProjection)
    assert projection.assessment_id == "asm.2026-q3"
    assert projection.current_maturity == 2
    assert projection.target_maturity == 4


def test_project_unknown_gap_raises():
    service = _runtime()
    projector = MaturityProjector(service)
    with pytest.raises(MaturityProjectorError, match="unknown gap"):
        projector.project("asm.2026-q3.gap.9999")


def test_project_recomputes_projection_when_initiatives_added_later():
    service = _runtime()
    projector = MaturityProjector(service)

    before = projector.project(_gap_id(service))
    service.create_entity("init.later", "ChangeInitiative", "Later Initiative")
    after = projector.project(_gap_id(service))

    assert "init.later" in after.proposed_initiative_ids
    assert after.projected_maturity >= before.projected_maturity
