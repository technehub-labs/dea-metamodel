"""Test 002 (CR-1.9, extended CR-2): every relationship has stable ID, name,
definition, source type, target type, direction, cardinality — in the CR-2
canonical structure (section 3)."""
from conftest import REL_ID

CARDINALITY = {"0..1", "1", "0..*", "1..*"}


def test_relationships_have_stable_ids(relationships):
    for r in relationships:
        assert REL_ID.match(r["id"]), f"relationship id {r.get('id')!r} does not match dea:kebab-case"


def test_relationship_ids_unique(relationships):
    ids = [r["id"] for r in relationships]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate relationship ids: {dupes}"


def test_relationships_complete(relationships, entity_ids):
    for r in relationships:
        for field in ("name", "definition", "direction", "cardinality", "category"):
            assert r.get(field), f"{r['id']}: missing {field}"
        src = r.get("source", {}).get("types", [])
        tgt = r.get("target", {}).get("types", [])
        assert src, f"{r['id']}: missing source types"
        assert tgt, f"{r['id']}: missing target types"
        for sid in src:
            assert sid in entity_ids, f"{r['id']}: source {sid} not a registered entity"
        for tid in tgt:
            assert tid in entity_ids, f"{r['id']}: target {tid} not a registered entity"
        assert r["cardinality"].get("source") in CARDINALITY, f"{r['id']}: bad source cardinality"
        assert r["cardinality"].get("target") in CARDINALITY, f"{r['id']}: bad target cardinality"
        assert r["direction"] == "source-to-target", f"{r['id']}: direction must be canonical"
