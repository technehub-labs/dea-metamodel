"""Risk — generated from schemas/entities/risk.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Risk(Entity):
    """A condition or event that threatens the enterprise's ability to persist or to realize a capability/objective. OpenDEAM v0.3.0 (ADR-0003), L2/Risk & Compliance."""

    type: Literal['Risk']
    risk_category: Optional[Literal['strategic', 'operational', 'regulatory', 'technology', 'financial', 'reputational']] = None
    """Risk classification."""
    likelihood: Optional[Literal['rare', 'unlikely', 'possible', 'likely', 'almost-certain']] = None
    """Assessed likelihood."""
    impact: Optional[Literal['negligible', 'minor', 'moderate', 'major', 'severe']] = None
    """Assessed impact."""
