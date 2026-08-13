"""EcosystemPlatform — generated from schemas/entities/ecosystem-platform.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class EcosystemPlatform(Entity):
    """A standing multi-sided structure the enterprise hosts for repeated exchange among many ecosystem actors (marketplace, partner API program, developer portal). OpenDEAM v0.3.0 (ADR-0003), L1/Ecosystem Platforms."""

    type: Literal['EcosystemPlatform']
    platform_kind: Optional[Literal['marketplace', 'developer-portal', 'partner-api-program', 'data-exchange']] = None
    """The form of multi-sided exchange the platform hosts."""
    participant_count: Optional[int] = None
    """Approximate number of active third-party participants."""
