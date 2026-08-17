"""PolicyEvaluation — generated from schemas/entities/policy-evaluation.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class PolicyEvaluation(Entity):
    """The evaluation of an action or subject against a policy (CR-7 §38): policy, subject, action, context, result, reason, timestamp. Produces a PolicyDecision (§39)."""

    type: Literal['PolicyEvaluation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    policy_ref: Optional[str] = None
    subject_ref: Optional[str] = None
    action_ref: Optional[str] = None
    context: Optional[str] = None
    result: Optional[Literal['compliant', 'non-compliant', 'conditional', 'not-applicable']] = None
    reason: Optional[str] = None
    evaluated_at: Optional[str] = None
