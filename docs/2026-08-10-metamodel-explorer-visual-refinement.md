# DEA Metamodel Explorer — Visual Refinement Plan

> **For Hermes:** Use subagent-driven-development skill to execute task-by-task.
> Source-of-truth hierarchy: GitHub > local origin/main > test-server tree > local docs > session memory.
> All changes must drift-check against `technehub-labs/dea-metamodel` `main` before merge.

**Goal:** Fix the 8 visual & drift issues on https://technehub-labs.github.io/metamodel/ so the diagram is readable, color-consistent with the rest of the org, and matches the canonical 33-entity / 30-relationship / 5-layer state of `dea-metamodel`.

**Architecture:** Three-axis changes:
1. **Diagram source** (`dea-metamodel/.github/scripts/generate_puml.py` + `metamodel-puml/metamodel-v2.puml`) — fix cluster fills, entity stroke colours, stereotype circles, aspect ratio.
2. **Pages host** (`technehub-labs.github.io/metamodel/index.html` + `viewer.js`) — fix drift (23→33 entities, 31→30 relationships, 6→5 layers), add `?entity=SO` deep-link.
3. **Sync workflow** (`dea-metamodel/.github/workflows/`) — verify regeneration pipeline produces the expected SVG.

**Tech Stack:** PlantUML 1.2024.7 (server-side), Python 3 (post-processing), vanilla HTML/CSS/JS (no framework).

---

## Diagnosis (verified against current artefacts)

| # | Issue | Evidence | Severity |
|---|---|---|---|
| 1 | Cluster fills have no contrast against `#080B10` page bg | L1 `#0D2620` contrast 1.23, L2 `#2E2010` 1.25, L3 `#0F1D2E` 1.16, L4 `#1F1735` 1.16, L5 `#2E1212` 1.14 (need ≥3:1) | 🔴 Critical |
| 2 | Attribute text `+ id : string` etc. is dim gray `#8B949E` 13px on `#0D1117` | Contrast 4.71 (passes AA but visually weak at 13px) | ⚠️ Warning |
| 3 | SVG is 2418×846 (aspect 2.86:1) → squished text when CSS scales to column | viewBox + `preserveAspectRatio="none"` causes horizontal stretch | 🔴 Critical |
| 4 | All entities are the same teal `#2DD4BF` regardless of layer | `entity-graph.json` per-entity `color` field is unused | 🔴 Critical (user-flagged color consistency) |
| 5 | `index.html` says **23 entities / 31 relationships / 6 layers** with 6 differently-named filter buttons; canonical is **33 / 30 / 5** | Stale scaffold, never updated when graph grew | 🔴 Critical (representational drift) |
| 6 | Stereotype ellipses are `#FFFFFF` with `#000000` "C" icon — breaks dark theme | SVG `<ellipse fill="#FFFFFF">` on dark theme | ⚠️ Warning |
| 7 | Relationship labels are very dim italic gray `#8B949E` 11–12px | SVG `<text font-style="italic" fill="#8B949E">` | ⚠️ Warning |
| 8 | Catalog repo READMEs link to `?entity=SO` deep-links but `viewer.js` doesn't parse URL params | `viewer.js` has no `URLSearchParams` / `selectEntity` reading | 💡 Suggestion (broken feature) |

**Plus one bonus consistency gap:**
9. Metaframework pages (`dea-metaframework/pages/`) use 7-colour ECF-domain palette; metamodel pages use 5-colour layer palette — these should align semantically where they overlap.

---

## Per-layer entity palette (Kimi K3 spec — adopted)

| Layer | Name | Hex | Stroke width | Accent bar | Contrast vs `#080B10` | Contrast vs `#0D1117` |
|---|---|---|---|---|---|---|
| L1 | Strategic & Investment | `#2DD4BF` teal | 1.5 | 3px | 10.57 | 10.10 |
| L2 | Business Operating Model | `#FBBF24` amber | 1.5 | 3px | 11.89 | 11.36 |
| L3 | Digital & Data | `#38BDF8` sky | 1.5 | 3px | 9.24 | 8.83 |
| L4 | Technical & Integration | `#A78BFA` violet | 1.5 | 3px | 7.23 | 6.91 |
| L5 | Measurement & Governance | `#FB7185` rose | 1.5 | 3px | 7.38 | 7.05 |

All ≥ 7:1 — exceeds 3:1 boundary requirement with ≥ 3.9:1 headroom on the weakest hue (L4). These are the existing CSS tokens `--l1..--l5` already defined in `viewer.css`. Do not introduce new hues.

**Fill rule (Kimi):** All entity rects use `--node-fill: #0D1117` (one neutral, all layers). Layer identity expressed only via **stroke + left accent bar + stereotype label** — never by tinted fill. Tinted fills at these hues fail contrast and look washed on `#080B10`.

---

## Edge / relationship styling

| Class | Use | Stroke | Width | Dash | Opacity |
|---|---|---|---|---|---|
| `rel-structural` | solid `--` (composition, ownership) | `#3D4B5C` | 1.5 | none | 1 |
| `rel-flow` | dotted `..` (data flow, classification, carries) | `#2DD4BF` | 1.5 | `4 3` | 0.8 |

Arrowheads: unfilled triangles, single direction. Edge labels: 11px `#8B98A5` (was `#8B949E`, brighten slightly), `paint-order: stroke` with 3px `#080B10` halo for legibility on dark bg.

---

## Task list

### Phase A — Fix diagram source (dea-metamodel)

#### Task 1: Fix cluster fill contrast against `#080B10`

**Objective:** Bump 5 cluster fills to ≥3:1 contrast against the page bg.
**Files:** `metamodel-puml/metamodel-v2.puml`

**Old → New:**
| Layer | Old | New | New contrast |
|---|---|---|---|
| L1 | `#0D2620` | `#163A36` | 3.18 ✓ |
| L2 | `#2E2010` | `#4A3712` | 3.12 ✓ |
| L3 | `#0F1D2E` | `#1A3A55` | 3.41 ✓ |
| L4 | `#1F1735` | `#33264D` | 3.05 ✓ |
| L5 | `#2E1212` | `#5A2B2B` | 3.08 ✓ |

(Sample values tuned against `#080B10` luminance. Final values to be verified against actual ratio during execution; target ≥ 3.0:1.)

Replace each `package "Layer N: …" #0D2620 {` line with the new hex. Also update the corresponding comment if present.

#### Task 2: Fix diagram aspect ratio (no more squish)

**Objective:** Make SVG close to 1.45:1 instead of 2.86:1 so text isn't horizontally stretched.
**Files:** `metamodel-puml/metamodel-v2.puml`, `.github/scripts/generate_puml.py`

**Step A:** In `.puml`, add to the `skinparam` block (top of file):
```
skinparam dpi 96
skinparam maxMessageSize 200
skinparam nodesep 80
skinparam ranksep 90
```
The current values (`nodesep 60`, `ranksep 60`) plus `linetype ortho` and `!theme plain` are causing PlantUML to lay the graph out on a single ultra-wide row. Larger `ranksep` forces more vertical separation.

**Step B:** In the SVG post-processing or in the PUML render command, set `!pragma layout elk` to use the ELK layout engine which produces more balanced (closer to square) layouts than the default GraphViz `dot`.

**Step C:** Verify the resulting SVG has `viewBox` width:height between 1.3:1 and 1.7:1. If still too wide, increase `nodesep` to 100.

#### Task 3: Per-layer entity stroke + accent bar

**Objective:** Each entity box stroked in its layer's `--lN` hex with a 3px left accent bar.
**Files:** `.github/scripts/generate_puml.py` (post-processing), `metamodel-puml/metamodel-v2.puml`

**Approach A (PUML):** In the PUML, define a `skinparam class` block per-layer via `class Foo #color` syntax. PlantUML supports per-class colour overrides:
```
class Foo #stroke:#2DD4BF
```
…but stroke alone doesn't give the accent-bar effect.

**Approach B (post-processing):** Keep PUML simple, do the per-layer stroke + accent bar injection in the Python post-processor that already exists (`inject_svg_attributes.py`). Add to that script:
1. Read entity-graph.json to map `class_alias → layer`.
2. For each `<g id="elem_X" class="entity" data-alias="X">`, find the inner `<rect fill="#0D1117" style="stroke:#2DD4BF;…">` and rewrite the stroke colour to the layer hex from the palette table above.
3. Insert a 3px-wide `<rect class="node-bar" fill="{layer-hex}" x="2" y="2" width="3" height="H-4">` immediately after the main rect, clipped to the rounded corner via a clipPath or just rendered as a small filled rectangle inset.
4. Change the stereotype ellipse `fill="#FFFFFF"` to `fill="{layer-hex}"` at 0.18 alpha (`{hex}2E`) and the "C" path inside to `fill="{layer-hex}"` at full alpha (or `#0D1117` for legibility).

#### Task 4: Attribute text legibility

**Objective:** Make `+ id : string` lines readable.
**Files:** `.github/scripts/inject_svg_attributes.py` (post-processing)

Bump attribute font-size from 13px to 13px (already at minimum readable), change `fill="#8B949E"` to `fill="#B1BAC4"` (contrast 7.95 against `#0D1117`, passes AAA). Add a 2px `paint-order: stroke` halo with `#0D1117` for text that crosses relationship lines.

#### Task 5: Relationship label legibility

**Objective:** Brighten italic relationship labels.
**Files:** `.github/scripts/inject_svg_attributes.py`

Change `fill="#8B949E"` on relationship `<text>` elements (the italic ones) to `fill="#B1BAC4"`, keep 11–12px, keep italic. Add 2.5px halo with `#080B10`.

---

### Phase B — Fix Pages host drift (technehub-labs.github.io)

#### Task 6: Replace 23/31/6-layer drift in index.html

**Objective:** Align the index.html chrome with the canonical 33/30/5 state.
**Files:** `metamodel/index.html`

Verbatim replacements:
- Nav badge `v3.0.0` → `v2.0.0-alpha`
- Nav badge `23 entities` → `33 entities`
- Nav badge `31 relationships` → `30 relationships`
- Nav badge `6 layers` → `5 layers`
- Diagram meta `23 entities · 31 relationships · 6 layers · click any class to inspect` → `33 entities · 30 relationships · 5 layers · click any class to inspect`
- Intro eyebrow `Six layers — ecosystem on top` → `Five layers — strategic intent to measurable outcome`
- Filter buttons (6 → 5, names must match `LAYER_NAMES` in viewer.js):
  ```
  L1 · Ecosystem  →  L1 · Strategic & Investment
  L2 · Strategic  →  L2 · Business Operating Model
  L3 · Business   →  L3 · Digital & Data
  L4 · Digital    →  L4 · Technical & Integration
  L5 · Technology →  L5 · Measurement & Governance
  L6 · Measurement → (delete)
  ```
  And inline `style="--c:#…"` per button must match the per-layer hex in the CSS:
  ```
  L1 → --c:#2dd4bf  (teal)
  L2 → --c:#fbbf24  (amber)
  L3 → --c:#38bdf8  (sky)
  L4 → --c:#a78bfa  (violet)
  L5 → --c:#fb7185  (rose)
  ```

#### Task 7: viewer.js URL-param deep-link

**Objective:** Make `?entity=SO` deep-links from catalog READMEs work.
**Files:** `metamodel/viewer.js`

Add after the constants block (around line 20):
```javascript
// Deep-link support: ?entity=SO selects + scrolls-to that entity on load.
function applyEntityDeepLink() {
  const params = new URLSearchParams(window.location.search);
  const target = (params.get('entity') || '').toUpperCase().trim();
  if (!target) return;
  // Wait for graph + diagram render before selecting.
  requestAnimationFrame(() => {
    const card = document.querySelector(`.entity-card[data-alias="${target}"]`);
    if (card) {
      card.click();                  // triggers selectEntity(...)
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      console.warn(`[metamodel] ?entity=${target} not found in graph`);
    }
  });
}
// Call once at end of init, after renderEntityGrid() finishes.
```

Hook the call after the existing `await fetch…` block where the entity grid is built. No new dependencies.

#### Task 8: viewer.css — accent-bar styling on entity cards

**Objective:** Make the per-layer identity visible in the entity-card grid (not just the SVG).
**Files:** `metamodel/viewer.css`

The CSS already has:
```css
.entity-card[data-layer="L1"]::before { background: var(--l1); }
… (L1–L5)
```
Good. Verify each layer maps to the correct hex (currently L1 `#2dd4bf`, L2 `#fbbf24`, L3 `#38bdf8`, L4 `#a78bfa`, L5 `#fb7185`) — these already match the table in Task 3. **No CSS change needed if already correct.** Add a verification step in Task 10.

#### Task 9: viewer.js — adopt the entity color from the graph

**Objective:** Use `entity.color` from the JSON when rendering the card (currently unused).
**Files:** `metamodel/viewer.js`

In the `renderEntityGrid()` function, when creating an entity card, set `card.style.setProperty('--card-accent', entity.color || 'var(--l' + layerNum + ')')`. Then in CSS, `.entity-card::before { background: var(--card-accent, var(--accent)); }`. This lets future per-entity colour overrides (when the JSON gets per-entity dark-theme hex) flow through automatically.

---

### Phase C — Verification

#### Task 10: Re-render SVG + sync to Pages

**Objective:** Make sure the new SVG lands on Pages.
**Files:** (no code change — workflow execution)

Steps:
1. Commit Task 1–5 changes to `dea-metamodel` on a `fix/metamodel-visual-refinement` branch.
2. Push → trigger `render-metamodel.yml` → produces new `viewer/metamodel.svg`.
3. Confirm new SVG passes `validate_svg_graph.py` (already in CI).
4. `notify-pages.yml` dispatches to Pages repo.
5. Wait for Pages cron to sync (or trigger manually via `gh workflow run`).
6. Verify `technehub-labs.github.io/metamodel/metamodel.svg` has updated timestamp and:
   - viewBox aspect ≤ 1.7:1
   - 33 entities, each with a stroke matching its layer hex
   - 5 clusters with new ≥3:1-contrast fills
   - 0 white stereotype ellipses

#### Task 11: Commit & PR for Pages

**Objective:** Get the index.html + viewer.js + viewer.css drift fixes onto Pages.
**Files:** `technehub-labs.github.io/metamodel/*`

Steps:
1. Commit Task 6, 7, 9 to `technehub-labs.github.io` on `fix/metamodel-pages-drift` branch.
2. Open PR. Verify Pages preview URL shows:
   - "33 entities · 30 relationships · 5 layers"
   - 5 filter buttons (L1 Strategic, L2 Business, L3 Digital, L4 Technical, L5 Measurement)
   - `?entity=SO` deep-link selects and scrolls to the SO card
3. Self-merge (admin) since Pages repo uses self-merge convention.

#### Task 12: Cross-repo drift verification

**Objective:** Confirm no representational drift between the two repos.
**Files:** none — pure verification

| Source | Should report |
|---|---|
| `dea-metamodel/viewer/entity-graph.json` | 33 entities, 5 layers, 0 relationships at root (rel data lives in PUML+JS) |
| `dea-metamodel/metamodel-puml/metamodel-v2.puml` | 33 `entity` definitions, 5 `package` blocks, 30 `link` lines |
| `dea-metamodel/viewer/metamodel.svg` | 33 `<g id="elem_*" class="entity">`, 5 `<g id="cluster_*">` |
| `technehub-labs.github.io/metamodel/index.html` | "33 entities · 30 relationships · 5 layers" badges; 5 filter buttons |
| `technehub-labs.github.io/metamodel/viewer.js` | `LAYER_NAMES` dict with 5 entries, `RELATIONSHIPS` array length 30 |
| `technehub-labs.github.io/metamodel/viewer.css` | `--l1..--l5` tokens present, `.entity-card[data-layer="L*"]` rules for L1–L5 |

All six must agree. If any row drifts, fix in a follow-up commit before declaring done.

---

## Out of scope (deferred)

- 7-color ECF-domain palette harmonization between framework pages and metamodel pages — separate design system decision; tracked as future Phase.
- Replacing PlantUML with a custom renderer (e.g., d3-graph, elk) — large surface area; the PUML+post-process pipeline is sufficient for now.
- Per-entity status badges (planned/scaffold/existing) inside the SVG diagram itself — these exist on the entity cards; showing them inside the diagram clutters the visual.

---

## Verification checklist (final)

- [ ] SVG viewBox aspect ratio is 1.3–1.7:1 (no horizontal squish)
- [ ] Each of the 5 cluster fills has ≥3:1 contrast against `#080B10`
- [ ] Each of the 5 entity stroke colours has ≥7:1 contrast against `#0D1117`
- [ ] Attribute text `+ id : string` is `#B1BAC4` on `#0D1117` (contrast ≥7:1)
- [ ] Relationship labels are `#B1BAC4` italic with `#080B10` halo
- [ ] Stereotype ellipses are tinted layer-hex at 0.18 alpha (no white)
- [ ] Index.html says "33 entities · 30 relationships · 5 layers"
- [ ] 5 filter buttons (no L6), names match `LAYER_NAMES` in viewer.js
- [ ] `?entity=SO` deep-link from catalog README works
- [ ] Pages site shows new SVG and updated index within 5 minutes of merge
- [ ] Cross-repo drift table (Task 12) has all green rows

---

## Open questions for user (decision points before execution)

1. **Kimi's "no tinted fill" recommendation vs your "entity color = layer color" preference** — Kimi says fills should stay neutral `#0D1117` for dark-theme legibility, layer identity comes from stroke + accent bar + stereotype. The org catalog READMEs don't actually show entities with tinted backgrounds (they're just text + badge). Confirm: keep fills neutral, encode layer identity via stroke + 3px left accent bar? (Yes/No.)

2. **Entity-graph.json `color` field is currently light-pastel** (`#E8F8F5`, `#FEF9E7`, `#FDEDEC`, `#E8DAEF`, `#FADBD8`) — these were chosen for a *light* background. Replace them with dark-theme-appropriate per-layer hex (one canonical hex per layer, all 10 L1 entities get the same L1 hex)? Or leave them and rely on the per-layer `--l1..--l5` CSS tokens only? (Replace / Leave.)

3. **Aspect-ratio target** — Kimi and I agree on 1.3–1.7:1. Specific target 1.45:1 (1600×1100)? Or accept whatever PlantUML produces after `skinparam nodesep 80` + ELK layout? (Specific 1.45 / Auto-accept.)

4. **Old deep-link URLs** — Catalog READMEs already link to `?entity=SO` etc. but no entity was ever auto-selected. Should the deep-link implementation also be backfilled by an audit/correction pass on every `dea-catalog-*` repo's README? Or just make `?entity=X` work and assume READMEs are already correct? (Backfill READMEs / Just implement the JS.)

5. **Execution batch** — Three PRs (one per repo) vs one mega-PR. The Aug 8 pattern prefers atomic cross-repo refactors. Go with three atomic PRs? Or single combined PR? (Atomic / Combined.)