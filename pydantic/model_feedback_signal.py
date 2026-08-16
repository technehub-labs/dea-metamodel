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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    signal_kind: Optional[Literal['drift', 'performance-degradation', 'outcome-quality']] = None
    """Discriminator within dea-catalog-model-deployments (ADR-0002 D6)."""
