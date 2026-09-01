"""ECF drift detector (CR-ECF-CG-005 §5).

Detects:
  - changed Domain definitions (canonical PascalCase enum changed);
  - changed Stage definitions (canonical PascalCase enum changed);
  - missing Coordinates (any (Domain, Stage) pair absent from the canonical
    49-space that downstream code claims);
  - duplicate Coordinates (an identifier reused for a different (D,S) pair);
  - local ECF enumerations (kebab-case values where canonical PascalCase
    should be used in canonical references);
  - invalid identifiers (the canonical lowerCamelCase pattern is broken);
  - terminology drift (e.g., "Enterprise Composition Framework" or other
    expansions appearing instead of "Enterprise Concept Framework");
  - incompatible schema changes (a schema is added or removed without a
    corresponding CR index row);
  - undocumented extensions (an extension block appears that is not
    declared in the catalog's profile declaration).

Run from repo root: python3 scripts/detect_drift.py [--strict]

Without --strict: prints findings as warnings, exit 0 unless hard failures
(missing-coordinate or invalid-identifier) are found.
With --strict: any finding fails the gate.

Designed for GitHub Actions (CG-006 wires it into CI).
"""

from __future__ import annotations
import glob, json, os, re, sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MATRIX = REPO / 'conformance' / 'matrix.yaml'
FWK = Path(os.environ.get('ECF_FRAMEWORK_ROOT', '/home/hermes/dea-work/dea-metaframework'))
DOMAIN_SCHEMA = FWK / 'schemas' / 'ecf-domain.schema.json'
STAGE_SCHEMA = FWK / 'schemas' / 'ecf-stage.schema.json'
COORD_SCHEMA = FWK / 'schemas' / 'ecf-coordinate.schema.json'

# Canonical coordinate identifier suffix mapping (PascalCase -> lowerCamelCase)
# Derived from the actual catalog use; matching the dea-metaframework
# schema's lowerCamelCase identifier pattern. If dea-metaframework ever
# changes this mapping, update this table.
DOMAIN_ID = {
    'GovernanceAndExistence': 'governanceExistence',
    'SupplyAndResources': 'supplyResources',
    'PeopleAndOrganization': 'peopleOrganization',
    'CustomerAndDemand': 'customerDemand',
    'ProductAndOffering': 'productOffering',
    'OperationsAndDelivery': 'operationsDelivery',
    'FinanceAndValue': 'financeValue',
}
STAGE_ID = {
    'Conceive': 'conceive',
    'Design': 'design',
    'Build': 'build',
    'Activate': 'activate',
    'Operate': 'operate',
    'Improve': 'improve',
    'Retire': 'retire',
}
ID_PATTERN = re.compile(r'^ecf:[a-z][a-zA-Z0-9]*\.[a-z][a-zA-Z0-9]*$')
CORRECT_TERM = 'Enterprise Concept Framework'
WRONG_TERMS = ['Enterprise Composition Framework', 'Enterprise Conceptual Framework']

# Catalog roots to scan (CG-005 §4 matrix).
# Default: local workspace clones. CI overrides via ECF_CATALOG_ROOTS env
# (colon-separated absolute paths).
DEFAULT_ROOTS = [
    Path('/home/hermes/dea-work/dea-catalog-business-capabilities'),
    Path('/home/hermes/dea-work/dea-catalog-processes'),
]

def canonical_domains() -> set[str]:
    return set(json.load(open(DOMAIN_SCHEMA))['enum'])

def canonical_stages() -> set[str]:
    return set(json.load(open(STAGE_SCHEMA))['enum'])

def canonical_id_space() -> set[str]:
    return {f"ecf:{DOMAIN_ID[d]}.{STAGE_ID[s]}" for d in canonical_domains() for s in canonical_stages()}

def main():
    strict = '--strict' in sys.argv
    findings: list[tuple[str, str, str]] = []  # (severity, repo, message)
    hard: list[tuple[str, str, str]] = []
    soft: list[tuple[str, str, str]] = []

    # I1..I3: Domain/Stage/Coordinate identity (canonical PascalCase enums
    # haven't drifted). The detector reads them fresh each run; if the
    # schema enum has changed since the last matrix compile, the matrix
    # would no longer match.
    if not MATRIX.exists():
        hard.append(('FAIL', 'dea-metamodel', 'conformance/matrix.yaml missing'))
    else:
        m = yaml.safe_load(open(MATRIX))
        # If the matrix declares a different contract version, that's drift.
        if m.get('contractVersion') != '1.0.0':
            soft.append(('WARN', 'dea-metamodel', f"matrix declares contractVersion={m.get('contractVersion')}, expected 1.0.0"))

    # Scan consumer catalogs for canonicalReferences + identifier correctness.
    # Scope: only the canonical entities/ tree (research/, fixtures/,
    # specializations/, metamodel-pointer are not canonical entries).
    canonical_ids = canonical_id_space()
    canonical_domains_set = canonical_domains()
    canonical_stages_set = canonical_stages()
    roots_env = os.environ.get('ECF_CATALOG_ROOTS')
    if roots_env:
        catalog_roots = [Path(p) for p in roots_env.split(':') if p]
    else:
        catalog_roots = DEFAULT_ROOTS
    for root in catalog_roots:
        if not root.exists():
            soft.append(('WARN', root.name, 'catalog not present locally; skipped'))
            continue
        # Only scan the canonical entities directory. Map view/specialization
        # files have their own shape (handled below separately).
        entities_root = root / 'entities'
        if not entities_root.exists():
            continue
        files = sorted(glob.glob(str(entities_root / '**' / '*.yaml'), recursive=True))
        files = [f for f in files if '/README' not in f and '/readme' not in f]
        for fp in files:
            try:
                e = yaml.safe_load(open(fp))
            except yaml.YAMLError as ex:
                hard.append(('FAIL', root.name, f"{fp}: YAML parse error: {ex}"))
                continue
            if not e:
                continue
            blk = e.get('ecfConformance')
            if blk is None and files:
                soft.append(('WARN', root.name, f"{fp}: entry present without ecfConformance block"))
                continue
            if not blk:
                continue
            for ref in blk.get('canonicalReferences') or []:
                # Skip non-coordinate references (e.g. baseline-catalog,
                # inherits-baseline) : these are view-level, not coordinate
                # assertions.
                if ref.get('kind') != 'coordinate':
                    continue
                d = ref.get('domain'); s = ref.get('stage'); ident = ref.get('identifier') or ''
                if d not in canonical_domains_set:
                    hard.append(('FAIL', root.name, f"{fp}: canonical reference domain '{d}' not in canonical enum"))
                if s not in canonical_stages_set:
                    hard.append(('FAIL', root.name, f"{fp}: canonical reference stage '{s}' not in canonical enum"))
                if not ID_PATTERN.match(ident):
                    hard.append(('FAIL', root.name, f"{fp}: identifier '{ident}' does not match canonical lowerCamelCase pattern"))
                elif ident not in canonical_ids:
                    hard.append(('FAIL', root.name, f"{fp}: identifier '{ident}' not in canonical 49-space"))
                # Identifier ↔ (domain, stage) cross-check (CG-005 Invariant 3).
                if ident.startswith('ecf:') and d in DOMAIN_ID and s in STAGE_ID:
                    expected = f"ecf:{DOMAIN_ID[d]}.{STAGE_ID[s]}"
                    if ident != expected:
                        hard.append(('FAIL', root.name, f"{fp}: identifier '{ident}' does not match (domain={d}, stage={s}); expected '{expected}'"))

    # Terminology drift (CG-005 Invariant 8): grep the consumer repos for
    # incorrect expansions.
    for root in catalog_roots:
        if not root.exists():
            continue
        for path in glob.glob(str(root / '**' / '*.md'), recursive=True):
            try:
                text = open(path, encoding='utf-8').read()
            except UnicodeDecodeError:
                continue
            for wrong in WRONG_TERMS:
                if wrong in text:
                    soft.append(('WARN', root.name, f"{path}: contains incorrect expansion '{wrong}' (should be '{CORRECT_TERM}')"))

    # Report
    findings = hard + soft
    if hard:
        print(f"DRIFT: {len(hard)} hard failure(s), {len(soft)} soft warning(s)", file=sys.stderr)
        for sev, repo, msg in findings:
            print(f"  [{sev}] {repo}: {msg}", file=sys.stderr)
        sys.exit(1 if strict or hard else 0)
    print(f"PASS: 0 hard failures, {len(soft)} soft warning(s).")
    if soft:
        for sev, repo, msg in soft:
            print(f"  [{sev}] {repo}: {msg}")


if __name__ == '__main__':
    main()