"""Provenance  :  generated from schemas/entities/provenance.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Provenance(Entity):
    """A first-class record of how a Measurement result came to exist, carrying the 11 provenance elements of CR-MET-011 section 5 (Q18a). W3C PROV alignment: the Observation is the PROV entity, the collection and calculation steps are PROV activities, and the responsible-party concept carries the accountable party. Reuses dea:Evidence, dea:EvidenceSource, and dea:EvidenceArtifact (CR-5 section 16) rather than duplicating evidence semantics. A Provenance record is 1:1 with the Observation it describes; it is never shared between results."""

    type: Literal['Provenance']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    source_ref: str
    """Provenance element 1: the original data source (a dea:EvidenceSource). Never a free-text label."""
    source_record_ref: str
    """Provenance element 2: the specific originating record or dataset."""
    collection_activity: str
    """Provenance element 3: how the information was acquired (a dea:BusinessProcess or a described extraction step). The W3C PROV activity."""
    calculation_activity: str
    """Provenance element 4: how the result was derived (the dea:Measurement that executed the formula). The W3C PROV activity."""
    transformation_chain: Optional[list[str]] = None
    """Provenance element 5: the ordered processing and conversion steps applied between collection and calculation."""
    responsible_party_ref: str
    """Provenance element 6: the party accountable for the result (a dea:Actor). The W3C PROV responsible-party concept. Covers person, system, or automated process."""
    configuration_ref: str
    """Provenance element 7: the measurement configuration in effect when the result was produced."""
    formula_version_ref: str
    """Provenance element 8: the exact calculation definition applied, including the version. A result MUST NOT be attributed to a formula without its version."""
    metric_version_ref: str
    """Provenance element 9: the exact Metric definition applied, including the version. This is the binding record for historical reconstruction: the meaning of a historical result is the meaning the Metric had at the version recorded here."""
    evidence_refs: Optional[list[str]] = None
    """Provenance element 10: supporting source material (dea:Evidence / dea:EvidenceArtifact)."""
    timestamps: Optional[dict[str, Any]] = None
    """Provenance element 11: the relevant temporal information. The 7 CR-MET-011 temporal dimensions MUST NOT be collapsed into one timestamp (Q17)."""
    reproducibility: Optional[dict[str, Any]] = None
    """CR-MET-011 section 6: the declared reproducibility posture of the recorded result."""
