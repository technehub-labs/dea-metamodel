"""AgentSkill — generated from schemas/entities/agent-skill.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AgentSkill(Entity):
    """A reusable capability/competency available to an Agent (CR-7 §48/§49): purpose, inputs, outputs, preconditions, postconditions, tools, policies, decision/action scope, failure modes and escalation. AgentSkill ≠ BusinessCapability (§48): a skill may implement or contribute to one."""

    type: Literal['AgentSkill']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    purpose: Optional[str] = None
    inputs: Optional[str] = None
    outputs: Optional[str] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None
    failure_modes: Optional[str] = None
    escalation: Optional[str] = None
