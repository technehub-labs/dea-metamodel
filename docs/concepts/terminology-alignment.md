# Terminology Alignment — ECF vs Concepts Model

> **KB note — `Domain` and `Stage` are reserved for the Enterprise Concept
> Framework. The Concepts Model speaks in Concept Area, Concept Profile,
> Concept Classification, and ECF Context. The two vocabularies are related
> by association, never by identity.** Source:
> [CR-CM-000](../../change-requests/CR-CM-000.md). Machine-readable registry:
> [`vocabulary/terminology-registry.yaml`](../../vocabulary/terminology-registry.yaml).
> Conformance: `tests/conformance/test_015_terminology_registry.py`.

## 1. The problem

Two vocabularies were on a collision course. The Enterprise Concept
Framework (ECF — `technehub-labs/dea-metaframework`) uses **Domain** and
**Stage** as the two axes of its 7×7 foundation matrix. The forthcoming
OpenDEA Concepts Model needs thematic groupings of its own — and the
natural-but-wrong move would be to reuse *Domain* for them. One word, two
meanings, and every catalog, profile, and tool would have to guess which
one was meant.

CR-CM-000 settles this *before* the first canonical Concepts Model ships:
fix the terminology first, then build on it.

## 2. The five artifact boundaries

| Artifact | Home | Role in the terminology contract |
|---|---|---|
| Enterprise Concept Framework | `technehub-labs/dea-metaframework` | Owns **Domain** and **Stage** (the matrix axes). |
| OpenDEA Concepts Model | forthcoming sub-tree of this repo | Owns **Concept Area**, **Concept Profile**, **Concept Classification**, **ECF Context**. |
| OpenDEA Foundational Metamodel | this repo (`metamodel/`, `specification/`) | Consumes terminology; never redefines reserved terms. |
| Catalogs | `dea-catalog-*` repos | Reference ECF coordinates and Concepts Model groupings; never re-define governed terms locally. |
| Profiles | `metamodel/profiles/` | Extend, never redefine (O001–O009); terminology rules apply unchanged. |

## 3. Reserved terms (ECF)

- **Domain → ECF Domain.** One of the seven axiom-derived rows of the
  foundation matrix (Governance & Existence … Finance & Value). Answers
  *"what does the enterprise do?"*
- **Stage → ECF Stage.** One of the seven lifecycle columns (Conceive …
  Retire). Answers *"how does the work evolve?"*

Every use of *Domain* must be either explicitly **ECF Domain** or
namespace-qualified (e.g. `ecf:Domain`). No Concepts Model artifact may use
*Domain* as a generic thematic grouping.

## 4. Concepts Model terms

- **Concept Area** — a thematic grouping of concepts *within* the Concepts
  Model. Concepts may belong to **multiple** Concept Areas.
- **Concept Profile** — a named, purpose-bound selection of concepts and
  their groupings.
- **Concept Classification** — the assignment of a concept to one or more
  classification targets (Concept Areas, Concept Profiles).
- **ECF Context** — an *optional* association between a concept and ECF
  coordinates (ECF Domain, ECF Stage). Concepts may carry **zero or more**
  ECF Contexts.

## 5. The non-identity principle

**Concept Area ≠ ECF Domain.** They are modeled as different concepts, and
no automatic one-to-one mapping is assumed between them. An ECF Context is
an *association* — a concept may sit in several Concept Areas, relate to
several ECF coordinates, or to none. The matrix is a coordinate system, not
a folder tree; the Concepts Model is a semantic graph, not a matrix copy.

This mirrors the framework's own anti-pattern guidance ("mixing axes",
"overloading a cell"): collapsing two orthogonal vocabularies into one word
is how semantic drift starts.

## 6. Why the registry ships first

Acceptance criterion 7 is the load-bearing one: the terminology registry is
introduced **before** the first canonical Concepts Model. Any future
Concepts Model CR lands against an already-governed vocabulary, so its
schemas, examples, and docs inherit the boundaries by construction instead
of being retrofitted after drift has set in. The conformance test
(`test_015_terminology_registry.py`) enforces the registry's integrity and
guards the boundary going forward.
