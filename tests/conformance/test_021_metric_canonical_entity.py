"""CR-MET-001: Metric canonical entity + new Measurement/MeasurementObservation entities.

CR-MET-001 binding CR-MET-000 reconciliation and ADR-MET-001 / ADR-MET-002.
"""
import json
import re

import yaml

from conftest import BASE

ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*:[a-z0-9-]+(/[a-z0-9-]+)?$")


def _entities():
    path = BASE / "metamodel" / "dea-metamodel.yaml"
    return [e for e in yaml.safe_load(path.read_text()).get("entities", [])
            if isinstance(e, dict) and e.get("id", "").startswith("dea:")]


def _schemas():
    return {p.stem: json.loads(p.read_text())
            for p in sorted((BASE / "schemas" / "entities").glob("*.json"))}


def test_metric_re_membershiped_to_foundational():
    """dea:PerformanceMetric MUST be in foundational scope per ADR-MET-001."""
    by_id = {e["id"]: e for e in _entities()}
    assert "dea:PerformanceMetric" in by_id, \
        "CR-MET-001: dea:PerformanceMetric missing from registry"
    metric = by_id["dea:PerformanceMetric"]
    membership = metric.get("membership", {})
    assert membership.get("kind") == "core", \
        f"CR-MET-001: dea:PerformanceMetric membership.kind must be 'core' (got {membership.get('kind')})"
    assert membership.get("profile") in (None, "null"), \
        f"CR-MET-001: dea:PerformanceMetric membership.profile must be null (got {membership.get('profile')})"


def test_metric_legacy_ids_include_cr10j_scenario_metric():
    """dea:PerformanceMetric.legacy_ids MUST include CR-10J:scenario-metric."""
    by_id = {e["id"]: e for e in _entities()}
    metric = by_id["dea:PerformanceMetric"]
    legacy = metric.get("legacy_ids", [])
    assert "CR-10J:scenario-metric" in legacy, \
        f"CR-MET-001: dea:PerformanceMetric.legacy_ids must include 'CR-10J:scenario-metric' (got {legacy})"


def test_metric_definition_is_binding_text():
    """dea:PerformanceMetric.definition MUST contain the binding CR-MET-001 markers."""
    by_id = {e["id"]: e for e in _entities()}
    metric = by_id["dea:PerformanceMetric"]
    definition = metric.get("definition", "")
    for marker in [
        "formally defined, reusable semantic specification",
        "CR-MET-001",
        "foundational",
        "measurement-dimension",
        "MUST NOT contain individual observation values",
    ]:
        assert marker in definition, \
            f"CR-MET-001: dea:PerformanceMetric.definition missing marker '{marker}'"


def test_metric_dimension_measurement_dimension():
    """dea:PerformanceMetric.dimension MUST be measurement-dimension (ADR-0002 D1)."""
    by_id = {e["id"]: e for e in _entities()}
    metric = by_id["dea:PerformanceMetric"]
    assert metric.get("dimension") == "measurement-dimension", \
        f"CR-MET-001: dea:PerformanceMetric.dimension must be 'measurement-dimension' (got {metric.get('dimension')})"


def test_measurement_entity_present():
    """dea:Measurement MUST be present and foundational per ADR-MET-002."""
    by_id = {e["id"]: e for e in _entities()}
    assert "dea:Measurement" in by_id, \
        "CR-MET-001: dea:Measurement missing from registry"
    measurement = by_id["dea:Measurement"]
    membership = measurement.get("membership", {})
    assert membership.get("kind") == "core", \
        f"CR-MET-001: dea:Measurement membership.kind must be 'core' (got {membership.get('kind')})"
    assert measurement.get("dimension") == "measurement-dimension", \
        f"CR-MET-001: dea:Measurement dimension must be 'measurement-dimension' (got {measurement.get('dimension')})"


def test_measurement_observation_entity_present():
    """dea:MeasurementObservation MUST be present and foundational per ADR-MET-002."""
    by_id = {e["id"]: e for e in _entities()}
    assert "dea:MeasurementObservation" in by_id, \
        "CR-MET-001: dea:MeasurementObservation missing from registry"
    obs = by_id["dea:MeasurementObservation"]
    membership = obs.get("membership", {})
    assert membership.get("kind") == "core", \
        f"CR-MET-001: dea:MeasurementObservation membership.kind must be 'core' (got {membership.get('kind')})"
    assert obs.get("dimension") == "measurement-dimension", \
        f"CR-MET-001: dea:MeasurementObservation dimension must be 'measurement-dimension' (got {obs.get('dimension')})"


def test_observation_unchanged_in_assessment_profile():
    """Existing dea:Observation MUST stay in profile: dea:assessment unchanged per user clarification 2026-10-18."""
    by_id = {e["id"]: e for e in _entities()}
    assert "dea:Observation" in by_id, \
        "CR-MET-001: dea:Observation missing from registry (regression)"
    observation = by_id["dea:Observation"]
    membership = observation.get("membership", {})
    assert membership.get("kind") == "profile", \
        f"CR-MET-001: dea:Observation membership.kind must remain 'profile' (got {membership.get('kind')})"
    assert membership.get("profile") == "dea:assessment", \
        f"CR-MET-001: dea:Observation membership.profile must remain 'dea:assessment' (got {membership.get('profile')})"


def test_metric_schema_requires_subject_concept():
    """metric.json MUST declare subject_concept as required per CR-MET-001."""
    schemas = _schemas()
    assert "metric" in schemas, "CR-MET-001: metric.json schema missing"
    schema = schemas["metric"]
    required = schema.get("required", [])
    assert "subject_concept" in required, \
        f"CR-MET-001: metric.json must require 'subject_concept' (got {required})"


def test_metric_schema_requires_measurement_nature():
    """metric.json MUST declare measurement_nature as required per CR-MET-001."""
    schemas = _schemas()
    schema = schemas["metric"]
    required = schema.get("required", [])
    assert "measurement_nature" in required, \
        f"CR-MET-001: metric.json must require 'measurement_nature' (got {required})"
    # And the enum MUST be the binding five-value enum
    nature = schema["properties"]["measurement_nature"]
    enum = nature.get("enum", [])
    assert enum == ["numeric", "ordinal", "nominal", "boolean", "composite"], \
        f"CR-MET-001: measurement_nature enum must be [numeric, ordinal, nominal, boolean, composite] (got {enum})"


def test_measurement_schema_present_with_required_references():
    """measurement.json MUST exist with applies_metric and measures_subject as required per ADR-MET-002."""
    schemas = _schemas()
    assert "measurement" in schemas, \
        "CR-MET-001: measurement.json schema missing (required by ADR-MET-002)"
    schema = schemas["measurement"]
    required = schema.get("required", [])
    assert "applies_metric" in required, \
        f"CR-MET-001: measurement.json must require 'applies_metric' (got {required})"
    assert "measures_subject" in required, \
        f"CR-MET-001: measurement.json must require 'measures_subject' (got {required})"


def test_measurement_observation_schema_present_with_required_references():
    """measurement-observation.json MUST exist with produced_by and value as required."""
    schemas = _schemas()
    assert "measurement-observation" in schemas, \
        "CR-MET-001: measurement-observation.json schema missing"
    schema = schemas["measurement-observation"]
    required = schema.get("required", [])
    assert "produced_by" in required, \
        f"CR-MET-001: measurement-observation.json must require 'produced_by' (got {required})"
    assert "value" in required, \
        f"CR-MET-001: measurement-observation.json must require 'value' (got {required})"


def test_metric_legacy_field_preserved_for_migration():
    """metric.json MUST preserve legacy_metric_type for one release cycle (deprecation window)."""
    schemas = _schemas()
    schema = schemas["metric"]
    props = schema.get("properties", {})
    assert "legacy_metric_type" in props, \
        "CR-MET-001: metric.json must preserve 'legacy_metric_type' for migration"
    enum = props["legacy_metric_type"].get("enum", [])
    assert "kpi" in enum and "performance" in enum, \
        f"CR-MET-001: legacy_metric_type enum must preserve the MECE taxonomy (got {enum})"
