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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    technology_category: Literal['language', 'framework', 'runtime', 'database', 'library', 'build-tool', 'ci-cd', 'monitoring', 'orchestration', 'platform']
    """Category of technology."""
    vendor: Optional[str] = None
    """Vendor or open-source project."""
    version_requirement: Optional[str] = None
    """Required version range."""
    adoption_status: Optional[Literal['approved', 'deprecated', 'banned', 'experimental']] = None
    """CR-003: renamed from lifecycle_status — this is technology ADOPTION posture, distinct from the universal entity lifecycle (CR-3R). Enterprise lifecycle status."""
