# Chapter 10 — The Mass Model and Inertia Loads

*(Chapter stub — template, assumptions and the validation record populated;
a fuller walk-through of WTONECG/WTENV and the weight database follows in a
later step. Their per-module equation citations remain authoritative in
[`00_theory_sources.md`](00_theory_sources.md).)*

## Scope & regulatory basis

Where every pound in the analysis lives and how it accelerates: the tagged
weight database as the mass single source of truth, the longitudinal mass
distribution behind the fuselage beam (chapter 6), the loading behind each CG
case, the two design weights and consumable fuel (14 CFR 23.473(b)/(c) — the
rules of record are the hub's §The two design weights), the surface weights
the empennage inertia is built on, and the exported `CONM2` mass model.

## The rules in one place

- **`weight.items` is the mass SSOT** (`CONVENTIONS.md` §1): every item
  tagged with the component that reacts it, wing shares stated as a fraction
  of a row, the fuselage beam *derived* from the tags, and every entered
  override reported against the derived value rather than silently taken.
- **Each mass enters exactly one field** — spread by a distribution *or*
  accelerated as a point with its own self-inertia, never both.
- **A surface's inertia acts along its own normal axis** — which is why the
  vertical tail, spanning `z`, takes both a lateral bending term and a
  vertical axial term (chapter 2 §2.9; the closure below).

## How it is validated — the record (moved from the theory hub)

### The mass distribution as a closure gate (step B1, 2026-08-08)

The Ch 15 fuselage beam has no printed oracle (Ref 1 ships no program for it), and
its *input* — the longitudinal mass distribution — had none either: it was a
hand-entered lump table that nothing checked. Step B1 makes
`weight.items` the single source and gates the beam on reconciliation identities
instead (`sloads/mass_distribution.py`, `tests/test_mass_distribution.py`):

| Identity | What it locks |
|---|---|
| `Σ(wing items) + Σ(beam stations) == Σ(all items) == W` | The partition is complete: no item lost between the two distributions, none counted twice |
| `Σ(items tagged wing) == 2 × (panel_weight_lb + Σ concentrated)` | The itemized wing and WINGINER's spanwise model describe one wing. Both WINGINER terms are per **side**, so the airplane carries twice their sum. **Holds on every shipped fixture since design note 29 (2026-08-17):** the wing-tank share of a fuel row is stated as `MassItem.wing_fraction` (derived from WINGINER's own `concentrated` entry — 3,800 / 4,000 / 1,200 lb on the three fuel-in-wing fixtures, no number invented) and read through `reacted_parts`; before it those pounds rode both beams — 7–15 % of the body beam, above the base-method band — and were pinned open. The tie is the invariant gate for that step (no printed oracle covers a fuel split), and it is a validator (`wing_mass_tie_open`) as well as a test |
| entered `fuselage_mass.stations` vs the derived table | Reported, never silently taken — the two disagreed by 10–100 % of the beam on every shipped fixture |

The beam carries the empennage (it hangs off the aft fuselage) and excludes the
wing (which enters as the Ch 15 p103 carry-through reaction — applying it as mass
too would double it). The free-free closure the beam already satisfied
(`ΣFz = 0`, terminal `Myy = 0`) is unchanged by all of this: it held on the light
beam and holds on the correct one, which is precisely why it could not have caught
the missing mass.

### The entered loading, and what checks it (D-25, 2026-08-15)

There is **no printed oracle for a loading**: Appendix A prints weights, CGs and
inertias, never the item set behind a CG case, and WTONECG/WTENV take the loading
hierarchy as data. The suite's answer had been to *derive* one — search the
discretionary subsets of `weight.items` for a set that reproduces the case's
weight and CG with a solved ballast row inside the fuselage — which is a search,
not a source. D-25 makes the loading an input (`CgCase.loading`), following the
same `MassItemKind` partition WTONECG's database uses (empty → minimum flight
weight → discretionary useful load, Ref 1 Ch 4), with fuel treated as continuously
burnable per 23.473(b)/(c) as decision G-5 already established for the derived
route.

What replaces the missing oracle is a **checked echo** (D-25a) plus a reduction
identity, both in CI:

| Gate | What it locks |
|---|---|
| `Σw`, `Σwx/Σw`, `Σwz/Σw` of the entered loading vs the case's `weight_lb`/`xcg`/`zcg`, within `max(0.5 lb, 0.1 %)` and `0.5 in` | The stated loading really is the case it claims to be. The loading is authoritative, so this is *reported*, never absorbed by adjusting the loading |
| entering the loading the search finds reproduces the searched result item-for-item (`rel=1e-12`) | The entered route is a superset of the derived one, not a second answer — the same reduction rule concept mode obeys against FAR 23 |

The credibility gate (10 % ballast) stays on **solved** ballast only (D-25d): a
number the tool invented has to be plausible, whereas a number an engineer states
is data — and stress/flight-test ballast on a real airplane is not bounded by what
a search finds comfortable. The fraction is stated everywhere the case appears
rather than being silently accepted.

### The CONM2 mass model as an *external* check (step C1–C5, 2026-08-08)

Every closure gate above is internal: sloads checking sloads. The distributed
**inertia** load has no printed oracle and, until this step, no external check
either — the same code computed it and wrote it out, so no artifact could
disagree. The `CONM2` export supplies one: sbeam parses the mass model
independently, and its own grid-point-weight generator recovers weight, CG and
inertia from it.

Verified by hand 2026-08-08 (sbeam is not a dependency, so CI cannot run it):
`sbeam.gpwg.compute_gpwg` reproduces sloads' mass, CG-x and CG-z for all four
`ga6_normal` payload cases exactly. The `GRAV`-driven nodal-inertia comparison
(plan 12 C6) needs the round-trip harness and is filed.

Two scope limits, stated rather than discovered: `GRAV` is a uniform
*translational* field and sbeam has no `RFORCE`, so rotational-acceleration
inertia (pitch/yaw) is not recoverable from a `CONM2` set and stays checked by
sloads-side closure; and a payload case is only exported when the weight database
can produce it as a loading — 7 of the 18 shipped cases, all four of ga6's among
them.

### The vertical tail's two inertia axes, and its exact-ratio closure (2026-08-10)

A surface's inertia is built on the acceleration along **its own normal axis**,
and that is where the two empennage surfaces stop being alike. The h-tail's
normal axis is the airplane's vertical, so `n_n = n_z` and there is no axial
term. The **fin spans in `z`**, so the same vertical acceleration runs *along*
its beam: it takes `n_n = n_y` for bending and `n_a = n_z` for an axial column
that compresses the surface and produces no bending at all.

`n_y` has no producer in a single-condition view — a lateral load factor is a
property of a balanced case — so it is derived the one self-consistent way
available, from the only lateral aerodynamic load the suite models, which is the
fin's own:

    n_y = (LT25 + LT50) / W_case          W_case = the condition's V-n CG case weight

That makes the fin's closure **exact and case-independent**, which is why it is
the gate:

| Closure | Analytic target | Why it is not a tautology |
|---|---|---|
| **Fin lateral inertia** | `Σ inertia / Σ air ≡ −W_vt/W_case` | The left side comes out of the strip quadrature; the right is two scalars it never touches. `n_y ∝ Fy` cancels the air load out of the ratio, so the identity holds on a rudder kick and a side gust alike — and fails immediately if the *vertical* factor is reached for where the lateral one belongs |
| **Fin axial column** | `Σ f_span = −n_z·W_vt`, and root bending unchanged by it | An axial load has no moment about its own line of action; asserting both at once catches it leaking into the bending channel |

**Two limitations, both stated in-band on every fin result rather than only
here.** First, the term **relieves**: the surface total comes out at exactly
`(1 − W_vt/W_case)` of the air load — 0.68 % on `ga6_normal`, 1.84 % on the
regional jet — which is the *unconservative* direction, and small only because a
fin is light. Second, it inherits decision **L-7**: with the wing-body sideslip
term off (the shipped default) the real airplane's `n_y` is *larger* than this
one (the missing side force adds to the fin's), so the relief above is a lower
bound on itself; with the term on the balanced case carries the larger `n_y`
and the relief follows it.
A condition naming no V-n point has no `W_case` and therefore gets **no** lateral
term, reported rather than filled with a gross-weight stand-in.

This supersedes plan 13 decision **L-8** for the per-condition view (user
decision, 2026-08-10). The assembled balanced case still accounts for the fin's
mass in its closure field, so the applied aerodynamic set it reads from
`tail_span` is taken as `fz − f_inertia`: each mass enters exactly one field.

## Sources

- Reference 1 Ch 3–4 (weight database, WTONECG/WTENV), Ch 15 (the fuselage
  mass table); Appendix A oracle pages per the hub's per-module rows.
- 14 CFR 23.473(b)/(c) — the two design weights and burnable fuel (rules
  G-4/G-14/G-5, stated in the hub).
- `CONVENTIONS.md` §1 — the mass-model conventions and their owners.
