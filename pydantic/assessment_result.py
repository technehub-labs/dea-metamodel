"""AssessmentResult — generated from schemas/entities/assessment-result.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentResult(Entity):
    """The central object connecting assessment to architecture (CR-5 §10): subject, criterion, score or maturity level, evidence, confidence, assessor, framework and temporal anchors. A result never modifies the identity of the assessed entity (A007)."""

    type: Literal['AssessmentResult']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    assessment_ref: Optional[str] = None
    subject_ref: Optional[str] = None
    """Reference to the AssessmentSubject (A002)."""
    criterion_ref: Optional[str] = None
    """Reference to the AssessmentCriterion (A003)."""
    score: Optional[dict[str, Any]] = None
    maturity_level_ref: Optional[str] = None
    """MaturityLevel within the framework's MaturityModel (A005)."""
    confidence: Optional[dict[str, Any]] = None
    """CR-5 §18 common confidence structure."""
    state_role: Optional[Literal['baseline', 'current', 'target', 'forecast']] = None
    """CR-5 §20/§29: role of this result in the maturity trajectory."""
    observed_at: Optional[str] = None
    """When the underlying evidence was collected (CR-5 §22)."""
    assessed_at: Optional[str] = None
    """When the assessment was performed (CR-5 §22)."""
    valid_from: Optional[str] = None
    """When the result is considered applicable (CR-5 §22)."""
    assessor: Optional[str] = None
    provenance: Optional[str] = None
    """CR-5 §19: who assessed, with what framework, when, based on what evidence."""
    evidence_refs: Optional[list[str]] = None
