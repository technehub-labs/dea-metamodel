"""InfrastructureComponent — generated from schemas/entities/infrastructure-component.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class InfrastructureComponent(Entity):
    """An infrastructure-as-code managed resource (compute, network, storage, security group) that hosts or supports solution components. A subClass of SolutionComponent with component_type='infrastructure'. Catalog: technehub-labs/dea-catalog-application-components (shared with ApplicationComponent)."""

    type: Literal['InfrastructureComponent']
    infrastructure_type: Optional[Literal['compute', 'network', 'storage', 'security', 'container', 'serverless', 'database-host']] = None
    """Category of infrastructure resource."""
    iac_tool: Optional[str] = None
    """Infrastructure-as-code tool that provisions this component (Terraform, CloudFormation, Pulumi)."""
