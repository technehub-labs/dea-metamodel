"""BenchmarkReference — generated from schemas/entities/benchmark-reference.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class BenchmarkReference(Entity):
    """A specific comparative value drawn from a benchmark population (CR-5 §28): industry level, peer median, percentile. Compared against results via benchmarked-against — never treated as a result (A011)."""

    type: Literal['BenchmarkReference']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    benchmark_ref: Optional[str] = None
    value: Optional[float] = None
    percentile: Optional[float] = None
    criterion_ref: Optional[str] = None
