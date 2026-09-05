#!/usr/bin/env python3
"""CLI for the cross-repo consumer (CR-CATALOG-STRUCT-07a).

Usage:
    # Fetch every known catalog and print a one-line summary per repo.
    python -m tools.cross_repo_consumer.cli --repos dea-catalog-processes \
        dea-catalog-business-capabilities

    # Use a local cache (faster re-runs; CI sets XDG_CACHE_HOME).
    python -m tools.cross_repo_consumer.cli --repos dea-catalog-stakeholders \
        --cache-dir ~/.cache/dea-metaframework

    # Validate against the bundled schema (offline-friendly).
    python -m tools.cross_repo_consumer.cli --repos dea-catalog-processes \
        --offline --cache-dir .cache

Exit codes:
    0  success.
    1  one or more fetches or parses failed (errors printed to stderr).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .fetch import fetch_catalog_yaml
from . import parse_catalog_yaml, aggregate_summary


_KNOWN_CATALOG_REPOS = (
    "dea-catalog-processes",
    "dea-catalog-business-capabilities",
    "dea-catalog-digital-business-service-factory",
    "dea-catalog-stakeholders",
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cross-repo-consumer",
        description=(
            "Fetch and summarize one or more catalog repos' CATALOG.yaml "
            "per the CR-CATALOG-STRUCT-07 contract."
        ),
    )
    p.add_argument(
        "--repos",
        nargs="*",
        default=list(_KNOWN_CATALOG_REPOS),
        help=(
            "Catalog repo names (without org prefix). "
            f"Defaults to all known adopters: {', '.join(_KNOWN_CATALOG_REPOS)}."
        ),
    )
    p.add_argument("--ref", default="main", help="Git ref (default: main).")
    p.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Cache directory for fetched YAML; speeds up repeated runs.",
    )
    p.add_argument(
        "--offline",
        action="store_true",
        help="Do not fetch; only read from --cache-dir.",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP timeout in seconds (default: 15).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    catalogs = []
    failures: list[str] = []

    for repo in args.repos:
        try:
            fetch = fetch_catalog_yaml(
                repo,
                ref=args.ref,
                cache_dir=args.cache_dir,
                timeout_s=args.timeout,
                offline=args.offline,
            )
            cat = parse_catalog_yaml(fetch.bytes)
            catalogs.append(cat)
            print(f"  fetched  {repo:55s} ({len(fetch.bytes):5d}B, "
                  f"{'cache' if fetch.from_cache else 'http'})")
        except Exception as exc:  # noqa: BLE001 (CLI surface; surfacing all)
            failures.append(f"{repo}: {type(exc).__name__}: {exc}")
            print(f"  FAILED   {repo:55s} {type(exc).__name__}: {exc}",
                  file=sys.stderr)

    if not catalogs:
        print("no catalogs fetched", file=sys.stderr)
        return 1

    print()
    print(aggregate_summary(catalogs))
    if failures:
        print()
        print(f"{len(failures)} failure(s):", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())