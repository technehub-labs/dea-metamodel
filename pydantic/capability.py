"""Capability — generated from schemas/entities/capability.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Capability(Entity):
    """A business or technical capability that the enterprise possesses or requires."""

    type: Literal['Capability']
    capability_type: Literal['business', 'technical', 'hybrid']
    """Nature of the capability."""
    domain: Optional[str] = None
    """Business domain this capability belongs to."""
    maturity_level: Literal['nascent', 'emerging', 'defined', 'managed', 'optimizing']
    """CMMI-style maturity assessment."""
    owner: Optional[str] = None
    """Role or team responsible for this capability."""
    parent_capability: Optional[str] = None
    """ID of parent Capability in the capability hierarchy."""
    child_capabilities: Optional[list[str]] = None
    """IDs of child Capabilities."""
    realized_by: Optional[list[str]] = None
    """SolutionComponent IDs that realize this capability."""
    processes: Optional[list[str]] = None
    """Process IDs that deliver this capability."""
    metrics: Optional[list[str]] = None
    """Metric IDs that measure this capability."""
