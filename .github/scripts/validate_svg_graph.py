#!/usr/bin/env python3
"""Cross-format validator: ensure the rendered SVG matches the
canonical entity-graph.

Reads:
  - viewer/metamodel.svg (the rendered diagram)
  - viewer/entity-graph.json (canonical registry)

Extracts entity display_names from the SVG and compares against the
canonical entity-graph. Exits 0 on match, 1 on drift.

Why this matters:
  The SVG used to be hand-maintained and drifted from the entity-graph
  for over a month (committed July 27; entity-graph evolved Aug 8-9).
  After PR-2 wires SVG-in-repo automation, this validator ensures CI
  catches any future drift where the generator and the graph diverge.

Extraction strategy:
  PlantUML emits one <g class="entity ..."> block per entity. Inside
  each block, the first substantial <text>...</text> is the display
  name (e.g. "Strategic Objective"); subsequent <text> blocks hold
  attribute labels. We extract the longest text content per entity
  block, which empirically is the display name.
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

    PlantUML SVG structure for one entity (simplified):

        <g class="entity" data-qualified-name="..." id="ent0003"
           data-alias="SO" data-layer="L1">
          <title>SO · L1</title>
          <rect .../>
          <ellipse .../>
          <text>Strategic Objective</text>     <-- display name
          <line .../>
          <text>id : string</text>
          <text>name : string</text>
          ...
        </g>

    Strategy: split SVG by `<g class="entity` boundaries, then take the
    longest `<text>` content from each block as the display name.
    """
    if not SVG.exists():
        return []

    content = SVG.read_text()

    # Split on entity block boundaries. Each entity <g> is uniquely
    # identified by `class="entity"` (not "cluster" or "link").
    blocks = re.split(r'(?=<g\s+class="entity")', content)

    names = []
    for block in blocks:
        # Only process if this is a real entity block (has class="entity")
        if 'class="entity"' not in block[:200]:
            continue
        # Find all <text>...</text> in this block
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', block)
        if not texts:
            continue
        # Take the longest text (empirically = display name)
        longest = max(texts, key=len).strip()
        if longest and not longest.startswith("("):
            names.append(longest)
    return names


def load_graph_display_names():
    """Load canonical entity display names from entity-graph.json."""
    if not GRAPH.exists():
        return []
    with open(GRAPH) as f:
        g = json.load(f)
    return [e["display_name"] for e in g["entities"]]


def normalize(s):
    """Normalize for comparison: collapse whitespace, lowercase."""
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
