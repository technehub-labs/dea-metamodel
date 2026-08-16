"""Actor — generated from schemas/entities/actor.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Actor(Entity):
    """A performer of enterprise processes — human, team, system, or AI agent. Actors are internal performers; external or affected parties are Stakeholders (separate entity). Catalog: technehub-labs/dea-catalog-actors."""

    type: Literal['Actor']
    actor_type: Literal['human', 'team', 'system', 'ai-agent', 'hybrid']
    """The kind of performer. 'human' is an individual person; 'team' is a group of humans acting as a unit; 'system' is software/hardware automation; 'ai-agent' is an ML/LLM/agent-based system that performs autonomously; 'hybrid' is a human-team-system composition."""
    scope: Optional[Literal['individual', 'team', 'departmental', 'enterprise', 'ecosystem']] = None
    """The scope at which the actor operates."""
    owner: Optional[str] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    capabilities: Optional[list[str]] = None
    """References to Capabilities in technehub-labs/dea-catalog-business-capabilities that this Actor performs."""
    processes_performed: Optional[list[str]] = None
    """References to Processes in technehub-labs/dea-catalog-processes that this Actor performs."""
    links: Optional[dict[str, Any]] = None
    """Optional links to other catalogs. stakeholder_ref points to a Stakeholder entry when the Actor represents an internal user who is also a stakeholder in some other process; digital_identity_ref points to a dea-catalog-digital-identities entry when the Actor has a digital twin."""
