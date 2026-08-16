"""Shared loaders for the conformance suite (CR-1.9)."""
import json
import re
from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).parent.parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
ENTITY_ID = re.compile(r"^dea:[A-Z][A-Za-z0-9]*$")
REL_ID = re.compile(r"^dea:[a-z][a-z0-9-]*$")


@pytest.fixture(scope="session")
def manifest():
    return yaml.safe_load((BASE / "metamodel" / "manifest.yaml").read_text())


@pytest.fixture(scope="session")
def normative():
    return yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())


@pytest.fixture(scope="session")
def canonical_version(manifest):
    v = manifest["metamodel"]["version"]
    assert SEMVER.match(v), f"manifest version {v!r} is not semver"
    return v


@pytest.fixture(scope="session")
def entities(normative):
    return normative["entities"]


@pytest.fixture(scope="session")
def relationships(normative):
    return normative["relationships"]


@pytest.fixture(scope="session")
def entity_ids(entities):
    return {e["id"] for e in entities}
