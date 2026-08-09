#!/usr/bin/env python3
"""Cross-format validator: ensure the rendered SVG matches the
canonical entity-graph.

Reads:
  - viewer/metamodel.svg (the rendered diagram — written by CI)
  - viewer/entity-graph.json (canonical registry)

Extracts entity display_names from the SVG and compares against the
canonical entity-graph. Exits 0 on match, 1 on drift.

PlantUML SVG structure:
  - Each entity is wrapped in `<g id="elem_ALIAS">...</g>` (PUML 1.2024.x)
  - or `<g id="entNNN">...</g>` (PUML 1.2026.x)
  - Layer packages are wrapped in `<g id="cluster_Layer N: ...">`
  - The display name is the first <text> inside each entity block

Extraction strategy: use regex to find entity block START positions
in the document, then iterate through the document capturing text
content between consecutive entity blocks. The text immediately
before each block (or the part of the opening tag after id=) identifies
which entity we're processing.
"""
import sys
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
SVG = BASE / "viewer" / "metamodel.svg"
GRAPH = BASE / "viewer" / "entity-graph.json"


ATTRIBUTE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*:\s*")
NOISE_PATTERNS = [
    re.compile(r"^\(scaffold\)$"),
    re.compile(r"^\(existing\)$"),
    re.compile(r"^\(planned\)$"),
]

# Pattern that matches an entity block START.
ENTITY_START = re.compile(r'<g\s+id="(?:elem_|ent)([^"]*)"')

# Pattern that matches a layer cluster START.
LAYER_START = re.compile(r'<g\s+id="cluster_')


def is_attribute_label(text: str) -> bool:
    return bool(ATTRIBUTE_PATTERN.match(text.strip()))


def is_noise(text: str) -> bool:
    t = text.strip()
    if any(p.match(t) for p in NOISE_PATTERNS):
        return True
    # Layer labels: "Layer 1: Strategic & Investment"
    if t.startswith("Layer ") and ("&amp;" in t or ":" in t):
        return True
    return False


def extract_svg_entity_names():
    """Parse SVG and extract entity display names.

    Strategy: walk the document finding entity block start markers.
    For each, capture text content up to the next entity block start.
    """
    if not SVG.exists():
        return []

    content = SVG.read_text()

    # Find positions of all entity block starts
    starts = [(m.start(), m.group(1)) for m in ENTITY_START.finditer(content)]
    # Find positions of all layer cluster starts (to filter out layer labels)
    cluster_starts = {m.start() for m in LAYER_START.finditer(content)}

    names = []
    for i, (start_pos, alias) in enumerate(starts):
        # Block runs from start_pos to the next entity start (or end of doc)
        end_pos = starts[i+1][0] if i + 1 < len(starts) else len(content)
        block = content[start_pos:end_pos]
        # Extract texts
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', block)
        # Filter
        candidates = [
            t.strip() for t in texts
            if t.strip() and not is_attribute_label(t) and not is_noise(t)
        ]
        if candidates:
            longest = max(candidates, key=len)
            names.append(longest)
    return names


def load_graph_display_names():
    if not GRAPH.exists():
        return []
    with open(GRAPH) as f:
        g = json.load(f)
    return [e["display_name"] for e in g["entities"]]


def normalize(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def main():
    svg_names = extract_svg_entity_names()
    graph_names = load_graph_display_names()

    print(f"SVG entities found:    {len(svg_names)}")
    print(f"Graph entities:        {len(graph_names)}")

    if not svg_names:
        print("\nERROR: SVG has no entities — render may have failed")
        return 1

    svg_norm = {normalize(n) for n in svg_names}
    graph_norm = {normalize(n) for n in graph_names}

    only_in_svg = svg_norm - graph_norm
    only_in_graph = graph_norm - svg_norm

    if only_in_svg:
        print(f"\nERROR: {len(only_in_svg)} entities in SVG but NOT in entity-graph:")
        for n in sorted(only_in_svg):
            print(f"  '{n}'")
    if only_in_graph:
        print(f"\nERROR: {len(only_in_graph)} entities in entity-graph but NOT in SVG:")
        for n in sorted(only_in_graph):
            print(f"  '{n}'")

    if only_in_svg or only_in_graph:
        print(f"\n=== DRIFT DETECTED ===")
        print("Run: python3 .github/scripts/generate_puml.py | plantuml -tsvg")
        print("Then commit viewer/metamodel.svg")
        return 1

    print(f"\n=== ALIGNED ===")
    print(f"All {len(graph_norm)} entity-graph entries are present in the SVG.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
