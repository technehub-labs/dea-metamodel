"""CR-11 Phase 1 — interoperability registry and canonical exchange.

The InteropRegistry is where Sources, Adapters, Mappings, ExternalIdentifiers
and Extensions are registered and *governed* (CR-11AT: mappings are governed
assets). It enforces the Phase-1 invariants:

- concept references are namespaced (CR-11AS);
- opendea: targets resolve against the canonical registry — a mapping cannot
  point at a concept that does not exist;
- extensions never use the opendea: namespace (CR-11AR);
- adapters reference registered systems;
- external identifiers are never adopted as canonical identity (CR-11I);
- mapping supersession requires a replacement reference (CR-11AU).

export() produces a canonical Exchange from any GraphStore — the seed of the
CR-11T JSON exchange format (full schema/validation lands in Phase 3).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..api.service import Registry
from ..graph import GraphStore
from ..scenario.engine import snapshot_store
from .model import (Exchange, Extension, ExternalIdentifier, ExternalSystem,
                    ImportMode, IntegrationAdapter, InteropError, MappingRelation,
                    SemanticMapping, split_concept_ref)


class InteropRegistry:
    """Registered, governed interoperability assets."""

    def __init__(self):
        self.systems: Dict[str, ExternalSystem] = {}
        self.adapters: Dict[str, IntegrationAdapter] = {}
        self.mappings: Dict[str, SemanticMapping] = {}
        self.identifiers: List[ExternalIdentifier] = []
        self.extensions: Dict[str, Extension] = {}

    # ---- sources ----
    def register_system(self, system: ExternalSystem) -> ExternalSystem:
        if system.id in self.systems:
            raise InteropError(f"external system {system.id!r} already registered")
        self.systems[system.id] = system
        return system

    # ---- adapters ----
    def register_adapter(self, adapter: IntegrationAdapter) -> IntegrationAdapter:
        if adapter.source not in self.systems:
            raise InteropError(
                f"adapter {adapter.id!r} references unregistered system "
                f"{adapter.source!r}")
        if adapter.id in self.adapters:
            raise InteropError(f"adapter {adapter.id!r} already registered")
        self.adapters[adapter.id] = adapter
        return adapter

    # ---- mappings ----
    @staticmethod
    def _mapping_key(m: SemanticMapping) -> str:
        return f"{m.source_concept}|{m.target_concept}|{m.version}"

    def register_mapping(self, mapping: SemanticMapping) -> SemanticMapping:
        key = self._mapping_key(mapping)
        if key in self.mappings:
            raise InteropError(f"mapping {key!r} already registered")
        # opendea: targets must resolve against the canonical registry
        ns, name = split_concept_ref(mapping.target_concept)
        if ns == "opendea":
            entities = Registry.entities()
            if name not in entities:
                raise InteropError(
                    f"mapping target {mapping.target_concept!r} is not a "
                    "canonical OpenDEA concept (DEA-E001)")
        # NO_CORRESPONDENCE must not claim a resolvable target
        if mapping.relationship == MappingRelation.NO_CORRESPONDENCE:
            tns, _ = split_concept_ref(mapping.target_concept)
            if tns == "opendea":
                raise InteropError(
                    "NO_CORRESPONDENCE mappings must not target an opendea: "
                    "concept (CR-11F)")
        self.mappings[key] = mapping
        return mapping

    def mapping_for(self, source_concept: str) -> List[SemanticMapping]:
        return [m for m in self.mappings.values()
                if m.source_concept == source_concept]

    # ---- identity (CR-11I) ----
    def link_external_identifier(self, link: ExternalIdentifier) -> ExternalIdentifier:
        """Correlate an external record with an OpenDEA entity.

        The external identifier is preserved as a *link*; it never becomes the
        canonical identity. ``entity`` must be a canonical id.
        """
        from ..model.identity import is_canonical_id
        if not is_canonical_id(link.entity):
            raise InteropError(
                f"entity {link.entity!r} is not a canonical OpenDEA identity — "
                "external identifiers are correlated, never adopted (CR-11I)")
        if link.system not in self.systems:
            raise InteropError(f"unknown external system {link.system!r}")
        self.identifiers.append(link)
        return link

    def resolve(self, system: str, identifier: str) -> Optional[str]:
        """External record → canonical entity id (exact correlation only —
        reconciliation/confidence lands in CR-11 Phase 2, CR-11J/K)."""
        for link in self.identifiers:
            if link.system == system and link.identifier == identifier:
                return link.entity
        return None

    # ---- extensions (CR-11AR) ----
    def register_extension(self, extension: Extension) -> Extension:
        if extension.ref in self.extensions:
            raise InteropError(f"extension {extension.ref!r} already registered")
        self.extensions[extension.ref] = extension
        return extension

    # ---- exchange (CR-11S/T/U seed) ----
    def export(self, store: GraphStore, exchange_id: str, target: str,
               mapping_version: str = "",
               provenance: Optional[dict] = None) -> Exchange:
        """Canonical JSON export of the graph as an Exchange envelope.

        The payload serializes OpenDEA *semantics* (entities + relationships
        with their assertion/provenance/temporal metadata) — not the internal
        store layout (CR-11U).
        """
        snapshot = snapshot_store(store)
        payload = {
            "entities": snapshot["nodes"],
            "relationships": snapshot["edges"],
        }
        return Exchange(
            id=exchange_id, source="opendea", target=target,
            operation=ImportMode.FULL, payload=payload,
            schema_version="1.0.0",
            profile_versions={"dea:core": "1.0.0"},
            mapping_version=mapping_version,
            provenance=provenance or {"exportedBy": "opendea-runtime"},
        )
