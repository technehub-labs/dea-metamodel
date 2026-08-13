"""ModelFeedbackSignal — generated from schemas/entities/model-feedback-signal.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ModelFeedbackSignal(Entity):
    """Drift, performance-degradation, or outcome-quality feedback captured from Events, used to trigger retraining of an AI/ML Model. OpenDEAM v0.3.0 (ADR-0003), L4/Model Operations."""

    type: Literal['ModelFeedbackSignal']
    signal_kind: Optional[Literal['drift', 'performance-degradation', 'outcome-quality']] = None
    """Discriminator within dea-catalog-model-deployments (ADR-0002 D6)."""
    derived_from: Optional[list[str]] = None
    """Event/streams the feedback is captured from."""
