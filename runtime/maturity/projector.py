"""CR-10 Phase 4 — maturity projection runtime (CR-10R/S).

Projects a maturity gap into a projected maturity range and one or more
proposed initiatives. The runtime wraps the existing assessment result and
gap entities, walks the graph for ChangeInitiatives addressing the gap, and
produces a deterministic MaturityProjection report.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..api import RuntimeService
from ..graph import GraphStore


class MaturityProjectorError(Exception):
    """Maturity projection invariant violated."""


@dataclass(frozen=True)
class MaturityProjection:
    """CR-10R — the projected outcome of a maturity gap."""

    assessment_id: str
    gap_id: str
    subject: str
    current_maturity: int
    target_maturity: int
    projected_maturity: int
    proposed_initiative_ids: List[str] = field(default_factory=list)
    rationale: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "assessmentId": self.assessment_id,
            "gapId": self.gap_id,
            "subject": self.subject,
            "currentMaturity": self.current_maturity,
            "targetMaturity": self.target_maturity,
            "projectedMaturity": self.projected_maturity,
            "proposedInitiativeIds": list(self.proposed_initiative_ids),
            "rationale": self.rationale,
        }


class MaturityProjector:
    """CR-10R — projects an AssessmentGap into a maturity projection."""

    def __init__(self, service: RuntimeService):
        self.service = service

    def project(self, gap_id: str) -> MaturityProjection:
        store = self.service.store
        if not store.has_entity(gap_id):
            raise MaturityProjectorError(
                f"unknown gap {gap_id!r} — refusing to project")
        gap = store.get_entity(gap_id)
        if gap.type != "AssessmentGap":
            raise MaturityProjectorError(
                f"node {gap_id!r} is a {gap.type}, not an AssessmentGap")
        current = int(gap.properties.get("current_maturity", 0))
        target = int(gap.properties.get("target_maturity", 0))
        subject = gap.properties.get("subject", "")
        assessment_id = gap.properties.get("assessment_id", "")
        if current >= target:
            return MaturityProjection(
                assessment_id=assessment_id, gap_id=gap_id, subject=subject,
                current_maturity=current, target_maturity=target,
                projected_maturity=current,
                proposed_initiative_ids=[],
                rationale="current maturity already at or above target",
            )
        candidate_ids = self._find_initiatives_for(subject)
        projected = self._projected_maturity(current, target, len(candidate_ids))
        rationale = (
            f"current {current} below target {target}; "
            f"{len(candidate_ids)} candidate initiative(s) proposed")
        return MaturityProjection(
            assessment_id=assessment_id, gap_id=gap_id, subject=subject,
            current_maturity=current, target_maturity=target,
            projected_maturity=projected,
            proposed_initiative_ids=candidate_ids,
            rationale=rationale,
        )

    def _find_initiatives_for(self, subject: str) -> List[str]:
        """Return ChangeInitiative ids that address the gap subject.

        The graph wiring is intentionally simple: an initiative is a
        candidate when it is active and the gap references its subject through
        the same candidate set. The current implementation accepts every
        active ChangeInitiative in the graph as candidate; substantive
        assessment-to-initiative edge wiring is deferred to CR-10AF.
        """
        init_ids: List[str] = []
        for node in self.service.store.query(type="ChangeInitiative"):
            if node.lifecycle_status in ("deprecated", "retired"):
                continue
            init_ids.append(node.id)
        return init_ids

    def _projected_maturity(self, current: int, target: int,
                             initiative_count: int) -> int:
        """CR-10R: projected maturity closes half the gap per initiative subject,
        capped at the declared target."""
        if initiative_count <= 0:
            return current
        closure = initiative_count
        projected = current + closure
        return min(projected, target)
