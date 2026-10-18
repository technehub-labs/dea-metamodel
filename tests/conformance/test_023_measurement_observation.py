"""CR-MET-003: Measurement and Observation full attribute sets + 3 new relationships.

CR-MET-003 binding CR-MET-001 / CR-MET-002 and ADR-MET-002.
"""
import json
import re

import yaml

from conftest import BASE

ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*:[a-z0-9-]+(@\\d+\\.\\d+\\.\\d+)?$")


def _relationships():
    return [r for r in yaml.safe_load(
        (BASE / "metamodel" / "dea-metamodel.yaml").read_text()
    ).get("relationships", [])
        if isinstance(r, dict) and r.get("id", "").startswith("dea:")]


def _registry_relationships():
    return yaml.safe_load(
        (BASE / "metamodel" / "registry" / "relationships.yaml").read_text()
    )["relationships"]


def _fixtures():
    return yaml.safe_load(
        (BASE / "tests" / "conformance" / "fixtures" / "measurement_observations.yaml").read_text()
    )


def _schemas():
    return {p.stem: json.loads(p.read_text())
            for p in sorted((BASE / "schemas" / "entities").glob("*.json"))}


def test_measurement_schema_full_attribute_set():
    """measurement.json MUST declare the binding attribute set per user-supplied CR-MET-003 §4."""
    schemas = _schemas()
    schema = schemas["measurement"]
    required = schema.get("required", [])
    for field in [
        "applies_metric",
        "measures_subject",
        "measurement_method",
        "measurement_time",
        "measurement_status",
    ]:
        assert field in required, \
            f"CR-MET-003: measurement.json must require '{field}' (got {required})"
    props = schema.get("properties", {})
    for field in [
        "reporting_period_start", "reporting_period_end",
        "measurement_source", "configuration_reference",
        "evidence_reference", "context",
    ]:
        assert field in props, \
            f"CR-MET-003: measurement.json must declare '{field}' (got {sorted(props.keys())})"


def test_measurement_observation_schema_full_attribute_set():
    """measurement-observation.json MUST declare the binding attribute set per user-supplied CR-MET-003 §5."""
    schemas = _schemas()
    schema = schemas["measurement-observation"]
    required = schema.get("required", [])
    for field in [
        "produced_by", "value", "observed_at", "observation_status",
    ]:
        assert field in required, \
            f"CR-MET-003: measurement-observation.json must require '{field}' (got {required})"
    props = schema.get("properties", {})
    for field in [
        "valid_from", "valid_to",
        "reporting_period_start", "reporting_period_end",
        "observation_quality", "provenance_reference", "evidence_reference",
    ]:
        assert field in props, \
            f"CR-MET-003: measurement-observation.json must declare '{field}' (got {sorted(props.keys())})"


def test_measurement_status_enum_has_10_values():
    """measurement.json.measurement_status MUST be the binding 10-value enum (CR-MET-003 §5)."""
    schemas = _schemas()
    schema = schemas["measurement"]
    enum = schema["properties"]["measurement_status"]["enum"]
    expected = {
        "planned", "initiated", "in_progress", "pending_validation",
        "validated", "completed", "failed", "cancelled",
        "rejected", "superseded",
    }
    assert set(enum) == expected, \
        f"CR-MET-003: measurement_status enum must be {sorted(expected)} (got {sorted(enum)})"


def test_observation_status_enum_has_4_values():
    """measurement-observation.json.observation_status MUST be the 4-value enum (CR-MET-003 §5)."""
    schemas = _schemas()
    schema = schemas["measurement-observation"]
    enum = schema["properties"]["observation_status"]["enum"]
    expected = {"proposed", "active", "superseded", "retired"}
    assert set(enum) == expected, \
        f"CR-MET-003: observation_status enum must be {sorted(expected)} (got {sorted(enum)})"


def test_dea_produces_extended_with_measurement():
    """dea:produces source list MUST include dea:Measurement; target list MUST include dea:MeasurementObservation."""
    registry = _registry_relationships()
    produces = next((r for r in registry if r["id"] == "dea:produces"), None)
    assert produces is not None, "CR-MET-003: dea:produces missing from registry"
    assert "dea:Measurement" in produces["source"], \
        f"CR-MET-003: dea:produces source list must include dea:Measurement (got {produces['source']})"
    assert "dea:MeasurementObservation" in produces["target"], \
        f"CR-MET-003: dea:produces target list must include dea:MeasurementObservation (got {produces['target']})"


def test_dea_applies_metric_in_registry():
    """dea:applies-metric MUST be in the canonical source and registry with cardinality 1:1 per ADR-MET-002 decision 6."""
    canonical = _relationships()
    rel = next((r for r in canonical if r["id"] == "dea:applies-metric"), None)
    assert rel is not None, "CR-MET-003: dea:applies-metric missing from canonical source"
    assert rel["source"]["types"] == ["dea:Measurement"], \
        f"CR-MET-003: dea:applies-metric source must be [dea:Measurement] (got {rel['source']['types']})"
    assert rel["target"]["types"] == ["dea:PerformanceMetric"], \
        f"CR-MET-003: dea:applies-metric target must be [dea:PerformanceMetric] (got {rel['target']['types']})"
    assert str(rel["cardinality"]["source"]) == "1", \
        f"CR-MET-003: dea:applies-metric source cardinality must be '1' (got {rel['cardinality']['source']!r})"
    assert str(rel["cardinality"]["target"]) == "1", \
        f"CR-MET-003: dea:applies-metric target cardinality must be '1' (got {rel['cardinality']['target']!r})"


def test_dea_measures_subject_in_registry():
    """dea:measures-subject MUST be in the canonical source and registry with cardinality 1:1 per ADR-MET-002 decision 7."""
    canonical = _relationships()
    rel = next((r for r in canonical if r["id"] == "dea:measures-subject"), None)
    assert rel is not None, "CR-MET-003: dea:measures-subject missing from canonical source"
    assert rel["source"]["types"] == ["dea:Measurement"], \
        f"CR-MET-003: dea:measures-subject source must be [dea:Measurement] (got {rel['source']['types']})"
    target = set(rel["target"]["types"])
    expected_7 = {
        "dea:AIMLModel", "dea:ApplicationComponent", "dea:BusinessCapability",
        "dea:BusinessProcess", "dea:BusinessService", "dea:Outcome",
        "dea:StrategicObjective",
    }
    assert target == expected_7, \
        f"CR-MET-003: dea:measures-subject target must be the 7-type source list (got {sorted(target)})"
    assert str(rel["cardinality"]["source"]) == "1"
    assert str(rel["cardinality"]["target"]) == "1"


def test_all_measurement_fixtures_have_required_fields():
    """Every Measurement fixture MUST have applies_metric, measures_subject, measurement_method, measurement_time, measurement_status."""
    fx = _fixtures()
    for m in fx["measurements"]:
        for field in [
            "applies_metric", "measures_subject",
            "measurement_method", "measurement_time", "measurement_status",
        ]:
            assert m.get(field), \
                f"CR-MET-003: measurement fixture {m['id']} missing required field '{field}'"


def test_all_observation_fixtures_have_required_fields():
    """Every MeasurementObservation fixture MUST have produced_by, value, observed_at, observation_status."""
    fx = _fixtures()
    for o in fx["measurement_observations"]:
        for field in [
            "produced_by", "value", "observed_at", "observation_status",
        ]:
            assert o.get(field) is not None, \
                f"CR-MET-003: observation fixture {o['id']} missing required field '{field}'"


def test_numeric_observations_have_numeric_values():
    """Observations with a numeric value type MUST have value typed as a number (CR-MET-003 §8 + CR-MET-001 binding)."""
    fx = _fixtures()
    numeric_value_observations = [
        "dea:measurement-observation-2026-q3-customer-retention",  # 0.924 ratio
        "dea:measurement-observation-2026-q3-employee-engagement-1",  # 4.2 ordinal-1-5
        "dea:measurement-observation-2026-q3-employee-engagement-2",  # 3.8 ordinal-1-5
        "dea:measurement-observation-2026-q3-mttr",  # 142 minutes
        "dea:measurement-observation-2026-q3-mttr-superseded",  # 158 minutes
        "dea:measurement-observation-2026-q3-data-completeness",  # 0.987 ratio
    ]
    by_id = {o["id"]: o for o in fx["measurement_observations"]}
    for oid in numeric_value_observations:
        o = by_id[oid]
        assert isinstance(o["value"], (int, float)), \
            f"CR-MET-003: {oid} value must be numeric (got {type(o['value']).__name__} {o['value']!r})"


def test_failed_measurement_produces_no_observations():
    """The failed-Measurement fixture MUST have no corresponding produced_by reference in observations (canonical MAY-produce-zero case)."""
    fx = _fixtures()
    failed_id = "dea:measurement-2026-q3-data-completeness-failed"
    for o in fx["measurement_observations"]:
        assert o["produced_by"] != failed_id, \
            f"CR-MET-003: observation {o['id']} references failed measurement {failed_id} " \
            "(MAY produce zero observations rule violated)"


def test_superseded_observation_status():
    """The superseded observation fixture MUST have observation_status: superseded."""
    fx = _fixtures()
    superseded = next(
        (o for o in fx["measurement_observations"] if o["id"] == "dea:measurement-observation-2026-q3-mttr-superseded"),
        None,
    )
    assert superseded is not None, "CR-MET-003: superseded observation fixture missing"
    assert superseded["observation_status"] == "superseded", \
        f"CR-MET-003: superseded observation status must be 'superseded' (got {superseded['observation_status']!r})"


def test_egv004_identity_pattern():
    """Every fixture id MUST match the canonical id pattern (EGV-004 binding)."""
    fx = _fixtures()
    for m in fx["measurements"]:
        assert ID_PATTERN.match(m["id"]), \
            f"CR-MET-003: measurement fixture id {m['id']!r} does not match id pattern"
    for o in fx["measurement_observations"]:
        assert ID_PATTERN.match(o["id"]), \
            f"CR-MET-003: observation fixture id {o['id']!r} does not match id pattern"


def test_applies_metric_includes_semver():
    """applies_metric references SHOULD include a semantic version (CR-MET-003 §4)."""
    fx = _fixtures()
    for m in fx["measurements"]:
        am = m["applies_metric"]
        assert "@" in am, \
            f"CR-MET-003: measurement {m['id']} applies_metric {am!r} should include a semantic version (e.g. @1.0.0)"


def test_observation_observation_status_enum():
    """observation_status MUST be one of the 4 binding values."""
    fx = _fixtures()
    allowed = {"proposed", "active", "superseded", "retired"}
    for o in fx["measurement_observations"]:
        assert o["observation_status"] in allowed, \
            f"CR-MET-003: observation {o['id']} status {o['observation_status']!r} not in {sorted(allowed)}"
