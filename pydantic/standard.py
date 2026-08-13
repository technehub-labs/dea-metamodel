"""Standard — generated from schemas/entities/standard.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Standard(Entity):
    """A referenced industry standard or framework (TOGAF, Zachman, ISO, IEEE, etc.)."""

    type: Literal['Standard']
    standard_body: str
    domain: Literal['enterprise-architecture', 'data-architecture', 'software-architecture', 'security-architecture', 'cloud-architecture', 'integration-architecture', 'process-architecture', 'governance']
    """Primary domain this standard applies to."""
    url: Optional[str] = None
    """Canonical URL to the standard's documentation."""
    license: Optional[str] = None
    coverage: Optional[list[str]] = None
    """Aspects covered: framework, methodology, ontology, notation, etc."""
    conforms_to: Optional[list[str]] = None
    """Standards this one references or builds upon."""
    related_patterns: Optional[list[str]] = None
    related_principles: Optional[list[str]] = None
