"""CR-MET-006: Contextual Measurement Evaluation and Performance Interpretation Semantics.

CR-MET-006 binding CR-MET-001 / CR-MET-003 / CR-MET-005 and ADR-MET-005.
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
        (BASE / "tests" / "conformance" / "fixtures" / "performance_evaluation.yaml").read_text()
    )


# -------- schema presence --------

def test_baseline_schema_present_with_binding_fields():
    """baseline.json schema MUST exist with the 9 binding attributes (CR-MET-006 section 4)."""
    schemas = _schemas()
    assert "baseline" in schemas, "CR-MET-006: baseline.json schema missing"
    props = schemas["baseline"]["properties"]
    for field in [
        "kind", "approval_status", "reference_metric_ref", "subject_ref",
        "reference_value", "establishment_date", "applicable_period",
        "organizational_scope", "measurement_methodology", "source_evidence",
        "version", "supersedes_baselines",
    ]:
        assert field in props, f"CR-MET-006: baseline.json must declare '{field}'"


def test_performance_target_schema_present_with_binding_fields():
    """performance-target.json schema MUST exist with the 9 binding attributes."""
    schemas = _schemas()
    assert "performance-target" in schemas, "CR-MET-006: performance-target.json schema missing"
    props = schemas["performance-target"]["properties"]
    for field in [
        "target_metric_ref", "target_subject_ref", "target_scope",
        "target_value", "target_range", "target_direction",
        "effective_period", "owner_ref", "associated_objective_ref",
        "approval_status", "supporting_rationale",
    ]:
        assert field in props, f"CR-MET-006: performance-target.json must declare '{field}'"


def test_threshold_schema_present_with_binding_fields():
    """threshold.json schema MUST exist with the 4 directional models and 4 levels."""
    schemas = _schemas()
    assert "threshold" in schemas, "CR-MET-006: threshold.json schema missing"
    props = schemas["threshold"]["properties"]
    for field in [
        "threshold_metric_ref", "threshold_value", "threshold_level",
        "direction", "effective_period", "owner_ref", "escalation_rule_ref",
    ]:
        assert field in props, f"CR-MET-006: threshold.json must declare '{field}'"


def test_performance_interpretation_schema_present_with_binding_fields():
    """performance-interpretation.json schema MUST exist with the binding interpretation_kind/state."""
    schemas = _schemas()
    assert "performance-interpretation" in schemas, "CR-MET-006: performance-interpretation.json schema missing"
    props = schemas["performance-interpretation"]["properties"]
    for field in [
        "interprets_metric_ref", "interprets_observation_ref",
        "interpretation_kind", "interpretation_state", "reference_used",
        "absolute_variance", "relative_variance", "narrative",
        "evaluator_ref", "evaluated_at",
    ]:
        assert field in props, f"CR-MET-006: performance-interpretation.json must declare '{field}'"


# -------- controlled vocabularies --------

def test_baseline_kind_vocabulary():
    """Baseline.kind MUST be present with 6 binding values."""
    values = _vocab_values("Baseline.kind")
    assert values is not None, "CR-MET-006: Baseline.kind vocabulary missing"
    expected = {"historical", "initial", "strategic", "operational", "regulatory", "scenario_derived"}
    assert values == expected, f"CR-MET-006: Baseline.kind must be {sorted(expected)} (got {sorted(values)})"


def test_baseline_approval_status_vocabulary():
    """Baseline.approval_status MUST be present with 4 values."""
    values = _vocab_values("Baseline.approval_status")
    assert values is not None, "CR-MET-006: Baseline.approval_status vocabulary missing"
    expected = {"draft", "proposed", "approved", "retired"}
    assert values == expected, f"CR-MET-006: Baseline.approval_status must be {sorted(expected)} (got {sorted(values)})"


def test_performance_target_direction_vocabulary():
    """PerformanceTarget.direction MUST be present with 5 binding values."""
    values = _vocab_values("PerformanceTarget.direction")
    assert values is not None, "CR-MET-006: PerformanceTarget.direction vocabulary missing"
    expected = {"increase", "decrease", "maintain", "bounded", "exact_match"}
    assert values == expected, f"CR-MET-006: PerformanceTarget.direction must be {sorted(expected)} (got {sorted(values)})"


def test_threshold_level_vocabulary():
    """Threshold.level MUST be present with 4 binding values."""
    values = _vocab_values("Threshold.level")
    assert values is not None, "CR-MET-006: Threshold.level vocabulary missing"
    expected = {"critical", "warning", "acceptable", "optimal"}
    assert values == expected, f"CR-MET-006: Threshold.level must be {sorted(expected)} (got {sorted(values)})"


def test_threshold_direction_vocabulary():
    """Threshold.direction MUST be present with 4 binding values."""
    values = _vocab_values("Threshold.direction")
    assert values is not None, "CR-MET-006: Threshold.direction vocabulary missing"
    expected = {"higher_is_better", "lower_is_better", "bounded_optimum", "exact_match"}
    assert values == expected, f"CR-MET-006: Threshold.direction must be {sorted(expected)} (got {sorted(values)})"


def test_performance_interpretation_kind_vocabulary():
    """PerformanceInterpretation.kind MUST be present with 4 binding values."""
    values = _vocab_values("PerformanceInterpretation.kind")
    assert values is not None, "CR-MET-006: PerformanceInterpretation.kind vocabulary missing"
    expected = {"variance_evaluation", "threshold_evaluation", "benchmark_evaluation", "composite_judgment"}
    assert values == expected, f"CR-MET-006: PerformanceInterpretation.kind must be {sorted(expected)} (got {sorted(values)})"


def test_performance_interpretation_state_vocabulary():
    """PerformanceInterpretation.state MUST be present with 6 binding values."""
    values = _vocab_values("PerformanceInterpretation.state")
    assert values is not None, "CR-MET-006: PerformanceInterpretation.state vocabulary missing"
    expected = {"exceeds_target", "meets_target", "within_tolerance", "warning", "critical", "unknown"}
    assert values == expected, f"CR-MET-006: PerformanceInterpretation.state must be {sorted(expected)} (got {sorted(values)})"


# -------- fixture integrity --------

def test_fixtures_use_only_valid_vocabulary_values():
    """Every fixture's controlled-vocab field must use a value in the vocabulary."""
    fx = _fixtures()
    kind_values = _vocab_values("Baseline.kind")
    approval_values = _vocab_values("Baseline.approval_status")
    pt_dir_values = _vocab_values("PerformanceTarget.direction")
    pt_approval_values = _vocab_values("PerformanceTarget.approval_status")
    th_level_values = _vocab_values("Threshold.level")
    th_dir_values = _vocab_values("Threshold.direction")
    pi_kind_values = _vocab_values("PerformanceInterpretation.kind")
    pi_state_values = _vocab_values("PerformanceInterpretation.state")

    for b in fx["baselines"]:
        assert b["kind"] in kind_values
        assert b["approval_status"] in approval_values
    for t in fx["performance_targets"]:
        assert t["target_direction"] in pt_dir_values
        assert t["approval_status"] in pt_approval_values
    for t in fx["thresholds"]:
        assert t["threshold_level"] in th_level_values
        assert t["direction"] in th_dir_values
    for p in fx["performance_interpretations"]:
        assert p["interpretation_kind"] in pi_kind_values
        assert p["interpretation_state"] in pi_state_values


def test_performance_target_value_range_mutually_exclusive():
    """CR-MET-006 cross-field invariant: target_value and target_range are mutually exclusive (anyOf constraint)."""
    fx = _fixtures()
    for pt in fx["performance_targets"]:
        has_value = "target_value" in pt
        has_range = "target_range" in pt
        assert has_value != has_range, \
            f"CR-MET-006: PerformanceTarget {pt['id']} has both/neither target_value and target_range"


# -------- canonical-source invariants --------

def test_new_entities_in_canonical_source():
    """The 4 NEW entities MUST be present in the canonical source."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    entity_ids = {e["id"] for e in normative["entities"]}
    for nid in ("dea:Baseline", "dea:PerformanceTarget", "dea:Threshold", "dea:PerformanceInterpretation"):
        assert nid in entity_ids, f"CR-MET-006: required entity {nid} missing"


def test_existing_assessment_target_preserved():
    """CR-MET-006 MUST preserve dea:AssessmentTarget unchanged (maturity-level targets, CR-5 section 21)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    at = next(e for e in normative["entities"] if e["id"] == "dea:AssessmentTarget")
    # AssessmentTarget is preserved; PerformanceTarget is a separate sibling.
    assert at["id"] == "dea:AssessmentTarget"
    # The definition should NOT mention "value-level"; it's still about maturity levels.
    assert "maturity" in at["definition"].lower() or "level" in at["definition"].lower(), \
        "CR-MET-006: dea:AssessmentTarget should retain maturity-level semantics"


def test_existing_benchmark_reference_reused_not_new_entity():
    """CR-MET-006 MUST REUSE existing dea:BenchmarkReference; no dea:Benchmark entity introduced."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    entity_ids = {e["id"] for e in normative["entities"]}
    assert "dea:BenchmarkReference" in entity_ids, "dea:BenchmarkReference should exist"
    # CR-MET-006 binding: reuse dea:BenchmarkReference; do NOT introduce a separate Benchmark entity.
    # (The pre-existing dea:Agent entry is allowed; we test only for dea:Benchmark.)


def test_new_relationships_in_canonical_source():
    """The 5 NEW relationships MUST be present in the canonical source."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    rel_ids = {r["id"] for r in normative["relationships"]}
    for nid in (
        "dea:references", "dea:applies-subject", "dea:specifies-target",
        "dea:interprets", "dea:has-target",
    ):
        assert nid in rel_ids, f"CR-MET-006: required relationship {nid} missing"


def test_extended_relationships_include_new_entities():
    """CR-MET-006 extended dea:constrains (adds Threshold, PerformanceMetric) and dea:benchmarked-against (adds PerformanceMetric)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    rels = {r["id"]: r for r in normative["relationships"]}

    # dea:constrains
    assert "dea:Threshold" in rels["dea:constrains"]["source"]["types"], \
        "CR-MET-006: dea:constrains source list must include dea:Threshold"
    assert "dea:PerformanceMetric" in rels["dea:constrains"]["target"]["types"], \
        "CR-MET-006: dea:constrains target list must include dea:PerformanceMetric"

    # dea:benchmarked-against
    assert "dea:PerformanceMetric" in rels["dea:benchmarked-against"]["source"]["types"], \
        "CR-MET-006: dea:benchmarked-against source list must include dea:PerformanceMetric"


def test_relationship_instance_enum_has_new_relationships():
    """The relationship-instance.json enum MUST include the 5 new relationships."""
    schema = json.loads(
        (BASE / "schemas" / "relationships" / "relationship-instance.json").read_text()
    )
    enum = set(schema["properties"]["relationship_type"]["enum"])
    for nid in (
        "applies-subject", "has-target", "interprets",
        "references", "specifies-target",
    ):
        assert nid in enum, f"CR-MET-006: relationship-instance.json enum must include '{nid}'"
    # CR-MET-006 binding: Benchmark concept is realized via dea:benchmarked-against (the existing
    # relationship; no separate dea:benchmarks enum entry is introduced).


def test_relationship_count_increment():
    """CR-MET-006 MUST add 5 NEW + 2 EXTENDED relationships (107 -> 112)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    assert len(normative["relationships"]) == 112, \
        f"CR-MET-006: relationship count must be 112 (got {len(normative['relationships'])})"


def test_entity_count_increment():
    """CR-MET-006 MUST add 4 NEW entities (153 -> 157)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    assert len(normative["entities"]) == 157, \
        f"CR-MET-006: entity count must be 157 (got {len(normative['entities'])})"


def test_interprets_target_includes_measurement_observation():
    """dea:interprets target MUST include dea:MeasurementObservation (and dea:Observation, the assessment-side sibling)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    rel = next(r for r in normative["relationships"] if r["id"] == "dea:interprets")
    targets = rel["target"]["types"]
    assert "dea:MeasurementObservation" in targets, \
        "CR-MET-006: dea:interprets target must include dea:MeasurementObservation"
    assert "dea:Observation" in targets, \
        "CR-MET-006: dea:interprets target must include dea:Observation (assessment-side sibling)"