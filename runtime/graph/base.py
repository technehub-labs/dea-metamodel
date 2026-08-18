"""CR-9D/CR-9E — Canonical graph model and the vendor-independent GraphStore
interface.

The GraphStore is the *port* in the CR-9A runtime architecture: every semantic
service (validation, reasoning, assessment, decision, agent interfaces) talks to
this interface, never to a graph database directly (CR-9D: "Do not tie OpenDEA
directly to one graph database"). Reference and production implementations —
in-memory, Neo4j, Neptune, ArangoDB, PostgreSQL+graph, RDF triplestore — are
interchangeable behind it.

Canonical graph model (CR-9E):

- :class:`Node` — an entity instance: stable canonical id (CR-8 §7), type,
  name, lifecycle state, assertion provenance, source-of-record linkage and
  arbitrary properties.
- :class:`Edge` — a relationship assertion. Edges are *first-class* and carry
  their own metadata (CR-9E: "An edge should itself be capable of carrying
  metadata"): provenance, temporal validity (CR-9F), lifecycle status and
  properties.

CR-9B is honoured structurally: what the enterprise *is understood to be*
(node/edge identity + type), what is *observed* (assertion.status=observed),
what is *claimed* (assertion provenance) and what is *inferred*
(provenance.derived_from / derivation_rule) are distinct fields — never
collapsed into a single representation.

CR-9CQ (no silent inference): the store never materializes derived edges on its
own. ``infer()`` is declared on the interface but the foundation raises
:class:`InferenceUnavailable` — reasoning lands in CR-9.3, and when it does,
derived results must carry provenance and an explicit state transition.
"""
from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, ContextManager, Dict, Iterable, List, Optional

# CR-8 §7 — stable identity (mirrors schemas/model-envelope.json element id).
# Names are not identities; ids are lowercase dot-namespaced slugs.
import re

CANONICAL_ID = re.compile(r"^[a-z][a-z0-9-]*(\.[a-z0-9-]+)*$")

# Lifecycle states shared by nodes and edges (CR-6 §22; envelope schema enums).
LIFECYCLE_STATES = ("proposed", "planned", "active", "deprecated", "retired")

# Assertion provenance classes (CR-8 §40 / envelope metadata.assertion_status).
ASSERTION_STATUSES = ("declared", "observed", "imported", "inferred",
                      "generated", "validated", "approved")


class GraphError(Exception):
    """Base class for graph-store failures."""


class DuplicateEntityError(GraphError):
    """create_entity on an id that already exists."""


class EntityNotFoundError(GraphError):
    """Reference to an entity id that does not exist."""


class ReferentialIntegrityError(GraphError):
    """Edge endpoint missing, or delete would orphan edges."""


class CanonicalIdError(GraphError):
    """id violates the CR-8 §7 canonical identity pattern."""


class InferenceUnavailable(GraphError):
    """CR-9CQ — reasoning is not part of the runtime foundation (CR-9.3)."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_instant(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 instant (date or date-time). None passes through."""
    if value is None or isinstance(value, datetime):
        return value
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        # bare date
        dt = datetime.fromisoformat(text + "T00:00:00+00:00")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class Node:
    """CR-9E Node — one canonical entity instance in the graph."""
    id: str
    type: str
    name: str
    version: str = "1.0.0"
    lifecycle_status: Optional[str] = None
    assertion: Dict[str, Any] = field(default_factory=dict)
    source: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not CANONICAL_ID.match(self.id):
            raise CanonicalIdError(
                f"entity id {self.id!r} violates canonical identity (CR-8 §7)")
        if self.lifecycle_status and self.lifecycle_status not in LIFECYCLE_STATES:
            raise GraphError(f"unknown lifecycle_status {self.lifecycle_status!r}")


@dataclass
class Edge:
    """CR-9E Edge — a first-class, metadata-carrying relationship assertion."""
    type: str
    source: str  # source entity id
    target: str  # target entity id
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    status: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.status and self.status not in LIFECYCLE_STATES:
            raise GraphError(f"unknown edge status {self.status!r}")

    @property
    def key(self) -> tuple:
        return (self.source, self.type, self.target)

    def is_active_at(self, instant: Any = None) -> bool:
        """CR-9F 'what is true now?' — temporal validity + lifecycle status.

        An edge is active at ``instant`` (default: now) when:
        - its lifecycle status is not ``deprecated``/``retired`` (a *planned*
          edge must never be read as a current edge — CR-6 §22), and
        - ``valid_from <= instant`` (when set), and
        - ``instant < valid_to`` (when set).
        """
        if self.status in ("deprecated", "retired", "planned", "proposed"):
            return False
        at = _parse_instant(instant) or utcnow()
        vf = _parse_instant(self.valid_from)
        vt = _parse_instant(self.valid_to)
        if vf and at < vf:
            return False
        if vt and at >= vt:
            return False
        return True


class GraphStore(ABC):
    """CR-9D — the logical graph interface every implementation must honour.

    Implementations MUST NOT add semantics beyond this contract; CR-9CL runtime
    conformance is demonstrated by passing the vendor-independent contract
    suite (tests/runtime/test_graphstore_contract.py).
    """

    # ---- entity CRUD ----
    @abstractmethod
    def create_entity(self, node: Node) -> Node: ...

    @abstractmethod
    def get_entity(self, entity_id: str) -> Node: ...

    @abstractmethod
    def update_entity(self, entity_id: str, **changes) -> Node: ...

    @abstractmethod
    def delete_entity(self, entity_id: str, cascade: bool = False) -> None: ...

    @abstractmethod
    def has_entity(self, entity_id: str) -> bool: ...

    # ---- relationship CRUD ----
    @abstractmethod
    def create_relationship(self, edge: Edge) -> Edge: ...

    @abstractmethod
    def delete_relationship(self, source: str, rel_type: str, target: str) -> None: ...

    @abstractmethod
    def edges_of(self, entity_id: str, direction: str = "both",
                 rel_type: Optional[str] = None) -> List[Edge]: ...

    # ---- queries ----
    @abstractmethod
    def query(self, type: Optional[str] = None,
              where: Optional[Callable[[Node], bool]] = None) -> List[Node]:
        """Entity lookup: filter by canonical type and/or predicate."""

    @abstractmethod
    def neighbors(self, entity_id: str, rel_type: Optional[str] = None,
                  direction: str = "out", at: Any = None) -> List[Node]:
        """Direct neighbours; ``at`` applies CR-9F temporal edge filtering."""

    @abstractmethod
    def traverse(self, start_id: str, rel_types: Optional[Iterable[str]] = None,
                 direction: str = "out", max_depth: int = 10,
                 at: Any = None) -> List[Node]:
        """Breadth-first traversal from ``start_id`` (exclusive of start)."""

    @abstractmethod
    def find_path(self, source_id: str, target_id: str,
                  rel_types: Optional[Iterable[str]] = None,
                  at: Any = None) -> Optional[List[Edge]]:
        """Shortest directed path source→target as an edge list, or None."""

    # ---- transactions (CR-9BP) ----
    @abstractmethod
    def transaction(self) -> "ContextManager[GraphStore]":
        """Context manager: all mutations commit atomically; on exception the
        store rolls back — the graph is never left partially updated."""

    # ---- reasoning (CR-9Q/CR-9CQ — not part of the foundation) ----
    def infer(self, *args, **kwargs):
        raise InferenceUnavailable(
            "infer() is not available in the runtime foundation (CR-9.1). "
            "Reasoning arrives with CR-9.3 and must never silently convert "
            "inferred knowledge into authoritative fact (CR-9CQ).")

    # ---- introspection ----
    @abstractmethod
    def stats(self) -> Dict[str, int]:
        """Node/edge counts — the seed of CR-9CN golden-graph regression."""


def clone(obj):
    """Defensive copy helper for implementations returning stored objects."""
    return copy.deepcopy(obj)
