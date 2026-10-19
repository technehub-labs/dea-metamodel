"""CR-MET-005: Measurement Units, Dimensionality, Formula and Aggregation Semantics.

CR-MET-005 binding CR-MET-001 / CR-MET-003 / CR-MET-004 and ADR-MET-002.
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
        (BASE / "tests" / "conformance" / "fixtures" / "measurement_semantics.yaml").read_text()
    )


def test_unit_schema_has_dimensionality_and_conversion_fields():
    """unit.json schema MUST declare dimensionality, canonical_symbol, ucum_code, conversion_to_base_factor, conversion_to_base_offset, composite_dimensions (CR-MET-005 section 4.1)."""
    schema = _schemas()["unit"]
    props = schema.get("properties", {})
    for field in [
        "dimensionality",
        "canonical_symbol",
        "ucum_code",
        "conversion_to_base_factor",
        "conversion_to_base_offset",
        "composite_dimensions",
    ]:
        assert field in props, \
            f"CR-MET-005: unit.json must declare '{field}' (got {sorted(props.keys())})"
    # the existing symbol and quantity_kind are preserved
    assert "symbol" in props
    assert "quantity_kind" in props


def test_scale_schema_has_extended_scale_type_enum():
    """scale.json schema MUST extend scale_type to 6 values (CR-MET-005 section 3.2)."""
    schema = _schemas()["scale"]
    enum = schema["properties"]["scale_type"]["enum"]
    expected = {"nominal", "ordinal", "interval", "ratio", "categorical", "boolean"}
    assert set(enum) == expected, \
        f"CR-MET-005: scale_type enum must be {sorted(expected)} (got {sorted(enum)})"


def test_scale_schema_has_scale_values_and_ordered():
    """scale.json schema MUST declare scale_values and ordered."""
    schema = _schemas()["scale"]
    props = schema.get("properties", {})
    for field in ["scale_values", "ordered"]:
        assert field in props, \
            f"CR-MET-005: scale.json must declare '{field}' (got {sorted(props.keys())})"


def test_aggregation_rule_schema_has_operator_weight_basis_unit_semantics():
    """aggregation-rule.json schema MUST declare operator (11-value), weight_basis, unit_semantics (CR-MET-005 section 4.3)."""
    schema = _schemas()["aggregation-rule"]
    props = schema.get("properties", {})
    for field in ["operator", "weight_basis", "unit_semantics"]:
        assert field in props, \
            f"CR-MET-005: aggregation-rule.json must declare '{field}' (got {sorted(props.keys())})"
    enum = props["operator"]["enum"]
    assert len(enum) == 11, \
        f"CR-MET-005: operator enum must have 11 values (got {len(enum)})"
    expected = {"SUM", "COUNT", "MIN", "MAX", "MEAN", "WEIGHTED_MEAN",
                "MEDIAN", "PERCENTILE", "RATE", "RATIO", "DISTINCT_COUNT"}
    assert set(enum) == expected, \
        f"CR-MET-005: operator enum must be {sorted(expected)} (got {sorted(enum)})"
    # the existing rule_kind, weights, and expression properties are preserved
    for preserved in ["rule_kind", "weights", "expression"]:
        assert preserved in props, \
            f"CR-MET-005: aggregation-rule.json must preserve '{preserved}'"


def test_metric_schema_has_formula_composite_precision_rounding_null_fields():
    """metric.json schema MUST declare formula_definition, composite_definition, precision, decimal_scale, rounding_rule, null_value_semantics (CR-MET-005 section 4.4)."""
    schema = _schemas()["metric"]
    props = schema.get("properties", {})
    for field in [
        "formula_definition",
        "composite_definition",
        "precision",
        "decimal_scale",
        "rounding_rule",
        "null_value_semantics",
    ]:
        assert field in props, \
            f"CR-MET-005: metric.json must declare '{field}' (got {sorted(props.keys())})"
    # the existing calculation_definition string is preserved
    assert "calculation_definition" in props


def test_observation_schema_has_uncertainty_comparability_precision():
    """measurement-observation.json schema MUST declare uncertainty_reference, comparability_requirements, precision."""
    schema = _schemas()["measurement-observation"]
    props = schema.get("properties", {})
    for field in ["uncertainty_reference", "comparability_requirements", "precision"]:
        assert field in props, \
            f"CR-MET-005: measurement-observation.json must declare '{field}' (got {sorted(props.keys())})"


def test_unit_dimensionality_controlled_vocabulary():
    """Unit.dimensionality MUST be present with 11 binding values (CR-MET-005 section 3.1)."""
    values = _vocab_values("Unit.dimensionality")
    assert values is not None, "CR-MET-005: Unit.dimensionality vocabulary missing"
    expected = {"time", "length", "mass", "currency", "count", "temperature",
                "information_quantity", "rate", "ratio", "dimensionless_index", "composite"}
    assert values == expected, \
        f"CR-MET-005: Unit.dimensionality must be {sorted(expected)} (got {sorted(values)})"


def test_scale_scale_type_controlled_vocabulary():
    """Scale.scale_type MUST be present with 6 binding values (CR-MET-005 section 3.2)."""
    values = _vocab_values("Scale.scale_type")
    assert values is not None, "CR-MET-005: Scale.scale_type vocabulary missing"
    expected = {"nominal", "ordinal", "interval", "ratio", "categorical", "boolean"}
    assert values == expected, \
        f"CR-MET-005: Scale.scale_type must be {sorted(expected)} (got {sorted(values)})"


def test_aggregation_rule_operator_controlled_vocabulary():
    """AggregationRule.operator MUST be present with 11 binding values (CR-MET-005 section 3.3)."""
    values = _vocab_values("AggregationRule.operator")
    assert values is not None, "CR-MET-005: AggregationRule.operator vocabulary missing"
    expected = {"SUM", "COUNT", "MIN", "MAX", "MEAN", "WEIGHTED_MEAN",
                "MEDIAN", "PERCENTILE", "RATE", "RATIO", "DISTINCT_COUNT"}
    assert values == expected, \
        f"CR-MET-005: AggregationRule.operator must be {sorted(expected)} (got {sorted(values)})"


def test_metric_rounding_rule_controlled_vocabulary():
    """Metric.rounding_rule MUST be present with 4 binding values (CR-MET-005 section 3.6)."""
    values = _vocab_values("Metric.rounding_rule")
    assert values is not None, "CR-MET-005: Metric.rounding_rule vocabulary missing"
    expected = {"half_up", "half_even", "half_down", "truncate"}
    assert values == expected, \
        f"CR-MET-005: Metric.rounding_rule must be {sorted(expected)} (got {sorted(values)})"


def test_all_unit_fixtures_have_valid_dimensionality():
    """Every Unit fixture MUST have a valid dimensionality value in the controlled vocabulary."""
    values = _vocab_values("Unit.dimensionality")
    fx = _fixtures()
    for u in fx["units"]:
        assert u.get("dimensionality") in values, \
            f"CR-MET-005: Unit {u['id']} dimensionality {u.get('dimensionality')!r} not in vocabulary"


def test_all_scale_fixtures_have_valid_scale_type():
    """Every Scale fixture MUST have a valid scale_type value."""
    values = _vocab_values("Scale.scale_type")
    fx = _fixtures()
    for s in fx["scales"]:
        assert s.get("scale_type") in values, \
            f"CR-MET-005: Scale {s['id']} scale_type {s.get('scale_type')!r} not in vocabulary"
    # the boolean fixture MUST have exactly two scale_values
    for s in fx["scales"]:
        if s.get("scale_type") == "boolean":
            assert len(s.get("scale_values", [])) == 2, \
                f"CR-MET-005: Scale {s['id']} (boolean) must have exactly 2 scale_values"


def test_all_aggregation_rule_fixtures_have_valid_operator():
    """Every AggregationRule fixture MUST have a valid operator value."""
    values = _vocab_values("AggregationRule.operator")
    fx = _fixtures()
    for r in fx["aggregation_rules"]:
        assert r.get("operator") in values, \
            f"CR-MET-005: AggregationRule {r['id']} operator {r.get('operator')!r} not in vocabulary"


def test_weighted_mean_aggregation_rule_has_weight_basis():
    """WEIGHTED_MEAN operator MUST have a non-empty weight_basis (CR-MET-005 section 3.3 invariant)."""
    fx = _fixtures()
    for r in fx["aggregation_rules"]:
        if r.get("operator") == "WEIGHTED_MEAN":
            assert r.get("weight_basis"), \
                f"CR-MET-005: AggregationRule {r['id']} with WEIGHTED_MEAN must declare weight_basis"


def test_formula_definition_fixture_has_valid_unit_semantics():
    """The formula_definition fixture's unit_semantics MUST declare output_unit."""
    fx = _fixtures()
    mttr = next((m for m in fx["metrics"] if m["id"] == "dea:metric-mttr"), None)
    assert mttr is not None, "CR-MET-005: MTTR metric fixture missing"
    fd = mttr.get("formula_definition")
    assert fd, "CR-MET-005: MTTR metric must carry formula_definition"
    assert fd.get("unit_semantics"), \
        "CR-MET-005: formula_definition must declare unit_semantics"
    assert fd["unit_semantics"].get("output_unit"), \
        "CR-MET-005: formula_definition.unit_semantics must declare output_unit"


def test_composite_definition_required_iff_measurement_nature_composite():
    """CR-MET-005 cross-field invariant: composite_definition MUST be present iff measurement_nature=composite."""
    fx = _fixtures()
    for m in fx["metrics"]:
        is_composite = m.get("measurement_nature") == "composite"
        has_composite_def = "composite_definition" in m
        if is_composite:
            assert has_composite_def, \
                f"CR-MET-005: Metric {m['id']} has measurement_nature=composite but lacks composite_definition"
        else:
            assert not has_composite_def, \
                f"CR-MET-005: Metric {m['id']} has composite_definition but measurement_nature={m.get('measurement_nature')!r} != composite"


def test_composite_definition_weight_sums_to_at_most_one():
    """CR-MET-005: composite Metric component weights MUST sum to <= 1.0 (convention; informational)."""
    fx = _fixtures()
    for m in fx["metrics"]:
        cd = m.get("composite_definition")
        if not cd:
            continue
        weights = [c["weight"] for c in cd.get("component_metrics", [])]
        if weights:
            assert sum(weights) <= 1.0 + 1e-9, \
                f"CR-MET-005: Metric {m['id']} component weights sum to {sum(weights)} > 1.0"


def test_no_new_entity_introduced():
    """CR-MET-005 MUST NOT introduce a new entity (ADR-013 anti-accumulation; audit-then-specifies)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    # CR-MET-004 baseline: 153 entities, 107 relationships. CR-MET-005 adds neither.
    assert len(normative["entities"]) == 153, \
        f"CR-MET-005: entity count must remain 153 (got {len(normative['entities'])})"
    assert len(normative["relationships"]) == 107, \
        f"CR-MET-005: relationship count must remain 107 (got {len(normative['relationships'])})"
    # the existing entities we depend on must remain present
    entity_ids = {e["id"] for e in normative["entities"]}
    for required in ("dea:Unit", "dea:Scale", "dea:AggregationRule",
                     "dea:PerformanceMetric", "dea:Measurement", "dea:MeasurementObservation"):
        assert required in entity_ids, \
            f"CR-MET-005: required entity {required} missing from registry"


def test_stream_a_closed():
    """All 5 Stream A canonical-source-touching CRs are sealed (CR-MET-001..005).

    CR-MET-000 is the foundation CR (already merged; not in this set).
    CR-MET-006..012 are Stream B/C and remain untracked in the working tree
    (they will land in their own future PRs per cardinal R2).
    """
    cr_files = {p.name for p in (BASE / "change-requests").glob("CR-MET-*.md")}
    expected = {"CR-MET-000.md", "CR-MET-001.md", "CR-MET-002.md",
                "CR-MET-003.md", "CR-MET-004.md", "CR-MET-005.md"}
    missing = expected - cr_files
    assert not missing, \
        f"CR-MET-005: Stream A not closed; missing {sorted(missing)}"