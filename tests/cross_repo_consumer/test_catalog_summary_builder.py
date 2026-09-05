"""Tests for the catalog_summary_builder (CR-CATALOG-STRUCT-07b).

The builder wraps the cross-repo consumer to produce per-adopter
summary dicts, then attaches them to the entity graph. Tests are
offline-only: the fetcher is exercised against a local cache dir.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from catalog_summary_builder import (
    KNOWN_CATALOG_REPOS,
    attach_catalog_summaries,
    build_catalog_summaries,
)


@pytest.fixture
def consumer_cache(tmp_path):
    """Build a cache directory from local CATALOG.yaml files."""
    cache = tmp_path / "cache"
    cache.mkdir()
    for repo in KNOWN_CATALOG_REPOS:
        src = Path(f"/home/hermes/dea-work/{repo}/CATALOG.yaml")
        if src.is_file():
            (cache / f"{repo}@main.yaml").write_bytes(src.read_bytes())
    return cache


def test_known_catalog_repos_lists_all_four_adopters() -> None:
    """The builder's hard-coded list of adopters matches the standard."""
    assert set(KNOWN_CATALOG_REPOS) == {
        "dea-catalog-processes",
        "dea-catalog-business-capabilities",
        "dea-catalog-digital-business-service-factory",
        "dea-catalog-stakeholders",
    }


def test_build_summaries_offline(consumer_cache: Path) -> None:
    """build_catalog_summaries parses every cached adopter."""
    summaries = build_catalog_summaries(
        cache_dir=consumer_cache, offline=True
    )
    assert len(summaries) == 4
    # Process catalog is the smallest non-scaffold adopter.
    proc = summaries["dea-catalog-processes"]
    assert proc["abbreviation"] == "BP"
    assert proc["entity_count"] >= 2
    assert proc["latest_modified"] is not None
    # Stakeholders scaffold returns 0 entities.
    sh = summaries["dea-catalog-stakeholders"]
    assert sh["abbreviation"] == "SH"
    assert sh["entity_count"] == 0
    assert sh["latest_modified"] is None


def test_build_summaries_generated_at_is_iso_8601(
    consumer_cache: Path,
) -> None:
    summaries = build_catalog_summaries(
        cache_dir=consumer_cache, offline=True
    )
    # Loose ISO 8601 check: contains "T" and ends with "Z".
    for s in summaries.values():
        assert "T" in s["generated_at"]
        assert s["generated_at"].endswith("Z")


def test_attach_catalog_summaries_only_att_mknown_repos() -> None:
    """attach_catalog_summaries only touches entities whose catalog_repo
    is in the supplied summaries dict."""
    graph = {
        "entities": [
            {
                "entity_id": "dea:entity-business-process",
                "class_alias": "BP",
                "display_name": "Business Process",
                "catalog_repo": "dea-catalog-processes",
                "repo_url": None,
                "status": "existing",
            },
            {
                "entity_id": "dea:entity-ecosystem-platform",
                "class_alias": "EP",
                "display_name": "Ecosystem Platform",
                "catalog_repo": "dea-catalog-ecosystem-platforms",  # not a known adopter
                "repo_url": None,
                "status": "proposed",
            },
            {
                "entity_id": "dea:entity-collaboration-agreement",
                "class_alias": "CA",
                "display_name": "Collaboration Agreement",
                "catalog_repo": None,
                "repo_url": None,
                "status": "planned",
            },
        ]
    }
    summaries = {
        "dea-catalog-processes": {
            "entity_count": 2,
            "canonical": 2,
            "candidates": 0,
            "retired": 0,
            "research_files": 3,
            "latest_modified": "2026-09-05",
            "metamodel_version": "1.0.0",
            "abbreviation": "BP",
            "catalog_name": "Business Process",
            "generated_at": "2026-09-05T12:00:00Z",
        }
    }
    attached = attach_catalog_summaries(graph, summaries)
    assert attached == 1
    assert "catalog_summary" in graph["entities"][0]
    assert "catalog_summary" not in graph["entities"][1]  # not a known adopter
    assert "catalog_summary" not in graph["entities"][2]  # catalog_repo is null


def test_attach_handles_missing_summaries_gracefully() -> None:
    """No summaries -> no attachments; no exception."""
    graph = {
        "entities": [
            {
                "entity_id": "dea:entity-x",
                "class_alias": "X",
                "display_name": "X",
                "catalog_repo": "dea-catalog-processes",
                "repo_url": None,
                "status": "existing",
            }
        ]
    }
    attached = attach_catalog_summaries(graph, {})
    assert attached == 0
    assert "catalog_summary" not in graph["entities"][0]


def test_build_summaries_offline_cache_miss(tmp_path: Path) -> None:
    """Empty cache + offline=True -> empty summaries (no exception)."""
    cache = tmp_path / "empty"
    cache.mkdir()
    summaries = build_catalog_summaries(cache_dir=cache, offline=True)
    assert summaries == {}


def test_summary_schema_is_complete(consumer_cache: Path) -> None:
    """Each summary has every required field (defends against silent
    field drops if the dataclass changes)."""
    required = {
        "entity_count",
        "canonical",
        "candidates",
        "retired",
        "research_files",
        "latest_modified",
        "metamodel_version",
        "abbreviation",
        "catalog_name",
        "generated_at",
    }
    summaries = build_catalog_summaries(
        cache_dir=consumer_cache, offline=True
    )
    for repo, s in summaries.items():
        missing = required - s.keys()
        assert not missing, f"{repo} summary missing {missing}"