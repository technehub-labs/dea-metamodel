"""Generate metamodel-puml/metamodel-v2.puml from viewer/entity-graph.json.

Regenerates the canonical PlantUML source for the metamodel viewer diagram.
As of OpenDEAM v0.2.0 (ADR-0002) everything is derived from the graph —
which is itself generated from the OpenDEAM root model by
generate_entity_graph.py. No hardcoded layer definitions or relationship
lists live here anymore.

  - Layer packages  <- graph.layers (id, name, dark_color)
  - Dimension block <- graph.dimensions + dimension entities (e.g. MTR)
  - Edges           <- graph.relationships (style derived from rel_type)
  - Inheritance     <- entity.specializes (ADR-0002 D3), emitted as --|>

Output is deterministic: layers in graph order, entities alphabetically
by class_alias within each layer.

Run: python3 .github/scripts/generate_puml.py > metamodel-puml/metamodel-v2.puml
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_tokens import load_tokens

BASE = Path(__file__).parent.parent.parent
GRAPH = BASE / "viewer" / "entity-graph.json"
TOKENS = load_tokens()


def main():
    with open(GRAPH) as f:
        g = json.load(f)

    entities = g["entities"]
    layers = g["layers"]
    relationships = g.get("relationships", [])
    rel_tok = TOKENS["relationship_label"]

    by_layer = {}
    dimension_entities = []
    for e in entities:
        if "layer" in e:
            by_layer.setdefault(e["layer"], []).append(e)
        else:
            dimension_entities.append(e)
    for layer in by_layer:
        by_layer[layer].sort(key=lambda e: e["class_alias"])

    # ─── Header ───
    print("@startuml")
    print("!theme plain")
    print("skinparam linetype ortho")
    print("skinparam nodesep 80")
    print("skinparam ranksep 90")
    print("skinparam dpi 96")
    print("skinparam maxMessageSize 200")
    print("skinparam defaultFontName Arial")
    # Canvas: transparent — the diagram inherits the page background (C2
    # design token canvas.background). inject_svg_attributes.py re-enforces
    # this on the rendered SVG in case a PlantUML version ignores it.
    print(f'skinparam backgroundColor {TOKENS["canvas"]["background"]}')
    # ELK layout engine produces more balanced (closer to square) layouts
    # than the default GraphViz dot, especially for many-cluster diagrams.
    print("!pragma layout elk")
    print("skinparam class {")
    print(f'    BackgroundColor {TOKENS["entity"]["fill"]}')
    print(f'    FontColor       {TOKENS["entity"]["name_text"]}')
    print("    BorderColor     #2dd4bf")
    print("    ArrowColor      #2dd4bf")
    print("}")
    print("skinparam arrow {")
    print("    Color     #2dd4bf")
    print(f'    FontColor {rel_tok["text"]}')
    print(f'    FontStyle {rel_tok["font_style"]}')
    print(f'    FontSize  {rel_tok["font_size"]}')
    print("}")
    print()
    print("' --- AUTO-GENERATED from viewer/entity-graph.json (OpenDEAM " +
          g["metamodel_version"] + ", pin " + g.get("opendeam_model_pin", "?") + ") ---")
    print("' Do not edit manually — regenerate with: python3 .github/scripts/generate_puml.py")
    print()

    def emit_entity(e, indent="    "):
        alias = e["class_alias"]
        display = e["display_name"]
        status = e.get("status", "")
        # NOTE: no <<abstract>> stereotype on entities — PlantUML renders it
        # as a «abstract» text line that the SVG cross-format validator's
        # longest-text heuristic picks up as the entity name. Abstractness
        # lives in the graph data (abstract: true), not the diagram.
        if status in ("scaffold", "existing"):
            print(f"{indent}' ({status})")
        print(f'{indent}entity "{display}" as {alias} {{')
        print(f"{indent}    + id : string")
        print(f"{indent}    + name : string")
        print(f"{indent}}}")

    # ─── Layer packages with entities ───
    for l in layers:
        lid = l["id"]
        if lid not in by_layer:
            continue
        num = lid[1:]
        print(f'package "Layer {num}: {l["name"]}" {l["dark_color"]} {{')
        for e in by_layer[lid]:
            emit_entity(e)
        print("}")
        print()

    # ─── Dimension entities (ADR-0002 D1: cross-cutting, no home layer) ───
    if dimension_entities:
        dim_names = {d["id"]: d["name"] for d in g.get("dimensions", [])}
        dim_fill = TOKENS["dimension"]["fill"]
        for e in dimension_entities:
            dim_label = dim_names.get(e.get("dimension", ""), "Dimension")
            print(f'package "{dim_label} (cross-cutting)" <<dimension>> {dim_fill} {{')
            emit_entity(e)
            print("}")
            print()

    # ─── Inheritance (ADR-0002 D3: specializes) ───
    specializations = [(e["class_alias"], e["specializes"]) for e in entities if e.get("specializes")]
    if specializations:
        print("' --- SPECIALIZATION (entity.specializes) ---")
        for child, parent in specializations:
            print(f"{child} --|> {parent}")
        print()

    # ─── Typed relationships (rel_type + cardinality; style derived) ───
    print("' --- RELATIONSHIPS (from graph; style derived from rel_type) ---")
    valid_aliases = {e["class_alias"] for e in entities}
    valid_count = 0
    for r in relationships:
        if r["from"] not in valid_aliases or r["to"] not in valid_aliases:
            print(f"' WARNING: relationship references unknown alias — skipping {r['from']}->{r['to']}")
            continue
        edge = ".." if r.get("style") == "dashed" else "--"
        label = f'{r["label"]} [{r["cardinality"]}]' if r.get("cardinality") else r["label"]
        print(f'{r["from"]} {edge} {r["to"]} : "{label}"')
        valid_count += 1
    print()
    print(f"' Generated {valid_count} relationship edges, {len(specializations)} specialization edges")
    print()
    print("@enduml")


if __name__ == "__main__":
    main()
