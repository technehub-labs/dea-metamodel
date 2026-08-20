"""CR-11 Phase 3 — Exchange service (CR-11S/T/U/V/AN/AP).

JSON Schema for the CR-11 Phase 1 Exchange envelope, plus `export` /
`import` against any GraphStore, plus validation and round-trip preservation.
"""
from __future__ import annotations

import jsonschema
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..api import RuntimeService
from ..graph import Edge, GraphStore, Node
from ..scenario.engine import snapshot_store
from ..interoperability import (Exchange, ExternalIdentifier,
                                ImportMode, InteropError,
                                InteropRegistry)


class ExchangeError(Exception):
    """Exchange service invariant violated."""


EXCHANGE_JSON_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "OpenDEA Exchange Envelope",
    "type": "object",
    "required": ["exchange"],
    "properties": {
        "exchange": {
            "type": "object",
            "required": [
                "id", "source", "target", "operation", "payload",
                "schemaVersion",
            ],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "source": {"type": "string", "minLength": 1},
                "target": {"type": "string", "minLength": 1},
                "operation": {
                    "type": "string",
                    "enum": [
                        "FULL_IMPORT", "INCREMENTAL_IMPORT", "DELTA_IMPORT",
                        "EVENT_IMPORT", "ON_DEMAND_QUERY",
                    ],
                },
                "payload": {
                    "type": "object",
                    "required": ["entities", "relationships"],
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["id", "type", "name"],
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string"},
                                    "name": {"type": "string"},
                                    "version": {"type": ["string", "null"]},
                                    "lifecycle_status": {"type": ["string", "null"]},
                                    "properties": {"type": ["object", "null"]},
                                    "assertion": {"type": ["object", "null"]},
                                    "source": {"type": ["object", "null"]},
                                },
                            },
                        },
                        "relationships": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "source", "target"],
                                "properties": {
                                    "type": {"type": "string"},
                                    "source": {"type": "string"},
                                    "target": {"type": "string"},
                                    "valid_from": {"type": ["string", "null"]},
                                    "valid_to": {"type": ["string", "null"]},
                                    "status": {"type": ["string", "null"]},
                                    "provenance": {"type": ["object", "null"]},
                                },
                            },
                        },
                    },
                },
                "schemaVersion": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                "profileVersions": {"type": "object"},
                "mappingVersion": {"type": "string"},
                "provenance": {"type": "object"},
                "timestamp": {"type": "string"},
            },
        },
    },
}


def exchange_json_schema() -> Dict[str, Any]:
    return dict(EXCHANGE_JSON_SCHEMA)


@dataclass(frozen=True)
class ExchangeSummary:
    imported_entities: int
    imported_edges: int
    imported_external_identifiers: int
    source: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "importedEntities": self.imported_entities,
            "importedEdges": self.imported_edges,
            "importedExternalIdentifiers": self.imported_external_identifiers,
            "source": self.source,
        }


class ExchangeService:
    """CR-11S/T/U/V — runtime import/export of canonical exchanges."""

    def __init__(self, registry: InteropRegistry):
        self.registry = registry

    def export_graph(self, store: GraphStore, target: str,
                     source: str = "opendea") -> Exchange:
        snap = snapshot_store(store)
        payload = {
            "entities": [
                {
                    "id": n["id"],
                    "type": n["type"],
                    "name": n["name"],
                    "version": n.get("version", "1.0.0"),
                    "lifecycle_status": n.get("lifecycle_status"),
                    "properties": n.get("properties", {}),
                    "assertion": n.get("assertion", {}),
                    "source": n.get("source", {}),
                } for n in snap["nodes"]
            ],
            "relationships": [
                {
                    "type": r["type"],
                    "source": r["source"],
                    "target": r["target"],
                    "valid_from": r.get("valid_from"),
                    "valid_to": r.get("valid_to"),
                    "status": r.get("status"),
                    "provenance": r.get("provenance", {}),
                } for r in snap["edges"]
            ],
        }
        return Exchange(
            id=f"exchange.export.{source}.to.{target}",
            source=source,
            target=target,
            operation=ImportMode.FULL,
            payload=payload,
            schema_version="1.0.0",
            profile_versions={"dea:core": "1.0.0"},
            mapping_version="",
            provenance={"exportedBy": "runtime.interop"},
        )

    def import_exchange(self, exchange: Exchange, store: GraphStore,
                        source: Optional[str] = None) -> ExchangeSummary:
        src = source or exchange.source
        if src not in self.registry.systems and src != "opendea":
            raise ExchangeError(
                f"unknown external source {src!r} — refusing to import")
        entities = exchange.payload.get("entities", [])
        relationships = exchange.payload.get("relationships", [])
        existing = {n.id for n in store.query()}
        imported_entities = 0
        for ent in entities:
            if ent["id"] in existing:
                continue
            store.create_entity(Node(
                id=ent["id"],
                type=ent["type"],
                name=ent["name"],
                version=ent.get("version", "1.0.0"),
                lifecycle_status=ent.get("lifecycle_status"),
                assertion=ent.get("assertion", {}),
                source={**ent.get("source", {}), "sourceSystem": src},
                properties=ent.get("properties", {}),
            ))
            imported_entities += 1

        existing_edge_keys: set = set()
        for n_id in (ent["id"] for ent in entities):
            if not store.has_entity(n_id):
                continue
            for edge in store.edges_of(n_id, direction="both"):
                existing_edge_keys.add((edge.source, edge.type, edge.target))
        imported_edges = 0
        for rel in relationships:
            key = (rel["source"], rel["type"], rel["target"])
            if key in existing_edge_keys:
                continue
            store.create_relationship(Edge(
                type=rel["type"],
                source=rel["source"],
                target=rel["target"],
                valid_from=rel.get("valid_from"),
                valid_to=rel.get("valid_to"),
                status=rel.get("status"),
                provenance=rel.get("provenance", {}),
            ))
            imported_edges += 1

        external_count = 0
        if src in self.registry.systems:
            for ent in entities:
                try:
                    self.registry.link_external_identifier(ExternalIdentifier(
                        system=src, identifier=ent["id"],
                        entity=ent["id"], identifier_type="primary",
                    ))
                    external_count += 1
                except InteropError:
                    pass

        return ExchangeSummary(
            imported_entities=imported_entities,
            imported_edges=imported_edges,
            imported_external_identifiers=external_count,
            source=src,
        )

    def validate(self, exchange: Exchange) -> List[str]:
        errors: List[str] = []
        if not exchange.id:
            errors.append("exchange.id is required")
        if not exchange.source:
            errors.append("exchange.source is required")
        if not exchange.target:
            errors.append("exchange.target is required")
        if not exchange.schema_version:
            errors.append("exchange.schemaVersion is required")
        if not isinstance(exchange.payload, dict):
            errors.append("exchange.payload must be an object")
            return errors
        entities = exchange.payload.get("entities")
        relationships = exchange.payload.get("relationships")
        if not isinstance(entities, list):
            errors.append("exchange.payload.entities must be a list")
        if not isinstance(relationships, list):
            errors.append("exchange.payload.relationships must be a list")
        try:
            jsonschema.validate(exchange.as_dict(),
                                exchange_json_schema())
        except jsonschema.ValidationError as exc:
            errors.append(str(exc))
        except jsonschema.SchemaError:
            pass
        return errors
