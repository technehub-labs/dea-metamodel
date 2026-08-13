"""Control — generated from schemas/entities/control.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Control(Entity):
    """A mechanism (process, technical, or organizational) that mitigates a Risk or enforces a Regulation. OpenDEAM v0.3.0 (ADR-0003), L2/Risk & Compliance."""

    type: Literal['Control']
    control_type: Optional[Literal['preventive', 'detective', 'corrective']] = None
    """Control mechanism class."""
    mitigates: Optional[list[str]] = None
    """Risk ids this control mitigates."""
