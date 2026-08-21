"""CR-11 Phase 7 — Federation (CR-11AH/AI/AJ + AK boundary).

OpenDEA does not own every enterprise fact. Federation provides:

* **EntityLocality** — every graph node declares where its authoritative
  representation lives (LOCAL / FEDERATED / IMPORTED / DERIVED / VIRTUAL).
* **FederatedReference** — a structured pointer to an authoritative
  external record (system + adapter + external identifier + source-aware
  schema version) that OpenDEA can resolve on demand.
* **FederationView** — a read-only query-dispatch facade that routes a
  query to the most appropriate local + remote sources, applies the
  registered :class:`AuthorityPolicy`, and returns a unified response
  without copying the entire external dataset into OpenDEA.
* **SourceResolver** — pluggable per-system resolver; defaults to the
  in-graph resolver when no remote adapter is bound.

CR-11AK explicitly forbids "a universal federation engine" in this
phase. The shipping surface is therefore deliberately narrow: a
catalog-level reference + dispatch shape, not a query optimizer.
"""
from .model import (AuthorityContext, EntityLocality, FederatedQuery,
                     FederatedReference, FederationError, Locality,
                     QueryDispatchResult, ResolutionStrategy)
from .service import (FederationView, InGraphResolver, QueryAdapter,
                       RemoteSource, SourceResolver, resolve_reference)

__all__ = [
    "AuthorityContext", "EntityLocality", "FederatedQuery",
    "FederatedReference", "FederationError", "Locality",
    "QueryDispatchResult", "ResolutionStrategy",
    "FederationView", "InGraphResolver", "QueryAdapter",
    "RemoteSource", "SourceResolver", "resolve_reference",
]
