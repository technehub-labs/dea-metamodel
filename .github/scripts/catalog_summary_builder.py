"""Build catalog summary data for the viewer (CR-CATALOG-STRUCT-07b).

Reads each conformant catalog's CATALOG.yaml via the cross-repo consumer
(dea-metaframework/tools/cross_repo_consumer; vendored copy at
.github/scripts/cross_repo_consumer/) and produces a per-catalog summary
that the viewer can render inside an entity's detail panel.

Output schema (catalog_summary entry per entity-graph.entities[] element):

    catalog_summary: {
        "entity_count": int,        # total entities in the catalog
        "canonical": int,           # structurally canonical
        "candidates": int,
        "retired": int,
        "research_files": int,
        "latest_modified": str,     # YYYY-MM-DD or None
        "metamodel_version": str,
        "abbreviation": str,        # catalog's abbreviation (BC/BP/DBSF/SH/...)
        "catalog_name": str,        # catalog's full name
        "generated_at": str,        # ISO 8601, when this summary was built
    }

Entities whose catalog_repo is null or not a known adopter get NO
catalog_summary field (the viewer falls back to the existing UI).

Public surface:
    build_catalog_summaries(cache_dir, offline=True) -> dict[str, dict]
        Fetch + parse every known adopter's CATALOG.yaml; return
        {repo_name: summary_dict}.

Import model:
    The consumer module is vendored at .github/scripts/cross_repo_consumer/
    and is loaded via a sys.path insertion (scripts/ is not a package).
    This keeps the vendored copy isolated from the rest of dea-metamodel's
    Python tooling (generate_puml.py, generate_registry.py, etc.) which
    do not need the consumer.
"""

from __future__ import annotations

import datetime as _dt
import os
import sys
from pathlib import Path
from typing import Any

# Local import; the consumer module is vendored alongside this file.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from cross_repo_consumer import parse_catalog_yaml  # noqa: E402
from cross_repo_consumer.fetch import fetch_catalog_yaml  # noqa: E402


# Known conformant adopters (L1 catalogs). Keep in lock-step with the
# cross-repo adoption tracker at dea-metaframework/docs/standards/
# catalog-repository-pattern-adoption.md.
KNOWN_CATALOG_REPOS: tuple[str, ...] = (
    "dea-catalog-processes",
    "dea-catalog-business-capabilities",
    "dea-catalog-digital-business-service-factory",
    "dea-catalog-stakeholders",
)


def _summary_for_catalog(repo: str, catalog) -> dict[str, Any]:
    """Build one catalog_summary entry from a parsed Catalog object."""
    return {
        "entity_count": catalog.counts.entities,
        "canonical": catalog.counts.canonical,
        "candidates": catalog.counts.candidates,
        "retired": catalog.counts.retired,
        "research_files": catalog.counts.research_files,
        "latest_modified": catalog.latest_last_modified(),
        "metamodel_version": catalog.metadata.metamodel_version or "",
        "abbreviation": catalog.metadata.abbreviation or "",
        "catalog_name": catalog.metadata.name or "",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def build_catalog_summaries(
    cache_dir: Path | None = None,
    *,
    offline: bool | None = None,
    timeout_s: float = 15.0,
) -> dict[str, dict[str, Any]]:
    """Fetch + parse every known adopter; return {repo_name: summary_dict}.

    Args:
        cache_dir: If given, write fetches here as <repo>@main.yaml and
            read on subsequent calls. The CI workflow should set this to
            `.cache/cross_repo_consumer/` (gitignored) so the second run
            in the same job is free.
        offline: If True, never make a network call; raise on cache miss.
            If False, always fetch. If None (default), honor the
            CROSS_REPO_CONSUMER_OFFLINE env var: "1" / "true" -> True.
        timeout_s: HTTP timeout (per repo).

    Returns:
        Mapping of repo name -> summary dict. Repos that fail to fetch
        or parse are NOT included (the caller decides whether to fail).

    Raises:
        ValueError: If offline=True and any repo's cache is missing.
    """
    if offline is None:
        offline = os.environ.get("CROSS_REPO_CONSUMER_OFFLINE", "").lower() in (
            "1",
            "true",
            "yes",
        )
    summaries: dict[str, dict[str, Any]] = {}
    for repo in KNOWN_CATALOG_REPOS:
        try:
            fetch = fetch_catalog_yaml(
                repo,
                ref="main",
                cache_dir=cache_dir,
                timeout_s=timeout_s,
                offline=offline,
            )
            catalog = parse_catalog_yaml(fetch.bytes)
        except Exception:
            # Per the §9 contract the consumer MUST be tolerant: a missing
            # or stale catalog_repo is shown as "no data" in the viewer,
            # not as a hard failure. Skip; the entity-graph entry's
            # catalog_summary stays absent.
            continue
        summaries[repo] = _summary_for_catalog(repo, catalog)
    return summaries


def attach_catalog_summaries(
    entity_graph: dict[str, Any],
    summaries: dict[str, dict[str, Any]],
) -> int:
    """Mutate entity_graph.entities[] in place; attach catalog_summary
    where catalog_repo matches a known adopter.

    Returns:
        The number of entities that received a catalog_summary.
    """
    attached = 0
    for entity in entity_graph.get("entities", []):
        repo = entity.get("catalog_repo")
        if repo and repo in summaries:
            entity["catalog_summary"] = summaries[repo]
            attached += 1
    return attached


__all__ = [
    "KNOWN_CATALOG_REPOS",
    "attach_catalog_summaries",
    "build_catalog_summaries",
]