"""Runtime test suite bootstrap (CR-9CO).

Makes the repo root importable so `import runtime...` works without packaging.
"""
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).parent.parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from runtime.graph import Edge, InMemoryGraphStore, Node  # noqa: E402


@pytest.fixture()
def store():
    return InMemoryGraphStore()


@pytest.fixture()
def two_nodes(store):
    store.create_entity(Node(id="cap.customer-service", type="BusinessCapability",
                             name="Customer Service"))
    store.create_entity(Node(id="app.cs-platform", type="ApplicationComponent",
                             name="CS Platform"))
    return store
