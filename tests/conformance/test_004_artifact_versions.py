"""Test 004 (CR-1.9): every generated artifact declares the canonical
metamodel version."""
import glob
import json
import re

from conftest import BASE


def test_json_schemas_declare_version(canonical_version):
    paths = sorted(glob.glob(str(BASE / "schemas" / "entities" / "*.json"))
                   + glob.glob(str(BASE / "schemas" / "relationships" / "*.json")))
    assert paths, "no schema files found"
    missing = []
    for p in paths:
        d = json.loads(open(p).read())
        if d.get("metamodel_version") != canonical_version:
            missing.append(p.split("schemas/")[1])
    assert not missing, f"schemas without metamodel_version={canonical_version}: {missing}"


def test_typescript_declares_version(canonical_version):
    ts = (BASE / "typescript" / "src" / "interfaces.ts").read_text()
    assert f'METAMODEL_VERSION = \'{canonical_version}\'' in ts, \
        "typescript/src/interfaces.ts missing/stale METAMODEL_VERSION"


def test_pydantic_declares_version(canonical_version):
    init = (BASE / "pydantic" / "__init__.py").read_text()
    assert f'__metamodel_version__ = "{canonical_version}"' in init, \
        "pydantic/__init__.py missing/stale __metamodel_version__ (regenerate: generate_pydantic.py)"


def test_ttl_declares_version(canonical_version):
    ttl = (BASE / "ttl" / "dea-metamodel-ontology.ttl").read_text()
    assert f'owl:versionInfo "{canonical_version}"' in ttl, \
        "ttl/dea-metamodel-ontology.ttl missing/stale owl:versionInfo"


def test_version_file_matches_manifest(canonical_version):
    v = (BASE / "VERSION").read_text().strip()
    assert v == canonical_version, f"VERSION file {v} != manifest {canonical_version}"


def test_normative_source_version_matches_manifest(normative, canonical_version):
    v = str(normative["metamodel"]["version"])
    assert v == canonical_version, f"normative source {v} != manifest {canonical_version}"
