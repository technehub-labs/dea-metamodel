"""Catalog dataclass + parser for the cross-repo consumer.

The cross-repo consumer contract (CR-CATALOG-STRUCT-07, dea-metaframework
docs/standards/catalog-repository-pattern.md §9) defines a Catalog as the
machine-readable view of a single catalog repo's `CATALOG.yaml`. This
module turns that YAML into a typed dataclass plus a few read-only
helpers so downstream consumers (viewer, AF smoke test, dea-cli, etc.)
do not all reimplement the parsing logic.

Public surface:
    Catalog                 dataclass.
    parse_catalog_yaml(...) YAML bytes/str -> Catalog.
    summary(...)            Catalog -> str (one-line human-readable).
    aggregate_summary(...)   list[Catalog] -> str (multi-catalog rollup).

Two-state semantics (important):
    The regenerator emits TWO distinct state fields per entity:
    - `state`           structural (research/candidate/canonical/retired);
                        where the canonical YAML lives in the subtree.
    - `lifecycle_status` semantic (active/candidate/retired/...);
                        declared inside the canonical YAML itself.
    Consumers MUST treat these independently: `state` answers "where
    does the YAML live?"; `lifecycle_status` answers "what does the
    entity say about itself?". A canonical-state entity can have any
    lifecycle_status; the two are not redundant.

Security note (STRICT PROHIBITION):
    This module is read-only. It MUST NOT fetch credentials, write
    files, or mutate the catalog. All inputs are assumed pre-trusted
    (from GitHub's `raw.githubusercontent.com` HTTPS endpoint); see
    `CatalogFetcher` for the fetch path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _coerce_int(v: object) -> int:
    """Coerce any YAML scalar (int/str/bool/None/list) to int.

    The regenerator's output schema is loose (catalog-index-schema.json
    has empty `properties: {}`), so we accept whatever the YAML gives
    us. Anything non-coercible falls back to 0.
    """
    if isinstance(v, bool):  # bool is a subclass of int; explicit guard
        return int(v)
    if isinstance(v, int):
        return v
    try:
        return int(str(v))
    except (TypeError, ValueError):
        return 0


# Schema keys the regenerator guarantees at the catalog root. The
# catalog-index-schema.json is currently permissive (empty properties);
# this list codifies what the regenerator actually emits.
_KNOWN_TOP_LEVEL_KEYS = frozenset({"catalog"})


@dataclass(frozen=True)
class CatalogEntity:
    """One entity in `catalog.entities[]`.

    Fields map 1:1 to the regenerator's output schema (see
    `tools/regenerate_catalog.py:build_entity_entry`). Two distinct
    state fields exist:
    - `state`            structural (research/candidate/canonical/retired)
    - `lifecycle_status` semantic   (active/candidate/retired/...)
    """

    id: str
    type: str
    state: str
    path: str
    lifecycle_status: str
    version: str
    last_modified: str
    research_count: int = 0
    candidate_count: int = 0
    canonical_count: int = 0
    retired_count: int = 0

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> "CatalogEntity":
        """Build a CatalogEntity from one entry of `entities[]`.

        Raises ValueError on missing required keys.
        """
        try:
            entity_id = str(raw["id"])
            path = str(raw["path"])
            state = str(raw["state"])
            lifecycle = str(raw["lifecycle_status"])
        except KeyError as exc:
            raise ValueError(
                f"entity entry missing required key {exc.args[0]!r}: {raw!r}"
            ) from exc
        return cls(
            id=entity_id,
            type=str(raw.get("type", "unknown")),
            state=state,
            path=path,
            lifecycle_status=lifecycle,
            version=str(raw.get("version", "0.0.0")),
            last_modified=str(raw.get("last_modified", "")),
            research_count=_coerce_int(raw.get("research_count", 0)),
            candidate_count=_coerce_int(raw.get("candidate_count", 0)),
            canonical_count=_coerce_int(raw.get("canonical_count", 0)),
            retired_count=_coerce_int(raw.get("retired_count", 0)),
        )


@dataclass(frozen=True)
class CatalogCounts:
    """Per-state entity counts surfaced at catalog.counts{}."""

    entities: int
    canonical: int
    candidates: int
    retired: int
    research_files: int
    open_change_requests: int

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> "CatalogCounts":
        return cls(
            entities=_coerce_int(raw.get("entities", 0)),
            canonical=_coerce_int(raw.get("canonical", 0)),
            candidates=_coerce_int(raw.get("candidates", 0)),
            retired=_coerce_int(raw.get("retired", 0)),
            research_files=_coerce_int(raw.get("research_files", 0)),
            open_change_requests=_coerce_int(raw.get("open_change_requests", 0)),
        )


@dataclass(frozen=True)
class CatalogMetadata:
    """Catalog-level identity + provenance."""

    id: str
    name: str
    abbreviation: str
    owner: str | None
    license: str | None
    repository: str | None
    metamodel_version: str | None
    description: str | None = None

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> "CatalogMetadata":
        return cls(
            id=str(raw.get("id", "")),
            name=str(raw.get("name", "")),
            abbreviation=str(raw.get("abbreviation", "")),
            owner=(str(raw["owner"]) if raw.get("owner") else None),
            license=(str(raw["license"]) if raw.get("license") else None),
            repository=(str(raw["repository"]) if raw.get("repository") else None),
            metamodel_version=(
                str(raw["metamodel_version"])
                if raw.get("metamodel_version")
                else None
            ),
            description=(str(raw["description"]) if raw.get("description") else None),
        )


@dataclass(frozen=True)
class Catalog:
    """A single catalog repo's parsed `CATALOG.yaml`."""

    metadata: CatalogMetadata
    counts: CatalogCounts
    entities: tuple[CatalogEntity, ...]
    raw: Mapping[str, object] = field(repr=False)

    @property
    def entity_ids(self) -> frozenset[str]:
        """Set of every entity ID in this catalog."""
        return frozenset(e.id for e in self.entities)

    def entities_by_state(self, state: str) -> tuple[CatalogEntity, ...]:
        """Filter entities by structural state (research/candidate/canonical/retired)."""
        return tuple(e for e in self.entities if e.state == state)

    def entities_by_lifecycle(self, status: str) -> tuple[CatalogEntity, ...]:
        """Filter entities by lifecycle_status (active/candidate/retired/...)."""
        return tuple(e for e in self.entities if e.lifecycle_status == status)

    def latest_last_modified(self) -> str | None:
        """Most recent last_modified timestamp across entities, or None."""
        timestamps = [e.last_modified for e in self.entities if e.last_modified]
        return max(timestamps) if timestamps else None


def parse_catalog_yaml(yaml_text: str | bytes) -> Catalog:
    """Parse `CATALOG.yaml` content into a Catalog.

    Args:
        yaml_text: Raw YAML bytes or string.

    Returns:
        A Catalog dataclass.

    Raises:
        ValueError: If the YAML is missing required top-level keys
            (the regenerator always emits `catalog:` at the root).
        yaml.YAMLError: If the text is not parseable YAML.
    """
    import yaml  # local import keeps the module lightweight for non-Python callers

    if isinstance(yaml_text, bytes):
        yaml_text = yaml_text.decode("utf-8")
    doc = yaml.safe_load(yaml_text)
    if not isinstance(doc, Mapping):
        raise ValueError("CATALOG.yaml must be a YAML mapping at top level")
    if "catalog" not in doc:
        raise ValueError(
            "CATALOG.yaml must contain a top-level `catalog:` key "
            "(regenerator always emits this)"
        )
    catalog_block = doc["catalog"]
    if not isinstance(catalog_block, Mapping):
        raise ValueError("CATALOG.yaml `catalog:` must be a mapping")

    metadata = CatalogMetadata.from_dict(catalog_block)
    counts_block = catalog_block.get("counts", {}) or {}
    counts = CatalogCounts.from_dict(counts_block)
    entities_block = catalog_block.get("entities", []) or []
    if not isinstance(entities_block, list):
        raise ValueError("CATALOG.yaml `catalog.entities` must be a list")
    entities = tuple(CatalogEntity.from_dict(e) for e in entities_block)

    return Catalog(
        metadata=metadata,
        counts=counts,
        entities=entities,
        raw=doc,
    )


def summary(catalog: Catalog) -> str:
    """One-line human-readable summary of a single catalog."""
    m = catalog.metadata
    counts = catalog.counts
    return (
        f"{m.abbreviation or m.id:>6s} | "
        f"{counts.entities:3d} entities "
        f"({counts.canonical} canonical, "
        f"{counts.candidates} candidates, "
        f"{counts.retired} retired) | "
        f"{m.metamodel_version or '-':>8s} | "
        f"{m.name}"
    )


def aggregate_summary(catalogs: list[Catalog]) -> str:
    """Multi-catalog rollup, sorted by abbreviation.

    Useful for the viewer and any consumer that wants a single-line
    "across all catalogs" overview.
    """
    if not catalogs:
        return "no catalogs"
    header = (
        f"{'abbrev':>6s} | {'entities':>9s} | "
        f"{'canon':>5s} | {'cand':>4s} | {'ret':>3s} | "
        f"{'meta':>8s} | name"
    )
    rows = [header, "-" * len(header)]
    for cat in sorted(catalogs, key=lambda c: c.metadata.abbreviation or c.metadata.id):
        rows.append(summary(cat))
    return "\n".join(rows)


__all__ = [
    "Catalog",
    "CatalogEntity",
    "CatalogCounts",
    "CatalogMetadata",
    "aggregate_summary",
    "parse_catalog_yaml",
    "summary",
]