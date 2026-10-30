# CR-MET-016: Waves 2-4 Boundary Lifecycle Sync

| Field | Value |
|---|---|
| **CR** | CR-MET-016 |
| **Title** | Waves 2-4 boundary: lifecycle corrections and viewer registration for the org-wide catalog advancement programme |
| **Status** | Proposed (this PR) |
| **Target repository** | `technehub-labs/dea-metamodel` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-02 |
| **Depends on** | CR-MET-014 (rules), CR-MET-015 (wave-1 boundary) |
| **Trigger** | Programme closure. Waves 2-4 advanced 21 repositories to the reputable-foundation standard (kit: pointer + schema + gates 1-6 + three CI workflows + FOUNDATIONS/RECORD-STANDARD), created 3, and observed owner-side population of a 22nd. |

## 1. Lifecycle changes

| Entity | From | To | Observation |
|---|---|---|---|
| dea:Tenet | scaffold | existing | dea-catalog-tenets populated by the owner-side CR-TEN series (8 canonical records; observed after this programme's own kit was superseded by the owner's series) |
| dea:FinancialResource | proposed | scaffold | dea-catalog-financial-resources created + kitted (CR-FR-CAT-01) |
| dea:IntangibleResource | proposed | scaffold | dea-catalog-intangible-resources created + kitted (CR-INR-CAT-01) |
| dea:PhysicalResource | proposed | scaffold | dea-catalog-physical-resources created + kitted (CR-PHR-CAT-01) |

## 2. Viewer registration

`KNOWN_CATALOG_REPOS` +21 (all wave 2-4 repositories that carry the CATALOG.yaml index discipline). dea-catalog-tenets joins when its owner-side layout adopts the index (their follow-up).

## 3. Findings named during waves 2-4 (follow-ups, not fixed here)

1. **Owner-parallel development:** organizational-units, stakeholders, metrics, application-components, system-functions, and blueprints carry active owner-side CR series (records present; some indexes stale). Left to the owner; the governance register records their states.
2. **Alias drifts (metamodel vs root model v0.8.0):** IntegrationInterface IFI (metamodel) vs IF (root model); ArchitecturePattern PAT vs AP. The pointers follow the root model (the allocation validator's authority); a metamodel-side reconciliation CR should follow.
3. **Discriminators absent from the metamodel:** pattern_kind, signal_kind, technology_kind are declared only in the root model; the metamodel entity records carry no discriminator fields.
4. **Metamodel schema defects:** tenet.json's over-escaped version pattern (normalized in catalog projections by the kit generator); 25 entities still lack schemas (derived projections flagged).
5. **CR series numbering collision:** dea-catalog-metrics uses CR-MET-NN numbering that collides lexically with this repository's CR-MET series (different repos; register notes it).

## 4. Regenerated

metamodel/registry/*, specification/* (lifecycle values only); 369 conformance tests green.

## 5. NOT-list

1. No entity definitions, artifacts declarations, or catalog_repo pointers change.
2. No owner-active repository is modified.
3. Viewer/Puml/SVG regeneration stays upstream-pinned (CR-MET-014 finding 4).
