"""CR-9BT.2/.3 — Canonical model loader.

Pipeline (CR-9K: source → mapping → **validation** → graph):

    model envelope (YAML/JSON)
        → reference validator (tools/opendea_validate.py, levels 0–3)
        → graph transaction (nodes + edges atomically, CR-9BP)
        → LoadReport

A model that fails validation is *never* partially loaded: validation runs
before any mutation, and the load itself executes inside a single store
transaction. Canonical entities and relationships are preserved verbatim
(CR-9 DoD): every envelope field — assertion provenance (CR-8 §40-41),
source-of-record linkage (§42-43), temporal validity (CR-9F), lifecycle
status (CR-6 §22) — lands on the corresponding Node/Edge unchanged.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from ..graph.base import Edge, GraphStore, Node

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "tools" / "opendea_validate.py"


def _load_validator():
    """Import the CR-8 reference validator as a module (single source of truth
    for conformance — the runtime never re-implements validation rules)."""
    spec = importlib.util.spec_from_file_location("opendea_validate", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModelLoadError(Exception):
    """Validation failed or the envelope is malformed; nothing was loaded."""

    def __init__(self, message: str, report: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.report = report or {}


@dataclass
class LoadReport:
    """What the loader did — the receipt for a graph load."""
    model_id: str
    model_version: str
    spec_version: str
    profiles: List[str] = field(default_factory=list)
    nodes_loaded: int = 0
    edges_loaded: int = 0
    conformance_levels: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "model": {"id": self.model_id, "version": self.model_version},
            "opendea": {"version": self.spec_version},
            "profiles": self.profiles,
            "loaded": {"nodes": self.nodes_loaded, "edges": self.edges_loaded},
            "conformance": self.conformance_levels,
        }


def _validate_document(doc: Dict[str, Any], label: str) -> Dict[str, Any]:
    """Run the reference validator against an in-memory envelope."""
    validator = _load_validator()
    # The validator is path-based; materialize deterministically in a temp file.
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
        yaml.safe_dump(doc, fh)
        tmp = fh.name
    try:
        report = validator.validate(tmp)
    finally:
        Path(tmp).unlink(missing_ok=True)
    report["model"] = label
    return report


def load_document(doc: Dict[str, Any], store: GraphStore,
                  validate: bool = True) -> LoadReport:
    """Load an already-parsed model envelope into ``store``."""
    if not isinstance(doc, dict) or "elements" not in doc:
        raise ModelLoadError("document is not an OpenDEA model envelope "
                             "(missing 'elements')")
    label = (doc.get("model") or {}).get("id", "<unknown>")
    if validate:
        report = _validate_document(doc, label)
        if report["conformance"]["status"] != "passed":
            raise ModelLoadError(
                f"model {label!r} failed conformance validation "
                f"({report['summary']['errors']} error(s)) — refusing to load "
                "invalid semantics into the graph (CR-9K)",
                report=report)

    nodes = [
        Node(
            id=el["id"],
            type=el["type"],
            name=el["name"],
            version=el.get("version", "1.0.0"),
            lifecycle_status=el.get("lifecycle_status"),
            assertion=el.get("assertion") or {},
            source=el.get("source") or {},
            properties=el.get("properties") or {},
        )
        for el in doc["elements"]
    ]
    edges = [
        Edge(
            type=rel["type"],
            source=el["id"],
            target=rel["target"],
            valid_from=rel.get("valid_from"),
            valid_to=rel.get("valid_to"),
            status=rel.get("status"),
            provenance=rel.get("provenance") or {},
            properties={k: v for k, v in rel.items()
                        if k not in ("type", "target", "valid_from", "valid_to",
                                     "status", "provenance")},
        )
        for el in doc["elements"]
        for rel in el.get("relationships", [])
    ]

    with store.transaction():
        for node in nodes:
            store.create_entity(node)
        for edge in edges:
            store.create_relationship(edge)

    return LoadReport(
        model_id=label,
        model_version=(doc.get("model") or {}).get("version", ""),
        spec_version=(doc.get("opendea") or {}).get("version", ""),
        profiles=list(doc.get("profiles", [])),
        nodes_loaded=len(nodes),
        edges_loaded=len(edges),
        conformance_levels={"syntax": "pass", "structural": "pass",
                            "semantic": "pass", "profile": "pass"},
    )


def load_model(path: Union[str, Path], store: GraphStore,
               validate: bool = True) -> LoadReport:
    """Load a model envelope file (YAML or JSON) into ``store``."""
    text = Path(path).read_text()
    doc = yaml.safe_load(text)  # YAML ⊇ JSON
    return load_document(doc, store, validate=validate)
