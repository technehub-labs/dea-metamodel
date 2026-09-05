"""Fetch + cache layer for the cross-repo consumer.

The cross-repo consumer contract (CR-CATALOG-STRUCT-07, §9) says a
consumer MUST read catalogs by fetching
`https://raw.githubusercontent.com/technehub-labs/<repo>/main/CATALOG.yaml`.

This module wraps `urllib.request.urlopen` with:

- A pluggable timeout (default 15s; long enough for cold-start latency,
  short enough to fail CI in under 30s).
- A pluggable cache directory (`set_cache_dir(...)`); fetched bytes
  are written as `<cache>/<repo>.yaml` keyed by `<repo>@<ref>`. The
  consumer can opt into local-only mode (`offline=True`) for testing.
- A `CredentialStrippingFetcher` (already used in the regenerator via
  `urllib.parse` userinfo stripping) is NOT needed here: `raw.githubusercontent.com`
  is the public read-only endpoint and never carries credentials. The
  contract in §9 explicitly says to fetch from `raw.githubusercontent.com`,
  not from authenticated `git@github.com:` URLs.

This module is HTTP-fetch-only; it does not parse YAML. The caller is
expected to pass the bytes to `catalog.parse_catalog_yaml`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Public endpoint per the standard (§9 step 1).
DEFAULT_RAW_BASE = (
    "https://raw.githubusercontent.com/technehub-labs/{repo}/{ref}/CATALOG.yaml"
)

DEFAULT_TIMEOUT_S = 15.0


@dataclass(frozen=True)
class FetchResult:
    """One fetch attempt's outcome.

    `bytes` is the raw YAML payload. `from_cache` distinguishes a fresh
    fetch from a cache hit (useful for diagnostics in the viewer / CLI).
    """

    repo: str
    ref: str
    bytes: bytes
    from_cache: bool


def _cache_path(cache_dir: Path, repo: str, ref: str) -> Path:
    """Filename-safe path for a cached fetch. Refs with slashes are
    flattened to '_' so the cache stays a flat directory."""
    safe_ref = ref.replace("/", "_")
    return cache_dir / f"{repo}@{safe_ref}.yaml"


def fetch_catalog_yaml(
    repo: str,
    *,
    ref: str = "main",
    cache_dir: "Path | str | None" = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    offline: bool = False,
) -> FetchResult:
    """Fetch `CATALOG.yaml` for a single catalog repo.

    Args:
        repo: Catalog repo name without orgs prefix (e.g.
            `"dea-catalog-processes"`). Fetches from
            `technehub-labs/<repo>` on the public read-only endpoint.
        ref: Branch / tag / SHA. Defaults to `"main"`.
        cache_dir: If provided, fetched bytes are written here keyed by
            `<repo>@<ref>.yaml`. Subsequent calls with the same args
            return the cached bytes without a network round-trip.
        timeout_s: HTTP timeout (seconds). Default 15.
        offline: If True, do NOT perform a network fetch. Instead,
            raise `FileNotFoundError` if the cache does not contain
            the requested `<repo>@<ref>.yaml`. Used by tests and by
            consumers running in sandboxed environments.

    Returns:
        FetchResult with the raw YAML bytes.

    Raises:
        urllib.error.URLError: Network error or non-2xx response.
        FileNotFoundError: `offline=True` and the cache misses.
    """
    import urllib.request

    if cache_dir is not None:
        cache_dir = Path(cache_dir)  # accept str | Path
        cached = _cache_path(cache_dir, repo, ref)
        if cached.is_file():
            return FetchResult(repo=repo, ref=ref, bytes=cached.read_bytes(), from_cache=True)

    if offline:
        raise FileNotFoundError(
            f"offline=True and cache miss for {repo}@{ref} "
            f"(cache_dir={cache_dir})"
        )

    url = DEFAULT_RAW_BASE.format(repo=repo, ref=ref)
    with urllib.request.urlopen(url, timeout=timeout_s) as resp:  # noqa: S310
        payload = resp.read()

    if cache_dir is not None:
        cache_dir = Path(cache_dir)  # accept str | Path
        _cache_path(cache_dir, repo, ref).write_bytes(payload)

    return FetchResult(repo=repo, ref=ref, bytes=payload, from_cache=False)


def fetch_many(
    repos: Iterable[str],
    *,
    ref: str = "main",
    cache_dir: "Path | str | None" = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    offline: bool = False,
) -> list[FetchResult]:
    """Fetch `CATALOG.yaml` for many repos.

    Fetches sequentially (urllib is single-threaded by default and
    parallel fetches can hammer `raw.githubusercontent.com`). Returns
    results in the same order as the input.
    """
    return [
        fetch_catalog_yaml(
            r,
            ref=ref,
            cache_dir=cache_dir,
            timeout_s=timeout_s,
            offline=offline,
        )
        for r in repos
    ]


__all__ = [
    "DEFAULT_RAW_BASE",
    "DEFAULT_TIMEOUT_S",
    "FetchResult",
    "fetch_catalog_yaml",
    "fetch_many",
]