#!/usr/bin/env python3
"""Cross-format validator: ensure the rendered SVG matches the
canonical entity-graph.

Reads:
  - viewer/metamodel.svg (the rendered diagram — written by CI)
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
  each block, the longest <text>...</text> is empirically the display
  name (e.g. "Strategic Objective"). Attribute labels like
  "id : string" or "ecfCoordinates : (Domain, Stage)" are also rendered
  as <text> but are either:
    (a) shorter than the display name, or
    (b) contain " : " — a clear attribute pattern.
  We filter out anything matching the attribute pattern to be defensive.

  We also exclude any text starting with "(scaffold)" or "(existing)"
  status markers that may render as text in some PlantUML versions.
"""
import sys
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
SVG = BASE / "viewer" / "metamodel.svg"
GRAPH = BASE / "viewer" / "entity-graph.json"


# Text that looks like an attribute: "<name> : <type>"
ATTRIBUTE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*:\s*")

# Status markers and other noise to skip
NOISE_PATTERNS = [
    re.compile(r"^\(scaffold\)$"),
    re.compile(r"^\(existing\)$"),
    re.compile(r"^\(planned\)$"),
]


def is_attribute_label(text: str) -> bool:
    """True if text looks like an attribute ('name : type')."""
    return bool(ATTRIBUTE_PATTERN.match(text.strip()))


def is_noise(text: str) -> bool:
    """True if text is a known noise pattern (status markers, etc.)."""
    t = text.strip()
    return any(p.match(t) for p in NOISE_PATTERNS)


def extract_svg_entity_names():
    """Parse SVG and extract entity display names."""
    if not SVG.exists():
        return []

    content = SVG.read_text()

    # Split on entity block boundaries. Each entity <g> is uniquely
    # identified by `class="entity"` (not "cluster" or "link").
    blocks = re.split(r'(?=<g\s+class="entity")', content)

    names = []
    for block in blocks:
        if 'class="entity"' not in block[:200]:
            continue
        # Find all <text>...</text> in this block, in document order
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', block)
        if not texts:
            continue
        # Skip attribute labels and noise; pick the longest remaining
        candidates = [
            t.strip() for t in texts
            if t.strip() and not is_attribute_label(t) and not is_noise(t)
        ]
        if not candidates:
            continue
        # Take the longest — empirically the display name
        longest = max(candidates, key=len)
        if longest:
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
