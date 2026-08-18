"""CR-9CQ/CR-9CR — the two foundational runtime security principles.

1. No silent inference: the runtime never converts inferred knowledge into
   authoritative fact without an explicit state transition. In the foundation
   milestone this means: inference does not exist yet, and it fails loudly.
2. No autonomous mutation by default: the foundation exposes no agent write
   path at all; loaded graphs contain exactly what the model declared.
"""
import pytest

from runtime.graph import InMemoryGraphStore, InferenceUnavailable
from runtime.model import load_model

from conftest import BASE


def test_infer_fails_loudly():
    store = InMemoryGraphStore()
    with pytest.raises(InferenceUnavailable, match="CR-9.3"):
        store.infer()


def test_loaded_graph_contains_only_declared_edges():
    """No derived/inferred edges are materialized during load (CR-9CQ)."""
    store = InMemoryGraphStore()
    import yaml
    for path in sorted((BASE / "models" / "golden").glob("*.yaml")):
        store = InMemoryGraphStore()
        load_model(path, store)
        doc = yaml.safe_load(path.read_text())
        declared = sum(len(el.get("relationships", [])) for el in doc["elements"])
        assert store.stats()["edges"] == declared, \
            f"{path.name}: graph contains edges the model did not declare"
