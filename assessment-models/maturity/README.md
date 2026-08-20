# Maturity Scoring v2 — Renames, Non-Linear Bands, Effort Multipliers

> The canonical **v2 maturity scoring scheme** for OpenDEA. Establishes new names, non-linear band widths, and explicit per-level effort multipliers. Lands as a sibling to v1 (CMMI names, linear bands). v1 remains canonical until Phase D promotion.

## 1. Context

The current five-level model (Ad Hoc / Defined / Managed / Quantitatively Managed / Optimising) is inherited from CMMI-era vocabulary and uses a 0–100 scale split into bands of 25/25/25/15/10 points.

Two structural criticisms:

1. **Archaic naming.** The names describe 1990s software-process culture, not modern engineering organisations. "Quantitatively Managed" in particular is a barrier to adoption outside process-improvement circles.

2. **Linear presentation hides diminishing returns.** Capability maturity exhibits two crossing curves:
   - **Effort is superlinear** (roughly exponential): each level costs disproportionately more organisational effort than the previous. L1→L2 is documentation; L3→L4 requires metrics infrastructure and instrumented pipelines; L4→L5 requires cultural and feedback-loop rewiring.
   - **Value is sublinear** (roughly logarithmic): the largest outcome gains come early (L1→L3 eliminates chaos and establishes repeatability). L4→L5 gains are real but marginal — optimisation at the edges.

The narrowing top bands in v1 already encode this *implicitly*. v2 makes it *explicit and computable*.

### Caveats (model honesty)

- Returns are not monotonic everywhere. Some transitions unlock **compounding** returns (crossing into measured, SLO-driven operations enables automation that accelerates everything below). These are documented per level as `inflection` notes, not treated as violations.
- Maturity is multi-axis. Diminishing returns apply per domain; portfolio allocation across domains is a separate concern (out of scope).

---

## 2. Level names (v2)

| Level | v1 name (legacy) | v2 name | Rationale |
|-------|------------------|---------|-----------|
| 1 | Ad Hoc | **Emergent** | Practice exists but is person-dependent and informal |
| 2 | Defined | **Structured** | Documented, agreed, but inconsistently enforced |
| 3 | Managed | **Systematic** | Formal, tooling-enabled, governance active |
| 4 | Quantitatively Managed | **Adaptive** | Metrics-driven; organisation senses and responds |
| 5 | Optimising | **Self-Optimising** | Continuous improvement is autonomous, not programme-driven |

Design rules:
- Single word per level (current set mixes 1–3 words; inconsistent in charts/CLI).
- All adjectives describing *the organisation's state*, not the process regime.
- No acronym collision with existing DEA catalogue vocabulary.

---

## 3. Scoring bands (v2)

Band width now explicitly represents **effort-to-traverse**, not linear progress:

| Level | Name | Range | Width | Effort Multiplier |
|-------|------|-------|-------|-------------------|
| 1 | Emergent | 0–20 | 20 | 1.0× |
| 2 | Structured | 21–45 | 25 | 1.5× |
| 3 | Systematic | 46–70 | 25 | 2.5× |
| 4 | Adaptive | 71–88 | 18 | 4.0× |
| 5 | Self-Optimising | 89–100 | 12 | 6.0× |

Rationale:
- L1 shrinks (25→20): escaping chaos is high-value, comparatively low-effort. A small score band reflects how quickly this should happen if leadership commits.
- L4/L5 narrow further (15→18/12 distribution shifts): each point at the top costs more to earn; fewer points available signals diminishing headroom.
- **Effort multiplier** is the relative organisational cost of earning one point *within* that band, normalised to L1 = 1.0×. Multipliers are superlinear (1.0 → 1.5 → 2.5 → 4.0 → 6.0), consistent with the exponential effort curve.

The band boundaries sum to 100; the bands are contiguous and non-overlapping. The canonical machine-readable form lives in [`maturity-bands-v2.yaml`](maturity-bands-v2.yaml).

---

## 4. Effort-adjusted value (computable ROI signal)

Raw score answers "where are we?" It does not answer "was it worth it, and what's the next marginal point worth?" The effort multiplier enables a second computed metric:

```
value_realised(score) = Σ over bands b:  points_earned_in(b) / effort_multiplier(b)
```

Worked example — an organisation scoring 80 (Adaptive):

| Band | Points earned | Multiplier | Value units |
|------|---------------|------------|-------------|
| Emergent | 20 | 1.0 | 20.0 |
| Structured | 25 | 1.5 | 16.7 |
| Systematic | 25 | 2.5 | 10.0 |
| Adaptive | 10 | 4.0 | 2.5 |
| **Total** | **80 (raw)** | | **49.2 (effort-adjusted)** |

Interpretation for tooling and governance dashboards:
- **Raw score** (80/100) — capability position, comparable across domains.
- **Effort-adjusted value** (49.2) — diminishing-returns curve made visible: the last 10 points delivered 2.5 value units; the first 20 delivered 20.
- **Marginal point cost** at Adaptive = 4.0× baseline → next-point ROI can be compared *across domains* (raising Operations from 68→70 costs 2.5×/point; raising Technology from 44→46 crosses into Systematic at 2.5×/point) — this is the portfolio-allocation signal the current model cannot produce.

The full worked-example YAML is at [`examples/effort-adjusted-value.yaml`](examples/effort-adjusted-value.yaml).

---

## 5. Migration plan (4 phases)

Per the additive-migration rule:

| Phase | What ships | Status |
|-------|-----------|--------|
| **A — registry** | `maturity-bands-v2.yaml` published as advisory alongside v1 | ✅ this PR |
| **B — beta files** | v2 maturity model files with `legacy_name` aliases; consumer tooling reads v1 by default | ✅ this PR (band YAML + legacy-name map + worked example) |
| **C — consumers** | dea-cli gains `--scoring v2`; dea-web-viewer renders both band sets behind a feature flag; assessment-tools mappings updated | future CRs in `technehub-labs/dea-cli`, `technehub-labs/dea-web-viewer`, `Assessment-Models/dea-catalog-assessment-tools` (archived, but consumers can mirror locally) |
| **D — promotion** | After one full assessment cycle on v2, v2 becomes canonical; v1 deprecated with `superseded-by` link | future CR |

No model content (characteristics, exit criteria, evidence) changes in this proposal — only names, bands, and scoring metadata.

---

## 6. Backward compatibility

- v1 ids (`level-1-ad-hoc` etc.) remain valid forever in v1-alpha files.
- `legacy_name` alias on every v2 level lets existing assessment data resolve. See [`v2-to-v1-legacy-name-map.yaml`](v2-to-v1-legacy-name-map.yaml).
- Band boundary change (25→20, etc.) is a **scoring change**, not a data change; historical raw scores remain meaningful because underlying assessment answers are unchanged — only the band they map to shifts. dea-cli will report both mappings during the transition window.

---

## 7. Where this fits in CR-014

This sub-tree is part of the [assessment sub-metamodel landing](../../change-requests/CR-014.md). The v2 maturity scoring scheme is the maturity-model-interpretation layer for the assessment sub-metamodel: a result can be `interpreted-by` a MaturityModel (v1 or v2 — both are valid MaturityModel references per CR-AM-01 §13).

---

## 8. Cross-references

- Historical proposal (archived repo, read-only): https://github.com/Assessment-Models/dea-catalog-maturity-models/pull/1
- CR-014 (parent CR): [`../../change-requests/CR-014.md`](../../change-requests/CR-014.md)
- CR-AM-01 (parent CR for the assessment sub-metamodel evolution): https://github.com/Assessment-Models/dea-catalog-assessment-tools/blob/main/change-requests/CR-AM-01.md
- Canonical machine-readable form: [`maturity-bands-v2.yaml`](maturity-bands-v2.yaml)
- Legacy-name map: [`v2-to-v1-legacy-name-map.yaml`](v2-to-v1-legacy-name-map.yaml)
- Worked example: [`examples/effort-adjusted-value.yaml`](examples/effort-adjusted-value.yaml)
- Migration governance: [`governance/migration.md`](governance/migration.md)