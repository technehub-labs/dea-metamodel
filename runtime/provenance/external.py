"""CR-11 Phase 4 — external provenance (CR-11O/AE/BD).

CR-9.2 built the *internal* provenance graph (Conclusion → Assertion →
Evidence → Source). CR-11 Phase 4 extends it with the *external* source chain
so that any claim ingested from outside the canonical graph can still be
traced all the way back to its origin, and so that the chain is interoperable
with the established PROV concepts (Entity / Activity / Agent / Source).

Three CR-11 sub-items ship here:

* **CR-11O — Evidence preservation**
    External Fact → OpenDEA Assertion → Evidence → Source → Timestamp.
    The external source is recorded on the assertion (``externalSource``) and
    on the evidence (``capturedFrom``) so it survives normalisation.

* **CR-11AE — Provenance interoperability**
    Every CR-9 Assertion is exposed with a PROV-shaped projection::

        Entity       ← the OpenDEA subject (the Entity being described)
        Assertion    ← the KnowledgeAsset (prov:Entity / prov:Activity)
        Activity     ← the activity that produced the assertion
                       (import, mapping, manual capture)
        Agent        ← the actor (``asserted_by`` / ``mapping.owner``)
        Source       ← the ExternalSystem the activity read from

* **CR-11BD — Integration provenance chain**
    End-to-end walk::

        OpenDEA Entity
           ↓ (traces-to)
        Assertion (KnowledgeAsset)
           ↓ (traces-to)
        Evidence
           ↓ (traces-to)
        Mapping (SemanticMapping)        ← CR-11E
           ↓ (via)
        Adapter (IntegrationAdapter)     ← CR-11C/D
           ↓ (reads)
        ExternalIdentifier link          ← CR-11I
           ↓ (into)
        External Record
           ↓ (in)
        External System                  ← CR-11B

The chain is the defining capability of a trustworthy enterprise semantic
platform: *every* canonical fact remains traceable back to where it came from.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..graph import GraphStore, Node
from ..interoperability import (ExternalIdentifier, ExternalSystem,
                                IntegrationAdapter, InteropRegistry,
                                SemanticMapping, split_concept_ref)
from .model import Assertion, ProvenanceError
from .service import ProvenanceService


# --------------------------------------------------------------------- models


@dataclass(frozen=True)
class ExternalProvenanceLink:
    """One hop in the integration provenance chain (CR-11BD).

    ``role`` is the canonical CR-11 hop label ("assertion", "evidence",
    "source", "mapping", "adapter", "external-identifier", "external-system")
    so callers can serialize it independently of the resolved entity kind.
    ``provenance_kind`` mirrors the runtime ``provenance_kind`` taxonomy so the
    chain can be filtered without traversing the graph.
    """

    id: str
    role: str
    type: str
    name: str
    provenance_kind: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id, "role": self.role,
            "type": self.type, "name": self.name,
        }
        if self.provenance_kind:
            d["provenanceKind"] = self.provenance_kind
        if self.properties:
            d["properties"] = self.properties
        return d


@dataclass(frozen=True)
class ExternalProvenanceChain:
    """CR-11BD — full integration provenance chain for one OpenDEA entity."""

    subject: str
    assertions: List[Assertion]
    links: List[ExternalProvenanceLink]
    external_systems: List[ExternalIdentifier]
    sources: List[Node]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "assertions": [a.as_dict() for a in self.assertions],
            "links": [l.as_dict() for l in self.links],
            "externalIdentifiers": [e.as_dict() for e in self.external_systems],
            "sources": [{"id": s.id, "type": s.type, "name": s.name,
                         "properties": s.properties} for s in self.sources],
        }


@dataclass(frozen=True)
class ProvMapping:
    """CR-11AE — PROV-style projection of one OpenDEA Assertion.

    The OpenDEA runtime carries its own assertion/evidence/source vocabulary.
    When consumers want to interoperate with W3C PROV tooling this projection
    is enough; nothing in the runtime re-shapes to PROV internally, so the two
    representations stay parallel rather than lossy.
    """

    entity: str                # prov:Entity — the OpenDEA subject
    activity: str              # prov:Activity — what produced the assertion
    agent: str                 # prov:Agent — who/what did it
    source: str = ""           # prov:Entity (the ExternalSystem)
    used: List[str] = field(default_factory=list)   # prov:Usage → evidence ids

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provEntity": self.entity,
            "provActivity": self.activity,
            "provAgent": self.agent,
            "provSource": self.source or None,
            "provUsed": self.used or None,
        }


# --------------------------------------------------------------------- service


class ExternalProvenanceService:
    """CR-11O / CR-11AE / CR-11BD — external-facing provenance service.

    Composes the canonical :class:`ProvenanceService` with the
    :class:`InteropRegistry` so that an OpenDEA entity can always be traced
    from its canonical representation back through the adapter / mapping /
    external identifier / external system that produced it.

    No graph mutation happens here: external provenance is read by walking the
    canonical provenance graph *plus* the interoperability registry; the only
    write method (``record_external_source``) is a convenience that pairs a
    fresh Evidence/Source pair with an ExternalIdentifier link so callers
    don't have to thread three separate APIs.
    """

    # Provenance roles used in :class:`ExternalProvenanceLink`.
    ROLE_ASSERTION = "assertion"
    ROLE_EVIDENCE = "evidence"
    ROLE_SOURCE = "source"
    ROLE_MAPPING = "mapping"
    ROLE_ADAPTER = "adapter"
    ROLE_EXTERNAL_IDENTIFIER = "external-identifier"
    ROLE_EXTERNAL_SYSTEM = "external-system"

    def __init__(self, store: GraphStore,
                 registry: Optional[InteropRegistry] = None):
        self.store = store
        self.registry = registry or InteropRegistry()
        self.provenance = ProvenanceService(store)

    # ------------------------------------------------------------------ writes

    def record_external_source(self, evidence_id: str, source_id: str,
                               external_identifier: ExternalIdentifier,
                               adapter: Optional[IntegrationAdapter] = None,
                               mapping: Optional[SemanticMapping] = None,
                               *,
                               system: Optional[ExternalSystem] = None,
                               evidence_name: Optional[str] = None,
                               source_name: Optional[str] = None
                               ) -> Dict[str, Any]:
        """Register an external-source evidence pair *and* its link atomically.

        The evidence captures what we saw; the source records where it came
        from; the :class:`ExternalIdentifier` correlation is registered with
        the InteropRegistry in the same call so the trio can never get out of
        sync. The adapter and mapping are optional but, when supplied, they
        anchor the chain end-to-end.
        """
        if self.registry.resolve(external_identifier.system,
                                 external_identifier.identifier) is not None:
            raise ProvenanceError(
                f"external identifier {external_identifier.system}:"
                f"{external_identifier.identifier} is already linked")
        self.registry.link_external_identifier(external_identifier)
        if system is not None and system.id != external_identifier.system:
            raise ProvenanceError(
                "external system declared on the source must match the link "
                "system (CR-11B)")
        if system is not None:
            self.registry.register_system(system)
        elif external_identifier.system not in self.registry.systems:
            raise ProvenanceError(
                f"external system {external_identifier.system!r} is not "
                "registered — pass it via ``system`` first")
        if adapter is not None:
            self.registry.register_adapter(adapter)
        if mapping is not None:
            self.registry.register_mapping(mapping)

        evidence_node = self.provenance.register_evidence(
            evidence_id,
            evidence_name or f"External evidence {external_identifier.identifier}",
            confidence=external_identifier.identifier_type == "primary" and 1.0
                        or None,
            capturedFrom=external_identifier.system,
            externalIdentifier=external_identifier.identifier,
        )
        source_node = self.provenance.register_source(
            source_id,
            source_name or f"Source {external_identifier.system}",
            system=external_identifier.system,
            externalIdentifier=external_identifier.identifier,
        )
        return {
            "evidence": evidence_node, "source": source_node,
            "external_identifier": external_identifier,
        }

    # ------------------------------------------------------------------- reads

    def prov_projection(self, assertion_id: str) -> ProvMapping:
        """CR-11AE — project one :class:`Assertion` to PROV-shaped concepts."""
        assertion = self.provenance.read_assertion(assertion_id)
        evidence_ids = list(assertion.evidence)
        source = assertion.source or ""
        return ProvMapping(
            entity=assertion.subject,
            activity=f"activity.{assertion.id}",
            agent=assertion.asserted_by or "unknown",
            source=source,
            used=evidence_ids,
        )

    def integration_chain(self, subject: str
                          ) -> ExternalProvenanceChain:
        """CR-11BD — full external-facing provenance chain for ``subject``.

        Walks the canonical provenance graph (assertions / evidence / sources)
        and, for every evidence that carries an external-identifier correlation,
        extends the chain through the adapter → mapping → external system that
        produced it. The chain ends at the :class:`ExternalSystem` node, which
        is the *origin* of the line.
        """
        chain = self.provenance.why(subject)
        links: List[ExternalProvenanceLink] = []
        external_ids: List[ExternalIdentifier] = []
        seen_sources: set[str] = {s.id for s in chain.sources}

        for evidence in chain.evidence:
            ext_id = evidence.properties.get("externalIdentifier")
            system_name = evidence.properties.get("capturedFrom")
            if not ext_id or not system_name:
                continue
            matched = next(
                (ei for ei in self.registry.identifiers
                 if ei.system == system_name and ei.identifier == ext_id),
                None)
            if matched is None:
                continue
            external_ids.append(matched)
            links.append(self._link_from_node(
                evidence, self.ROLE_EVIDENCE))
            for adapter in self.registry.adapters.values():
                if adapter.source == system_name:
                    links.append(ExternalProvenanceLink(
                        id=adapter.id, role=self.ROLE_ADAPTER,
                        type="IntegrationAdapter", name=adapter.name,
                        provenance_kind="adapter",
                        properties={
                            "protocol": adapter.protocol,
                            "format": adapter.format,
                            "version": adapter.version,
                            "externalSystem": adapter.source,
                        },
                    ))
                    break
            system = self.registry.systems.get(matched.system)
            mapping_for_system = self._mapping_for_system(system)
            if mapping_for_system is not None:
                links.append(self._link_from_mapping(mapping_for_system))
            links.append(self._link_from_external_identifier(matched))
            if system is not None:
                # The ExternalSystem hop is the origin of the line.
                links.append(self._link_from_system(system))
                if system.id not in seen_sources and self.store.has_entity(
                        system.id):
                    chain.sources.append(self.store.get_entity(system.id))
                    seen_sources.add(system.id)

        for assertion in chain.assertions:
            links.insert(
                0, self._link_from_assertion(assertion))

        return ExternalProvenanceChain(
            subject=subject,
            assertions=chain.assertions,
            links=links,
            external_systems=external_ids,
            sources=chain.sources,
        )

    # --------------------------------------------------------------- helpers

    def _link_from_node(self, node: Node, role: str) -> ExternalProvenanceLink:
        return ExternalProvenanceLink(
            id=node.id, role=role, type=node.type, name=node.name,
            provenance_kind=node.properties.get("provenance_kind", ""),
            properties={
                k: v for k, v in node.properties.items()
                if k not in {"provenance_kind"} and not isinstance(v, (list, dict))
            },
        )

    def _link_from_assertion(self, assertion: Assertion
                             ) -> ExternalProvenanceLink:
        props: Dict[str, Any] = {
            "status": assertion.status.value,
            "assertedBy": assertion.asserted_by,
        }
        if assertion.confidence is not None:
            props["confidence"] = assertion.confidence
        if assertion.source:
            props["source"] = assertion.source
        return ExternalProvenanceLink(
            id=assertion.id, role=self.ROLE_ASSERTION,
            type="KnowledgeAsset",
            name=f"Assertion about {assertion.subject}",
            provenance_kind="assertion", properties=props,
        )

    def _link_from_mapping(self, mapping: SemanticMapping
                           ) -> ExternalProvenanceLink:
        return ExternalProvenanceLink(
            id=f"mapping.{mapping.source_concept}->{mapping.target_concept}",
            role=self.ROLE_MAPPING, type="SemanticMapping",
            name=f"{mapping.source_concept} → {mapping.target_concept}",
            provenance_kind="mapping",
            properties={
                "relationship": mapping.relationship.value,
                "confidence": mapping.confidence.value,
                "lossiness": mapping.lossiness.value,
                "owner": mapping.owner,
                "version": mapping.version,
            },
        )

    def _link_from_external_identifier(self, link: ExternalIdentifier
                                       ) -> ExternalProvenanceLink:
        return ExternalProvenanceLink(
            id=f"extlink.{link.system}.{link.identifier}",
            role=self.ROLE_EXTERNAL_IDENTIFIER, type="ExternalIdentifier",
            name=f"{link.system}:{link.identifier}",
            provenance_kind="external-identifier",
            properties={
                "system": link.system, "identifier": link.identifier,
                "entity": link.entity,
                "identifierType": link.identifier_type,
            },
        )

    def _mapping_for_system(self, system: Optional[ExternalSystem]
                             ) -> Optional[SemanticMapping]:
        """Pick the mapping whose ``source_concept`` namespace matches the
        system's ``provider`` (case-insensitive) — the most reliable signal
        we have without forcing every mapping to carry a system ref.
        Falls back to the first mapping whose target_concept is ``opendea:``
        and whose ``source_concept`` namespace prefix is non-empty.
        """
        if system is None:
            return None
        provider = (system.provider or "").lower()
        if provider:
            for mapping in self.registry.mappings.values():
                ns, _ = split_concept_ref(mapping.source_concept)
                if ns and ns.lower() == provider:
                    return mapping
        for mapping in self.registry.mappings.values():
            ns, _ = split_concept_ref(mapping.source_concept)
            target_ns, _ = split_concept_ref(mapping.target_concept)
            if ns and target_ns == "opendea":
                return mapping
        return None

    @staticmethod
    def _link_from_system(system: ExternalSystem) -> ExternalProvenanceLink:
        return ExternalProvenanceLink(
            id=system.id, role="external-system", type="ExternalSystem",
            name=system.name, provenance_kind="external-system",
            properties={
                "type": system.type, "provider": system.provider,
                "version": system.version,
                "classification": system.classification,
            },
        )


# Re-export for ergonomic imports.
__all__ = [
    "ExternalProvenanceLink",
    "ExternalProvenanceChain",
    "ProvMapping",
    "ExternalProvenanceService",
]
