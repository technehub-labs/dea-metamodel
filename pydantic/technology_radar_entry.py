"""TechnologyRadarEntry — generated from schemas/entities/technology-radar-entry.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class TechnologyRadarEntry(Entity):
    """An emerging technology or technique being tracked (assess/trial/adopt/hold) prior to becoming a governed L5 Technology. OpenDEAM v0.3.0 (ADR-0003), L2/Innovation & Foresight."""

    type: Literal['TechnologyRadarEntry']
    radar_ring: Optional[Literal['assess', 'trial', 'adopt', 'hold']] = None
    """Current radar position."""
    graduates_to: Optional[str] = None
    """Technology id if adopted."""
