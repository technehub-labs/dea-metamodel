"""Test 002 (CR-1.9): every relationship has stable ID, name, definition,
source type, target type, direction, cardinality."""
from conftest import REL_ID


def test_relationships_have_stable_ids(relationships):
    for r in relationships:
        assert REL_ID.match(r["id"]), f"relationship id {r.get('id')!r} does not match dea:kebab-case"


def test_relationship_ids_unique(relationships):
    ids = [r["id"] for r in relationships]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate relationship ids: {dupes}"


def test_relationships_complete(relationships, entity_ids):
    for r in relationships:
        for field in ("name", "definition", "direction", "cardinality"):
            assert r.get(field), f"{r['id']}: missing {field}"
        assert r.get("source"), f"{r['id']}: missing source type(s)"
        assert r.get("target"), f"{r['id']}: missing target type(s)"
        for sid in r["source"]:
            assert sid in entity_ids, f"{r['id']}: source {sid} not a registered entity"
        for tid in r["target"]:
            assert tid in entity_ids, f"{r['id']}: target {tid} not a registered entity"
