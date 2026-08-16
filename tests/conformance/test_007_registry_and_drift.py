"""CR-1.11 enforcement: registries in sync with the normative source,
referential integrity, no duplicate authoritative representations."""
import yaml

from conftest import BASE


def test_entity_registry_in_sync(entities, canonical_version):
    reg = yaml.safe_load((BASE / "metamodel" / "registry" / "entities.yaml").read_text())
    assert str(reg["registry_version"]) == canonical_version
    reg_ids = [e["id"] for e in reg["entities"]]
    src_ids = [e["id"] for e in entities]
    assert reg_ids == src_ids, "entity registry out of sync with normative source " \
        "(regenerate registry from metamodel/dea-metamodel.yaml)"


def test_relationship_registry_in_sync(relationships, canonical_version):
    reg = yaml.safe_load((BASE / "metamodel" / "registry" / "relationships.yaml").read_text())
    assert str(reg["registry_version"]) == canonical_version
    reg_ids = [r["id"] for r in reg["relationships"]]
    src_ids = [r["id"] for r in relationships]
    assert reg_ids == src_ids, "relationship registry out of sync with normative source"


def test_manifest_points_at_existing_normative_source(manifest):
    p = BASE / manifest["metamodel"]["normative_source"]["path"]
    assert p.exists(), f"normative source missing: {p}"


def test_layer_and_dimension_refs_resolve(normative):
    layers = {l["id"] for l in normative["layers"]}
    dims = {d["id"] for d in normative["dimensions"]}
    for e in normative["entities"]:
        if e.get("layer"):
            assert e["layer"] in layers, f"{e['id']}: unknown layer {e['layer']}"
        if e.get("dimension"):
            assert e["dimension"] in dims, f"{e['id']}: unknown dimension {e['dimension']}"


def test_legacy_index_deprecated():
    legacy = yaml.safe_load((BASE / "metamodel.yaml").read_text())
    mm = legacy["metamodel"]
    assert mm.get("deprecated") is True and mm.get("superseded_by") == "metamodel/dea-metamodel.yaml", \
        "legacy metamodel.yaml must declare deprecation and point at the normative source"
