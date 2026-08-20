"""CR-11 Phase 3 — Exchange service tests."""
import json
import pytest

from runtime.api import RuntimeService
from runtime.graph import Edge, InMemoryGraphStore, Node
from runtime.interoperability import (Exchange, ExternalIdentifier,
                                       ExternalSystem, ImportMode,
                                       InteropRegistry, SemanticMapping)
from runtime.interop.exchange_service import (ExchangeError, ExchangeService,
                                                exchange_json_schema)


def _registry():
    reg = InteropRegistry()
    reg.register_system(ExternalSystem(
        id="system.servicenow", name="ServiceNow", type="CMDB"))
    return reg


def test_exchange_json_schema_is_well_formed():
    schema = exchange_json_schema()
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert "properties" in schema
    assert "exchange" in schema["properties"]


def test_export_produces_canonical_envelope():
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("app.cs", "ApplicationComponent", "CS Platform")
    service.create_entity("cap.cs", "BusinessCapability", "CS Capability")
    service.create_relationship("app.cs", "supports", "cap.cs", status="active")
    registry = _registry()
    svc = ExchangeService(registry)

    exchange = svc.export_graph(service.store, target="system.servicenow",
                                  source="opendea")

    assert isinstance(exchange, Exchange)
    assert exchange.source == "opendea"
    assert exchange.target == "system.servicenow"
    payload = exchange.payload
    assert "app.cs" in {n["id"] for n in payload["entities"]}
    assert "cap.cs" in {n["id"] for n in payload["entities"]}
    assert any(r["type"] == "supports" for r in payload["relationships"])


def test_validate_passes_canonical_envelope():
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("app.cs", "ApplicationComponent", "CS Platform")
    registry = _registry()
    svc = ExchangeService(registry)

    exchange = svc.export_graph(service.store, target="system.servicenow",
                                  source="opendea")
    errors = svc.validate(exchange)
    assert errors == []


def test_validate_rejects_missing_required_fields():
    service = RuntimeService(InMemoryGraphStore())
    registry = _registry()
    svc = ExchangeService(registry)
    bad = Exchange(
        id="",  # empty id is invalid
        source="opendea",
        target="system.servicenow",
        operation=ImportMode.FULL,
        payload={},
        schema_version="1.0.0",
    )
    errors = svc.validate(bad)
    assert any("id" in e for e in errors)


def test_import_round_trip_preserves_entities_and_edges():
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("app.cs", "ApplicationComponent", "CS Platform")
    service.create_entity("cap.cs", "BusinessCapability", "CS Capability")
    service.create_relationship("app.cs", "supports", "cap.cs", status="active")
    registry = _registry()
    svc = ExchangeService(registry)

    exchange = svc.export_graph(service.store, target="system.servicenow",
                                  source="opendea")
    target_store = InMemoryGraphStore()
    summary = svc.import_exchange(exchange, target_store, source="system.servicenow")
    assert summary.imported_entities == 2
    assert summary.imported_edges == 1
    assert target_store.has_entity("app.cs")
    assert target_store.has_entity("cap.cs")


def test_import_records_external_identifier_link():
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("app.cs", "ApplicationComponent", "CS Platform")
    registry = _registry()
    svc = ExchangeService(registry)

    exchange = svc.export_graph(service.store, target="system.servicenow",
                                  source="opendea")
    target_store = InMemoryGraphStore()
    svc.import_exchange(exchange, target_store, source="system.servicenow")

    assert registry.resolve("system.servicenow", "app.cs") == "app.cs"
