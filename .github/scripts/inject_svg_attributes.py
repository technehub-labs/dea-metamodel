"""Inject class="entity" and data-alias="<ALIAS>" attributes into PlantUML 1.2024.x SVG,
plus a second pass of coupled visual refinements (per-layer stroke, accent bar,
stereotype tint, label halos).

PlantUML 1.2024.x emits <g id="elem_<ALIAS>">...</g> for entities but
DOES NOT emit class="entity" or data-alias attributes. The Pages
site's viewer.js depends on g.entity[data-alias] selectors to wire
click + hover interactivity, so we post-process the SVG to add them.

Usage:
  python3 .github/scripts/inject_svg_attributes.py viewer/metamodel.svg
  python3 .github/scripts/inject_svg_attributes.py < input.svg > output.svg

The script runs five idempotent passes:

  1. For each <g id="elem_<ALIAS>">...</g>, prepend class="entity"
     and data-alias="<ALIAS>" to the opening tag's attribute list.
  2. For each <g id="cluster_...">...</g>, prepend class="cluster".
  3. (Phase A, Task 3) Per-layer visual refinements on every entity group:
       - Rewrite the entity <rect> stroke style from the hardcoded
         "stroke:#2DD4BF;stroke-width:1.0;" to the layer's accent at
         width 1.5.
       - Inject a 3px-wide left accent bar (<rect class="node-bar" .../>)
         immediately after the entity rect, inset 2px from the left and
         top/bottom edges, full height minus 4px vertical inset.
       - Tint the stereotype <ellipse> fill with the layer accent blended
         into the canvas #0D1117 at 0.18 alpha (precomputed per-layer
         hex values), recolor the ellipse stroke to the layer accent, and
         recolor the "C" stereotype <path> fill to the layer accent.
  4. (Phase A, Task 4) Attribute text legibility: for every <text> inside
     a <g class="entity" data-alias="..."> group whose content starts with
     " + ", lift fill from #8B949E to #B1BAC4 (AAA contrast 7.95:1 against
     #0D1117) and add a paint-order halo with a #0D1117 stroke 2px.
  5. (Phase A, Task 5) Relationship label legibility: for every italic
     <text> inside a <g id="link_<A>_<B>"> group, lift fill from #8B949E
     to #B1BAC4 and add a paint-order halo with a #080B10 stroke 2.5px.

Idempotent: every pass skips work it has already done, so re-running on
an already-injected SVG is a no-op.
"""
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Pass 1 + 2: entity / cluster class injection (pre-existing behavior)
# ---------------------------------------------------------------------------

ENTITY_RE = re.compile(r'<g\s+id="(elem_[^"]+)"([^>]*)>')
CLUSTER_RE = re.compile(r'<g\s+id="(cluster_[^"]+)"([^>]*)>')


def has_class(tag_attrs: str, cls: str) -> bool:
    """True if the existing attributes already include class="...cls..."""
    m = re.search(r'class="([^"]*)"', tag_attrs)
    if not m:
        return False
    classes = m.group(1).split()
    return cls in classes


def inject_classes(content: str) -> str:
    """Pass 1+2: inject class="entity" / class="cluster" + data-alias."""
    def replace_entity(match):
        elem_id = match.group(1)
        attrs   = match.group(2) or ""
        alias   = elem_id[len("elem_"):]
        if has_class(attrs, "entity"):
            return match.group(0)
        new_attrs = f'class="entity" data-alias="{alias}"' + ("" if not attrs else " " + attrs.lstrip())
        return f'<g id="{elem_id}" {new_attrs}>'

    content = ENTITY_RE.sub(replace_entity, content)

    def replace_cluster(match):
        cluster_id = match.group(1)
        attrs      = match.group(2) or ""
        if has_class(attrs, "cluster"):
            return match.group(0)
        new_attrs = 'class="cluster"' + ("" if not attrs else " " + attrs.lstrip())
        return f'<g id="{cluster_id}" {new_attrs}>'

    content = CLUSTER_RE.sub(replace_cluster, content)
    return content


# ---------------------------------------------------------------------------
# Pass 3: per-layer entity stroke, accent bar, stereotype tint
# ---------------------------------------------------------------------------

# Layer palette (must stay in sync with viewer.css --l1..--l5 tokens).
LAYER_HEX = {
    "L1": "#2DD4BF",  # Strategic & Investment
    "L2": "#FBBF24",  # Business Operating Model
    "L3": "#38BDF8",  # Digital & Data
    "L4": "#A78BFA",  # Technical & Integration
    "L5": "#FB7185",  # Measurement & Governance
}

# Stereotype ellipse fill = layer accent blended into #0D1117 at alpha 0.18.
# Precomputed (do not recompute at runtime to keep output deterministic).
LAYER_STEREO = {
    "L1": "#123435",
    "L2": "#373019",
    "L3": "#142F3F",
    "L4": "#28263F",
    "L5": "#37222A",
}


def load_alias_to_layer(repo_root: Path) -> dict:
    """Read viewer/entity-graph.json and build {class_alias: layer} map."""
    graph_path = repo_root / "viewer" / "entity-graph.json"
    if not graph_path.exists():
        return {}
    graph = json.loads(graph_path.read_text())
    return {e["class_alias"]: e["layer"] for e in graph.get("entities", [])}


# Match an entity group: opening tag must contain data-alias="<X>" (either
# raw PlantUML output -- after pass 1+2 inject classes -- or pre-injected
# static viewer SVGs).
ENTITY_GROUP_RE = re.compile(
    r'(<g\s+[^>]*data-alias="([^"]+)"[^>]*>)(.*?)(</g>)',
    re.DOTALL,
)

# Inside an entity group, match the main entity rect (the one with id="<ALIAS>").
ENTITY_RECT_RE = re.compile(
    r'<rect\s+([^>]*?)id="' + r'(?P<id>[A-Za-z0-9]+)' + r'"([^>]*?)/>'
)


def rewrite_entity_group(match, alias_to_layer: dict) -> str:
    """Apply Task 3 transformations to a single <g class="entity">...</g> block."""
    open_tag = match.group(1)
    alias = match.group(2)
    inner = match.group(3)
    close_tag = match.group(4)

    layer = alias_to_layer.get(alias)
    if not layer:
        # Unknown alias (entity not in entity-graph.json): leave block alone.
        return match.group(0)

    layer_color = LAYER_HEX[layer]
    stereo_fill = LAYER_STEREO[layer]

    # --- 3a. Rewrite entity rect stroke style ---
    # PlantUML emits:
    #   <rect codeLine="..." fill="#0D1117" ... style="stroke:#2DD4BF;stroke-width:1.0;" .../>
    # We rewrite just the style attribute value. Use a precise pattern that
    # captures the rect whose id matches the alias (the main entity rect).
    rect_re = re.compile(
        r'(<rect\s+[^>]*?id="' + re.escape(alias) + r'"[^>]*?)'
        r'(style=")([^"]*)(")',
    )

    def rewrite_rect_style(rm):
        head, style_open, style_val, style_close = rm.groups()
        # Idempotence: if width is already 1.5, skip.
        if "stroke-width:1.5" in style_val:
            return rm.group(0)
        return f'{head}{style_open}stroke:{layer_color};stroke-width:1.5;{style_close}'

    new_inner, n_rect = rect_re.subn(rewrite_rect_style, inner, count=1)
    if n_rect == 0:
        # No matching rect found (atypical SVG) -- skip accent bar injection.
        return match.group(0)

    # --- 3b. Rewrite stereotype ellipse + "C" path ---
    # Two ellipses can appear per entity: the small visibility circles next to
    # attributes (fill="none", rx="3") and the stereotype badge (fill="#FFFFFF",
    # rx="9"). Only the rx="9" stereotype ellipse gets the layer tint.
    ellipse_re = re.compile(
        r'(<ellipse\s+[^>]*?)fill="#FFFFFF"([^>]*?)(style=")([^"]*)(")',
    )

    def rewrite_ellipse(em):
        head, mid, style_open, style_val, style_close = em.groups()
        if "rx=\"9\"" not in head and 'rx="9"' not in mid:
            # Not the stereotype ellipse (rx=3 visibility dot); skip.
            return em.group(0)
        # Rewrite fill to layer-tinted blend.
        head = re.sub(r'fill="#FFFFFF"', f'fill="{stereo_fill}"', head)
        # Rewrite stroke to layer accent at width 1.0.
        new_style = f"stroke:{layer_color};stroke-width:1.0;"
        return f'{head}fill="{stereo_fill}"{mid}{style_open}{new_style}{style_close}'

    new_inner = ellipse_re.sub(rewrite_ellipse, new_inner)

    # The "C" icon path comes right after the stereotype ellipse.
    # PlantUML emits: <path d="..." fill="#000000"/>
    # We rewrite fill="#000000" -> fill="<layer>" only on the path that
    # immediately follows the (now-tinted) stereotype ellipse. Use a
    # lookahead from the tinted ellipse to find the next path.
    path_re = re.compile(r'(<ellipse\s+[^>]*?fill="' + re.escape(stereo_fill) +
                         r'"[^>]*?></ellipse>)(\s*<path\s+[^>]*?fill=")#000000(")')

    def rewrite_path(pm):
        return f'{pm.group(1)}{pm.group(2)}{layer_color}{pm.group(3)}'

    new_inner, n_path = path_re.subn(rewrite_path, new_inner, count=1)

    # --- 3c. Inject 3px left accent bar immediately after the entity rect ---
    # Idempotence: check for class="node-bar" -- if already present, skip.
    if 'class="node-bar"' in new_inner:
        return open_tag + new_inner + close_tag

    # Extract the rect's x, y, width, height to compute the bar geometry.
    main_rect_m = re.search(
        r'<rect\s+[^>]*?id="' + re.escape(alias) + r'"[^>]*?/>',
        new_inner,
    )
    if not main_rect_m:
        return open_tag + new_inner + close_tag

    rect_attrs = main_rect_m.group(0)
    def _attr(name):
        # Use a leading word boundary so 'x=' doesn't match inside 'rx='.
        m = re.search(rf'(?<!\w){name}="([^"]+)"', rect_attrs)
        return m.group(1) if m else None

    rect_x  = float(_attr("x") or 0)
    rect_y  = float(_attr("y") or 0)
    rect_h  = float(_attr("height") or 0)
    bar_x = rect_x + 2
    bar_y = rect_y + 2
    bar_h = rect_h - 4
    accent_bar = (
        f'<rect class="node-bar" fill="{layer_color}" '
        f'x="{bar_x}" y="{bar_y}" width="3" height="{bar_h}"/>'
    )

    # Insert accent bar immediately after the entity rect (the rect with
    # id="<alias>"). We splice by replacing the matched rect string with
    # rect + accent_bar.
    new_inner = new_inner.replace(
        main_rect_m.group(0),
        main_rect_m.group(0) + accent_bar,
        1,
    )

    return open_tag + new_inner + close_tag


def inject_layer_visuals(content: str, alias_to_layer: dict) -> str:
    """Pass 3: per-layer entity stroke + accent bar + stereotype tint."""
    if not alias_to_layer:
        return content
    return ENTITY_GROUP_RE.sub(lambda m: rewrite_entity_group(m, alias_to_layer), content)


# ---------------------------------------------------------------------------
# Pass 4: attribute text legibility (inside entity groups)
# ---------------------------------------------------------------------------

# Match an entire <g ...data-alias="...">...</g> block, then operate on
# <text> nodes within that block whose content starts with " + ".
ATTR_TEXT_RE = re.compile(
    r'(<text\b[^>]*?)fill="#8B949E"([^>]*?>)\s*\+\s+([^<]*</text>)',
)

HALO_ATTR_STYLE = 'paint-order: stroke; stroke: #0D1117; stroke-width: 2px;'


def lift_attribute_text(content: str) -> str:
    """Pass 4: lift #8B949E -> #B1BAC4 + halo on entity attribute <text>."""
    def replace_in_entity_group(em):
        open_tag, alias, inner, close_tag = em.group(1), em.group(2), em.group(3), em.group(4)
        # Idempotence per-element: skip <text> already carrying the halo style.
        def rewrite_text(tm):
            head, tail, body = tm.group(1), tm.group(2), tm.group(3)
            if "paint-order: stroke" in head or "paint-order: stroke" in tail:
                return tm.group(0)
            return f'{head}fill="#B1BAC4" style="{HALO_ATTR_STYLE}"{tail}{body}'

        # ATTR_TEXT_RE matches anywhere; restrict to "+ prefix" body content.
        ATTR_RE = re.compile(
            r'(<text\b[^>]*?)fill="#8B949E"([^>]*?>)\s*(\+[^<]*</text>)'
        )
        new_inner = ATTR_RE.sub(rewrite_text, inner)
        return open_tag + new_inner + close_tag

    return ENTITY_GROUP_RE.sub(replace_in_entity_group, content)


# ---------------------------------------------------------------------------
# Pass 5: relationship label legibility (italic text inside link groups)
# ---------------------------------------------------------------------------

LINK_GROUP_RE = re.compile(
    r'(<g\s+id="link_[^"]+"[^>]*>)(.*?)(</g>)',
    re.DOTALL,
)

REL_TEXT_RE = re.compile(
    r'(<text\b[^>]*?fill="#8B949E"[^>]*?font-style="italic"[^>]*?>)'
    r'([^<]*</text>)'
)

REL_HALO_STYLE = 'paint-order: stroke; stroke: #080B10; stroke-width: 2.5px;'


def lift_relationship_text(content: str) -> str:
    """Pass 5: lift #8B949E -> #B1BAC4 + halo on italic relationship labels."""
    def rewrite_link_group(lm):
        open_tag, inner, close_tag = lm.group(1), lm.group(2), lm.group(3)
        if "paint-order: stroke" in inner:
            # Group already processed.
            return lm.group(0)

        def rewrite_text(tm):
            head, body = tm.group(1), tm.group(2)
            # Idempotence: skip if paint-order halo already present.
            if "paint-order: stroke" in head:
                return tm.group(0)
            new_head = head.replace(
                'fill="#8B949E"',
                f'fill="#B1BAC4" style="{REL_HALO_STYLE}"',
            )
            return new_head + body

        new_inner = REL_TEXT_RE.sub(rewrite_text, inner)
        return open_tag + new_inner + close_tag

    return LINK_GROUP_RE.sub(rewrite_link_group, content)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def inject(content: str) -> str:
    repo_root = Path(__file__).resolve().parent.parent.parent
    alias_to_layer = load_alias_to_layer(repo_root)

    content = inject_classes(content)
    content = inject_layer_visuals(content, alias_to_layer)
    content = lift_attribute_text(content)
    content = lift_relationship_text(content)
    return content


def main():
    if len(sys.argv) > 1:
        src = Path(sys.argv[1]).read_text()
        out = inject(src)
        if len(sys.argv) > 2:
            Path(sys.argv[2]).write_text(out)
        else:
            Path(sys.argv[1]).write_text(out)
    else:
        content = sys.stdin.read()
        sys.stdout.write(inject(content))


if __name__ == "__main__":
    main()
