"""ReferenceModel — generated from schemas/entities/reference-model.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ReferenceModel(Entity):
    """A reference architecture model serving as a template for concrete architectures."""

    type: Literal['ReferenceModel']
    domain: Literal['integration', 'data', 'application', 'infrastructure', 'security', 'business', 'technology']
    """Primary domain."""
    abstraction_level: Literal['conceptual', 'logical', 'physical']
    """Abstraction level of this reference model."""
    scope: Optional[str] = None
    """What the model covers and boundaries."""
    layers: Optional[list[str]] = None
    key_components: Optional[list[str]] = None
    """SolutionComponent IDs that define this reference model."""
    patterns: Optional[list[str]] = None
    """ArchitecturePattern IDs used in this model."""
    related_reference_models: Optional[list[str]] = None
    related_standards: Optional[list[str]] = None
    related_principles: Optional[list[str]] = None
