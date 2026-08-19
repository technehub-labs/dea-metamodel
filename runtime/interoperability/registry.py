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

from dataclasses import replace
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from ..api.service import Registry
from ..graph import GraphStore
from ..scenario.engine import snapshot_store
from .identity import (AuthorityPolicy, ConflictStatus, ConflictValue,
                       EntityResolution, KnowledgeConflict,
                       ReconciliationState, ResolutionCandidate)
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
        self.resolutions: List[EntityResolution] = []
        self.conflicts: List[KnowledgeConflict] = []
        self.authority_policies: Dict[str, AuthorityPolicy] = {}
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

    def reconcile_external(self, system: str, identifier: str,
                           candidates: Optional[Iterable[ResolutionCandidate]] = None,
                           auto_match_threshold: float = 0.95,
                           review_threshold: float = 0.70) -> EntityResolution:
        """CR-11J/K — reconcile an external record without adopting its id.

        Exact ExternalIdentifier links resolve as MATCHED. Candidate-based
        matching is thresholded: below the auto-match threshold the result is a
        reviewable CANDIDATE, never a silent merge.
        """
        resolution_id = f"resolution.{system}.{len(self.resolutions) + 1}"
        exact = self.resolve(system, identifier)
        if exact:
            resolution = EntityResolution(
                id=resolution_id, system=system, identifier=identifier,
                state=ReconciliationState.MATCHED, entity=exact,
                score=1.0, method="exact", review_required=False)
            self.resolutions.append(resolution)
            return resolution

        candidate_list = list(candidates or [])
        if not candidate_list:
            resolution = EntityResolution(
                id=resolution_id, system=system, identifier=identifier,
                state=ReconciliationState.UNMATCHED, review_required=True)
            self.resolutions.append(resolution)
            return resolution

        best = max(candidate_list, key=lambda c: c.score)
        high = [c for c in candidate_list if c.score >= auto_match_threshold]
        if len(high) > 1:
            state, entity, review = ReconciliationState.CONFLICTING, None, True
        elif high:
            state, entity, review = ReconciliationState.MATCHED, best.entity, False
        elif best.score >= review_threshold:
            state, entity, review = ReconciliationState.CANDIDATE, None, True
        else:
            state, entity, review = ReconciliationState.UNMATCHED, None, True
        resolution = EntityResolution(
            id=resolution_id, system=system, identifier=identifier,
            state=state, entity=entity, score=best.score, method=best.method,
            candidates=candidate_list, review_required=review)
        self.resolutions.append(resolution)
        return resolution

    def approve_resolution(self, resolution_id: str, entity: str,
                           approved_by: str) -> EntityResolution:
        """Explicitly approve a candidate/matched resolution as MERGED.

        Approval is the only path to consolidation (CR-11L). The external id
        remains an ExternalIdentifier link; it is never adopted as canonical
        identity (CR-11I).
        """
        if not approved_by:
            raise InteropError("resolution approval requires an explicit actor")
        resolution = next((r for r in self.resolutions if r.id == resolution_id),
                          None)
        if resolution is None:
            raise InteropError(f"unknown resolution {resolution_id!r}")
        if resolution.state not in (ReconciliationState.CANDIDATE,
                                    ReconciliationState.MATCHED,
                                    ReconciliationState.CONFLICTING):
            raise InteropError(
                f"cannot approve resolution in state {resolution.state.value}")
        candidate_entities = {c.entity for c in resolution.candidates}
        if resolution.entity:
            candidate_entities.add(resolution.entity)
        if entity not in candidate_entities:
            raise InteropError(
                f"approved entity {entity!r} was not a reconciliation candidate")
        merged = replace(
            resolution,
            state=ReconciliationState.MERGED,
            entity=entity,
            approved_by=approved_by,
            review_required=False,
        )
        self.resolutions = [merged if r.id == resolution_id else r
                            for r in self.resolutions]
        self.link_external_identifier(ExternalIdentifier(
            system=resolution.system, identifier=resolution.identifier,
            entity=entity, identifier_type="reconciled"))
        return merged

    def record_conflict(self, entity: str, property: str,
                        values: Iterable[ConflictValue]) -> Optional[KnowledgeConflict]:
        """CR-11L — preserve source disagreement as first-class knowledge."""
        value_list = list(values)
        for value in value_list:
            if value.source not in self.systems:
                raise InteropError(f"unknown conflict source {value.source!r}")
        if len({repr(v.value) for v in value_list}) < 2:
            return None
        conflict = KnowledgeConflict(
            id=f"conflict.{entity}.{property}.{len(self.conflicts) + 1}",
            entity=entity, property=property, values=value_list)
        self.conflicts.append(conflict)
        return conflict

    # ---- source authority (CR-11M/N/R) ----
    def register_authority_policy(self, policy: AuthorityPolicy) -> AuthorityPolicy:
        for source, _property in policy.weights:
            if source not in self.systems:
                raise InteropError(
                    f"authority policy references unregistered system {source!r}")
        if policy.id in self.authority_policies:
            raise InteropError(f"authority policy {policy.id!r} already registered")
        self.authority_policies[policy.id] = policy
        return policy

    def resolve_conflict(self, conflict_id: str, policy_id: str,
                         resolved_by: str) -> KnowledgeConflict:
        """Resolve a conflict through a declared AuthorityPolicy.

        The chosen value is recorded as the resolution; every competing value
        remains in the conflict (CR-11L — conflicts are preserved, not erased).
        """
        if not resolved_by:
            raise InteropError("conflict resolution requires an explicit actor")
        conflict = next((c for c in self.conflicts if c.id == conflict_id), None)
        if conflict is None:
            raise InteropError(f"unknown conflict {conflict_id!r}")
        policy = self.authority_policies.get(policy_id)
        if policy is None:
            raise InteropError(f"unknown authority policy {policy_id!r}")
        chosen = policy.authoritative_value(conflict.property, conflict.values)
        resolved_at = datetime.now(timezone.utc).isoformat()
        resolved = replace(
            conflict,
            status=ConflictStatus.RESOLVED,
            resolution={
                "property": conflict.property,
                "source": chosen.source,
                "value": chosen.value,
                "policy": policy.id,
                "resolvedBy": resolved_by,
                "resolvedAt": resolved_at,
            },
            resolved_at=resolved_at,
        )
        self.conflicts = [resolved if c.id == conflict_id else c
                          for c in self.conflicts]
        return resolved

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
