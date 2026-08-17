"""Escalation — generated from schemas/entities/escalation.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Escalation(Entity):
    """An escalation raised when authority, confidence or policy boundaries are exceeded (CR-7 §25; G011): actions exceeding an Agent's authority must escalate or fail safely."""

    type: Literal['Escalation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    trigger: Optional[str] = None
    raised_by: Optional[str] = None
    target_ref: Optional[str] = None
    """Who/what the escalation goes to."""
    reason: Optional[str] = None
    raised_at: Optional[str] = None
