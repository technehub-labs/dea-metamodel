#!/usr/bin/env python3
"""Generate viewer/entity-graph.json from the OpenDEAM root model.

The OpenDEAM model (technehub-labs/dea-architecture-framework,
model/opendeam-model.yaml, pinned by tag) is the single source of truth.
This script derives the T1 viewer graph deterministically from it:

  - layers[]        <- model architecture.layers (v0.2.0: L1-L5)
  - dimensions[]    <- model architecture.orthogonal_allocators
                       (ADR-0002 D1: measurement is a dimension, not a layer)
  - entities[]      <- model allocation.entities; dimension entities (no
                       home layer, e.g. MTR) carry `dimension` instead of
                       `layer`/`layer_name`/`building_block`
  - relationships[] <- model relationships, with `style` derived from
                       `rel_type` (style is deprecated as of v0.2.0 —
                       viewers should render from rel_type)

Usage:
  python3 .github/scripts/generate_entity_graph.py --model /path/to/opendeam-model.yaml
  python3 .github/scripts/generate_entity_graph.py --model-tag v0.2.0   # fetches from GitHub

Output: viewer/entity-graph.json (overwritten). Deterministic: entities
sorted by (layer, class_alias), relationships in model order.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.parent
OUT = BASE / "viewer" / "entity-graph.json"
MODEL_REPO = "technehub-labs/dea-architecture-framework"

# style is DEPRECATED (ADR-0002 D4) — derived from rel_type for T3
# back-compat only. Viewers should render from rel_type directly.
STYLE_BY_REL_TYPE = {
    "realization": "solid",
    "composition": "solid",
    "aggregation": "solid",
    "flow": "solid",
    "dependency": "dashed",
    "governance": "dashed",
    "association": "dashed",
}

# Dimension entity -> orthogonal allocator id. The OpenDEAM model declares
# the allocators but not which dimension entity backs each, so the mapping
# is maintained here (v0.4.0: CON joins MTR — ADR-0004 D2).
DIMENSION_ALLOCATOR = {
    "MTR": "measurement-dimension",
    "CON": "semantic-dimension",
}


def darken(hex_color: str, factor: float = 0.45, bg: str = "#0d1117") -> str:
    """Blend a bright layer color toward the dark theme background.

    Deterministic dark fill for PUML packages — replaces the hardcoded
    dark_palette that drifted from the model's authoritative colors.
    """
    c = hex_color.lstrip("#")
    b = bg.lstrip("#")
    rgb = tuple(round(int(c[i:i+2], 16) * factor + int(b[i:i+2], 16) * (1 - factor)) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def main() -> int:
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--model", type=Path, help="Path to opendeam-model.yaml")
    src.add_argument("--model-tag", help="Git tag of dea-architecture-framework to fetch the model from")
    args = ap.parse_args()

    if args.model:
        model = yaml.safe_load(args.model.read_text())
        pin = None
    else:
        url = f"https://raw.githubusercontent.com/{MODEL_REPO}/{args.model_tag}/model/opendeam-model.yaml"
        with urllib.request.urlopen(url, timeout=30) as r:
            model = yaml.safe_load(r.read().decode())
        pin = args.model_tag

    version = model["model"]["version"]
    # CR-001: metamodel_version is THIS repo's normative metamodel version
    # (metamodel/manifest.yaml); the upstream root-model version is tracked
    # separately via opendeam_model_pin.
    manifest_path = Path(__file__).parent.parent.parent / "metamodel" / "manifest.yaml"
    metamodel_version = yaml.safe_load(manifest_path.read_text())["metamodel"]["version"]
    layers = model["architecture"]["layers"]
    allocators = model["architecture"].get("orthogonal_allocators", [])
    entities = model["allocation"]["entities"]
    rels = model["relationships"]

    layer_by_id = {l["id"]: l for l in layers}
    bb_name = {bb["id"]: bb["name"] for l in layers for bb in l["building_blocks"]}

    graph_layers = [
        {
            "id": l["id"],
            "name": l["name"],
            "qualifier": l["qualifier"],
            "color": l["color"],
            "dark_color": darken(l["color"]),
        }
        for l in layers
    ]
    graph_dims = [
        {"id": a["id"], "name": a["name"], "kind": a["kind"]}
        for a in allocators
    ]

    def sort_key(e):
        return (e.get("layer", "L99"), e["class_alias"])

    graph_entities = []
    for e in sorted(entities, key=sort_key):
        g = {
            "entity_id": e["entity_id"],
            "class_alias": e["class_alias"],
            "display_name": e["display_name"],
            "catalog_repo": e.get("catalog_repo"),
            "repo_url": f"https://github.com/technehub-labs/{e['catalog_repo']}" if e.get("catalog_repo") else None,
            "status": e["status"],
            "description": e.get("description", ""),
        }
        if "layer" in e:
            l = layer_by_id[e["layer"]]
            g.update({
                "layer": e["layer"],
                "layer_name": l["name"],
                "building_block": e["building_block"],
                "building_block_name": bb_name[e["building_block"]],
                "color": l["color"],
            })
        else:
            # OpenDEAM v0.4.0 (ADR-0004): two dimension entities — MTR backs
            # measurement-dimension, CON backs semantic-dimension. The model
            # does not declare the entity->allocator link, so it is kept here;
            # unknown dimension entities warn rather than silently mislabel.
            alloc = DIMENSION_ALLOCATOR.get(e["class_alias"])
            if not alloc:
                print(
                    f"WARNING: dimension entity {e['class_alias']} has no "
                    f"allocator mapping in DIMENSION_ALLOCATOR",
                    file=sys.stderr,
                )
                alloc = "unknown"
            g["dimension"] = alloc
            g["color"] = "#9CA3AF"
        for opt in ("abstract", "specializes", "realized_in_layers", "discriminator",
                    "ecf_coordinates", "measured_by", "scope_layers",
                    "governed_by", "defined_by", "parent_concept",
                    "enforcement", "migration_note",
                    "entity_role", "completeness_contract"):
            if opt in e:
                g[opt] = e[opt]
        graph_entities.append(g)

    valid = {e["class_alias"] for e in entities}
    graph_rels = []
    for r in rels:
        if r["from"] not in valid or r["to"] not in valid:
            print(f"WARNING: skipping relationship with unknown alias: {r}", file=sys.stderr)
            continue
        graph_rels.append({
            "from": r["from"],
            "to": r["to"],
            "label": r["label"],
            "rel_type": r["rel_type"],
            "cardinality": r["cardinality"],
            "style": STYLE_BY_REL_TYPE[r["rel_type"]],
        })

    graph = {
        "$schema": "https://technehub-labs.github.io/dea-metamodel/viewer/entity-graph.schema.json",
        "metamodel_version": metamodel_version,
        "opendeam_model_repo": MODEL_REPO,
        "opendeam_model_pin": pin or f"v{version}",
        "description": (
            "Entity-to-repo mapping for the interactive metamodel viewer, generated from the "
            "OpenDEAM root model (dea-architecture-framework). Do not edit manually — regenerate "
            "with .github/scripts/generate_entity_graph.py. As of OpenDEAM v0.2.0 (ADR-0002), "
            "measurement is an orthogonal dimension: dimension entities carry `dimension` instead "
            "of `layer`, and relationships carry rel_type + cardinality (style is derived)."
        ),
        "viewer_route": "/metamodel/",
        "viewer_url": "https://technehub-labs.github.io/metamodel/",
        "layers": graph_layers,
        "dimensions": graph_dims,
        "entities": graph_entities,
        "relationships": graph_rels,
    }

    OUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT} — {len(graph_layers)} layers, {len(graph_dims)} dimensions, "
          f"{len(graph_entities)} entities, {len(graph_rels)} relationships (model v{version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
