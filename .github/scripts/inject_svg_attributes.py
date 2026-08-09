"""Inject class="entity" and data-alias="<ALIAS>" attributes into PlantUML 1.2024.x SVG.

PlantUML 1.2024.x emits <g id="elem_<ALIAS>">...</g> for entities but
DOES NOT emit class="entity" or data-alias attributes. The Pages
site's viewer.js depends on g.entity[data-alias] selectors to wire
click + hover interactivity, so we post-process the SVG to add them.

Usage:
  python3 .github/scripts/inject_svg_attributes.py viewer/metamodel.svg
  python3 .github/scripts/inject_svg_attributes.py < input.svg > output.svg

The script:
  - For each <g id="elem_<ALIAS>">...</g>, prepend class="entity"
    and data-alias="<ALIAS>" to the opening tag's attribute list.
  - For each <g id="cluster_...">...</g>, prepend class="cluster".

Idempotent: re-running on an already-injected SVG is a no-op (it
detects existing class attributes and skips).
"""
import re
import sys
from pathlib import Path


ENTITY_RE = re.compile(r'<g\s+id="(elem_[^"]+)"([^>]*)>')
CLUSTER_RE = re.compile(r'<g\s+id="(cluster_[^"]+)"([^>]*)>')


def has_class(tag_attrs: str, cls: str) -> bool:
    """True if the existing attributes already include class="...cls..."""
    m = re.search(r'class="([^"]*)"', tag_attrs)
    if not m:
        return False
    classes = m.group(1).split()
    return cls in classes


def inject(content: str) -> str:
    # Inject class="entity" + data-alias into entity groups
    def replace_entity(match):
        elem_id = match.group(1)             # "elem_SO"
        attrs   = match.group(2) or ""       # existing attributes (may be empty)
        alias   = elem_id[len("elem_"):]     # "SO"

        if has_class(attrs, "entity"):
            return match.group(0)             # already injected, skip
        # Inject class="entity" and data-alias="<alias>" at the front
        new_attrs = f'class="entity" data-alias="{alias}"' + ("" if not attrs else " " + attrs.lstrip())
        return f'<g id="{elem_id}" {new_attrs}>'

    content = ENTITY_RE.sub(replace_entity, content)

    # Inject class="cluster" into layer cluster groups
    def replace_cluster(match):
        cluster_id = match.group(1)
        attrs      = match.group(2) or ""
        if has_class(attrs, "cluster"):
            return match.group(0)
        new_attrs = 'class="cluster"' + ("" if not attrs else " " + attrs.lstrip())
        return f'<g id="{cluster_id}" {new_attrs}>'

    content = CLUSTER_RE.sub(replace_cluster, content)

    return content


def main():
    if len(sys.argv) > 1:
        src = Path(sys.argv[1]).read_text()
        out = inject(src)
        # If second arg given, write to file; else overwrite first
        if len(sys.argv) > 2:
            Path(sys.argv[2]).write_text(out)
        else:
            Path(sys.argv[1]).write_text(out)
    else:
        # Read from stdin, write to stdout
        content = sys.stdin.read()
        sys.stdout.write(inject(content))


if __name__ == "__main__":
    main()
