#!/usr/bin/env python3
"""Cross-format validator: ensure the rendered SVG matches the
canonical entity-graph.

Reads:
  - viewer/metamodel.svg (the rendered diagram — written by CI)
  - viewer/entity-graph.json (canonical registry)

Checks:
  1. Entity names: every entity-graph display_name must appear in the SVG
  2. Entity markers: every <g id="elem_X"> should have class="entity" + data-alias="X"
     (these are injected by .github/scripts/inject_svg_attributes.py
     for Pages-site interactivity)
  3. Relationship edges (informational): warn if the SVG has 0 <g id="link_*">
     (relationship lines should be drawn; if missing, check the PUML)

Exits 0 on match, 1 on drift.
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

# PlantUML 1.2024.x: <g id="elem_ALIAS">...</g>
# PlantUML 1.2026.x: <g id="entNNN">...</g>
# Legacy PlantUML (<=1.2020): <g class="entity" data-alias="X">...</g>
ENTITY_START = re.compile(r'<g\s+(?:id="(?:elem_|ent)([^"]*)"|class="entity")')
LAYER_START = re.compile(r'<g\s+id="cluster_')

# PlantUML 1.2024.x emits relationship groups as <g id="link_*">;
# PlantUML 1.2026.x used <g class="link">. We must chop these out of
# the content before scanning entity text, otherwise the LAST entity
# block's contents include all relationship labels that follow it in
# the file.
LINK_BLOCK_PATTERN = re.compile(r'<g\s+(?:id="link_[^"]*"|class="link")[^>]*>.*?</g>', re.DOTALL)


def is_attribute_label(text: str) -> bool:
    return bool(ATTRIBUTE_PATTERN.match(text.strip()))


def is_noise(text: str) -> bool:
    t = text.strip()
    if any(p.match(t) for p in NOISE_PATTERNS):
        return True
    if t.startswith("Layer ") and ("&amp;" in t or ":" in t):
        return True
    return False


def extract_svg_entity_names():
    """Parse SVG and extract entity display names.

    Strategy: chop out all <g id="link_*"> / <g class="link"> blocks
    before extracting entity text. This prevents relationship labels
    from polluting the last entity block (whose range extends to
    end-of-document).
    """
    if not SVG.exists():
        return []

    content = SVG.read_text()
    scrubbed = LINK_BLOCK_PATTERN.sub("", content)

    starts = [(m.start(), m.group(1)) for m in ENTITY_START.finditer(scrubbed)]

    names = []
    for i, (start_pos, alias) in enumerate(starts):
        end_pos = starts[i+1][0] if i + 1 < len(starts) else len(scrubbed)
        block = scrubbed[start_pos:end_pos]
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', block)
        candidates = [
            t.strip() for t in texts
            if t.strip() and not is_attribute_label(t) and not is_noise(t)
        ]
        if candidates:
            names.append(max(candidates, key=len))
    return names


def check_interactivity_attrs(content):
    """Verify each <g id="elem_X"> has class="entity" + data-alias="X".

    The inject_svg_attributes.py script adds these. If they're missing,
    the Pages-site viewer.js (which uses `g.entity[data-alias]` selectors
    for click/hover) will silently fail to wire interactivity.
    """
    errors = []
    entity_tags = re.findall(r'<g\s+id="(elem_[^"]+)"[^>]*>', content)
    for tag in entity_tags:
        alias = tag[len("elem_"):]
        # Find the full <g id="..." ...> opening tag
        m = re.search(r'<g\s+id="' + re.escape(tag) + r'"([^>]*)>', content)
        if not m:
            continue
        attrs = m.group(1)
        # Check class includes "entity"
        cls_match = re.search(r'class="([^"]*)"', attrs)
        cls = cls_match.group(1).split() if cls_match else []
        if "entity" not in cls:
            errors.append(f"<g id=\"{tag}\"> missing class=\"entity\" (Pages-site interactivity broken)")
        # Check data-alias matches the elem_ alias
        alias_match = re.search(r'data-alias="([^"]*)"', attrs)
        if not alias_match or alias_match.group(1) != alias:
            errors.append(f"<g id=\"{tag}\"> missing or mismatched data-alias attribute")
    return errors


def check_relationship_lines(content):
    """Return total relationship <g> count.

    PlantUML 1.2024.x emits relationship groups as <g id="link_*">
    (no class="link" attribute). PlantUML 1.2026.x used <g class="link">.
    Both formats count.
    """
    new_format = content.count('<g id="link_')
    old_format = content.count('class="link"')
    return new_format + old_format


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
    content = SVG.read_text() if SVG.exists() else ""

    print(f"SVG entities found:    {len(svg_names)}")
    print(f"Graph entities:        {len(graph_names)}")
    print(f"SVG relationship lines: {check_relationship_lines(content)}")
    print()

    errors = []

    if not svg_names:
        print("\nERROR: SVG has no entities — render may have failed")
        return 1

    # Check 1: entity name alignment
    svg_norm = {normalize(n) for n in svg_names}
    graph_norm = {normalize(n) for n in graph_names}
    only_in_svg = svg_norm - graph_norm
    only_in_graph = graph_norm - svg_norm
    if only_in_svg:
        errors.append(f"{len(only_in_svg)} entities in SVG but NOT in entity-graph")
    if only_in_graph:
        errors.append(f"{len(only_in_graph)} entities in entity-graph but NOT in SVG")

    # Check 2: interactivity attributes
    attr_errors = check_interactivity_attrs(content)
    if attr_errors:
        errors.extend(attr_errors)

    if errors:
        print(f"\n=== {len(errors)} ERROR(S) ===")
        for e in errors:
            print(f"  ✗ {e}")
        # Print sample attribute errors (cap to 5)
        for e in attr_errors[:5]:
            print(f"  - {e}")
        print(f"\n=== DRIFT DETECTED ===")
        print("Run: python3 .github/scripts/generate_puml.py | plantuml -tsvg")
        print("Then: python3 .github/scripts/inject_svg_attributes.py viewer/metamodel.svg")
        return 1

    # Check 3: relationship lines (informational only)
    rel_count = check_relationship_lines(content)
    if rel_count == 0:
        print("⚠ WARNING: SVG has 0 relationship lines. Check that the PUML")
        print("  includes typed relationships (e.g. `SO -- II : \"drives\"`).")
        print()
        # Don't fail — just warn
    elif rel_count > 0:
        print(f"✓ SVG has {rel_count} relationship lines")

    print(f"\n=== ALIGNED ===")
    print(f"All {len(graph_norm)} entity-graph entries are present in the SVG.")
    print(f"All {len(svg_names)} entity markers have class=\"entity\" + data-alias.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
