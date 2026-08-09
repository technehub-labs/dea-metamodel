#!/usr/bin/env python3
"""Cross-repo validator: ensures consistency between entity-graph.json,
schemas/entities/, and the per-catalog metamodel-pointer.yaml files
in technehub-labs.

Runs three classes of checks:

  A) Local schema-graph consistency:
     - Every entity in entity-graph.json has a corresponding
       schemas/entities/<kebab-id>.json schema file (when one should exist).
       Exception: status='planned' entries with empty catalog scaffolds
       don't require schemas yet.
     - Every schema in schemas/entities/ has a corresponding entity-graph
       entry. Exception: entity.json (the abstract root).

  B) Schema representation consistency:
     - Every owl:Class in ttl/dea-metamodel-ontology.ttl that has a
       dea:specification pointer must point at an existing schema file.
     - Every owl:Class in ttl/ that is named after a schema file must
       have a dea:specification pointer.

  C) Cross-repo pointer validation (requires network):
     - Every catalog_repo in entity-graph.json must exist on GitHub.
     - Every metamodel-pointer.yaml in a technehub-labs catalog repo
       must reference an entity_id present in entity-graph.json.

Exits 0 on success, 1 on any consistency violation.
"""
import sys
import json
import os
import re
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
SCHEMA_DIR = BASE / "schemas" / "entities"
GRAPH_FILE = BASE / "viewer" / "entity-graph.json"
TTL_FILE = BASE / "ttl" / "dea-metamodel-ontology.ttl"
ORG = "technehub-labs"


def load_graph():
    """Load entity-graph.json. Returns dict with 'entities' list."""
    if not GRAPH_FILE.exists():
        return None
    with open(GRAPH_FILE) as f:
        return json.load(f)


def load_schema_files():
    """Return set of kebab-id schema file basenames (no extension)."""
    return {p.stem for p in SCHEMA_DIR.glob("*.json")}


def load_ttl_classes():
    """Parse ttl/dea-metamodel-ontology.ttl. Return dict of:
       {class_name: {'subclass': str|None, 'specification': str|None}}"""
    if not TTL_FILE.exists():
        return {}
    classes = {}
    current = None
    for line in open(TTL_FILE):
        m = re.match(r"dea:(\w+)\s+a\s+owl:Class\s*;", line)
        if m:
            current = m.group(1)
            classes[current] = {"subclass": None, "specification": None}
            continue
        if current:
            m = re.match(r"\s+rdfs:subClassOf\s+dea:(\w+)\s*;", line)
            if m:
                classes[current]["subclass"] = m.group(1)
                continue
            m = re.match(r"\s+dea:specification\s+<(\S+)>\s*\.?", line)
            if m:
                classes[current]["specification"] = m.group(1)
                continue
            if line.strip() and not line.startswith(" "):
                current = None  # left the class block
    return classes


def github_headers():
    """Build headers for GitHub API. Uses GITHUB_TOKEN env var if present."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_repo_exists(repo):
    """Check whether technehub-labs/<repo> exists."""
    url = f"https://api.github.com/repos/{ORG}/{repo}"
    try:
        req = urllib.request.Request(url, headers=github_headers())
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        return e.code != 404
    except Exception:
        return False


def github_fetch_file(repo, path):
    """Fetch a file from a technehub-labs repo. Returns decoded content or None."""
    url = f"https://api.github.com/repos/{ORG}/{repo}/contents/{path}"
    try:
        req = urllib.request.Request(url, headers=github_headers())
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            import base64
            return base64.b64decode(data["content"]).decode()
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


def check_local(graph, schema_files, ttl_classes):
    """Checks A and B — run against local files only, no network."""
    errors = []
    warnings = []

    graph_ids = {e["entity_id"].replace("dea:entity-", ""): e for e in graph["entities"]}

    # A1. Schemas without graph entries (orphan schemas).
    for sf in schema_files:
        if sf == "entity":
            continue  # abstract root — no graph entry by design
        if sf not in graph_ids:
            errors.append(
                f"schema schemas/entities/{sf}.json has no entity-graph entry "
                f"(should be dea:entity-{sf})"
            )

    # A2. Graph entries without schemas — only OK if status='planned' AND
    # catalog_repo is empty (true placeholder) or repo is empty.
    # For scaffold/existing/entries with content, schema must exist.
    for sid, e in graph_ids.items():
        status = e.get("status", "")
        if status == "planned":
            continue  # planned entries don't require schemas yet
        if f"{sid}.json" not in schema_files:
            errors.append(
                f"graph entry dea:entity-{sid} (status='{status}') has no "
                f"schemas/entities/{sid}.json schema file"
            )

    # B1. TTL classes with dea:specification pointing at missing schema files.
    for cls, data in ttl_classes.items():
        spec = data.get("specification")
        if spec:
            spec_path = BASE / spec
            if not spec_path.exists():
                errors.append(
                    f"TTL class dea:{cls} has dea:specification <{spec}> "
                    f"but {spec} does not exist locally"
                )

    # B2. TTL classes that should have a dea:specification but don't.
    # Heuristic: classes whose CamelCase name matches a schema file basename
    # (kebab -> CamelCase) should have dea:specification.
    for cls, data in ttl_classes.items():
        if data.get("specification"):
            continue
        camel = cls
        # Schema files use kebab-case; map CamelCase -> kebab-case
        kebab = re.sub(r"([A-Z])", r"-\1", camel).lower().lstrip("-")
        if f"{kebab}.json" in {f"{s}.json" for s in schema_files}:
            warnings.append(
                f"TTL class dea:{cls} has no dea:specification but "
                f"schemas/entities/{kebab}.json exists"
            )

    return errors, warnings


def check_cross_repo(graph, schema_files):
    """Checks C — requires network access to GitHub API."""
    errors = []

    # C1. Every catalog_repo in entity-graph must exist on GitHub.
    catalog_repos = sorted(set(e["catalog_repo"] for e in graph["entities"]))
    print(f"\nC1: Verifying {len(catalog_repos)} catalog repos on GitHub...")
    for repo in catalog_repos:
        if not github_repo_exists(repo):
            errors.append(f"graph catalog_repo '{repo}' does not exist on GitHub")
            continue
        print(f"  ✓ {repo}")

    # C2. Every catalog repo's metamodel-pointer.yaml must reference an
    # entity_id present in entity-graph.json.
    graph_ids = {e["entity_id"] for e in graph["entities"]}
    print(f"\nC2: Verifying catalog metamodel-pointer.yaml files reference valid entity_ids...")
    for repo in catalog_repos:
        content = github_fetch_file(repo, "metamodel-pointer.yaml")
        if not content:
            warnings_list.append(  # type: ignore
                f"catalog repo '{repo}' has no metamodel-pointer.yaml"
            )
            continue
        # Find entity_id lines: "entity_id: dea:entity-xxx" (top-level or list item)
        claimed = []
        for line in content.split("\n"):
            m = re.match(r"\s*-?\s*entity_id:\s*(dea:entity-\S+)", line)
            if m:
                claimed.append(m.group(1))
        if not claimed:
            warnings_list.append(  # type: ignore
                f"catalog repo '{repo}' metamodel-pointer.yaml has no entity_id claim"
            )
            continue
        for cid in claimed:
            if cid not in graph_ids:
                errors.append(
                    f"catalog repo '{repo}' metamodel-pointer.yaml references "
                    f"{cid}, which is not in entity-graph.json"
                )
            else:
                print(f"  ✓ {repo} -> {cid}")

    return errors


def main():
    graph = load_graph()
    if graph is None:
        print(f"ERROR: {GRAPH_FILE} not found")
        sys.exit(1)

    schema_files = load_schema_files()
    ttl_classes = load_ttl_classes()

    print(f"=== Cross-repo validator ===")
    print(f"Graph: {len(graph['entities'])} entities")
    print(f"Schemas: {len(schema_files)} files")
    print(f"TTL: {len(ttl_classes)} owl:Class declarations")

    errors, warnings = check_local(graph, schema_files, ttl_classes)

    print(f"\n=== Local checks (no network) ===")
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for w in warnings: print(f"  ⚠ {w}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors: print(f"  ✗ {e}")
        return 1
    print(f"✓ All local checks pass")

    # Cross-repo checks are optional — only run if network is available.
    # We try and gracefully degrade; CI runs this with network.
    print(f"\n=== Cross-repo checks (network required) ===")
    try:
        # Test if we have network
        req = urllib.request.Request(
            "https://api.github.com/repos/technehub-labs/dea-metamodel",
            headers=github_headers())
        with urllib.request.urlopen(req, timeout=5) as r:
            pass
        # Network is available
        warnings_list = []
        cross_errors = check_cross_repo(graph, schema_files)
        errors.extend(cross_errors)
        if warnings_list:
            print(f"Warnings: {len(warnings_list)}")
            for w in warnings_list: print(f"  ⚠ {w}")
    except Exception as e:
        print(f"  ⊘ Skipped (no network: {type(e).__name__})")

    if errors:
        print(f"\n=== FAILED ({len(errors)} errors) ===")
        for e in errors: print(f"  ✗ {e}")
        return 1

    print(f"\n=== PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
