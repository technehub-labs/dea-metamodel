"""SolutionComponent — generated from schemas/entities/solution-component.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class SolutionComponent(Entity):
    """A physical or logical software or hardware component that implements capabilities. OpenDEAM v0.2.0 (ADR-0002 D3): this is an ABSTRACT parent — concrete subclasses (ApplicationComponent, InfrastructureComponent, IntegrationComponent) are realized in L5 and discriminated by component_type."""

    type: Literal['SolutionComponent']
    component_type: Literal['application', 'infrastructure', 'integration']
    """Component category (discriminator for subtypes)."""
    deployment_model: Literal['on-premise', 'iaas', 'paas', 'saas', 'faas', 'hybrid', 'multi-cloud']
    """Deployment context."""
    technology_stack: Optional[list[str]] = None
    """Technology IDs used in this component."""
    capabilities_realized: Optional[list[str]] = None
    services_provided: Optional[list[str]] = None
    services_consumed: Optional[list[str]] = None
    patterns_applied: Optional[list[str]] = None
    owner: Optional[str] = None
    dependencies: Optional[list[str]] = None
    security_classification: Optional[Literal['public', 'internal', 'confidential', 'restricted']] = None
