"""CR-9.2 — provenance graph model (CR-9O/P/T/BC).

The provenance layer makes claims, evidence and sources explicit graph citizens
without changing the frozen CR-8 specification. Runtime assertions are encoded
as canonical ``KnowledgeAsset`` nodes carrying ``provenance_kind=assertion``;
evidence and sources use the CR-5 ``Evidence`` / ``EvidenceSource`` types, and
the chain uses the canonical ``traces-to`` lineage relationship.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..graph import Node


class AssertionStatus(str, Enum):
    """CR-9O — assertion lifecycle statuses."""

    PROPOSED = "proposed"
    VERIFIED = "verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DISPUTED = "disputed"


class ProvenanceError(Exception):
    """Provenance graph invariant violated."""


@dataclass(frozen=True)
class Assertion:
    """CR-9O — a claim about a subject, with explicit provenance."""

    id: str
    subject: str
    claim: Dict[str, Any]
    asserted_by: str
    status: AssertionStatus = AssertionStatus.PROPOSED
    confidence: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    source: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    derived_from: List[str] = field(default_factory=list)
    derivation_rule: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "id": self.id,
            "subject": self.subject,
            "claim": self.claim,
            "assertedBy": self.asserted_by,
            "status": self.status.value,
            "confidence": self.confidence,
            "validFrom": self.valid_from,
            "validTo": self.valid_to,
            "source": self.source,
            "evidence": self.evidence or None,
            "derivedFrom": self.derived_from or None,
            "derivationRule": self.derivation_rule,
        }.items() if v is not None}


@dataclass(frozen=True)
class ProvenanceChain:
    """CR-9BC — Conclusion → Assertions → Evidence → Source Systems."""

    subject: str
    assertions: List[Assertion]
    evidence: List[Node]
    sources: List[Node]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "assertions": [a.as_dict() for a in self.assertions],
            "evidence": [{"id": e.id, "type": e.type, "name": e.name,
                          "properties": e.properties} for e in self.evidence],
            "sources": [{"id": s.id, "type": s.type, "name": s.name,
                         "properties": s.properties} for s in self.sources],
        }
