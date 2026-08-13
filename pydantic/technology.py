"""Technology — generated from schemas/entities/technology.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Technology(Entity):
    """A technology choice (language, framework, runtime, database, library) used by one or more solution components. Technologies are governed and standardised via the Standards + Principles catalogs. Catalog: technehub-labs/dea-catalog-patterns (shared with ArchitecturePattern)."""

    type: Literal['Technology']
    technology_category: Literal['language', 'framework', 'runtime', 'database', 'library', 'build-tool', 'ci-cd', 'monitoring', 'orchestration', 'platform']
    """Category of technology."""
    vendor: Optional[str] = None
    """Vendor or open-source project."""
    version_requirement: Optional[str] = None
    """Required version range."""
    lifecycle_status: Optional[Literal['approved', 'deprecated', 'banned', 'experimental']] = None
    """Enterprise lifecycle status."""
