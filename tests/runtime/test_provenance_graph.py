"""CR-9.2 — canonical provenance graph tests (CR-9O/P/T/BC)."""

import pytest

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.provenance import (AssertionStatus, ProvenanceError,
                                ProvenanceService)
from conftest import BASE


def _capability_store():
    store = InMemoryGraphStore()
    svc = RuntimeService(store)
    svc.create_entity("cap.customer-service", "BusinessCapability", "Customer Service")
    return store


def test_assertion_evidence_source_chain():
    """CR-9P/BC: Conclusion → Assertion → Evidence → Source is traversable."""
    store = _capability_store()
    prov = ProvenanceService(store)
    prov.register_source("src.cmdb", "Enterprise CMDB", system="ServiceNow")
    prov.register_evidence("ev.app-inventory", "Application Inventory", confidence=0.9)

    assertion = prov.assert_fact(
        "assertion.cap-maturity-current",
        subject="cap.customer-service",
        claim={"maturity": 2.7},
        asserted_by="architect-42",
        status=AssertionStatus.PROPOSED,
        confidence=0.92,
        evidence=["ev.app-inventory"],
        source="src.cmdb",
    )

    assert assertion.status == AssertionStatus.PROPOSED
    chain = prov.why("cap.customer-service")
    assert [a.id for a in chain.assertions] == ["assertion.cap-maturity-current"]
    assert [e.id for e in chain.evidence] == ["ev.app-inventory"]
    assert [s.id for s in chain.sources] == ["src.cmdb"]


def test_competing_assertions_coexist_without_mutating_subject():
    """CR-9O: multiple claims coexist; the underlying entity is not corrupted."""
    store = _capability_store()
    prov = ProvenanceService(store)
    prov.assert_fact("assertion.maturity-low", "cap.customer-service",
                     {"maturity": 2.4}, asserted_by="assessment-2025")
    prov.assert_fact("assertion.maturity-high", "cap.customer-service",
                     {"maturity": 3.1}, asserted_by="assessment-2026",
                     status=AssertionStatus.DISPUTED)

    assertions = prov.assertions_for("cap.customer-service")
    assert [a.id for a in assertions] == [
        "assertion.maturity-low", "assertion.maturity-high"]
    assert {a.claim["maturity"] for a in assertions} == {2.4, 3.1}
    assert store.get_entity("cap.customer-service").properties == {}


def test_approval_requires_explicit_transition():
    """CR-9CQ: no claim enters the graph already authoritative."""
    store = _capability_store()
    prov = ProvenanceService(store)
    with pytest.raises(ProvenanceError, match="cannot be created approved"):
        prov.assert_fact("assertion.immediate-approval", "cap.customer-service",
                         {"criticality": "high"}, asserted_by="agent-7",
                         status=AssertionStatus.APPROVED)


def test_assertion_status_transition_is_explicit_and_audited():
    """CR-9O/CQ: status changes are transitions with actor + history."""
    store = _capability_store()
    prov = ProvenanceService(store)
    prov.assert_fact("assertion.criticality", "cap.customer-service",
                     {"criticality": "high"}, asserted_by="agent-7")

    prov.transition_assertion("assertion.criticality", AssertionStatus.VERIFIED,
                              actor="architect-42", reason="inventory checked")
    prov.transition_assertion("assertion.criticality", AssertionStatus.APPROVED,
                              actor="ea-board", reason="board approval")

    assertion = prov.assertions_for("cap.customer-service")[0]
    assert assertion.status == AssertionStatus.APPROVED
    node = store.get_entity("assertion.criticality")
    assert [h["to"] for h in node.properties["status_history"]] == [
        "verified", "approved"]
    assert node.properties["approved_by"] == "ea-board"


def test_unregistered_evidence_and_source_are_rejected():
    """CR-9P: evidence/source chain links only registered provenance nodes."""
    store = _capability_store()
    prov = ProvenanceService(store)
    with pytest.raises(ProvenanceError, match="provenance evidence"):
        prov.assert_fact("assertion.missing-evidence", "cap.customer-service",
                         {"maturity": 2.7}, asserted_by="agent-7",
                         evidence=["ev.missing"])
    with pytest.raises(ProvenanceError, match="provenance source"):
        prov.assert_fact("assertion.missing-source", "cap.customer-service",
                         {"maturity": 2.7}, asserted_by="agent-7",
                         source="src.missing")


def test_direct_source_chain_without_evidence():
    """CR-9BC: a source may support an assertion directly when evidence is absent."""
    store = _capability_store()
    prov = ProvenanceService(store)
    prov.register_source("src.ea-repository", "EA Repository", system="Repository")
    prov.assert_fact("assertion.criticality", "cap.customer-service",
                     {"criticality": "high"}, asserted_by="architect-42",
                     source="src.ea-repository")

    chain = prov.why("cap.customer-service")
    assert chain.evidence == []
    assert [s.id for s in chain.sources] == ["src.ea-repository"]


def test_derived_assertion_keeps_derivation_provenance():
    """CR-9T seed: derived claims declare what they derived from and by which rule."""
    store = _capability_store()
    prov = ProvenanceService(store)
    base = prov.assert_fact("assertion.supports-objective", "cap.customer-service",
                            {"supports": "obj.customer-experience"},
                            asserted_by="architect-42")

    derived = prov.assert_fact(
        "assertion.strategic-capability", "cap.customer-service",
        {"classification": "strategic"}, asserted_by="rule-engine",
        derived_from=[base.id], derivation_rule="DEA-INF-007")

    edge = next(e for e in store.edges_of(derived.id, direction="out",
                                          rel_type="traces-to")
                if e.target == "cap.customer-service")
    assert edge.provenance["derived_from"] == [base.id]
    assert edge.provenance["derivation_rule"] == "DEA-INF-007"


def test_illegal_transition_is_rejected():
    """CR-9CQ: approval cannot skip the explicit verification transition."""
    store = _capability_store()
    prov = ProvenanceService(store)
    prov.assert_fact("assertion.criticality", "cap.customer-service",
                     {"criticality": "high"}, asserted_by="agent-7")
    with pytest.raises(ProvenanceError, match="illegal assertion transition"):
        prov.transition_assertion("assertion.criticality", AssertionStatus.APPROVED,
                                  actor="ea-board")


def test_loaded_canonical_evidence_graph_is_explainable():
    """CR-9P + loader: canonical Evidence -supports→ Result joins the Why chain."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "golden" / "dmm.yaml", store)

    chain = ProvenanceService(store).why("ar.cs-001")

    assert [e.id for e in chain.evidence] == ["ev.inventory"]
    assert chain.evidence[0].type == "Evidence"
