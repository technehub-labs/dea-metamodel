"""CR-9.5 integration tests."""

import pytest

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.integration import IntegrationService
from runtime.interoperability import (ExternalIdentifier, ExternalSystem,
                                      IntegrationAdapter,
                                      InteropRegistry, SemanticMapping)


def _registry():
    reg = InteropRegistry()
    reg.register_system(ExternalSystem(id="system.servicenow",
                                       name="ServiceNow CMDB", type="CMDB"))
    reg.register_system(ExternalSystem(id="system.leanix",
                                       name="LeanIX", type="EA_REPOSITORY"))
    reg.register_adapter(IntegrationAdapter(
        id="adapter.servicenow-cmdb",
        name="ServiceNow CMDB Adapter",
        source="system.servicenow",
        protocol="REST", format="json",
        capabilities=["READ", "IMPORT"]))
    reg.register_mapping(SemanticMapping(
        source_concept="external:archimate.ApplicationComponent",
        target_concept="opendea:ApplicationComponent"))
    return reg


def test_integration_service_runs_full_import_into_a_clean_store():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    registry = _registry()
    integration = IntegrationService(registry, service=service)

    report = integration.run_full_import("system.servicenow", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS Platform",
         "lifecycle_status": "active",
         "properties": {"vendor": "legacy-vendor"}},
        {"id": "cap.cs", "type": "BusinessCapability", "name": "Customer Service"},
    ], source_tag="cmdb")

    assert report.imported == 2
    assert report.skipped == 0
    assert service.get_entity("app.cs").type == "ApplicationComponent"
    assert service.get_entity("app.cs").properties["sourceSystem"] == "system.servicenow"


def test_integration_incremental_import_skips_already_known_entities():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    registry = _registry()
    integration = IntegrationService(registry, service=service)

    integration.run_full_import("system.servicenow", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS Platform"}],
        source_tag="cmdb")
    second = integration.run_incremental_import("system.servicenow", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS Platform"},
        {"id": "app.new", "type": "ApplicationComponent", "name": "New"}])

    assert second.imported == 1
    assert second.skipped == 1


def test_integration_records_source_metadata_on_imported_entities():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    registry = _registry()
    integration = IntegrationService(registry, service=service)

    integration.run_full_import("system.servicenow", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS",
         "external_id": "CI-001"}], source_tag="cmdb")

    node = service.get_entity("app.cs")
    assert node.properties["sourceSystem"] == "system.servicenow"
    assert node.properties["sourceRecord"] == "CI-001"
    assert node.source["sourceSystem"] == "system.servicenow"


def test_integration_links_external_identifier_to_canonical_entity():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    registry = _registry()
    integration = IntegrationService(registry, service=service)

    integration.run_full_import("system.servicenow", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS",
         "external_id": "CI-001"}], source_tag="cmdb")

    assert registry.resolve("system.servicenow", "CI-001") == "app.cs"
    assert service.get_entity("app.cs").id == "app.cs"
    assert service.get_entity("app.cs").id != "CI-001"


def test_integration_record_conflict_when_sources_disagree():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    registry = _registry()
    integration = IntegrationService(registry, service=service)

    integration.run_full_import("system.servicenow", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS",
         "external_id": "CI-001", "lifecycle_state": "RETIRED"}],
        source_tag="cmdb")
    integration.run_full_import("system.leanix", [
        {"id": "app.cs", "type": "ApplicationComponent", "name": "CS",
         "external_id": "FS-987", "lifecycle_state": "active"}],
        source_tag="ea")

    conflicts = registry.conflicts
    assert any(c.entity == "app.cs" and c.property == "lifecycle_state"
               for c in conflicts)
