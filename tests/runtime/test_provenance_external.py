"""CR-11 Phase 4 — external provenance (CR-11O/AE/BD)."""

import pytest

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.interoperability import (AdapterCapability, ExternalIdentifier,
                                       ExternalSystem, GovernanceStatus,
                                       ImportMode, IntegrationAdapter,
                                       InteropRegistry, Lossiness,
                                       MappingConfidence, MappingRelation,
                                       Namespace, SemanticMapping)
from runtime.provenance import (AssertionStatus, ExternalProvenanceService,
                                ProvenanceService)
from conftest import BASE


def _setup_store():
    store = InMemoryGraphStore()
    svc = RuntimeService(store)
    svc.create_entity("cap.customer-service", "BusinessCapability",
                      "Customer Service")
    return store, InteropRegistry()


def _seed_servicenow(registry):
    """Register a ServiceNow system + adapter + mapping (CR-11B/C/D/E)."""
    registry.register_system(ExternalSystem(
        id="itsm.servicenow",
        name="ServiceNow ITSM",
        type="ITSM",
        provider="ServiceNow",
        version="vancouver",
        classification="INTERNAL",
        owner="integration-team",
    ))
    registry.register_adapter(IntegrationAdapter(
        id="adapter.servicenow-import",
        name="ServiceNow OpenDEA importer",
        source="itsm.servicenow",
        protocol="REST",
        format="json",
        capabilities=[AdapterCapability.IMPORT],
        version="1.0.0",
        status=GovernanceStatus.ACTIVE,
    ))
    registry.register_mapping(SemanticMapping(
        source_concept="servicenow:cmdb_ci",
        target_concept="opendea:ApplicationComponent",
        relationship=MappingRelation.MAPS_TO,
        transformation="identifier → canonical id",
        confidence=MappingConfidence.EXACT,
        lossiness=Lossiness.LOSSLESS,
        owner="mapping-team",
        version="1.0.0",
        status=GovernanceStatus.ACTIVE,
        approved_by="architect-42",
        effective_date="2025-01-01",
    ))


def test_cr_11o_evidence_preserved_with_external_source():
    """CR-11O — the external source is preserved through normalisation."""
    store, registry = _setup_store()
    _seed_servicenow(registry)
    prov = ExternalProvenanceService(store, registry)

    captured = prov.record_external_source(
        evidence_id="ev.snow.cmdb-app-42",
        source_id="src.snow.cmdb",
        external_identifier=ExternalIdentifier(
            system="itsm.servicenow",
            identifier="cmdb_ci:0a82e2",
            entity="cap.customer-service",
            identifier_type="primary",
        ),
    )

    evidence = captured["evidence"]
    source = captured["source"]

    assert evidence.properties["externalIdentifier"] == "cmdb_ci:0a82e2"
    assert evidence.properties["capturedFrom"] == "itsm.servicenow"
    assert source.properties["system"] == "itsm.servicenow"
    assert source.properties["externalIdentifier"] == "cmdb_ci:0a82e2"

    assertion = prov.provenance.assert_fact(
        "assertion.snow.maturity",
        subject="cap.customer-service",
        claim={"maturity": 3.0},
        asserted_by="snow-import-1",
        status=AssertionStatus.PROPOSED,
        confidence=0.95,
        evidence=["ev.snow.cmdb-app-42"],
        source="src.snow.cmdb",
    )
    chain = prov.provenance.why("cap.customer-service")
    assert [a.id for a in chain.assertions] == ["assertion.snow.maturity"]
    assert [e.id for e in chain.evidence] == ["ev.snow.cmdb-app-42"]
    # External identifier survives through evidence → source → assertion
    assert chain.evidence[0].properties["externalIdentifier"] == "cmdb_ci:0a82e2"


def test_cr_11o_rejects_duplicate_link():
    """CR-11I — re-linking the same external record raises."""
    store, registry = _setup_store()
    _seed_servicenow(registry)
    prov = ExternalProvenanceService(store, registry)
    prov.record_external_source(
        "ev.snow.once",
        "src.snow.once",
        ExternalIdentifier(
            system="itsm.servicenow", identifier="cmdb_ci:0a82e2",
            entity="cap.customer-service", identifier_type="primary"),
    )
    with pytest.raises(Exception):
        prov.record_external_source(
            "ev.snow.twice",
            "src.snow.twice",
            ExternalIdentifier(
                system="itsm.servicenow", identifier="cmdb_ci:0a82e2",
                entity="cap.customer-service", identifier_type="primary"),
        )


def test_cr_11ae_prov_projection_carries_core_concepts():
    """CR-11AE — assertion projects to Entity / Activity / Agent / Source."""
    store, registry = _setup_store()
    _seed_servicenow(registry)
    prov = ExternalProvenanceService(store, registry)

    prov.record_external_source(
        "ev.snow.prov",
        "src.snow.prov",
        ExternalIdentifier(
            system="itsm.servicenow", identifier="cmdb_ci:0a82e2",
            entity="cap.customer-service", identifier_type="primary"),
    )
    prov.provenance.assert_fact(
        "assertion.snow.prov",
        subject="cap.customer-service",
        claim={"maturity": 3.0},
        asserted_by="snow-import-1",
        status=AssertionStatus.VERIFIED,
        confidence=0.92,
        evidence=["ev.snow.prov"],
        source="src.snow.prov",
    )

    prov_map = prov.prov_projection("assertion.snow.prov")
    d = prov_map.as_dict()
    assert d["provEntity"] == "cap.customer-service"
    assert d["provActivity"] == "activity.assertion.snow.prov"
    assert d["provAgent"] == "snow-import-1"
    assert d["provSource"] == "src.snow.prov"
    assert d["provUsed"] == ["ev.snow.prov"]


def test_cr_11bd_integration_chain_walks_through_adapter_mapping_system():
    """CR-11BD — entity → assertion → evidence → mapping → adapter → ext id → system."""
    store, registry = _setup_store()
    _seed_servicenow(registry)
    prov = ExternalProvenanceService(store, registry)

    prov.record_external_source(
        "ev.snow.chain",
        "src.snow.chain",
        ExternalIdentifier(
            system="itsm.servicenow", identifier="cmdb_ci:0a82e2",
            entity="cap.customer-service", identifier_type="primary"),
    )
    prov.provenance.assert_fact(
        "assertion.snow.chain",
        subject="cap.customer-service",
        claim={"maturity": 3.0},
        asserted_by="snow-import-1",
        status=AssertionStatus.VERIFIED,
        confidence=0.92,
        evidence=["ev.snow.chain"],
        source="src.snow.chain",
    )

    chain = prov.integration_chain("cap.customer-service")
    roles = [link.role for link in chain.links]
    # The chain MUST reach the external system, anchored on the assertion.
    assert roles[0] == "assertion"
    assert "external-system" in roles
    assert "external-identifier" in roles
    # Asserts every canonical hop is present.
    assert "evidence" in roles
    assert "mapping" in roles
    assert "adapter" in roles

    payload = chain.as_dict()
    by_role = {l["role"]: l for l in payload["links"]}
    assert by_role["external-system"]["id"] == "itsm.servicenow"
    assert by_role["external-system"]["type"] == "ExternalSystem"
    assert by_role["adapter"]["id"] == "adapter.servicenow-import"
    assert by_role["mapping"]["provenanceKind"] == "mapping"
    assert any(ei["identifier"] == "cmdb_ci:0a82e2"
               for ei in payload["externalIdentifiers"])


def test_cr_11bd_chain_without_external_link_only_carries_canonical():
    """A subject without any external source has the canonical chain only.

    The BD chain never invents external-system hops when none were recorded —
    the absence of external provenance is itself a meaningful answer.
    """
    store, _ = _setup_store()
    prov = ExternalProvenanceService(store)
    prov.provenance.register_source("src.snow.manual",
                                    "Manual capture", system="manual")
    prov.provenance.register_evidence("ev.manual", "Manual review")
    prov.provenance.assert_fact(
        "assertion.manual",
        subject="cap.customer-service",
        claim={"maturity": 2.5},
        asserted_by="architect-42",
        status=AssertionStatus.VERIFIED,
        evidence=["ev.manual"],
        source="src.snow.manual",
    )
    chain = prov.integration_chain("cap.customer-service")
    roles = [link.role for link in chain.links]
    assert roles[0] == "assertion"
    assert "external-system" not in roles
    assert "external-identifier" not in roles
    assert chain.external_systems == []
