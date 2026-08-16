"""Test 001 (CR-1.9): every entity has stable ID, name, definition,
semantic layer (or dimension), and lifecycle status."""
from conftest import ENTITY_ID


def test_entities_have_stable_ids(entities):
    for e in entities:
        assert ENTITY_ID.match(e["id"]), f"entity id {e.get('id')!r} does not match dea:PascalCase"


def test_entity_ids_unique(entities):
    ids = [e["id"] for e in entities]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate entity ids: {dupes}"


def test_entities_have_name_definition_layer_lifecycle(entities):
    layers = {"L1", "L2", "L3", "L4", "L5"}
    for e in entities:
        assert e.get("name"), f"{e['id']}: missing name"
        assert e.get("definition"), f"{e['id']}: missing definition"
        if e.get("abstract"):
            continue  # abstract anchors span all layers
        # CR-4: Core entities are layer-agnostic (CR-3M — layer is a viewpoint,
        # not identity). Profile entities keep their root-model layer/dimension.
        if (e.get("membership") or {}).get("kind") == "core":
            pass
        else:
            assert e.get("layer") in layers or e.get("dimension"), \
                f"{e['id']}: no semantic layer or dimension"
        assert e.get("lifecycle") in {"existing", "scaffold", "proposed", "planned"}, \
            f"{e['id']}: missing/invalid lifecycle status"
