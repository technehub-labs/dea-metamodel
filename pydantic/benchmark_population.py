"""BenchmarkPopulation — generated from schemas/entities/benchmark-population.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class BenchmarkPopulation(Entity):
    """The peer or industry population over which a benchmark is computed (CR-5 §28)."""

    type: Literal['BenchmarkPopulation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    segment: Optional[str] = None
    """Industry, geography, size band or other segmentation."""
    population_size: Optional[int] = None
