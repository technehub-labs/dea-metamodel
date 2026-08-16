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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    component_type: Literal['application', 'infrastructure', 'integration']
    """Component category (discriminator for subtypes)."""
    deployment_model: Literal['on-premise', 'iaas', 'paas', 'saas', 'faas', 'hybrid', 'multi-cloud']
    """Deployment context."""
    services_provided: Optional[list[str]] = None
    services_consumed: Optional[list[str]] = None
    patterns_applied: Optional[list[str]] = None
    dependencies: Optional[list[str]] = None
    security_classification: Optional[Literal['public', 'internal', 'confidential', 'restricted']] = None
