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
    domain: Literal['integration', 'data', 'application', 'infrastructure', 'security', 'business', 'technology']
    """Primary domain."""
    abstraction_level: Literal['conceptual', 'logical', 'physical']
    """Abstraction level of this blueprint."""
    scope: Optional[str] = None
    """What the blueprint covers and boundaries."""
    layers: Optional[list[str]] = None
    key_components: Optional[list[str]] = None
    """SolutionComponent IDs that define this blueprint."""
    patterns: Optional[list[str]] = None
    """ArchitecturePattern IDs this blueprint is composed of (ADR-0004 D5)."""
    related_blueprints: Optional[list[str]] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    related_guardrails: Optional[list[str]] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    related_tenets: Optional[list[str]] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
