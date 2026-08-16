"""Test 005 (CR-1.9): viewer graph version equals the source metamodel version."""
import json

from conftest import BASE


def test_viewer_graph_version_equals_metamodel(canonical_version):
    g = json.loads((BASE / "viewer" / "entity-graph.json").read_text())
    assert g.get("metamodel_version") == canonical_version, \
        f"viewer graph {g.get('metamodel_version')} != canonical {canonical_version} " \
        "(regenerate: generate_entity_graph.py)"
