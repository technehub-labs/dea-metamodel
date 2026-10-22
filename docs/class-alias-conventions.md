# Class Alias Conventions

The `class_alias` on every entity in `metamodel/dea-metamodel.yaml` is a short
rendering key used by the viewer and by the PUML renderer. The viewer graph
schema constrains it to five characters, and the viewer keys nodes on it, so an
alias is a **consumed interface value**, not a label.

This document records why the conventions below exist so that a future alias is
chosen deliberately rather than by first letters.

## Two namespaces, and they never meet

| Namespace | Shape | Owner | Example |
|---|---|---|---|
| Entity alias | 1-5 characters, uppercase | `dea-metamodel` | `MTR` for `dea:PerformanceMetric` |
| Catalogue record id | colon-namespaced, full words | `dea-catalog-*` | `dea:metric-mean-time-to-recovery` |

A catalogue record never needs an entity alias, and an entity alias never
becomes a record id. This is the structural reason the MTTR hazard below does
not reach the metamodel.

## Rule 1: an alias is entity-scoped, never a business abbreviation

The failure this prevents is concrete. The catalogue record
`dea:metric-mean-time-to-recovery` defines its formula as:

```
MTTR = (sum_i RecoveryTime_i) / n
```

`MTTR` already means *Mean Time to Recovery* in the wild. It is equally the
natural abbreviation for *Mean Time to Repair* and for *Mean Time to Respond*.
Three records could each bind `MTTR` locally to a different quantity and
nothing would detect it.

Because record ids are colon-namespaced and aliases are entity-scoped, the
metamodel alias layer cannot and does not see that collision. The defence is a
separate rule in `dea-catalog-*` (`check_formula_namespace.py`): a formula's
left-hand variable is bound to its record id, and the short form is permitted
only as a declared local binding. Disambiguation comes from the namespace, not
from the spelling, so `MTTR` is unambiguous without renaming it.

**Consequence for metamodel aliases:** never mint an alias from a business or
industry acronym. `MTR` is *Metric*, not *Mean Time to Repair*, and the rule is
what keeps the two apart.

## Rule 2: two to four characters, role-qualified, never bare initials

Naive acronym derivation was tested against the ten Metric entities and fails:

| Entity | Naive acronym | Problem |
|---|---|---|
| Baseline | `B` | single letter, no meaning |
| Threshold | `T` | single letter, no meaning |
| Provenance | `P` | single letter, no meaning |
| Correlation | `C` | single letter, no meaning |
| PerformanceTarget | `PT` | visually collides conceptually with PerformanceMetric (`MTR`) |

The adopted form is a distinct stem plus a role suffix, so each alias reads as a
word fragment that cannot be mistaken for another entity's stem:

| Entity | Alias | Entity | Alias |
|---|---|---|---|
| IndicatorDesignation | `IDS` | ReportingPeriod | `RPT` |
| Baseline | `BSL` | Provenance | `PRV` |
| PerformanceTarget | `PTG` | AnalyticalResult | `ANR` |
| Threshold | `THR` | PerformanceInterpretation | `PIT` |
| CausalHypothesis | `CSH` | Correlation | `COR` |

`PTG` rather than `PT`, and `PIT` rather than `PI`, because the unsuffixed forms
are exactly the ones that invite confusion with `PerformanceMetric`.

## Rule 3: uniqueness is global and enforced

Uniqueness is checked across the whole metamodel, not per family, so a metric
alias can never collide with a kernel alias.

This rule was not theoretical. `InvestmentInitiative` and `IntegrationInterface`
both carried `II`. Resolution was decided by which binding the **consumed**
artefact uses, not by which entity is older: `viewer/entity-graph.json` binds
`II` to `dea:entity-investment-initiative`, and `dea:IntegrationInterface` is not
allocated in the pinned upstream model at all. So `InvestmentInitiative` keeps
`II` and `IntegrationInterface` became `IFI`, which also follows the existing
`IFC` / `IGC` / `ISC` family convention.

The viewer artefact is the source of truth for a binding. Entity age is not.

## Rule 4: an alias may be absent, but never wrong

94 entities carry no alias, and that is acceptable: absence renders as the
display name. A wrong alias renders as a collision or an ambiguity, which is
worse than absence. Assign when a binding is actually needed.

## Enforcement

`check_alias_uniqueness` in `.github/scripts/validate_artifacts.py` fails when:

- two entities share a `class_alias`, or
- a `class_alias` exceeds the viewer's five-character cap.

It runs in CI under the artifact drift ratchet, and the full report is republished
hourly by `artifact-drift-watch.yml`. The category is baselined at zero, so any
future collision is an immediate failure rather than a backlog entry.

Verified by negative test: reintroducing `II` on `IntegrationInterface` moves the
count 0 to 1 and fails the gate.

## Worked example: what to do when an alias is needed

1. Split the entity name into camelCase words. Do not stop there.
2. Take a distinct stem per word, then suffix each with its role
   (`PerformanceTarget` becomes `PTG`, not `PT`).
3. Confirm the result is two to four characters and does not appear in the
   69-alias inventory.
4. If the entity represents a business quantity that has common industry
   abbreviations, prefer **no alias** and let the display name render. The alias
   space is for entity kinds, not for measures.