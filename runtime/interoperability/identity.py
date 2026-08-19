"""CR-11 Phase 2 — identity reconciliation and source authority.

CR-11J/K/L/M/N: external records are reconciled against canonical identity
without ever adopting external identifiers, silently merging uncertain matches,
or letting one source be authoritative for every property.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .model import InteropError


class ReconciliationState(str, Enum):
    """CR-11K — reconciliation states."""

    UNMATCHED = "UNMATCHED"
    CANDIDATE = "CANDIDATE"
    MATCHED = "MATCHED"
    MERGED = "MERGED"
    CONFLICTING = "CONFLICTING"
    REJECTED = "REJECTED"


class ConflictStatus(str, Enum):
    """CR-11L — conflict lifecycle."""

    OPEN = "open"
    RESOLVED = "resolved"
    DEFERRED = "deferred"
    OVERRIDDEN = "overridden"


class TieBreaker(str, Enum):
    """CR-11N — how authority ties are handled."""

    HIGHEST = "highest"
    NEWEST = "newest"
    MOST_CONFIDENT = "most-confident"
    HUMAN = "human"
    NO_WRITE = "no-write"


@dataclass(frozen=True)
class ConflictValue:
    """CR-11L — one source's competing value for a property."""

    source: str
    value: Any
    observed_at: str = ""
    confidence: Optional[float] = None

    def __post_init__(self):
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise InteropError("confidence must be between 0 and 1")

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "source": self.source, "value": self.value,
            "observedAt": self.observed_at or None,
            "confidence": self.confidence,
        }.items() if v is not None}


@dataclass(frozen=True)
class KnowledgeConflict:
    """CR-11L — preserved disagreement between external sources."""

    id: str
    entity: str
    property: str
    values: List[ConflictValue]
    status: ConflictStatus = ConflictStatus.OPEN
    resolution: Optional[Dict[str, Any]] = None
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None

    def __post_init__(self):
        object.__setattr__(self, "status", ConflictStatus(self.status))
        if len({repr(v.value) for v in self.values}) < 2:
            raise InteropError("a conflict requires at least two differing values")
        if self.status != ConflictStatus.OPEN and not self.resolution:
            raise InteropError("non-open conflicts require a resolution record")

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "id": self.id, "entity": self.entity, "property": self.property,
            "values": [v.as_dict() for v in self.values],
            "status": self.status.value, "resolution": self.resolution,
            "detectedAt": self.detected_at, "resolvedAt": self.resolved_at,
        }.items() if v is not None}


@dataclass(frozen=True)
class AuthorityPolicy:
    """CR-11N — property-specific source authority.

    ``weights`` maps ``(source, property) → 0.0…1.0``. A source with no
    declared weight has no authority for that property and must not be chosen
    by default (CR-11R: undefined authority = oscillation/corruption).
    """

    id: str
    scope: str
    weights: Dict[Tuple[str, str], float]
    tie_breaker: TieBreaker = TieBreaker.HIGHEST
    effective_from: str = ""
    effective_to: str = ""
    owner: str = ""
    approval: str = ""

    def __post_init__(self):
        object.__setattr__(self, "tie_breaker", TieBreaker(self.tie_breaker))
        for (source, property_), weight in self.weights.items():
            if not source or not property_:
                raise InteropError("authority weights require (source, property)")
            if not 0.0 <= weight <= 1.0:
                raise InteropError("authority weights must be between 0 and 1")

    def weight_for(self, source: str, property: str) -> float:
        return self.weights.get((source, property), 0.0)

    def authoritative_value(self, property: str,
                            values: List[ConflictValue]) -> ConflictValue:
        """Choose the authoritative value for one property.

        The losing values are not discarded here; callers preserve them in a
        KnowledgeConflict (CR-11L).
        """
        ranked = [(self.weight_for(v.source, property), v) for v in values]
        if not ranked or max(weight for weight, _ in ranked) <= 0.0:
            raise InteropError(
                f"no authority declared for property {property!r} (CR-11M/R)")
        highest = max(weight for weight, _ in ranked)
        winners = [v for weight, v in ranked if weight == highest]
        if len(winners) == 1:
            return winners[0]
        if self.tie_breaker == TieBreaker.NEWEST:
            return max(winners, key=lambda v: v.observed_at)
        if self.tie_breaker == TieBreaker.MOST_CONFIDENT:
            return max(winners, key=lambda v: v.confidence or 0.0)
        if self.tie_breaker in (TieBreaker.HUMAN, TieBreaker.NO_WRITE):
            raise InteropError(
                f"authority tie for {property!r} requires {self.tie_breaker.value}")
        return winners[0]

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "id": self.id, "scope": self.scope,
            "weights": [{"source": s, "property": p, "weight": w}
                        for (s, p), w in sorted(self.weights.items())],
            "tieBreaker": self.tie_breaker.value,
            "effectiveFrom": self.effective_from or None,
            "effectiveTo": self.effective_to or None,
            "owner": self.owner or None,
            "approval": self.approval or None,
        }.items() if v is not None}


@dataclass(frozen=True)
class ResolutionCandidate:
    """CR-9N/CR-11J — one possible canonical match."""

    entity: str
    score: float
    method: str = "semantic"
    evidence: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise InteropError("candidate score must be between 0 and 1")

    def as_dict(self) -> Dict[str, Any]:
        return {"entity": self.entity, "score": self.score,
                "method": self.method, "evidence": self.evidence}


@dataclass(frozen=True)
class EntityResolution:
    """CR-11J — the auditable result of reconciling an external record."""

    id: str
    system: str
    identifier: str
    state: ReconciliationState
    entity: Optional[str] = None
    score: float = 0.0
    method: str = "unknown"
    candidates: List[ResolutionCandidate] = field(default_factory=list)
    review_required: bool = True
    approved_by: str = ""
    evidence: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        object.__setattr__(self, "state", ReconciliationState(self.state))
        if not 0.0 <= self.score <= 1.0:
            raise InteropError("resolution score must be between 0 and 1")
        if self.state == ReconciliationState.MERGED and not self.approved_by:
            raise InteropError(
                "MERGED resolutions require explicit approval (CR-11L: never "
                "silently merge)")

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "id": self.id, "system": self.system, "identifier": self.identifier,
            "state": self.state.value, "entity": self.entity,
            "score": self.score, "method": self.method,
            "candidates": [c.as_dict() for c in self.candidates],
            "reviewRequired": self.review_required,
            "approvedBy": self.approved_by or None,
            "evidence": self.evidence or None,
            "createdAt": self.created_at,
        }.items() if v is not None}
