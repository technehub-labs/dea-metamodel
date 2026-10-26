"""CR-MET-013: canonical Unit records.

The Unit entity type is admitted in the metamodel, but until CR-MET-013 the
only Unit records anywhere were conformance fixtures. The
dea-catalog-metrics seed ingestion (dea-catalog-metrics CR-MET-016) found 21
unit references in real catalog use, none of them resolvable.
metamodel/vocabularies/units.yaml admits the 19 canonical units they resolve
to, with the seed's flat and plural spellings carried as aliases (Q19 ruling:
the ratio form and singular names are canonical).

This suite validates every record against schemas/entities/unit.json, the
Unit.dimensionality controlled vocabulary, id and alias discipline, and the
manifest registration.
"""
import json
import re

import jsonschema
import yaml

from conftest import BASE

UNITS_FILE = BASE / "metamodel" / "vocabularies" / "units.yaml"
ID_PATTERN = re.compile(r"^dea:unit-[a-z0-9][a-z0-9-]*$")


def _units():
    return yaml.safe_load(UNITS_FILE.read_text())["units"]


def _unit_schema():
    return json.loads(
        (BASE / "schemas" / "entities" / "unit.json").read_text()
    )


def _dimensionality_vocabulary():
    voc = yaml.safe_load(
        (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
    )["classifications"]
    return set(voc["Unit.dimensionality"]["values"])


def test_units_file_is_registered_in_the_manifest():
    """A canonical data file the manifest does not register is invisible."""
    manifest = yaml.safe_load((BASE / "metamodel" / "manifest.yaml").read_text())
    vocabularies = manifest["metamodel"].get("vocabularies") or {}
    assert vocabularies.get("units") == "metamodel/vocabularies/units.yaml", (
        "CR-MET-013: metamodel/vocabularies/units.yaml must be registered "
        "under metamodel.vocabularies.units in the manifest"
    )


def test_every_unit_record_validates_against_the_unit_schema():
    schema = _unit_schema()
    for record in _units():
        jsonschema.validate(record, schema)


def test_every_unit_dimensionality_is_in_the_controlled_vocabulary():
    allowed = _dimensionality_vocabulary()
    for record in _units():
        assert record.get("dimensionality") in allowed, (
            f"CR-MET-013: {record['id']} dimensionality "
            f"{record.get('dimensionality')!r} not in the vocabulary"
        )


def test_composite_units_declare_composite_dimensions():
    """CR-MET-005: composite dimensionality MAY declare composite_dimensions.

    This suite makes it MUST for the canonical set: a canonical composite
    unit without its dimensional formula is not reviewable.
    """
    allowed = _dimensionality_vocabulary()
    for record in _units():
        if record.get("dimensionality") == "composite":
            parts = record.get("composite_dimensions") or []
            assert parts, (
                f"CR-MET-013: {record['id']} is composite but declares no "
                f"composite_dimensions"
            )
            for part in parts:
                assert part.get("dimensionality") in allowed, (
                    f"CR-MET-013: {record['id']} composite part "
                    f"{part.get('dimensionality')!r} not in the vocabulary"
                )
                assert isinstance(part.get("exponent"), int)


def test_unit_ids_are_unique_and_well_formed():
    ids = [u["id"] for u in _units()]
    assert len(ids) == len(set(ids)), "CR-MET-013: duplicate unit ids"
    for unit_id in ids:
        assert ID_PATTERN.match(unit_id), (
            f"CR-MET-013: unit id {unit_id!r} must match "
            f"dea:unit-<lowercase-slug>"
        )


def test_aliases_are_unique_and_resolve_to_exactly_one_unit():
    """An alias that resolved to two units would make a legacy reference
    ambiguous; an alias colliding with a canonical id would be a second name
    for a thing that already has one."""
    ids = {u["id"] for u in _units()}
    seen = {}
    for record in _units():
        for alias in record.get("aliases") or []:
            assert alias not in ids, (
                f"CR-MET-013: {record['id']} alias {alias!r} is itself a "
                f"canonical unit id"
            )
            assert alias not in seen, (
                f"CR-MET-013: alias {alias!r} appears on both "
                f"{seen[alias]!r} and {record['id']!r}"
            )
            assert ID_PATTERN.match(alias), (
                f"CR-MET-013: alias {alias!r} must match "
                f"dea:unit-<lowercase-slug>"
            )
            seen[alias] = record["id"]


def test_every_unit_has_a_quantity_kind():
    for record in _units():
        assert (record.get("quantity_kind") or "").strip(), (
            f"CR-MET-013: {record['id']} has no quantity_kind"
        )


def test_the_canonical_set_covers_the_catalogs_unit_references():
    """Every unit_ref the dea-catalog-metrics corpus carries must resolve.

    The two repos both live under dea-work on a development host, and CI
    checks out dea-metamodel for the catalog already. When the catalog
    checkout is absent this test skips rather than guessing.
    """
    import os

    import pytest

    catalog = os.environ.get("DEA_CATALOG_METRICS_ROOT") or (
        BASE.parent / "dea-catalog-metrics"
    )
    catalog = __import__("pathlib").Path(catalog)
    records = sorted(
        (catalog / "entities" / "v1-alpha").glob("dea:metric-*/*.yaml")
    )
    if not records:
        pytest.skip("dea-catalog-metrics checkout not available")
    referenced = set()
    for path in records:
        unit_ref = (yaml.safe_load(path.read_text()) or {}).get("unit_ref")
        if unit_ref:
            referenced.add(unit_ref)
    canonical = {u["id"] for u in _units()}
    aliases = {a for u in _units() for a in (u.get("aliases") or [])}
    unresolved = referenced - canonical - aliases
    assert not unresolved, (
        f"CR-MET-013: catalog references that resolve to no canonical unit "
        f"or alias: {sorted(unresolved)}"
    )
