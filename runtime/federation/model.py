"""CR-11 Phase 7 — federation data model (CR-11AH/AI/AJ).

The model layer carries:

* :class:`EntityLocality` — re-exported from :mod:`runtime.interoperability`
  for ergonomic discovery (LOCAL / FEDERATED / IMPORTED / DERIVED /
  VIRTUAL).
* :class:`FederatedReference` — a structured reference to an authoritative
  external record (system + adapter + external identifier + source-aware
  schema version). Every federated node declares at least one of these
  on its properties so a query knows where to look.
* :class:`FederatedQuery` — a typed query envelope that names a *subject*
  (the OpenDEA-side concept) plus optional *include_sources* and an
  *authority* name (the registered ``AuthorityPolicy`` to apply).
* :class:`ResolutionStrategy` — how the :class:`FederationView`
  attempts to materialise a result: in-graph-first, source-priority,
  or merged.
* :class:`AuthorityContext` — the slice of :class:`AuthorityPolicy`
  relevant to a single query. The runtime never invents authority —
  every dispatch names the policy it consulted.
* :class:`QueryDispatchResult` — a typed result: which sources
  contributed, the merged record set (deduplicated by source priority),
  and any notes (e.g. "policy <X> applied" or "no remote adapter bound").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..interoperability import (EntityLocality, ExternalIdentifier,
                                InteropError, InteropRegistry)


class FederationError(Exception):
    """Federation invariant violated."""


class ResolutionStrategy(str, Enum):
    """How the federated view resolves a query."""

    IN_GRAPH_FIRST = "in-graph-first"        # local store, fall back to remote
    SOURCE_PRIORITY = "source-priority"      # declared sources, ordered
    MERGED = "merged"                        # local + remote merged by source priority


class Locality(str, Enum):
    """Per-result provenance — where the answer for a single record came from.

    Distinct from :class:`EntityLocality`, which describes the *node*;
    :class:`Locality` describes the *result*. A LOCAL node may resolve
    through a remote adapter if the in-graph resolver cannot satisfy
    the query.
    """

    IN_GRAPH = "IN_GRAPH"     # served by the opendea: in-graph resolver
    REMOTE = "REMOTE"         # served by a bound remote adapter
    UNION = "UNION"           # merged result spanning both


@dataclass(frozen=True)
class FederatedReference:
    """A structured reference to an authoritative external record.

    Three things together make a federation reference actionable:

    * the ExternalSystem id (``system``)
    * the adapter that knows how to reach it (``adapter``)
    * the external identifier at that system (``external_identifier``)

    The optional ``schema_version`` records which contract version
    produced the record so the right translator can be picked up later.
    """

    system: str
    adapter: str
    external_identifier: str
    schema_version: str = "1.0.0"
    locality_hint: EntityLocality = EntityLocality.FEDERATED

    def __post_init__(self):
        if not self.system or ":" in self.system:
            raise FederationError(
                f"system must be a registered ExternalSystem id, got {self.system!r}")
        if not self.adapter:
            raise FederationError("adapter is required for a federated reference")
        if not self.external_identifier:
            raise FederationError(
                "external identifier is required for a federated reference")
        # Validate that the locality hint is recognised; the value is
        # left untouched because the dataclass is frozen.
        EntityLocality(self.locality_hint)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "system": self.system,
            "adapter": self.adapter,
            "externalIdentifier": self.external_identifier,
            "schemaVersion": self.schema_version,
            "locality": self.locality_hint.value,
        }


@dataclass(frozen=True)
class FederatedQuery:
    """A typed query dispatch request (CR-11AJ)."""

    subject: str                            # OpenDEA-side concept
    include_sources: List[str] = field(default_factory=list)
    authority_policy: str = ""              # name of InteropRegistry policy
    strategy: ResolutionStrategy = ResolutionStrategy.IN_GRAPH_FIRST
    filters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.subject:
            raise FederationError("federated query requires a subject")
        try:
            ResolutionStrategy(self.strategy)
        except ValueError as exc:
            raise FederationError(
                f"unknown resolution strategy {self.strategy!r}") from exc


@dataclass(frozen=True)
class AuthorityContext:
    """The slice of the resolved AuthorityPolicy affecting one query."""

    policy: str
    sources: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    chosen_source: Optional[str] = None
    rationale: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "policy": self.policy, "sources": self.sources,
            "weights": self.weights, "chosenSource": self.chosen_source,
            "rationale": self.rationale,
        }.items() if v not in (None, "", [], {})}


@dataclass(frozen=True)
class QueryDispatchResult:
    """The result returned from :meth:`FederationView.dispatch`."""

    subject: str
    records: List[Dict[str, Any]]
    authority: Optional[AuthorityContext]
    provenance: Dict[str, List[str]] = field(default_factory=dict)
    strategy: ResolutionStrategy = ResolutionStrategy.IN_GRAPH_FIRST
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject, "records": self.records,
            "authority": self.authority.as_dict() if self.authority else None,
            "provenance": self.provenance,
            "strategy": self.strategy.value,
            "notes": self.notes,
        }


# Re-export EntityLocality from the canonical interoperability module
# so callers don't need a second import.
__all__ = [
    "AuthorityContext", "EntityLocality", "FederatedQuery",
    "FederatedReference", "FederationError", "Locality",
    "QueryDispatchResult", "ResolutionStrategy",
]
