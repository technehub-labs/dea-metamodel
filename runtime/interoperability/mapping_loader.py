"""CR-11 Phase 5 — reference mapping registry loader.

Lifts the YAML files under ``mappings/`` into :class:`SemanticMapping`
entries on an :class:`InteropRegistry`. Each row with a resolvable
``opendea`` target becomes a governed mapping; rows that don't target
an :class:`OpenDEA concept` (the "no direct equivalent" entries) are
recorded as an :class:`Extension` shape so the *absence of equivalence*
is itself first-class information — never a silent skip.

The loader is read-only: no canonical graph mutation. Anyone replacing
the YAML files sees the registry contents change accordingly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from .model import (Extension, InteropError, MappingConfidence, MappingRelation,
                    SemanticMapping)


# CR-11 vocabulary for the external namespaces we map.
# These are NEVER ``opendea`` — extensions stay external (CR-11AR).
_EXTERNAL_NAMESPACES: Dict[str, str] = {
    "archimate": "archimate",   # ArchiMate 3.2
    "bpmn": "bpmn",             # BPMN 2.0
    "dmn": "dmn",               # DMN 1.4
    "dmm": "dmm",               # Data Management Maturity Model
}


def _confidence(value: Optional[str]) -> MappingConfidence:
    if not value:
        return MappingConfidence.UNCERTAIN
    cleaned = str(value).strip()
    # accept EXACT/exact/Exact — try the canonical (Title) and the raw form.
    for candidate in (cleaned.title(), cleaned.upper(), cleaned.lower(),
                      cleaned):
        try:
            return MappingConfidence(candidate)
        except ValueError:
            continue
    return MappingConfidence.UNCERTAIN


def _lossiness(value: Optional[str]) -> Any:
    if not value:
        return "UNKNOWN"
    from .model import Lossiness
    cleaned = str(value).strip()
    for candidate in (cleaned.upper(), cleaned.title(), cleaned):
        try:
            return Lossiness(candidate)
        except ValueError:
            continue
    return "UNKNOWN"


def _split_opendea_ref(ref: str) -> tuple[str, str]:
    """Extract (namespace, name) from `dea:BusinessProcess` style refs."""
    if not ref:
        return "", ""
    if ":" in ref:
        ns, _, name = ref.partition(":")
        return ns, name
    return "dea", ref


class MappingRegistry:
    """Read-only facade over the YAML files under ``mappings/``.

    Combining :class:`MappingRegistry` with an :class:`InteropRegistry`
    is the canonical pattern (see ``load_reference_mappings``).
    """

    def __init__(self, mappings_root: Path):
        self.root = mappings_root
        self.standards: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def default(cls) -> "MappingRegistry":
        repo = Path(__file__).resolve()
        for parent in repo.parents:
            candidate = parent / "mappings"
            if candidate.exists():
                return cls(candidate)
        raise InteropError(f"could not locate mappings/ from {repo}")

    def standards_loaded(self) -> List[str]:
        return sorted(self.standards.keys())

    def load_standard(self, standard: str) -> Dict[str, Any]:
        clean = standard.replace(".yaml", "")
        sub = self.root / clean / "mapping.yaml"
        if not sub.exists():
            raise InteropError(f"unknown reference mapping standard {standard!r}")
        with sub.open() as f:
            data = yaml.safe_load(f) or {}
        self.standards[clean] = data
        return data


def load_reference_mappings(registry: Optional[Any] = None,
                            mappings_root: Optional[Path] = None,
                            *,
                            standards: Optional[Iterable[str]] = None,
                            ) -> Dict[str, Dict[str, Any]]:
    """Load reference mappings into an :class:`InteropRegistry`.

    Returns a per-standard summary describing which mappings were lifted.
    """
    from .registry import InteropRegistry as _Registry
    registry = registry or _Registry()
    repo = MappingRegistry(mappings_root) if mappings_root is not None \
        else MappingRegistry.default()
    requested = [f"{s}.yaml" if not s.endswith(".yaml") else s
                 for s in standards] if standards is not None \
        else [f"{s}.yaml" for s in ("archimate", "bpmn", "dmn", "dmm")]
    canonical = [s.replace(".yaml", "") for s in requested]

    summary: Dict[str, Dict[str, Any]] = {}
    for standard, key in zip(requested, canonical):
        try:
            data = repo.load_standard(standard)
        except InteropError as exc:
            summary[key] = {"loaded": False, "error": str(exc)}
            continue

        ns_name = _EXTERNAL_NAMESPACES.get(key, key)
        mappings = data.get("mappings") or []
        # CR-11X/Y/Z — explicit confidence/lossiness rows override legacy
        # ``mappings:`` entries on the same source/target pair.
        confidence_by_pair: Dict[tuple, Dict[str, Any]] = {}
        for row in data.get("confidence_lossiness") or []:
            ext_value = (row.get("archimate") or row.get("bpmn")
                         or row.get("dmn") or row.get("dmm"))
            if not ext_value or ext_value == "(no direct equivalent)":
                continue
            _, opendea_name = _split_opendea_ref(row.get("opendea", ""))
            if not opendea_name:
                continue
            confidence_by_pair[(ns_name, ext_value,
                                f"opendea:{opendea_name}")] = row
        gaps = sum(1 for row in mappings
                   if any(k for k in row
                          if k in {"archimate", "bpmn", "dmn", "dmm"}
                          and row.get(k) == "(no direct equivalent)"))
        lifted = 0
        extensions = 0

        for row in mappings:
            ext = (row.get("archimate") or row.get("bpmn")
                   or row.get("dmn") or row.get("dmm"))
            if ext is None:
                continue
            if ext == "(no direct equivalent)":
                continue
            opendea_ref = row.get("opendea", "")
            _, opendea_name = _split_opendea_ref(opendea_ref)
            if not opendea_name:
                continue
            target_concept = f"opendea:{opendea_name}"
            overlay = confidence_by_pair.get(
                (ns_name, ext, target_concept)) or {}
            confidence = _confidence(overlay.get("confidence")
                                    or row.get("confidence"))
            lossiness = _lossiness(overlay.get("lossiness")
                                  or row.get("lossiness"))
            note = overlay.get("note") or row.get("note", "")
            try:
                registry.register_mapping(SemanticMapping(
                    source_concept=f"{ns_name}:{ext}",
                    target_concept=target_concept,
                    relationship=MappingRelation.MAPS_TO,
                    transformation=note,
                    confidence=confidence,
                    lossiness=lossiness,
                    owner="reference-mapping",
                    version=data.get("version", "1.0.0"),
                ))
                lifted += 1
            except InteropError:
                registry.register_extension(Extension(
                    namespace=ns_name,
                    name=opendea_name,
                    version=data.get("version", "1.0.0"),
                    definition=note,
                    source=ext,
                ))
                extensions += 1

        summary[key] = {
            "loaded": True,
            "version": data.get("version", "1.0.0"),
            "mappings_lifted": lifted,
            "gaps": gaps,
            "extensions": extensions,
        }

    return summary


__all__ = [
    "MappingRegistry",
    "load_reference_mappings",
]
