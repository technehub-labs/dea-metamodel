"""CR-MET-010 Level 1: Metric structural conformance.

Per CR-MET-010 section 7, Level 1 (structural conformance) covers:
- Valid schema
- Required attributes
- Valid identity
- Valid references
- Valid data types
"""
import re

import yaml
from jsonschema import Draft7Validator

from conftest import BASE

FIXTURE = yaml.safe_load(
    (BASE / "tests" / "conformance" / "fixtures" / "metric_governance.yaml").read_text()
)

ID_PATTERN = re.compile(r"^dea:metric-[a-z][a-z0-9-]*$")
REF_PATTERN = re.compile(r"^dea:[a-z0-9-]+$")


def _metrics():
    return FIXTURE["metrics"]


def test_l1_every_metric_validates_against_schema():
    schema = yaml.safe_load("{}")  # placeholder to keep import symmetry
    schema = __import__("json").loads(
        (BASE / "schemas" / "entities" / "metric.json").read_text()
    )
    validator = Draft7Validator(schema)
    for m in _metrics():
        errs = list(validator.iter_errors(m))
        assert not errs, f"L1: {m['id']} fails schema validation: {[e.message for e in errs]}"


def test_l1_required_attributes_present():
    required = ["id", "name", "type", "version", "subject_concept", "measurement_nature"]
    for m in _metrics():
        for field in required:
            assert m.get(field), f"L1: {m['id']} missing required attribute {field}"


def test_l1_identity_pattern_valid():
    for m in _metrics():
        assert ID_PATTERN.match(m["id"]), f"L1: {m['id']} violates the canonical Metric id pattern"


def test_l1_identity_unique():
    ids = [m["id"] for m in _metrics()]
    assert len(ids) == len(set(ids)), f"L1: duplicate Metric identities {ids}"


def test_l1_type_constant_is_metric():
    for m in _metrics():
        assert m["type"] == "Metric", f"L1: {m['id']} declares type {m['type']}"


def test_l1_version_is_semver():
    for m in _metrics():
        assert re.match(r"^\d+\.\d+\.\d+$", m["version"]), \
            f"L1: {m['id']} version {m['version']} is not semver"


def test_l1_references_use_canonical_form():
    """Every *_ref value must use the canonical dea:<slug> identifier form (E004)."""
    for m in _metrics():
        gov = m.get("governance") or {}
        for key, value in gov.items():
            if key.endswith("_ref") and isinstance(value, str):
                assert REF_PATTERN.match(value), \
                    f"L1: {m['id']}.governance.{key}={value!r} is not a canonical identifier"
        if m.get("unit_ref"):
            assert REF_PATTERN.match(m["unit_ref"]), \
                f"L1: {m['id']}.unit_ref={m['unit_ref']!r} is not a canonical identifier"


def test_l1_data_types_correct():
    numeric_natures = {"numeric", "ordinal", "nominal", "boolean", "composite"}
    for m in _metrics():
        assert m["measurement_nature"] in numeric_natures, \
            f"L1: {m['id']} measurement_nature {m['measurement_nature']!r} not in binding enum"
        assert isinstance(m["scope_classification"], list), \
            f"L1: {m['id']} scope_classification must be an array"
        for dim in m.get("quality_dimensions", []):
            assert isinstance(dim["verdict"], str), \
                f"L1: {m['id']} quality verdict must be a string"


def test_l1_conformance_block_declares_three_levels():
    """CR-MET-010 section 7 requires exactly three conformance levels."""
    for m in _metrics():
        conf = m.get("conformance")
        assert conf, f"L1: {m['id']} must declare a conformance block"
        for level in ("structural", "semantic", "governance"):
            assert level in conf, f"L1: {m['id']} conformance block missing level {level!r}"


def test_l1_no_legacy_migration_fields_on_new_records():
    """The deprecated 7-value MECE taxonomy (CR-MET-001) must not appear on new records."""
    for m in _metrics():
        assert "legacy_metric_type" not in m, \
            f"L1: {m['id']} carries deprecated legacy_metric_type"