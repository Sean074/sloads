# Appendix E — Worked example: the concept twin (`atr42_100`)

The third end-to-end pass, and the first outside the FAR 23 band: an
**ATR 42-300**, a 48-seat twin turboprop well above the 12,500-lb and 9-seat
limits the FAR 23 core is calibrated to
([Scope and limits](../20_theory/04_scope_and_applicability.md)). It is run in
**concept mode**, and it ends where concept mode is meant to end: a balanced,
full-span load set written as a solver deck whose equilibrium is checked.

**The figures.** Every number this pass refers to is in
[`_generated/worked_atr42_100.md`](_generated/worked_atr42_100.md), written
from a run of the bundled example. There is no printed oracle for this
airplane, so that table ends with the **closure checks** that stand in for one
(`CLAUDE.md` rule 2): what you verify here is that the airplane balances, not
that it matches a book.

**The data.** The published values (span, area, weights, CG limits, engines,
speeds) are cited one by one in
[`examples/atr42_100.sources.md`](../../examples/atr42_100.sources.md).
Everything else (chords, tail and control areas, the mass breakdown, the aero
coefficients) is **estimated**, marked **[E]** there, and never presented as
the airplane's certified value. Read the register beside this pass.

## 1. What concept mode changes

Concept mode is **category `C`** on the Structural Speeds page
([GUI user guide §7](../10_standard/GUI_USER_GUIDE.md#7-concept-mode-caveats)).
Against the FAR 23 core it changes three things, and on a GA input it reduces
exactly to that core:

- **The caps are lifted.** The 23.337 load-factor formula and the weight and
  seat limits no longer apply: you enter the design load factors, and they are
  taken verbatim. The GUI's applicability banner says when an airplane is
  outside the FAR 23 band; it never blocks.
- **Weights come from the mass model.** The itemised loading on Weight & Mass
  Properties is the source of truth; the statistical estimate becomes a sanity
  figure.
- **The deliverable is a balanced beam model.** Beyond the per-module loads,
  every selected flight case and every ground case is assembled into one
  free-free airplane that balances, and written as `FORCE`/`MOMENT` cards on
  the loads reference axis.

## 2. The pass

Load it (**New from example → `atr42_100`**). The pages are the same fourteen
as the single's; what differs is what they hold.

1. **[Geometry](01_configuration_layout.md).** The published span and area on
   a constructed planform: a constant-chord centre section and tapered outer
   panels, kinked at the engine butt line. Two wing engines (layout `2W`).
2. **[Weight & Mass Properties](02_weight_mass.md).** The **mass model**:
   empty-weight items, crew, 48 seats, and fuel in the wing tanks, at the
   published MTOW, MLW and MZFW. The named CG cases include the zero-fuel
   state (`mzfw aft`) and the landing corners, so each balanced case is
   assembled at the mass state it names. The figures table gives the aft-gross
   weight, CG and pitch inertia.
3. **[Aerodynamic Data](03_aero_coefficients.md).** Estimated polars, marked
   [E] in the register.
4. **[Structural Speeds](04_structural_speeds.md).** Category `C`, the
   design load factors entered, VC and VD chosen from the published Vmo. The
   resulting speeds are in the figures table.
5. **[Flight Envelope](05_flight_envelope.md).** Several altitudes up to the
   ceiling; SELECT picks the critical wing cases (the figures table quotes the
   PMAA case).
6. **[Wing](06_wing_loads.md), [Fuselage](07_fuselage_loads.md) and
   [Tail](08_tail_loads.md) Loads.** As the single, with the engines and fuel
   hanging on the wing.
7. **[Aileron](09_aileron_loads.md), [Flap](10_flap_loads.md),
   [Tab](11_tab_loads.md) and [Engine Mount](12_engine_mount.md) Loads.** As
   the single, per engine.
8. **[One Engine Out](13_one_engine_out.md).** The chapter the twin unlocks:
   the failed engine's thrust loss and windmilling drag, reacted at the fin.
   Note the SF column in the figures table: the failure at VC is one of the
   two families the regulation prescribes **already ultimate** (`SF=1.0`),
   the one at VD is a limit case (`SF=1.5`).
9. **[Landing Loads](14_landing_loads.md).** Tricycle gear on the published
   track and wheelbase.

## 3. The deliverable: the balanced beam model

Open the **Beam Model** page. It draws the LRA free-free beam that every load
is stated on, and **Write the deck and the OEW mass set** writes the solver
deck and the operating-empty mass set into a folder you choose. Headless, the
same deck:

```bash
.venv/bin/sloads --export-sbeam out --export-target lra examples/atr42_100.project.json
```

What to check, all of it in the closure block of the figures table:

- **Every case balances.** Each balanced case is the whole airplane, tip to
  tip and nose to tail, with no constraint. The deck check re-reads the
  written cards and sums them: all six resultants of every subcase close to
  zero.
- **The deck is LIMIT.** For every flight case, the inertia load set sums to
  exactly −n<sub>z</sub>·W. Had the safety factor been applied it would read
  −1.5·n<sub>z</sub>·W. Each subcase states its `SF=` and nothing applies it
  ([Conventions](03_conventions.md)).
- **How much was assumed.** A real airplane's computed loads never balance
  exactly; the closure supplies the remainder as a rigid-body load-factor
  increment Δn, and the deck prints it per subcase. The table names the
  largest on a flight case. A large Δn means the inputs disagree with each
  other (a weight that does not match the lift, say), and it is the first
  thing to look at before trusting a case.

## 4. What this pass does not prove

That the loads are a transport airplane's certification loads. Concept mode
runs the FAR 23 method on a Part 25-sized airplane, and some Part 25 rows are
not built; the
[Scope and limits](../20_theory/04_scope_and_applicability.md) page lists each
one and which way it errs. What the pass does prove is the chain: a concept
configuration goes in, and a balanced, LIMIT, equilibrium-checked load set
comes out, each case stating the factor your sizing applies.
