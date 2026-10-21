"""CR-MET-012: measurement analytics and decision-intelligence integration.

Covers:
- Section 3: the 6 complementary analytical capabilities
- Section 4: the 4 measurement-intelligence stack layers
- Section 5: aggregation inheriting the CR-MET-005 rules (Q21a)
- Section 6: correlation versus causal hypothesis (Q22c)
- Section 7: the information-type separation (Q20b-prime)
- Section 8: the Outcome-to-Observation many-to-many relationship
- Section 11: the 5 end-to-end reference scenarios
"""
import json

import yaml

from conftest import BASE

FIXTURE = yaml.safe_load(
    (BASE / "tests" / "conformance" / "fixtures" / "measurement_analytics.yaml").read_text()
)
CLASSIFICATIONS = yaml.safe_load(
    (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
)["classifications"]
NORMATIVE = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())

ANALYTICAL_CAPABILITIES = [
    "descriptive", "diagnostic", "predictive", "prescriptive",
    "comparative", "scenario_simulation",
]
# Q20b-prime: the 4 DERIVED result types. observation and decision are absent by design.
DERIVED_RESULT_TYPES = ["estimate", "forecast", "simulation_result", "recommendation"]


def _results():
    return FIXTURE["analytical_results"]


def _correlations():
    return FIXTURE["correlations"]


def _hypotheses():
    return FIXTURE["causal_hypotheses"]


def _scenarios():
    return FIXTURE["scenario_records"]


def _schema(stem):
    return json.loads((BASE / "schemas" / "entities" / f"{stem}.json").read_text())


def test_section3_six_analytical_capabilities_supported():
    schema = _schema("analytical-result")
    assert set(schema["properties"]["analytical_capability"]["enum"]) == set(ANALYTICAL_CAPABILITIES)
    voc = set(CLASSIFICATIONS["AnalyticalResult.analytical_capability"]["values"])
    assert voc == set(ANALYTICAL_CAPABILITIES)


def test_section3_fixture_exercises_every_capability():
    used = {r["analytical_capability"] for r in _results()}
    assert used == set(ANALYTICAL_CAPABILITIES), f"CR-MET-012 section 3: fixture covers {sorted(used)}"


def test_section4_four_stack_layers_have_a_home_in_the_metamodel():
    """Section 4 layers map onto existing entities; the layer descriptions are not
    separate deployable applications and must not introduce parallel entities."""
    ids = {e["id"] for e in NORMATIVE["entities"]}
    semantic_foundation = {"dea:PerformanceMetric", "dea:Measurement", "dea:MeasurementObservation"}
    measurement_context = {
        "dea:Baseline", "dea:PerformanceTarget", "dea:Threshold",
        "dea:BenchmarkReference", "dea:ReportingPeriod", "dea:Provenance",
    }
    assert semantic_foundation <= ids, "CR-MET-012 section 4: semantic foundation entities missing"
    assert measurement_context <= ids, "CR-MET-012 section 4: measurement context entities missing"
    assert "dea:AnalyticalResult" in ids, "CR-MET-012 section 4: analytical services layer entity missing"


def test_section5_aggregation_must_declare_a_rule():
    """Q21a: aggregation must respect the CR-MET-005 rules; a simple arithmetic
    average is NOT a universal aggregation method."""
    for r in _results():
        assert r["aggregation_rule_ref"], \
            f"CR-MET-012 Q21a: {r['id']} MUST declare the AggregationRule applied"


def test_section5_aggregation_rule_must_use_a_controlled_operator():
    """Q21a: aggregation reuses the CR-MET-005 AggregationRule operator set."""
    allowed = set(CLASSIFICATIONS["AggregationRule.operator"]["values"])
    assert "WEIGHTED_MEAN" in allowed and "MEAN" in allowed and "SUM" in allowed, \
        "CR-MET-005 binding: the controlled operator set must be present"
    # A rollup across organizational units must NOT declare a plain mean on a ratio.
    for r in _results():
        if r["analytical_capability"] == "comparative" and "index" in str(r.get("unit")):
            assert "weighted" in r["aggregation_rule_ref"] or "MEAN" not in r["aggregation_rule_ref"], \
                f"CR-MET-005 section 3.3: {r['id']} rolls a ratio up and MUST use a weighted rule"


def test_section7_derived_result_types_exclude_observation_and_decision():
    """Q20b-prime: Observation and Decision already exist as first-class entities with
    their own lifecycle. Absorbing them as result_type values would destroy identity."""
    schema = _schema("analytical-result")
    enum = schema["properties"]["result_type"]["enum"]
    assert set(enum) == set(DERIVED_RESULT_TYPES), f"CR-MET-012 section 7: result_type is {enum}"
    assert "observation" not in enum, "dea:MeasurementObservation is the first-class Observation"
    assert "decision" not in enum, "dea:Decision is the first-class authorized management choice"


def test_section7_observation_and_decision_remain_first_class_entities():
    ids = {e["id"] for e in NORMATIVE["entities"]}
    assert "dea:MeasurementObservation" in ids
    assert "dea:Decision" in ids
    assert "dea:AnalyticalResult" in ids


def test_section7_every_result_cites_its_evidence():
    """An analytical output with no cited measurement evidence is not admissible."""
    for r in _results():
        assert r["evidence_refs"], f"CR-MET-012 section 7: {r['id']} MUST cite measurement evidence"


def test_section7_every_result_declares_confidence():
    schema = _schema("analytical-result")
    assert "confidence" in schema["required"], \
        "CR-MET-012 section 7: confidence must be required on every analytical result"
    for r in _results():
        assert 0 <= r["confidence"] <= 1, f"CR-MET-012 section 7: {r['id']} confidence out of range"


def test_section7_every_result_carries_provenance():
    """CR-MET-011 section 5 provenance binding extends to analytical outputs."""
    for r in _results():
        assert r["provenance_reference"], \
            f"CR-MET-012 section 7: {r['id']} MUST carry a Provenance reference"


def test_forecast_and_simulation_require_uncertainty_and_model():
    """A forward-looking output with no uncertainty statement is inadmissible."""
    for r in _results():
        if r["result_type"] in {"forecast", "simulation_result"}:
            assert r["uncertainty"], f"CR-MET-012: {r['id']} MUST declare uncertainty"
            assert r["model_ref"], f"CR-MET-012: {r['id']} MUST declare the model that produced it"
            assert r["horizon_ref"], f"CR-MET-012: {r['id']} MUST declare its forward horizon"


def test_simulation_result_requires_a_scenario():
    for r in _results():
        if r["result_type"] == "simulation_result":
            assert r["scenario_ref"], \
                f"CR-MET-012: {r['id']} is conditioned on a scenario and MUST declare it"
        else:
            assert r["scenario_ref"] is None, \
                f"CR-MET-012: {r['id']} is {r['result_type']} and MUST NOT claim a scenario"


def test_recommendation_produces_no_value_and_records_alternatives():
    """A recommendation proposes an action; it does not assert a quantity."""
    for r in _results():
        if r["result_type"] == "recommendation":
            assert r["value"] is None, f"CR-MET-012: {r['id']} recommendation MUST NOT carry a value"
            assert r["alternative_considered"], \
                f"CR-MET-012: {r['id']} MUST record the alternatives considered so it is auditable"
            for alt in r["alternative_considered"]:
                assert alt["rationale"], f"CR-MET-012: {r['id']} alternative MUST state a rationale"


def test_recommendation_is_not_a_decision():
    """A Recommendation informs a Decision; it does not become one."""
    ids = {e["id"] for e in NORMATIVE["entities"]}
    rels = {r["id"]: r for r in NORMATIVE["relationships"]}
    assert "dea:Decision" in ids
    assert "dea:informs-decision" in rels, "CR-MET-012 section 6: the informs-decision relationship must exist"
    assert "dea:AnalyticalResult" in rels["dea:informs-decision"]["source"]["types"]
    assert "dea:Decision" in rels["dea:informs-decision"]["target"]["types"]


def test_section6_correlation_and_hypothesis_are_distinct_entities():
    ids = {e["id"] for e in NORMATIVE["entities"]}
    assert "dea:Correlation" in ids, "CR-MET-012 section 6: Correlation must be first-class"
    assert "dea:CausalHypothesis" in ids, "CR-MET-012 section 6: CausalHypothesis must be first-class"
    assert "dea:Correlation" != "dea:CausalHypothesis"


def test_section6_correlation_never_asserts_causation():
    """The confusion guard: a correlation records association only."""
    schema = _schema("correlation")
    assert "confusion_guard" in schema["required"], \
        "CR-MET-012 section 6: confusion_guard must be required on every Correlation"
    for c in _correlations():
        assert c["confusion_guard"] is False, \
            f"CR-MET-012 section 6: {c['id']} MUST NOT assert a causal claim"


def test_section6_correlation_records_method_and_sample():
    for c in _correlations():
        assert c["method"], f"CR-MET-012 section 6: {c['id']} MUST record the statistical method"
        assert c["sample_size"] >= 1, f"CR-MET-012 section 6: {c['id']} MUST record the sample size"
        assert c["evidence_refs"], f"CR-MET-012 section 6: {c['id']} MUST cite its source Observations"


def test_section6_correlation_records_confounder_candidates():
    """Absence of confounders is not evidence of their absence."""
    for c in _correlations():
        assert "confounder_candidates" in c, \
            f"CR-MET-012 section 6: {c['id']} MUST record confounder candidates (even if empty)"


def test_section6_hypothesis_requires_mechanism_and_validation_state():
    schema = _schema("causal-hypothesis")
    assert "mechanism" in schema["required"], "a hypothesis without a mechanism is an assertion"
    assert "validation_state" in schema["required"]
    voc = set(CLASSIFICATIONS["CausalHypothesis.validation_state"]["values"])
    assert set(schema["properties"]["validation_state"]["enum"]) == voc
    for h in _hypotheses():
        assert h["mechanism"], f"CR-MET-012 section 6: {h['id']} MUST state a mechanism"
        assert h["validation_state"] in voc


def test_section6_hypothesis_records_counter_evidence_and_falsification():
    """A hypothesis with no counter-evidence is either trivially true or not honestly recorded."""
    for h in _hypotheses():
        assert h["counter_evidence"], \
            f"CR-MET-012 section 6: {h['id']} MUST record counter-evidence"
        assert h["falsification_test"], \
            f"CR-MET-012 section 6: {h['id']} MUST declare how it would be refuted"


def test_section6_counter_evidence_is_schema_level_required():
    """The counter-evidence obligation is a schema requirement, not only a fixture convention.

    Fixture-level assertions alone would pass even if the schema permitted a
    hypothesis with no counter-evidence, leaving the rule unenforced for every
    authoring surface outside the conformance fixture.
    """
    schema = _schema("causal-hypothesis")
    assert "counter_evidence" in schema["required"], \
        "CR-MET-012 section 6: counter_evidence must be required by the schema"
    assert "falsification_test" in schema["required"], \
        "CR-MET-012 section 6: falsification_test must be required by the schema"


def test_section6_hypothesis_confidence_may_not_exceed_correlation_strength():
    """Confidence in a mechanism is bounded by the strength of the association observed
    for it. A 0.63 correlation cannot license a 0.9 causal confidence."""
    corr = {c["id"]: c for c in _correlations()}
    for h in _hypotheses():
        for ref in h["supporting_correlation_refs"]:
            c = corr[ref]
            assert h["confidence"] <= abs(c["coefficient"]), \
                f"CR-MET-012 section 6: {h['id']} confidence {h['confidence']} exceeds the supporting correlation strength {abs(c['coefficient'])}"


def test_section6_correlation_relationship_is_symmetric():
    rels = {r["id"]: r for r in NORMATIVE["relationships"]}
    assert rels["dea:correlates"]["symmetric"] is True, \
        "CR-MET-012 section 6: correlation has no direction and MUST be symmetric"
    assert rels["dea:correlates"]["inverse"] == "dea:correlates"


def test_section6_hypothesis_is_tested_by_correlation():
    rels = {r["id"]: r for r in NORMATIVE["relationships"]}
    assert "dea:tests-hypothesis" in rels
    assert "dea:Correlation" in rels["dea:tests-hypothesis"]["source"]["types"]
    assert "dea:CausalHypothesis" in rels["dea:tests-hypothesis"]["target"]["types"]


def test_section8_outcome_supports_multiple_observations():
    """Section 8: an Outcome may be supported by multiple Observations over time; one
    Observation may contribute evidence to multiple related assessments or outcomes."""
    rels = {r["id"]: r for r in NORMATIVE["relationships"]}
    assert "dea:derives-from" in rels
    assert "dea:AnalyticalResult" in rels["dea:derives-from"]["source"]["types"]
    assert "dea:MeasurementObservation" in rels["dea:derives-from"]["target"]["types"]
    schema = _schema("analytical-result")
    assert schema["properties"]["evidence_refs"]["type"] == "array", \
        "CR-MET-012 section 8: evidence must be many-valued"


def test_section11_five_reference_scenarios_present():
    assert len(_scenarios()) == 5, "CR-MET-012 section 11: 5 reference scenarios required"
    assert {s["scenario"] for s in _scenarios()} == {"A", "B", "C", "D", "E"}


def test_section11_each_scenario_cites_evidence():
    for s in _scenarios():
        assert s["chain"], f"CR-MET-012 section 11: scenario {s['scenario']} must have a chain"
        assert len(s["chain"]) >= 5, \
            f"CR-MET-012 section 11: scenario {s['scenario']} chain is too short to be end-to-end"
        assert s["required_evidence_cited"] is True, \
            f"CR-MET-012 section 11: scenario {s['scenario']} must cite evidence"


def test_section11_scenarios_are_named_per_the_user_specification():
    names = {s["scenario"]: s["name"] for s in _scenarios()}
    assert names == {
        "A": "Strategic performance management",
        "B": "Digital maturity improvement",
        "C": "Operational optimization",
        "D": "Enterprise risk intelligence",
        "E": "Transformation benefits realization",
    }


def _entity_types():
    """The registered entity type ids (dea:X)."""
    return {e["id"] for e in NORMATIVE["entities"]}


# Catalog identifier prefixes mapped to their registered metamodel entity type.
# The catalog (dea-catalog-metrics) publishes instances under these prefixes; the
# metamodel registers the type. The mapping is explicit, never inferred.
CATALOG_PREFIX_TO_TYPE = {
    "dea:metric-": "dea:PerformanceMetric",
    "dea:Observation-": "dea:MeasurementObservation",
}


def _resolve_type(ref):
    """Resolve an instance reference to its registered entity type.

    Scenario chains name concrete instances (dea:BusinessProcess-order-to-cash,
    dea:metric-process-cycle-time), while the metamodel registers entity types
    (dea:BusinessProcess, dea:PerformanceMetric). Catalog prefixes map through the
    explicit CATALOG_PREFIX_TO_TYPE table; everything else resolves by walking
    progressively shorter name suffixes until a registered type is found.
    """
    ids = _entity_types()
    for prefix, entity_type in CATALOG_PREFIX_TO_TYPE.items():
        if ref.startswith(prefix):
            assert entity_type in ids, \
                f"catalog prefix {prefix!r} maps to unregistered type {entity_type!r}"
            return entity_type
    parts = ref.split(":")
    if len(parts) != 2:
        return None
    rest = parts[1].split("-")
    while rest:
        candidate = f"{parts[0]}:{'-'.join(rest)}"
        if candidate in ids:
            return candidate
        rest.pop()
    return None


def test_section11_scenario_chains_reference_registered_entity_types():
    """Every hop in a reference scenario must resolve to a registered entity type.

    Chains name concrete instances; resolution strips the instance suffix.
    """
    fixture_refs = (
        {r["id"] for r in _results()}
        | {c["id"] for c in _correlations()}
        | {h["id"] for h in _hypotheses()}
    )
    unresolved = []
    for s in _scenarios():
        for hop in s["chain"]:
            if hop in fixture_refs:
                continue
            if _resolve_type(hop) is None:
                unresolved.append(f"scenario {s['scenario']} hop {hop!r}")
    assert not unresolved, \
        "CR-MET-012 section 11: unresolvable scenario hops: " + "; ".join(unresolved)


def test_section11_resolution_strips_instance_suffix():
    """The resolution rule itself is verified, so a false pass cannot hide."""
    assert _resolve_type("dea:BusinessProcess-order-to-cash") == "dea:BusinessProcess"
    assert _resolve_type("dea:metric-strategic-objective-attainment") == "dea:PerformanceMetric", \
        "dea:metric-* are catalog instances of dea:PerformanceMetric (CR-MET-009 binding)"
    assert _resolve_type("dea:Observation-strategic-2026q1") == "dea:MeasurementObservation", \
        "dea:Observation-* catalog instances resolve to the CR-MET-001 entity"
    assert _resolve_type("dea:PerformanceMetric") == "dea:PerformanceMetric"


def test_notlist_metamodel_does_not_absorb_runtime_engines():
    """The NOT-list: the metamodel provides the semantic foundation; runtime systems
    provide the engines. No new entity asserts an execution engine."""
    for e in NORMATIVE["entities"]:
        if e["id"] in {"dea:AnalyticalResult", "dea:Correlation", "dea:CausalHypothesis"}:
            assert e["membership"]["kind"] in {"core", "profile"}, \
                f"CR-MET-012 NOT-list: {e['id']} must be a semantic construct, not a runtime engine"


def test_notlist_analytical_result_is_not_in_the_measurement_observation_union():
    """An AnalyticalResult MUST NOT publish as an equivalent measurement fact."""
    assert "dea:AnalyticalResult" not in {
        t for r in NORMATIVE["relationships"] if r["id"] == "dea:produces"
        for t in r["target"]["types"]
    }, "CR-MET-012 section 7: an analytical output is not a produced measurement result"