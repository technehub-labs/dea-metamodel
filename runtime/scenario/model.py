"""CR-10 Phase 1 — Scenario model.

A scenario is a **first-class semantic object, not a copy of the enterprise
model** (CR-10 §1). It references a Baseline and carries only its delta
(CR-10B/C): explicit changes, assumptions, constraints and expected outcomes.

Design rules encoded here:

- **Baseline immutability (CR-10B/BG).** A Baseline is a named, frozen
  snapshot reference. Scenario evaluation MUST NOT mutate it.
- **Explicit deltas (CR-10C).** Changes use a closed operation vocabulary
  (ADD…SCALE) so scenarios stay compact and traceable.
- **Assumptions are semantic objects (CR-10D).** Never buried inside
  simulation logic: id, statement, value, unit, confidence, source, owner.
- **Constraints are semantic objects (CR-10E).** subject/operator/value/
  unit/priority/source — budget, time, risk, availability, maturity,
  regulatory.
- **Uncertainty is explicit (CR-10O).** Outcomes declare their knowledge
  class (Known…Unknown) and confidence; forecasts are never presented as
  deterministic facts.
- **Immutability after evaluation (CR-10AG).** Once evaluated, a scenario
  version is frozen; changes produce a new version, never a silent edit.
- **Recommendation ≠ decision (CR-10AI).** This model has no approval
  semantics; approval lives in the CR-7/CR-9.7 decision machinery.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..model.identity import is_canonical_id


class ChangeOperation(str, Enum):
    """CR-10C — the closed scenario-delta vocabulary."""
    ADD = "ADD"
    REMOVE = "REMOVE"
    REPLACE = "REPLACE"
    MODIFY = "MODIFY"
    RECLASSIFY = "RECLASSIFY"
    CONNECT = "CONNECT"
    DISCONNECT = "DISCONNECT"
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"
    MOVE = "MOVE"
    SCALE = "SCALE"


class ScenarioStatus(str, Enum):
    """CR-10A lifecycle. Terminal-ish side states included."""
    DRAFT = "draft"
    DEFINED = "defined"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    CLOSED = "closed"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


#: Legal forward transitions. APPROVED requires the decision machinery
#: (CR-10AI — a scenario never approves itself); the engine exposes
#: transitions up to EVALUATED and records the rest as externally driven.
_ALLOWED = {
    ScenarioStatus.DRAFT: {ScenarioStatus.DEFINED, ScenarioStatus.CANCELLED},
    ScenarioStatus.DEFINED: {ScenarioStatus.EVALUATING, ScenarioStatus.DRAFT,
                             ScenarioStatus.DEFERRED, ScenarioStatus.CANCELLED},
    ScenarioStatus.EVALUATING: {ScenarioStatus.EVALUATED, ScenarioStatus.DEFERRED,
                                ScenarioStatus.CANCELLED},
    ScenarioStatus.EVALUATED: {ScenarioStatus.APPROVED, ScenarioStatus.REJECTED,
                               ScenarioStatus.DEFERRED, ScenarioStatus.SUPERSEDED},
    ScenarioStatus.APPROVED: {ScenarioStatus.IMPLEMENTED, ScenarioStatus.SUPERSEDED},
    ScenarioStatus.IMPLEMENTED: {ScenarioStatus.CLOSED},
    ScenarioStatus.DEFERRED: {ScenarioStatus.DRAFT, ScenarioStatus.CANCELLED},
    ScenarioStatus.REJECTED: set(),
    ScenarioStatus.SUPERSEDED: set(),
    ScenarioStatus.CANCELLED: set(),
    ScenarioStatus.CLOSED: set(),
}


class Uncertainty(str, Enum):
    """CR-10O — knowledge classes for forecasts and outcomes."""
    KNOWN = "known"
    ESTIMATED = "estimated"
    ASSUMED = "assumed"
    PREDICTED = "predicted"
    SIMULATED = "simulated"
    UNKNOWN = "unknown"


class ScenarioError(Exception):
    """Scenario invariants violated (lifecycle, identity, frozen version)."""


@dataclass(frozen=True)
class Baseline:
    """CR-10B/CR-9BG — a named, immutable snapshot reference.

    ``snapshot`` holds the frozen graph bytes (node/edge dicts) at baseline
    time. Scenarios read from it; nothing writes to it.
    """
    id: str
    name: str
    snapshot: Dict[str, Any]  # {"nodes": [...], "edges": [...]}
    source: str = ""          # e.g. model id + version, or "runtime"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        if not is_canonical_id(self.id):
            raise ScenarioError(f"baseline id {self.id!r} is not canonical (CR-8 §7)")


@dataclass
class Change:
    """CR-10C — one explicit delta operation.

    Fields used per operation:
      ADD         target=new id; node={type,name,properties?}
      REMOVE      target=id (cascades edges)
      REPLACE     target=old id; node={id,type,name,properties?} for the
                  replacement; edges are rewired to the replacement
      MODIFY      target=id; set={field: value} (name/properties/lifecycle_status)
      RECLASSIFY  target=id; set={"type": NewType}
      CONNECT     target=source id; edge={type, to, valid_from?, status?, provenance?}
      DISCONNECT  target=source id; edge={type, to}
      ENABLE      target=id  → lifecycle_status=active
      DISABLE     target=id  → lifecycle_status=deprecated
      MOVE        target=source id; edge={type, from, to}
      SCALE       target=id; set={"scale": n} (property)
    """
    target: str
    operation: ChangeOperation
    node: Optional[Dict[str, Any]] = None
    edge: Optional[Dict[str, Any]] = None
    set: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""

    def as_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"target": self.target, "operation": self.operation.value}
        if self.node is not None:
            d["node"] = self.node
        if self.edge is not None:
            d["edge"] = self.edge
        if self.set:
            d["set"] = self.set
        if self.rationale:
            d["rationale"] = self.rationale
        return d


@dataclass
class Assumption:
    """CR-10D — an explicit, inspectable assumption."""
    id: str
    statement: str
    value: Optional[Any] = None
    unit: Optional[str] = None
    confidence: Optional[float] = None
    source: str = ""
    owner: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "id": self.id, "statement": self.statement, "value": self.value,
            "unit": self.unit, "confidence": self.confidence,
            "source": self.source, "owner": self.owner}.items() if v is not None and v != ""}


@dataclass
class Constraint:
    """CR-10E — an explicit constraint (budget, time, risk, regulatory…)."""
    subject: str
    operator: str  # <=, >=, <, >, ==, !=
    value: Any
    unit: str = ""
    priority: str = "medium"  # low | medium | high | mandatory
    source: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "subject": self.subject, "operator": self.operator, "value": self.value,
            "unit": self.unit, "priority": self.priority,
            "source": self.source}.items() if v is not None and v != ""}


@dataclass
class Outcome:
    """CR-10I/O — a projected, uncertainty-qualified outcome."""
    metric: str
    baseline: Optional[Any] = None
    expected: Optional[Any] = None
    target: Optional[Any] = None
    unit: str = ""
    confidence: Optional[float] = None
    uncertainty: Uncertainty = Uncertainty.ESTIMATED
    timeframe: str = ""
    evidence: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "metric": self.metric, "baseline": self.baseline, "expected": self.expected,
            "target": self.target, "unit": self.unit, "confidence": self.confidence,
            "uncertainty": self.uncertainty.value, "timeframe": self.timeframe,
            "evidence": self.evidence or None}.items() if v is not None and v != ""}


@dataclass
class Scenario:
    """CR-10A — the first-class scenario object."""
    id: str
    name: str
    baseline: str  # Baseline id
    description: str = ""
    owner: str = ""
    purpose: str = ""
    changes: List[Change] = field(default_factory=list)
    assumptions: List[Assumption] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    expected_outcomes: List[Outcome] = field(default_factory=list)
    status: ScenarioStatus = ScenarioStatus.DRAFT
    version: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)
    _frozen: bool = field(default=False, repr=False)

    def __post_init__(self):
        if not is_canonical_id(self.id):
            raise ScenarioError(f"scenario id {self.id!r} is not canonical (CR-8 §7)")

    # ---- CR-10A: derived view of what the delta touches ----
    @property
    def affected_entities(self) -> List[str]:
        seen: List[str] = []
        for c in self.changes:
            for eid in [c.target,
                        (c.node or {}).get("id"),
                        (c.edge or {}).get("to"),
                        (c.edge or {}).get("from")]:
                if eid and eid not in seen:
                    seen.append(eid)
        return seen

    # ---- CR-10AG: evaluated versions are immutable ----
    @property
    def frozen(self) -> bool:
        return self._frozen

    def _assert_mutable(self):
        if self._frozen:
            raise ScenarioError(
                f"scenario {self.id!r} v{self.version} is frozen (evaluated). "
                "CR-10AG: create a new version instead of silently modifying "
                "an evaluated scenario.")

    def add_change(self, change: Change) -> None:
        self._assert_mutable()
        self.changes.append(change)

    def add_assumption(self, assumption: Assumption) -> None:
        self._assert_mutable()
        self.assumptions.append(assumption)

    def add_constraint(self, constraint: Constraint) -> None:
        self._assert_mutable()
        self.constraints.append(constraint)

    def add_outcome(self, outcome: Outcome) -> None:
        self._assert_mutable()
        self.expected_outcomes.append(outcome)

    def transition(self, to: ScenarioStatus) -> None:
        allowed = _ALLOWED.get(self.status, set())
        if to not in allowed:
            raise ScenarioError(
                f"illegal lifecycle transition {self.status.value} → {to.value} "
                f"(allowed: {sorted(s.value for s in allowed) or 'none'})")
        self.status = to
        if to in (ScenarioStatus.EVALUATED,):
            self._frozen = True

    def new_version(self) -> "Scenario":
        """CR-10AG — evolve a frozen scenario by explicit versioning."""
        import copy
        nxt = copy.deepcopy(self)
        nxt.version = self.version + 1
        nxt.status = ScenarioStatus.DRAFT
        nxt._frozen = False
        nxt.provenance = {**self.provenance, "supersedes": f"{self.id}@v{self.version}"}
        self.status = ScenarioStatus.SUPERSEDED if self.status == ScenarioStatus.EVALUATED else self.status
        return nxt

    # ---- CR-10AF: reproducibility ----
    def as_dict(self) -> Dict[str, Any]:
        """Canonical serialization — the scenario definition half of the
        reproducibility tuple (baseline version + scenario definition +
        assumptions + rules + simulation version, CR-10AF)."""
        return {
            "id": self.id, "name": self.name, "version": self.version,
            "baseline": self.baseline, "description": self.description,
            "owner": self.owner, "purpose": self.purpose,
            "status": self.status.value,
            "changes": [c.as_dict() for c in self.changes],
            "assumptions": [a.as_dict() for a in self.assumptions],
            "constraints": [c.as_dict() for c in self.constraints],
            "expectedOutcomes": [o.as_dict() for o in self.expected_outcomes],
            "affectedEntities": self.affected_entities,
            "provenance": self.provenance,
        }

    def reproducibility_hash(self) -> str:
        """Stable digest of the definition — two evaluations of the same
        definition on the same baseline version MUST produce the same hash."""
        payload = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()
