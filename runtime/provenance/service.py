"""CR-9.2 — provenance graph service.

Builds the CR-9P evidence graph on top of the CR-9.1 canonical graph:

    Conclusion (subject)
        ↑ traces-to
    Assertion (KnowledgeAsset, provenance_kind=assertion)
        ↑ traces-to
    Evidence
        ↑ traces-to
    EvidenceSource

All writes pass through RuntimeService, so canonical identity, type and
relationship-endpoint validation remain registry-backed. The service never
mutates the subject's authoritative properties: it records competing claims as
separate assertions (CR-9O) and resolves them only through explicit status
transitions — never by overwrite (CR-9CQ).
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from ..api import RuntimeService
from ..graph import EntityNotFoundError, GraphStore, Node
from ..graph.base import utcnow
from .model import Assertion, AssertionStatus, ProvenanceChain, ProvenanceError


class ProvenanceService:
    """Canonical provenance graph facade for a GraphStore."""

    ASSERTION_KIND = "assertion"
    EVIDENCE_KIND = "evidence"
    SOURCE_KIND = "source"

    def __init__(self, store: GraphStore):
        self.store = store
        self.service = RuntimeService(store)

    # ---- registrations ----
    def register_source(self, source_id: str, name: str,
                        system: Optional[str] = None,
                        **properties: Any) -> Node:
        """Register an EvidenceSource — the origin evidence was collected from."""
        props = {**properties, "provenance_kind": self.SOURCE_KIND}
        if system:
            props["system"] = system
        return self.service.create_entity(
            source_id, "EvidenceSource", name, properties=props)

    def register_evidence(self, evidence_id: str, name: str,
                          confidence: Optional[float] = None,
                          **properties: Any) -> Node:
        """Register Evidence — support for a claim, never the claim itself."""
        props = {**properties, "provenance_kind": self.EVIDENCE_KIND}
        if confidence is not None:
            props["confidence"] = confidence
        return self.service.create_entity(
            evidence_id, "Evidence", name, properties=props)

    # ---- assertions ----
    def assert_fact(self, assertion_id: str, subject: str,
                    claim: Dict[str, Any], asserted_by: str,
                    status: AssertionStatus = AssertionStatus.PROPOSED,
                    confidence: Optional[float] = None,
                    valid_from: Optional[str] = None,
                    valid_to: Optional[str] = None,
                    evidence: Optional[Iterable[str]] = None,
                    source: Optional[str] = None,
                    derived_from: Optional[Iterable[str]] = None,
                    derivation_rule: Optional[str] = None) -> Assertion:
        """Record a claim about a subject as an explicit assertion.

        The subject is never mutated. Evidence/source links are lineage edges:
        assertion → evidence → source (or assertion → source when no evidence
        was supplied).
        """
        status = AssertionStatus(status)
        if status == AssertionStatus.APPROVED:
            raise ProvenanceError(
                "assertions cannot be created approved — approval is an "
                "explicit state transition (CR-9CQ)")
        if not self.store.has_entity(subject):
            raise EntityNotFoundError(f"assertion subject {subject!r} not found")
        evidence_ids = list(evidence or [])
        for evidence_id in evidence_ids:
            self._require_kind(evidence_id, self.EVIDENCE_KIND)
        if source:
            self._require_kind(source, self.SOURCE_KIND)
        derived_ids = list(derived_from or [])
        for parent_id in derived_ids:
            if not self.store.has_entity(parent_id):
                raise ProvenanceError(
                    f"derived_from reference {parent_id!r} is not present in the graph")

        props = {
            "provenance_kind": self.ASSERTION_KIND,
            "subject": subject,
            "claim": claim,
            "asserted_by": asserted_by,
            "status": status.value,
        }
        if confidence is not None:
            props["confidence"] = confidence
        if valid_from:
            props["valid_from"] = valid_from
        if valid_to:
            props["valid_to"] = valid_to
        if derived_ids:
            props["derived_from"] = derived_ids
        if derivation_rule:
            props["derivation_rule"] = derivation_rule

        edge_provenance: Dict[str, Any] = {
            "assertedBy": asserted_by,
            "sourceSystem": "opendea-runtime"}
        if derived_ids:
            edge_provenance["derived_from"] = derived_ids
        if derivation_rule:
            edge_provenance["derivation_rule"] = derivation_rule

        self.service.create_entity(
            assertion_id, "KnowledgeAsset", f"Assertion about {subject}",
            properties=props,
            assertion={"status": "declared", "asserted_by": asserted_by,
                       **({"confidence": confidence} if confidence is not None else {})})
        self.service.create_relationship(
            assertion_id, "traces-to", subject, status="active",
            valid_from=valid_from, valid_to=valid_to,
            provenance=edge_provenance)
        for evidence_id in evidence_ids:
            self.service.create_relationship(
                assertion_id, "traces-to", evidence_id, status="active",
                provenance={"assertedBy": asserted_by,
                            "sourceSystem": "opendea-runtime"})
            if source:
                self.service.create_relationship(
                    evidence_id, "traces-to", source, status="active",
                    provenance={"assertedBy": asserted_by,
                                "sourceSystem": "opendea-runtime"})
        if source and not evidence_ids:
            self.service.create_relationship(
                assertion_id, "traces-to", source, status="active",
                provenance={"assertedBy": asserted_by,
                            "sourceSystem": "opendea-runtime"})
        return self._read_assertion(assertion_id)

    def transition_assertion(self, assertion_id: str,
                             to: AssertionStatus,
                             actor: str,
                             reason: str = "") -> Assertion:
        """Explicitly transition an assertion's lifecycle status (CR-9O).

        Approval is authoritative and therefore requires an actor; every
        transition appends an auditable history entry instead of overwriting
        the prior state silently (CR-9CQ).
        """
        to = AssertionStatus(to)
        assertion = self._read_assertion(assertion_id)
        allowed = {
            AssertionStatus.PROPOSED: {
                AssertionStatus.VERIFIED, AssertionStatus.REJECTED,
                AssertionStatus.DISPUTED, AssertionStatus.SUPERSEDED},
            AssertionStatus.VERIFIED: {
                AssertionStatus.APPROVED, AssertionStatus.REJECTED,
                AssertionStatus.DISPUTED, AssertionStatus.SUPERSEDED},
            AssertionStatus.APPROVED: {
                AssertionStatus.SUPERSEDED, AssertionStatus.DISPUTED},
            AssertionStatus.DISPUTED: {
                AssertionStatus.PROPOSED, AssertionStatus.VERIFIED,
                AssertionStatus.REJECTED, AssertionStatus.SUPERSEDED},
            AssertionStatus.REJECTED: set(),
            AssertionStatus.SUPERSEDED: set(),
        }
        if to not in allowed.get(assertion.status, set()):
            raise ProvenanceError(
                f"illegal assertion transition {assertion.status.value} → "
                f"{to.value} (CR-9O)")
        if to == AssertionStatus.APPROVED and not actor:
            raise ProvenanceError("approval requires an explicit actor (CR-9CQ)")

        node = self.store.get_entity(assertion_id)
        history = list(node.properties.get("status_history", []))
        history.append({
            "from": assertion.status.value,
            "to": to.value,
            "actor": actor,
            "reason": reason,
            "at": utcnow().isoformat(),
        })
        props = {**node.properties, "status": to.value,
                 "status_history": history}
        if to == AssertionStatus.APPROVED:
            props["approved_by"] = actor
        self.store.update_entity(assertion_id, properties=props)
        return self._read_assertion(assertion_id)

    def assertions_for(self, subject: str) -> List[Assertion]:
        """All assertions made about a subject — competing claims coexist."""
        if not self.store.has_entity(subject):
            raise EntityNotFoundError(f"assertion subject {subject!r} not found")
        return [self._read_assertion(e.source)
                for e in self.store.edges_of(subject, direction="in",
                                             rel_type="traces-to")
                if self._is_kind(e.source, self.ASSERTION_KIND)]

    # ---- explainability ----
    def why(self, subject: str) -> ProvenanceChain:
        """CR-9T/BC — answer 'Why?' with the full provenance chain."""
        assertions = self.assertions_for(subject)
        evidence: List[Node] = []
        sources: List[Node] = []

        def add_unique(nodes: List[Node], node: Node) -> None:
            if node.id not in {n.id for n in nodes}:
                nodes.append(node)

        for assertion in assertions:
            evidence_ids = []
            for edge in self.store.edges_of(assertion.id, direction="out",
                                            rel_type="traces-to"):
                if self._is_kind(edge.target, self.EVIDENCE_KIND):
                    evidence_ids.append(edge.target)
                    add_unique(evidence, self.store.get_entity(edge.target))
                elif self._is_kind(edge.target, self.SOURCE_KIND):
                    add_unique(sources, self.store.get_entity(edge.target))
            for evidence_id in evidence_ids:
                for edge in self.store.edges_of(evidence_id, direction="out"):
                    if self._is_kind(edge.target, self.SOURCE_KIND):
                        add_unique(sources, self.store.get_entity(edge.target))

        # Canonical loaded models already express evidence as
        # Evidence -supports→ AssessmentResult (CR-5 §16/§17). Include that
        # graph shape in Why? alongside runtime assertion lineage.
        for edge in self.store.edges_of(subject, direction="in", rel_type="supports"):
            if self._is_kind(edge.source, self.EVIDENCE_KIND):
                add_unique(evidence, self.store.get_entity(edge.source))
        return ProvenanceChain(subject=subject, assertions=assertions,
                               evidence=evidence, sources=sources)

    def read_assertion(self, assertion_id: str) -> Assertion:
        """Public read accessor for a single assertion by id."""
        return self._read_assertion(assertion_id)

    # ---- internals ----
    def _read_assertion(self, assertion_id: str) -> Assertion:
        node = self.store.get_entity(assertion_id)
        props = node.properties
        if props.get("provenance_kind") != self.ASSERTION_KIND:
            raise ProvenanceError(f"node {assertion_id!r} is not an assertion")
        evidence = [e.target for e in self.store.edges_of(
            assertion_id, direction="out", rel_type="traces-to")
            if self._is_kind(e.target, self.EVIDENCE_KIND)]
        source = next((e.target for e in self.store.edges_of(
            assertion_id, direction="out", rel_type="traces-to")
            if self._is_kind(e.target, self.SOURCE_KIND)), None)
        if source is None and evidence:
            source = next((e.target for e in self.store.edges_of(
                evidence[0], direction="out", rel_type="traces-to")
                if self._is_kind(e.target, self.SOURCE_KIND)), None)
        return Assertion(
            id=node.id,
            subject=props["subject"],
            claim=props.get("claim", {}),
            asserted_by=props.get("asserted_by", ""),
            status=AssertionStatus(props.get("status", AssertionStatus.PROPOSED.value)),
            confidence=props.get("confidence"),
            valid_from=props.get("valid_from"),
            valid_to=props.get("valid_to"),
            source=source,
            evidence=evidence,
            derived_from=list(props.get("derived_from", [])),
            derivation_rule=props.get("derivation_rule"),
        )

    def _require_kind(self, node_id: str, kind: str) -> None:
        if not self._is_kind(node_id, kind):
            raise ProvenanceError(
                f"node {node_id!r} is not registered provenance {kind}")

    def _is_kind(self, node_id: str, kind: str) -> bool:
        try:
            node = self.store.get_entity(node_id)
        except EntityNotFoundError:
            return False
        if node.properties.get("provenance_kind") == kind:
            return True
        canonical_types = {
            self.EVIDENCE_KIND: "Evidence",
            self.SOURCE_KIND: "EvidenceSource",
        }
        return node.type == canonical_types.get(kind)
