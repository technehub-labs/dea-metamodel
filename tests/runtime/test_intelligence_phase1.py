"""CR-012 Phase 1 — Enterprise Intelligence Signal model tests.

Covers the signal data model + the in-memory SignalStore per CR-012 §3.1,
§3.2, §6 design constraints.
"""
from __future__ import annotations

import pytest

from runtime.intelligence import (Observation, Signal, SignalClassification,
                                    SignalError, SignalLifecycleStatus,
                                    SignalSeverity, SignalConfidence,
                                    SignalStore, SignalStoreError)


# ------------------------------------------------------------ vocabulary
def test_classification_vocabulary_matches_cr012_section_3_2():
    """CR-012 §3.2 — every classification in the normative vocabulary is exported."""
    expected = {
        "maturity_gap", "compliance_drift", "risk", "capability_gap",
        "federation_anomaly", "mapping_staleness", "agent_anomaly",
        "observation_only",
    }
    actual = {c.value for c in SignalClassification}
    assert actual == expected


def test_severity_vocabulary_matches_cr012_section_3_2():
    expected = {"info", "low", "medium", "high", "critical"}
    actual = {s.value for s in SignalSeverity}
    assert actual == expected


def test_confidence_vocabulary_matches_cr012_section_3_1():
    expected = {"exact", "high", "medium", "low", "uncertain"}
    actual = {c.value for c in SignalConfidence}
    assert actual == expected


def test_lifecycle_states_match_cr012_lifecycle_yaml():
    expected = {"open", "acknowledged", "in_review", "accepted",
                "dismissed", "resolved"}
    actual = {s.value for s in SignalLifecycleStatus}
    assert actual == expected


# ------------------------------------------------------------ Observation
def _observation(**overrides) -> Observation:
    base = dict(
        id="obs.cap-cs.2026-q3.maturity-gap",
        cycle_id="loop.maturity-watchdog",
        subject="cap.customer-service",
        kind="maturity-gap-detector@1.0.0",
        evidence=["asm.2026-q3", "asm-result.asm.2026-q3.cap.customer-service"],
        confidence=SignalConfidence.HIGH,
        scope="capability:cap.customer-service",
    )
    base.update(overrides)
    return Observation(**base)


def test_observation_constructs_with_required_fields():
    obs = _observation()
    assert obs.id == "obs.cap-cs.2026-q3.maturity-gap"
    assert obs.kind == "maturity-gap-detector@1.0.0"
    assert obs.confidence == SignalConfidence.HIGH


def test_observation_rejects_non_canonical_id():
    with pytest.raises(SignalError, match="not canonical"):
        _observation(id="OBS-bad")


def test_observation_rejects_kind_without_version():
    with pytest.raises(SignalError, match="pattern@version"):
        _observation(kind="maturity-gap-detector")


def test_observation_rejects_empty_evidence():
    with pytest.raises(SignalError, match="at least one piece of evidence"):
        _observation(evidence=[])


def test_observation_is_immutable():
    obs = _observation()
    with pytest.raises(Exception):  # FrozenInstanceError
        obs.confidence = SignalConfidence.LOW  # type: ignore[misc]


# ------------------------------------------------------------ Signal — construction
def _signal(**overrides) -> Signal:
    base = dict(
        id="sig.cap-cs.2026-q3.maturity-gap",
        observation_ref="obs.cap-cs.2026-q3.maturity-gap",
        classification=SignalClassification.MATURITY_GAP,
        severity=SignalSeverity.MEDIUM,
        confidence=SignalConfidence.HIGH,
        entities=["cap.customer-service"],
        owner="actor.enterprise-architect",
        rationale="Maturity below target band for Q3",
    )
    base.update(overrides)
    return Signal(**base)


def test_signal_constructs_with_required_fields():
    sig = _signal()
    assert sig.status == SignalLifecycleStatus.OPEN
    assert sig.raised_at
    assert sig.history[0]["to"] == "open"


def test_signal_requires_owner_to_be_canonical_actor():
    with pytest.raises(SignalError, match="owner"):
        _signal(owner="not_canonical")  # underscore — fails CR-8 §7 regex


def test_signal_requires_at_least_one_entity():
    with pytest.raises(SignalError, match="at least one entity"):
        _signal(entities=[])


def test_signal_rejects_critical_without_escalation_policy():
    """CR-012 severity invariant — a critical signal without
    escalation_policy_ref is rejected at construction."""
    with pytest.raises(SignalError, match="escalation_policy_ref"):
        _signal(severity=SignalSeverity.CRITICAL)


def test_critical_signal_with_escalation_policy_constructs():
    sig = _signal(
        severity=SignalSeverity.CRITICAL,
        escalation_policy_ref="policy.escalation.ciso",
    )
    assert sig.severity == SignalSeverity.CRITICAL
    assert sig.escalation_policy_ref == "policy.escalation.ciso"


def test_signal_rejects_uncertain_at_high_severity():
    """CR-012 confidence invariant — UNCERTAIN only at info/low."""
    # critical without escalation_policy_ref fires the severity check first;
    # we add one here so the confidence check is the one that fires.
    with pytest.raises(SignalError, match="UNCERTAIN"):
        _signal(confidence=SignalConfidence.UNCERTAIN,
                severity=SignalSeverity.MEDIUM)
    with pytest.raises(SignalError, match="UNCERTAIN"):
        _signal(confidence=SignalConfidence.UNCERTAIN,
                severity=SignalSeverity.HIGH)
    with pytest.raises(SignalError, match="UNCERTAIN"):
        _signal(confidence=SignalConfidence.UNCERTAIN,
                severity=SignalSeverity.CRITICAL,
                escalation_policy_ref="policy.escalation.ciso")


def test_signal_allows_uncertain_at_low_severity():
    sig = _signal(confidence=SignalConfidence.UNCERTAIN,
                  severity=SignalSeverity.LOW)
    assert sig.confidence == SignalConfidence.UNCERTAIN


def test_signal_proposed_action_cannot_carry_approved_flag():
    """CR-012 §3.2 invariant — proposed_action on a Signal is not an
    ActionProposal; it MUST NOT mark itself approved."""
    with pytest.raises(SignalError, match="approved: true"):
        _signal(proposed_action="scenario.create x — approved: true")


def test_signal_deduplicates_entities():
    sig = _signal(entities=["cap.cs", "cap.customer-service", "cap.cs"])
    assert sig.entities == ["cap.cs", "cap.customer-service"]


# ------------------------------------------------------------ lifecycle
def test_lifecycle_open_can_be_dismissed_with_rationale():
    sig = _signal()
    sig.transition(SignalLifecycleStatus.ACKNOWLEDGED, by="actor.ea")
    sig.transition(SignalLifecycleStatus.DISMISSED, by="actor.ea",
                   dismissed_rationale="duplicate of asm.2026-q3 gap X")
    assert sig.status == SignalLifecycleStatus.DISMISSED
    assert sig.resolved_at is not None
    assert sig.rationale_at_dismiss == "duplicate of asm.2026-q3 gap X"


def test_lifecycle_open_can_be_resolved_only_after_acknowledged():
    """The lifecycle graph is directed; open → resolved is a skip
    (open → acknowledged → ... → resolved). Reject the skip."""
    sig = _signal()
    with pytest.raises(SignalError, match="not permitted"):
        sig.transition(SignalLifecycleStatus.RESOLVED)


def test_lifecycle_full_path_records_audit_history():
    sig = _signal()
    sig.transition(SignalLifecycleStatus.ACKNOWLEDGED, by="actor.ea")
    sig.transition(SignalLifecycleStatus.IN_REVIEW, by="actor.ea")
    sig.transition(SignalLifecycleStatus.ACCEPTED, by="actor.ea")
    sig.transition(SignalLifecycleStatus.RESOLVED, by="actor.ea")
    assert [h["to"] for h in sig.history] == [
        "open", "acknowledged", "in_review", "accepted", "resolved",
    ]
    assert sig.acknowledged_at is not None
    assert sig.resolved_at is not None


def test_lifecycle_dismissed_must_carry_rationale():
    sig = _signal()
    sig.transition(SignalLifecycleStatus.ACKNOWLEDGED, by="actor.ea")
    with pytest.raises(SignalError, match="rationale"):
        sig.transition(SignalLifecycleStatus.DISMISSED, by="actor.ea",
                       dismissed_rationale="")


def test_lifecycle_resolved_is_terminal():
    sig = _signal()
    sig.transition(SignalLifecycleStatus.ACKNOWLEDGED, by="actor.ea")
    sig.transition(SignalLifecycleStatus.RESOLVED, by="actor.ea")
    with pytest.raises(SignalError, match="not permitted"):
        sig.transition(SignalLifecycleStatus.OPEN)


# ------------------------------------------------------------ SignalStore
def _seed_store():
    store = SignalStore()
    store.register_observation(_observation())
    store.register_observation(_observation(
        id="obs.app-cmdb.2026-q3.federation-anomaly",
        subject="app.cs-platform",
        kind="federation-anomaly-detector@1.0.0",
        evidence=["adapter.cmdb-pulse.last-successful-sync.never"],
    ))
    store.raise_signal(_signal())
    store.raise_signal(_signal(
        id="sig.app-cmdb.2026-q3.federation-anomaly",
        observation_ref="obs.app-cmdb.2026-q3.federation-anomaly",
        classification=SignalClassification.FEDERATION_ANOMALY,
        severity=SignalSeverity.HIGH,
        confidence=SignalConfidence.EXACT,
        entities=["app.cs-platform"],
        owner="actor.integration-ops",
        rationale="CMDB adapter hasn't synced since 2026-08-19",
    ))
    return store


def test_store_rejects_signal_without_registered_observation():
    store = SignalStore()
    with pytest.raises(SignalStoreError, match="unknown observation"):
        store.raise_signal(_signal())


def test_store_rejects_duplicate_observation_id():
    store = SignalStore()
    store.register_observation(_observation())
    with pytest.raises(SignalStoreError, match="already registered"):
        store.register_observation(_observation())


def test_store_rejects_duplicate_signal_id():
    store = _seed_store()
    with pytest.raises(SignalStoreError, match="already registered"):
        store.raise_signal(_signal())


def test_store_lookups_by_owner_classification_and_status():
    store = _seed_store()
    assert {s.id for s in store.signals_by_owner("actor.enterprise-architect")} == {
        "sig.cap-cs.2026-q3.maturity-gap"}
    assert {s.id for s in store.signals_by_owner("actor.integration-ops")} == {
        "sig.app-cmdb.2026-q3.federation-anomaly"}
    assert {s.id for s in store.signals_by_status(SignalLifecycleStatus.OPEN)} == {
        "sig.cap-cs.2026-q3.maturity-gap",
        "sig.app-cmdb.2026-q3.federation-anomaly",
    }
    sigs = store.signals_by_classification(
        SignalClassification.MATURITY_GAP, SignalSeverity.MEDIUM)
    assert len(sigs) == 1 and sigs[0].id == "sig.cap-cs.2026-q3.maturity-gap"


def test_store_signals_for_entity_indexes_correctly():
    store = _seed_store()
    sigs = store.signals_for_entity("app.cs-platform")
    assert {s.id for s in sigs} == {"sig.app-cmdb.2026-q3.federation-anomaly"}


def test_store_rejects_non_canonical_lookup_keys():
    store = _seed_store()
    with pytest.raises(SignalStoreError, match="not canonical"):
        store.signals_by_owner("Owner-Bad")  # CR-8 §7 — uppercase not allowed
    with pytest.raises(SignalStoreError, match="not canonical"):
        store.signals_for_entity("not_canonical")  # underscore not in canonical pattern
    with pytest.raises(SignalStoreError, match="not canonical"):
        store.get_signal("123.bad")  # must start with letter


def test_store_len_and_contains():
    store = _seed_store()
    assert len(store) == 2
    assert "sig.cap-cs.2026-q3.maturity-gap" in store
    assert "nope" not in store


def test_signal_serialisation_round_trips_classification_and_severity():
    sig = _signal()
    d = sig.as_dict()
    assert d["classification"] == "maturity_gap"
    assert d["severity"] == "medium"
    assert d["status"] == "open"
    assert d["entities"] == ["cap.customer-service"]
    assert d["history"][0]["to"] == "open"