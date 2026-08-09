"""Generate metamodel-puml/metamodel-v2.puml from viewer/entity-graph.json.

This script regenerates the canonical PlantUML source for the metamodel
viewer diagram. Output is deterministic (entities grouped by layer, then
sorted alphabetically within layer).

Run: python3 .github/scripts/generate_puml.py > metamodel-puml/metamodel-v2.puml
"""
import json
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


def camel_to_title(camel: str) -> str:
    """Convert CamelCase to space-separated Title Case.

    'AI/MLModel' -> 'AI/ML Model'
    'BusinessObject' -> 'Business Object'
    'JourneyTouchpoint' -> 'Journey Touchpoint'
    """
    import re
    # Insert space before uppercase letters preceded by lowercase or digit
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', camel)
    # Insert space between consecutive uppercase + lowercase (e.g. AI/ML)
    s = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)
    return s


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

    print("@startuml")
    print("skinparam linetype ortho")
    print("skinparam nodesep 60")
    print("skinparam ranksep 60")
    print("skinparam defaultFontName Arial")
    print("skinparam class {")
    print("    BackgroundColor White")
    print("    BorderColor #2C3E50")
    print("    ArrowColor #2C3E50")
    print("}")
    print()
    print("' --- ENTITY DEFINITIONS (auto-generated from viewer/entity-graph.json) ---")
    print("' Do not edit manually — regenerate with: python3 .github/scripts/generate_puml.py")
    print()

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
                print(f"    ' (scaffold)")
            elif status == "existing":
                print(f"    ' (existing)")
            print(f'    entity "{display}" as {alias} {{')
            print("        + id : string")
            # Show first 2 attributes from schema if known
            print(f'        + name : string')
            print("    }")
        print("}")
        print()

    # Relationship section (placeholder — manual relationships in real diagrams)
    # For now, we don't have a relationship vocabulary in entity-graph.json;
    # relationships are documented in metamodel.yaml + ttl. The PUML viewer
    # currently shows no relationships (it's an entity catalog view).
    print("' --- RELATIONSHIPS ---")
    print("' (The interactive viewer at https://technehub-labs.github.io/metamodel/")
    print("'  renders typed relationships from the relationship-instance graph.")
    print("'  The static SVG snapshot is an entity catalog view only.)")
    print()
    print("@enduml")


if __name__ == "__main__":
    main()
