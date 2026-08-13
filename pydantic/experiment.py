"""Experiment — generated from schemas/entities/experiment.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Experiment(Entity):
    """A bounded, time-boxed test of a Signal's relevance to the enterprise before committing investment. OpenDEAM v0.3.0 (ADR-0003), L2/Innovation & Foresight."""

    type: Literal['Experiment']
    hypothesis: Optional[str] = None
    """What the experiment tests."""
    signal_ref: Optional[str] = None
    """The Signal that triggered this experiment."""
    outcome: Optional[Literal['pending', 'validated', 'invalidated', 'inconclusive']] = None
    """Experiment result."""
