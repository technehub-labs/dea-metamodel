"""Golden graph fixtures (CR-9CN + CR-11AO)."""

from __future__ import annotations

from typing import Dict, Mapping


#: Path of every golden graph fixture, relative to the repository root.
#: CR-11AO adds the interop golden fixtures — basic-enterprise, federated,
#: agentic, scenario — alongside the CR-9CN originals (enterprise, dmm,
#: customer-service-baseline).
GOLDEN_GRAPHS: Mapping[str, str] = {
    "enterprise": "models/golden/enterprise.yaml",
    "dmm": "models/golden/dmm.yaml",
    "customer-service-baseline": "models/scenarios/customer-service-baseline.yaml",
    "basic-enterprise": "models/golden/basic-enterprise.yaml",
    "agentic": "models/golden/agent.yaml",
    "multi-agent": "models/golden/multi-agent.yaml",
    "governed-agent": "models/golden/governed-agent.yaml",
}


#: Expected structural outcomes for each golden graph. An absent key means
#: the test asserts only that the graph loads cleanly and is queryable.
GoldenGraphExpectations = Dict[str, Dict[str, int]]


_EXPECTED: GoldenGraphExpectations = {
    "models/golden/enterprise.yaml": {
        "expected_nodes": 11,
        "expected_edges": 5,
    },
    "models/golden/dmm.yaml": {
        "expected_nodes": 5,
        "expected_edges": 3,
    },
    "models/scenarios/customer-service-baseline.yaml": {
        "expected_nodes": 3,
        "expected_edges": 2,
    },
    "models/golden/basic-enterprise.yaml": {
        "expected_nodes": 7,
        "expected_edges": 5,
    },
}


def golden_graph_assertions(path: str) -> Dict[str, int]:
    """Return the expected structural assertions for a golden graph path."""
    return dict(_EXPECTED.get(path, {}))
