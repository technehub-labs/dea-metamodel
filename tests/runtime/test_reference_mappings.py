"""CR-11 Phase 5 — reference mappings (CR-11X/Y/Z + DMM)."""

import pytest

from runtime.interoperability import (InteropRegistry, Lossiness,
                                       MappingConfidence, MappingRelation,
                                       SemanticMapping, Namespace,
                                       load_reference_mappings)
from conftest import BASE


def test_loader_lifts_archimate_bpmn_dmn_dmm_mappings():
    """CR-11X/Y/Z + DMM — the four reference mappings parse and register."""
    reg = InteropRegistry()
    summary = load_reference_mappings(registry=reg)

    for std in ("archimate", "bpmn", "dmn", "dmm"):
        assert std in summary, summary
        assert summary[std]["loaded"] is True
        assert summary[std]["mappings_lifted"] >= 5, summary[std]

    # Every lifted mapping carries the four required governance fields.
    for mapping in reg.mappings.values():
        assert mapping.owner == "reference-mapping"
        assert mapping.version == "1.0.0"
        assert mapping.status.value == "ACTIVE"
        # OpenDEA targets stay opendea: — extensions live in the standard namespace.
        assert mapping.target_concept.startswith("opendea:")


def test_archimate_mapping_carries_confidence_and_lossiness():
    """CR-11X — confidence/lossiness explicit on the ArchiMate mapping rows."""
    reg = InteropRegistry()
    summary = load_reference_mappings(registry=reg, standards=["archimate"])

    # ArchiMate ↔ BusinessCapability is an EXACT / LOSSLESS pair — the closest
    # mapping we ship.
    key = "archimate:Capability|opendea:BusinessCapability|1.0.0"
    mapping = reg.mappings[key]
    assert mapping.confidence == MappingConfidence.EXACT
    assert mapping.lossiness == Lossiness.LOSSLESS

    # Arches — Tech Component is HIGH / PARTIAL (OpenDEA Technology is broader).
    key = "archimate:Technology Component|opendea:Technology|1.0.0"
    assert reg.mappings[key].confidence == MappingConfidence.HIGH
    assert reg.mappings[key].lossiness == Lossiness.PARTIAL


def test_archimate_gaps_are_documented_as_no_direct_equivalent():
    """Decision/Change/Agent/AssessmentResult have no ArchiMate counterpart."""
    reg = InteropRegistry()
    summary = load_reference_mappings(registry=reg, standards=["archimate"])

    # 4 gaps were surfaced — the absence of equivalence is itself information.
    assert summary["archimate"]["gaps"] == 4
    # None of the gaps produced a SemanticMapping entry.
    pairs = {(m.source_concept, m.target_concept) for m in reg.mappings.values()}
    assert not any("Decision" == m.split(":")[-1] and "archimate" in s
                   for s, m in pairs)


def test_bpmn_mapping_decision_criterion_maps_to_exclusive_gateway():
    """CR-11Y — DecisionCriterion absorbs the BPMN exclusive-gateway shape."""
    reg = InteropRegistry()
    load_reference_mappings(registry=reg, standards=["bpmn"])

    # OpenDEA DecisionCriterion ↔ BPMN Exclusive Gateway.
    key = "bpmn:Exclusive Gateway|opendea:DecisionCriterion|1.0.0"
    assert key in reg.mappings
    assert reg.mappings[key].confidence == MappingConfidence.HIGH


def test_dmn_mapping_records_decision_path_and_felt_preservation():
    """CR-11Z — DMN profile shape (Decision → Evidence → DecisionRecord) is captured."""
    reg = InteropRegistry()
    summary = load_reference_mappings(registry=reg, standards=["dmn"])

    # DecisionRecord ↔ DMN DecisionResult: EXACT / LOSSLESS.
    key = "dmn:DecisionResult (decision invocation)|opendea:DecisionRecord|1.0.0"
    assert key in reg.mappings
    assert reg.mappings[key].confidence == MappingConfidence.EXACT

    # FEEL preservation is recorded in the loaded YAML (not the in-memory
    # mapping), so we round-trip via MappingRegistry.
    from runtime.interoperability.mapping_loader import MappingRegistry
    data = MappingRegistry.default().load_standard("dmn.yaml")
    assert data["feels_preserved"]["rule_expression_kind"] == "dmn-feel"
    assert data["profile"]["decision"] == "opendea:Decision"
    assert data["profile"]["evidence"] == "opendea:Evidence"
    assert data["profile"]["outcome"] == "opendea:DecisionRecord"

    assert summary["dmn"]["mappings_lifted"] >= 10


def test_dmm_band_correspondence_maps_levels_to_maturity_v2():
    """DMM Level 1–5 ↔ OpenDEA Emergent/Structured/Systematic/Adaptive/Self-Optimising."""
    from runtime.interoperability.mapping_loader import MappingRegistry
    data = MappingRegistry.default().load_standard("dmm.yaml")
    bands = data["bands"]
    assert bands["DMM_initial"]["opendea"] == "Emergent"
    assert bands["DMM_optimising"]["opendea"] == "Self-Optimising"
    assert bands["DMM_managed"]["opendea"] == "Structured"
    assert bands["DMM_quantitative"]["opendea"] == "Adaptive"


def test_mapping_does_not_adopt_external_metamodel():
    """No mapping writes to opendea: namespace (CR-11AR/W)."""
    reg = InteropRegistry()
    load_reference_mappings(registry=reg)
    # Source side stays external.
    for mapping in reg.mappings.values():
        ns, _ = mapping.source_concept.split(":", 1)
        assert ns != "opendea"


def test_loader_is_deterministic_and_idempotent():
    """Calling the loader twice produces the same registry state."""
    reg_a = InteropRegistry()
    reg_b = InteropRegistry()
    summary_a = load_reference_mappings(registry=reg_a)
    summary_b = load_reference_mappings(registry=reg_b)
    assert summary_a == summary_b
    assert set(reg_a.mappings) == set(reg_b.mappings)
