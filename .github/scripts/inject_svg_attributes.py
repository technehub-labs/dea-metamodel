"""Inject class="entity" and data-alias="<ALIAS>" attributes into PlantUML 1.2024.x SVG,
then enforce the locked diagram design tokens (viewer/diagram-tokens.json).

PlantUML 1.2024.x emits <g id="elem_<ALIAS>">...</g> for entities but
DOES NOT emit class="entity" or data-alias attributes. The Pages
site's viewer.js depends on g.entity[data-alias] selectors to wire
click + hover interactivity, so we post-process the SVG to add them.

Usage:
  python3 .github/scripts/inject_svg_attributes.py viewer/metamodel.svg
  python3 .github/scripts/inject_svg_attributes.py < input.svg > output.svg

All design values come from viewer/diagram-tokens.json (via diagram_tokens.py)
and viewer/entity-graph.json (per-layer accent/dark colors cascading from the
OpenDEAM root model). Design principle (locked 2026-08-15, variant "C2"):
no canvas — transparent background; dark layer-colored packages; small italic
relationship labels with NO outline/halo; light-grey attribute text on dark
entity fills. Do not hardcode colors/sizes here — extend the token file.

Passes (all idempotent — re-running on an injected SVG is a no-op):

  1. Entity/class injection: <g id="elem_<ALIAS>"> gets class="entity"
     and data-alias="<ALIAS>".
  2. Cluster injection: <g id="cluster_..."> gets class="cluster".
  3. Per-entity visuals (token: entity.*): entity rect stroke -> layer
     accent; stereotype badge fill -> accent blended into entity fill
     (stereotype_blend_alpha), badge + "C" icon + visibility dots recolored
     to the layer accent; 3px left accent bar injected.
  4. Attribute text (token: entity.attribute_text): PlantUML emits
     attribute rows as BLACK text (fill="#000000") on the dark entity fill
     — invisible. Rewritten to the attribute_text token, no halo.
  5. Relationship labels (token: relationship_label.*): italic edge labels
     normalized to the token fill + font size. NO halo/outline (the old
     paint-order stroke is stripped if present). If PlantUML ignored the
     PUML-level FontSize, size is enforced here and labels re-centred.
  6. Canvas (token: canvas.background): the SVG root background is forced
     transparent so the diagram inherits the page background.
  7. Package frames (token: package.*): PlantUML's plain theme drops the
     per-package colors from the PUML and renders white frames with black
     strokes. Fill/stroke are re-enforced from the graph (layer dark_color /
     accent; dimension tokens for cross-cutting packages) and package
     titles recolored to match.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_tokens import (
    DIM,
    alias_to_layer,
    layer_palette,
    load_graph,
    load_tokens,
    stereotype_fill,
)

TOKENS = load_tokens()
GRAPH = load_graph()
PALETTE = layer_palette(TOKENS, GRAPH)          # {"L1": {"accent","dark"}, ..., "DIM": ...}
ALIAS_LAYER = alias_to_layer(GRAPH)             # {"SO": "L1", ..., "MTR": "DIM"}
ENTITY_TOK = TOKENS["entity"]
REL_TOK = TOKENS["relationship_label"]
PKG_TOK = TOKENS["package"]


def layer_of(alias: str) -> str:
    return ALIAS_LAYER.get(alias, DIM)


def accent_of(alias: str) -> str:
    return PALETTE[layer_of(alias)]["accent"]


# ---------------------------------------------------------------------------
# Pass 1 + 2: entity / cluster class injection (pre-existing behavior)
# ---------------------------------------------------------------------------

ENTITY_RE = re.compile(r'<g\s+id="(elem_[^"]+)"([^>]*)>')
CLUSTER_RE = re.compile(r'<g\s+id="(cluster_[^"]+)"([^>]*)>')


def has_class(tag_attrs: str, cls: str) -> bool:
    """True if the existing attributes already include class="...cls...\""""
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
# Pass 3: per-entity visuals (stroke, badge, icon, dots, accent bar)
# ---------------------------------------------------------------------------

# Match an entity group: opening tag must contain data-alias="<X>" (either
# raw PlantUML output -- after pass 1+2 inject classes -- or pre-injected
# static viewer SVGs).
ENTITY_GROUP_RE = re.compile(
    r'(<g\s+[^>]*data-alias="([^"]+)"[^>]*>)(.*?)(</g>)',
    re.DOTALL,
)

# PlantUML emits the badge ellipse self-closing: <ellipse ... fill="#FFFFFF"
# rx="9" ... style="stroke:#000000;stroke-width:1.0;"/> (older versions used
# a separate closing tag — both forms matched).
BADGE_ELLIPSE_RE = re.compile(
    r'<ellipse\s+[^>]*?fill="#FFFFFF"[^>]*?rx="9"[^>]*?/>'
)
# The "C" stereotype icon is the only black-filled <path> inside an entity.
C_ICON_RE = re.compile(r'(<path\s+d="[^"]+"\s*)fill="#000000"\s*/>')
# Visibility dots: small unfilled ellipses (rx="3") with a black stroke.
VIS_DOT_RE = re.compile(
    r'(<ellipse\s+[^>]*?fill="none"[^>]*?)style="stroke:#000000;stroke-width:1\.0;"'
)


def rewrite_entity_group(match) -> str:
    """Apply pass-3 transformations to a single <g class="entity">...</g> block."""
    open_tag = match.group(1)
    alias = match.group(2)
    inner = match.group(3)
    close_tag = match.group(4)

    if alias not in ALIAS_LAYER:
        # Unknown alias (entity not in entity-graph.json): leave block alone.
        return match.group(0)

    layer_color = accent_of(alias)
    stereo_fill = stereotype_fill(layer_color, TOKENS)
    stroke_w = ENTITY_TOK["stroke_width"]

    # --- 3a. Rewrite entity rect stroke style ---
    # PlantUML emits:
    #   <rect codeLine="..." fill="#0D1117" ... style="stroke:#2DD4BF;stroke-width:1.0;" .../>
    rect_re = re.compile(
        r'(<rect\s+[^>]*?id="' + re.escape(alias) + r'"[^>]*?)'
        r'(style=")([^"]*)(")',
    )

    def rewrite_rect_style(rm):
        head, style_open, style_val, style_close = rm.groups()
        # Idempotence: if already at the token width with the layer color, skip.
        if f"stroke:{layer_color}" in style_val and f"stroke-width:{stroke_w}" in style_val:
            return rm.group(0)
        return f'{head}{style_open}stroke:{layer_color};stroke-width:{stroke_w};{style_close}'

    new_inner, n_rect = rect_re.subn(rewrite_rect_style, inner, count=1)
    if n_rect == 0:
        # No matching rect found (atypical SVG) -- skip accent bar injection.
        return match.group(0)

    # --- 3b. Stereotype badge ellipse: white -> accent-tinted fill, accent stroke ---
    def rewrite_badge(em):
        tag = em.group(0)
        # Idempotence: badge already tinted.
        if f'fill="{stereo_fill}"' in tag:
            return tag
        tag = tag.replace('fill="#FFFFFF"', f'fill="{stereo_fill}"')
        tag = re.sub(r'style="[^"]*"', f'style="stroke:{layer_color};stroke-width:1.0;"', tag)
        return tag

    new_inner = BADGE_ELLIPSE_RE.sub(rewrite_badge, new_inner)

    # --- 3b2. "C" icon path: black -> layer accent ---
    new_inner = C_ICON_RE.sub(rf'\1fill="{layer_color}"/>', new_inner)

    # --- 3b3. Visibility dots: black stroke -> layer accent ---
    new_inner = VIS_DOT_RE.sub(rf'\1style="stroke:{layer_color};stroke-width:1.0;"', new_inner)

    # --- 3c. Inject left accent bar immediately after the entity rect ---
    # Idempotence: check for class="node-bar" -- if already present, skip.
    if 'class="node-bar"' in new_inner:
        return open_tag + new_inner + close_tag

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

    rect_x = float(_attr("x") or 0)
    rect_y = float(_attr("y") or 0)
    rect_h = float(_attr("height") or 0)
    bar_w = ENTITY_TOK["accent_bar_width"]
    bar_x = rect_x + 2
    bar_y = rect_y + 2
    bar_h = rect_h - 4
    accent_bar = (
        f'<rect class="node-bar" fill="{layer_color}" '
        f'x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}"/>'
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


def inject_layer_visuals(content: str) -> str:
    """Pass 3: per-entity stroke + badge/icon/dots + accent bar."""
    if not ALIAS_LAYER:
        return content
    return ENTITY_GROUP_RE.sub(rewrite_entity_group, content)


# ---------------------------------------------------------------------------
# Pass 4: attribute text (token: entity.attribute_text)
# ---------------------------------------------------------------------------

# PlantUML 1.2024.x + plain theme emits attribute rows as BLACK text with no
# visibility marker:
#   <text fill="#000000" font-family="Arial" font-size="14" ...>id : string</text>
# Older versions emitted fill="#8B949E" with a leading "+ ". Both forms are
# rewritten to the attribute_text token. No halo: the text sits on the solid
# entity fill where the token color has AAA contrast.
ATTR_TEXT_RE = re.compile(
    r'<text\b[^>]*?fill="(?:#000000|#8B949E)"[^>]*?>(\s*\+?\s*[A-Za-z_][A-Za-z0-9_]*\s*:\s*[^<]*)</text>'
)


def lift_attribute_text(content: str) -> str:
    """Pass 4: attribute rows -> entity.attribute_text, inside entity groups."""
    attr_fill = ENTITY_TOK["attribute_text"]

    def replace_in_entity_group(em):
        open_tag, alias, inner, close_tag = em.group(1), em.group(2), em.group(3), em.group(4)

        def rewrite_text(tm):
            head = tm.group(0)
            if f'fill="{attr_fill}"' in head:
                return head  # idempotent
            return re.sub(r'fill="(?:#000000|#8B949E)"', f'fill="{attr_fill}"', head, count=1)

        return open_tag + ATTR_TEXT_RE.sub(rewrite_text, inner) + close_tag

    return ENTITY_GROUP_RE.sub(replace_in_entity_group, content)


# ---------------------------------------------------------------------------
# Pass 5: relationship labels (token: relationship_label.*)
# ---------------------------------------------------------------------------

# Italic <text> elements are relationship labels (entity names, package
# titles and attribute rows are upright). Two source forms exist:
#   fresh render:  <text fill="#8B949E" font-family="..." font-size="N"
#                        font-style="italic" lengthAdjust="spacing"
#                        textLength="L" x="X" y="Y">label</text>
#   legacy injected: same but fill="#B1BAC4" with a paint-order halo style.
TEXT_RE = re.compile(r'<text\b(?P<attrs>[^>]*)>(?P<body>[^<]*</text>)')


def normalize_relationship_labels(content: str) -> str:
    """Pass 5: token fill + size on relationship labels, halo stripped."""
    target_fill = REL_TOK["text"]
    target_size = int(REL_TOK["font_size"])

    def rewrite(tm):
        attrs = tm.group("attrs")
        body = tm.group("body")
        if 'font-style="italic"' not in attrs:
            return tm.group(0)  # not a relationship label
        if body.startswith("&#171;"):
            return tm.group(0)  # «stereotype» text — handled by pass 7

        # Strip any legacy halo style attribute entirely.
        attrs = re.sub(r'\s*style="[^"]*paint-order:[^"]*"', "", attrs)
        # Enforce token fill.
        attrs = re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{target_fill}"', attrs, count=1)

        # Enforce token font size, re-centring the label when the size changes.
        size_m = re.search(r'font-size="([\d.]+)"', attrs)
        if size_m and float(size_m.group(1)) != target_size:
            old_size = float(size_m.group(1))
            ratio = target_size / old_size
            attrs = attrs.replace(size_m.group(0), f'font-size="{target_size}"', 1)
            len_m = re.search(r'textLength="([\d.]+)"', attrs)
            x_m = re.search(r'(?<!\w)x="([\d.]+)"', attrs)
            if len_m and x_m:
                old_len = float(len_m.group(1))
                new_len = old_len * ratio
                new_x = float(x_m.group(1)) + (old_len - new_len) / 2.0
                # Drop lengthAdjust/textLength so the label renders at its
                # natural metrics; shift x to keep the visual centre.
                attrs = re.sub(r'\s*lengthAdjust="[^"]*"', "", attrs)
                attrs = attrs.replace(len_m.group(0), "", 1)
                attrs = attrs.replace(x_m.group(0), f'x="{new_x:.4f}"', 1)

        return f'<text{attrs}>{body}'

    return TEXT_RE.sub(rewrite, content)


# ---------------------------------------------------------------------------
# Pass 6: canvas background (token: canvas.background)
# ---------------------------------------------------------------------------

SVG_ROOT_RE = re.compile(r'(<svg\b[^>]*?style=")([^"]*)(")')


def enforce_canvas(content: str) -> str:
    """Pass 6: root SVG background -> canvas.background token (transparent)."""
    target = TOKENS["canvas"]["background"]

    def rewrite(rm):
        head, style_val, close = rm.groups()
        if f"background:{target}" in style_val:
            return rm.group(0)
        if "background:" in style_val:
            new_style = re.sub(r'background:[^;]+;', f'background:{target};', style_val)
        else:
            # PlantUML honors `skinparam backgroundColor transparent` by
            # omitting the background entirely — make it explicit anyway so
            # the token is visible in the artefact.
            new_style = style_val + f"background:{target};"
        return head + new_style + close

    return SVG_ROOT_RE.sub(rewrite, content, count=1)


# ---------------------------------------------------------------------------
# Pass 7: package frames + titles (token: package.*)
# ---------------------------------------------------------------------------

# PlantUML's plain theme drops the per-package colors from the PUML source
# (package "..." #RRGGBB) and renders package frames as white paths with a
# black stroke. Enforce the graph's layer colors instead.
PKG_PATH_RE = re.compile(r'<path d="[^"]+" fill="#FFFFFF" style="stroke:#000000;stroke-width:1\.0;"/>')
PKG_TITLE_RE = re.compile(
    r'<text([^>]*)>((?:Layer \d|Semantic Dimension|Measurement Dimension)[^<]*)</text>'
)
TITLE_LAYER_RE = re.compile(r"Layer (\d)")


def enforce_packages(content: str) -> str:
    """Pass 7: package frame fill/stroke + title color from the palette."""
    stroke_w = PKG_TOK["stroke_width"]

    # --- frames: identify each white package path's layer via the title ---
    pieces = []
    last = 0
    for m in PKG_PATH_RE.finditer(content):
        ahead = content[m.end():m.end() + 4000]
        tm = PKG_TITLE_RE.search(ahead)
        lm = TITLE_LAYER_RE.match(tm.group(2)) if tm else None
        layer = f"L{lm.group(1)}" if lm else DIM
        pal = PALETTE.get(layer, PALETTE[DIM])
        new_path = m.group(0).replace(
            'fill="#FFFFFF" style="stroke:#000000;stroke-width:1.0;"',
            f'fill="{pal["dark"]}" style="stroke:{pal["accent"]};stroke-width:{stroke_w};"',
        )
        pieces.append(content[last:m.start()])
        pieces.append(new_path)
        last = m.end()
    pieces.append(content[last:])
    content = "".join(pieces)

    # --- titles: black -> layer accent ---
    def rewrite_title(tm):
        attrs, title = tm.group(1), tm.group(2)
        lm = TITLE_LAYER_RE.match(title)
        layer = f"L{lm.group(1)}" if lm else DIM
        accent = PALETTE.get(layer, PALETTE[DIM])["accent"]
        if f'fill="{accent}"' in attrs:
            return tm.group(0)
        new_attrs = re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{accent}"', attrs, count=1)
        return f"<text{new_attrs}>{title}</text>"

    content = PKG_TITLE_RE.sub(rewrite_title, content)

    # --- «dimension» stereotype texts: black italic -> dimension accent ---
    dim_accent = PALETTE[DIM]["accent"]
    DIM_STEREO_RE = re.compile(
        r'<text\b[^>]*?fill="(?P<fill>#[0-9A-Fa-f]{6})"[^>]*?>&#171;dimension&#187;</text>'
    )

    def rewrite_dim_stereo(m):
        if m.group("fill") == dim_accent:
            return m.group(0)
        return m.group(0).replace(f'fill="{m.group("fill")}"', f'fill="{dim_accent}"', 1)

    content = DIM_STEREO_RE.sub(rewrite_dim_stereo, content)
    return content


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def inject(content: str) -> str:
    content = inject_classes(content)
    content = inject_layer_visuals(content)
    content = lift_attribute_text(content)
    content = normalize_relationship_labels(content)
    content = enforce_canvas(content)
    content = enforce_packages(content)
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
