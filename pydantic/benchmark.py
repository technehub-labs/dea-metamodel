"""Benchmark — generated from schemas/entities/benchmark.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Benchmark(Entity):
    """A comparative reference external to the enterprise's own assessment (CR-5 §28). Benchmarking is modeled separately from assessment: AssessmentResult ≠ Benchmark and AssessmentTarget ≠ Benchmark (A011)."""

    type: Literal['Benchmark']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    framework_ref: Optional[str] = None
    population_ref: Optional[str] = None
    authority: Optional[str] = None
    """The body publishing the benchmark."""
    published_at: Optional[str] = None
