"""PolicyDecision — generated from schemas/entities/policy-decision.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class PolicyDecision(Entity):
    """The outcome of a policy evaluation — e.g. 'Agent A is permitted to access Dataset X' (CR-7 §39). Not the same as an enterprise Decision ('deploy Agent A'); the two are kept separate."""

    type: Literal['PolicyDecision']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    evaluation_ref: Optional[str] = None
    decision: Optional[Literal['permit', 'deny', 'permit-with-conditions', 'escalate']] = None
    decided_at: Optional[str] = None
