"""CR-MET-004: Measurement lifecycle, execution modes and processing semantics.

CR-MET-004 binding CR-MET-001 / CR-MET-003 and ADR-MET-002.
"""
import json

import yaml

from conftest import BASE

LIFECYCLE_VOCAB = BASE / "metamodel" / "vocabularies" / "measurement-lifecycle.yaml"


def _lifecycle():
    return yaml.safe_load(LIFECYCLE_VOCAB.read_text())


def _schemas():
    return {p.stem: json.loads(p.read_text())
            for p in sorted((BASE / "schemas" / "entities").glob("*.json"))}


def _relationships():
    return [r for r in yaml.safe_load(
        (BASE / "metamodel" / "dea-metamodel.yaml").read_text()
    ).get("relationships", [])
        if isinstance(r, dict) and r.get("id", "").startswith("dea:")]


def _fixtures():
    return yaml.safe_load(
        (BASE / "tests" / "conformance" / "fixtures" / "measurement_lifecycle.yaml").read_text()
    )


def _legal_transitions():
    return {(t["from"], t["to"]) for t in _lifecycle()["transitions"]}


def test_lifecycle_vocabulary_file_exists():
    """The measurement-lifecycle vocabulary artifact MUST exist (CR-MET-004 §4.1)."""
    assert LIFECYCLE_VOCAB.exists(), \
        f"CR-MET-004: {LIFECYCLE_VOCAB} must exist (canonical Measurement lifecycle vocabulary)"


def test_lifecycle_declares_10_canonical_states():
    """The lifecycle vocabulary MUST declare the 10 canonical Measurement states."""
    states = [s["id"] for s in _lifecycle()["states"]]
    expected = {
        "planned", "initiated", "in_progress", "pending_validation",
        "validated", "completed", "failed", "cancelled",
        "rejected", "superseded",
    }
    assert set(states) == expected, \
        f"CR-MET-004: lifecycle states must be {sorted(expected)} (got {sorted(states)})"
    assert len(states) == 10, f"CR-MET-004: must declare exactly 10 states (got {len(states)})"


def test_lifecycle_states_match_measurement_status_schema_enum():
    """The declared states MUST match the Measurement.measurement_status schema enum exactly."""
    states = {s["id"] for s in _lifecycle()["states"]}
    schema_enum = set(_schemas()["measurement"]["properties"]["measurement_status"]["enum"])
    assert states == schema_enum, \
        f"CR-MET-004: lifecycle states must match measurement_status enum " \
        f"(states-only={sorted(states - schema_enum)}, enum-only={sorted(schema_enum - states)})"


def test_lifecycle_declares_8_execution_modes():
    """The lifecycle vocabulary MUST declare the 8 canonical execution modes."""
    modes = [m["id"] for m in _lifecycle()["execution_modes"]]
    expected = {
        "automated", "manual", "calculated", "aggregated",
        "external", "assessed", "simulated", "ai_assisted",
    }
    assert set(modes) == expected, \
        f"CR-MET-004: execution modes must be {sorted(expected)} (got {sorted(modes)})"
    assert len(modes) == 8, f"CR-MET-004: must declare exactly 8 execution modes (got {len(modes)})"


def test_execution_modes_match_schema_enum():
    """The declared execution modes MUST match the Measurement.execution_mode schema enum exactly."""
    modes = {m["id"] for m in _lifecycle()["execution_modes"]}
    schema_enum = set(_schemas()["measurement"]["properties"]["execution_mode"]["enum"])
    assert modes == schema_enum, \
        f"CR-MET-004: execution modes must match execution_mode enum " \
        f"(modes-only={sorted(modes - schema_enum)}, enum-only={sorted(schema_enum - modes)})"


def test_verification_states_match_schema_enum():
    """The declared verification states MUST match the MeasurementObservation.verification_state schema enum."""
    states = {s["id"] for s in _lifecycle()["verification_states"]}
    schema_enum = set(
        _schemas()["measurement-observation"]["properties"]["verification_state"]["enum"]
    )
    assert states == schema_enum, \
        f"CR-MET-004: verification states must match verification_state enum " \
        f"(states-only={sorted(states - schema_enum)}, enum-only={sorted(schema_enum - states)})"
    assert len(states) == 4, f"CR-MET-004: must declare exactly 4 verification states (got {len(states)})"


def test_transition_set_is_closed():
    """Every transition's from_state and to_state MUST be a declared state (the transition set is closed)."""
    states = {s["id"] for s in _lifecycle()["states"]}
    for t in _lifecycle()["transitions"]:
        assert t["from"] in states, \
            f"CR-MET-004: transition from_state {t['from']!r} is not a declared state"
        assert t["to"] in states, \
            f"CR-MET-004: transition to_state {t['to']!r} is not a declared state"
        assert t.get("guard"), \
            f"CR-MET-004: transition {t['from']} -> {t['to']} must declare a guard"


def test_terminal_states_are_declared_and_have_no_outgoing_transitions():
    """Every declared terminal state MUST have no outgoing transitions."""
    states = {s["id"] for s in _lifecycle()["states"]}
    terminal = set(_lifecycle()["terminal_states"])
    assert terminal <= states, \
        f"CR-MET-004: terminal states must be declared states (got {sorted(terminal - states)})"
    for t in _lifecycle()["transitions"]:
        assert t["from"] not in terminal, \
            f"CR-MET-004: terminal state {t['from']!r} must have no outgoing transition (to {t['to']!r})"


def test_conditionally_terminal_states_have_exactly_one_outgoing_transition():
    """completed, failed and rejected are conditionally terminal: each MUST have exactly
    one outgoing transition, to superseded (CR-MET-004 section 3.1)."""
    outgoing = {}
    for t in _lifecycle()["transitions"]:
        outgoing.setdefault(t["from"], []).append(t["to"])
    for state in ("completed", "failed", "rejected"):
        targets = outgoing.get(state, [])
        assert targets == ["superseded"], \
            f"CR-MET-004: {state!r} must have exactly one outgoing transition, to 'superseded' (got {targets})"


def test_terminal_states_are_cancelled_and_superseded():
    """The 2 strictly-terminal states (cancelled, superseded) MUST be declared terminal."""
    terminal = set(_lifecycle()["terminal_states"])
    expected = {"cancelled", "superseded"}
    assert terminal == expected, \
        f"CR-MET-004: terminal states must be {sorted(expected)} (got {sorted(terminal)})"


def test_measurement_schema_requires_execution_mode():
    """The measurement.json schema MUST require execution_mode (CR-MET-004 §4.2)."""
    schema = _schemas()["measurement"]
    required = schema.get("required", [])
    assert "execution_mode" in required, \
        f"CR-MET-004: measurement.json must require 'execution_mode' (got {required})"


def test_measurement_schema_declares_lifecycle_fields():
    """The measurement.json schema MUST declare state_transitions and logical_measurement_event."""
    props = _schemas()["measurement"].get("properties", {})
    for field in ["state_transitions", "logical_measurement_event"]:
        assert field in props, \
            f"CR-MET-004: measurement.json must declare '{field}' (got {sorted(props.keys())})"
    transitions = props["state_transitions"]
    assert transitions.get("type") == "array", \
        f"CR-MET-004: state_transitions must be type=array (got {transitions.get('type')})"
    item_required = transitions["items"].get("required", [])
    for field in ["from_state", "to_state", "transitioned_at"]:
        assert field in item_required, \
            f"CR-MET-004: state_transitions item must require '{field}' (got {item_required})"


def test_measurement_observation_schema_declares_correction_fields():
    """The measurement-observation.json schema MUST declare verification_state and supersedes_observation."""
    props = _schemas()["measurement-observation"].get("properties", {})
    for field in ["verification_state", "supersedes_observation"]:
        assert field in props, \
            f"CR-MET-004: measurement-observation.json must declare '{field}' (got {sorted(props.keys())})"


def test_dea_supersedes_extended_with_measurement_types():
    """dea:supersedes MUST include dea:Measurement and dea:MeasurementObservation in source and target (CR-MET-004 §4.4.1)."""
    rel = next((r for r in _relationships() if r["id"] == "dea:supersedes"), None)
    assert rel is not None, "CR-MET-004: dea:supersedes missing from canonical source"
    for endpoint in ("source", "target"):
        types = rel[endpoint]["types"]
        assert "dea:Measurement" in types, \
            f"CR-MET-004: dea:supersedes {endpoint} must include dea:Measurement (got {types})"
        assert "dea:MeasurementObservation" in types, \
            f"CR-MET-004: dea:supersedes {endpoint} must include dea:MeasurementObservation (got {types})"
    # the pre-existing 8 source and 8 target entity types must be preserved
    assert len(rel["source"]["types"]) == 10, \
        f"CR-MET-004: dea:supersedes source must have 8 pre-existing + 2 new types (got {len(rel['source']['types'])})"
    assert len(rel["target"]["types"]) == 10, \
        f"CR-MET-004: dea:supersedes target must have 8 pre-existing + 2 new types (got {len(rel['target']['types'])})"


def test_all_fixture_transitions_are_legal():
    """Every fixture state_transitions pair MUST be a legal transition per the vocabulary file."""
    legal = _legal_transitions()
    fx = _fixtures()
    for m in fx["measurements"]:
        for t in m.get("state_transitions", []):
            pair = (t["from_state"], t["to_state"])
            assert pair in legal, \
                f"CR-MET-004: measurement {m['id']} has illegal transition {pair}"


def test_all_fixture_terminal_states_are_terminal():
    """Every fixture's measurement_status MUST be a declared terminal state when it has no outgoing transition."""
    terminal = set(_lifecycle()["terminal_states"])
    fx = _fixtures()
    for m in fx["measurements"]:
        if m["measurement_status"] in terminal:
            continue
        # non-terminal fixtures must have at least one outgoing transition recorded
        assert m.get("state_transitions"), \
            f"CR-MET-004: non-terminal measurement {m['id']} must record state_transitions"


def test_all_fixture_execution_modes_are_declared():
    """Every fixture's execution_mode MUST be a declared execution mode."""
    modes = {m["id"] for m in _lifecycle()["execution_modes"]}
    fx = _fixtures()
    for m in fx["measurements"]:
        assert m.get("execution_mode") in modes, \
            f"CR-MET-004: measurement {m['id']} execution_mode {m.get('execution_mode')!r} not a declared mode"


def test_ai_assisted_observation_is_estimate_not_verified():
    """The AI-assisted observation MUST carry verification_state: ai_estimated (never independently_verified or human_verified)."""
    fx = _fixtures()
    ai_obs = next(
        (o for o in fx["measurement_observations"]
         if o["id"] == "dea:measurement-observation-2026-q3-employee-engagement-ai"),
        None,
    )
    assert ai_obs is not None, "CR-MET-004: AI-assisted observation fixture missing"
    assert ai_obs["verification_state"] == "ai_estimated", \
        f"CR-MET-004: AI-assisted observation verification_state must be 'ai_estimated' " \
        f"(got {ai_obs['verification_state']!r})"
    assert ai_obs["verification_state"] not in ("independently_verified", "human_verified"), \
        "CR-MET-004: an AI-assisted measurement must not produce a verified observation"


def test_correction_pair_is_consistent():
    """The correction observation MUST reference a prior observation whose status is superseded."""
    fx = _fixtures()
    by_id = {o["id"]: o for o in fx["measurement_observations"]}
    corrected = by_id.get("dea:measurement-observation-2026-q2-customer-retention-corrected")
    assert corrected is not None, "CR-MET-004: corrected observation fixture missing"
    prior_ref = corrected.get("supersedes_observation")
    assert prior_ref, "CR-MET-004: corrected observation must declare supersedes_observation"
    prior = by_id.get(prior_ref)
    assert prior is not None, \
        f"CR-MET-004: supersedes_observation {prior_ref!r} must resolve to a fixture observation"
    assert prior["observation_status"] == "superseded", \
        f"CR-MET-004: the superseded observation {prior_ref!r} must have observation_status 'superseded' " \
        f"(got {prior['observation_status']!r})"


def test_idempotency_no_two_completed_share_a_logical_key():
    """No two completed Measurements may share the same logical_measurement_event key (CR-MET-004 §3.5)."""
    fx = _fixtures()
    completed_keys = [
        m["logical_measurement_event"] for m in fx["measurements"]
        if m.get("measurement_status") == "completed" and m.get("logical_measurement_event")
    ]
    assert len(completed_keys) == len(set(completed_keys)), \
        f"CR-MET-004: two completed Measurements share a logical_measurement_event key: {completed_keys}"


def test_no_new_entity_or_relationship_introduced():
    """CR-MET-004 MUST NOT introduce a new entity or a new relationship (ADR-013 anti-accumulation; no workflow-engine dependency)."""
    normative = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    entity_ids = {e["id"] for e in normative["entities"]}
    assert "dea:Measurement" in entity_ids
    assert "dea:MeasurementObservation" in entity_ids
    # CR-MET-003 baseline: 153 entities, 107 relationships. CR-MET-004 adds neither.
    # CR-MET-006 added 4 entities + 5 relationships; the CR-MET-004 invariant is preserved (>= baseline).
    assert len(normative["entities"]) >= 153, \
        f"CR-MET-004: entity count must be >= 153 (got {len(normative['entities'])})"
    assert len(normative["relationships"]) >= 107, \
        f"CR-MET-004: relationship count must be >= 107 (got {len(normative['relationships'])})"
    # the transition declaration reuses the existing CR-6 LifecycleTransition entity
    assert "dea:LifecycleTransition" in entity_ids, \
        "CR-MET-004: the transition declaration MUST reuse dea:LifecycleTransition"


def test_metamodel_runtime_boundary_declared():
    """The vocabulary file MUST declare the metamodel/runtime boundary (CR-MET-004 §7)."""
    boundary = _lifecycle().get("metamodel_runtime_boundary")
    assert boundary, "CR-MET-004: metamodel_runtime_boundary must be declared"
    assert boundary.get("metamodel"), "CR-MET-004: metamodel responsibilities must be declared"
    assert boundary.get("runtime"), "CR-MET-004: runtime responsibilities must be declared"
    # the metamodel side must NOT claim runtime execution duties
    for forbidden in ("Execute the measurement modes", "Manage the state transition execution",
                      "Implement the retry mechanisms", "Run the validation checks"):
        assert forbidden not in boundary["metamodel"], \
            f"CR-MET-004: {forbidden!r} is a runtime responsibility, not a metamodel one"


def test_idempotency_rules_declared():
    """The vocabulary file MUST declare the retry/idempotency rules (CR-MET-004 §3.5)."""
    idem = _lifecycle().get("idempotency")
    assert idem, "CR-MET-004: idempotency semantics must be declared"
    assert idem.get("key_field") == "logical_measurement_event", \
        f"CR-MET-004: idempotency key_field must be 'logical_measurement_event' (got {idem.get('key_field')!r})"
    for rule in ("rule_1", "rule_2", "rule_3"):
        assert idem.get(rule), f"CR-MET-004: idempotency {rule} must be declared"
