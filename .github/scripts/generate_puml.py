"""Generate metamodel-puml/metamodel-v2.puml from viewer/entity-graph.json.

This script regenerates the canonical PlantUML source for the metamodel
viewer diagram. Output is deterministic (entities grouped by layer, then
sorted alphabetically within layer), with skinparam styling for the
dark theme and a curated set of typed relationship edges.

Run: python3 .github/scripts/generate_puml.py > metamodel-puml/metamodel-v2.puml
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
GRAPH = BASE / "viewer" / "entity-graph.json"

# Layer definitions (number, label, color)
LAYER_DEFS = {
    "L1": (1, "Layer 1: Strategic & Investment", "#E8F8F5"),
    "L2": (2, "Layer 2: Business Operating Model", "#FEF9E7"),
    "L3": (3, "Layer 3: Digital & Data", "#FDEDEC"),
    "L4": (4, "Layer 4: Technical & Integration", "#E8DAEF"),
    "L5": (5, "Layer 5: Measurement & Governance", "#FADBD8"),
}


# Curated relationship set — matches the OLD viewer.js RELATIONSHIPS array
# and viewer.html legend. Each entry is (from_alias, to_alias, label, style)
# where style is 'solid' or 'dashed'. Aliases must match class_alias in
# entity-graph.json. Adding a relationship here requires updating
# technehub-labs.github.io/metamodel/viewer.js's RELATIONSHIPS array too
# (the static SVG relationship lines are decorative — the JS overlay
# draws the same edges on top of the entity cards for hover/select
# interactivity).
RELATIONSHIPS = [
    # Layer 1 & 2
    ("SO",   "II",  "drives",                   "solid"),
    ("II",   "CAP", "funds",                    "solid"),
    ("VS",   "CAP", "traverses",                "solid"),
    ("VS",   "JT",  "experienced via",          "solid"),
    ("CAP",  "BP",  "implemented by",           "solid"),
    ("CAP",  "OU",  "owned by",                 "solid"),
    ("CAP",  "BO",  "produces / consumes",      "solid"),
    ("SH",   "BP",  "served by",                "dashed"),
    ("AC",   "BP",  "performs",                 "solid"),
    # Layer 2 & 3 (Digital Integration)
    ("JT",   "DI",  "authenticates",            "solid"),
    ("DI",   "DE",  "represented by",           "solid"),
    ("BP",   "SF",  "automated by",             "solid"),
    ("BO",   "DE",  "digitized as",             "solid"),
    ("OU",   "BO",  "custodian of",             "dashed"),
    ("BS",   "BO",  "exposes",                  "solid"),
    # Layer 3 Internal (Intelligence & Data)
    ("DE",   "IC",  "classified by",            "dashed"),
    ("DE",   "DP",  "curated into",             "dashed"),
    ("SF",   "EVT", "publishes / subscribes",   "solid"),
    ("EVT",  "DE",  "carries payload of",       "dashed"),
    ("DP",   "API", "exposed via",              "solid"),
    ("AIM",  "DP",  "trained on",               "solid"),
    ("AIM",  "SF",  "enhances / automates",     "solid"),
    # Layer 4 (Technology Execution)
    ("SF",   "APC", "hosted by",                "solid"),
    ("APC",  "PS",  "deployed on",              "dashed"),
    ("SF",   "API", "exposed via",              "solid"),
    ("API",  "DE",  "serves / exchanges",       "dashed"),
    ("TEC",  "APC", "implements",               "solid"),
    # Measurement (Cross-cutting)
    ("SO",   "MTR", "measured by",              "dashed"),
    ("CAP",  "MTR", "evaluated by",             "dashed"),
    ("SF",   "MTR", "evaluated by",             "dashed"),
]


def main():
    with open(GRAPH) as f:
        g = json.load(f)

    entities = g["entities"]

    # Group by layer
    by_layer = {}
    for e in entities:
        layer = e["layer"]
        by_layer.setdefault(layer, []).append(e)
    for layer in by_layer:
        by_layer[layer].sort(key=lambda e: e["class_alias"])

    # ─── Header ───
    print("@startuml")
    print("!theme plain")
    print("skinparam linetype ortho")
    print("skinparam nodesep 60")
    print("skinparam ranksep 60")
    print("skinparam defaultFontName Arial")
    print("skinparam class {")
    print("    BackgroundColor White")
    print("    BorderColor #2C3E50")
    print("    ArrowColor #2C3E50")
    print("}")
    # Dark-theme cluster fills matching the previous (manually-uploaded)
    # SVG. PlantUML 1.2026.x used dark defaults; 1.2024.x uses light
    # defaults — explicit overrides restore the visual continuity.
    print("skinparam package {")
    print("    BackgroundColor #0d2620")
    print("    FontColor #e6edf3")
    print("    BorderColor #e6edf3")
    print("}")
    print("skinparam rectangle {")
    print("    BackgroundColor #0d1117")
    print("    FontColor #e6edf3")
    print("    BorderColor #2dd4bf")
    print("}")
    print()
    print("' --- ENTITY DEFINITIONS (auto-generated from viewer/entity-graph.json) ---")
    print("' Do not edit manually — regenerate with: python3 .github/scripts/generate_puml.py")
    print()

    # ─── Layer packages with entities ───
    valid_aliases = {e["class_alias"] for e in entities}
    for layer_key in ("L1", "L2", "L3", "L4", "L5"):
        if layer_key not in by_layer:
            continue
        num, label, color = LAYER_DEFS[layer_key]
        print(f'package "{label}" {color} {{')
        for e in by_layer[layer_key]:
            alias = e["class_alias"]
            display = e["display_name"]
            status = e.get("status", "")
            if status == "scaffold":
                print("    ' (scaffold)")
            elif status == "existing":
                print("    ' (existing)")
            print(f'    entity "{display}" as {alias} {{')
            print("        + id : string")
            print("        + name : string")
            print("    }")
        print("}")
        print()

    # ─── Typed relationships ───
    print("' --- RELATIONSHIPS (curated set; sync with viewer.js RELATIONSHIPS) ---")
    valid_count = 0
    for from_alias, to_alias, label, style in RELATIONSHIPS:
        if from_alias not in valid_aliases:
            print(f"' WARNING: RELATIONSHIPS contains unknown alias '{from_alias}' — skipping")
            continue
        if to_alias not in valid_aliases:
            print(f"' WARNING: RELATIONSHIPS contains unknown alias '{to_alias}' — skipping")
            continue
        edge = ".." if style == "dashed" else "--"
        print(f'{from_alias} {edge} {to_alias} : "{label}"')
        valid_count += 1
    print()
    print(f"' Generated {valid_count} relationship edges")
    print()
    print("@enduml")


if __name__ == "__main__":
    main()
