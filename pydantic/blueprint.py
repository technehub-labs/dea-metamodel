"""Blueprint — generated from schemas/entities/blueprint.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Blueprint(Entity):
    """A composed, reusable target-state design assembled from Architecture Patterns, providing a template for solution design. Renamed from Reference Model in v0.4.0 (ADR-0004 D5). Catalog: technehub-labs/dea-catalog-blueprints."""

    type: Literal['Blueprint']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    domain: Literal['integration', 'data', 'application', 'infrastructure', 'security', 'business', 'technology']
    """Primary domain."""
    abstraction_level: Literal['conceptual', 'logical', 'physical']
    """Abstraction level of this blueprint."""
    scope: Optional[str] = None
    """What the blueprint covers and boundaries."""
    layers: Optional[list[str]] = None
