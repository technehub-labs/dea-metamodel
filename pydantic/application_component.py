"""ApplicationComponent — generated from schemas/entities/application-component.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ApplicationComponent(Entity):
    """A deployable unit of an application system (a service, batch job, scheduled task). A subClass of SolutionComponent with component_type='application'. Catalog: technehub-labs/dea-catalog-application-components."""

    type: Literal['ApplicationComponent']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    deployment_unit: Optional[Literal['service', 'batch-job', 'scheduled-task', 'event-handler', 'lambda', 'daemon']] = None
    """How this application component is deployed and executed."""
    runtime: Optional[str] = None
    """Runtime environment (JVM 21, Node 24, Python 3.12, etc.)."""
