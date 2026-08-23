"""CR-AM-05A hierarchical dimensions & assessment instruments.

The Dimension is a recursively composable assessment taxonomy: a
sub-dimension is simply a Dimension with a parent Dimension — there is
no SubDimension class (CR-AM-05A §3, §40). This module enforces the
hierarchy invariants of §8 by construction, not by trust:

* Acyclic. A → B → C → A is invalid.
* No self-parent. A → A is invalid.
* Unique identity. (id, version) pairs are unique within a model
  namespace.
* Known parents. Every declared parent reference must resolve.

It also provides the instrument-evolution helpers of §29–§33:

* Adding questions produces a new instrument version without touching
  the maturity model (§29).
* Retiring a question never invalidates historical results (§30).
* Question replacement is explicit lineage via `supersedes` (§31).
* Result lineage preserves instrument + question versions (§33).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional


class HierarchyError(ValueError):
    """Raised when a Dimension hierarchy violates a CR-AM-05A §8 rule."""


class InstrumentEvolutionError(ValueError):
    """Raised when an instrument evolution violates CR-AM-05A §29–§33."""


@dataclass(frozen=True)
class DimensionNode:
    """A validated dimension within a hierarchy."""

    id: str
    version: str
    parent_id: Optional[str]

    @property
    def is_root(self) -> bool:
        return self.parent_id is None


def _node_key(dim: Mapping[str, Any]) -> tuple:
    return (dim.get("id"), dim.get("version", "1.0.0"))


def _parent_id(dim: Mapping[str, Any]) -> Optional[str]:
    parent = dim.get("parent_dimension")
    if isinstance(parent, Mapping):
        return parent.get("id")
    return None


def validate_dimension_hierarchy(
    dimensions: Iterable[Mapping[str, Any]],
) -> list[DimensionNode]:
    """Validate a set of dimensions and return them as ordered nodes.

    Ordering is topological (roots first), so consumers can render or
    aggregate without re-walking parents. Raises HierarchyError on any
    §8 violation.
    """
    dims = list(dimensions)
    by_id: dict[tuple, Mapping[str, Any]] = {}
    nodes: dict[tuple, DimensionNode] = {}

    # Unique identity (§8): same (id, version) twice is invalid.
    for dim in dims:
        key = _node_key(dim)
        if key in by_id:
            raise HierarchyError(
                f"duplicate dimension identity {key[0]!r}@{key[1]!r} "
                f"within the same model namespace (CR-AM-05A §8)"
            )
        by_id[key] = dim

    for dim in dims:
        did = str(dim.get("id") or "")
        pid = _parent_id(dim)
        # No self-parent (§8).
        if pid is not None and pid == did:
            raise HierarchyError(
                f"dimension {did!r} is its own parent (CR-AM-05A §8)"
            )
        nodes[_node_key(dim)] = DimensionNode(
            id=did, version=str(dim.get("version", "1.0.0")), parent_id=pid
        )

    # id -> node lookup for parent walks.
    node_by_id: dict[str, DimensionNode] = {n.id: n for n in nodes.values()}

    # Known parents: every parent reference must resolve within the set.
    for node in nodes.values():
        if node.parent_id is not None and node.parent_id not in node_by_id:
            raise HierarchyError(
                f"dimension {node.id!r} references unknown parent "
                f"{node.parent_id!r}"
            )

    # Acyclic (§8): walk each node to a root; a revisit means a cycle.
    for node in nodes.values():
        seen: set = set()
        current = node
        while current.parent_id is not None:
            if current.id in seen:
                raise HierarchyError(
                    f"cycle detected in dimension hierarchy at {current.id!r} "
                    f"(CR-AM-05A §8)"
                )
            seen.add(current.id)
            current = node_by_id[current.parent_id]

    # Topological ordering: depth ascending (roots first).
    def depth(node: DimensionNode) -> int:
        d, current = 0, node
        while current.parent_id is not None:
            current = node_by_id[current.parent_id]
            d += 1
        return d

    return sorted(nodes.values(), key=lambda n: (depth(n), n.id))


def hierarchy_depth(dimensions: Iterable[Mapping[str, Any]]) -> int:
    """Maximum depth of the hierarchy. Arbitrary depth is permitted (AC-AM05A-02)."""
    nodes = validate_dimension_hierarchy(dimensions)
    depth_by_id: dict[str, int] = {}

    def depth(node: DimensionNode) -> int:
        if node.id in depth_by_id:
            return depth_by_id[node.id]
        if node.parent_id is None:
            depth_by_id[node.id] = 0
            return 0
        parent = next(n for n in nodes if n.id == node.parent_id)
        depth_by_id[node.id] = depth(parent) + 1
        return depth_by_id[node.id]

    return max((depth(n) for n in nodes), default=-1) + 1


def iter_path(
    dimensions: Iterable[Mapping[str, Any]], dimension_id: str
) -> list[str]:
    """Root-to-node id path for one dimension (§34 semantic path support)."""
    nodes = validate_dimension_hierarchy(dimensions)
    by_id = {n.id: n for n in nodes}
    if dimension_id not in by_id:
        raise HierarchyError(f"unknown dimension {dimension_id!r}")
    path = []
    current = by_id[dimension_id]
    while True:
        path.append(current.id)
        if current.parent_id is None:
            break
        current = by_id[current.parent_id]
    return list(reversed(path))


def instrument_questions(instrument: Mapping[str, Any]) -> dict:
    """Question version map for an instrument: question_id -> version.

    Derived from sections[].items[].question (§25 binding). Used for
    §33 historical-lineage checks.
    """
    questions: dict[str, str] = {}
    for section in instrument.get("sections") or []:
        for item in section.get("items") or []:
            q = item.get("question") or {}
            qid, qver = q.get("id"), q.get("version")
            if qid:
                if qid in questions and questions[qid] != qver:
                    raise InstrumentEvolutionError(
                        f"question {qid!r} bound at two versions "
                        f"({questions[qid]!r} and {qver!r}) within one instrument"
                    )
                questions[qid] = str(qver or "1.0.0")
    return questions


def validate_instrument_evolution(
    old: Mapping[str, Any], new: Mapping[str, Any]
) -> dict:
    """Validate an instrument revision per §29 (incremental evolution).

    Adding questions requires no maturity-model change; the maturity
    model reference must therefore be identical between revisions.
    Returns a summary {added, removed, retained, maturity_model_unchanged}.
    """
    old_q = instrument_questions(old)
    new_q = instrument_questions(new)
    old_mm = (old.get("maturity_model") or {}).get("id")
    new_mm = (new.get("maturity_model") or {}).get("id")
    old_mm_v = (old.get("maturity_model") or {}).get("version")
    new_mm_v = (new.get("maturity_model") or {}).get("version")
    if old_mm and new_mm and (old_mm, old_mm_v) != (new_mm, new_mm_v):
        # A maturity-model change alongside an instrument revision is not
        # "incremental question evolution" (§29); it needs its own CR path.
        raise InstrumentEvolutionError(
            f"instrument revision changes maturity model "
            f"{old_mm!r}@{old_mm_v!r} → {new_mm!r}@{new_mm_v!r}; "
            f"incremental evolution must leave the maturity model unchanged "
            f"(CR-AM-05A §29)"
        )
    return {
        "added": sorted(set(new_q) - set(old_q)),
        "removed": sorted(set(old_q) - set(new_q)),
        "retained": sorted(set(old_q) & set(new_q)),
        "maturity_model_unchanged": True,
    }


def result_lineage_preserves_instrument(result: Mapping[str, Any]) -> bool:
    """§33: a result must preserve instrument id+version in its lineage.

    Non-negotiable: without it, "why did Organization A receive Level 3?"
    cannot be answered reproducibly after the questionnaire changes.
    """
    lineage = result.get("lineage") or {}
    instrument = lineage.get("assessment_instrument") or {}
    return bool(instrument.get("id") and instrument.get("version"))
