"""Unit  :  generated from schemas/entities/unit.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Unit(Entity):
    """A standard quantity in which a measure is expressed (CR-5 §9/Phase 2); percent, ratio, months, currency, count. Referenced by measures; never embedded in names."""

    type: Literal['Unit']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    symbol: Optional[str] = None
    quantity_kind: Optional[str] = None
    """e.g. ratio, duration, currency, count."""
    dimensionality: Optional[Literal['time', 'length', 'mass', 'currency', 'count', 'temperature', 'information_quantity', 'rate', 'ratio', 'dimensionless_index', 'composite']] = None
    """The dimensionality of the Unit (CR-MET-005). Time, length, mass, currency, count, temperature, information quantity, rate, ratio, dimensionless index, or composite."""
    canonical_symbol: Optional[str] = None
    """Canonical symbol for interoperability (e.g. UCUM-style)."""
    ucum_code: Optional[str] = None
    """Reference to the Unified Code for Units of Measure (UCUM) for this Unit. The canonical UCUM data is held externally per CR-MET-005 section 2.2; this field is a reference handle, not the table."""
    conversion_to_base_factor: Optional[float] = None
    """The multiplicative factor for conversion to the base Unit of the same dimensionality (e.g. minutes -> seconds: 60)."""
    conversion_to_base_offset: Optional[float] = None
    """The additive offset for conversion to the base Unit of the same dimensionality (e.g. Celsius -> Kelvin: -273.15 inverted as +273.15)."""
    composite_dimensions: Optional[list[str]] = None
    """For Units with dimensionality: composite; the dimensional components with their exponents (e.g. velocity = distance / time -> [{dimensionality: length, exponent: 1}, {dimensionality: time, exponent: -1}]). Optional; informational warning (not a conformance failure) when absent for a composite Unit."""
