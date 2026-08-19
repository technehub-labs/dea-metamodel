"""CR-9.3 — semantic reasoning model (CR-9Q/R/S/T).

Reasoning is levelled, rules are governed runtime artifacts, and every derived
result carries the reasoning level, rule reference, supporting assertions and
confidence needed to answer "Why?" (CR-9T). Derived knowledge is proposed,
never silently authoritative (CR-9CQ).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional

from ..graph import GraphStore


class ReasoningLevel(Enum):
    """CR-9R — reasoning levels are never blended."""

    DETERMINISTIC = 1
    ONTOLOGICAL = 2
    GRAPH = 3
    PROBABILISTIC = 4
    GENERATIVE = 5


class RuleSeverity(str, Enum):
    """CR-9S — governance severity for a rule consequence."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ReasoningError(Exception):
    """Reasoning rule or inference invariant violated."""


RULE_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$")


@dataclass(frozen=True)
class RuleMatch:
    """One conclusion produced by evaluating a rule against a graph."""

    subject: str
    claim: Dict[str, Any]
    derived_from: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    explanation: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ReasoningError("confidence must be between 0 and 1")


@dataclass
class Rule:
    """CR-9S — a first-class, governed reasoning rule."""

    id: str
    name: str
    level: ReasoningLevel
    applies_to: List[str]
    condition: Callable[[GraphStore], Iterable[RuleMatch]]
    version: str = "1.0.0"
    enabled: bool = True
    profile: str = "dea:core"
    severity: RuleSeverity = RuleSeverity.ERROR
    description: str = ""

    def __post_init__(self):
        if not RULE_ID.match(self.id):
            raise ReasoningError(
                f"rule id {self.id!r} must use the DEA-INF-001 convention")
        self.level = ReasoningLevel(self.level)
        self.severity = RuleSeverity(self.severity)

    def evaluate(self, store: GraphStore) -> List[RuleMatch]:
        """Evaluate the rule. Disabled rules are inert (CR-9S)."""
        if not self.enabled:
            return []
        return list(self.condition(store))


@dataclass(frozen=True)
class Inference:
    """CR-9Q/T — a derived assertion with full explainability metadata."""

    subject: str
    claim: Dict[str, Any]
    rule_id: str
    rule_name: str
    level: ReasoningLevel
    confidence: Optional[float]
    derived_from: List[str]
    explanation: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "claim": self.claim,
            "rule": {"id": self.rule_id, "name": self.rule_name},
            "level": self.level.value,
            "confidence": self.confidence,
            "derivedFrom": self.derived_from,
            "explanation": self.explanation,
        }
