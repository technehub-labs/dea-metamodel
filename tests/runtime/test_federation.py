"""CR-11 Phase 7 — Federation (CR-11AH/AI/AJ + AK boundary)."""

import pytest

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.interoperability import (AuthorityPolicy, ExternalIdentifier,
                                       ExternalSystem, InteropRegistry)
from runtime.federation import (AuthorityContext, EntityLocality,
                                 FederatedQuery, FederatedReference,
                                 FederationError, FederationView,
                                 QueryDispatchResult, ResolutionStrategy,
                                 SourceResolver, RemoteSource)
from runtime.federation.service import (DirectQueryAdapter, InGraphResolver)
from conftest import BASE


# ---------------------------------------------------------------- fixtures


def _seed():
    store = InMemoryGraphStore()
    rt = RuntimeService(store)
    rt.create_entity("cap.customer-service", "BusinessCapability",
                     "Customer Service")
    rt.create_entity("app.callcenter", "ApplicationComponent",
                     "Call Center Platform")
    reg = InteropRegistry()
    reg.register_system(ExternalSystem(id="itsm.servicenow",
                                        name="ServiceNow", type="ITSM"))
    reg.register_system(ExternalSystem(id="ea.leanscape",
                                        name="LeanScape EA", type="EA_REPO"))
    return store, reg


# ---------------------------------------------------------------- CR-11AI


def test_entity_locality_vocabulary_is_canonical():
    """CR-11AI — EntityLocality exposes the five canonical states."""
    assert EntityLocality.LOCAL.value == "LOCAL"
    assert EntityLocality.FEDERATED.value == "FEDERATED"
    assert EntityLocality.IMPORTED.value == "IMPORTED"
    assert EntityLocality.DERIVED.value == "DERIVED"
    assert EntityLocality.VIRTUAL.value == "VIRTUAL"


def test_federated_reference_rejects_incomplete_references():
    """A FederatedReference requires system, adapter, external_identifier."""
    with pytest.raises(FederationError):
        FederatedReference(system="", adapter="adapter.x",
                            external_identifier="snow:1")
    with pytest.raises(FederationError):
        FederatedReference(system="itsm.servicenow", adapter="",
                            external_identifier="snow:1")
    with pytest.raises(FederationError):
        FederatedReference(system="itsm.servicenow", adapter="adapter.x",
                            external_identifier="")


def test_federated_query_requires_subject_and_validates_strategy():
    q = FederatedQuery(subject="cap.x")
    assert q.strategy == ResolutionStrategy.IN_GRAPH_FIRST
    with pytest.raises(FederationError):
        FederatedQuery(subject="")
    with pytest.raises(FederationError):
        FederatedQuery(subject="cap.x", strategy="optical-fibre")


# ---------------------------------------------------------------- CR-11AH


def test_federation_view_serves_in_graph_first_when_local_present():
    """IN_GRAPH_FIRST prefers the local answer — CR-11AH bound dispatch."""
    store, reg = _seed()
    view = FederationView(store, reg)
    res = view.dispatch(FederatedQuery(subject="cap.customer-service"))
    assert res.strategy == ResolutionStrategy.IN_GRAPH_FIRST
    assert len(res.records) == 1
    assert res.records[0]["source"] == "opendea"
    assert res.records[0]["locality"] == "IN_GRAPH"
    assert res.authority.chosen_source == "opendea"


def test_federation_view_annotates_when_no_resolver_binds():
    """IN_GRAPH_FIRST with no remote adapter produces an annotated empty."""
    store, reg = _seed()
    view = FederationView(store, reg)
    res = view.dispatch(FederatedQuery(
        subject="app.nonexistent",
        include_sources=["itsm.servicenow"]))
    assert res.records == []
    assert any("no answer" in n for n in res.notes)


def test_federation_view_resolves_remote_reference_through_registry():
    """bind_remote → references resolve through the bound resolver."""
    store, reg = _seed()
    reg.link_external_identifier(ExternalIdentifier(
        system="itsm.servicenow", identifier="cmdb_ci:0a82e2",
        entity="cap.customer-service", identifier_type="primary"))

    class InMemoryRemote(SourceResolver):
        def resolve(self, reference, *, filters=None):
            return {
                "entity": "cap.customer-service",
                "source": reference.system,
                "externalIdentifier": reference.external_identifier,
                "adapter": reference.adapter,
                "locality": "REMOTE",
                "synthetic": True,
            }
    view = FederationView(store, reg)
    view.bind_remote("itsm.servicenow",
                     RemoteSource(system="itsm.servicenow",
                                   adapter="adapter.snow",
                                   resolver=InMemoryRemote()))
    res = view.dispatch(FederatedQuery(
        subject="cmdb_ci:0a82e2",
        include_sources=["itsm.servicenow"]))
    assert any(r.get("synthetic") for r in res.records)
    assert res.authority.chosen_source in {"itsm.servicenow", "opendea"}


# ---------------------------------------------------------------- CR-11AJ


def test_query_adapter_translates_via_declared_sources():
    """CR-11AJ — DirectQueryAdapter iterates declared sources in order."""
    store, reg = _seed()
    view = FederationView(store, reg, adapter=DirectQueryAdapter())

    class TagResolver(SourceResolver):
        def __init__(self, tag): self.tag = tag
        def resolve(self, reference, *, filters=None):
            return {"entity": self.tag, "source": reference.system,
                    "adapter": reference.adapter,
                    "externalIdentifier": reference.external_identifier,
                    "locality": "REMOTE"}

    view.bind_remote("itsm.servicenow",
                     RemoteSource(system="itsm.servicenow",
                                   adapter="adapter.snow",
                                   resolver=TagResolver("from_snow")))
    view.bind_remote("ea.leanscape",
                     RemoteSource(system="ea.leanscape",
                                   adapter="adapter.ea",
                                   resolver=TagResolver("from_ea")))
    # Subject NOT in the local graph, so the SOURCE_PRIORITY strategy
    # produces the first declared non-empty answer rather than the local.
    res = view.dispatch(FederatedQuery(
        subject="ext:nonexistent",
        include_sources=["ea.leanscape", "itsm.servicenow"],
        strategy=ResolutionStrategy.SOURCE_PRIORITY,
    ))
    sources = [r.get("source") for r in res.records]
    assert "ea.leanscape" in sources  # first declared wins under priority


# ---------------------------------------------------------------- CR-11AK


def test_merged_strategy_returns_union_of_local_and_remote():
    """MERGED strategy yields a union WITHOUT dropping duplicates silently."""
    store, reg = _seed()
    view = FederationView(store, reg)

    class EchoResolver(SourceResolver):
        def resolve(self, reference, *, filters=None):
            return {"entity": "cap.customer-service",
                    "source": reference.system,
                    "externalIdentifier": reference.external_identifier,
                    "locality": "REMOTE"}
    view.bind_remote("itsm.servicenow",
                     RemoteSource(system="itsm.servicenow",
                                   adapter="adapter.snow",
                                   resolver=EchoResolver()))
    res = view.dispatch(FederatedQuery(
        subject="cap.customer-service",
        include_sources=["itsm.servicenow"],
        strategy=ResolutionStrategy.MERGED))
    # Union — local answer (opendea) and remote answer (itsm.servicenow).
    sources = {r.get("source") for r in res.records}
    assert sources == {"opendea", "itsm.servicenow"}


def test_authority_policy_is_explicit_and_visible_in_result():
    """AuthorityPolicy is recorded on the result, never silently assumed."""
    store, reg = _seed()
    # No policy bound.
    view = FederationView(store, reg)
    res = view.dispatch(FederatedQuery(
        subject="cap.customer-service", authority_policy="policy.unknown"))
    assert any("no explicit authority" in n for n in res.notes)

    # A policy that resolves.
    reg.register_authority_policy(AuthorityPolicy(
        id="policy.cap-default", scope="global",
        weights={("itsm.servicenow", "maturity"): 0.7,
                 ("ea.leanscape", "maturity"): 0.3}))
    res = view.dispatch(FederatedQuery(
        subject="cap.customer-service", authority_policy="policy.cap-default"))
    assert res.authority.policy == "policy.cap-default"
    assert set(res.authority.weights) == {
        "itsm.servicenow/maturity", "ea.leanscape/maturity"}


def test_bind_remote_rejects_unregistered_systems():
    """CR-11AH — remote bindings require a registered ExternalSystem first."""
    store, reg = _seed()
    class TagResolver(SourceResolver):
        def resolve(self, reference, *, filters=None): return {}
    view = FederationView(store, reg)
    with pytest.raises(FederationError):
        view.bind_remote("unknown.system",
                         RemoteSource(system="unknown.system",
                                       adapter="adapter.x",
                                       resolver=TagResolver()))
    # Mismatched binding key is also caught.
    with pytest.raises(FederationError):
        view.bind_remote("itsm.servicenow",
                         RemoteSource(system="ea.leanscape",
                                       adapter="adapter.x",
                                       resolver=TagResolver()))


# ---------------------------------------------------------------- query adapter contract


def test_query_adapter_contract_does_not_invent_identifiers():
    """The DirectQueryAdapter only echoes remote answers — never invents them."""
    store, reg = _seed()
    view = FederationView(store, reg)

    class NotFoundResolver(SourceResolver):
        def resolve(self, reference, *, filters=None): return None
    view.bind_remote("itsm.servicenow",
                     RemoteSource(system="itsm.servicenow",
                                   adapter="adapter.snow",
                                   resolver=NotFoundResolver()))
    res = view.dispatch(FederatedQuery(
        subject="cap.unknown",
        include_sources=["itsm.servicenow"]))
    assert res.records == []
    assert any("no answer" in n for n in res.notes)


def test_in_graph_resolver_returns_record_for_opendea_reference():
    """InGraphResolver probes the local graph as a federated reference."""
    store, reg = _seed()
    resolver = InGraphResolver(store, reg)
    out = resolver.resolve(FederatedReference(
        system="opendea", adapter="in-graph",
        external_identifier="cap.customer-service"))
    assert out is not None
    assert out["entity"] == "cap.customer-service"


def test_federation_view_resolve_reference_helper():
    """resolve_reference is the single-call entry point."""
    store, reg = _seed()
    view = FederationView(store, reg)
    out = view.resolve_reference(FederatedReference(
        system="opendea", adapter="in-graph",
        external_identifier="cap.customer-service"))
    assert out and out["entity"] == "cap.customer-service"
    # Unregistered system returns None — never raises.
    out = view.resolve_reference(FederatedReference(
        system="itsm.servicenow", adapter="adapter.snow",
        external_identifier="cmdb_ci:0a82e2"))
    assert out is None
