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
import os
import sys
import urllib.request
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.parent
OUT = BASE / "viewer" / "entity-graph.json"
CROSSWALK = BASE / "metamodel" / "migration" / "relationship-crosswalk.yaml"
REGISTRY = BASE / "metamodel" / "registry" / "relationships.yaml"
MODEL_REPO = "technehub-labs/dea-architecture-framework"

# Ensure the scripts/ directory is on sys.path so the vendored
# cross_repo_consumer package and the catalog_summary_builder helper
# are importable. This mirrors the vendoring strategy used elsewhere
# in dea-metamodel tooling (e.g. .github/scripts/ is invoked as a
# script, not a package).
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

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
    # CR-002 (2I): resolve every edge to canonical relationship IDs via the
    # crosswalk. Unknown labels are a hard failure (R012).
    cw = yaml.safe_load(CROSSWALK.read_text())["crosswalk"]["viewer_label_mappings"]
    cw_by_key = {(c["current"], c["rel_type"]): c for c in cw}
    registry = yaml.safe_load(REGISTRY.read_text())["relationships"]
    reg_by_id = {r["id"]: r for r in registry}
    for r in rels:
        if r["from"] not in valid or r["to"] not in valid:
            print(f"WARNING: skipping relationship with unknown alias: {r}", file=sys.stderr)
            continue
        mapping = cw_by_key.get((r["label"], r["rel_type"]))
        if mapping is None:
            print(f"ERROR: no crosswalk disposition for ({r['label']!r}, {r['rel_type']!r}) — R012",
                  file=sys.stderr)
            return 1
        if mapping["status"] == "split":
            rel_ids = mapping["alternatives"]
        elif mapping["proposed"] is None:
            # review-required with no canonical target yet: carry the label, no rel_id
            rel_ids = []
        else:
            rel_ids = [mapping["proposed"]]
        for rid in rel_ids:
            if rid not in reg_by_id:
                print(f"ERROR: crosswalk target {rid} not in relationship registry", file=sys.stderr)
                return 1
        edge = {
            "from": r["from"],
            "to": r["to"],
            "label": r["label"],
            "rel_type": r["rel_type"],
            "cardinality": r["cardinality"],
            "style": STYLE_BY_REL_TYPE[r["rel_type"]],
            "rel_ids": rel_ids,
        }
        if mapping.get("reverse"):
            edge["canonical_inverse"] = True
        if mapping["status"] != "accepted":
            edge["disposition"] = mapping["status"]
        graph_rels.append(edge)

    # CR-4 Phase 7: stamp core/profile membership onto graph entities so the
    # viewer can render Core and Profile elements independently.
    norm_entities = yaml.safe_load(
        (BASE / "metamodel" / "dea-metamodel.yaml").read_text())["entities"]
    membership_by_legacy = {}
    for e in norm_entities:
        for lid in e.get("legacy_ids", []):
            membership_by_legacy[lid] = e["membership"]
    for ge in graph_entities:
        m = membership_by_legacy.get(ge["entity_id"])
        if m:
            ge["membership"] = m

    graph = {
        "$schema": "https://technehub-labs.github.io/dea-metamodel/viewer/entity-graph.schema.json",
        "metamodel_version": metamodel_version,
        "opendeam_model_repo": MODEL_REPO,
        "opendeam_model_pin": pin or f"v{version}",
        "description": (
            "Entity-to-repo mapping for the interactive metamodel viewer, generated from the "
            "OpenDEAM root model (dea-architecture-framework). Do not edit manually; regenerate "
            "with .github/scripts/generate_entity_graph.py. As of OpenDEAM v0.2.0 (ADR-0002), "
            "measurement is an orthogonal dimension: dimension entities carry `dimension` instead "
            "of `layer`, and relationships carry rel_type + cardinality (style is derived). "
            "As of v0.2.1 (CR-CATALOG-STRUCT-07b), each entity whose catalog_repo matches a "
            "known conformant adopter carries a `catalog_summary` field with the latest "
            "CATALOG.yaml counts (entity_count, canonical, candidates, retired, research_files), "
            "latest_modified date, metamodel_version, and abbreviation; populated at build "
            "time from the cross-repo consumer (vendored at "
            ".github/scripts/cross_repo_consumer/)."
        ),
        "viewer_route": "/metamodel/",
        "viewer_url": "https://technehub-labs.github.io/metamodel/",
        "layers": graph_layers,
        "dimensions": graph_dims,
        "entities": graph_entities,
        "relationships": graph_rels,
        # CR-002 §18: viewer consumes canonical relationship definitions,
        # never its own semantics. Full definitions from the normative source.
        "relationship_definitions": [
            {
                "id": r["id"],
                "name": r["name"],
                "definition": r["definition"],
                "category": r["category"],
                "direction": r["direction"],
                "cardinality": r["cardinality"],
                "inverse": r["inverse"],
                "lifecycle": r["lifecycle"],
            }
            for r in yaml.safe_load(
                (BASE / "metamodel" / "dea-metamodel.yaml").read_text()
            )["relationships"]
            if not r.get("virtual")
        ],
    }

    # CR-CATALOG-STRUCT-07b: embed catalog_summary per entity whose
    # catalog_repo matches a known conformant adopter. The summary is
    # built at generation time from CATALOG.yaml via the cross-repo
    # consumer (vendored at .github/scripts/cross_repo_consumer/). The
    # viewer reads entity-graph.json and surfaces catalog_summary in
    # the entity detail panel.
    try:
        from catalog_summary_builder import (
            attach_catalog_summaries,
            build_catalog_summaries,
        )

        cache_dir_env = os.environ.get("CATALOG_SUMMARY_CACHE")
        offline_env = os.environ.get("CATALOG_SUMMARY_OFFLINE", "").lower() in (
            "1", "true", "yes",
        )
        summaries = build_catalog_summaries(
            cache_dir=Path(cache_dir_env) if cache_dir_env else None,
            offline=offline_env or cache_dir_env is not None,
            timeout_s=15.0,
        )
        attached = attach_catalog_summaries(graph, summaries)
        print(
            f"  catalog_summary: attached to {attached} of "
            f"{len(graph_entities)} entities "
            f"({len(summaries)} adopters fetched)"
        )
    except Exception as exc:  # noqa: BLE001
        # Per the §9 contract the consumer MUST be tolerant: missing
        # catalogs are shown as "no data" in the viewer, not as a hard
        # failure. Log and continue.
        print(f"  catalog_summary: skipped ({type(exc).__name__}: {exc})")

    OUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT} — {len(graph_layers)} layers, {len(graph_dims)} dimensions, "
          f"{len(graph_entities)} entities, {len(graph_rels)} relationships (model v{version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
