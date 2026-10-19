"""CR-MET-002: Metric classification + taxonomy (six axes, controlled vocabularies).

CR-MET-002 binding CR-MET-001 and ADR-MET-003.
"""
import json

import yaml

from conftest import BASE


def _vocab():
    return yaml.safe_load(
        (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
    )["classifications"]


def _vocab_values(key):
    """Return the set of allowed values for a Metric.<prop> controlled-vocabulary entry."""
    voc = _vocab()
    if key not in voc:
        return None
    return set(voc[key]["values"])


def _fixtures():
    return yaml.safe_load(
        (BASE / "tests" / "conformance" / "fixtures" / "classified_metrics.yaml").read_text()
    )["metrics"]


def _schemas():
    return {p.stem: json.loads(p.read_text())
            for p in sorted((BASE / "schemas" / "entities").glob("*.json"))}


def test_classification_version_bumped():
    """The classifications.yaml version MUST be at least 0.9.0 (CR-MET-002 binding).

    Version-agnostic by design: later CRs in the programme (CR-MET-004 and
    beyond) legitimately bump this version as they add controlled
    vocabularies. This test asserts the CR-MET-002 baseline, not an exact
    pin, so a later vocabulary addition does not break it.
    """
    voc = yaml.safe_load(
        (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
    )
    version = str(voc["version"])
    parts = version.split(".")
    assert len(parts) == 3, \
        f"CR-MET-002: classifications.yaml version must be semver (got {version!r})"
    assert tuple(int(p) for p in parts) >= (0, 9, 0), \
        f"CR-MET-002: classifications.yaml version must be at least 0.9.0 (got {version})"


def test_metric_subject_classification_vocabulary_present():
    """The Metric.subject_classification scheme MUST be present in the controlled vocabulary."""
    values = _vocab_values("Metric.subject_classification")
    assert values is not None, "CR-MET-002: Metric.subject_classification scheme missing"
    assert "dea:subject-financial" in values, "CR-MET-002: subject-financial missing"
    assert "dea:subject-customer" in values, "CR-MET-002: subject-customer missing"
    assert len(values) == 10, f"CR-MET-002: subject axis must have 10 values (got {len(values)})"


def test_metric_purpose_classification_vocabulary_present():
    """The Metric.purpose_classification scheme MUST be present with 10 values."""
    values = _vocab_values("Metric.purpose_classification")
    assert values is not None, "CR-MET-002: Metric.purpose_classification scheme missing"
    assert "performance_measurement" in values, "CR-MET-002: performance_measurement missing"
    assert "predictive_measurement" in values, "CR-MET-002: predictive_measurement missing"
    assert len(values) == 10, f"CR-MET-002: purpose axis must have 10 values (got {len(values)})"


def test_metric_orientation_classification_vocabulary_present():
    """The Metric.orientation_classification scheme MUST be present with 4 values."""
    values = _vocab_values("Metric.orientation_classification")
    assert values is not None, "CR-MET-002: Metric.orientation_classification scheme missing"
    assert values == {"leading", "lagging", "diagnostic", "concurrent"}, \
        f"CR-MET-002: orientation axis must be {{leading, lagging, diagnostic, concurrent}} (got {values})"


def test_metric_scope_classification_vocabulary_present():
    """The Metric.scope_classification scheme MUST be present with 10 values."""
    values = _vocab_values("Metric.scope_classification")
    assert values is not None, "CR-MET-002: Metric.scope_classification scheme missing"
    assert "process" in values, "CR-MET-002: process scope missing"
    assert "enterprise" in values, "CR-MET-002: enterprise scope missing"
    assert len(values) == 10, f"CR-MET-002: scope axis must have 10 values (got {len(values)})"


def test_metric_management_significance_vocabulary_present():
    """The Metric.management_significance scheme MUST be present with 6 values."""
    values = _vocab_values("Metric.management_significance")
    assert values is not None, "CR-MET-002: Metric.management_significance scheme missing"
    assert "kpi" in values, "CR-MET-002: kpi missing from management_significance"
    assert "kri" in values, "CR-MET-002: kri missing from management_significance"
    assert "kci" in values, "CR-MET-002: kci missing from management_significance"
    assert "sli" in values, "CR-MET-002: sli missing from management_significance"
    assert "general_metric" in values, "CR-MET-002: general_metric missing"
    assert "other_governed_designation" in values, "CR-MET-002: other_governed_designation missing"
    assert len(values) == 6, f"CR-MET-002: management_significance axis must have 6 values (got {len(values)})"


def test_indicator_kind_vocabulary_present():
    """The Indicator.kind scheme MUST be present with 4 values per ADR-MET-003 decision 6."""
    values = _vocab_values("Indicator.kind")
    assert values is not None, "CR-MET-002: Indicator.kind scheme missing"
    assert values == {"leading", "lagging", "diagnostic", "concurrent"}, \
        f"CR-MET-002: Indicator.kind must be {{leading, lagging, diagnostic, concurrent}} (got {values})"


def test_metric_schema_has_classification_fields():
    """The metric.json schema MUST declare all 5 new classification fields per CR-MET-002 §4.2."""
    schemas = _schemas()
    schema = schemas["metric"]
    props = schema.get("properties", {})
    for field in [
        "subject_classification",
        "purpose_classification",
        "orientation_classification",
        "scope_classification",
        "management_significance",
    ]:
        assert field in props, f"CR-MET-002: metric.json missing '{field}' field"
        # each MUST be an array with enum-typed items
        assert props[field].get("type") == "array", \
            f"CR-MET-002: '{field}' must be type=array (got {props[field].get('type')})"


def test_indicator_schema_has_kind_field():
    """The indicator.json schema MUST declare 'kind' per ADR-MET-003 decision 6."""
    schemas = _schemas()
    schema = schemas["indicator"]
    props = schema.get("properties", {})
    assert "kind" in props, "CR-MET-002: indicator.json missing 'kind' field"
    enum = props["kind"].get("enum", [])
    assert enum == ["leading", "lagging", "diagnostic", "concurrent"], \
        f"CR-MET-002: indicator.kind enum must be [leading, lagging, diagnostic, concurrent] (got {enum})"


def test_indicator_kind_matches_metric_orientation():
    """Indicator.kind enum MUST equal Metric.orientation_classification enum (cross-check)."""
    schemas = _schemas()
    indicator_kind = set(schemas["indicator"]["properties"]["kind"]["enum"])
    metric_orientation = set(
        schemas["metric"]["properties"]["orientation_classification"]["items"]["enum"]
    )
    assert indicator_kind == metric_orientation, \
        f"CR-MET-002: Indicator.kind ({indicator_kind}) must equal Metric.orientation_classification ({metric_orientation})"


def test_all_six_fixtures_have_subject_classification():
    """Every representative Metric fixture MUST have a non-empty subject_classification."""
    fixtures = _fixtures()
    assert len(fixtures) == 6, f"CR-MET-002: must have 6 representative fixtures (got {len(fixtures)})"
    for fx in fixtures:
        subjects = fx.get("subject_classification", [])
        assert len(subjects) >= 1, \
            f"CR-MET-002: {fx['id']} must have at least one subject_classification"
        for s in subjects:
            assert s.startswith("dea:subject-"), \
                f"CR-MET-002: {fx['id']} subject '{s}' must be a dea:subject-* reference"


def test_all_six_fixtures_have_valid_measurement_nature():
    """Every fixture's measurement_nature MUST be in the controlled vocabulary (CR-MET-001)."""
    natures = _vocab_values("Metric.measurement_nature")
    for fx in _fixtures():
        assert fx.get("measurement_nature") in natures, \
            f"CR-MET-002: {fx['id']} measurement_nature '{fx.get('measurement_nature')}' not in vocabulary"


def test_all_six_fixtures_have_valid_purpose_orientation_scope_management():
    """Every fixture's classification values MUST be in their respective controlled vocabularies."""
    purposes = _vocab_values("Metric.purpose_classification")
    orientations = _vocab_values("Metric.orientation_classification")
    scopes = _vocab_values("Metric.scope_classification")
    mgmts = _vocab_values("Metric.management_significance")
    for fx in _fixtures():
        for p in fx.get("purpose_classification", []):
            assert p in purposes, \
                f"CR-MET-002: {fx['id']} purpose '{p}' not in vocabulary"
        for o in fx.get("orientation_classification", []):
            assert o in orientations, \
                f"CR-MET-002: {fx['id']} orientation '{o}' not in vocabulary"
        for s in fx.get("scope_classification", []):
            assert s in scopes, \
                f"CR-MET-002: {fx['id']} scope '{s}' not in vocabulary"
        for m in fx.get("management_significance", []):
            assert m in mgmts, \
                f"CR-MET-002: {fx['id']} management_significance '{m}' not in vocabulary"


def test_mean_time_to_recovery_has_multiple_subjects():
    """The Mean Time to Recovery fixture MUST have multiple subject classifications
    (canonical example of 'MAY have multiple subject classifications' rule)."""
    for fx in _fixtures():
        if fx["id"] == "dea:metric-mean-time-to-recovery":
            subjects = fx.get("subject_classification", [])
            assert len(subjects) >= 2, \
                f"CR-MET-002: MTTR fixture must have multiple subjects (got {subjects})"
            assert "dea:subject-technology" in subjects
            assert "dea:subject-operational" in subjects
            return
    raise AssertionError("CR-MET-002: MTTR fixture missing from classified_metrics.yaml")


def test_classification_does_not_alter_identity():
    """Classification fields MUST NOT appear in any entity's identity-related required set.
    The id field is the binding identity; classification fields are optional.
    """
    schemas = _schemas()
    schema = schemas["metric"]
    required = schema.get("required", [])
    classification_fields = {
        "subject_classification",
        "purpose_classification",
        "orientation_classification",
        "scope_classification",
        "management_significance",
    }
    for field in classification_fields:
        assert field not in required, \
            f"CR-MET-002: '{field}' must NOT be required (classification MUST NOT alter identity; got in required={required})"
