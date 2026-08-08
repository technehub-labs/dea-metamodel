# Process Type Taxonomy

> Canonical reference for classifying Processes in the DEA metamodel.
> Metamodel: `technehub-labs/dea-metamodel` v3.0.0-alpha
> Schema: `schemas/entities/process.json`

## 1. Why two axes

Processes have two orthogonal properties that must each be captured:

1. **What role does the process play in the enterprise?** (`process_intent`)
2. **Whose work does the process most advance?** (`process_audience`)

Conflating them into a single label (as the v1 enum did with
`business / operational / support / management`) breaks MECE and forces
arbitrary tie-breaker decisions.

The v2 schema splits these into two enums and adds two multi-valued
references for the people/organizations the process touches:

| Field | Type | Cardinality | Source |
|---|---|---|---|
| `process_intent` | enum (3 values) | single | derived (Porter value-chain) |
| `process_audience` | enum (7 values) | single | derived (ECF axiom) |
| `stakeholders` | ref | multi-valued | `dea-catalog-stakeholders` |
| `actors` | ref | multi-valued | `dea-catalog-actors` |

The two enums are pure and independent. Stakeholders and actors are
attributes, not axes.

---

## 2. Axis 1 — `process_intent`

| Value | Definition | Boundary rule |
|---|---|---|
| `operational` | Executes the recurring, day-to-day running of the enterprise. | Activities are recurring, defined, and measured; the output is consumed internally or handed off to an external-facing process. |
| `support` | Provides specialist capability, tooling, or services consumed by other processes without producing the primary output itself. | The output is a service/capability consumed by other processes; the process does not directly advance an external relationship or produce the operational chain's primary artefact. |
| `management` | Sets direction, allocates resources, governs performance, and decides on changes. | The output is a decision, a plan, a budget, a policy, or a performance verdict — not an operational artefact. |

**Tie-breaker order (apply top-down):**

1. Is any output a decision / plan / budget / policy / performance verdict? → `management`
2. Does the process provide a service consumed by other processes without producing the primary output? → `support`
3. Otherwise (executes defined recurring work) → `operational`

---

## 3. Axis 2 — `process_audience`

The seven Enterprise Concept Framework (ECF) domains, axiom-derived
from the grounding axiom:

> **"An enterprise is any bounded entity that persists by exchanging
> value with its environment."**

| Value | Domain | Definition |
|---|---|---|
| `governance-existence` | 1 | The precondition of boundedness — what defines the entity, what rules apply. |
| `supply-resources` | 2 | The substrate the enterprise persists on — physical or virtual assets and capacity. |
| `people-organization` | 3 | The humans who perform every capability and the structure that organizes them. |
| `customer-demand` | 4 | The people whose need the entity meets, and the demand they generate. |
| `product-offering` | 5 | The catalog of what the enterprise offers — design, packaging, release, retirement. |
| `operations-delivery` | 6 | The engine that turns an offering into a delivered outcome. |
| `finance-value` | 7 | The measurement of value created, consumed, and retained. |

**Boundary rule:** assign the domain whose work the process most
advances. A single process has exactly one primary audience.

### Why not "stakeholder type"?

Stakeholders (customer / partner / supplier / regulator / investor /
community / board) are **not** the right axis for process audience.
The same stakeholder can participate in processes whose primary
audience differs:

- A channel partner can be `customer-demand` (they help acquire
  customers) or `product-offering` (they co-shape what is offered),
  depending on the process.
- A regulator is `governance-existence` — they participate in a
  governance activity, not in a regulator service.

ECF domains are MECE by construction (axiom-derived). Stakeholder
types are not closed (new types keep emerging: AI agents, DAO
treasuries, ecosystem orchestrators).

---

## 4. Stakeholders vs Actors

| Concept | Definition | Catalog |
|---|---|---|
| Stakeholder | A party whose relationship with the enterprise is affected by or engaged in the process. External or affected. | `dea-catalog-stakeholders` |
| Actor | A performer of the process — human, team, system, or AI agent. | `dea-catalog-actors` |

The same person can be a stakeholder of one process (e.g. "Quarterly
earnings call" — investor) and an actor of another (e.g. "Operate
internal payroll" — payroll specialist).

Employees are **actors**, not stakeholders, of the processes they
perform. They are **stakeholders** of processes whose work affects
their employment relationship (e.g. performance review).

---

## 5. MECE verification

| Test | Process v2 |
|---|---|
| **M**utually exclusive | Each process has exactly one `process_intent` (tie-breaker) AND exactly one `process_audience` (whose work most advanced). Axes are orthogonal. |
| **C**ollectively exhaustive | 3 × 7 = 21 cells. Audience is axiom-derived (proven CE). Stakeholders are open-set (multi-valued ref). |
| **P**ure | Each axis has a single discriminator. |

---

## 6. Migration from v1

The v1 enum `["business", "operational", "support", "management"]` is
**removed** in v3.0.0-alpha. Existing entries using `business` map as
follows (best-effort, requires manual review):

| v1 value | Likely v2 mapping |
|---|---|
| `business` | `process_intent`: depends on the work — typically `operational`. `process_audience`: typically `customer-demand`, `partner-facing` work → `customer-demand` or `product-offering`, `supplier-facing` work → `supply-resources`. |
| `operational` | `process_intent`: `operational`. `process_audience`: depends on whose work. |
| `support` | `process_intent`: `support`. `process_audience`: depends. |
| `management` | `process_intent`: `management`. `process_audience`: depends. |

No blast radius today: no `dea-catalog-processes` repo exists; no
catalog entries reference `process_type`. The schema change is
clean.

---

## 7. Worked examples

| Process | `process_intent` | `process_audience` |
|---|---|---|
| Acquire customer via digital channel | `operational` | `customer-demand` |
| Quarterly customer-success review | `management` | `customer-demand` |
| Provide customer onboarding training | `support` | `customer-demand` |
| Onboard alliance partner under revenue-share | `operational` | `product-offering` |
| Operate channel-partner portal | `operational` | `customer-demand` |
| Source new logistics vendor | `operational` | `supply-resources` |
| Annual supplier performance review | `management` | `supply-resources` |
| Procure cloud capacity from hyperscaler | `operational` | `supply-resources` |
| Run nightly batch reconciliation | `operational` | `operations-delivery` |
| Provide internal IT helpdesk | `support` | `supply-resources` |
| Set annual corporate budget | `management` | `finance-value` |
| File GDPR DPIA to regulator | `management` | `governance-existence` |
| Operate internal payroll | `operational` | `people-organization` |
| Conduct annual performance review | `management` | `people-organization` |
| Quarterly board governance review | `management` | `governance-existence` |

---

## 8. See also

- `technehub-labs/dea-metaframework` — REPORT.md §2 (axiom derivation), §7 (MECE sub-decomposition)
- `technehub-labs/dea-catalog-stakeholders` — stakeholder catalog
- `technehub-labs/dea-catalog-actors` — actor catalog
- `technehub-labs/dea-catalog-processes` — process catalog