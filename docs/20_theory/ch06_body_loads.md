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

## Method — two cantilevers off the wing station (Ch 15, as note 64 states it)

For each condition, following Ref 1 p103 with the reaction placed where the
beam model has a member (design note 64 D-64.2, D-64.4, D-64.5):

1. Multiply each fuselage station weight of the case's loading (chapter 10)
   by the load factor to get its inertia force (`fz = −NZ·w`, down for
   positive `NZ`).
2. Apply the balancing tail air load `LT` at the tail station.
3. Close the free body at the **wing station** — the side of body's own
   fuselage station, where the LRA model's wing post stands: the reaction is
   `R = −ΣFz` and the couple that zeroes the whole set's moment about that
   station.
4. Integrate the **forward body from the nose to the front spar** and the
   **aft body from the tail to the rear spar**, each from its free end toward
   the wing, shear and bending **positive for an up load in both bodies**. A
   station at or between the spars belongs to the box: its load is applied
   there and carried by neither cantilever.

The beam's mass table is *derived* from the tagged weight database
(chapter 10), and the beam carries everything except the wing — the empennage
hangs off the aft fuselage, while the wing enters only as the one reaction at
the wing station (applying it as mass too would count it twice).

**p103's two spar reactions survive as the reported fitting pair.** The
manual reacts the unbalanced moment at the front and rear spar attachments;
sloads reports that pair, `R_f + R_r = R` with its moment about the wing
station recovering the couple, as the static equivalent of the one reaction
at the two spars — **applied nowhere**, so a consumer can carry it into their
own box model. Nothing is integrated through the carry-through, where the
model has no beam: the linear distribution over `[x_f, x_r]` that stood from
2026-08-03 to 2026-09-21 (M4-1) smoothed a spike across a region that is
integrated by nothing, and retired with the whole-body closure correction. A
project that cannot place the wing post is refused by name.

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
- **The box is not analysed here.** Between the spars the body is the
  wing-body box, whose load path is not a beam; the fitting pair is reported
  so a consumer can apply their own box model, and the deck's front-spar,
  rear-spar and post elements carry the cut loads without integrating them.
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
invariant the module nowhere encodes): the forward body's terminal shear and
moment at the front spar, the aft body's at the rear spar, the loads applied
within the box and the wing reaction sum to zero force and zero moment about
the wing station (free-free in both ΣFz and ΣM; note 64 gate 4), and a
positive load factor bends both bodies down (gate 5). The same free body is
re-checked downstream from the deliverable itself: the LRA deck's front-spar,
rear-spar and post elements recover the two cantilever sums and the wing
reaction from the solver (chapter 11).

A closure gate of this shape could not catch a *missing mass* — the beam
closes on a light table just as well as on the right one — which is exactly
why the mass-partition identities of chapter 10 exist alongside it.

## Sources

- Reference 1 Ch 15 ("Net Fuselage Loads"), p103 — the two-pass procedure.
- `docs/25_notes/64_wing_body_joint_note.md` — the wing-station reaction, the
  two cantilevers and the box rule (D-64.2, D-64.4, D-64.5; gates 4–5).
- `docs/25_notes/04_m4-1_body_moment_closure.md` — the retired linear
  carry-through distribution, for the *why it changed* reader only.
- [`00_theory_sources.md`](00_theory_sources.md) — the `body_loads` provenance
  row and the concept-closure identity table.
