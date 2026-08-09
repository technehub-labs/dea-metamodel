#!/usr/bin/env python3
"""Cross-format validator: ensure the rendered SVG matches the
canonical entity-graph.

Reads:
  - viewer/metamodel.svg (the rendered diagram)
  - viewer/entity-graph.json (canonical registry)

Extracts entity class names from the SVG and compares against the
canonical entity-graph display_names. Exits 0 on match, 1 on drift.

Why this matters:
  The SVG used to be hand-maintained and drifted from the entity-graph
  for over a month (committed July 27; entity-graph evolved Aug 8-9).
  After PR-2 wires SVG-in-repo automation, this validator ensures CI
  catches any future drift where the generator and the graph diverge.

Extraction strategy:
  PlantUML emits SVG <g> elements with class="entity ..." wrapping each
  entity box. The entity display_name appears as text inside the box.
  We extract those text values, normalise (strip whitespace, collapse
  hyphens), and match against entity-graph display_names.
"""
import sys
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
SVG = BASE / "viewer" / "metamodel.svg"
GRAPH = BASE / "viewer" / "entity-graph.json"


def extract_svg_entity_names():
    """Parse SVG and extract entity display names.

    PlantUML SVG structure for an entity:
        <g class="entity ..." >
            <text>Display Name</text>
            ...
        </g>

    We extract all text inside <g class="entity ..."> blocks.
    """
    if not SVG.exists():
        return []

    content = SVG.read_text()

    # PlantUML emits class="entity" on a <g> wrapper. Find each one and
    # extract the first <text>...</text> inside.
    pattern = re.compile(
        r'<g\s+class="entity[^"]*"[^>]*>\s*<text[^>]*>([^<]+)</text>',
        re.DOTALL,
    )
    names = []
    for m in pattern.finditer(content):
        name = m.group(1).strip()
        # Skip any noise like "(scaffold)" status markers (those are
        # rendered as separate text elements, not the first one inside
        # the entity box, but be defensive).
        if name and not name.startswith("("):
            names.append(name)
    return names


def load_graph_display_names():
    """Load canonical entity display names from entity-graph.json."""
    if not GRAPH.exists():
        return []
    with open(GRAPH) as f:
        g = json.load(f)
    return [e["display_name"] for e in g["entities"]]


def normalize(s):
    """Normalize for comparison: strip whitespace, lowercase, drop punctuation."""
    return re.sub(r"\s+", " ", s.strip().lower())


def main():
    svg_names = extract_svg_entity_names()
    graph_names = load_graph_display_names()

    print(f"SVG entities found: {len(svg_names)}")
    print(f"Graph entities:      {len(graph_names)}")

    if not svg_names:
        print("ERROR: SVG has no entities — render may have failed")
        return 1

    svg_norm = {normalize(n) for n in svg_names}
    graph_norm = {normalize(n) for n in graph_names}

    only_in_svg = svg_norm - graph_norm
    only_in_graph = graph_norm - svg_norm

    if only_in_svg:
        print(f"\nERROR: {len(only_in_svg)} entities in SVG but NOT in entity-graph:")
        for n in sorted(only_in_svg):
            print(f"  {n}")
    if only_in_graph:
        print(f"\nERROR: {len(only_in_graph)} entities in entity-graph but NOT in SVG:")
        for n in sorted(only_in_graph):
            print(f"  {n}")

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
