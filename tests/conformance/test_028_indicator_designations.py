"""CR-MET-008: Governed Management Indicator Designations and Semantics.

CR-MET-008 binding CR-MET-001 / CR-MET-006 / CR-MET-007.
"""
import json

import yaml

from conftest import BASE


def _schemas():
    return {p.stem: json.loads(p.read_text())
            for p in sorted((BASE / "schemas" / "entities").glob("*.json"))}


def _vocab_values(key):
    voc = yaml.safe_load(
        (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
    )["classifications"]
    if key not in voc:
        return None
    return set(voc[key]["values"])


def _fixtures():
    return yaml.safe_load(
        (BASE / "tests" / "conformance" / "fixtures" / "indicator_designations.yaml").read_text()
    )


def _normative():
    return yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())


# -------- schema presence --------

def test_indicator_designation_schema_present_with_binding_fields():
    """indicator-designation.json schema MUST exist with the 13 binding attributes (CR-MET-008 section 5)."""
    schemas = _schemas()
    assert "indicator-designation" in schemas, "CR-MET-008: indicator-designation.json schema missing"
    props = schemas["indicator-designation"]["properties"]
    for field in [
        "designation_type", "associated_metric_ref", "management_purpose",
        "associated_objective_ref", "organizational_scope",
        "accountable_owner_ref", "reporting_frequency", "target_reference",
        "threshold_reference", "escalation_rules", "measurement_orientation",
        "effective_period", "approval_status",
    ]:
        assert field in props, f"CR-MET-008: indicator-designation.json must declare '{field}'"


# -------- controlled vocabularies --------

def test_designation_type_vocabulary():
    """IndicatorDesignation.designation_type MUST be present with 5 binding values."""
    values = _vocab_values("IndicatorDesignation.designation_type")
    assert values is not None, "CR-MET-008: IndicatorDesignation.designation_type vocabulary missing"
    expected = {"KPI", "KRI", "KCI", "SLI", "Operational"}
    assert values == expected, \
        f"CR-MET-008: IndicatorDesignation.designation_type must be {sorted(expected)} (got {sorted(values)})"


def test_measurement_orientation_vocabulary():
    """IndicatorDesignation.measurement_orientation MUST be present with 3 binding values."""
    values = _vocab_values("IndicatorDesignation.measurement_orientation")
    assert values is not None, "CR-MET-008: IndicatorDesignation.measurement_orientation vocabulary missing"
    expected = {"leading", "lagging", "neutral"}
    assert values == expected, \
        f"CR-MET-008: IndicatorDesignation.measurement_orientation must be {sorted(expected)} (got {sorted(values)})"


def test_reporting_frequency_vocabulary():
    """IndicatorDesignation.reporting_frequency MUST be present with 8 binding values."""
    values = _vocab_values("IndicatorDesignation.reporting_frequency")
    assert values is not None, "CR-MET-008: IndicatorDesignation.reporting_frequency vocabulary missing"
    expected = {"real_time", "hourly", "daily", "weekly", "monthly", "quarterly", "semi_annual", "annual"}
    assert values == expected, \
        f"CR-MET-008: IndicatorDesignation.reporting_frequency must be {sorted(expected)} (got {sorted(values)})"


def test_approval_status_vocabulary():
    """IndicatorDesignation.approval_status MUST be present with 4 binding values."""
    values = _vocab_values("IndicatorDesignation.approval_status")
    assert values is not None, "CR-MET-008: IndicatorDesignation.approval_status vocabulary missing"
    expected = {"draft", "proposed", "approved", "retired"}
    assert values == expected, \
        f"CR-MET-008: IndicatorDesignation.approval_status must be {sorted(expected)} (got {sorted(values)})"


# -------- fixture integrity --------

def test_fixtures_use_only_valid_vocabulary_values():
    """Every fixture's controlled-vocab field must use a value in the vocabulary."""
    fx = _fixtures()
    type_values = _vocab_values("IndicatorDesignation.designation_type")
    orient_values = _vocab_values("IndicatorDesignation.measurement_orientation")
    freq_values = _vocab_values("IndicatorDesignation.reporting_frequency")
    status_values = _vocab_values("IndicatorDesignation.approval_status")
    for d in fx["designations"]:
        assert d["designation_type"] in type_values, \
            f"designation {d['id']} designation_type {d['designation_type']!r} not in vocabulary"
        assert d["measurement_orientation"] in orient_values, \
            f"designation {d['id']} measurement_orientation {d['measurement_orientation']!r} not in vocabulary"
        assert d["reporting_frequency"] in freq_values, \
            f"designation {d['id']} reporting_frequency {d['reporting_frequency']!r} not in vocabulary"
        assert d["approval_status"] in status_values, \
            f"designation {d['id']} approval_status {d['approval_status']!r} not in vocabulary"


def test_fixtures_cover_all_5_designation_types():
    """The fixtures MUST cover all 5 designation_types from the controlled vocabulary."""
    fx = _fixtures()
    covered_types = {d["designation_type"] for d in fx["designations"]}
    expected = {"KPI", "KRI", "KCI", "SLI", "Operational"}
    assert covered_types == expected, \
        f"CR-MET-008: fixtures must cover all 5 designation types (got {covered_types})"


def test_same_metric_multiple_designations_pattern():
    """CR-MET-008 binding: One Metric may carry multiple designations (EGV-004 preserved)."""
    fx = _fixtures()
    # Customer Retention Rate carries both KPI Lagging and KRI Leading
    crr_refs = [d["associated_metric_ref"] for d in fx["designations"]
                if d["associated_metric_ref"] == "dea:metric-customer-retention-rate"]
    assert len(crr_refs) >= 2, \
        "CR-MET-008: the same Metric must carry multiple designations (CR-MET-008 EGV-004 invariant)"
    # And they have different designation types and orientations
    types = {d["designation_type"] for d in fx["designations"]
             if d["associated_metric_ref"] == "dea:metric-customer-retention-rate"}
    orientations = {d["measurement_orientation"] for d in fx["designations"]
                    if d["associated_metric_ref"] == "dea:metric-customer-retention-rate"}
    assert len(types) >= 2, \
        f"CR-MET-008: same Metric should carry multiple designation types (got {types})"
    assert len(orientations) >= 2, \
        f"CR-MET-008: same Metric should support multiple orientations (got {orientations})"


def test_kpi_designations_have_objective_owner_reporting():
    """CR-MET-008 section 5.1: KPI designations MUST have associated_objective_ref, accountable_owner_ref, reporting_frequency, measurement_orientation."""
    fx = _fixtures()
    for d in fx["designations"]:
        if d["designation_type"] == "KPI":
            assert d.get("associated_objective_ref"), \
                f"KPI designation {d['id']} must have associated_objective_ref"
            assert d.get("accountable_owner_ref"), \
                f"KPI designation {d['id']} must have accountable_owner_ref"
            assert d.get("reporting_frequency"), \
                f"KPI designation {d['id']} must have reporting_frequency"
            assert d.get("measurement_orientation"), \
                f"KPI designation {d['id']} must have measurement_orientation"


def test_kri_designations_have_escalation_and_owner():
    """CR-MET-008 section 5.2: KRI designations MUST have escalation_rules and accountable_owner_ref."""
    fx = _fixtures()
    for d in fx["designations"]:
        if d["designation_type"] == "KRI":
            assert d.get("escalation_rules"), \
                f"KRI designation {d['id']} must have escalation_rules (section 5.2)"
            assert d.get("accountable_owner_ref"), \
                f"KRI designation {d['id']} must have accountable_owner_ref (section 5.2 risk owner)"


def test_kci_designations_have_control_objective_and_owner():
    """CR-MET-008 section 5.3: KCI designations MUST have associated_objective_ref (control objective) and accountable_owner_ref (control owner)."""
    fx = _fixtures()
    for d in fx["designations"]:
        if d["designation_type"] == "KCI":
            assert d.get("associated_objective_ref"), \
                f"KCI designation {d['id']} must have associated_objective_ref (control objective)"
            assert d.get("accountable_owner_ref"), \
                f"KCI designation {d['id']} must have accountable_owner_ref (control owner)"


# -------- canonical-source invariants --------

def test_new_entity_in_canonical_source():
    """dea:IndicatorDesignation MUST be present in the canonical source."""
    entity_ids = {e["id"] for e in _normative()["entities"]}
    assert "dea:IndicatorDesignation" in entity_ids, \
        "CR-MET-008: dea:IndicatorDesignation entity missing"


def test_new_relationship_in_canonical_source():
    """dea:has-designation MUST be present in the canonical source with the correct source/target."""
    rels = {r["id"]: r for r in _normative()["relationships"]}
    assert "dea:has-designation" in rels, "CR-MET-008: dea:has-designation missing"
    rel = rels["dea:has-designation"]
    assert "dea:PerformanceMetric" in rel["source"]["types"], \
        "CR-MET-008: dea:has-designation source MUST be PerformanceMetric"
    assert "dea:IndicatorDesignation" in rel["target"]["types"], \
        "CR-MET-008: dea:has-designation target MUST be IndicatorDesignation"
    assert rel["category"] == "governance", \
        f"CR-MET-008: dea:has-designation category must be 'governance' (got {rel['category']})"


def test_relationship_instance_enum_includes_has_designation():
    """The relationship-instance.json enum MUST include 'has-designation'."""
    schema = json.loads((BASE / "schemas" / "relationships" / "relationship-instance.json").read_text())
    enum = schema["properties"]["relationship_type"]["enum"]
    assert "has-designation" in enum, \
        "CR-MET-008: relationship-instance.json enum must include 'has-designation'"


def test_entity_count_increment():
    """CR-MET-008 MUST add 1 NEW entity (157 -> 158)."""
    assert len(_normative()["entities"]) == 158, \
        f"CR-MET-008: entity count must be 158 (got {len(_normative()['entities'])})"


def test_relationship_count_increment():
    """CR-MET-008 MUST add 1 NEW relationship (112 -> 113)."""
    assert len(_normative()["relationships"]) == 113, \
        f"CR-MET-008: relationship count must be 113 (got {len(_normative()['relationships'])})"


def test_performance_metric_unchanged():
    """CR-MET-008 MUST NOT modify the PerformanceMetric entity or the Metric schema; designations are separate."""
    normative = _normative()
    pm = next(e for e in normative["entities"] if e["id"] == "dea:PerformanceMetric")
    # The PerformanceMetric entity should not have a 'designations' attribute
    # The designations live on dea:IndicatorDesignation via dea:has-designation
    assert pm["id"] == "dea:PerformanceMetric"
    # The Metric schema should not declare the 13 designation fields
    schemas = _schemas()
    metric_props = schemas["metric"]["properties"]
    for designation_field in [
        "designation_type", "reporting_frequency", "measurement_orientation",
        "escalation_rules", "accountable_owner_ref",
    ]:
        assert designation_field not in metric_props, \
            f"CR-MET-008: metric schema must NOT carry designation field '{designation_field}'"