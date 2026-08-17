"""AgentOpportunity — generated from schemas/entities/agent-opportunity.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AgentOpportunity(Entity):
    """A derived decision-support object identifying where an agent could create value (CR-7 §56): subject capability, potential agent, expected value, risk, readiness, recommended autonomy. Derived — never an architectural entity assumed to exist in the target architecture. Links DMM assessment to agentic transformation (§55)."""

    type: Literal['AgentOpportunity']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    subject_ref: Optional[str] = None
    potential_agent_ref: Optional[str] = None
    expected_value: Optional[str] = None
    risk: Optional[str] = None
    readiness: Optional[str] = None
    recommended_autonomy: Optional[str] = None
    derived: Optional[Literal[True]] = None
