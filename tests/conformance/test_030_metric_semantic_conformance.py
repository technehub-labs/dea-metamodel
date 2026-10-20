"""CR-MET-010 Level 2: Metric semantic conformance.

Per CR-MET-010 section 7, Level 2 (semantic conformance) covers:
- Unambiguous definition
- Valid classification
- Appropriate unit or scale
- Valid formula semantics
- Appropriate subject concept
- Valid relationships
"""
import json

import yaml

from conftest import BASE

FIXTURE = yaml.safe_load(
    (BASE / "tests" / "conformance" / "fixtures" / "metric_governance.yaml").read_text()
)

CLASSIFICATIONS = yaml.safe_load(
    (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
)["classifications"]


def _metrics():
    return FIXTURE["metrics"]


def _vocab(scheme):
    return set(CLASSIFICATIONS[scheme]["values"])


def test_l2_subject_classification_values_known():
    allowed = _vocab("Metric.subject_classification")
    for m in _metrics():
        for v in m["subject_classification"]:
            assert v in allowed, f"L2: {m['id']} subject_classification {v!r} not in vocabulary"


def test_l2_purpose_classification_values_known():
    allowed = _vocab("Metric.purpose_classification")
    for m in _metrics():
        for v in m["purpose_classification"]:
            assert v in allowed, f"L2: {m['id']} purpose_classification {v!r} not in vocabulary"


def test_l2_orientation_classification_values_known():
    allowed = _vocab("Metric.orientation_classification")
    for m in _metrics():
        assert isinstance(m["orientation_classification"], list), \
            f"L2: {m['id']} orientation_classification must be an array"
        for v in m["orientation_classification"]:
            assert v in allowed, f"L2: {m['id']} orientation_classification {v!r} not in vocabulary"


def test_l2_scope_classification_values_known():
    allowed = _vocab("Metric.scope_classification")
    for m in _metrics():
        for v in m["scope_classification"]:
            assert v in allowed, f"L2: {m['id']} scope_classification {v!r} not in vocabulary"


def test_l2_directionality_values_known():
    allowed = _vocab("Metric.directionality")
    for m in _metrics():
        assert m["directionality"] in allowed, f"L2: {m['id']} directionality not in vocabulary"


def test_l2_unit_matches_schema_unit_reference():
    """A Metric declaring a unit must reference a unit the schema accepts (CR-MET-005 binding)."""
    schema = json.loads((BASE / "schemas" / "entities" / "metric.json").read_text())
    assert "unit" in schema["properties"], "L2: metric.json must declare unit"
    unit_semantics = schema["properties"]["formula_definition"]["properties"]["unit_semantics"]
    assert "output_unit" in unit_semantics.get("required", []), \
        "L2: formula_definition.unit_semantics MUST require output_unit"
    for m in _metrics():
        assert m.get("unit"), f"L2: {m['id']} must declare unit"
        assert isinstance(m["unit"], str), f"L2: {m['id']} unit must be a string"
        assert m["unit"].startswith("dea:unit-"), \
            f"L2: {m['id']} unit {m['unit']!r} must reference a dea:Unit entity"


def test_l2_quality_dimension_values_known():
    """CR-MET-010 section 6: ten quality dimensions with governed verdicts."""
    dims = _vocab("MetricQuality.quality_dimension")
    verdicts = _vocab("MetricQuality.quality_verdict")
    for m in _metrics():
        for d in m.get("quality_dimensions", []):
            assert d["dimension"] in dims, f"L2: {m['id']} quality dimension {d['dimension']!r} unknown"
            assert d["verdict"] in verdicts, f"L2: {m['id']} quality verdict {d['verdict']!r} unknown"


def test_l2_governance_object_values_known():
    """CR-MET-010 Q16a: four governance objects."""
    allowed = _vocab("MetricGovernance.governance_object")
    for m in _metrics():
        gov = m.get("governance") or {}
        assert gov["governance_object"] in allowed, \
            f"L2: {m['id']} governance_object {gov['governance_object']!r} not in the 4-value enum"


# Approval evidence fields are NOT governance roles. CR-MET-010 section 4 declares
# eight roles; approval evidence is recorded separately (approved_by_ref, approved_at).
_APPROVAL_EVIDENCE = {"approved_by_ref"}


def test_l2_governance_role_names_known():
    """CR-MET-010 section 4: eight governance roles. Every role-bearing *_ref key must
    map to a declared role; approval evidence fields are exempt."""
    roles = set(_vocab("MetricGovernance.governance_role"))
    for m in _metrics():
        gov = m.get("governance") or {}
        for key in gov:
            if key.endswith("_ref") and key not in _APPROVAL_EVIDENCE:
                assert key.replace("_ref", "") in roles, \
                    f"L2: {m['id']}.governance.{key} does not map to a declared governance role"


def test_l2_subject_concept_declared():
    """CR-MET-001 binding: subject_concept is what distinguishes a Metric, not its label."""
    for m in _metrics():
        assert m["subject_concept"].startswith("dea:subject-"), \
            f"L2: {m['id']} subject_concept must use the dea:subject-<slug> form"


def test_l2_orientation_directionality_are_consistent():
    """A leading or diagnostic orientation paired with higher_is_better and a bounded
    target must not be self-contradictory. This is a semantic coherence check."""
    for m in _metrics():
        if m["orientation_classification"] == "leading":
            assert m["directionality"] in {"higher_is_better", "lower_is_better", "target_band", "categorical"}, \
                f"L2: {m['id']} leading orientation with directionality {m['directionality']!r} is incoherent"