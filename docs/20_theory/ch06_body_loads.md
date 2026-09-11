# Chapter 6 — Fuselage (Body) Loads

The net fuselage beam analysis — the body analogue of NETLOADS, from
Reference 1 Ch 15 ("Net Fuselage Loads"). Ch 15 gives a *suggested procedure*
rather than a ported `.BAS` program: the fuselage is a simple beam carrying
the inertia of the fuselage mass items, reacted by the tail air load and the
wing-attach reactions. Module: `sloads/modules/body_loads.py`.

## Scope & regulatory basis

The fuselage's running vertical shear `Sz` and bending `Myy` per station, for
the critical symmetric flight conditions. The regulatory loads themselves are
the flight conditions' (FAR 23.331ff, through the load factor `NZ` and the
balancing tail load); Ch 15 is method, not regulation. Ground conditions load
the fuselage through the assembled balanced deck instead (chapters 8 and 9),
and pressurization is permanently out of scope (decision D-24 —
`CONVENTIONS.md` §1, ground/flight family separation).

## Cases analyzed — via SELECT, like the wing

The fuselage is the second family on the **prune-before** pipeline: its
critical conditions are selected by SELECT (chapter 4 §Cases analyzed) from
the balanced V-n matrix, and each arrives with its load factor `NZ` and its
balancing tail load `LT`. There is no fuselage-specific FAR condition list —
contrast the empennage (chapter 5) and ground (chapter 8) families.

## Method — the two-pass Ch 15 beam

For each condition, following Ref 1 p103:

1. Multiply each fuselage station weight by the load factor to get its
   inertia force (`fz = −NZ·w`, down for positive `NZ`).
2. Apply the balancing tail air load `LT` at the tail station.
3. Integrate nose→tail to the running shear `Sz` and bending `Myy`; the
   terminal moment of *that* set is the **unbalanced moment** `M_ub` ("the
   moment at the aft end is the unbalanced moment", p103).
4. React `M_ub` — and the residual vertical force `R_total = NZ·W_fus − LT`
   — at the wing **front and rear spar attachments**, then re-integrate the
   whole set.

The beam's mass table is *derived* from the tagged weight database
(chapter 10), and the beam carries everything except the wing — the empennage
hangs off the aft fuselage, while the wing enters only as the carry-through
reaction (applying it as mass too would count it twice).

**The distributed carry-through reaction is a refinement of p103 — ours, not
the manual's.** p103 prescribes two point reactions; applied literally they
put a `±M_ub/d` shear spike across a short carry-through. The two reactions
are therefore applied as the statically equivalent **linear distribution over
`[x_f, x_r]`** — identical resultant and first moment, no spike — and it
collapses continuously onto the manual's two-point solve as `d → 0`. The
reactions `R_f`/`R_r` are still reported as the fitting loads; they are *not*
applied on top of the distribution, which already carries them. The options
trade is `docs/40_history/04_m4-1_body_moment_closure.md`.

## Assumptions & limitations

- **A vertical symmetric-flight beam.** Ch 15 solves the body in `Sz`/`Myy`
  only: no lateral bending, no torsion, no longitudinal load path. The
  lateral and three-dimensional fuselage states exist only in the assembled
  balanced model (chapter 9). The beam's waterline is a structural statement
  distinct from where its masses sit, and neither coordinate enters this
  chapter's shear or bending (`CONVENTIONS.md` §7.2).
- **Lumped station masses.** The longitudinal mass distribution is the
  Ch 15 lumped table derived from the weight database; the entered
  `fuselage_mass.stations` override is reported against the derived table,
  never silently taken (chapter 10).
- **The carry-through shape is stated, not derived.** The linear distribution
  above is a modelling choice with the manual's Bruhn pointer as precedent
  for diffusing discrete loads, not authority for this particular shape; the
  fitting loads are reported separately so a consumer can apply their own.
- **The station weights must already exclude** the wing mass outside the
  fuselage, per Ch 15 — an input obligation, checked by the mass-partition
  identity (chapter 10), not by this module.
- **One lumped term is stated rather than distributed:** the fuselage's share
  of the airplane-less-tail pitching moment (the Munk moment) has no
  per-station carrier yet (M4-19); its measured size is stated with the
  balanced cases (chapter 9).

## How it is validated

**There is no printed station-by-station oracle** — Ch 15 ships no program
and Appendix A prints no fuselage beam table — so the gate is **equilibrium
closure with an independent witness** (hub provenance table: a physical
invariant the module nowhere encodes): the applied vertical force sums to
zero, the running shear returns to ~0 at the aft end, and the terminal `Myy`
is ~0 (free-free in both ΣFz and ΣM; backlog M4-1). The same conditions are
re-checked downstream from the deliverable itself: the exported body deck's
card text closes to zero force and zero moment about its aft-most station,
and sbeam reassembles the whole cumulative table from the `FORCE` cards and
`GRID` coordinates alone (chapter 11).

A closure gate of this shape could not catch a *missing mass* — the beam
closes on a light table just as well as on the right one — which is exactly
why the mass-partition identities of chapter 10 exist alongside it.

## Sources

- Reference 1 Ch 15 ("Net Fuselage Loads"), p103 — the two-pass procedure.
- `docs/40_history/04_m4-1_body_moment_closure.md` — the carry-through
  distribution decision.
- [`00_theory_sources.md`](00_theory_sources.md) — the `body_loads` provenance
  row and the concept-closure identity table.
