"""Regression tests for SVG entity-name extraction (validate_svg_graph).

The failure these lock down: PlantUML emits relationship edges without a <g>
wrapper, so their italic labels land inside the FOLLOWING entity block. Name
selection takes max(candidates, key=len), so a long edge label can outrank the
actual display name and the validator reports a false DRIFT DETECTED.

Observed in CI on 2026-10-22: "contextualized" (13 chars) beat "Concept"
(7 chars), producing 70 SVG entities against 70 graph entities with one spurious
mismatch in each direction.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SCRIPT = BASE / ".github" / "scripts" / "validate_svg_graph.py"
SPEC = importlib.util.spec_from_file_location("vsg", SCRIPT)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError(f"cannot load {SCRIPT}")
vsg = importlib.util.module_from_spec(SPEC)
sys.modules["vsg"] = vsg
SPEC.loader.exec_module(vsg)


def _entity(alias: str, name: str) -> str:
    return (
        f'<g id="elem_{alias}" class="entity" data-alias="{alias}">'
        f'<text>{name}</text>'
        f'<text>id : string</text>'
        f"</g>"
    )


def _edge(label: str) -> str:
    return (
        '<line style="stroke:#2DD4BF"/>'
        f'<text font-style="italic">{label}</text>'
        f'<text font-style="italic">&#160;</text>'
    )


def test_italic_edge_label_does_not_displace_display_name():
    """The regression itself: a long edge label after Concept must not win."""
    svg = _entity("CON", "Concept") + _edge("contextualized") + _entity("BP", "Business Process")

    scrubbed = vsg.scrub_svg(svg)
    assert "contextualized" not in scrubbed
    assert "Contextualized" not in scrubbed

    starts = [(m.start(), m.group(1)) for m in vsg.ENTITY_START.finditer(scrubbed)]
    assert len(starts) == 2, f"expected 2 entity starts, got {len(starts)}"


def test_scrub_removes_link_wrappers():
    svg = (
        _entity("BP", "Business Process")
        + '<g id="link_1" class="link"><text>executes</text><line/></g>'
        + _entity("ISF", "Information System Function")
    )
    scrubbed = vsg.scrub_svg(svg)
    assert "executes" not in scrubbed
    assert len(vsg.ENTITY_START.findall(scrubbed)) == 2


def test_cardinality_fragments_are_scrubbed():
    """Cardinality annotations render italic and are equally not names."""
    svg = _entity("THR", "Threshold") + _edge("[0..N:0..1]") + _entity("PTG", "Performance Target")
    scrubbed = vsg.scrub_svg(svg)
    assert "[0..N:0..1]" not in scrubbed


def test_non_italic_text_is_preserved():
    """Guard against over-scrubbing: entity names must survive."""
    svg = _entity("PRV", "Provenance")
    scrubbed = vsg.scrub_svg(svg)
    assert "Provenance" in scrubbed


def test_display_names_with_slash_are_not_split_away():
    """AI/ML Model renders as separate text nodes; the name must still match."""
    svg = (
        '<g id="elem_AIM" class="entity" data-alias="AIM">'
        "<text>AI</text><text>/</text><text>ML</text><text>Model</text>"
        "</g>"
    )
    scrubbed = vsg.scrub_svg(svg)
    texts = re.findall(r"<text[^>]*>([^<]+)</text>", scrubbed)
    assert texts == ["AI", "/", "ML", "Model"], texts


def test_scrub_is_idempotent():
    svg = _entity("CON", "Concept") + _edge("contextualized")
    once = vsg.scrub_svg(svg)
    assert vsg.scrub_svg(once) == once