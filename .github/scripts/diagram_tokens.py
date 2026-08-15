#!/usr/bin/env python3
"""Canonical design-token loader for the metamodel diagram pipeline.

Single entry point for every design value used when regenerating
viewer/metamodel.svg. Reads:

  - viewer/diagram-tokens.json  (locked design decisions: canvas, entity,
    relationship label, package, dimension tokens)
  - viewer/entity-graph.json    (per-layer colors cascade from the OpenDEAM
    root model: layers[].color = accent, layers[].dark_color = package fill)

Design principle (locked 2026-08-15, variant "C2"): no canvas — transparent
SVG background inheriting the page; dark layer-colored packages; small italic
relationship labels with no outline; light-grey attribute text on dark entity
fills. See viewer/diagram-tokens.json for the full token set and rationale.

Used by generate_puml.py and inject_svg_attributes.py. Do not hardcode design
values in those scripts — extend the token file instead.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
TOKENS_PATH = BASE / "viewer" / "diagram-tokens.json"
GRAPH_PATH = BASE / "viewer" / "entity-graph.json"

# Layer id used for dimension entities (no home layer) in alias maps.
DIM = "DIM"


def load_tokens() -> dict:
    return json.loads(TOKENS_PATH.read_text())


def load_graph() -> dict:
    return json.loads(GRAPH_PATH.read_text())


def layer_palette(tokens: dict, graph: dict) -> dict:
    """{layer_id: {"accent": ..., "dark": ...}} plus DIM entry from tokens.

    Accent/dark colors cascade from the OpenDEAM root model via the graph —
    new layers added to the model flow through with no token-file change.
    """
    pal = {
        l["id"]: {"accent": l["color"], "dark": l["dark_color"]}
        for l in graph.get("layers", [])
    }
    pal[DIM] = {
        "accent": tokens["dimension"]["accent"],
        "dark": tokens["dimension"]["fill"],
    }
    return pal


def alias_to_layer(graph: dict) -> dict:
    """{class_alias: layer_id | DIM} for every entity in the graph."""
    return {e["class_alias"]: e.get("layer", DIM) for e in graph.get("entities", [])}


def blend(fg: str, bg: str, alpha: float) -> str:
    """Deterministic hex blend: fg at alpha over bg. Used for the stereotype
    badge tint (layer accent blended into the entity fill)."""
    f = fg.lstrip("#")
    b = bg.lstrip("#")
    rgb = tuple(
        round(int(f[i:i + 2], 16) * alpha + int(b[i:i + 2], 16) * (1 - alpha))
        for i in (0, 2, 4)
    )
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def stereotype_fill(accent: str, tokens: dict) -> str:
    """Badge tint for one layer accent, per the entity token spec."""
    return blend(accent, tokens["entity"]["fill"], tokens["entity"]["stereotype_blend_alpha"])
