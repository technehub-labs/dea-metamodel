#!/usr/bin/env python3
"""Regenerate metamodel/registry/ from the normative source (CR-1.11 drift enforcement).

The registries are derived artifacts: entity inventory (id, classification,
membership) and relationship inventory (id, endpoints, inverse). Semantics live
only in metamodel/dea-metamodel.yaml — this script must never add, drop or
reorder content, only project it.

Run: python3 .github/scripts/generate_registry.py
"""
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.parent
NORMATIVE = BASE / "metamodel" / "dea-metamodel.yaml"
MANIFEST = BASE / "metamodel" / "manifest.yaml"
OUT_ENT = BASE / "metamodel" / "registry" / "entities.yaml"
OUT_REL = BASE / "metamodel" / "registry" / "relationships.yaml"

ENT_HEADER = ("# Entity Registry (CR-1.5/CR-4) — authoritative inventory, "
              "generated from metamodel/dea-metamodel.yaml\n")
REL_HEADER = ("# Relationship Registry — authoritative inventory, generated from metamodel/dea-metamodel.yaml\n"
              "# CR-002: single canonical relationship ontology (categories A-K, CR-2 section 4)\n")


def project_entity(e):
    return {
        "id": e["id"],
        "name": e["name"],
        "layer": e.get("layer"),
        "dimension": e.get("dimension"),
        "abstract": e.get("abstract", False),
        "status": e.get("status"),
        "lifecycle": e.get("lifecycle"),
        "catalog_repo": e.get("catalog_repo"),
        "membership": e.get("membership"),
    }


def project_relationship(r):
    return {
        "id": r["id"],
        "name": r["name"],
        "category": r["category"],
        "source": r["source"]["types"],
        "target": r["target"]["types"],
        "inverse": r.get("inverse"),
        "status": r.get("status"),
        "lifecycle": r.get("lifecycle"),
    }


def dump(doc):
    return yaml.dump(doc, sort_keys=False, allow_unicode=True, width=120)


def main():
    norm = yaml.safe_load(NORMATIVE.read_text())
    version = yaml.safe_load(MANIFEST.read_text())["metamodel"]["version"]

    ent_doc = {"registry_version": version,
               "entities": [project_entity(e) for e in norm["entities"]]}
    rel_doc = {"registry_version": version,
               "relationships": [project_relationship(r) for r in norm["relationships"]]}

    OUT_ENT.write_text(ENT_HEADER + dump(ent_doc))
    OUT_REL.write_text(REL_HEADER + dump(rel_doc))
    print(f"registry regenerated at version {version}: "
          f"{len(ent_doc['entities'])} entities, {len(rel_doc['relationships'])} relationships")


if __name__ == "__main__":
    sys.exit(main())
