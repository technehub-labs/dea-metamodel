"""CR-012 Phase 1 — Signal + Observation data model.

CR-012 §3.1 (Observation), §3.2 (Signal), §6 design constraints.
The data model is the contract; :class:`SignalStore` enforces the
audit chain on top of it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..model.identity import is_canonical_id


class SignalError(Exception):
    """A Signal invariant (CR-012 §3.2, §6.3) has been violated."""


# ---------------------------------------------------------------- vocabularies
class SignalClassification(str, Enum):
    """CR-012 §3.2 vocabulary — every Signal carries one of these."""
    MATURITY_GAP = "maturity_gap"
    COMPLIANCE_DRIFT = "compliance_drift"
    RISK = "risk"
    CAPABILITY_GAP = "capability_gap"
    FEDERATION_ANOMALY = "federation_anomaly"
    MAPPING_STALENESS = "mapping_staleness"
    AGENT_ANOMALY = "agent_anomaly"
    OBSERVATION_ONLY = "observation_only"


class SignalSeverity(str, Enum):
    """CR-012 §3.2 vocabulary."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SignalConfidence(str, Enum):
    """CR-012 confidence vocabulary (matches MappingConfidence scale)."""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class SignalLifecycleStatus(str, Enum):
    """CR-012 §3.2 / lifecycle.yaml — directed graph, no skipping."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


# Allowed lifecycle transitions (CR-012 lifecycle.yaml invariant).
_LIFECYCLE_TRANSITIONS: Dict[SignalLifecycleStatus, List[SignalLifecycleStatus]] = {
    SignalLifecycleStatus.OPEN: [
        SignalLifecycleStatus.ACKNOWLEDGED,
    ],
    SignalLifecycleStatus.ACKNOWLEDGED: [
        SignalLifecycleStatus.IN_REVIEW,
        SignalLifecycleStatus.DISMISSED,
        SignalLifecycleStatus.RESOLVED,
    ],
    SignalLifecycleStatus.IN_REVIEW: [
        SignalLifecycleStatus.ACCEPTED,
        SignalLifecycleStatus.DISMISSED,
        SignalLifecycleStatus.RESOLVED,
    ],
    SignalLifecycleStatus.ACCEPTED: [
        SignalLifecycleStatus.DISMISSED,
        SignalLifecycleStatus.RESOLVED,
    ],
    SignalLifecycleStatus.DISMISSED: [],
    SignalLifecycleStatus.RESOLVED: [],
}


# ----------------------------------------------------------------- helpers
def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_entities(entities: List[str]) -> List[str]:
    out: List[str] = []
    for ent in entities or []:
        if not is_canonical_id(ent):
            raise SignalError(
                f"entity {ent!r} is not a canonical OpenDEA id (CR-012 §3.2)")
        if ent not in out:
            out.append(ent)
    if not out:
        raise SignalError("a Signal must reference at least one entity (CR-012 §3.2)")
    return out


# ----------------------------------------------------------------- Observation
@dataclass(frozen=True)
class Observation:
    """CR-012 §3.1 — raw governed output of one reasoning cycle.

    An Observation is recorded evidence, NOT an inference (ADR-008, CR-9R/T).
    Promotion to a Signal is an explicit, auditable decision.
    """
    id: str
    cycle_id: str
    subject: str
    kind: str  # pattern_name@version
    evidence: List[str] = field(default_factory=list)
    confidence: SignalConfidence = SignalConfidence.MEDIUM
    scope: str = ""
    observed_at: str = field(default_factory=_utcnow)

    def __post_init__(self):
        if not is_canonical_id(self.id):
            raise SignalError(f"observation id {self.id!r} is not canonical")
        if not is_canonical_id(self.cycle_id):
            raise SignalError(f"cycle id {self.cycle_id!r} is not canonical")
        if not is_canonical_id(self.subject):
            raise SignalError(f"subject {self.subject!r} is not canonical")
        if "@" not in self.kind:
            raise SignalError(
                f"observation kind {self.kind!r} must be 'pattern@version' "
                "(CR-012 pattern-library convention)")
        # Observation is frozen — coerce enums via object.__setattr__
        object.__setattr__(self, "confidence", SignalConfidence(self.confidence))
        if not self.evidence:
            raise SignalError(
                "observations must carry at least one piece of evidence "
                "(CR-012 observation.yaml invariant)")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cycleId": self.cycle_id,
            "subject": self.subject,
            "kind": self.kind,
            "evidence": list(self.evidence),
            "confidence": self.confidence.value,
            "scope": self.scope,
            "observedAt": self.observed_at,
        }


# ----------------------------------------------------------------- Signal
@dataclass
class Signal:
    """CR-012 §3.2 — governed enterprise-attention artifact.

    Every Signal carries classification, severity, confidence, entities,
    owner, rationale, status, and the audit chain (lifecycle transitions).
    Construction is strict: missing owner / classification / severity /
    confidence is rejected; critical-severity without an
    escalation_policy_ref is rejected.
    """
    id: str
    observation_ref: str
    classification: SignalClassification
    severity: SignalSeverity
    confidence: SignalConfidence
    entities: List[str]
    owner: str
    rationale: str = ""
    proposed_action: str = ""
    status: SignalLifecycleStatus = SignalLifecycleStatus.OPEN
    escalation_policy_ref: str = ""
    raised_at: str = field(default_factory=_utcnow)
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    rationale_at_dismiss: str = ""

    def __post_init__(self):
        if not is_canonical_id(self.id):
            raise SignalError(f"signal id {self.id!r} is not canonical")
        if not is_canonical_id(self.observation_ref):
            raise SignalError(
                f"observation_ref {self.observation_ref!r} is not canonical")
        if not is_canonical_id(self.owner):
            raise SignalError(
                f"owner {self.owner!r} must be a canonical OpenDEA Actor "
                "(CR-012 §3.2 vocabulary invariant, ADR-009)")
        if self.severity == SignalSeverity.CRITICAL and not self.escalation_policy_ref:
            raise SignalError(
                "critical signals MUST carry an escalation_policy_ref "
                "(CR-012 §3.5 severity invariant)")
        if self.confidence == SignalConfidence.UNCERTAIN and self.severity not in {
                SignalSeverity.INFO, SignalSeverity.LOW}:
            raise SignalError(
                "an UNCERTAIN-confidence signal is permitted only at severity "
                "info or low (CR-012 confidence vocabulary invariant)")
        self.classification = SignalClassification(self.classification)
        self.severity = SignalSeverity(self.severity)
        self.confidence = SignalConfidence(self.confidence)
        self.status = SignalLifecycleStatus(self.status)
        self.entities = _normalise_entities(self.entities)
        if self.proposed_action and "approved: true" in self.proposed_action.lower():
            raise SignalError(
                "proposed_action on a Signal MUST NOT carry an `approved: true` "
                "flag — proposals are a separate type (CR-012 §3.2 invariant)")
        # initial transition is the raise itself
        self._history: List[Dict[str, str]] = [
            {"to": self.status.value, "at": self.raised_at, "by": ""},
        ]

    # --- public state ----------------------------------------------------
    @property
    def history(self) -> List[Dict[str, str]]:
        return list(self._history)

    # --- transitions ------------------------------------------------------
    _RESOLVING_STATES = {
        SignalLifecycleStatus.DISMISSED, SignalLifecycleStatus.RESOLVED,
    }

    def transition(self, to: SignalLifecycleStatus, *, by: str = "",
                   dismissed_rationale: str = "") -> None:
        """Apply a lifecycle transition. CR-012 lifecycle.yaml invariant.

        - Rejects skips (e.g. open → resolved without acknowledgment is
          forbidden unless the signal is auto-resolved at raise — and we do
          not allow that in Phase 1).
        - Sets acknowledged_at / resolved_at appropriately.
        - Records the transition in ``history`` (audit chain, CR-012 §6.5).
        """
        to = SignalLifecycleStatus(to)
        allowed = _LIFECYCLE_TRANSITIONS[self.status]
        if to not in allowed:
            raise SignalError(
                f"lifecycle transition {self.status.value} → {to.value} is not "
                "permitted (CR-012 lifecycle.yaml directed graph)")
        if to in self._RESOLVING_STATES and not self.acknowledged_at:
            # acknowledged_at is the FIRST acknowledge; resolve from any non-open state
            self.acknowledged_at = _utcnow()
        if to == SignalLifecycleStatus.DISMISSED and not dismissed_rationale:
            raise SignalError(
                "dismissal MUST carry a rationale (CR-012 lifecycle.yaml "
                "invariant: 'dismissed' requires rationale)")
        self.status = to
        self.rationale_at_dismiss = dismissed_rationale if to == \
            SignalLifecycleStatus.DISMISSED else self.rationale_at_dismiss
        if to in self._RESOLVING_STATES:
            self.resolved_at = _utcnow()
        self._history.append({"to": to.value, "at": _utcnow(), "by": by})

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "id": self.id,
            "observationRef": self.observation_ref,
            "classification": self.classification.value,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "entities": list(self.entities),
            "owner": self.owner,
            "rationale": self.rationale,
            "status": self.status.value,
            "raisedAt": self.raised_at,
            "history": list(self._history),
        }
        if self.proposed_action:
            out["proposedAction"] = self.proposed_action
        if self.escalation_policy_ref:
            out["escalationPolicyRef"] = self.escalation_policy_ref
        if self.acknowledged_at:
            out["acknowledgedAt"] = self.acknowledged_at
        if self.resolved_at:
            out["resolvedAt"] = self.resolved_at
        if self.rationale_at_dismiss:
            out["dismissRationale"] = self.rationale_at_dismiss
        return out