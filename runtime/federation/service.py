"""CR-11 Phase 7 — federation service (CR-11AH/AI/AJ).

The service implements the bounded federation shape:

    OpenDEA query
          ↓
    Determine source  ← :class:`FederationView.dispatch`
          ↓
    Query external system  ← a bound :class:`QueryAdapter`
          ↓
    Normalize result  ← :class:`SourceResolver` pluggable per system
          ↓
    Return semantic result  ← :class:`QueryDispatchResult`

CR-11AK boundary:

* No universal federation engine — there is no query optimiser.
* No automatic schema-rewriting across systems — adapters are explicit
  classes the caller registers.
* No silent source adoption — the authority policy always names itself;
  if none is registered the result is annotated, never silently trusted.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from ..graph import GraphStore, Node
from ..interoperability import (AuthorityPolicy, ExternalIdentifier,
                                ExternalSystem, InteropRegistry)
from .model import (AuthorityContext, EntityLocality, FederatedQuery,
                     FederatedReference, FederationError,
                     QueryDispatchResult, ResolutionStrategy)


# ---------------------------------------------------------------- resolvers


class SourceResolver:
    """Pluggable per-system record materialisation.

    A resolver turns a :class:`FederatedReference` into a dict (the
    shape that :class:`QueryDispatchResult.records` carries) or returns
    :class:`None` when the system cannot answer. Resolvers never
    silently fabricate results — they answer or refuse.
    """

    def resolve(self, reference: FederatedReference, *,
                filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("resolve() must be implemented")


class InGraphResolver(SourceResolver):
    """Default resolver: the data is already in the OpenDEA graph.

    The resolver walks the registered :class:`InteropRegistry`
    ExternalIdentifier links and returns the corresponding canonical
    node plus the link metadata. Federation answers without remote
    access when the data is already known.
    """

    def __init__(self, store: GraphStore, registry: InteropRegistry):
        self.store = store
        self.registry = registry

    def resolve(self, reference: FederatedReference, *,
                filters: Optional[Dict[str, Any]] = None
                ) -> Optional[Dict[str, Any]]:
        # Special case: ``opendea`` is the local system — match by
        # entity id directly so the federation entry point can probe
        # "subject X" without asking callers to know the external id.
        if reference.system == "opendea":
            try:
                node = self.store.get_entity(reference.external_identifier)
            except Exception:
                return None
            return {
                "entity": node.id,
                "name": node.name,
                "type": node.type,
                "properties": dict(node.properties),
                "source": "opendea",
                "externalIdentifier": reference.external_identifier,
                "adapter": reference.adapter,
                "locality": "IN_GRAPH",
            }
        for link in self.registry.identifiers:
            if (link.system == reference.system
                    and link.identifier == reference.external_identifier):
                try:
                    node = self.store.get_entity(link.entity)
                except Exception:
                    return {"entity": link.entity,
                            "source": reference.system,
                            "externalIdentifier": reference.external_identifier,
                            "locality": "IN_GRAPH",
                            "synthesised": True}
                return {
                    "entity": node.id,
                    "name": node.name,
                    "type": node.type,
                    "properties": dict(node.properties),
                    "source": reference.system,
                    "externalIdentifier": reference.external_identifier,
                    "adapter": reference.adapter,
                    "locality": "IN_GRAPH",
                }
        return None


# ---------------------------------------------------------------- adapter


@dataclass
class RemoteSource:
    """A registered remote system: identifier + adapter + resolver."""

    system: str
    adapter: str
    resolver: SourceResolver

    def query(self, reference: FederatedReference, *,
              filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        return self.resolver.resolve(reference, filters=filters or {})


class QueryAdapter:
    """CR-11AJ — query adapter bound to a remote system.

    An adapter is the typed boundary between OpenDEA's federation
    vocabulary and a producer-specific query grammar. Adapters expose
    a single :meth:`query` method that takes a :class:`FederatedQuery`
    and returns the normalised record list.

    The default :class:`DirectQueryAdapter` works against the
    :class:`InGraphResolver`; concrete adapters for ServiceNow, BPMN
    engines, etc. subclass and translate the query grammar.
    """

    def query(self, query: FederatedQuery,
              sources: Sequence["RemoteSource"],
              in_graph: InGraphResolver
              ) -> Dict[str, Dict[str, Any]]:
        """Return ``{external_identifier: normalised_record}``.

        The dispatcher merges the per-source answers under a shared
        fingerprint key. Adapters must never invent identifiers the
        remote system didn't return.
        """
        raise NotImplementedError("QueryAdapter.query() must be implemented")


class DirectQueryAdapter(QueryAdapter):
    """Adapter that re-uses each remote source's resolver directly.

    Useful for the bounded Phase 7 surface where a single external
    reference per subject is sufficient and no joined query is
    required. The federation dispatcher iterates the registered
    sources in declared order.
    """

    def query(self, query: FederatedQuery,
              sources: Sequence[RemoteSource],
              in_graph: InGraphResolver
              ) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        for source in sources:
            reference = FederatedReference(
                system=source.system, adapter=source.adapter,
                external_identifier=query.subject,
                locality_hint=EntityLocality.FEDERATED,
            )
            record = source.query(reference, filters=query.filters)
            if record is not None and query.subject not in out:
                out[query.subject] = record
        # Always check in-graph; in-graph answers win under
        # ``IN_GRAPH_FIRST`` and never conflict in ``SOURCE_PRIORITY``.
        local_ref = FederatedReference(
            system="opendea", adapter="in-graph",
            external_identifier=query.subject,
            locality_hint=EntityLocality.LOCAL,
        )
        record = in_graph.resolve(local_ref, filters=query.filters)
        if record is not None and query.subject not in out:
            out[query.subject] = record
        return out


# ------------------------------------------------------------------ view


class FederationView:
    """CR-11AJ — bounded federation dispatcher.

    The view reads the :class:`InteropRegistry` for source authority,
    asks a :class:`QueryAdapter` to translate the request, merges the
    results under the chosen :class:`ResolutionStrategy`, and returns
    a :class:`QueryDispatchResult`. No universal optimiser; no silent
    fallback to authoritative defaults.
    """

    def __init__(self, store: GraphStore, registry: InteropRegistry,
                 adapter: Optional[QueryAdapter] = None,
                 remote_sources: Optional[Dict[str, RemoteSource]] = None):
        self.store = store
        self.registry = registry
        self.adapter = adapter or DirectQueryAdapter()
        self.remote_sources: Dict[str, RemoteSource] = dict(remote_sources or {})
        self.in_graph = InGraphResolver(store, registry)

    def bind_remote(self, system: str, source: RemoteSource) -> None:
        """Register a remote system with a resolver."""
        if source.system != system:
            raise FederationError(
                f"remote source {source!r} does not match binding key {system!r}")
        if system not in self.registry.systems:
            raise FederationError(
                f"external system {system!r} is not registered with the "
                "InteropRegistry — bind it before exposing it for federation")
        self.remote_sources[system] = source

    # ---- dispatch ----
    def dispatch(self, query: FederatedQuery) -> QueryDispatchResult:
        if not query.subject:
            raise FederationError("federated query requires a subject")

        # Source selection — declared sources first, plus any policy-blessed
        # systems the registry knows about.
        available = [self.remote_sources[s] for s in (query.include_sources or [])
                     if s in self.remote_sources]
        provenance: Dict[str, List[str]] = {"in-graph": [], "remote": []}
        notes: List[str] = []

        # In-graph probe (always — IN_GRAPH_FIRST prefers this).
        local_ref = FederatedReference(
            system="opendea", adapter="in-graph",
            external_identifier=query.subject,
            locality_hint=EntityLocality.LOCAL,
        )
        local_record = self.in_graph.resolve(local_ref, filters=query.filters)
        if local_record is not None:
            provenance["in-graph"].append(query.subject)

        # Ask the adapter for the union of answers from declared sources.
        merged = self.adapter.query(query, available, self.in_graph)
        for key in merged:
            provenance["remote"].append(key)

        # Apply the strategy.
        records, authority_ctx = self._apply(query, merged, local_record, notes)

        # Authority context — explicit even when no policy is bound.
        if query.authority_policy:
            policy = self.registry.authority_policies.get(query.authority_policy)
            if policy is None:
                notes.append(
                    f"unknown authority policy {query.authority_policy!r} — "
                    "result carries no explicit authority")
            else:
                authority_ctx = AuthorityContext(
                    policy=policy.id,
                    sources=sorted({s for (s, _) in policy.weights}),
                    weights={f"{s}/{prop}": float(w)
                              for (s, prop), w in policy.weights.items()},
                    chosen_source=authority_ctx.chosen_source if authority_ctx
                                  else None,
                    rationale=authority_ctx.rationale if authority_ctx
                               else "policy applied; no remote conflict",
                )

        return QueryDispatchResult(
            subject=query.subject,
            records=records,
            authority=authority_ctx,
            provenance=provenance,
            strategy=query.strategy,
            notes=notes,
        )

    # ---- reference resolution ----
    def resolve_reference(self, reference: FederatedReference
                           ) -> Optional[Dict[str, Any]]:
        """Resolve one :class:`FederatedReference` through the binding."""
        if reference.system == "opendea":
            return self.in_graph.resolve(reference)
        source = self.remote_sources.get(reference.system)
        if source is None:
            return None
        return source.query(reference)

    # ---- helpers ----
    def _apply(self, query: FederatedQuery,
               merged: Dict[str, Dict[str, Any]],
               local_record: Optional[Dict[str, Any]],
               notes: List[str]
               ) -> tuple[List[Dict[str, Any]], Optional[AuthorityContext]]:
        if query.strategy == ResolutionStrategy.IN_GRAPH_FIRST:
            if local_record is not None:
                return [local_record], AuthorityContext(
                    policy=query.authority_policy or "",
                    chosen_source="opendea",
                    rationale="IN_GRAPH_FIRST — local answer served",
                )
            if merged:
                first = next(iter(merged.values()))
                src = first.get("source", "")
                return list(merged.values()), AuthorityContext(
                    policy=query.authority_policy or "",
                    chosen_source=src,
                    rationale=f"IN_GRAPH_FIRST fell back to remote ({src})",
                )
            notes.append("IN_GRAPH_FIRST — no answer (graph empty + no remote adapter)")
            return [], None

        if query.strategy == ResolutionStrategy.SOURCE_PRIORITY:
            ordered = self._source_priority_sources(query.include_sources)
            by_priority = []
            seen: set[str] = set()
            for src in ordered:
                if src in self.remote_sources:
                    answer = self.remote_sources[src].query(
                        FederatedReference(
                            system=src, adapter=self.remote_sources[src].adapter,
                            external_identifier=query.subject,
                            locality_hint=EntityLocality.FEDERATED,
                        ), filters=query.filters)
                    if answer is not None and query.subject not in seen:
                        by_priority.append(answer)
                        seen.add(query.subject)
            if not by_priority and local_record is not None:
                by_priority.append(local_record)
            chosen = by_priority[0].get("source") if by_priority else None
            return by_priority, AuthorityContext(
                policy=query.authority_policy or "",
                chosen_source=chosen or "",
                rationale="SOURCE_PRIORITY — first non-empty wins",
            )

        # MERGED
        union: List[Dict[str, Any]] = []
        if local_record is not None:
            union.append({**local_record, "locality": "UNION"})
        for rec in merged.values():
            if rec not in union:
                union.append({**rec, "locality": "UNION"})
        return union, AuthorityContext(
            policy=query.authority_policy or "",
            sources=list(merged.keys()),
            rationale="MERGED — local + remote answers concatenated by source",
        )

    def _source_priority_sources(self, declared: Iterable[str]) -> List[str]:
        order = list(declared or [])
        # Stable: declared order wins. We do NOT silently re-order via
        # authority policies — that would violate CR-11AK ("Do not implement
        # a universal federation engine").
        return order


# Module-level ergonomic helper for the common "resolve one
# FederatedReference through any available resolver" pattern.
def resolve_reference(view: FederationView, reference: FederatedReference
                      ) -> Optional[Dict[str, Any]]:
    return view.resolve_reference(reference)
