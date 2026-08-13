"""Signal — generated from schemas/entities/signal.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Signal(Entity):
    """A weak or early indicator of environmental change (market, technology, regulatory, competitive) worth tracking before it forces adaptation. OpenDEAM v0.3.0 (ADR-0003), L2/Innovation & Foresight."""

    type: Literal['Signal']
    signal_source: Optional[Literal['market', 'technology', 'regulatory', 'competitor', 'customer']] = None
    """Where the signal originates."""
    strength: Optional[Literal['weak', 'emerging', 'strong']] = None
    """Assessed signal strength."""
