"""CR-9D — InMemoryGraphStore: the reference GraphStore implementation.

Purpose (CR-9BV): *demonstrate the semantics*. It is the store the runtime
test-suite, the golden-graph contract and the documentation examples run
against — deliberately dependency-free so the CR-9D interface can be exercised
anywhere. It is not a production persistence story; Neo4j/Neptune/ArangoDB/
PostgreSQL/RDF adapters plug into the same ABC.

Implementation notes:
- Reads return deep copies — callers can never mutate stored state by accident
  (a silent-mutation vector; see CR-9CQ's spirit).
- Transactions are copy-on-write: mutations stage on a working copy and swap
  in on commit; any exception discards the stage (CR-9BP).
- Referential integrity is enforced: edges require both endpoints; deleting an
  entity with edges requires ``cascade=True``.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterable, List, Optional

from collections import deque

from .base import (DuplicateEntityError, Edge, EntityNotFoundError, GraphError,
                   GraphStore, Node, ReferentialIntegrityError)


class InMemoryGraphStore(GraphStore):
    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[tuple, Edge] = {}
        self._staged = None  # (nodes, edges) while inside a transaction

    # ---- transaction plumbing (CR-9BP) ----
    @contextmanager
    def transaction(self):
        if self._staged is not None:
            # nested: join the outer transaction
            yield self
            return
        self._staged = (copy.deepcopy(self._nodes), copy.deepcopy(self._edges))
        try:
            yield self
        except Exception:
            self._staged = None  # ROLLBACK — committed state untouched
            raise
        else:
            self._nodes, self._edges = self._staged  # COMMIT
            self._staged = None

    @property
    def _n(self) -> Dict[str, Node]:
        return self._staged[0] if self._staged else self._nodes

    @property
    def _e(self) -> Dict[tuple, Edge]:
        return self._staged[1] if self._staged else self._edges

    # ---- entity CRUD ----
    def create_entity(self, node: Node) -> Node:
        if node.id in self._n:
            raise DuplicateEntityError(f"entity {node.id!r} already exists")
        self._n[node.id] = copy.deepcopy(node)
        return copy.deepcopy(node)

    def get_entity(self, entity_id: str) -> Node:
        try:
            return copy.deepcopy(self._n[entity_id])
        except KeyError:
            raise EntityNotFoundError(f"entity {entity_id!r} not found")

    def update_entity(self, entity_id: str, **changes) -> Node:
        if entity_id not in self._n:
            raise EntityNotFoundError(f"entity {entity_id!r} not found")
        if "id" in changes and changes["id"] != entity_id:
            raise GraphError("entity id is immutable (CR-8 §7: stable identity)")
        node = copy.deepcopy(self._n[entity_id])
        for key, value in changes.items():
            if not hasattr(node, key):
                raise GraphError(f"Node has no field {key!r}")
            setattr(node, key, value)
        node.__post_init__()  # re-validate invariants
        self._n[entity_id] = node
        return copy.deepcopy(node)

    def delete_entity(self, entity_id: str, cascade: bool = False) -> None:
        if entity_id not in self._n:
            raise EntityNotFoundError(f"entity {entity_id!r} not found")
        attached = [k for k, e in self._e.items()
                    if e.source == entity_id or e.target == entity_id]
        if attached and not cascade:
            raise ReferentialIntegrityError(
                f"entity {entity_id!r} has {len(attached)} relationship(s); "
                "pass cascade=True to delete them too")
        for k in attached:
            del self._e[k]
        del self._n[entity_id]

    def has_entity(self, entity_id: str) -> bool:
        return entity_id in self._n

    # ---- relationship CRUD ----
    def create_relationship(self, edge: Edge) -> Edge:
        for endpoint in (edge.source, edge.target):
            if endpoint not in self._n:
                raise ReferentialIntegrityError(
                    f"edge endpoint {endpoint!r} not present in graph")
        if edge.key in self._e:
            raise DuplicateEntityError(
                f"relationship {edge.source} -[{edge.type}]-> {edge.target} already exists")
        self._e[edge.key] = copy.deepcopy(edge)
        return copy.deepcopy(edge)

    def delete_relationship(self, source: str, rel_type: str, target: str) -> None:
        key = (source, rel_type, target)
        if key not in self._e:
            raise EntityNotFoundError(
                f"relationship {source} -[{rel_type}]-> {target} not found")
        del self._e[key]

    def edges_of(self, entity_id: str, direction: str = "both",
                 rel_type: Optional[str] = None) -> List[Edge]:
        out = []
        for e in self._e.values():
            if rel_type and e.type != rel_type:
                continue
            if direction in ("out", "both") and e.source == entity_id:
                out.append(e)
            elif direction in ("in", "both") and e.target == entity_id:
                out.append(e)
        return copy.deepcopy(out)

    # ---- queries ----
    def query(self, type: Optional[str] = None,
              where: Optional[Callable[[Node], bool]] = None) -> List[Node]:
        out = []
        for n in self._n.values():
            if type and n.type != type:
                continue
            if where and not where(copy.deepcopy(n)):
                continue
            out.append(n)
        return copy.deepcopy(out)

    def neighbors(self, entity_id: str, rel_type: Optional[str] = None,
                  direction: str = "out", at: Any = None) -> List[Node]:
        if entity_id not in self._n:
            raise EntityNotFoundError(f"entity {entity_id!r} not found")
        ids = []
        for e in self.edges_of(entity_id, direction=direction, rel_type=rel_type):
            if not e.is_active_at(at):
                continue
            ids.append(e.target if e.source == entity_id and direction != "in"
                       else e.source)
        return [self.get_entity(i) for i in ids]

    def traverse(self, start_id: str, rel_types: Optional[Iterable[str]] = None,
                 direction: str = "out", max_depth: int = 10,
                 at: Any = None) -> List[Node]:
        if start_id not in self._n:
            raise EntityNotFoundError(f"entity {start_id!r} not found")
        allowed = set(rel_types) if rel_types else None
        seen, order = {start_id}, []
        frontier = deque([(start_id, 0)])
        while frontier:
            current, depth = frontier.popleft()
            if depth >= max_depth:
                continue
            for e in self.edges_of(current, direction=direction):
                if allowed and e.type not in allowed:
                    continue
                if not e.is_active_at(at):
                    continue
                nxt = e.target if e.source == current and direction != "in" else e.source
                if nxt not in seen:
                    seen.add(nxt)
                    order.append(nxt)
                    frontier.append((nxt, depth + 1))
        return [self.get_entity(i) for i in order]

    def find_path(self, source_id: str, target_id: str,
                  rel_types: Optional[Iterable[str]] = None,
                  at: Any = None) -> Optional[List[Edge]]:
        for eid in (source_id, target_id):
            if eid not in self._n:
                raise EntityNotFoundError(f"entity {eid!r} not found")
        allowed = set(rel_types) if rel_types else None
        # BFS over edges
        frontier = deque([(source_id, [])])
        seen = {source_id}
        while frontier:
            current, path = frontier.popleft()
            if current == target_id:
                return copy.deepcopy(path)
            for e in self.edges_of(current, direction="out"):
                if allowed and e.type not in allowed:
                    continue
                if not e.is_active_at(at):
                    continue
                if e.target not in seen:
                    seen.add(e.target)
                    frontier.append((e.target, path + [e]))
        return None

    # ---- introspection ----
    def stats(self) -> Dict[str, int]:
        return {"nodes": len(self._n), "edges": len(self._e)}
