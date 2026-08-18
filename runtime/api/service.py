"""CR-9.1 — Entity/relationship service API.

RuntimeService is the programmatic facade above a GraphStore: it adds
*semantic* write-time validation on top of the store's structural guarantees,
using the canonical registry (metamodel/dea-metamodel.yaml) and the CR-8 type
hierarchy — the same sources the reference validator uses. Graph-mutation
paths that bypass this service (raw store access) still get referential
integrity and identity checks, but not registry semantics.

Scope note (CR-9BT/CR-9CT): this is the foundation CRUD surface. REST/GraphQL
bindings (CR-9AU), query services (CR-9U), reasoning (CR-9Q) and agent
interfaces (CR-9AH) build on it in later milestones.

CR-9CR honoured by construction: there is no agent mutation path here at
all — agents are read-only by default and any future agent write path must
pass through authority/policy evaluation first (CR-9AJ/CR-9AK).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..graph.base import Edge, GraphStore, Node
from ..model.identity import is_canonical_id
from ..model.loader import _load_validator


class SemanticValidationError(Exception):
    """A write violated registry semantics (type, relationship, endpoints)."""


class Registry:
    """Canonical registry view shared by the service (delegates to the CR-8
    validator's loaders — one source of truth, never a parallel copy)."""

    _cache: Optional[tuple] = None

    @classmethod
    def load(cls):
        if cls._cache is None:
            validator = _load_validator()
            cls._cache = validator.load_registry()
        assert cls._cache is not None
        return cls._cache

    @classmethod
    def entities(cls):
        return cls.load()[0]

    @classmethod
    def relationships(cls):
        return cls.load()[1]

    @classmethod
    def hierarchy(cls):
        return cls.load()[2]

    @classmethod
    def type_satisfies(cls, actual: str, declared: str) -> bool:
        validator = _load_validator()
        return validator.type_satisfies(actual, declared, cls.hierarchy())


class RuntimeService:
    """Entity/relationship CRUD with registry-backed semantic validation."""

    def __init__(self, store: GraphStore):
        self.store = store

    # ---- entities ----
    def create_entity(self, id: str, type: str, name: str,
                      properties: Optional[Dict[str, Any]] = None,
                      lifecycle_status: Optional[str] = None,
                      assertion: Optional[Dict[str, Any]] = None,
                      source: Optional[Dict[str, Any]] = None,
                      version: str = "1.0.0") -> Node:
        if not is_canonical_id(id):
            raise SemanticValidationError(
                f"entity id {id!r} violates canonical identity (CR-8 §7)")
        entities = Registry.entities()
        if type not in entities:
            raise SemanticValidationError(
                f"unknown type {type!r} — not in the canonical registry (DEA-E001)")
        if entities[type].get("abstract"):
            raise SemanticValidationError(
                f"type {type} is abstract and cannot be instantiated (CR-8 §9)")
        return self.store.create_entity(Node(
            id=id, type=type, name=name, version=version,
            lifecycle_status=lifecycle_status, assertion=assertion or {},
            source=source or {}, properties=properties or {}))

    def get_entity(self, entity_id: str) -> Node:
        return self.store.get_entity(entity_id)

    def update_entity(self, entity_id: str, **changes) -> Node:
        if "type" in changes:
            raise SemanticValidationError(
                "entity type is immutable — retype via delete+create so the "
                "change is explicit and auditable (CR-9BF)")
        return self.store.update_entity(entity_id, **changes)

    def delete_entity(self, entity_id: str, cascade: bool = False) -> None:
        self.store.delete_entity(entity_id, cascade=cascade)

    def query(self, type: Optional[str] = None, where=None) -> List[Node]:
        return self.store.query(type=type, where=where)

    # ---- relationships ----
    def create_relationship(self, source: str, rel_type: str, target: str,
                            valid_from: Optional[str] = None,
                            valid_to: Optional[str] = None,
                            status: Optional[str] = None,
                            provenance: Optional[Dict[str, Any]] = None,
                            properties: Optional[Dict[str, Any]] = None) -> Edge:
        rels = Registry.relationships()
        if rel_type not in rels:
            raise SemanticValidationError(
                f"undeclared relationship type {rel_type!r} (DEA-E002)")
        src = self.store.get_entity(source)  # raises if absent
        tgt = self.store.get_entity(target)
        rdef = rels[rel_type]
        src_types = {t.split(":", 1)[1] for t in rdef["source"]["types"]}
        tgt_types = {t.split(":", 1)[1] for t in rdef["target"]["types"]}
        if not any(Registry.type_satisfies(src.type, st) for st in src_types):
            raise SemanticValidationError(
                f"{src.type} is not a valid source for {rel_type} "
                f"(expected one of {sorted(src_types)}) (DEA-E006)")
        if not any(Registry.type_satisfies(tgt.type, tt) for tt in tgt_types):
            raise SemanticValidationError(
                f"{tgt.type} is not a valid target for {rel_type} "
                f"(expected one of {sorted(tgt_types)}) (DEA-E005)")
        return self.store.create_relationship(Edge(
            type=rel_type, source=source, target=target,
            valid_from=valid_from, valid_to=valid_to, status=status,
            provenance=provenance or {}, properties=properties or {}))

    def delete_relationship(self, source: str, rel_type: str, target: str) -> None:
        self.store.delete_relationship(source, rel_type, target)

    def neighbors(self, entity_id: str, rel_type: Optional[str] = None,
                  direction: str = "out", at: Any = None) -> List[Node]:
        return self.store.neighbors(entity_id, rel_type=rel_type,
                                    direction=direction, at=at)

    def traverse(self, start_id: str, **kwargs) -> List[Node]:
        return self.store.traverse(start_id, **kwargs)

    def find_path(self, source_id: str, target_id: str, **kwargs):
        return self.store.find_path(source_id, target_id, **kwargs)
