"""ModelDeployment — generated from schemas/entities/model-deployment.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ModelDeployment(Entity):
    """A running instance of an AI/ML Model, hosted on an Application Component, with its own version, monitoring state, and health. OpenDEAM v0.3.0 (ADR-0003), L4/Model Operations."""

    type: Literal['ModelDeployment']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    model_ref: Optional[str] = None
    """The AI/ML Model this deployment instantiates."""
    environment: Optional[Literal['dev', 'staging', 'production']] = None
    """Deployment environment."""
    deployment_kind: Optional[Literal['api-endpoint', 'batch', 'embedded', 'streaming']] = None
    """Discriminator within dea-catalog-model-deployments (ADR-0002 D6)."""
