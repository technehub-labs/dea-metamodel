"""CR-11 Phase 1 — semantic interoperability foundation tests.

Phase-1 slice of the CR-11 Definition of Done:
- External systems are first-class integration concepts ✓
- Connectors and semantic adapters are distinct ✓
- External identifiers are preserved ✓
- Semantic mappings are versioned ✓
- Mapping confidence is represented ✓
- Mapping lossiness is represented ✓
- External extensions have namespaces ✓
"""
import pytest

from runtime.graph import Edge, InMemoryGraphStore, Node
from runtime.interoperability import (AdapterCapability, Exchange, Extension,
                                      ExternalIdentifier, ExternalSystem,
                                      GovernanceStatus, ImportMode,
                                      IntegrationAdapter, InteropError,
                                      InteropRegistry, Lossiness,
                                      MappingConfidence, MappingRelation,
                                      SemanticMapping, split_concept_ref)


@pytest.fixture()
def registry():
    reg = InteropRegistry()
    reg.register_system(ExternalSystem(
        id="system.servicenow", name="Service Management Platform",
        type="ITSM", provider="ServiceNow", version="2026.1",
        endpoint="https://cmdb.example.internal/api",
        authentication="vault://prod/servicenow-ro",
        classification="INTERNAL", owner="it-operations"))
    return reg


# ---- CR-11B: external systems ----

def test_external_system_first_class(registry):
    system = registry.systems["system.servicenow"]
    assert system.type == "ITSM"
    assert system.classification == "INTERNAL"


def test_credentials_never_inline():
    with pytest.raises(InteropError, match="CR-11AY"):
        ExternalSystem(id="system.bad", name="Bad", type="CMDB",
                       authentication="password=hunter2")


# ---- CR-11C/D: adapters vs connectors ----

def test_adapter_binds_system_and_declares_capabilities(registry):
    adapter = registry.register_adapter(IntegrationAdapter(
        id="adapter.servicenow-cmdb", name="ServiceNow CMDB Adapter",
        source="system.servicenow", protocol="REST", format="json",
        capabilities=[AdapterCapability.READ, AdapterCapability.IMPORT,
                      AdapterCapability.EVENT]))
    assert AdapterCapability.EVENT in adapter.capabilities
    assert adapter.protocol == "REST"  # the connector (transport)


def test_adapter_requires_registered_system(registry):
    with pytest.raises(InteropError, match="unregistered system"):
        registry.register_adapter(IntegrationAdapter(
            id="adapter.ghost", name="Ghost", source="system.ghost",
            protocol="SQL"))


# ---- CR-11E/F/G/H/AQ/AT/AU: mappings ----

def archimate_mapping(**kw):
    base = dict(
        source_concept="external:archimate.ApplicationComponent",
        target_concept="opendea:ApplicationComponent",
        relationship=MappingRelation.EQUIVALENT,
        confidence=MappingConfidence.HIGH,
        lossiness=Lossiness.PARTIAL,
        owner="ea-team", version="1.0.0",
        transformation="direct — names/properties carried verbatim",
        approved_by="architecture-board", effective_date="2026-08-18")
    base.update(kw)
    return SemanticMapping(**base)


def test_mapping_first_class_with_confidence_and_lossiness(registry):
    m = registry.register_mapping(archimate_mapping())
    d = m.as_dict()
    assert d["relationship"] == "EQUIVALENT"
    assert d["confidence"] == "High"
    assert d["lossiness"] == "PARTIAL"
    assert d["version"] == "1.0.0"  # mappings are versioned (CR-11AT)


def test_mapping_relationships_beyond_equals(registry):
    m = registry.register_mapping(archimate_mapping(
        source_concept="external:archimate.Plateau",
        target_concept="opendea:ArchitectureState",
        relationship=MappingRelation.RELATED_TO,
        confidence=MappingConfidence.MEDIUM, version="1.1.0"))
    assert m.relationship == MappingRelation.RELATED_TO


def test_mapping_target_must_be_canonical(registry):
    with pytest.raises(InteropError, match="DEA-E001"):
        registry.register_mapping(archimate_mapping(
            target_concept="opendea:NoSuchConcept", version="9.9.9"))


def test_no_correspondence_cannot_target_opendea(registry):
    with pytest.raises(InteropError, match="NO_CORRESPONDENCE"):
        registry.register_mapping(archimate_mapping(
            relationship=MappingRelation.NO_CORRESPONDENCE, version="1.2.0"))


def test_concept_refs_must_be_namespaced():
    with pytest.raises(InteropError, match="CR-11AS"):
        split_concept_ref("ApplicationComponent")
    assert split_concept_ref("external:X") == ("external", "X")


def test_superseded_requires_replacement():
    with pytest.raises(InteropError, match="replacement reference"):
        SemanticMapping(
            source_concept="external:a.B", target_concept="opendea:BusinessService",
            status=GovernanceStatus.SUPERSEDED)


def test_superseded_with_replacement_ok():
    m = SemanticMapping(
        source_concept="external:a.B", target_concept="opendea:BusinessService",
        status=GovernanceStatus.SUPERSEDED,
        superseded_by="external:a.B|opendea:BusinessService|2.0.0")
    assert m.as_dict()["supersededBy"].endswith("2.0.0")


# ---- CR-11I: canonical identity preserved ----

def test_external_identifier_links_never_adopts(registry):
    link = registry.link_external_identifier(ExternalIdentifier(
        system="system.servicenow", identifier="CI-001234",
        identifier_type="primary", entity="app.customer-platform"))
    assert link.entity == "app.customer-platform"
    assert registry.resolve("system.servicenow", "CI-001234") == "app.customer-platform"
    assert registry.resolve("system.servicenow", "UNKNOWN") is None


def test_external_id_rejected_as_canonical_identity(registry):
    with pytest.raises(InteropError, match="CR-11I"):
        registry.link_external_identifier(ExternalIdentifier(
            system="system.servicenow", identifier="CI-001234",
            entity="CI-001234"))  # not a canonical id


# ---- CR-11AR/AS: extensions stay external ----

def test_extension_external_namespace(registry):
    ext = registry.register_extension(Extension(
        namespace="external", name="vendorX:SpecializedCapability",
        definition="Vendor-specific capability concept with no OpenDEA equivalent",
        source="system.servicenow"))
    assert ext.ref == "external:vendorX:SpecializedCapability"


def test_extension_cannot_use_opendea_namespace():
    with pytest.raises(InteropError, match="opendea"):
        Extension(namespace="opendea", name="SneakyCoreEdit")


# ---- CR-11S/U/V: exchange envelope ----

def test_export_produces_canonical_exchange(registry):
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.customer-service",
                             type="BusinessCapability", name="Customer Service"))
    store.create_entity(Node(id="app.cs", type="ApplicationComponent", name="CS App"))
    store.create_relationship(Edge(type="supports", source="app.cs",
                                   target="cap.customer-service",
                                   provenance={"assertedBy": "architect-42"}))
    ex = registry.export(store, "exchange.2026-08-18", "system.ea-repo",
                         mapping_version="1.0.0")
    d = ex.as_dict()["exchange"]
    assert d["schemaVersion"] == "1.0.0"          # CR-11V
    assert d["mappingVersion"] == "1.0.0"         # CR-11V
    assert d["operation"] == "FULL_IMPORT"
    # CR-11U: canonical semantics, not internal layout — provenance survives
    rels = d["payload"]["relationships"]
    assert rels[0]["provenance"]["assertedBy"] == "architect-42"
    assert {e["id"] for e in d["payload"]["entities"]} == {"cap.customer-service", "app.cs"}
